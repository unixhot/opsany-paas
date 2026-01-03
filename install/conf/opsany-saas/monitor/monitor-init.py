# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['celery_app', 'RUN_VER', 'APP_CODE', 'SECRET_KEY', 'BK_URL', 'PAAS_ESB_URL', 'PAAS_LOGIN_URL', 'BASE_DIR']

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

# app 基本信息

# SaaS运行版本，如非必要请勿修改
RUN_VER = 'open'
# SaaS应用ID
APP_CODE = 'monitor'
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = "MONITOR_SECRET_KEY"
# SaaS平台URL
BK_URL = "https://DOMAIN_NAME"
PAAS_ESB_URL = "http://LOCAL_IP:8002"
PAAS_LOGIN_URL = "http://LOCAL_IP:8003"

if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {
        'development': 'dev',
        'testing': 'stag',
        'production': 'prod',
    }.get(PAAS_V2_ENVIRONMENT)

# 默认头像
DEFAULT_USER_ICON = "uploads/workbench/user_icon/edfb99ee-08d6-41b8-ac5f-117fb86b0912.png"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))


DEFAULT_LANGUAGE = "chinese_simplified"
DEFAULT_THEME = "theme-default"