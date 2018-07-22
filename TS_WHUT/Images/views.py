from django.shortcuts import render
from django.views.generic.base import View
from django.http import QueryDict
import imghdr
import json

from Users.models import ImageModel, GroupImage, UserProfile, LikeShip, Collection, BannerModel

from utils.is_login import is_login
from utils.AltResponse import AltHttpResponse


class ImageView(View):
    @is_login
    def post(self, request):
        """
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
        image = ImageModel(image=image, desc=desc, user=user, cates=cate_str, name=name)
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
        """
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
        """
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
                    "cates": str,
                    "collection": int,
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
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
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
                    datas.append(data)
            except:
                pass
        return AltHttpResponse(json.dumps(datas))


class ImageCateView(View):
    def get(self, request):
        """
        url:
            /image/cate
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
                    "cates": str,
                    "collection": int,
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
                if image.if_active:
                    data = {
                        "id": image.id,
                        "image": image.image['avatar'].url,  # 缩略图
                        "desc": image.desc,
                        "user": image.user.username,
                        "pattern": image.pattern,
                        "like": image.like_nums,
                        "collection": image.collection_nums,
                        "cates": image.cates,
                        "height": image.image.height,
                        "width": image.image.width,
                        "download_nums": image.download_nums,
                        "name": image.name,
                    }
                    datas.append(data)
            return AltHttpResponse(json.dumps(datas))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class ImagePattern(View):
    def get(self, request):
        """
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
                    "cates": str,
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
                data = {
                    "id": image.id,
                    "image": image.image['avatar'].url,  # 缩略图
                    "desc": image.desc,
                    "cates": image.cates,
                    "user": image.user.username,
                    "pattern": image.pattern,
                    "like": image.like_nums,
                    "collection": image.collection_nums,
                    "height": image.image.height,
                    "width": image.image.width,
                    "download_nums": image.download_nums,
                    "name": image.name,
                }
                datas.append(data)
            return AltHttpResponse(json.dumps(datas))
        else:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response


class ImageUser(View):
    def get(self, request):
        """
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
                    "collection": int,
                    "cates": str,
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
                    "name": image.name,
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
        """
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
                "download_nums": image.download_nums,
                "name": image.name,
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """
        url:
            /image/like
        method:
            POST
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
            image.like_nums += 1
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
        """
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
        """
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
                "download_nums": image.download_nums,
                "name": image.name,
            }
            datas.append(data)
        return AltHttpResponse(json.dumps(datas))

    @is_login
    def post(self, request):
        """
        url:
            /image/collect
        method:
            POST
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
            image.collection_nums += 1
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
        """
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
        """
        url:
            /image/banner
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
        """
        url:
            /image/download
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
        return AltHttpResponse(json.dumps(data))


class GetImage(View):
    def get(self, request):
        """
        url:
            /image/id
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
        iamge_id = int(request.GET.get('id'))
        if not iamge_id:
            response = AltHttpResponse(json.dumps({"error": "参数错误"}))
            response.status_code = 400
            return response
        image = ImageModel.objects.get(id=iamge_id)       
        if not image.if_active:
            response = AltHttpResponse(json.dumps({"error": "图片未审查"}))
            response.status_code = 404
            return response
        data = {
            "id": image.id,
            "image": image.image['replace'].url,
            "desc": image.desc,
            "user": image.user.username,
            "pattern": image.pattern,
            "cates": image.cates,
            "like": image.like_nums,
            "collection": image.collection_nums,
            "height": image.image.height,
            "width": image.image.width,
            "download_nums": image.download_nums,
            "name": image.name,
        }
        return AltHttpResponse(json.dumps(data))
