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


class GetImportModelTree(Component):
    """
    apiMethod GET

    ### 功能描述

    获取模型树

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | model_code | str | 否   | 模型code |
    | data_type | str | 否   | 数据类型 data_tree,model_tree,parent_model_code,parent_model_data_id, |
    | parent_model_data_id | str | 否   | 父级ID |
    | search_type | str | 否   | 搜索类型 |
    | search_data | str | 否   | 搜索数据 |
    | page | int | 否   | 页码 |
    | per_page | int | 否   | 页数 |

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20007,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息获取成功",
        "data": {
        }
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        model_code = forms.Field()
        data_type = forms.Field()
        parent_model_data_id = forms.Field(required=False)
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        page = forms.Field(required=False)
        per_page = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['model_code', 'data_type', 'parent_model_data_id', 'search_type', 'search_data', 'model_code_list', 'page', 'per_page'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}import-model-tree/'.format(base_api_url),
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
