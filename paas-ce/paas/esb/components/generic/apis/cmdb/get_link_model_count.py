# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetLinkModelCount(Component):
    """
    apiMethod POST

    ### 功能描述

    获取实例关联指定模型总数

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | inst_model_code | str | 是  | 模型code |
    | model_code_name_list | list | 是  | 当前模型实例列表 |
    | field_code_list | dict | 是  | 关联模型字段code列表 |

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
    	inst_model_code = forms.Field(required=True)
        model_code_name_list = forms.Field(required=True)
        field_code_list = forms.Field(required=True)
        # group_list = forms.ListField(required=True)
        pass
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["inst_model_code", "model_code_name_list", "field_code_list"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}get-link-model-count/'.format(base_api_url),
            # params=params,
            data=json.dumps(params),
            # data=params,
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
