#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# views.py
"""
模块功能: /user路由开头的API, 与用户相关的各种操作
"""
__author__ = 'Aiyane'


from django.contrib.auth.hashers import make_password
from django.views.generic.base import View
from django.http import QueryDict
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
import json

from .models import UserProfile, ImageModel, DownloadShip, Follow
from operation.models import UserMessage

from utils.send_email import send_register_email
from utils.AltResponse import AltHttpResponse
from utils.is_login import is_login


class RegisterView(View):
    @is_login
    def get(self, request):
        """
        url:
            /user
        method:
            GET
        success:
            status_code: 200
            json={
                "id": int,
                "username": str,
                "email": str,
                "gender": str, (male或female)
                "image": str, (url)
                "birthday": data,
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
            "image": user.image.url,
            "birthday": user.birthday,
        }
        return AltHttpResponse(json.dumps(data))

    def post(self, request):
        """
        url:
            /user
        method:
            POST
        params:
            *:username (formData)
            *:password (formData)
            *:email (formData)
        ret:
            success:
                status_code=200
                json={
                    "status": "true",
                    "message": "请前往邮箱验证"
                }
            failure:
                status_code=400
                json={
                    "error": "邮箱已被注册"
                }
            failure:
                status_code=400
                json={
                    "error": "用户名已经存在"
                }
        """
        email = request.POST.get("email", "")
        emails = list(UserProfile.objects.all().values_list('email'))
        if email in emails:
            user = UserProfile.objects.get(email=email)
            response = AltHttpResponse(json.dumps({"error": "邮箱已被注册"}))
            response.status_code = 400
            return response

        username = request.POST.get("username", "")
        usernames = list(UserProfile.objects.all().values_list('username'))
        if username in usernames:
            response = AltHttpResponse(json.dumps({"error": "用户名已经存在"}))
            response.status_code = 400
            return response

        register_form = RegisterForm(request.POST)
        if not register_form.is_valid:
            response = AltHttpResponse(json.dumps({"error": "格式错误"}))
            response.status_code = 400
            return response

        pass_word = request.POST.get("password", "")
        user_profile = UserProfile()
        user_profile.username = username
        user_profile.email = email
        user_profile.is_active = False
        user_profile.password = pass_word
        user_profile.save()

        # 写入欢迎注册消息
        user_message = UserMessage()
        user_message.user = user_profile
        user_message.message = "欢迎注册图说理工网"
        user_message.save()

        # 发送验证邮箱
        send_register_email(email, "register")

        # 登录
        login(request, user_profile)
        return AltHttpResponse(json.dumps({"status": 'true', "message": "请前往邮箱验证"}))

    @is_login
    def delete(self, request):
        """
        url:
            /user
        method:
            DELETE
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        request.user.delete()
        return AltHttpResponse(json.dumps({"status": "true"}))

    @is_login
    def put(self, request):
        """
        url:
            /user
        method:
            PUT 
        params:
            :username (formData)
            :email (formData)
            :image (formData)
            :gender (formData)
            :birthday (formData)
            :password (formData)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        success:
            status_code: 200
            json={
                "status": "true",
                "message": "请前往邮箱验证"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 400
            json={
                "error": "邮箱已经存在"
            }
        failure:
            status_code: 400
            json={
                "error": "用户名已经存在"
            }
        """
        user = request.user
        put_get = QueryDict(request.body).get

        # 邮箱必须唯一
        email = put_get("email", "")
        change_eamil = False
        if email:
            if UserProfile.objects.get(email=email):
                response = AltHttpResponse(json.dumps({"error": "邮箱已经存在"}))
                response.status_code = 400
                return response
            else:
                # 写入重置邮箱消息
                user_message = UserMessage()
                user_message.user = user
                user_message.message = user.username + "修改邮箱为:" + email
                user_message.save()

                # 发送验证邮箱
                send_register_email(email, "update_email")
                change_eamil = True

        # 用户名必须唯一
        username = put_get("username", "")
        if username:
            if UserProfile.objects.get(username=username):
                response = AltHttpResponse(json.dumps({"hrror": "用户名已经存在"}))
                response.status_code = 400
                return response
            else:
                user.username = username

        image = request.files.get("image", "")
        if image:
            user.image = image
        gender = put_get("gender", "")
        if gender:
            user.gender = gender
        birthday = put_get("birthday", "")
        if birthday:
            user.birthday = birthday
        password = put_get("password", "")
        if password:
            user.password = make_password(password)
        user.save()

        if change_eamil:
            return AltHttpResponse(json.dumps({"status": "true", "message": "请前往邮箱验证"}))
        else:
            return AltHttpResponse(json.dumps({"status": "true"}))


class LoginView(View):
    def post(self, request):
        """
        url:
            /user/login
        method:
            POST
        params:
            *:username (formData)
            *:password (formData)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 400
            json={
                "error": "用户名或密码错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未激活"
            }
        """
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)

        if user is None:
            response = AltHttpResponse(json.dumps({"error": "用户名或密码错误"}))
            response.status_code = 400
            return response
        elif user.is_active:
            login(request, user)
            return AltHttpResponse(json.dumps({"status": "true"}))
        else:
            response = AltHttpResponse(json.dumps({"error": "用户未激活"}))
            response.status_code = 404
            return response


