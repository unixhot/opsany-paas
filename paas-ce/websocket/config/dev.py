'''
Author: your name
Date: 2020-12-03 00:58:55
LastEditTime: 2020-12-03 00:59:37
LastEditors: your name
Description: In User Settings Edit
FilePath: /control-backend/config/dev.py
'''
# -*- coding: utf-8 -*-
from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = 'DEVELOP'

# APP本地静态资源目录
STATIC_URL = '/static/'

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
BROKER_URL = 'amqp://azpaas:123456.coM@192.168.111.71:5672//'


# Celery 消息队列设置 Redis
# BROKER_URL = 'redis://localhost:6379/2'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

DEBUG = True

# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `framework_py` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'control',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
}

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
GUACD_HOST = '127.0.0.1'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = '/opt/dev-paas/uploads/guacamole/'
GUACD_PATH = '/srv/guacamole'
# 堡垒机超时时间，单位s
TERMINAL_TIMEOUT = 1800
TERMINAL_PATH = '/opt/dev-paas/uploads/terminal'
MEDIA_URL = ''


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': 86400,           # 1天
        "OPTIONS": {
            "CLIENT_CALSS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            "PASSWORD": "123456.coM",
        }
    }
}
