# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetTencentReginList(Component):
    """
    apiMethod GET

    ### 功能描述

    查询腾讯云地区列表(非最新)

    ### 请求参数
    {{ common_args_desc }}

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20001,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "公有云地区列表获取成功",
        "data": [
            {
                "service_provider": 2,
                "region_id": "ap-beijing",
                "region_name": "华北地区(北京)"
            },
            {
                "service_provider": 2,
                "region_id": "ap-chengdu",
                "region_name": "西南地区(成都)"
            }
        ]
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        pass

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist()

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}tencent-regin/'.format(base_api_url),
            params=json.dumps(params),
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
