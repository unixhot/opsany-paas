# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
Django settings for esb project.

Generated by 'django-admin startproject' using Django 1.8.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import *  # noqa

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@3dqbfh23ihs)*ffdck21g(f)+)95qnj4i3n2m-yhafl#&@#hx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
# Django apps and Middlewares
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'esb',
    'esb.bkcore',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'esb.middlewares.APICommonMiddleware',
    'esb.middlewares.DebugHelperMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'esb.jinja2.environment',
        }
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
# LANGUAGE_CODE = 'zh-hans'
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

# timezone
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True


# language
# 避免循环引用
def _(s):
    return s


LANGUAGES = (
    ('en', _(u'English')),
    ('zh-hans', _(u'简体中文')),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'locale/locale_api'),
)

# Authentication
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )


# logging
LOG_DIR = os.environ.get('PAAS_LOGGING_DIR') or os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# 100M, total 1G
LOG_MAX_BYTES = 104857600
LOG_BACKUP_COUNT = 10
LOG_CLASS = 'logging.handlers.RotatingFileHandler'


def get_loggings(log_level):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d \n \t %(message)s \n',    # noqa
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(message)s'
            },
            'api_simple': {
                # 不要添加换行符，Elasticsearch日志采集器认为每行均是一个合法JSON字符串
                'format': '%(message)s'
            },
            'console_simple': {
                'format': '[%(levelname)s] %(message)s'
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.NullHandler',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'console_simple',
            },
            'root': {
                'class': LOG_CLASS,
                'formatter': 'verbose',
                'filename': os.path.join(LOG_DIR, 'esb.log'),
                'maxBytes': LOG_MAX_BYTES,
                'backupCount': LOG_BACKUP_COUNT
            },
            'api': {
                'class': LOG_CLASS,
                'formatter': 'api_simple',
                'filename': os.path.join(LOG_DIR, 'esb_api.log'),
                'maxBytes': LOG_MAX_BYTES,
                'backupCount': LOG_BACKUP_COUNT
            },
        },
        'loggers': {
            'django': {
                'handlers': ['null'],
                'level': 'INFO',
                'propagate': True,
            },
            'thrift': {
                'handlers': ['root'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['root'],
                'level': 'ERROR',
                'propagate': True,
            },
            # the root logger, for all the project
            'root': {
                'handlers': ['root', 'console'],
                'level': log_level,
                'propagate': False,
            },
            # Logging config for ESB projects
            'api': {
                'handlers': ['api'],
                'level': log_level,
                'propagate': False,
            },
            'esb.management': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }


# Static files
SITE_URL = '/'

STATIC_URL = SITE_URL + 'static/'

STATIC_VERSION = '0.0.1'

HTTP_SCHEMA = 'https'

# component esb_conf
ESB_SITE_ESB_CONF = 'components.esb_conf.config'

# JOB是否启用SSL验证
JOB_SSL = True
# 如果用户未配置config/default.py中的SSL_ROOT_DIR，则使用此目录
DEFAULT_SSL_ROOT_DIR = '/data/paas/ssl_dir'

from configs.default import *  # noqa


LOGGING = get_loggings(LOG_LEVEL)  # noqa
REDIS_CONF_FOR_RATELIMIT = {}
HTTP_SCHEMA = 'https'

# 默认超时时间
REQUEST_TIMEOUT_SECS = 30

RATE_LIMIT_KEY_NAMESPACE = 'bk_esb_rate_limit'


DJ_POOL_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 100,
    'recycle': 600
}
