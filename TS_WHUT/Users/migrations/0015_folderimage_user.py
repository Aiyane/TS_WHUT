# Generated by Django 2.0.5 on 2018-07-28 07:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0014_auto_20180728_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='folderimage',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
    ]
