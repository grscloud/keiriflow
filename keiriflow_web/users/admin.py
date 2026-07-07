from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SystemPermission, Role, User, Employee

@admin.register(SystemPermission)
class SystemPermissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'module')
    list_filter = ('module',)
    search_fields = ('code', 'name')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('name',)
    # 给角色配置原子权限时，提供方便的穿梭框交互
    filter_horizontal = ('permissions',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """扩展 Django 原生用户后台，使其支持多租户和动态角色字段"""
    list_display = ('username', 'email', 'tenant', 'role', 'is_staff', 'is_superuser')
    list_filter = ('tenant', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    
    # 将我们的租户和角色字段，优雅地塞进 Django 现有的后台表单区块中
    fieldsets = UserAdmin.fieldsets + (
        ('SaaS 多租户扩展信息', {'fields': ('tenant', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SaaS 多租户扩展信息', {'fields': ('tenant', 'role')}),
    )

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_no', 'last_name', 'first_name', 'tenant', 'department', 'deleted_at')
    list_filter = ('tenant', 'department', 'deleted_at')
    search_fields = ('employee_no', 'last_name', 'first_name')