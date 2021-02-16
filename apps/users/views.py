import json

from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django.contrib.auth import login, logout, authenticate
import regex as re
from django_redis import get_redis_connection
from django.conf import settings

from apps.users.models import Address
from apps.users.utils import generate_email_verify_url, check_email_verify_url
from celery_tasks.email.tasks import send_verify_email
from utils.response_code import RETCODE
from . import models as user_models
from utils import patterns
from utils.views import LoginRequiredView


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

        with transaction.atomic():
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
#     """用户中心 自定义重定向"""
#
#     def get(self, request):
#         user = request.user
#         if user.is_authenticated:
#             return render(request, 'user_center_info.html')
#         return redirect('/login/?next=/info/')


class InfoView(LoginRequiredView):
    """用户中心"""
    login_url = '/login/'

    def get(self, request):
        return render(request, 'user_center_info.html')


class EmailView(LoginRequiredView):
    """设置用户邮箱，并发送激活邮箱url"""

    def put(self, request):
        # 接收请求体非表单数据
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 校验
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('邮箱格式不正确')

        # 修改user模型的email字段
        user = request.user
        # 如果用户还没有设置邮箱再去设置，如果设置过了就不要用设置了
        if user.email != email:
            with transaction.atomic():
                user.email = email
                user.save()

        # 给当前设置的邮箱发一封激活url
        # # 在此进行对邮箱发送激活邮件
        # from django.core.mail import send_mail
        # # send_mail(subject='邮件主题', message='邮件普通内容', from_email='发件人', recipient_list=['收件人'],
        # #       html_message='邮件超文本内容')
        # send_mail(subject='美多商城', message='', from_email='美多商城<itcast99@163.com>', recipient_list=[email],
        #           html_message="<a href='http://www.baidu.com'>百度<a>")
        verify_url = generate_email_verify_url(user)
        send_verify_email.delay(email, verify_url)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class EmailVerifyView(View):
    """激活邮箱"""

    def get(self, request):
        token = request.GET.get('token')
        user = check_email_verify_url(token)
        if user is None:
            return http.HttpResponseForbidden('token无效')

        with transaction.atomic():
            user.email_active = True
            user.save()

        return redirect(reverse('users:info'))


class AddressesView(LoginRequiredView):
    """收货地址"""

    def get(self, request):
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province.id,
                "city": address.city.name,
                "city_id": address.city.id,
                "district": address.district.name,
                "district_id": address.district.id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': address_list
        }
        return render(request, 'user_center_site.html', context)


class AddressCreateView(LoginRequiredView):
    """新增收货地址"""

    def post(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        with transaction.atomic():
            address = Address.objects.create(
                user=request.user,
                title=f'{receiver}\t{mobile}',
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": province_id,
            "city": address.city.name,
            "city_id": city_id,
            "district": address.district.name,
            "district_id": district_id,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class UpdateDestroyAddressView(LoginRequiredView):
    """修改和删除用户收货地址"""

    def put(self, request, address_id):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            # 重新从数据库查询修改后的收货地址
            address = Address.objects.get(id=address_id)
            address.receiver = receiver
            address.province_id = province_id
            address.city_id = city_id
            address.district_id = district_id
            address.place = place
            address.mobile = mobile
            address.tel = tel
            address.email = email
            address.save()
        except Exception:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": province_id,
            "city": address.city.name,
            "city_id": city_id,
            "district": address.district.name,
            "district_id": district_id,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})
