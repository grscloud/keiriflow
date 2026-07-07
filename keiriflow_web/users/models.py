from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin
from tenants.models import Department, Tenant

class SystemPermission(models.Model):
    """全システム共通の細粒度権限マスタ"""
    code = models.CharField(max_length=50, primary_key=True, verbose_name="権限コード") # 例: expense:apply
    name = models.CharField(max_length=100, verbose_name="権限名")
    module = models.ForeignKey('tenants.SystemModule', on_delete=models.CASCADE, related_name='permissions', verbose_name="所属モジュール")

    class Meta:
        db_table = 'system_permission'

    def __str__(self):
        return f"{self.name} [{self.code}]"


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """テナントごとに完全隔離された役割（ロール）マスタ"""
    name = models.CharField(max_length=50, verbose_name="ロール名")
    # 多对多关联原子权限
    permissions = models.ManyToManyField(SystemPermission, related_name='roles', blank=True, verbose_name="付与された権限")

    class Meta:
        db_table = 'role'
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name} ({self.tenant.company_name if self.tenant else 'プラットフォーム'})"


class User(AbstractUser, BaseModel):
    """カスタムユーザーモデル"""
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    
    # ✨ 核心改造：由原先的文本 Choices 改为动态关联角色表
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="役割・権限"
    )

    class Meta:
        db_table = 'user'

    def __str__(self):
        role_name = self.role.name if self.role else "権限なし"
        return f"{self.username} ({role_name})"
        
    # ✨ 新增：判断用户是否拥有某项原子权限的快捷方法
    def has_custom_perm(self, perm_code):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        # 校验：角色是否包含该权限，且该权限所属的模块当前企业已经开通
        return self.role.permissions.filter(
            code=perm_code, 
            module__tenants=self.tenant
        ).exists()


class Employee(BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """社員マスタ"""
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='employee', verbose_name="ユーザー")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name='employees', verbose_name="部門")
    employee_no = models.CharField(max_length=30, verbose_name="社員番号")
    first_name = models.CharField(max_length=50, verbose_name="名")
    last_name = models.CharField(max_length=50, verbose_name="姓")

    class Meta:
        db_table = 'employee'
        unique_together = ('tenant', 'employee_no')

    def __str__(self):
        return f"[{self.employee_no}] {self.last_name} {self.first_name}"