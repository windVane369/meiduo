# -*- coding: utf-8 -*-
# celery启动文件

import os

from celery import Celery

# 让celery在启动时提前加载django配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo.settings.dev')

# 创建celery客户端对象
celery_app = Celery('meiduo')

# 加载celery配置，指定celery生产的任务存放到哪里
celery_app.config_from_object('celery_tasks.config')

# 注册celery可以生产什么任务
celery_app.autodiscover_tasks([
    'celery_tasks.sms',
])
