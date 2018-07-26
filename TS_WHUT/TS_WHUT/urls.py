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
from django.urls import path
from django.conf.urls.static import static
from django.conf.urls import include
from django.conf import settings
import xadmin
from operation.views import ActiveUserView, CatesView, GetMsg
from Users.views import (RegisterView, LoginView, GetUserMsgView, UserDownload, UserUpload, UserCommentLike,
                         LogoutView, History, FollowView, IsLogin, Following, FollowNum, FanNum, UserFolder)
from Images.views import (ImageView, ImageCateView, Download, GetImage, ImageFolder,
                          ImagePattern, ImageUser, ImageLike, ImageCollect, Banner, ImageComment)

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
    path('user/is_login/', IsLogin.as_view(), name="is_login"),
    path('user/download/', UserDownload.as_view(), name="user_download"),
    path('user/upload/', UserUpload.as_view(), name="user_upload"),
    path('user/folder/', UserFolder.as_view(), name="user_folder"),
    path('user/comment/like/', UserCommentLike.as_view(), name="comment_like"),


    path('image/', ImageView.as_view(), name="image"),
    path('image/cate/', ImageCateView.as_view(), name="image_cate"),
    path('image/pattern/', ImagePattern.as_view(), name="image_pattern"),
    path('image/user/', ImageUser.as_view(), name="image_like"),
    path('image/like/', ImageLike.as_view(), name="like"),
    path('image/collect/', ImageCollect.as_view(), name="collect"),
    path('image/banner/', Banner.as_view(), name="Banner"),
    path('image/download/', Download.as_view(), name="download"),
    path('image/id/', GetImage.as_view(), name="get_image"),
    path('image/folder/', ImageFolder.as_view(), name="image_folder"),
    path('image/comment/', ImageComment.as_view(), name="image_comment"),

    path('active/<str:active_code>/', ActiveUserView.as_view(), name="user_active"),
    path('cates/', CatesView.as_view(), name="cates"),
    path('message/', GetMsg.as_view(), name="get_message"),
    path('search/', include('haystack.urls'), name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
