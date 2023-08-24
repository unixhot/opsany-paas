# -*- coding: utf-8 -*-
from urllib import parse
from config import RUN_VER, UPLOAD_PATH
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


LOGIN_LOGO_CACHE_DIR = os.path.join(UPLOAD_PATH, "uploads/rbac/cache_icon/")

if not os.path.exists(LOGIN_LOGO_CACHE_DIR):
    os.makedirs(LOGIN_LOGO_CACHE_DIR)

DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': APP_CODE,  # 数据库名
            'USER': APP_CODE,  # 数据库用户
            'PASSWORD': os.getenv("MYSQL_PASSWORD", "MYSQL_OPSANY_RBAC_PASSWORD"),  # 数据库密码
            'HOST': os.getenv("MYSQL_HOST", "MYSQL_SERVER_IP"),  # 数据库主机
            'PORT': int(os.getenv("MYSQL_PORT", "MYSQL_SERVER_PORT")),  # 数据库端口
            # 'ATOMIC_REQUESTS': True,
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
BROKER_URL = 'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'.format(REDIS_USERNAME=REDIS_USERNAME, REDIS_PASSWORD=REDIS_PASSWORD, REDIS_HOST=REDIS_HOST, REDIS_PORT=REDIS_PORT)

# Redis Cache
CACHES.update(
    {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}@{}:{}/9".format(REDIS_USERNAME, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
            'TIMEOUT': 1800,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 1000},
            }
        }
    }
)

# Elastic APM
ELASTIC_APM = {
  'ENABLED': 'false',
  'SERVICE_NAME': 'opsany-saas-rbac',
  'SECRET_TOKEN': 'APM_SECRET_TOKEN',
  'SERVER_URL': 'http://APM_SERVER_HOST:8200',
  'ENVIRONMENT': 'prod',
}


