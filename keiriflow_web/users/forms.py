from django import forms
from django.contrib.auth import get_user_model
from tenants.models import Department, Customer, Project
from users.models import Role

User = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_code', 'department_name']
        widgets = {
            'department_code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
            'department_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_code', 'customer_name']
        widgets = {
            'customer_code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
            'customer_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['customer', 'project_code', 'project_name']
        widgets = {
            'customer': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none'}),
            'project_code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
            'project_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['customer'].queryset = Customer.objects.filter(tenant=tenant, deleted_at__isnull=True)


class EmployeeCreationForm(forms.Form):
    username = forms.CharField(label="ログインID", max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '例: tanaka'}))
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}))
    
    # ✨ 核心改造：从 ChoiceField 进化为 ModelChoiceField，动态载入当前租户的角色
    role = forms.ModelChoiceField(queryset=Role.objects.none(), label="権限ロール", widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none'}))
    
    employee_no = forms.CharField(label="社員番号", max_length=30, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '例: EMP002'}))
    last_name = forms.CharField(label="姓", max_length=50, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}))
    first_name = forms.CharField(label="名", max_length=50, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none'}))
    department = forms.ModelChoiceField(label="所属部門", queryset=Department.objects.none(), widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none'}))

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.objects.filter(tenant=tenant, deleted_at__isnull=True)
            # ✨ 严格安全隔离：只允许选择属于当前公司的角色
            self.fields['role'].queryset = Role.objects.filter(tenant=tenant, deleted_at__isnull=True)