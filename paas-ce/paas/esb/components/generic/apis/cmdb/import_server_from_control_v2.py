# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class ImportServerFromControlV2(Component):
    """
    apiMethod POST

    ### 功能描述

    同步管控新建主机v2(资源授权认证)

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | grains_data | 符合类型 | 是    | 导入信息 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "grains_data":  {
        'grains_data': {
            'CLOUD_SERVER_HOSTNAME': 'www.xxxxxxxxx.com',
            ....
        },
        'pk_name': 'xxxxxxxxxxxxx',
        'pk_value': 'xxxxxxxxxxx',
        'model_code': 'xxxxxxxxxxxxxxxx',
        'import_type': 'Agent采集',
        'position': 'xxxxxxxxxxx'
    }
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20002,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息创建成功",
        "grains_data": {
            ...
        }
    }
    ```

    """
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
        # print(self.request.wsgi_request.COOKIES)
        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}import-server-from-control-v2/'.format(base_api_url),
            # params=json.dumps(params),
            data=json.dumps(params),
            # cookies=self.request.wsgi_request.COOKIES,
            headers=self.request.wsgi_request.g.headers
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
