# -*- coding: utf-8 -*-

from conf.default import LOGGING

# Debug
DEBUG = False

# Log settings
LOG_LEVEL = 'ERROR'

LOGGING.update(**{
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'root': {
            'handlers': ['root'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['wb_mysql'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
})

# use the static root 'static' in production envs
if not DEBUG:
    STATIC_ROOT = 'static'

# For Nginx
SITE_URL = "/login/"
STATIC_URL = "/static/"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 默认用mysql
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': 'MYSQL_OPSANY_PASSWORD',
        'HOST': 'MYSQL_SERVER_IP',
        'PORT': 'MYSQL_SERVER_PORT',
    }
}

# Init User
USERNAME = 'admin'
PASSWORD = 'admin'

# Inner domain
PAAS_INNER_DOMAIN = 'LOCAL_IP'
HTTP_SCHEMA = 'https'

# Cookie
BK_COOKIE_DOMAIN = ''
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://DOMAIN_NAME',
    'https://LOCAL_IP',
    'http://DOMAIN_NAME',
    'http://LOCAL_IP',
]

# Secret Key
SECRET_KEY = 'jO149njrTj4kEx6ZbUH8Zc53bfQJctINWaEzTWIsOoxSDNwK2I'

# ESB Token
ESB_TOKEN = '41f076b7-afce-46eb-9e85-dab245eb0931'
RBAC_APP_SECRET = "RBAC_SECRET_KEY"
