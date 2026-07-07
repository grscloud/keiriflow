from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    # 根目录直接重定向到登录页面
    path('', RedirectView.as_view(url='/login/', permanent=False)),
]