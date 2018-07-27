from django.shortcuts import render
from django.views.generic.base import View
from django.http import QueryDict
import imghdr
import json

from Users.models import (ImageModel, GroupImage, UserProfile, LikeShip, Collection, Follow,
                          BannerModel, FolderImage, Folder, Comment)
from operation.models import UserMessage
from utils.is_login import is_login
from utils.AltResponse import AltHttpResponse


class ImageView(View):
    @is_login
    def post(self, request):
        """上传图片
        url:
            /image
        method:
            POST
        params:
            :image (FILES)
            :desc (formData 描述)
            :cates (formData 分类字符串)
            :name (formData 名字)
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
                "error": "没有图片文件"
            }
        """
        image = request.FILES.get("image")
        if not image:
            response = AltHttpResponse(json.dumps({"error": "没有图片文件"}))
            response.status_code = 400
            return response

        desc = request.POST.get("desc")
        user = request.user
        cate_str = request.POST.get("cates")
        name = request.POST.get('name')
        image = ImageModel(image=image, desc=desc, user=user,
                           cates=cate_str, name=name)
        image.save()
        user = request.user
        user.upload_nums += 1
        user.save()
        pattern = imghdr.what(image.image.path)
        image.pattern = pattern
        image.save()

        cates = cate_str.split(" ")
        if cates:
            for cate in cates:
                GroupImage(name=cate, image=image).save()

        return AltHttpResponse(json.dumps({"status": "true"}))

    @is_login
    def delete(self, request):
        """删除图片
        url:
            /image
        method:
            DELETE
        params:
            *:image-id (formData)
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
                "error": "没有图片文件"
            }
        """
        put = QueryDict(request.body)
        image_id = put.get("image-id")
        image = ImageModel.objects.get(id=image_id)
        user = request.user
        user.upload_nums -= 1
        user.save()
        if image:
            if image.user == request.user:
                image.delete()
                return AltHttpResponse(json.dumps({"status": "true"}))
            else:
                response = AltHttpResponse(json.dumps({"error": "不是上传用户"}))
                response.status_code = 400
                return response
        else:
            response = AltHttpResponse(json.dumps({"error": "没有该图片"}))
            response.status_code = 404
            return response

    def get(self, request):
        """获得一定数量的缩略图片_按时间倒序
        url:
            /image
        method:
            GET 
        params:
            *:num (url)
            *:page (分页)
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "like": int,
                    "user_image": str, (用户头像)
                    "user_id": int,
                    "cates": str,
                    "collection": int,
                    "height": int,
                    "width": int,
                    "download_nums": int,
                    "name": str,
                    "if_like": str,
                    "if_collect": str,
                    "if_follow": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        num = int(request.GET.get("num"))
        page = int(request.GET.get("page"))
        images = ImageModel.objects.filter(if_active=True)[::-1]

        if not num or not page:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

        start = (page-1)*num
        contacts = images[start: start+num]
        datas = []
        if contacts:
            try:
                for image in contacts:
                    user_url = image.user.image.url
                    like = 'false'
                    collect = 'false'
                    follow = 'false'
                    user = request.user
                    if LikeShip.objects.filter(user=user, image=image):
                        like = 'true'
                    if Collection.objects.filter(user=user, image=image):
                        collect = 'true'
                    if Follow.objects.filter(fan=user, follow=image.user):
                        follow = 'true'
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
                        "desc": image.desc,
                        "user": image.user.username,
                        "user_image": user_url,
                        "user_id": image.user.id,
                        "pattern": image.pattern,
                        "like": image.like_nums,
                        "cates": image.cates,
                        "collection": image.collection_nums,
                        "height": image.image.height,
                        "width": image.image.width,
                        "download_nums": image.download_nums,
                        "name": image.name,
                        "if_like": like,
                        "if_collect": collect,
                        "if_follow": follow,
                    }
                    datas.append(data)
            except:
                pass
        return AltHttpResponse(json.dumps(datas))


class ImageCateView(View):
    def get(self, request):
        """获取一定数量的缩略图片_按图片种类_时间倒序
        url:
            /image/cate
        method:
            GET 
        params:
            *:num (url)
            *:page (分页)
            *:name (种类名)
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "like": int,
                    "cates": str,
                    "user_id": int,
                    "collection": int,
                    "height": int,
                    "user_image": str,
                    "width": int,
                    "download_nums": int,
                    "name": str,
                    "if_like": str,
                    "if_collect": str,
                    "if_follow": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        name = request.GET.get("name")
        num = int(request.GET.get("num"))
        page = int(request.GET.get("page"))
        if not num or not page:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

        if name:
            start = (page-1)*num
            groups = GroupImage.objects.filter(
                name=name)[::-1][start:start+num]
            datas = []
            for group in groups:
                image = group.image
                if image and image.if_active:
                    user_url = image.user.image.url
                    like = 'false'
                    collect = 'false'
                    follow = 'false'
                    user = request.user
                    if LikeShip.objects.filter(user=user, image=image):
                        like = 'true'
                    if Collection.objects.filter(user=user, image=image):
                        collect = 'true'
                    if Follow.objects.filter(fan=user, follow=image.user):
                        follow = 'true'
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
                        "desc": image.desc,
                        "user": image.user.username,
                        "pattern": image.pattern,
                        "like": image.like_nums,
                        "collection": image.collection_nums,
                        "user_image": user_url,
                        "user_id": image.user.id,
                        "cates": image.cates,
                        "height": image.image.height,
                        "width": image.image.width,
                        "download_nums": image.download_nums,
                        "name": image.name,
                        "if_like": like,
                        "if_collect": collect,
                        "if_follow": follow,
                    }
                    datas.append(data)
            return AltHttpResponse(json.dumps(datas))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class ImagePattern(View):
    def get(self, request):
        """获取一定数量的缩略图片_按图片格式_时间倒序
        url:
            /image/pattern
        method:
            GET 
        params:
            *:num (url)
            *:page
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "like": int,
                    "collection": int,
                    "user_image": str
                    "cates": str,
                    "user_id": int,
                    "height": int,
                    "width": int,
                    "download_nums": int,
                    "name": str,
                    "if_like": str,
                    "if_collect": str,
                    "if_follow": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        pattern = request.GET.get("pattern")
        num = int(request.GET.get("num"))
        page = int(request.GET.get("page"))
        if not num or page:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

        if pattern:
            start = (page-1)*num
            images = ImageModel.objects.filter(pattern=pattern,
                                               if_active=True)[::-1][start:start+num]
            datas = []
            for image in images:
                if image and image.if_active:
                    user_url = image.user.image.url
                    like = 'false'
                    collect = 'false'
                    follow = 'false'
                    user = request.user
                    if LikeShip.objects.filter(user=user, image=image):
                        like = 'true'
                    if Collection.objects.filter(user=user, image=image):
                        collect = 'true'
                    if Follow.objects.filter(fan=user, follow=image.user):
                        follow = 'true'
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
                        "desc": image.desc,
                        "cates": image.cates,
                        "user": image.user.username,
                        "pattern": image.pattern,
                        "like": image.like_nums,
                        "user_id": image.user.id,
                        "collection": image.collection_nums,
                        "user_image": user_url,
                        "height": image.image.height,
                        "width": image.image.width,
                        "download_nums": image.download_nums,
                        "name": image.name,
                        "if_like": like,
                        "if_collect": collect,
                        "if_follow": follow,
                    }
                    datas.append(data)
            return AltHttpResponse(json.dumps(datas))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class ImageUser(View):
    def get(self, request):
        """获取一定数量的缩略图片_按上传者_时间倒序
        url:
            /image/user
        method:
            GET 
        params:
            *:num (url)
            *:id (用户id)
            *:page
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "like": int,
                    "user_image": str,
                    "collection": int,
                    "cates": str,
                    "height": int,
                    "width": int,
                    "download_nums": int,
                    "name": str,
                    "if_like": str,
                    "if_collect": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        user_id = request.GET.get("id")
        num = int(request.GET.get("num"))
        page = int(request.GET.get("page"))
        if not num or not page:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

        if user_id:
            user = UserProfile.objects.get(id=user_id)
            start = (page-1)*num
            images = ImageModel.objects.filter(user=user,
                                               if_active=True).order_by[::-1][start:start+num]
            datas = []
            for image in images:
                if image and image.if_active:
                    user_url = image.user.image.url
                    like = 'false'
                    collect = 'false'
                    r_user = request.user
                    if LikeShip.objects.filter(user=r_user, image=image):
                        like = 'true'
                    if Collection.objects.filter(user=r_user, image=image):
                        collect = 'true'
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
                        "desc": image.desc,
                        "user": image.user.username,
                        "pattern": image.pattern,
                        "cates": image.cates,
                        "like": image.like_nums,
                        "collection": image.collection_nums,
                        "height": image.image.height,
                        "width": image.image.width,
                        "download_nums": image.download_nums,
                        "user_image": user_url,
                        "name": image.name,
                        "if_like": like,
                        "if_collect": collect,
                    }
                    datas.append(data)
            return AltHttpResponse(json.dumps(datas))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class ImageLike(View):
    @is_login
    def get(self, request):
        """登录状态下获取一定数量的已点赞的缩略图片
        url:
            /image/like
        method:
            GET 
        params:
            *:num (url)
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "cates": str,
                    "pattern": str,
                    "like": int,
                    "collection": int,
                    "user_image": str,
                    "height": int,
                    "width": int,
                    "download_nums": int,
                    "name": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        num = int(request.GET.get("num"))
        if not num:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        likes = LikeShip.objects.filter(user=user)[:num]
        datas = []
        for like in likes:
            image = like.image
            user_url = image.user.image.url
            data = {
                "id": image.id,
                "image": image.image['avatar'].url,
                "desc": image.desc,
                "user": image.user.username,
                "pattern": image.pattern,
                "cates": image.cates,
                "like": image.like_nums,
                "collection": image.collection_nums,
                "height": image.image.height,
                "width": image.image.width,
                "user_image": user_url,
                "download_nums": image.download_nums,
                "name": image.name,
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """点赞某图片
        url:
            /image/like
        method:
            POST
        params:
            *:image-id
        success:
            status_code: 200
            json={
                "status": "true"
            }
        success:
            status_code: 200
            json={
                "status": "已点赞"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未审查"
            }
        """
        user = request.user
        image_id = request.POST.get("image-id")
        print(image_id)
        if image_id:
            image = ImageModel.objects.get(id=int(image_id))
            if not image.if_active:
                response = AltHttpResponse(json.dumps({"error": "图片未审查"}))
                response.status_code = 404
                return response
            if LikeShip.objects.filter(user=user, image=image):
                return AltHttpResponse(json.dumps({"status": "已点赞"}))
            image.like_nums += 1
            image_user = image.user
            image_user.like_nums += 1
            image_user.save()
            like = LikeShip(user=user, image=image)
            like.save()
            image.save()
            return AltHttpResponse(json.dumps({"status": "true"}))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

    @is_login
    def delete(self, request):
        """取消点赞
        url:
            /image/like
        method:
            DELETE 
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        put = QueryDict(request.body)
        image_id = put.get("image-id")
        image = ImageModel.objects.get(id=image_id)
        image.like_nums -= 1
        image.save()
        LikeShip.objects.filter(user=user, image=image)[0].delete()
        return AltHttpResponse(json.dumps({"status": "true"}))


