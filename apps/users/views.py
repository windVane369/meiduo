from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django.contrib.auth import login, logout, authenticate
import regex as re
from django_redis import get_redis_connection
from django.conf import settings

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
        redis_connection.delete(f'sms_{mobile}')
        if sms_code_server is None:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '未输入短信验证码'})
        if sms_code != sms_code_server.decode():
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '验证码输入错误'})

        # create_user 官网推荐
        user = user_models.User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        # 记录用户登陆状态（状态保持）
        login(request, user)

        response = redirect(reverse('contents:index'))
        # 注册时用户名写入到cookie，使用默认的有效期
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        return


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


class LoginView(View):
    """登录"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 用户登录认证
        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 状态保持
        login(request, user)

        request.session.set_expiry(0 if remembered is None else settings.SESSION_COOKIE_AGE)

        response = redirect(request.GET.get('next') or reverse('contents:index'))
        # 登录时用户名写入cookie，默认值为默认的有效期
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 清除状态保持
        logout(request)

        response = redirect(reverse('users:login'))
        # 清除cookie中的username
        response.delete_cookie('username')

        return response


# class InfoView(View):
#     """用户中心"""
#
#     def get(self, request):
#         user = request.user
#         if user.is_authenticated:
#             return render(request, 'user_center_info.html')
#         return redirect('/login/?next=/info/')


class InfoView(LoginRequiredMixin, View):
    """用户中心"""
    login_url = '/login/'

    def get(self, request):
        return render(request, 'user_center_info.html')
