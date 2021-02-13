from django.shortcuts import render
from django.views import View
from django import http
from django.contrib.auth import login, logout
import regex as re
from django_redis import get_redis_connection

from utils.response_code import RETCODE
from . import models as user_models
from utils import patterns


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1. 接收请求体表单数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 2. 校验数据
        # 判断必传参数是否传值
        if not all([username, password, password2, mobile, sms_code, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(rf'^{patterns.PATTERN_USERNAME_STR}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户')
        if not re.match(rf'^{patterns.PATTERN_PASSWORD_STR}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次密码输入不一致')
        if not re.match(rf'^{patterns.PATTERN_MOBILE_STR}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        redis_connection = get_redis_connection('verify_code')
        sms_code_server = redis_connection.get(f'sms_{mobile}')
        if sms_code_server is None:
            return http.HttpResponseForbidden('未输入短信验证码')
        if sms_code != sms_code_server.decode():
            return http.HttpResponseForbidden('验证码输入错误')

        # create_user 官网推荐
        user = user_models.User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        # 记录用户登陆状态（状态保持）
        login(request, user)

        return http.HttpResponse('注册成功')


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        # 从数据库查询当前username是否重复
        count = user_models.User.objects.filter(username=username).count()
        # 响应
        return http.JsonResponse({'count': count})


class MobileCountView(View):
    """判断手机号码是否重复注册"""

    def get(self, request, mobile):
        # 从数据库查询当前mobile是否重复
        count = user_models.User.objects.filter(mobile=mobile).count()
        # 响应
        return http.JsonResponse({'count': count})
