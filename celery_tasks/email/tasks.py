# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.conf import settings

from celery_tasks.main import celery_app


@celery_app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):
    """
    发送激活邮箱
    :param to_email: 收件人邮箱
    :param verify_url: 激活url
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   f'<p>您的邮箱为：{to_email} 。请点击此链接激活您的邮箱：</p>' \
                   f'<p><a href="{verify_url}">{verify_url}</a></p>'
    send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
