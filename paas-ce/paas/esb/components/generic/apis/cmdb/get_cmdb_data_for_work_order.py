# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetCmdbDataForWorkOrder(Component):
    """
    apiMethod GET

    ### 功能描述

    根据模型code和字段列表获取资源数据和字段-支持获取连接关联数据(资源授权认证)

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | model_code | str | 否   | 模型code APPLICATION |
    | model_field_code_str | dict | 否   | 字段 APPLICATION_name,APPLICATION_VISIBLE_NAME  |
    | is_auth | dict | 否   | 认证数据 1 |
    | is_link | dict | 否   | 是否获取连接数据 |
    | auth_username | dict | 否   | 认证用户名 |

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
        model_code = forms.Field(required=True)
        model_field_code_str = forms.Field(required=False)
        field_list = forms.Field(required=False)
        is_auth = forms.Field(required=False)
        is_link = forms.Field(required=False)
        auth_username = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["model_code", "model_field_code_str", "field_list", "is_link", "is_auth", "auth_username"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params["operator"] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path="{}get-cmdb_data-for-work-order/".format(base_api_url),
            params=params,
            data=None,
            cookies=self.request.wsgi_request.COOKIES,
        )

        # 对结果进行解析
        code = response["code"]
        if code == 200:
            result = {
                "code": response["code"],
                "api_code": response["successcode"],
                "message": response["message"],
                "result": True,
                "data": response.get("data", None),
            }
        else:
            result = {
                "api_code": response["errcode"],
                "result": False,
                "message": response["message"]
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
