from django.shortcuts import render
from django.views.generic.base import View
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout  # 对用户名密码校验，后一个发出一个session登录，登出
from django.http import HttpResponse, HttpResponseRedirect  # content_type='application/json'
from utils.send_email import send_register_email
from Users.models import UserProfile, EmailVerifyRecord
from django.contrib.auth.hashers import make_password
from .models import UserMessage
from .forms import LoginForm,RegisterForm,ModifyPwdForm
from django.contrib.auth.models import User

class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        if request.user.is_authenticated():
            auth.logout(request)
            # 登出, 返回主界面
            return AltHttpResponse(json.dumps({"ststus": 'true'}))
        else:
            error = "你尚未登陆,无需登出"
            return AltHttpResponse(json.dumps({"error": error}))

        
class RegisterView(View):
    """
    这是一个注册逻辑(RegisterView)的类，继承于View
    """
    def get(self, request):
        # 进入注册页面  
        return render(request, 'register.html', {"error": ""})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get("email", "")  # 将用户的email与password传入
            username = request.POST.get("username", "")
            user = UserProfile.objects.filter(email=email)
            if user:
                error = "用户已经存在"
                return render(request, "register.html", {'error':error})
                return AltHttpResponse(json.dumps({"error": "邮箱已被注册"}), status_code=400)
            user = UserProfile.objects.filter(username=username)
            if user and user[0].username == username:
                return AltHttpResponse(json.dumps({"error": "用户名已经存在"}), status_code=400)
            pass_word = request.POST.get("password", "")

            user_profile = UserProfile()
            user_profile.username = username
            user_profile.email =email 
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)

            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile
            user_message.message = "欢迎注册图说理工网"
            user_message.save()

            send_register_email(email, "register")  # 发送验证邮箱
            # 已经登录应该返回主界面
            login(request, user_profile)
            return AltHttpResponse(json.dumps({"status": 'true'}))
        else:
            # 注册失败返回注册页面
            return AltHttpResponse(json.dumps({"error": "表单验证失败"}), status_code=400)


class LoginView(View):

    def post(self, request):
        login_form = LoginForm(request.POST)  
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")

            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:  # 验证是否激活
                    auth.login(request, user)
                    return AltHttpResponse(json.dump({"status": 'true'}))
                else:
                    error = "该用户未被激活"
                    return AltHttpResponse(json.dump({"error": error}))
            else:
                error = "用户名或密码错误"
                return AltHttpResponse(json.dump({"error": error}))
        else:
            error = "请正确填写登陆信息"
            return AltHttpResponse(json.dumps({"error": error}))

        
class ResetView(View):
    def get(self, request):
        return render(request, 'reset.html', {'error':''})

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
                return render(request, 'reset.html',{"error": "邮箱"})
            else:
                error = "密码输入不一致"
                return render(request, "reset.html",{"error": error})
        else:
            error = "没有该用户"
            return render(request, "reset.html",{"error": error})

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
        all_records = EmailVerifyRecord.objects.filter(code=active_code)  # 这里的all_records是多个邮箱验证实例，因为验证码可能相同
        if all_records:
            for record in all_records:
                email = record.send_email
                user = UserProfile.objects.get(email=email)  # 得到一个用户信息邮箱与传来的邮箱验证邮箱相同的用户信息实例
                user.is_active = True  # 令这个实例中is_active值为True
                user.save()  # 保存用户

            # 返回主页, 验证成功
            login(request, user)
            return render(request, 'index.html')
        else:
            # 返回激活页面失效了
            return render(request, 'register.html', )


class CheckView(View):
    """
    这是一个用户重置密码逻辑(ActiveUserView)的类,继承于View，该类有一个方法，
    接受一个网页验证请求(request)参数，若用户点击重置密码，信息无误则返回密码重置网页，
    否则返回激活失败页面。
    """
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)  # 这里的all_records是多个邮箱验证实例，因为验证码可能相同
        if all_records:
            for record in all_records:
                email = record.send_email
                user = UserProfile.objects.get(email=email)  # 得到一个用户信息邮箱与传来的邮箱验证邮箱相同的用户信息实例
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
