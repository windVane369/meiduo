from django import http
from django.views import View
from django_redis import get_redis_connection

from random import randint

from apps.verifications.ccp import CCP
from apps.verifications import constants
from libs.captcha.captcha import captcha
from utils.response_code import RETCODE


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        # SDK生成图形验证码
        # name: 唯一标识
        # text: 图形验证码字符串
        # image_code: 图形验证码的图片bytes类型数据
        name, text, image_bytes = captcha.generate_captcha()

        # 创建redis链接，数据存储到verify_code数据库
        redis_connection = get_redis_connection('verify_code')
        # 将图形验证码字符串存储到redis数据库，并设置超时时间
        redis_connection.setex(uuid, constants.IMAGE_CODE_EXPIRE, text)

        return http.HttpResponse(image_bytes, content_type='image/png')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):

        # 接收查询参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验
        if not all([image_code_client, uuid]):
            return http.HttpResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 创建redis链接
        redis_connection = get_redis_connection('verify_code')
        # 提取图片验证码
        image_code_server_bytes = redis_connection.get(uuid)

        # 删除已经取出的图形验证码，让它只能被使用一次
        redis_connection.delete(uuid)

        # 判断redis中图形验证码过期
        if image_code_server_bytes is None:
            return http.HttpResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期'})

        # 将bytes转化为字符串类型
        image_code_server = image_code_server_bytes.decode()
        # 转小写后判断是否相同
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 利用容联云平台发短信
        # 随机生成一个6位数作为短信验证码
        sms_code = '%06d' % randint(0, 999999)
        # 存储到redis
        redis_connection.setex(f'sms_{mobile}', 300, sms_code)
        CCP.send_message(sms_code)

        # 响应
        return http.HttpResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
