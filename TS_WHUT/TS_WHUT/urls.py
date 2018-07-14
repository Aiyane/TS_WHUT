"""TS_WHUT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from login import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/$', include('Users.urls')),  # 配置用户页url
  # url(r'^operation/$', include('operation.urls')),
    url(r'^index/$', views.index),      # 主页
    url(r'^login/$', views.login),      # 登陆
    url(r'^register/$', views.register),  # 注册
    url(r'^logout/$', views.logout),    # 注销
    url(r'^captcha', include('captcha.urls')),   # 验证码
    url(r'^confirm/$', views.user_confirm),      # 邮箱验证
]
