# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetUserAuthApi(Component):
    """
    apiMethod GET

    ### 功能描述

    获取当前用户授权的api

    ### 请求参数
    {{ common_args_desc }}


    #### 接口参数

    | 字段           | 类型   | 必选 | 描述       |
    | -----          | ------ | ---- | --------   |
    | platform_cname | string |  是  | 平台别名   |
    | username | string |  是  | 用户名   |
    | access_token | string |  是  | access_token   |

    ### 返回结果示例

    ```python
    {
        "code": "200",
        "successcode": "20023",
        "message": "操作成功",
        "data": {
            "/api/workbench/v0_1/user-info/___GET",
            "/api/workbench/v0_1/nav-group/___PUT"
        },
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        platform_code = forms.CharField(required=True)
        username = forms.CharField(required=True)
        access_token = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["platform_code", "username", "access_token"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path=configs.base_api_url + 'user-auth-api/',
            params=params,
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
                'data': response.get("data", []),
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result

