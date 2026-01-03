# -*- coding: utf-8 -*-
from urllib import parse
from config import RUN_VER, MFA_TIME_OUT

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

#GUACD_HOST = '127.0.0.1'
#GUACD_PORT = '4822'
FOOT_CLIENT_IP = "BASTION_FOOT_CLIENT_IP"
FOOT_CLIENT_PORT = "BASTION_FOOT_CLIENT_PORT"

# 对应guacd的路径如下
GUACD_PATH = "/srv/guacamole"

MEDIA_URL = ''
UPLOAD_PATH = "/opt/opsany/"
TERMINAL_PATH = "/opt/opsany/uploads/terminal"
ORI_GUACD_PATH = os.path.join("/opt/opsany/uploads/guacamole")
TERMINAL_TIMEOUT = 1800

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'bastion',  # 数据库名
            'USER': 'bastion',  # 数据库用户
            'PASSWORD': "MYSQL_OPSANY_BASTION_PASSWORD",  # 数据库密码
            'HOST': "MYSQL_SERVER_IP",  # 数据库主机
            'PORT': int("MYSQL_SERVER_PORT"),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }

        },
    }
)

# Redis Config
REDIS_HOST = "REDIS_SERVER_IP"
REDIS_PORT = "REDIS_SERVER_PORT"
REDIS_USERNAME = parse.quote("REDIS_SERVER_USER")
REDIS_PASSWORD = parse.quote("REDIS_SERVER_PASSWORD")

# Redis Celery AMQP
# BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/8'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Redis Cache
CACHES.update(
    {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/8".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            'TIMEOUT': 86400,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            }
        },
        "cache": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/8".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            'TIMEOUT': 1800,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                # "PASSWORD": REDIS_PASSWORD,
            }
        },
        "mfa": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/8".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            'TIMEOUT': 1800,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                # "PASSWORD": REDIS_PASSWORD,
            }
        },
        "pod_login": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/14".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            'TIMEOUT': 1800,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                # "PASSWORD": REDIS_PASSWORD,
            }
        }
    }
)

WEBSOCKET_CHANNEL_LAYERS = ["redis://{}:{}@{}:{}/8".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)]

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-bastion',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'https://APM_SERVER_HOST:8200',
  'VERIFY_SERVER_CERT': 'false',
  'ENVIRONMENT': 'prod',
}

# Elastic frontend APM
FRONTEND_ELASTIC_APM = {
    'FRONTEND_SERVICE_NAME': 'opsany-saas-bastion-frontend',
    'FRONTEND_SERVER_URL': 'https://APM_SERVER_HOST:8200',
    "FRONTEND_ENABLED": 'false',
    'FRONTEND_ENVIRONMENT': 'prod',
}
