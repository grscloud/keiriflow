from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin
from tenants.models import Project

User = get_user_model()

class ExpenseReport(BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """精算書（経費精算申請）のメインテーブル"""
    class Status(models.TextChoices):
        DRAFT = 'draft', '下書き'          # 草稿：员工还没提交
        PENDING = 'pending', '申請中'      # 审批中：卡在审批人处
        APPROVED = 'approved', '精算完了'  # 结清：审批通过，财务可以打款
        REJECTED = 'rejected', '差し戻し'  # 驳回：被审批人打回，员工可修改后再提交

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='expense_reports', verbose_name="申請者")
    title = models.CharField(max_length=150, verbose_name="精算タイトル")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="ステータス")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True, blank=True, related_name='expense_reports', verbose_name="関連案件")
    
    # 冗余整张单子的总金额，方便大盘统计和列表展示，通过明细触发更新
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="合計金額")
    
    # 当前指派的审批人（动态工作流核心）
    current_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_approvals', verbose_name="現在の承認者")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="申請日時")

    class Meta:
        db_table = 'expense_report'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()}) - {self.total_amount}円"

    def update_total_amount(self):
        """计算当前报销单下所有未删除明细的总金额"""
        total = self.items.filter(deleted_at__isnull=True).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.total_amount = total
        self.save()


class ExpenseItem(BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """精算書の明細（1つの申請に紐づく複数の領収書データ）"""
    class Category(models.TextChoices):
        TRANSPORT = 'transport', '交通費'
        MEAL = 'meal', '会議費・交際費'
        SUPPLIES = 'supplies', '消耗品費'
        OTHERS = 'others', 'その他'

    expense_report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='items', verbose_name="精算書")
    category = models.CharField(max_length=30, choices=Category.choices, verbose_name="費目")
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="金額")
    expense_date = models.DateField(verbose_name="利用日")
    description = models.TextField(blank=True, verbose_name="備考・用途")

    class Meta:
        db_table = 'expense_item'

    def __str__(self):
        return f"{self.get_category_display()}: ¥{self.amount}"


class ApprovalLog(BaseModel, TimestampMixin, TenantMixin):
    """監査用：ワークフローの承認・差し戻し履歴ログ"""
    class Action(models.TextChoices):
        SUBMIT = 'submit', '申請'
        APPROVE = 'approve', '承認'
        REJECT = 'reject', '差し戻し'
        CANCEL = 'cancel', '取下げ'

    expense_report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='logs', verbose_name="精算書")
    approver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approval_logs', verbose_name="処理者")
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name="アクション")
    comment = models.TextField(blank=True, verbose_name="コメント・理由")

    class Meta:
        db_table = 'approval_log'
        ordering = ['created_at']  # 严格按时间正序排列日志

    def __str__(self):
        return f"{self.approver.username} が {self.get_action_display()} を行いました"