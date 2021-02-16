from django.db import models
from utils import db_utils


class Area(db_utils.BaseModel):
    name = models.CharField('名称', max_length=20)
    parent = db_utils.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'md_areas'
        verbose_name = verbose_name_plural = '省市区'
