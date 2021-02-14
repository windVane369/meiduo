from django.db import models
from utils import db_utils


class OAuthQQUser(db_utils.BaseModel):

    user = db_utils.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField('openid', max_length=64, db_index=True)

    class Meta:
        db_table = 'md_oauth_qq'
        verbose_name_plural = verbose_name = 'QQ第三方登录'
