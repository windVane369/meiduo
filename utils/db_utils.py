# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import Storage
from django.db import models


class BaseModel(models.Model):
    id = models.BigAutoField('主键ID', primary_key=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, db_index=True, editable=False)
    update_time = models.DateTimeField('修改时间', auto_now=True, db_index=True, editable=False)

    class Meta:
        abstract = True


class ForeignKey(models.ForeignKey):

    def __init__(self, to, on_delete=models.DO_NOTHING, **kwargs):
        kwargs.setdefault('db_constraint', False)
        super().__init__(to, on_delete, **kwargs)


class FastDFSStorage(Storage):

    def _open(self, name, mode='rb'):
        """
        当要打开某个文件时就会调用此方法
        :param name: 要打开的文件名
        :param mode: 打开文件的模式
        """
        pass

    def _save(self, name, content):
        """
        当要进行上传图片时就会来自动调用此方法
        :param name: 要上传的文件名
        :param content: 要上传的文件二进制数据
        :return: file_id
        """
        pass

    def url(self, name):
        """
        当获取图片的绝对路径时就会调用此方法
        :param name: 要访问的文件的file_id
        :return: 绝对路径  http://image.meiduo.site:8888/ + name
        """
        return settings.FDFS_BASE_URL + name
