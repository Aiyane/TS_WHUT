"""
后台管理界面显示
"""
from django.contrib import admin
from .models import (UserProfile, EmailVerifyRecord,
                     BannerModel, GroupImage, ImageModel)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'mobile', 'number', 'gender', 'birthday']
    search_fields = ['number', 'email', 'username', 'mobile']
    list_filter = ['is_staff']

class EmailVerifyRecordAdmin(admin.ModelAdmin):
    list_display = ['code', 'send_email', 'send_type', 'send_time']
    search_fields = ['send_email', 'code']
    list_filter = ['send_time', 'send_type']

class BannerModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'add_time', 'index']
    search_fields = ['title']
    list_filter = ['add_time', 'index']


class GroupImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'add_time', 'image']
    search_fields = ['name']
    list_filter = ['name']

class ImageModelAdmin(admin.ModelAdmin):
    list_display = ['if_active', 'desc', 'user', 'pattern', 'add_time']
    search_fields = ['desc']
    list_filter = ['pattern', 'if_active']

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
admin.site.register(BannerModel, BannerModelAdmin)
admin.site.register(GroupImage, GroupImageAdmin)
admin.site.register(ImageModel, ImageModelAdmin)