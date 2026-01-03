# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class MonitorEventAcknowledge(Component):
    """
    apiMethod POST

    ### 功能描述

    Zabbix告警事件的操作

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | event_id | int | 是  | 告警事件ID |
    | host_id | int | 否  | 实例ID(管控实例ID) |
    | zabbix_host_id | int | 否  | 实例ID(Zabbix实例ID) |
    | device_type | str | 是  | 实例类型 |
    | action | int | 是  | 操作类别 |
    | message | str | 否  | 消息内容 |
    | severity | int | 否 | 告警级别 |
    | suppress_until | int | 否 | 被抑制到的Unix时间戳 |
    | event_params | Dict | 否  | 其他参数 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "host_id":  1
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20003,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息更新成功",
        "data": [
            ...
        ]
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        event_id = forms.Field(required=True)
        host_id = forms.Field(required=False)
        zabbix_host_id = forms.Field(required=False)
        device_type = forms.Field(required=False)
        action = forms.Field(required=False)
        message = forms.Field(required=False)
        severity = forms.Field(required=False)
        suppress_until = forms.Field(required=False)
        event_params = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["event_id", "host_id", "zabbix_host_id", "device_type", "action", "message", "severity", "suppress_until", "event_params"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}zabbix-event-acknowledge/'.format(base_api_url),
            data=json.dumps(params),
            cookies=self.request.wsgi_request.COOKIES,
        )

        # 对结果进行解析
        code = response['code']
        if code == 200:
            result = {
                'code': response['code'],
                'api_code': response['successcode'],
                'message': response['message'],
                'result': True,
                'data': response['data'],
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
