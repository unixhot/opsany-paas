# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class AppRelatedProjects(Component):
    """
    apiMethod GET

    ### 功能描述

    获取已关联仓库

    ### 请求参数
    {{ common_args_desc }}
    
    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | app_name | str | 是 | 应用的唯一标识 |
    | search_type | str | 否 | 要查找的数据类型 |
    | search_data | str | 否 | 要查找的关键词 |
    | current | int | 否 | 当前页面 |
    | pageSize | int | 是 | 每页要展示的条数 |


    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20002,
        "message": "信息获取成功",
        "data": {
            "page": 1,
            "per_page": 10,
            "total": 0,
            "data": []
        }
    }
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        app_name = forms.CharField(required=True)
        search_type = forms.CharField(required=False)
        search_data = forms.CharField(required=False)
        current = forms.IntegerField(required=False)
        pageSize = forms.IntegerField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["app_name", "search_type", "search_data", "current", "pageSize"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}app-related-projects/'.format(base_api_url),
            params=params,
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
                'data': response.get("data", None),
            }
        else:
            result = {
                'api_code': response['errcode'],
                'result': False,
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result