# -*- coding: utf-8 -*-
import regex as re
from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

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


def generate_email_verify_url(user):
    """拿到用户信息进行加密并拼接好激活url"""

    serializer = Serializer(settings.SECRET_KEY, 24 * 60 * 60)

    data = {'user_id': user.id, 'email': user.email}

    token = serializer.dumps(data).decode()

    verify_url = f'{settings.EMAIL_VERIFY_URL}?token={token}'

    return verify_url


def check_email_verify_url(token):
    """
    对token进行解密,然后查询到用户
    :param token: 要解密的用户数据
    :return: user or None
    """
    serializer = Serializer(settings.SECRET_KEY, 3600 * 24)
    try:
        data = serializer.loads(token)
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
            return user
        except User.DoesNotExist:
            return None
    except BadData:
        return None
