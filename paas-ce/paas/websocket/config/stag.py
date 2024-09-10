# -*- coding: utf-8 -*-
from config import RUN_VER, MFA_TIME_OUT

if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import  * # noqa

# 预发布环境
RUN_MODE = 'STAGING'

DEBUG = True

# Terminal log path
TERMINAL_PATH = os.getenv("TERMINAL_PATH", "/opt/opsany/uploads/terminal")
# 正式环境的日志级别可以在这里配置
# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')

# 预发布环境数据库可以在这里配置

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'bastion',  # 数据库名
            'USER': 'bastion',  # 数据库用户
            'PASSWORD': 'bastion',  # 数据库密码
            'HOST': 'localhost',  # 数据库主机
            'PORT': '3306',  # 数据库端口
            'ATOMIC_REQUESTS': True,
        },
    }
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:123456.coM@127.0.0.1:6379/1",
        'TIMEOUT': 86400,  # 1天
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            # "PASSWORD": "123456.coM"
        }
    },
    "cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:123456.coM@127.0.0.1:6379/9",
        'TIMEOUT': 1800,  # 30分钟
        "OPTIONS": {
            "CLIENT_CALSS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            # "PASSWORD": "123456.coM",
        }
    },
    "mfa": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:123456.coM@127.0.0.1:6379/8",
        'TIMEOUT': 1800,  # 30分钟
        "OPTIONS": {
            "CLIENT_CALSS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            # "PASSWORD": "123456.coM",
        }
    },
    "pod_login": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:123456.coM@127.0.0.1:6379/14",
        'TIMEOUT': 1800,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            # "PASSWORD": "123456.coM",
        }
    }
}

CHANNEL_LAYERS = {
    'default': {
        # 'BACKEND': 'asgi_redis.RedisChannelLayer',
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://:123456.coM@localhost:6379/8'],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
        # 'ROUTING': 'shell.routing.channel_routing',
    }
}


GUACD_HOST = '127.0.0.1'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = '/opt/opsany/uploads/guacamole'
# 对应guacd的路径如下
GUACD_PATH = '/srv/guacamole'
# # 堡垒机超时时间，单位:秒
TERMINAL_TIMEOUT = 1800
MEDIA_URL = ''
UPLOAD_PATH = '/opt/opsany/'

ELASTIC_APM = {
  'SERVICE_NAME': 'saas-bastion',
  'SECRET_TOKEN': '',
  'SERVER_URL': 'http://192.168.18.194:8200',
  'ENVIRONMENT': 'dev',
}

