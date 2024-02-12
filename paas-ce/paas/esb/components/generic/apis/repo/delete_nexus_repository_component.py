# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class DeleteNexusRepositoryComponent(Component):
    """
    apiMethod DELETE

    ### 功能描述

    删除制品

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code | int | 是 | 应用id |
    | repository_id | str | 是 | 制品库名称
    | component_id | str | 是 | 制品id |
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20003,
        "message": "信息删除成功",
        "data": ""
    }
    ```
    """  #

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        code = forms.IntegerField(required=True)
        repository_id = forms.CharField(required=True)
        component_id = forms.CharField(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["code", "repository_id", "component_id"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.delete(
            host=configs.host,
            path='{}delete-nexus-repository-component/'.format(base_api_url),
            params=None,
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
                'data': response.get("data", None),
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message'],
                'response': response,
                'data': response.get("data", None),
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
