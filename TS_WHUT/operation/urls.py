#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# urls.py
"""
模块功能: operation路由
"""
__author__ = 'Aiyane'
from .views import ActiveUserView, RegisterView, ResetView,  ModifyPwdView, LoginView


from django.urls import path

urlpatterns = [
    path('active/<str:active_code>', ActiveUserView.as_view(), name="user_active"),
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('reset/<str:active_code>', ResetView.as_view(), name="reset_pwd"),
    path('modify_pwd/', ModifyPwdView.as_view(), name="modeify_pwd"),
]
