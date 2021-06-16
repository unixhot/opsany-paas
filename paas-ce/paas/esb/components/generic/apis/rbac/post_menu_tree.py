# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class PostMenuTree(Component):
    """
    apiMethod POST

    ### 功能描述

    获取该用户在特定平台的目录树

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段           | 类型   | 必选 | 描述       |
    | -----          | ------ | ---- | --------   |
    | platform_cname | string |  是  | 平台别名   |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "xxxx",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "platform_cname":  "workbench"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "status_code": 0,
        "status_info": "string",
        "data": {
            "menu_name": "string",
            "menu_code": "string",
            "id": 0,
            "priority": "string",
            "menu_type": "platform",
            "parent_id": null,
            "menu_address": "string",
            "children": [
                {
                    "menu_name": "string",
                    "menu_code": "string",
                    "id": 0,
                    "priority": "string",
                    "menu_type": "directory",
                    "parent_id": 1,
                    "menu_address": "string",
                    "children": [
                        {}
                    ]
                }
            ]
        }
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        # platform_cname = forms.Field()
        platform_cname = forms.CharField(required=True)     
        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["platform_cname"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        #data = self.form_data
        #params = {}
        #params = self.request.wsgi_request.body
        params = self.form_data
        data = self.request.wsgi_request.body

        # 设置当前操作者
        params["operator"] = str(self.current_user.username)
        #params = {"operator":str(self.current_user.username)}

        # 请求系统接口
        try:
            response = self.outgoing.http_client.post(
                host = configs.host,
                path = configs.base_api_url + 'auth/tree/',
                data = data,
                params=params,
                cookies=self.request.wsgi_request.COOKIES,
            )
        except:
            pass

        # 对结果进行解析
        code = response.get('code') if response.get('code') else response.get('status_code')
 
        if code == 0:
            result = {
                'status_code': 0,
                'data': response['data'],
            }
        else:
            result = {
                'status_code': 1,
                'status_info': response.get('status_info') if response.get('status_info') else response.get('message')
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
