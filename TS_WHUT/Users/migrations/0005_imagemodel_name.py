# Generated by Django 2.0.5 on 2018-07-22 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0004_auto_20180720_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagemodel',
            name='name',
            field=models.CharField(default='', max_length=20, verbose_name='名字'),
        ),
    ]
