# Generated by Django 2.0.5 on 2018-07-16 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagemodel',
            name='cates',
        ),
    ]
