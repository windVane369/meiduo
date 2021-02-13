# -*- coding: utf-8 -*-

from ronglian_sms_sdk import SmsSDK
from meiduo.settings import common


class CCP(object):
    accId = common.RLY_ACC_ID
    accToken = common.RLY_ACC_TOKEN
    appId = common.RLY_APP_ID

    @classmethod
    def send_message(cls, sms_code):
        # 设置发送的数据，参数1是验证码，参数2是失效时间
        data = (sms_code, common.RLY_SMS_CODE_REDIS_EXPIRES)
        sdk = SmsSDK(cls.accId, cls.accToken, cls.appId)
        sdk.sendMessage(common.RLY_SEND_SMS_TEMPLATE_ID, common.RLY_MOBILE, data)
