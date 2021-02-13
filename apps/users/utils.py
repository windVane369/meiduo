# -*- coding: utf-8 -*-
import regex as re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User
from utils import patterns


def get_user_by_account(account):
    """根据account查询用户"""
    try:
        if re.match(f'^{patterns.PATTERN_MOBILE_STR}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义认证后端类实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user and user.check_password(password) and user.is_active:
            return user
