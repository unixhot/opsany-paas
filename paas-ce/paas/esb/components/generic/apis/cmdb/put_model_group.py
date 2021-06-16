# -*- coding: utf-8 -*-
"""
Copyright © 2012-2017 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class PutModelGroup(Component):
    """
    apiMethod PUT

    ### 功能描述

    更新模型组信息

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code | string | 是    | 模型组code |
    | name | string | 是    | 模型组name |
    | model_type | string | 是    | 模型组类型 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "code": "wmy_host_admin",
        "name": "主机管理",
        "model_type": "zy"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20007,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息更新成功",
        "data": {
            "code": "wmy_host_admin",
            "name": "主机管理",
            "model_type": "zy",
            "built_in": true
        }
    }
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        code = forms.CharField(label=u'code', required=True)
        name = forms.CharField(label=u'name', required=False)
        model_type = forms.CharField(label=u'model_type', required=False)
        built_in = forms.BooleanField(label=u'built_in', required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['code', 'name', 'model_type', 'built_in'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.put(
            host=configs.host,
            path='{}model-group/'.format(base_api_url),
            params=json.dumps(params),
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
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
