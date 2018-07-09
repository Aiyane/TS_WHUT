from django.shortcuts import render
from django.views.generic.base import View


class ActiveUserView(View):
    # get方法, 验证注册用户
    def get(self, request, active_code):
        pass