# -*- coding: utf-8 -*-
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginRequiredView(LoginRequiredMixin, View):
    """验证用户登录的基类"""
    pass
