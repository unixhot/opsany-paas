# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import copy

from common.log import logger_api, logger
from common.base_utils import datetime_format


class BasicRequestLogger(object):
    """
    Basic Request Logger
    """

    def write(self, request, response):
        # 记录原始的请求参数，而不是被修改过的kwargs
        if getattr(request, "kwargs_copy", {}):
            kwargs = request.kwargs_copy
        elif getattr(request, "kwargs", {}):
            kwargs = request.kwargs
        else:
            kwargs = {}
        if request.system_name == 'CMSI' and request.component_alias_name == 'send_mail':
            kwargs = copy.copy(kwargs)
            kwargs.pop('attachments', None)
        msecs_cost = (request.ts_request_end - request.ts_request_start) * 1000
        if isinstance(response, dict):
            message = response and response.get('message', '')
        else:
            message = ''

        try:
            request_log = {
                'message': 'ESB request finished, method=%s system=%s component=%s' % (
                    request.method, request.system_name, request.component_alias_name),
                'type': 'pyls-comp-request',
                'request_id': getattr(request, "request_id", ""),
                'req_app_code': getattr(request, "app_code", ""),
                'req_username': getattr(request, "current_user_username", ""),
                'req_system_name': request.system_name,
                'req_component_name': request.component_alias_name,
                'req_client_ip': getattr(request, "client_ip", ""),
                'req_params': json.dumps(kwargs),
                'req_use_test_env': getattr(request, "use_test_env", ""),
                'req_status': getattr(request, "component_status", -1),
                'req_message': message,
                'req_msecs_cost': int(msecs_cost),
                'req_start_time': datetime_format(request.ts_request_start),
                'req_end_time': datetime_format(request.ts_request_end),
            }
            # Log to logstash, type="pyls-comp-request"
            logger_api.info(json.dumps(request_log))
        except Exception as e:
            logger.warning('logger reqeust exception: %s' % e)
