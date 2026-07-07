from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    dashboard_view, 
    master_data_view, 
    add_department_view, 
    add_customer_view, 
    add_project_view,
    add_employee_view
)

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('master-data/', master_data_view, name='master_data'),
    
    path('master-data/add-department/', add_department_view, name='add_department'),
    path('master-data/add-customer/', add_customer_view, name='add_customer'),
    path('master-data/add-project/', add_project_view, name='add_project'),
    path('master-data/add-employee/', add_employee_view, name='add_employee'), # 新增
]