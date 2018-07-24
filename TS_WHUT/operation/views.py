from django.views.generic.base import View
# 对用户名密码校验，后一个发出一个session登录，登出
from django.contrib.auth import authenticate, login, logout
from utils.send_email import send_register_email
from Users.models import UserProfile, EmailVerifyRecord, GroupImage, Folder
from django.http import QueryDict
from django.contrib.auth.hashers import make_password
from .models import UserMessage
from .forms import LoginForm, RegisterForm, ModifyPwdForm, EmailForm
from utils.AltResponse import AltHttpResponse
from utils.is_login import is_login
import json


class ResetView(View):
    # def get(self, request):
        # return render(request, 'reset.html', {'error': ''})

    def post(self, request):
        email = request.POST.get("email", "")
        user = UserProfile.objects.filter(email=email)[0]
        if user and user.email == email:
            # 保存用户信息
            user_message = UserMessage()
            user_message.user = user
            user_message.message = "图说理工网修改密码"
            user_message.save()

            password1 = request.POST.get("password1", "")
            password2 = request.POST.get("password2", "")
            if password1 == password2:
                user.password = make_password(password1)
                user.save()
                send_register_email(email, "forget")  # 发送验证邮箱
                # return render(request, 'reset.html', {"error": "邮箱"})
            else:
                error = "密码输入不一致"
                # return render(request, "reset.html", {"error": error})
        else:
            error = "没有该用户"
            # return render(request, "reset.html", {"error": error})


class ActiveUserView(View):
    """
    这是一个用户激活逻辑(ActiveUserView)的类,继承于View，该类有一个方法，
    接受一个网页验证请求(request)参数，若用户点击验证网址，
    则返回登录页面(login.html)
    """

    def get(self, request, active_code):
        """
        传入网页的验证码(active_code)是否与邮箱验证表单中的验证码(code)相同，
        相同则返回相关邮箱验证实例。filter与get的区别在于filter遇到表单中属性相同匹配到时不会报错，但是get会报错，
        所以用get时条件最好是该属性值在表单中是唯一的，随机验证码还是不能保证不会出项相同情况。
        """
        all_records = EmailVerifyRecord.objects.filter(
            code=active_code)  # 这里的all_records是多个邮箱验证实例，因为验证码可能相同
        if all_records:
            for record in all_records:
                email = record.send_email
                # 得到一个用户信息邮箱与传来的邮箱验证邮箱相同的用户信息实例
                user = UserProfile.objects.get(email=email)
                user.is_active = True  # 令这个实例中is_active值为True
                user.save()  # 保存用户

            # 返回主页, 验证成功
            login(request, user)
            # return render(request, 'index.html')
        # else:
            # 返回激活页面失效了
            # return render(request, 'register.html', )


class CheckView(View):
    """
    这是一个用户重置密码逻辑(ActiveUserView)的类,继承于View，该类有一个方法，
    接受一个网页验证请求(request)参数，若用户点击重置密码，信息无误则返回密码重置网页，
    否则返回激活失败页面。
    """

    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(
            code=active_code)  # 这里的all_records是多个邮箱验证实例，因为验证码可能相同
        if all_records:
            for record in all_records:
                email = record.send_email
                # 得到一个用户信息邮箱与传来的邮箱验证邮箱相同的用户信息实例
                user = UserProfile.objects.get(email=email)
                # 返回密码重置页面
                pass
                # return render(request, "password_reset.html", {"user": user})
        else:
            # 返回激活页面失效了
            pass


class ModifyPwdView(View):
    """
    修改用户密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        user = request.POST.get("username", "")
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                # 密码不一样
                pass
                # return render(request, "password_reset.html", {"user": user, "msg": "密码不一致!"})
            user = UserProfile.objects.get(username=user)
            user.password = make_password(pwd1)
            user.save()
            # login_type = "success"
            # 修改成功, 返回主页
            login(request, user)
            pass
        else:
            # 密码格式不正确, 返回密码重置页
            pass


class CatesView(View):
    def get(self, request):
        """
        url:
            /cates
        method:
            GET
        params:
            *:num
        success:
            status_code: 200
            json=[
                str (种类名)
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        num = request.GET.get("num")
        if not num:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        groups = GroupImage.objects.all().order_by("-add_time")[:num]
        datas = []
        for group in groups:
            datas.append(group.name)
        return AltHttpResponse(json.dumps(datas))

class GetMsg(View):
    @is_login
    def get(self, request):
        """
        url:
            /message/
        method:
            GET
        success:
            status_code: 200
            json=[
                {
                    "post_user": str, (发送用户用户名)
                    "message": str, (消息内容)
                    "has_read": bool, (是否已读)
                    "add_time": str, (发送时间)
                }
            ]
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        msgs = UserMessage.objects.filter(user=user)[::-1]
        data = []
        for msg in msgs:
            data.append({
                "post_user": msg.post_user,
                "message": msg.message,
                "has_read": msg.has_read,
                "add_time": msg.add_time,
            })
        return AltHttpResponse(json.dumps(data))
