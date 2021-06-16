# -*- coding: utf-8 -*-
from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 正式环境
RUN_MODE = 'PRODUCT'

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = 'ERROR'

# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# 正式环境数据库可以在这里配置

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'control',  # 数据库名
            'USER': 'control',  # 数据库用户
            'PASSWORD': 'dev_saas_password',  # 数据库密码
            'HOST': '127.0.0.1',  # 数据库主机
            'PORT': '3306',  # 数据库端口
        },
    }
)

CACHES.update(
    {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis_server_ip:6379/1",
            'TIMEOUT': 86400,           # 1天
            "OPTIONS": {
                "CLIENT_CALSS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                "PASSWORD": "redis_password",
            }
        }
    }
)

CHANNEL_LAYERS = {
    'default': {
        #'BACKEND': 'asgi_redis.RedisChannelLayer',
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://:redis_password@redis_server_ip:6379/7'],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
        #'ROUTING': 'shell.routing.channel_routing',
    }
}

ASGI_APPLICATION = 'terminal.routing.application'

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

# BROKER_URL = 'amqp://opsany:123456.coM@127.0.0.1:5672//'

# BROKER_URL = 'redis://localhost:6379/2'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

CORS_ALLOW_CREDENTIALS = True

GUACD_HOST = '127.0.0.1'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = '/opt/opsany/uploads/guacamole/'
# 对应guacd的路径如下
GUACD_PATH = '/srv/guacamole'
# 堡垒机超时时间，单位:秒
TERMINAL_TIMEOUT = 1800
TERMINAL_PATH = '/opt/opsany/uploads/terminal'
MEDIA_URL = ''