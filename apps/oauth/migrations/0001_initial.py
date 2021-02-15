# Generated by Django 3.1.6 on 2021-02-14 06:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.db_utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthQQUser',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='主键ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, db_index=True, verbose_name='修改时间')),
                ('openid', models.CharField(db_index=True, max_length=64, verbose_name='openid')),
                ('user', utils.db_utils.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': 'QQ第三方登录',
                'verbose_name_plural': 'QQ第三方登录',
                'db_table': 'md_oauth_qq',
            },
        ),
    ]