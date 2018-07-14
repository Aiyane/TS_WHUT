# from django.db import models
# from Users.models import UserProfile
# from datetime import datetime  # 导入当前时间
#
#
# class UserMessage(models.Model):
#     # 网站用户信息
#     post_user = models.CharField(max_length=20, default="图说理工网", verbose_name="发送用户")
#     user = models.ForeignKey(UserProfile, models.CASCADE ,verbose_name="接收用户")
#     message = models.CharField(max_length=500, verbose_name=u"消息内容")
#     has_read = models.BooleanField(default=False, verbose_name=u"是否已读")
#     add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
#
#     class Meta:
#         verbose_name = u"用户消息"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.message
