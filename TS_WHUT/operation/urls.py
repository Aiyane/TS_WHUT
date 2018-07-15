#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# urls.py
"""
模块功能: operation路由
"""
__author__ = 'whutlhc'
from .views import ActiveUserView, RegisterView, LoginView,ResetView

from django.urls import path

urlpatterns = [
    path('active/<str:active_code>', ActiveUserView.as_view(), name="user_active"),
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('reset/', ResetView.as_view(), name="reset")
]
