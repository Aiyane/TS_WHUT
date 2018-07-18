#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# forms.py
"""
模块功能: 表单
"""
__author__ = 'Aiyane'


from django import forms


class RegisterForm(forms.Form):
    """
    这是一个注册表单(RegisterForm)的类，该类继承于Form类，
    接受一个POST网页请求(request.POST)参数，该类有一个is_valid方法，
    用于检验Key对应值得基本格式是否出错，若出错则返回False，
    无误则返回True。
    """
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, min_length=2, max_length=10)
    password = forms.CharField(required=True, min_length=5, max_length=16)


class EmailForm(forms.Form):
    email = forms.EmailField(required=True)


class LoginForm(forms.Form):
    """
    这是一个登录表单(LoginForm)的类，该类继承于Form类，
    接受一个POST网页请求(request.POST)参数，该类有一个is_valid方法，
    用于检验Key对应值得基本格式是否出错，若出错则返回False，
    无误则返回True.以下方法中Key必须与前端传过来的Key相同
    """
    username = forms.CharField(
        required=True, min_length=2, max_length=10)
    password = forms.CharField(required=True, min_length=5, max_length=16)
