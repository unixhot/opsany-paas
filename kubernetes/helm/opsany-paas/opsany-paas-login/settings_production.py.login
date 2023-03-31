# -*- coding: utf-8 -*-
"""
生产环境配置
""" # noqa

DEBUG = False

# use the static root 'static' in production envs
if not DEBUG:
    STATIC_ROOT = 'static'

# 生产环境, 使用nginx反向代理 /login/static/
SITE_URL = "/login/"

STATIC_URL = "/static/"

# 数据库配置信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 默认用mysql
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': 'OpsAny@2023',
        'HOST': 'opsany-mysql',
        'PORT': '3306',
    }
}

# 初始化用户名、密码
USERNAME = 'admin'
PASSWORD = 'admin'

# inner domain, use consul domain,  for api
PAAS_INNER_DOMAIN = 'opsany-paas-openresty'
HTTP_SCHEMA = 'https'


# cookie访问域
BK_COOKIE_DOMAIN = 'test.opsany.cn'

SECRET_KEY = 'jO149njrTj4kEx6ZbUH8Zc53bfQJctINWaEzTWIsOoxSDNwK2I'

# ESB Token
ESB_TOKEN = '41f076b7-afce-46eb-9e85-dab245eb0931'
