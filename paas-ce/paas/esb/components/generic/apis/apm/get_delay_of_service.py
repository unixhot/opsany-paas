# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetDelayOfService(Component):
    """
    apiMethod GET

    ### 功能描述

    应用平台延迟卡片

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | start | datetime | 是 | 过去15分钟的时间 |
    | end | datetime | 是 | 当前时间 |
    |app_id | str | 是 | 应用code

    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20002,
        "message": "信息获取成功",
        "data": {
            "code": 200,
            "api_code": 20008,
            "result": true,
            "request_id": "xxxxxxxxxxxxxxxxxxxxxx",
            "message": "操作成功",
            "data": [
                {
                    ...
                },
                ...
            ]
        }
    }
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        start = forms.Field()
        end = forms.Field()
        app_id = forms.Field()
    
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["start", "end", "app_id"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-delay-of-service/'.format(base_api_url),
            params=params,
            data=None,
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
                'data': response.get("data", None),
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message'],
                'response': response,
                'data': response.get("data", None),
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
