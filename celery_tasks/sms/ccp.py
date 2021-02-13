# -*- coding: utf-8 -*-

from ronglian_sms_sdk import SmsSDK
from celery_tasks.sms import constants


class CCP(object):
    accId = constants.RLY_ACC_ID
    accToken = constants.RLY_ACC_TOKEN
    appId = constants.RLY_APP_ID

    @classmethod
    def send_message(cls, sms_code):
        # 设置发送的数据，参数1是验证码，参数2是失效时间
        data = (sms_code, constants.RLY_SMS_CODE_REDIS_EXPIRES)
        sdk = SmsSDK(cls.accId, cls.accToken, cls.appId)
        sdk.sendMessage(constants.RLY_SEND_SMS_TEMPLATE_ID, constants.RLY_MOBILE, data)
