from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField('手机号', max_length=11, unique=True)

    create_time = models.DateTimeField('创建时间', auto_now_add=True, db_index=True, editable=False)
    update_time = models.DateTimeField('修改时间', auto_now=True, db_index=True, editable=False)
    is_deleted = models.BooleanField('是否删除', default=False, null=False)

    class Meta:
        db_table = 'md_users'
        verbose_name_plural = verbose_name = '用户表'
