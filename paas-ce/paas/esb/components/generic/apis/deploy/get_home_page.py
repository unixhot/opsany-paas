
# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetHomePage(Component):
    """
    apiMethod GET

    ### 功能描述

    获取当前应用下持续部署资源统计

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code | str | 是 | 应用的code |


    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20002,
        "message": "信息获取成功",
        "data": {
            "deploy_task_count": 1,
            "seven_days_deploy_log_all_count": 0,
            "seven_days_deploy_log_status": {
                "seven_days_deploy_success_count": 0,
                "seven_days_deploy_fail_count": 0
            },
            "daily_success_counts": [
                {
                    "date": "2024-05-04",
                    "success_count": 0
                },
                {
                    "date": "2024-05-05",
                    "success_count": 0
                },
                {
                    "date": "2024-05-06",
                    "success_count": 0
                },
                {
                    "date": "2024-05-07",
                    "success_count": 0
                },
                {
                    "date": "2024-05-08",
                    "success_count": 0
                },
                {
                    "date": "2024-05-09",
                    "success_count": 0
                },
                {
                    "date": "2024-05-10",
                    "success_count": 0
                }
            ],
            "daily_error_counts": [
                {
                    "date": "2024-05-04",
                    "error_count": 0
                },
                {
                    "date": "2024-05-05",
                    "error_count": 0
                },
                {
                    "date": "2024-05-06",
                    "error_count": 0
                },
                {
                    "date": "2024-05-07",
                    "error_count": 0
                },
                {
                    "date": "2024-05-08",
                    "error_count": 0
                },
                {
                    "date": "2024-05-09",
                    "error_count": 0
                },
                {
                    "date": "2024-05-10",
                    "error_count": 0
                }
            ]
        }
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        code = forms.CharField(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["code"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-home-page/'.format(base_api_url),
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