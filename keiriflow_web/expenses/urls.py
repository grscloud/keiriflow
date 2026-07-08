from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list_view, name='expense_list'),
    path('create/', views.expense_create_view, name='expense_create'),
    path('process/<uuid:report_id>/', views.expense_process_view, name='expense_process'),
    # ✨ 新增：编辑再提交路由
    path('edit/<uuid:report_id>/', views.expense_edit_view, name='expense_edit'),
]