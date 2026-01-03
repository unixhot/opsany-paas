# -*- coding: utf-8 -*-
from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa
from urllib import parse

# 正式环境
RUN_MODE = 'PRODUCT'

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = 'ERROR'

UPLOAD_PATH = "/opt/opsany/"
# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# MySQL Config
DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': APP_CODE,  # 数据库名
            'USER': APP_CODE,  # 数据库用户
            'PASSWORD': "MYSQL_OPSANY_APM_PASSWORD",  # 数据库密码
            'HOST': "MYSQL_SERVER_IP",  # 数据库主机
            'PORT': int("MYSQL_SERVER_PORT"),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }
        },
    }
)
KIBANA_ES_USERNAME = "KIBANA_USERNAME"
KIBANA_ES_PASSWORD = "KIBANA_PASSWORD"
KIBANA_ES_CLUSTER = "KIBANA_CLUSTER"

ES_USERNAME = "ELASTIC_USERNAME"
ES_PASSWORD = "ELASTIC_PASSWORD"
ES_CLUSTER = "ELASTIC_CLUSTER"
HEART_BEAT_INDEX = "ELASTIC_SEARCH_INDEX"
CORS_ALLOW_CREDENTIALS = True


import mongoengine

# MongoDB Config
MONGO_CONN = mongoengine.connect(
    db='prom',  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host="MONGO_SERVER_IP",
    port=int("MONGO_SERVER_PORT"),
    username='prom',
    password="MONGO_PROM_PASSWORD",
    connect=False
    # authentication_source="admin",           # 进行身份认证的数据库，通常这个数据库为admin
)

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-apm',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'https://APM_SERVER_HOST:8200',
  'VERIFY_SERVER_CERT': 'false',
  'ENVIRONMENT': 'prod',
}

# Elastic frontend APM
FRONTEND_ELASTIC_APM = {
    'FRONTEND_SERVICE_NAME': 'opsany-saas-apm-frontend',
    'FRONTEND_SERVER_URL': 'https://APM_SERVER_HOST:8200',
    "FRONTEND_ENABLED": 'false',
    'FRONTEND_ENVIRONMENT': 'prod',
}

# 单位秒
HOME_PAGE_LAST_TIME = 60 * 15

# Redis Config
REDIS_HOST = "REDIS_SERVER_IP"
REDIS_PORT = "REDIS_SERVER_PORT"
REDIS_USERNAME = parse.quote("REDIS_SERVER_USER")
REDIS_PASSWORD = parse.quote("REDIS_SERVER_PASSWORD")

# Redis Celery AMQP
BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/21'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Reids Cache
CACHES.update(
    {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/21".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
             # 'TIMEOUT': 86400,  # 1天
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                # "PASSWORD": REDIS_PASSWORD,
            }
        }
    },
)
