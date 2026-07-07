import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.IntegerField(default=1)

    class Meta:
        abstract = True

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

# ✨ 新增：多租户行级隔离的核心 Mixin
class TenantMixin(models.Model):
    """所有需要按公司隔离的业务表（部门、客户、项目等）都需要继承它"""
    tenant = models.ForeignKey(
        'tenants.Tenant', 
        on_delete=models.PROTECT, # 极其重要：防止误删公司导致财务/主数据丢失
        related_name="%(class)s_records"
    )

    class Meta:
        abstract = True