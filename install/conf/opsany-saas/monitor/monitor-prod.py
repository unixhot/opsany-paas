# -*- coding: utf-8 -*-
from config import RUN_VER, default
from urllib import parse
import mongoengine

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
            'NAME': APP_CODE,  # 数据库名
            'USER': APP_CODE,  # 数据库用户
            'PASSWORD': os.getenv("MYSQL_PASSWORD", "MYSQL_OPSANY_MONITOR_PASSWORD"),  # 数据库密码
            'HOST': os.getenv("MYSQL_HOST", "MYSQL_SERVER_IP"),  # 数据库主机
            'PORT': int(os.getenv("MYSQL_PORT", "MYSQL_SERVER_PORT")),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }

        },
    }
)

ELASTIC_SEARCH = {
    "USER": os.getenv("ELASTIC_SEARCH_USERNAME", "elastic"),
    "PASSWORD": os.getenv("ES_PASSWORD", "OpsAny@2020"),
    "HOST": os.getenv("ES_SERVER_IP", "81.69.6.201"),
    "PORT": os.getenv("ELASTIC_PORT", "9200"),
}

HEART_BEAT_INDEX = os.getenv("ELASTIC_SEARCH_INDEX", "heartbeat-7.13.*")
HEART_BEAT_MONITOR_D = "{}/uploads/{}/heartbeat-monitors.d/".format(default.UPLOAD_PATH, APP_CODE)
if not os.path.exists(HEART_BEAT_MONITOR_D):
    os.makedirs(HEART_BEAT_MONITOR_D)

# 静态文件
setattr(default, "HEART_BEAT_MONITOR_D", HEART_BEAT_MONITOR_D)

# MongoDB Config
MONGO_CONN = mongoengine.connect(
    db=APP_CODE,  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host=os.getenv("MONGO_HOST", "MONGO_SERVER_IP"),
    port=int(os.getenv("MONGO_PORT", "MONGO_SERVER_PORT")),
    username=APP_CODE,
    password=os.getenv("MONGO_PASSWORD", "MONGO_MONITOR_PASSWORD"),
    connect=False
    # authentication_source="admin",           # 进行身份认证的数据库，通常这个数据库为admin
)

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "REDIS_SERVER_IP")
REDIS_PORT = os.getenv("REDIS_PORT", "REDIS_SERVER_PORT")
REDIS_USERNAME = parse.quote(os.getenv("REDIS_USERNAME", "REDIS_SERVER_USER") or "")  
REDIS_PASSWORD = parse.quote(os.getenv("REDIS_PASSWORD", "REDIS_SERVER_PASSWORD")) 

# Redis Celery AMQP
BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/6'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-monitor',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'http://APM_SERVER_HOST:8200',
  'ENVIRONMENT': 'prod',
}


