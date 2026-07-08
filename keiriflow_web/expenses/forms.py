from django import forms
from django.forms import inlineformset_factory
from .models import ExpenseReport, ExpenseItem
from tenants.models import Project

class ExpenseReportForm(forms.ModelForm):
    class Meta:
        model = ExpenseReport
        fields = ['title', 'project']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '例：4月分営業出張交通費'}),
            'project': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant, deleted_at__isnull=True)

# 动态多明细表单集 (Formset)
ExpenseItemFormSet = inlineformset_factory(
    ExpenseReport, 
    ExpenseItem,
    fields=['expense_date', 'category', 'amount', 'description'],
    extra=1, # 默认生成一行空白明细
    can_delete=True,
    widgets={
        'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'px-2 py-1 border rounded text-sm'}),
        'category': forms.Select(attrs={'class': 'px-2 py-1 border rounded text-sm bg-white'}),
        'amount': forms.NumberInput(attrs={'class': 'px-2 py-1 border rounded text-sm w-24', 'placeholder': '金額'}),
        'description': forms.TextInput(attrs={'class': 'px-2 py-1 border rounded text-sm w-full', 'placeholder': '用途・備考'}),
    }
)