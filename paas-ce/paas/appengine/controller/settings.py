# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from controller.settings_default import * # noqa

DEBUG = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': 'OpsAny2025.Dev',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

SECRET_KEY = 'XEz7VLlQNdIq9iFl1t6LtWobQEcG4ayoPa2esHwatkHZxiuDf0'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/static/'
CSRF_TRUSTED_ORIGINS = [
    'https://dev.opsany.cn',
    'http://dev.opsany.cn',
    'http://10.0.0.188:8001',
    'http://10.0.0.56:8001',
    #'https://10.0.0.188:8001',
    'http://115.227.17.162:8001',
    'http://127.0.0.1:8001',
    'http://0.0.0.0:8001',
]
