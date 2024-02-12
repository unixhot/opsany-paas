# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class PostNexusRepository(Component):
    """
    apiMethod POST

    ### 功能描述

    新建制品库

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | repository_id | str | 是 | 制品库名称 |
    | code | int | 是 | 应用id |
    | inner | Bool | 是 | 区分权限（当前或全部应用） |
    | describe | str | 否 | 描述 |
    | repository_type | str | 是 | 制品库类型 |
    | parameters | str | 否 | 其他参数 |
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20001,
        "message": "信息创建成功",
        "data": ""
    }
    ```
    """  #

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        repository_id = forms.CharField(required=True)
        code = forms.IntegerField(required=True)
        inner = forms.BooleanField(required=False)
        describe = forms.CharField(required=False)
        repository_type = forms.CharField(required=True)
        parameters = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["repository_id", "code", "inner", "describe", "repository_type", "parameters"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}post-nexus-repository/'.format(base_api_url),
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
