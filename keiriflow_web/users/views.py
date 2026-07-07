from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from tenants.models import Tenant, Department, Customer, Project
from users.models import Employee

User = get_user_model()

@login_required
def dashboard_view(request):
    user = request.user
    if user.is_superuser:
        context = {
            'is_platform_admin': True,
            'total_tenants': Tenant.objects.count(),
            'total_global_users': User.objects.count(),
        }
        return render(request, 'dashboard.html', context)
        
    context = {'tenant': user.tenant}
    
    # ✨ 改造：使用全新的细粒度权限判定逻辑
    if user.has_custom_perm('master:manage'):
        context.update({
            'is_admin': True,
            'total_employees': Employee.objects.filter(tenant=user.tenant, deleted_at__isnull=True).count(),
            'pending_approvals': 0,
            'monthly_spend': "¥0",
        })
    else:
        context.update({
            'is_admin': False,
            'my_drafts': 0,
            'my_processing': 0,
            'my_approved_this_month': "¥0",
        })
    return render(request, 'dashboard.html', context)


@login_required
def master_data_view(request):
    current_user = request.user
    if current_user.is_superuser:
        messages.warning(request, "システム管理者は管理サイトを利用してください。")
        return redirect('dashboard')
        
    # ✨ 改造：不再硬编码看角色字符串，而是校验是否拥有管理主数据的权限
    if not current_user.has_custom_perm('master:manage'):
        messages.error(request, "アクセス権限がありません。")
        return redirect('dashboard')
        
    current_tenant = current_user.tenant
    departments = Department.objects.filter(tenant=current_tenant, deleted_at__isnull=True)
    employees = Employee.objects.filter(tenant=current_tenant, deleted_at__isnull=True).select_related('department', 'user__role')
    customers = Customer.objects.filter(tenant=current_tenant, deleted_at__isnull=True)
    projects = Project.objects.filter(tenant=current_tenant, deleted_at__isnull=True).select_related('customer')
    
    from .forms import DepartmentForm, CustomerForm, ProjectForm, EmployeeCreationForm
    context = {
        'tenant': current_tenant,
        'departments': departments,
        'employees': employees,
        'customers': customers,
        'projects': projects,
        'dept_form': DepartmentForm(),
        'cust_form': CustomerForm(),
        'proj_form': ProjectForm(tenant=current_tenant),
        'emp_form': EmployeeCreationForm(tenant=current_tenant),
    }
    return render(request, 'master_data.html', context)


@login_required
def add_employee_view(request):
    if not request.user.has_custom_perm('master:manage'):
        return redirect('dashboard')

    from .forms import EmployeeCreationForm
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST, tenant=request.user.tenant)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user_record = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        tenant=request.user.tenant,
                        role=form.cleaned_data['role'] # 保存所选的动态 Role 实例
                    )
                    Employee.objects.create(
                        tenant=request.user.tenant,
                        user=user_record,
                        department=form.cleaned_data['department'],
                        employee_no=form.cleaned_data['employee_no'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                messages.success(request, f"社員「{user_record.username}」のアカウントを新規開設しました。")
            except Exception as e:
                messages.error(request, f"登録エラーが発生しました: {str(e)}")
        else:
            messages.error(request, "入力内容に不備があります。")
    return redirect('master_data')


@login_required
def add_department_view(request):
    if not request.user.has_custom_perm('master:manage'): return redirect('dashboard')
    from .forms import DepartmentForm
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save(commit=False)
            dept.tenant = request.user.tenant
            dept.save()
            messages.success(request, "部門を追加しました。")
    return redirect('master_data')


@login_required
def add_customer_view(request):
    if not request.user.has_custom_perm('master:manage'): return redirect('dashboard')
    from .forms import CustomerForm
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            cust = form.save(commit=False)
            cust.tenant = request.user.tenant
            cust.save()
            messages.success(request, "取引先を追加しました。")
    return redirect('master_data')


@login_required
def add_project_view(request):
    if not request.user.has_custom_perm('master:manage'): return redirect('dashboard')
    from .forms import ProjectForm
    if request.method == 'POST':
        form = ProjectForm(request.POST, tenant=request.user.tenant)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.tenant = request.user.tenant
            proj.save()
            messages.success(request, "案件を追加しました。")
    return redirect('master_data')