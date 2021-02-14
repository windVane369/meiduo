# -*- coding: utf-8 -*-
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
