# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm, TypeCheckField, ListField
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetInstByRelData(Component):
    """
    apiMethod POST

    ### 功能描述

    获取模型实例关联模型实例数据

    ### 请求参数
      {{ common_args_desc }}
  
    #### 接口参数
 
    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | inst_model_code | str | 否   | 模型code |
	| model_code_name | str | 是 | 模型名称 |
	| field_code | str | 是    | 模型字段 |
	| search | str | 是   | 搜索 |  
	| current | int | 是    | 当前页 |
	| pageSize | int | 是    | 每页数量 |

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20012,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息更新成功"
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        model_code_name = forms.Field()
        inst_model_code = forms.Field()
        field_code = forms.Field()
        search = forms.Field(required=False)
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        current = forms.Field()
        pageSize = forms.Field()
        # pass
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["model_code_name", "inst_model_code", "field_code", "search", "current", "pageSize", "search_type", "search_data"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username
        
       # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-inst-by-rel-data/'.format(base_api_url),
            params=params,
            headers=self.request.wsgi_request.g.headers
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
