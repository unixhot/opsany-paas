# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetControllerForPanel(Component):
    """
    apiMethod POST

    ### 功能描述

    通过控制器的name获取控制器信息

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | host_name | string | 是  | 主机名 |
    | ip | string | 是  | IP |
    | ip_type | string | 是  | IP类型 |


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
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        data = forms.Field()

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['data'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}get-controller-for-panel/'.format(base_api_url),
            params=json.dumps(params["data"]),
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
                'data': response['data'],       # 在这里处理返回的数据，可以处理让用户不想看到的内容
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message'],
                'data': data,
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
