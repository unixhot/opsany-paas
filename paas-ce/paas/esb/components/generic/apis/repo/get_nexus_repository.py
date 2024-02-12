# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetNexusRepository(Component):
    """
    apiMethod GET

    ### 功能描述

    获取制品库

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | format_type | str | 否 | 制品库格式 |
    | list_type | str | 否 | 根据这个来判断获取收藏的制品库 |
    | search_type | str | 否 | 根据制品库名称搜索 |
    | search_data | str | 否 | 搜索的关键字或搜索数据 |
    | code | int | 是 | 应用id |
    ```

    ### 返回结果示例

    ```python
    {
    "code": 200,
    "successcode": 20002,
    "message": "信息获取成功",
    "data": {
        "inner_list": [],
        "public_list": [
                {
                    "code": x,
                    "is_app": false,
                    "name": "maven-central",
                    "type": "proxy",
                    "format": "maven2",
                    "status": "Online",
                    "url": "http://127.0.0.1:8000/repository/maven-central",
                    "describe": "",
                    "attributes": {
                        "proxy": {
                            "remoteUrl": "https://repo1.maven.org/maven2/"
                        }
                    },
                    "active_time": null,
                    "tags": false
                },
                ......
            ]
        }
    }
    ```
    """  #

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        format_type = forms.CharField(required=False)
        list_type = forms.CharField(required=False)
        search_type = forms.CharField(required=False)
        search_data = forms.CharField(required=False)
        code = forms.IntegerField(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["format_type", "list_type", "search_type", "search_data", "code"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-nexus-repository/'.format(base_api_url),
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
