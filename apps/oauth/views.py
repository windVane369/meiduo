from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import render, redirect
from django import http
from django.views import View
from django.conf import settings
from django_redis import get_redis_connection
import regex as re

from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from apps.oauth.utils import OAuthQQ, generate_openid_signature, check_openid_signature
from meiduo.settings import common
from utils.response_code import RETCODE


class QQAuthURLView(View):
    """提供QQ登录url"""

    def get(self, request):
        next_url = request.GET.get('next') or '/'

        auth_qq = OAuthQQ(
            client_id=common.QQ_CLIENT_ID,
            client_secret=common.QQ_CLIENT_SECRET,
            redirect_uri=common.QQ_REDIRECT_URI,
            state=next_url
        )

        # auth_qq.get_qq_url() 获取拼接好的qq登录url
        return http.JsonResponse({
            'login_url': auth_qq.get_qq_url(),
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


class QQAuthUserView(View):
    """QQ登录成功后的回调处理"""

    # http://www.meiduo.site:8000/oauth_callback?code=C906BB022A8E9A0281641A1DE15C710B&state=%2F
    def get(self, request):

        # 获取查询参数中的code
        code = request.GET.get('code')

        # 校验
        if code is None:
            return http.HttpResponseForbidden('缺少code')

        # 创建QQ登录工具对象
        auth_qq = OAuthQQ(
            client_id=common.QQ_CLIENT_ID,
            client_secret=common.QQ_CLIENT_SECRET,
            redirect_uri=common.QQ_REDIRECT_URI
        )
        try:
            # 调用get_access_token
            access_token = auth_qq.get_access_token(code)
            # 调用get_openid
            openid = auth_qq.get_open_id(access_token)
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.SERVERERR, 'errmsg': 'OAuth2.0认证失败'})

        try:
            # 去数据库中查询openid存不存在
            auth_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            context = {'openid': generate_openid_signature(openid)}
            # 如果不存在,说明openid还没有绑定美多中的用户,应该去绑定
            return render(request, 'oauth_callback.html', context)

        else:
            # 如果存在, 说明openid之前已经绑定过美多用户,那么直接代表登录成功
            user = auth_model.user
            # 状态保持
            login(request, user)
            # 响应cookie存储username
            response = redirect(request.GET.get('state') or '/')
            response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

            # 重定向到指定的来源
            return response

    def post(self, request):
        """openid绑定用户逻辑"""
        # 接收表单数据
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid_sign = request.POST.get('openid')

        # 校验
        if all([mobile, password, sms_code, openid_sign]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # 短信验证码校验
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 将redis中的短信验证码获取来,
        sms_code_server_bytes = redis_conn.get('sms_%s' % mobile)
        # 短信验证码从redis获取出来之后就从redis数据库删除: 让它是一次性
        redis_conn.delete('sms_%s' % mobile)
        # 判断redis中是否获取到短信验证码(判断是否过期)
        if sms_code_server_bytes is None:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码已过期'})
        #  从redis获取出来的数据注意类型问题
        sms_code_server = sms_code_server_bytes.decode()
        # 判断短信验证码是否填写正确
        if sms_code != sms_code_server:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码输入错误'})

        # 对openid进行解密
        openid = check_openid_signature(openid_sign)
        if openid is None:
            return http.HttpResponseForbidden('openid无效')

        try:
            # 以mobile字段进行查询user表
            # 如果查询到了,说明此手机号在美多商城之前已经注册, 老用户
            user = User.objects.get(mobile=mobile)
            # 如果是已存在的老用户,就去校验用户密码是否正确
            if user.check_password(password) is False:
                return http.HttpResponseForbidden('绑定的用户信息填写不正确')
        except User.DoesNotExist:
            with transaction.atomic():
                # 如果没有查询到,说明此手机号是新的, 创建一个新的user
                user = User.objects.create_user(username=mobile, password=password, mobile=mobile)

        with transaction.atomic():
            # 新增oauth_qq表的一个记录
            OAuthQQUser.objects.create(user=user, openid=openid)

        # 绑定完成即代表登录成,
        login(request, user)
        response = redirect(request.GET.get('state') or '/')
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        return response
