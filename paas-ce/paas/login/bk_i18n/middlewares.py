# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa


import pytz
from django.utils import timezone
from django.conf import settings
from django.utils import translation
from django.utils.translation import trans_real as trans
from django.utils.deprecation import MiddlewareMixin

from bkaccount.constants import LOGIN_API_URL_SUFFIX_LIST


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get(settings.TIMEZONE_SESSION_KEY)
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except pytz.exceptions.UnknownTimeZoneError:
                timezone.deactivate()
        else:
            timezone.deactivate()


class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.session.get(settings.LANGUAGE_SESSION_KEY)
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()


class ApiLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # check api url
        full_path = request.get_full_path()
        is_api_url = False
        for i in LOGIN_API_URL_SUFFIX_LIST:
            if (full_path.startswith(settings.SITE_URL + 'api/v2/' + i + '/')
                    or full_path.startswith(settings.SITE_URL + "accounts/" + i + '/')):
                is_api_url = True
                break
        # only api url do
        if is_api_url:
            try:
                language = request.headers.get('blueking-language', 'en')
                language = trans.get_supported_language_variant(language)
            except Exception:
                language = 'en'
            if language:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