class ImageCollect(View):
    @is_login
    def get(self, request):
        """登录状态下获取一定数量的已收藏的缩略图片
        url:
            /image/collect
        method:
            GET 
        params:
            *:num (url)
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "cates": str,
                    "like": int,
                    "collection": int,
                    "height": int,
                    "width": int,
                    "user_image": str,
                    "download_nums": int,
                    "name": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        user = request.user
        user = request.user
        num = int(request.GET.get("num"))
        if not num:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        collects = Collection.objects.filter(user=user)[:num]
        datas = []
        for collect in collects:
            image = collect.image
            user_url = image.user.image.url
            data = {
                "id": image.id,
                "image": image.image['avatar'].url,
                "desc": image.desc,
                "user": image.user.username,
                "pattern": image.pattern,
                "cates": image.cates,
                "like": image.like_nums,
                "collection": image.collection_nums,
                "height": image.image.height,
                "width": image.image.width,
                "user_image": user_url,
                "download_nums": image.download_nums,
                "name": image.name,
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """收藏某图片
        url:
            /image/collect
        method:
            POST
        params:
            *:image-id 
        success:
            status_code: 200
            json={
                "status": "true"
            }
        success:
            status_code: 200
            json={
                "status": "已收藏"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未审查"
            }
        """
        user = request.user
        image_id = request.POST.get("image-id")
        if image_id:
            image = ImageModel.objects.get(id=image_id)
            if not image.if_active:
                response = AltHttpResponse(json.dumps({"error": "图片未审查"}))
                response.status_code = 404
                return response
            if Collection.objects.filter(user=user, image=image):
                return AltHttpResponse(json.dumps({"status": "已收藏"}))
            image.collection_nums += 1
            image_user = image.user
            image_user.collection_nums += 1
            image_user.save()
            image.save()
            collect = Collection(user=user, image=image)
            collect.save()
            return AltHttpResponse(json.dumps({"status": "true"}))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response

    @is_login
    def delete(self, request):
        """取消收藏
        url:
            /image/collect
        method:
            DELETE
        params:
            *:num (url)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        """
        user = request.user
        put = QueryDict(request.body)
        image_id = put.get("image-id")
        image = ImageModel.objects.get(id=image_id)
        image.collection_nums -= 1
        image.save()
        Collection.objects.filter(user=user, image=image)[0].delete()
        return AltHttpResponse(json.dumps({"status": "true"}))


class Banner(View):
    def get(self, request):
        """获取轮播图
        url:
            /image/banner/
        method:
            GET
        success:
            status_code: 200
            json=[
                {
                    "title": str,
                    "image": str, (src的url)
                    "target": str, (url)
                    "index": int
                }
            ]
        """
        banners = BannerModel.objects.filter(if_show=True)
        datas = []
        for banner in banners:
            data = {
                "title": banner.title,
                "image": banner.image.url,
                "target": banner.url,
                "index": banner.index
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))


class Download(View):
    @is_login
    def get(self, request):
        """下载原图
        url:
            /image/download/
        method:
            GET
        params:
            *:id (图片id)
        success:
            status_code: 200
            json={
               "id": int,
                "image": str,
                "desc": str,
                "user": str,
                "pattern": str,
                "like": int,
                "user_image": str, (用户头像)
                "cates": str,
                "collection": int,
                "height": int,
                "width": int,
                "download": int (下载量),
                "name": str,
            }
        failure:
            status_code: 404
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未审查"
            }
        """
        image_id = int(request.GET.get("id"))
        if not image_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        image = ImageModel.objects.get(id=image_id)
        if not image.if_active:
            response = AltHttpResponse(json.dumps({"error": "图片未审查"}))
            response.status_code = 404
            return response
        user_url = image.user.image.url
        data = {
            "id": image.id,
            "image": image.image.url,
            "desc": image.desc,
            "user": image.user.username,
            "user_image": user_url,
            "pattern": image.pattern,
            "like": image.like_nums,
            "cates": image.cates,
            "collection": image.collection_nums,
            "height": image.image.height,
            "width": image.image.width,
            "download_nums": image.download_nums,
            "name": image.name,
        }
        image.download_nums += 1
        image.save()
        image_user = image.user 
        image_user.download_nums += 1
        image_user.save()
        return AltHttpResponse(json.dumps(data))


class GetImage(View):
    def get(self, request):
        """通过图片id获取低质量图片
        url:
            /image/id/
        method:
            GET 
        params:
            *:id
        success:
            status_code: 200
            json={
                "id": int,
                "image": str,
                "desc": str,
                "user": str,
                "pattern": str,
                "cates": str,
                "like": int,
                "collection": int,
                "height": int,
                "width": int,
                "user_image": str,
                "download_nums": int,
                "name": str,
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未审查"
            }
        """
        image_id = int(request.GET.get('id'))
        if not image_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        image = ImageModel.objects.get(id=int(image_id))
        if not image.if_active:
            response = AltHttpResponse(json.dumps({"error": "图片未审查"}))
            response.status_code = 404
            return response
        user_url = image.user.image.url
        data = {
            "id": image.id,
            "image": image.image.url,
            "desc": image.desc,
            "user": image.user.username,
            "pattern": image.pattern,
            "cates": image.cates,
            "like": image.like_nums,
            "user_image": user_url,
            "collection": image.collection_nums,
            "height": image.image.height,
            "width": image.image.width,
            "download_nums": image.download_nums,
            "name": image.name,
        }
        return AltHttpResponse(json.dumps(data))


class ImageFolder(View):
    @is_login
    def get(self, request):
        """获得该收藏夹全部图片
        url:
            /image/folder/
        method:
            GET 
        params:
            *:id (收藏夹id)
        success:
            status_code: 200
            json=[
                {
                    "id": int,
                    "image": str,
                    "desc": str,
                    "user": str,
                    "pattern": str,
                    "cates": str,
                    "like": int,
                    "collection": int,
                    "height": int,
                    "width": int,
                    "user_image": str,
                    "download_nums": int,
                    "name": str,
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "不能查看其他用户收藏"
            }
        """
        folder_id = request.GET.get("id")
        if not folder_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        folder = Folder.objects.get(id=int(folder_id))
        if request.user.id != folder.user.id:
            response = AltHttpResponse(json.dumps({"error": "不能查看其他用户收藏"}))
        ships = FolderImage.objects.filter(folder=folder)
        datas = []
        for ship in ships:
            image = ship.image
            user_url = image.user.image.url
            datas.append({
                "id": image.id,
                "image": image.image['avatar'].url,
                "desc": image.desc,
                "user": image.user.username,
                "pattern": image.pattern,
                "cates": image.cates,
                "like": image.like_nums,
                "collection": image.collection_nums,
                "height": image.image.height,
                "width": image.image.width,
                "user_image": user_url,
                "download_nums": image.download_nums,
                "name": image.name,
            })
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """向收藏夹增加一张图片
        url:
            /image/folder/
        method:
            POST
        params:
            *:id (收藏夹id)
            *:image-id (图片id)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        success:
            status_code: 200
            json={
                "status": "已收藏"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "不能修改其他用户收藏"
            }
        """
        folder_id = request.POST.get('id')
        image_id = request.POST.get('image-id')
        if not folder_id or not image_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        folder = Folder.objects.get(id=int(folder_id))
        if folder.user.id != request.user.id:
            response = AltHttpResponse(json.dumps({"error": "不能修改其他用户收藏"}))
            response.status_code = 404
            return response
        image = ImageModel(id=int(image_id))
        if FolderImage.objects.filter(folder=folder, image=image):
                return AltHttpResponse(json.dumps({"status": "已收藏"}))
        FolderImage(image=image, folder=folder).save()
        folder.nums += 1
        folder.save()
        return AltHttpResponse(json.dumps({"status": "true"}))

    @is_login
    def delete(self, request):
        """向收藏夹删除一张图片
        url:
            /image/folder/
        method:
            DELETE
        params:
            *:id (收藏夹id)
            *:image-id (图片id)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        success:
            json={
                "status": "图片已删除"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        failure:
            status_code: 404
            json={
                "error": "不能修改其他用户收藏"
            }
        """
        folder_id = request.POST.get('id')
        image_id = request.POST.get('image-id')
        if not folder_id or not image_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        folder = Folder.objects.get(id=int(folder_id))
        if folder.user.id != request.user.id:
            response = AltHttpResponse(json.dumps({"error": "不能修改其他用户收藏"}))
            response.status_code = 404
            return response
        image = ImageModel(id=int(image_id))
        ship = FolderImage.objects.filter(folder=folder, image=image)
        if not ship:
            return AltHttpResponse(json.dumps({"status": "图片已删除"}))
        else:
            ship[0].delete()
            folder.nums -= 1
            folder.save()
            return AltHttpResponse(json.dumps({"status": "true"}))


class ImageComment(View):
    def get(self, request):
        """获取图片的全部评论
        url:
            /image/comment/
        method:
            GET
        params:
            *:id (图片id)
        success:
            status_code: 200
            json=[
                {
                    "id": int, (评论id)
                    "content": str, (内容)
                    "user": str, (用户名)
                    "like": int,
                    "user_id": int, (用户id)
                    "user_image": str, (用户头像)
                    "add_time": str, (时间)
                    "reply_user": str, (回复用户的用户名)
                    "reply_user_id": int, (回复用户的id)
                }
            ]
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未激活"
            }
        """
        image_id = request.GET.get('id')
        if not image_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        image = ImageModel(id=int(image_id))
        if not image.if_active:
            response = AltHttpResponse(json.dumps({"error": "图片未激活"}))
            response.status_code = 404
            return response
        comments = Comment.objects.filter(image=image)[::-1]
        data = []
        for comment in comments:
            data.append({
                "id": comment.id,
                "content": comment.content,
                "user": comment.user.username,
                "like": comment.like,
                "user": comment.user.id,
                "user_image": comment.user.image.url,
                "add_time": comment.add_time,
                "reply_user": comment.reply.username,
                "reply_user_id": comment.reply.id,
            })
        return AltHttpResponse(json.dumps(data))

    @is_login
    def post(self, request):
        """新增评论
        url:
            /image/comment/
        method:
            POST
        params:
            *:id (图片id)
            *:content (评论内容)
            :user-id (回复用户id)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "图片未激活"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        image_id = request.POST.get("id")
        content = request.POST.get("content")
        user_id = request.POST.get("user-id")
        if not image_id or not content:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        image = ImageModel(id=int(image_id))
        if not image.if_active:
            response = AltHttpResponse(json.dumps({"error": "图片未激活"}))
            response.status_code = 404
            return response
        comment = Comment(user=request.user, image=image, content=content)
        if user_id:
            reply_user = UserProfile.objects.get(id=int(user_id))
            comment.reply = reply_user
            # 保存新的用户信息
            UserMessage(post_user=request.user.username, user=reply_user, message=content).save()
        comment.save()
        return AltHttpResponse(json.dumps({"status": "true"}))

    @is_login
    def delete(self, request):
        """删除一条评论
        url:
            /image/comment/
        method:
            DELETE
        params:
            *:id (评论id)
        success:
            status_code: 200
            json={
                "status": "true"
            }
        failure:
            status_code: 400
            json={
                "error": "参数错误"
            }
        failure:
            status_code: 404
            json={
                "error": "不能删除其他用户评论"
            }
        failure:
            status_code: 404
            json={
                "error": "用户未登录"
            }
        """
        put_get = QueryDict(request.body).get
        comment_id = put_get('id')
        if not comment_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        comment = Comment.objects.get(id=int(comment_id))
        if comment.user.id != request.user.id:
            response = AltHttpResponse(json.dumps({"error": "不能修改其他用户评论"}))
            response.status_code = 404
            return response
        else:
            comment.delete()
            return AltHttpResponse(json.dumps({"status": "true"}))
