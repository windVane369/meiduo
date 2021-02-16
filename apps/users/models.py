from django.db import models
from django.contrib.auth.models import AbstractUser

from utils import db_utils


class User(AbstractUser):
    mobile = models.CharField('手机号', max_length=11, unique=True)
    email_active = models.BooleanField('邮箱状态', default=False)
    default_address = db_utils.ForeignKey('Address', related_name='users', null=True, blank=True,
                                          on_delete=models.SET_NULL, verbose_name='默认地址')

    create_time = models.DateTimeField('创建时间', auto_now_add=True, db_index=True, editable=False)
    update_time = models.DateTimeField('修改时间', auto_now=True, db_index=True, editable=False)

    class Meta:
        db_table = 'md_users'
        verbose_name_plural = verbose_name = '用户表'


class Address(db_utils.BaseModel):
    """用户地址"""
    user = db_utils.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = db_utils.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',
                                   verbose_name='省')
    city = db_utils.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = db_utils.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',
                                   verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'md_address'
        verbose_name_plural = verbose_name = '用户地址'
        ordering = ['-update_time']
