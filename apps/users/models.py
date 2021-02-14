from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField('手机号', max_length=11, unique=True)
    email_active = models.BooleanField('邮箱状态', default=False)

    create_time = models.DateTimeField('创建时间', auto_now_add=True, db_index=True, editable=False)
    update_time = models.DateTimeField('修改时间', auto_now=True, db_index=True, editable=False)

    class Meta:
        db_table = 'md_users'
        verbose_name_plural = verbose_name = '用户表'
