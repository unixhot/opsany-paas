# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetControlAgentInfo(Component):
    """
    apiMethod GET

    ### 功能描述

    获取管控平台Agent列表

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | token_data | str | 是  | token |
    | system_type | str | 是  | 系统类型 |
    | group_type | string | 是  | 分组ID |
    | search_type | string | 是  | 搜索字段 |
    | search_data | string | 是  | 搜索内容 |
    | group_level | string | 是  | 获取主机分组深度 |


    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20012,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "获取相关信息成功"
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        token_data = forms.Field(required=True)
        system_type = forms.Field(required=False)
        group_type = forms.Field(required=False)
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        group_level = forms.Field(required=False)
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["token_data", "system_type", "group_type", "search_type", "search_data", "group_level"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # bk_token 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}get-host-info/'.format(base_api_url),
            params=None,
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
                'data': response.get("data", None),
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
