# -*- coding: utf-8 -*-
from urllib import parse
from config import RUN_VER

if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

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


# 正式环境数据库可以在这里配置

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': APP_CODE,  # 数据库名
            'USER': APP_CODE,  # 数据库用户
            'PASSWORD': "MYSQL_OPSANY_REPO_PASSWORD",  # 数据库密码
            'HOST': "MYSQL_SERVER_IP",  # 数据库主机
            'PORT': int("MYSQL_SERVER_PORT"),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }

        },
    }
)

import mongoengine

MONGO_CONN = mongoengine.connect(
    db=DEVOPS_NAME,  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host="MONGO_SERVER_IP",
    port=int("MONGO_SERVER_PORT"),
    username='devops',
    password="MONGO_DEVOPS_PASSWORD",
    connect=False,
    # authentication_source="admin",           # 进行身份认证的数据库，通常这个数据库为admin
)

# Redis Config
REDIS_HOST = "REDIS_SERVER_IP"
REDIS_PORT = "REDIS_SERVER_PORT"
REDIS_USERNAME = parse.quote("REDIS_SERVER_USER")
REDIS_PASSWORD = parse.quote("REDIS_SERVER_PASSWORD")

# Redis Celery AMQP
BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/17'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)


HARBOR_URL = "REPO_HARBOR_URL"
HARBOR_USERNAME = "REPO_HARBOR_USERNAME"
HARBOR_PASSWORD = "REPO_HARBOR_PASSWORD"


CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

CORS_ALLOW_CREDENTIALS = True

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-repo',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'https://APM_SERVER_HOST:8200',
  'VERIFY_SERVER_CERT': 'false',
  'ENVIRONMENT': 'prod',
}

# Elastic frontend APM
FRONTEND_ELASTIC_APM = {
    'FRONTEND_SERVICE_NAME': 'opsany-saas-repo-frontend',
    'FRONTEND_SERVER_URL': 'https://APM_SERVER_HOST:8200',
    "FRONTEND_ENABLED": 'false',
    'FRONTEND_ENVIRONMENT': 'prod',
}
