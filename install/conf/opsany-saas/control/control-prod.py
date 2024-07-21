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
            'PASSWORD': os.getenv("MYSQL_PASSWORD", "MYSQL_OPSANY_CONTROL_PASSWORD"),  # 数据库密码
            'HOST': os.getenv("MYSQL_HOST", "MYSQL_SERVER_IP"),  # 数据库主机
            'PORT': int(os.getenv("MYSQL_PORT", "MYSQL_SERVER_PORT")),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB;\
                                 SET sql_mode='STRICT_TRANS_TABLES';",
            }

        },
    }
)

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "REDIS_SERVER_IP")
REDIS_PORT = os.getenv("REDIS_PORT", "REDIS_SERVER_PORT")
REDIS_USERNAME = parse.quote(os.getenv("REDIS_USERNAME", "REDIS_SERVER_USER") or "")  
REDIS_PASSWORD = parse.quote(os.getenv("REDIS_PASSWORD", "REDIS_SERVER_PASSWORD")) 

# Redis Celery AMQP
BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/4'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Reis Cache
CACHES.update(
    {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
             "LOCATION": "redis://{}:{}@{}:{}/1".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            # 'TIMEOUT': 86400,  # 1天
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                "PASSWORD": REDIS_PASSWORD,
            }
        },
        "salt": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/9".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            # 'TIMEOUT': 3600,  # 1天
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
                "PASSWORD": REDIS_PASSWORD,
            }
        }
    }
)

CHANNEL_LAYERS = {
    'default': {
        # 'BACKEND': 'asgi_redis.RedisChannelLayer',
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ["redis://{}:{}@{}:{}/9".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
        # 'ROUTING': 'shell.routing.channel_routing',
    }
}

ASGI_APPLICATION = 'terminal.routing.application'

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

# BROKER_URL = 'amqp://opsany:123456.coM@127.0.0.1:5672//'
# BROKER_URL = 'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2'.format(REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# BROKER_URL = 'redis://localhost:6379/2'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

CORS_ALLOW_CREDENTIALS = True

GUACD_HOST = '127.0.0.1'
GUACD_PORT = '4822'
# paas服务器本地路径，
ORI_GUACD_PATH = "/opt/opsany/uploads/guacamole/"
# 对应guacd的路径如下
GUACD_PATH = "/srv/guacamole"
# 堡垒机超时时间，单位:秒
TERMINAL_TIMEOUT = 1800
TERMINAL_PATH = "/opt/opsany/uploads/terminal"
MEDIA_URL = ''
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/opt/opsany/")
METRIC_PACKAGE_PATH = os.getenv("METRIC_PACKAGE_PATH", "uploads/agent/prom-exporter/")
METRIC_LOGO_PATH = "uploads/control/metric/logo/"
MINION_CACHE_FILE = "uploads/control/minion_cache_file/"
COLLECT_SCRIPT_PATH = "uploads/control/collect/script/"

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-control',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'https://APM_SERVER_HOST:8200',
  'VERIFY_SERVER_CERT': 'false',
  'ENVIRONMENT': 'prod',
}

# Elastic frontend APM
FRONTEND_ELASTIC_APM = {
    'FRONTEND_SERVICE_NAME': 'opsany-saas-control-frontend',
    'FRONTEND_SERVER_URL': 'https://APM_SERVER_HOST:8200',
    "FRONTEND_ENABLED": 'false',
    'FRONTEND_ENVIRONMENT': 'prod',
}
