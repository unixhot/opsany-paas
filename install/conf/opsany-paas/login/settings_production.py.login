# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

生产环境配置
""" # noqa

DEBUG = False

# Log settings
LOG_LEVEL = 'ERROR'

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
        'PASSWORD': 'MYSQL_OPSANY_PASSWORD',
        'HOST': 'MYSQL_SERVER_IP',
        'PORT': '3306',
    }
}

# 初始化用户名、密码
USERNAME = 'admin'
PASSWORD = 'admin'

# inner domain, use consul domain,  for api
PAAS_INNER_DOMAIN = 'LOCAL_IP'
HTTP_SCHEMA = 'https'


# cookie访问域
BK_COOKIE_DOMAIN = 'DOMAIN_NAME'
CSRF_TRUSTED_ORIGINS = [
    'https://DOMAIN_NAME',
    'http://DOMAIN_NAME',
]

SECRET_KEY = 'jO149njrTj4kEx6ZbUH8Zc53bfQJctINWaEzTWIsOoxSDNwK2I'

# ESB Token
ESB_TOKEN = '41f076b7-afce-46eb-9e85-dab245eb0931'
RBAC_APP_SECRET = "RBAC_SECRET_KEY"
