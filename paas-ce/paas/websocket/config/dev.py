# -*- coding: utf-8 -*-
import os
from urllib import parse
from config import RUN_VER, MFA_TIME_OUT

if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = 'DEVELOP'

# APP本地静态资源目录
STATIC_URL = '/static/'

# pycryptodomex             3.9.8
# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
# Celery 消息队列设置 Redis
# BROKER_URL = 'redis://127.0.0.1:6379/8'


# DEBUG = True
DEBUG = False

TERMINAL_PATH = os.getenv("TERMINAL_PATH", "D:/womaiyun/upload/terminal")
GUACD_HOST = '101.251.220.46'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = '/opt/dev-paas/uploads/guacamole/'
GUACD_PATH = '/srv/guacamole'
# 堡垒机超时时间，单位s
TERMINAL_TIMEOUT = 1800
MEDIA_URL = ''
UPLOAD_PATH = '/opt/opsany/'
# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `framework_py` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': APP_CODE,
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}
BK_TOKEN = "PyPvDq71XFeDK24GkcJhwgPsxr8a1Xvs575Ac8oFVyQ"
# BK_TOKEN = "zywDokcgpuKsZ7YUkR3zh4-EGJ21gez65XX1rfc5wdM"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': 86400,  # 1天
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            "PASSWORD": "123456"
        }
        },
    "cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': 1800,  # 30分钟
        "OPTIONS": {
            "CLIENT_CALSS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            "PASSWORD": "123456"
        }
    },
    "mfa": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': MFA_TIME_OUT,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            "PASSWORD": "123456"
        }
    },
    "pod_login": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': 86400,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            "PASSWORD": "123456"
        }
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ["redis://:123456@127.0.0.1:6379/11"],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    }
}


# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
