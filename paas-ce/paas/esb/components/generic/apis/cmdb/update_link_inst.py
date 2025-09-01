# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm, TypeCheckField, ListField
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class UpdateLinkInst(Component):
    """
    apiMethod POST

    ### 功能描述

    更新连接关系

    ### 请求参数
      {{ common_args_desc }}
  
    #### 接口参数
 
  	| 字段    | 类型     | 必选   | 描述       |
	| ----- | ------ | ---- | -------- |
	| method | str | 是    | 请求方法（POST, DELETE） |
	| model_code | str | 是    | 模型名code |
	| model_code_name | str | 是    | 模型名 |
	| field_code | str | 是    | 字段code(增加) |
	| target_code_list | list | 是    | 字段code（删除） |
	| target_code | int | 是    | 关联的目标code |



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
        model_code = forms.Field()
        model_code_name = forms.Field()
        field_code = forms.Field()
        target_code_list = forms.Field(required=False)
        target_code = forms.Field(required=False)
        method = forms.Field()
        # pass
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["model_code", "model_code_name", "field_code", "target_code", "method", "target_code_list"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username
        
        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}update-link-inst/'.format(base_api_url),
            data=json.dumps(params),
            # cookies=self.request.wsgi_request.COOKIES,
            headers=self.request.wsgi_request.g.headers if hasattr(self.request.wsgi_request, "g") else self.request.wsgi_request.headers
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
