# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class PostMenuPrivilege(Component):
    """
    apiMethod POST

    ### 功能描述

    获取用户对菜单的权限列表

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段           | 类型   | 必选 | 描述       |
    | -----          | ------ | ---- | --------   |
    | platform_cname | string |  是  | 平台别名   |
    | menu_code      | string |  是  | menu_code  |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "xxxx",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "platform_cname":  "workbench",
        "menu_code":  "setting"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "status_code": 0,
        "status_info": "string",
        "data": "[C, U, R, D]"
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        pass

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist()

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data
        data = self.request.wsgi_request.body

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path=configs.base_api_url + 'auth/privilege/',
            data = data,
            params = params,
            cookies=self.request.wsgi_request.COOKIES,
        )

        # 对结果进行解析
        code = response['status_code']
        if code == 0:
            result = {
                'status_code': 0,
                'data': response['data'],
            }
        else:
            result = {
                'status_code': 1,
                'status_info': response['status_info']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result