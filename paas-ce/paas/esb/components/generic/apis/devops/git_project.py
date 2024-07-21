# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class PostScript(Component):
    """
    apiMethod POST

    ### 功能描述

    执行脚本

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | host_list | list | 是  | 主机唯一标识列表 |
    | script_url | string | 是  | 脚本相对路径URL |
    | script_arg | string | 否  | 脚本参数 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "host_list":  ["unique value1", "unique value2", "unique value3"],
        "script_url": "uploads/xxx/xxx/xxx.py",
        "script_arg": "arg1 arg2 arg3"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20003,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "操作成功",
        "data": "xxxxxxx"
    }
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        host_list = forms.Field()
        script_url = forms.Field()
        script_arg = forms.Field(required=False)
        timeout = forms.IntegerField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["host_list", "script_url", "script_arg", "timeout"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username
        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}script/'.format(base_api_url.replace("api/control/v0_1/", "api/execution/v0_1/")),
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
                'api_code': response['error_code'],
                'result': False,
                'message': response['message'],
                'request_data': params
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
