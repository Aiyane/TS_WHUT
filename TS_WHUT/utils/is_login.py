#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# is_login.py
"""
模块功能: 判断是否登录
"""
__author__ = 'Aiyane'
from .AltResponse import AltHttpResponse
import json


def is_login(func):  # 我在这里写了一个装饰器，可以在方法中对权限判断
    def is_method(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(self, request, *args, **kwargs)
        else:
            response = AltHttpResponse(json.dumps({"error": "用户未登录"}))
            response.status_code =404
            return response
    return is_method
