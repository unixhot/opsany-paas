# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['celery_app', 'RUN_VER', 'APP_CODE', 'SECRET_KEY', 'BK_URL', 'BASE_DIR']

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

# app 基本信息

# SaaS运行版本，如非必要请勿修改
RUN_VER = 'open'
# SaaS应用ID
APP_CODE = 'auto'
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = os.getenv("APP_TOKEN", 'AUTO_SECRET_KEY')
# PAAS平台URL
BK_URL = os.getenv("BK_PAAS_HOST", "https://DOMAIN_NAME")
# 默认头像
DEFAULT_USER_ICON = os.getenv("DEFAULT_USER_ICON",
                              "uploads/workbench/user_icon/edfb99ee-08d6-41b8-ac5f-117fb86b0912.png")
# Upload目录
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/opt/opsany/")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))


DEFAULT_LANGUAGE = "chinese_simplified"
DEFAULT_THEME = "theme-default"
