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

UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/opt/opsany/")
MODEL_FILE_URL = "uploads/{}/model_file".format(APP_CODE)
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
            'PASSWORD': os.getenv("MYSQL_PASSWORD", "MYSQL_OPSANY_DEVOPS_PASSWORD"),  # 数据库密码
            'HOST': os.getenv("MYSQL_HOST", "MYSQL_SERVER_IP"),  # 数据库主机
            'PORT': int(os.getenv("MYSQL_PORT", "MYSQL_SERVER_PORT")),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }

        },
    }
)

import mongoengine

MONGO_CONN = mongoengine.connect(
    db=APP_CODE,  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host=os.getenv("MONGO_HOST", "MONGO_SERVER_IP"),
    port=int(os.getenv("MONGO_PORT", "MONGO_SERVER_PORT")),
    username=APP_CODE,
    password=os.getenv("MONGO_PASSWORD", "MONGO_DEVOPS_PASSWORD"),
    connect=False,
    # authentication_source="admin",           # 进行身份认证的数据库，通常这个数据库为admin
)

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

CORS_ALLOW_CREDENTIALS = True

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "REDIS_SERVER_IP")
REDIS_PORT = os.getenv("REDIS_PORT", "REDIS_SERVER_PORT")
REDIS_USERNAME = parse.quote(os.getenv("REDIS_USERNAME", "REDIS_SERVER_USER") or "")  
REDIS_PASSWORD = parse.quote(os.getenv("REDIS_PASSWORD", "REDIS_SERVER_PASSWORD")) 

# Redis Celery AMQP
# BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/9'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-devops',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'http://APM_SERVER_HOST:8200',
  'ENVIRONMENT': 'prod',
}
