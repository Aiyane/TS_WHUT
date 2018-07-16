"""
后台管理界面显示
"""
import xadmin
from xadmin import views
from .models import (UserProfile, EmailVerifyRecord,
                     BannerModel, GroupImage, ImageModel)


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


@xadmin.sites.register(views.CommAdminView)
class GlobalSetting(object):
    site_title = "图说理工后台管理系统"
    site_footer = "图说理工在线网"
    menu_style = 'Readable'


class UserProfileAdmin(object):
    list_display = ['username', 'email', 'is_staff',
                    'mobile', 'number', 'gender', 'birthday']
    search_fields = ['number', 'email', 'username', 'mobile']
    list_filter = ['is_staff']


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'send_email', 'send_type', 'send_time']
    search_fields = ['send_email', 'code']
    list_filter = ['send_time', 'send_type']


class BannerModelAdmin(object):
    list_display = ['title', 'url', 'add_time', 'index']
    search_fields = ['title']
    list_filter = ['add_time', 'index']


class GroupImageAdmin(object):
    list_display = ['name', 'add_time', 'image']
    search_fields = ['name']
    list_filter = ['name']


class ImageModelAdmin(object):
    list_display = ['if_active', 'desc', 'user', 'pattern', 'add_time']
    search_fields = ['desc']
    list_filter = ['pattern', 'if_active']


xadmin.site.unregister(UserProfile)
xadmin.site.register(UserProfile, UserProfileAdmin)
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(BannerModel, BannerModelAdmin)
xadmin.site.register(GroupImage, GroupImageAdmin)
xadmin.site.register(ImageModel, ImageModelAdmin)
