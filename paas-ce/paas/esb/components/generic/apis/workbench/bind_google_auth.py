# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class BindGoogleAuth(Component):
    """
    apiMethod POST

    ### 功能描述

    绑定MFA

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | verify_code | string | 是  | 授权码 |
    | secret | string | 是  | 秘钥 |
    | username | string | 是  | 用户名 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "receiver":  xx,
        "text":  xx,
        "subject":  xx,
        "text_type":  xx"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20003,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "信息发送成功"
    }
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        verify_code = forms.Field(required=True)
        secret = forms.Field(required=True)
        username = forms.Field(required=True)
        operator = forms.Field(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["operator", "verify_code", "secret", "username"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        data = self.form_data

        # 设置当前操作者
        # data['operator'] = self.current_user.username

        # 请求系统接口
        # print "self.request.wsgi_request.COOKIES"
        # print self.request.wsgi_request.COOKIES
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}google-auth/'.format(base_api_url),
            params=None,
            data=json.dumps(data),
            cookies=self.request.wsgi_request.COOKIES,
        )

        # 对结果进行解析
        print response
        print "qqqqqqqqqqqqqqqqqqqqqqq"
        code = response['code']
        if code == 200:
            result = {
                'code': response['code'],
                'api_code': response['successcode'],
                'message': response['message'],
                'result': True,
                'data': response,
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message'],
                'data': response
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result

