# -*- coding: utf-8 -*-
from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import  * # noqa

# 预发布环境
RUN_MODE = 'STAGING'

# 正式环境的日志级别可以在这里配置
# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')

BROKER_URL = 'amqp://opsany:123456.coM@127.0.0.1:5672//'

# BROKER_URL = 'redis://127.0.0.1:6379/2'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# 预发布环境数据库可以在这里配置

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'control',  # 数据库名
            'USER': 'control',  # 数据库用户
            'PASSWORD': 'control',  # 数据库密码
            'HOST': '127.0.0.1',  # 数据库主机
            'PORT': '3306',  # 数据库端口
        },
    }
)

CACHES.update(
    {
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
)

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

CHANNEL_LAYERS = {
    'default': {
        #'BACKEND': 'asgi_redis.RedisChannelLayer',
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://:123456.coM@localhost:6379/7'],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
        #'ROUTING': 'shell.routing.channel_routing',
    }
}

ASGI_APPLICATION = 'terminal.routing.application'

CORS_ALLOW_CREDENTIALS = True
BK_PAAS_URL = 'dev.womaiyun.com'
GUACD_HOST = '127.0.0.1'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = '/opt/dev-paas/uploads/guacamole'
# 对应guacd的路径如下
GUACD_PATH = '/srv/guacamole'
# 堡垒机超时时间，单位:秒
TERMINAL_TIMEOUT = 1800
TERMINAL_PATH = '/opt/dev-paas/uploads/terminal'
MEDIA_URL = ''