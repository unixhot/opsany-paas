# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class SendRobot(Component):
    """
    apiMethod POST

    ### 功能描述

    发送企微钉钉群告警通知

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | robot_type | str | 是  | 群类型 qw dd |
    | temp_id | int | 是  | 模板ID |
    | parameter | str | 是  | 参数 |
    | robot_list | str | 是  | 群标识 |
    | alert_info | str | 是  | 告警对象 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "nav_id":  xx
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20003,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息获取成功",
        "data": [
			...
        ]
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        robot_type = forms.CharField(required=True)
        temp_id = forms.IntegerField(required=True)
        parameter = forms.Field(required=True)
        robot_list = forms.Field(required=True)
        alert_info = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["robot_type", "temp_id", "parameter", "robot_list", "alert_info"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        data = self.form_data

        # 设置当前操作者
        data['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}send-robot/'.format(base_api_url),
            params=None,
            data=json.dumps(data),
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
                'message': response['message']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
