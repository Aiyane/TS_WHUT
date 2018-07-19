"""TS_WHUT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

import xadmin
from operation.views import ActiveUserView, ResetView,  ModifyPwdView, CatesView
from Users.views import (RegisterView, LoginView, GetUserMsgView,
                         LogoutView, History, FollowView, IsLogin, Following, FollowNum, FanNum)
from Images.views import (ImageView, ImageCateView,
                          ImagePattern, ImageUser, ImageLike, ImageCollect, Banner)

urlpatterns = [
    path('admin/', xadmin.site.urls),

    path('user/', RegisterView.as_view(), name="register"),
    path('user/msg/<str:username>/', GetUserMsgView.as_view(), name="get_user_msg"),
    path('user/login/', LoginView.as_view(), name="login"),
    path('user/logout/', LogoutView.as_view(), name="logout"),
    path('user/history/', History.as_view(), name="history"),
    path('user/follow/', FollowView.as_view(), name="follow"),
    path('user/follow/nums/', FollowNum.as_view(), name="follow_nums"),
    path('user/fan/nums/', FanNum.as_view(), name="fan_nums"),
    path('user/following/', Following.as_view(), name="following"),
    path('user/islogin/', IsLogin.as_view(), name="is_login"),

    path('image/', ImageView.as_view(), name="image"),
    path('image/cate/', ImageCateView.as_view(), name="image_cate"),
    path('image/pattern/', ImagePattern.as_view(), name="image_pattern"),
    path('image/user/', ImageUser.as_view(), name="image_like"),
    path('image/like/', ImageLike.as_view(), name="like"),
    path('image/collect/', ImageCollect.as_view(), name="collect"),
    path('image/banner/', Banner.as_view(), name="Banner"),

    path('active/<str:active_code>/', ActiveUserView.as_view(), name="user_active"),
    path('cates/', CatesView.as_view(), name="cates"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
