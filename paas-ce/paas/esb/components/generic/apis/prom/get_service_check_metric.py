# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class get_service_check_metric(Component):
    """
    apiMethod GET

    ### 功能描述

    获取应用监控服务拨测波测数据

    ### 请求参数
    {{ common_args_desc }}
    
    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | id | int | 是    |  服务拨测ID |
    | data_type | str | 是    |  数据类型(response_time, probability, history) |
    | time | list or str | 否   | 间隔时间(3, 12, 24, 168, 720) |
    | start_time | str | 否    | 开始时间(2020-09-02 18:38:01) |
    | end_time | str | 否    | 结束时间(2020-10-02 18:38:01)  |
    | current | str | 否    | 第几页 |
    | pageSize | str | 否    | 每页数量 |

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
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        id = forms.Field(required=True)
        data_type = forms.Field(required=True)
        time = forms.Field(required=False)
        start_time = forms.Field(required=False)
        end_time = forms.Field(required=False)
        current = forms.Field(required=False)
        pageSize = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["id", "data_type", "time", "start_time", "end_time", "current", "pageSize"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-service-check-metric/'.format(configs.base_api_url),
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