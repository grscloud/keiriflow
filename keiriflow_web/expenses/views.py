from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import ExpenseReport, ApprovalLog
from .forms import ExpenseReportForm, ExpenseItemFormSet

@login_required
def expense_list_view(request):
    """经报销列表首页（双视角：我的申请 + 待我审批）"""
    user = request.user
    if user.is_superuser:
        return redirect('dashboard')

    # 1. 我提交的报销单
    my_reports = ExpenseReport.objects.filter(user=user, deleted_at__isnull=True).order_by('-created_at')
    
    # 2. 待我审批的报销单（基于方案B：我是当前审批人，且状态是申请中）
    pending_approvals = []
    if user.has_custom_perm('expense:approve'):
        pending_approvals = ExpenseReport.objects.filter(
            tenant=user.tenant,
            current_approver=user,
            status=ExpenseReport.Status.PENDING,
            deleted_at__isnull=True
        ).order_by('-submitted_at')

    context = {
        'my_reports': my_reports,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create_view(request):
    """创建/提交报销单（核心自动路由逻辑）"""
    user = request.user
    if not user.has_custom_perm('expense:apply'):  # 确保这里和你的权限编码一致
        messages.error(request, "経費申請の権限がありません。")
        return redirect('expense_list')

    if request.method == 'POST':
        form = ExpenseReportForm(request.POST, tenant=user.tenant)
        formset = ExpenseItemFormSet(request.POST)
        
        is_submitting = 'submit_action' in request.POST

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    report = form.save(commit=False)
                    report.tenant = user.tenant
                    report.user = user
                    
                    if is_submitting:
                        if not hasattr(user, 'employee') or not user.employee.manager:
                            raise ValueError("直属の上司（承認者）が設定されていません。システム管理者に連絡してください。")
                        
                        report.status = ExpenseReport.Status.PENDING
                        report.current_approver = user.employee.manager
                        report.submitted_at = timezone.now()
                    else:
                        report.status = ExpenseReport.Status.DRAFT

                    report.save()
                    
                    # 👑 修复多租户明细报错核心
                    formset.instance = report
                    items = formset.save(commit=False)
                    for item in items:
                        item.tenant = user.tenant  # 注入租户ID
                        item.save()
                    
                    for obj in formset.deleted_objects:
                        obj.delete()

                    report.update_total_amount()

                    if is_submitting:
                        ApprovalLog.objects.create(
                            tenant=user.tenant, expense_report=report,
                            approver=user, action=ApprovalLog.Action.SUBMIT,
                            comment="経費精算が申請されました（自動ルート判定）。"
                        )
                        messages.success(request, f"精算書「{report.title}」を上司（{report.current_approver.username}さん）へ申請しました。")
                    else:
                        messages.success(request, "下書きとして保存しました。")
                        
                return redirect('expense_list')
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f"保存中にエラーが発生しました: {str(e)}")
    else:
        form = ExpenseReportForm(tenant=user.tenant)
        formset = ExpenseItemFormSet()

    return render(request, 'expenses/expense_form.html', {'form': form, 'formset': formset})


@login_required
def expense_process_view(request, report_id):
    """主管执行审批（同意/驳回）的原子操作"""
    if not request.user.has_custom_perm('expense:approve'):
        messages.error(request, "承認権限がありません。")
        return redirect('expense_list')

    report = get_object_or_404(ExpenseReport, id=report_id, tenant=request.user.tenant, deleted_at__isnull=True)
    
    # 安全边界：只有当前指定的审批人有权处理
    if report.current_approver != request.user or report.status != ExpenseReport.Status.PENDING:
        messages.error(request, "この申請を処理する権限がないか、すでに処理済みです。")
        return redirect('expense_list')

    if request.method == 'POST':
        action_type = request.POST.get('action') # 'approve' 或 'reject'
        comment = request.POST.get('comment', '').strip()

        with transaction.atomic():
            if action_type == 'approve':
                report.status = ExpenseReport.Status.APPROVED
                report.current_approver = None # 流程结束
                log_action = ApprovalLog.Action.APPROVE
                messages.success(request, "申請を承認（精算完了）しました。")
            elif action_type == 'reject':
                report.status = ExpenseReport.Status.REJECTED
                report.current_approver = None # 退回给员工修改
                log_action = ApprovalLog.Action.REJECT
                messages.warning(request, "申請を差し戻しました。")
            else:
                return redirect('expense_list')

            report.save()
            ApprovalLog.objects.create(
                tenant=request.user.tenant, expense_report=report,
                approver=request.user, action=log_action, comment=comment
            )
            
    return redirect('expense_list')

@login_required
def expense_edit_view(request, report_id):
    """差し戻しまたは下書き状態の精算書を編集・再申請する"""
    user = request.user
    # 严格越权校验：只能修改属于自己、且属于自己公司的未删除单据
    report = get_object_or_404(ExpenseReport, id=report_id, tenant=user.tenant, user=user, deleted_at__isnull=True)

    # 🚨 安全边界：只有“下書き(草稿)”和“差し戻し(驳回)”状态的单子允许被修改
    if report.status not in [ExpenseReport.Status.DRAFT, ExpenseReport.Status.REJECTED]:
        messages.error(request, "この申請は現在のステータスでは編集できません。")
        return redirect('expense_list')

    if request.method == 'POST':
        form = ExpenseReportForm(request.POST, instance=report, tenant=user.tenant)
        formset = ExpenseItemFormSet(request.POST, instance=report)
        is_submitting = 'submit_action' in request.POST

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    report = form.save(commit=False)
                    
                    if is_submitting:
                        if not hasattr(user, 'employee') or not user.employee.manager:
                            raise ValueError("直属の上司（承認者）が設定されていません。")
                        
                        report.status = ExpenseReport.Status.PENDING
                        report.current_approver = user.employee.manager
                        report.submitted_at = timezone.now()
                    else:
                        # 如果是点击下書き保存，状态扭转为草稿
                        report.status = ExpenseReport.Status.DRAFT

                    report.save()

                    # 保存更新后的明细（处理多租户注入）
                    items = formset.save(commit=False)
                    for item in items:
                        item.tenant = user.tenant
                        item.save()
                    
                    # 处理在前端被用户删除的明细行
                    for obj in formset.deleted_objects:
                        obj.delete()

                    # 重新触发总金额联动计算
                    report.update_total_amount()

                    # 记录工作流日志
                    if is_submitting:
                        ApprovalLog.objects.create(
                            tenant=user.tenant, expense_report=report,
                            approver=user, action=ApprovalLog.Action.SUBMIT,
                            comment="差し戻し/下書きからの再申請（自動ルート判定）。"
                        )
                        messages.success(request, f"精算書「{report.title}」を再申請しました。")
                    else:
                        messages.success(request, "修正内容を下書き保存しました。")
                        
                return redirect('expense_list')
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f"保存中にエラーが発生しました: {str(e)}")
    else:
        # GET 请求：将老数据回填到表单中
        form = ExpenseReportForm(instance=report, tenant=user.tenant)
        formset = ExpenseItemFormSet(instance=report)

    context = {
        'form': form,
        'formset': formset,
        'is_edit': True,
        'report': report
    }
    return render(request, 'expenses/expense_form.html', context)