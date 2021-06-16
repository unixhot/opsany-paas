# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class PostTencentInstInfo(Component):
    """
    apiMethod POST

    ### 功能描述

    根据地区信息查询腾讯云实例列表

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | region_list | array | 是    | 腾讯云地区id列表 |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "region_list":  [
            "ap-bangkok", "ap-beijing"
        ]
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20002,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "公有云实例详细信息查询成功",
        "data": [
            {
              "service_provider": 2,
              "region_id": "ap-bangkok",
              "region_name": "亚太地区(曼谷)",
              "instances_count": 0,
              "instance": []
            },
            {
              "service_provider": 2,
              "region_id": "ap-beijing",
              "region_name": "华北地区(北京)",
              "instances_count": 1,
              "instance": []
            }
        ]
    }
    ```
    """#
    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        region_list = forms.Field(label=u'region_list', required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['region_list'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}tencent-inst/'.format(base_api_url),
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
