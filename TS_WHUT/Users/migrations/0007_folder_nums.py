# Generated by Django 2.0.5 on 2018-07-23 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0006_comment_folder_folderimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='nums',
            field=models.IntegerField(default=0, verbose_name='数量'),
        ),
    ]
