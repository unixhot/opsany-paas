# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class ScriptLibraryCreate(Component):
    """
    apiMethod POST

    ### 功能描述

    脚本仓库创建脚本

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型   | 必选 | 描述      |
    | -----  | ------ | ---- | ------- |
    | script_type     | string    |  是  | 脚本类型  sh, py, ps1, bat |
    | script_name     | string    |  是  | 脚本名称 |
    | script_from     | string    |  是  | 脚本来源|
    | visible     | string    |  是  |可见范围 1: 私有, 2: 公开 |
    | version_remarks     | string    |  是  | 脚本描述 |
    | version     | string    |  是  | 版本号  |
    | script     | string    |  是  | 脚本内容|

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "xxxx",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "platform_cname":  "workbench",
        "task_id":  10
    }
    ```

    ### 返回结果示例

    ```python
    {
        "status_code": 0,
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        script_type = forms.CharField()
        script_name = forms.CharField()
        script_from = forms.CharField()
        visible = forms.CharField()
        version_remarks = forms.CharField(required=False)
        version = forms.CharField()
        script = forms.CharField()

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["script_type", "script_name", "script_from", "visible", "version_remarks", "version", "script"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data
        data = self.request.wsgi_request.body

        # 设置当前操作者
        params = {"operator": self.current_user.username}

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}script-library/'.format(configs.base_api_url),
            data = data,
            params = params,
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
                'data': response.get("data", None)
            }
        self.response.payload = result
