from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate
from django.http import HttpResponse
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

class Index(View):
    def get(self, request):
        return render(request, 'index.html')
   

class LookUserInfo(View):
    """
    查看用户详细信息的LookUserInfo类
    用户状态：非登陆
    非登陆的用户查看其他用户的信息
    给用户展示id:用户标识码,username:用户名,image:头像,
    """
    def get(self, request):
        username = request.POST.get("username","")
        user = UserProfile.objects.filter(username=username)
        if user:
            user_id = user.id
            user_img = user.image
            email = user.email
            user_info = {
                "id": user_id, 
                "username": username, 
                "image": username, 
                "email": email
            }
            return AltHttpResponse(json.dumps(user_info))
        else:
            error = "操作失败,无法查看"
            return AltHttpResponse(json.dumps({"error": error}))

            
class HistoryView(View):
    """
    用户历史记录HistoryView类
    用户状态：登陆
    用户查看的上传和下载的记录
    """
    def get(self, request):
        return AltHttpResponse(json.dumps({"status": 'true'}))
    
    def post(self, request):
        if is_authenticated():
            image_id = request.user.image_id
            id = request.user.id
            desc = request.user.desc
            like_num = request.user.like_num
            pattern = request.user.pattern
            cates = request.user.cates
            image_message = {
                "image-id": image_id, 
                "id": id, 
                "desc": desc, 
                "like-num": like_num, 
                "pattern": pattern, 
                "cates": cates
            }
            return AltHttpResponse(json.dumps(image_message))

        else:
            error = "查询失败"
            return AltHttpResponse(json.dumps({"error": error}))


class UploadView(View):
    """
    用户上传图片UploadView类
    用户状态：登陆
    """
    def post():
        if request.user.is_authenticated():
            id = request.user.id
            cate = request.POST.get("cates": "")
            cates = cate.split()         # 获取图片所属的所有种类



class DeleteView(VIew):
    def delete(request):
        
        

