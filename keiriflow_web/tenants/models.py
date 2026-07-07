from django.db import models
from core.models import BaseModel, TimestampMixin, SoftDeleteMixin

class SystemModule(models.Model):
    """プラットフォームのシステムモジュール（例：経費精算、勤怠管理など）"""
    code = models.CharField(max_length=50, primary_key=True, verbose_name="モジュールコード")
    name = models.CharField(max_length=100, verbose_name="モジュール名")
    is_active = models.BooleanField(default=True, verbose_name="有効フラグ")

    class Meta:
        db_table = 'system_module'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin):
    """企業（テナント）マスタ"""
    company_name = models.CharField(max_length=100, verbose_name="会社名")
    subdomain = models.CharField(max_length=50, unique=True, verbose_name="サブドメイン")
    is_active = models.BooleanField(default=True, verbose_name="有効ステータス")
    
    # ✨ 新增：当前企业开通的功能模块
    modules = models.ManyToManyField(SystemModule, related_name='tenants', blank=True, verbose_name="契約モジュール")

    class Meta:
        db_table = 'tenant'

    def __str__(self):
        return self.company_name


class Department(BaseModel, TimestampMixin, SoftDeleteMixin):
    """部門マスタ"""
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name='departments')
    department_code = models.CharField(max_length=20, verbose_name="部門コード")
    department_name = models.CharField(max_length=100, verbose_name="部門名")

    class Meta:
        db_table = 'department'
        unique_together = ('tenant', 'department_code')

    def __str__(self):
        return self.department_name


class Customer(BaseModel, TimestampMixin, SoftDeleteMixin):
    """取引先マスタ"""
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name='customers')
    customer_code = models.CharField(max_length=20, verbose_name="取引先コード")
    customer_name = models.CharField(max_length=100, verbose_name="取引先名")

    class Meta:
        db_table = 'customer'
        unique_together = ('tenant', 'customer_code')

    def __str__(self):
        return self.customer_name


class Project(BaseModel, TimestampMixin, SoftDeleteMixin):
    """案件（プロジェクト）マスタ"""
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name='projects')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='projects', verbose_name="取引先")
    project_code = models.CharField(max_length=20, verbose_name="案件コード")
    project_name = models.CharField(max_length=100, verbose_name="案件名")

    class Meta:
        db_table = 'project'
        unique_together = ('tenant', 'project_code')

    def __str__(self):
        return self.project_name