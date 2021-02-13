from django import http
from django.views import View
from django_redis import get_redis_connection

from random import randint

from apps.verifications import constants
from celery_tasks.sms.tasks import send_sms_code
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
        # 创建redis链接
        redis_connection = get_redis_connection('verify_code')

        # 用于判断60s发送一次
        send_flag = redis_connection.get(f'send_flag_{mobile}')
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 接收查询参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验
        if not all([image_code_client, uuid]):
            return http.HttpResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

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

        # 添加redis管道技术
        # 为什么使用管道？避免大量的操作redis，管道会把待执行的命令打包成一条执行，尽可能减少请求次数
        # 一般情况下，redis存储对实效性要求没有获取严格，只需要把数据存起来就可以，所以可以使用管道技术
        # 当存在多个存储指令时使用，单个的时候不要使用
        pipeline = redis_connection.pipeline()

        # 利用容联云平台发短信
        # 随机生成一个6位数作为短信验证码
        sms_code = '%06d' % randint(0, 999999)
        # redis存储命令加入管道
        # 存储到redis
        pipeline.setex(f'sms_{mobile}', 300, sms_code)
        # 记录已经发送过短信
        pipeline.setex(f'send_flag_{mobile}', 60, 1)
        # 执行管道
        pipeline.execute()
        # 调用异步任务
        send_sms_code.delay(sms_code)

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
