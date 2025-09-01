# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetAlarmRank(Component):
    """
    apiMethod GET

    ### 功能描述

    获取报警排名

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | search_type | string | 否  | 分类搜索类型 |
    | search_data | string | 否  | 分类搜索内容 |
    | group_id | string | 否  | 主机组id |
    | host_id | string | 否  | 主机id |
    | create_min_time | string | 否  | 开始时间 |
    | create_max_time | string | 否  | 结束时间 |
    | severity | array | 否  | 分类搜索内容 |


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
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        group_id = forms.Field(required=False)
        host_id = forms.Field(required=False)
        create_min_time = forms.Field(required=False)
        create_max_time = forms.Field(required=False)
        severity = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=[
                "search_type",
                "group_id",
                "host_id",
                "create_min_time",
                "create_max_time",
                "search_data",
                "severity",
            ])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}alarm-rank/'.format(base_api_url),
            params=params,
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
