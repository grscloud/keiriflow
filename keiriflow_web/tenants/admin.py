from django.contrib import admin
from .models import SystemModule, Tenant, Department, Customer, Project

@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'subdomain', 'is_active', 'created_at')
    search_fields = ('company_name', 'subdomain')
    list_filter = ('is_active',)
    # 在编辑租户时，可以用左右双栏穿梭框优雅地配置开通的模块
    filter_horizontal = ('modules',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    # 显示部门代码、部门名、所属租户以及是否被软删除
    list_display = ('department_code', 'department_name', 'tenant', 'deleted_at')
    # 右侧加入租户过滤器，点击即可过滤出“山田テクノロジー”的部门
    list_filter = ('tenant', 'deleted_at')
    search_fields = ('department_code', 'department_name')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_code', 'customer_name', 'tenant', 'deleted_at')
    list_filter = ('tenant', 'deleted_at')
    search_fields = ('customer_code', 'customer_name')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'customer', 'tenant', 'deleted_at')
    list_filter = ('tenant', 'customer', 'deleted_at')
    search_fields = ('project_code', 'project_name')