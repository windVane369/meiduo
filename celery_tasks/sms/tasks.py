# -*- coding: utf-8 -*-
from celery_tasks.main import celery_app
from celery_tasks.sms.ccp import CCP


@celery_app.task(name='send_sms_code')
def send_sms_code(sms_code):
    CCP.send_message(sms_code)
