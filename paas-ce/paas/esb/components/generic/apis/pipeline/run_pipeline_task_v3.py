# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class RunPipelineTaskV3(Component):
    """
    apiMethod POST

    ### 功能描述

    执行流水线

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | application_name | string | 是  | 应用唯一标识 |
    | job_name | string | 是  | 流水线名称 |
    | parameters | string | 是  | 流水线参数 |
    | req_source | string | 是  |执行方式 |
    | app_from | string | 是  | 调用应用 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "application_name": "opsany",
        "job_name": "job_name",
        "req_source": "API调用",
        "app_from": "workbench",
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
    """


    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        application_name = forms.CharField(required=True)
        job_name = forms.Field(required=True)
        parameters = forms.Field(required=False)
        req_source = forms.Field(required=False)
        app_from = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["application_name", "job_name", "parameters", "req_source", "app_from"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username
        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}api/run-pipeline-v3/'.format(base_api_url),
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
                'message': response['message'],
                'request_data': params
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
