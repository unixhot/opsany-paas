# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class UpdateAgentStateV2(Component):
    """
    apiMethod POST

    ### 功能描述

    更新节点的Agent情况v2(资源授权认证)

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | list | array | 是    | 节点列表 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
         "list":[
            {
                "ip": "127.0.0.1",
                "agent": "Agent正常",
                "controller_name": "default.None"
            },
            {
                "ip": "127.0.0.2",
                "agent": "Agent未安装",
                "controller_name": "default.None"
            }
        ]
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20001,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息更新成功",
        "data":  [
        {
            "code": 22,
            "model_code": "SERVER",
            "data": {
                "SERVER_name": "xxxxx",
                "SERVER_IN_RACK": "xxxxx",
                "SERVER_HOSTNAME": "xxxxx",
                "SERVER_INTERNAL_IP": "",
                "SERVER_PUBLIC_IP": "xxxx",
                "SERVER_AGENT_STATE": "Agent正常",
                "SERVER_CONTROLLER_NAME": "default.None"
            },
            "pk_name": "SERVER_name",
            "pk_value": "xxxxx",
            "position": "xx",
            "import_type": "逐条录入",
            "link_inst": [],
            "parent_inst": "xx",
            "business_code": "x"
        }
    ]
    }
    ```

    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        update_list = forms.Field()

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['update_list'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data
        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}update-agent-v2/'.format(base_api_url),
            params=None,
            data=json.dumps(params),
            cookies=self.request.wsgi_request.COOKIES,
            headers=self.request.wsgi_request.g.headers if hasattr(self.request.wsgi_request, "g") else self.request.wsgi_request.headers
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