class GetUserMsgView(View):
    def get(self, request, username):
        """
        url:
            /user/msg/<username>
        method:
            GET
        params:
            *:username (path)
        success:
            status_code: 200
            json={
                "id": int,
                "username": str,
                "email": str,
                "gender": str, (male或female)
                "image": str, (url)
            }
        failure:
            status_code: 400
            json={
                "error": "用户不存在"
            }
        """
        user = UserProfile.objects.get(username=username)
        if user and user.username == username:
            data = {
                "id": user.id,
                "username": username,
                "email": user.email,
                "image": user.image.url,
                "gender": user.gender,
            }
            return AltHttpResponse(json.dumps(data))
        else:
            response = AltHttpResponse(json.dumps({"error": "用户不存在"}))
            response.status_code = 400
            return response


class LogoutView(View):
    @is_login
    def post(self, request):
        """
        url:
            /user/logout
        method:
            POST
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        logout(request)
        return AltHttpResponse(json.dumps({"status": "true"}))


class History(View):
    @is_login
    def post(self, request):
        """ 按照时间倒序
        url:
            /user/logout
        method:
            POST
        params:
            :num (formData)
        success:
            status_code: 200
            json={
                "download-images":{
                    "id": int,
                    "image": str, (url)
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "like": int,
                    "collection": int,
                    "height": int,
                    "width": int,
                },
                "upload-images":{
                    "id": int,
                    "image": str, (url)
                    "is-active": str,
                    "desc": str,
                    "user": str, (上传者用户名)
                    "pattern": str, (格式)
                    "like": int,
                    "collection": int,
                    "height": int,
                    "width": int,
                }
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        num = int(request.POST.get("num"))
        images = ImageModel.objects.filter(
            user=user).order_by("-add_time")[:num]
        ships = DownloadShip.objects.filter(
            user=user).order_by("-add_time")[:num]
        download_images = []
        upload_images = []
        for ship in ships:
            data = {
                "id": ship.image.id,
                "image": ship.image.image.url,
                "desc": ship.image.desc,
                "user": ship.image.user.username,
                "pattern": ship.image.pattern,
                "like": ship.image.like_nums,
                "collection": ship.image.collection_nums,
                "height": ship.image.image.height,
                "width": ship.image.image.width,
            }
            download_images.append(data)
        for image in images:
            data = {
                "id": image.id,
                "image": image.image.url,
                "is-active": image.is_active,
                "desc": image.desc,
                "user": image.user.username,
                "pattern": image.pattern,
                "like": image.like_nums,
                "collection": image.collection_nums,
                "height": image.image.height,
                "width": image.image.width,
            }
            upload_images.append(data)
        return AltHttpResponse(json.dumps({"download-images": download_images, "upload-images": upload_images}))


class FollowView(View):
    @is_login
    def get(self, request):
        """查询粉丝名单
        url:
            /user/follow
        method:
            GET
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "username": str,
                    "image": str, (url)
                    "if_sign": str,
                },
            ]
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        follows = Follow.objects.filter(follow=user)
        datas = []
        for follow in follows:
            fan = follow.fan
            data = {
                "id": fan.id,
                "username": fan.username,
                "image": fan.image.url,
                "if_sign": fan.if_sign
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """关注他人
        url:
            /user/follow
        method:
            POST
        params:
            *:id
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        user = request.user
        user.follow_nums += 1
        user_id = int(request.POST.get("id"))
        if user_id:
            follow = UserProfile.objects.get(id=user_id)
            follow.fan_nums += 1
            Follow(fan=user, follow=follow).save()
            return AltHttpResponse(json.dumps({"status": "true"}))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

    @is_login
    def delete(self, request):
        """
        url:
            /user/follow
        method:
            DELETE
        params:
            *:id
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        user = request.user
        user.follow_nums -= 1
        user_id = int(request.POST.get("id"))
        if user_id:
            follow = UserProfile.objects.get(id=user_id)
            follow.fan_nums -= 1
            Follow.objects.filter(fan=user, follow=follow)[0].delete()
            return AltHttpResponse(json.dumps({"status": "true"}))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class Following(View):
    @is_login
    def get(self, request):
        """
        url:
            /user/following
        method:
            GET
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "username": str,
                    "image": str, (url)
                    "if_sign": str,
                },
            ]
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        follows = Follow.objects.filter(fan=user)
        datas = []
        for fols in follows:
            follow = fols.follow
            data = {
                "id": follow.id,
                "username": follow.username,
                "image": follow.image.url,
                "if_sign": follow.if_sign
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))


class IsLogin(View):
    @is_login
    def get(self, request):
        """
        url:
            /user/is_login/
        method:
            GET 
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        return AltHttpResponse(json.dumps({"status": "true"}))


class FollowNum(View):
    @is_login
    def get(self, request):
        """
        url:
            /user/follow/nums/
        method:
            GET 
        success:
            status_code: 200
            json={
                "num": int
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        return AltHttpResponse(json.dumps({"num": user.follow_nums}))


class FanNum(View):
    @is_login
    def get(self, request):
        """
        url:
            /user/fan/nums/
        method:
            GET 
        success:
            status_code: 200
            json={
                "num": int
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        return AltHttpResponse(json.dumps({"num": user.fan_nums}))
