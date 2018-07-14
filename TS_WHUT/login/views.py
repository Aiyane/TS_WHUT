from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from . import models
from . import forms
import hashlib
import datetime

# Create your views here.

# 密码加密
def hash_code(s, salt='TS_WHUT'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

# 主页
def index(request):
    pass
    return render(request, 'login/index.html')

# 用户登陆模块
def login(request):

    if request.session.get('is_login', None):
        return redirect("/index/")

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "所有字段都必须填写！"

        if login_form.is_valid():    # 表单类自带的数据验证方法
            username = login_form.cleaned_data['username']   # cleaned_data数据字典
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮箱验证！"
                    return render(request, 'login/login.html', locals())

                if user.password == hash_code(password):        # 与加密结果进行对比
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')  # 重定向
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())

# 用户注册模块
def register(request):

    if request.session.get('is_login', None):
        # 登陆状态不允许注册
        return redirect("/index/")

    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写内容"

        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']

            # 判断两次输入的密码是否一致
            if password1 != password2:
                message = "两次输入的密码不同"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)

                # 用户名唯一
                if same_name_user:
                    message = '用户已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)

                # 注册邮箱唯一
                if same_email_user:
                    message = '该邮箱已被注册'
                    return render(request, 'login/register.html', locals())

                # 用过以上初步验证,开始创建新用户
                new_user = models.User()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往邮箱确认'
                return redirect('login/confirm.html', locals())     # 注册完成跳转到登陆页面
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

# 注销登陆
def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    # 清空session中的内容
    request.session.flush()
    return redirect("/index/")

# 创建确认码
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code

# 发送邮件
def send_email(email, code):
    subject = '来自www.baidu.com的邮件等待确认'
    text_content = '欢迎访问百度'
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                   '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# 处理确认请求
def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的请求确认'
        return render(request, 'login/confirm.html', locals())

    create_time = confirm.create_time
    now = datetime.datetime.now()

    if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮箱验证信息已过期，请重新注册！'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '邮箱验证成功,请使用账户登陆！'
        return render(request, 'login/confirm.html', locals())