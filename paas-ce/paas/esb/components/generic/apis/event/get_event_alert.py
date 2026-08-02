# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetEventAlert(Component):
    """
    apiMethod GET

    ### 功能描述

    获取时间中心告警包括我的告警和全部告警

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code | int | 否  | 告警code |
    | start | string | 否  | 单条告警事件开始时间 |
    | end | string | 否  | 单条告警事件开始时间 |
    | current | string | 否  | 当前页码 |
    | pageSize | string | 否  | 每页数量 |
    | alert_type | string | 否  | 告警类型 my_alert：我的告警 all_alert：全部告警 |
    | status | string | 否  | 告警状态 1：待处理 2：处理中 3：已关闭 |
    | search_type | str | 否   | 筛选字段 |
    | search_data | str | 否   | 筛选数据 |
    | alert_subject | str | 否   | 告警标题 |
    | alert_source | str | 否   | 告警来源 |
    | alert_message | str | 否   | 告警内容 |
    | event_id | str | 否   | 告警ID |
    | hostname | str | 否   | 告警唯一标识 |
    | show_name | str | 否   | 实例名称 |
    | host_ip | str | 否   | 实例IP |
    | trigger_severity | str | 否   | 告警级别 |
    | params | string | 否  | 额外参数 |

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
        code = forms.Field(required=False)
        start = forms.Field(required=False)
        end = forms.Field(required=False)
        current = forms.Field(required=False)
        pageSize = forms.Field(required=False)
        alert_type = forms.Field(required=False)
        status = forms.Field(required=False)
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        alert_source = forms.Field(required=False)
        alert_subject = forms.Field(required=False)
        alert_message = forms.Field(required=False)
        event_id = forms.Field(required=False)
        hostname = forms.Field(required=False)
        show_name = forms.Field(required=False)
        host_ip = forms.Field(required=False)
        trigger_severity = forms.Field(required=False)
        params = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["code", "start", "end", "current", "pageSize", "alert_type",
                                                          "status", "search_type", "search_data", "alert_subject",
                                                          "alert_message", "event_id", "hostname", "show_name",
                                                          "host_ip", "trigger_severity", "params", "alert_source"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-alert/'.format(configs.base_api_url),
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
