# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetCacheToken(Component):
    """
    apiMethod POST

    ### 功能描述

    根据用户输入内容获取堡垒机连接用token
 

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数
    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | ip | string | 是  | 连接主机的IP地址 |
    | name | string | 是  | 主机名 |
    | ssh_port | int | 是  | 连接端口 |
    | system_type | string | 是  | 系统类型(Linux/Windows) |
    | username | string | 否  | 登陆主机用户名 |
    | ssh_key_id | int | 否  | 使用的秘钥ID |
    | password | string | 否  | 当username存在时为登陆的密码，当ssh_key_id存在时为passphrase |
    | network_proxy | string | 否  | 网络代理 |

    ### 请求参数示例

    ### 返回结果示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "ip": "",
        "name": "",
        "ssh_port": "",
        "system_type": "",
        "username": "",
        "ssh_key_id": "",
        "password": "",
        "network_proxy": 1,
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        ip = forms.CharField()
        name = forms.CharField()
        ssh_port = forms.IntegerField()
        system_type = forms.CharField()
        username = forms.CharField(required=False)
        ssh_key_id = forms.IntegerField(required=False)
        password = forms.CharField(required=False)
        network_proxy = forms.CharField(required=False)
        timeout = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["ip", "name", "ssh_port", "system_type", "username", "ssh_key_id", "password", "network_proxy", "timeout"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path=configs.base_api_url + 'get-cache-token/',
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
                'data': response['data'],
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
