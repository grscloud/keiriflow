from django.contrib import admin
from .models import ExpenseReport, ExpenseItem, ApprovalLog

class ExpenseItemInline(admin.TabularInline):
    """在编辑报销单主表时，直接在下方内嵌表格直接查看/修改其明细项目"""
    model = ExpenseItem
    extra = 1
    fields = ('expense_date', 'category', 'amount', 'description', 'deleted_at')

@admin.register(ExpenseReport)
class ExpenseReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'tenant', 'status', 'total_amount', 'current_approver', 'submitted_at')
    list_filter = ('tenant', 'status', 'submitted_at')
    search_fields = ('title', 'user__username')
    inlines = [ExpenseItemInline]

@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('expense_report', 'approver', 'action', 'created_at')
    list_filter = ('tenant', 'action')