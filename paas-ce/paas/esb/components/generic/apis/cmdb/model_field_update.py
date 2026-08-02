# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class ModelFieldUpdate(Component):
    """
    apiMethod POST

    ### 功能描述

    资源模型修改属性(字段)

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code  | string | 是    | 字段唯一标识 |
    | name   | string | 否    | 字段名称 |
    | type_name   | string | 否    | 字段类型 |
    | model_code        | string | 否    | 模型code |
    | field_group_code        | string | 否    | 字段分组 |
    | not_null        | bool | 否    | 是否为空 |
    | built_in        | bool | 否    | 是否必填 |
    | index        | int | 否    | 排序 |
    | attribute        | dict | 否    | 字段属性(包括规则下拉数据等相关配置) |

    """
    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        code = forms.Field()
        name = forms.Field()
        type_name = forms.Field()
        model_code = forms.Field()
        field_group_code = forms.Field()
        not_null = forms.BooleanField(required=False)
        built_in = forms.BooleanField(required=False)
        index = forms.IntegerField(required=False)
        attribute = forms.Field()

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["code", "name", "type_name", "model_code", "field_group_code",
                                                          "not_null", "built_in", "index", "attribute"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        data = self.request.wsgi_request.body

        # 设置当前操作者
        params = {"operator": self.current_user.username}
        # 请求系统接口
        response = self.outgoing.http_client.put(
            host=configs.host,
            path="{}model-field-operation/".format(base_api_url),
            params=params,
            data=data,
            # cookies=self.request.wsgi_request.COOKIES,
            headers=self.request.wsgi_request.g.headers if hasattr(self.request.wsgi_request, "g") else self.request.wsgi_request.headers
        )

        # 对结果进行解析
        code = response["code"]
        if code == 200:
            result = {
                "code": response["code"],
                "api_code": response["successcode"],
                "message": response["message"],
                "result": True,
                "data": response["data"],
            }
        else:
            result = {
                "api_code": response["errcode"],
                "result": False,
                "message": response["message"]
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
