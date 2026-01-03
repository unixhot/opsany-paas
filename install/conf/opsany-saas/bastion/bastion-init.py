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
APP_CODE = 'bastion'
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = "BASTION_SECRET_KEY"
# PAAS平台URL
BK_URL = "https://DOMAIN_NAME"
PAAS_ESB_URL = "http://LOCAL_IP:8002"
PAAS_LOGIN_URL = "http://LOCAL_IP:8003"
# UploadPath
UPLOAD_PATH = "/opt/opsany/"
# MFA过期时间，单位：秒
MFA_TIME_OUT = 1800

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))

# 默认语言和主题
DEFAULT_LANGUAGE = "chinese_simplified"
DEFAULT_THEME = "theme-default"
