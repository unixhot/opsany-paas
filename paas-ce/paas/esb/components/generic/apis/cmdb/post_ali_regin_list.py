# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class PostAliReginList(Component):
    """
    apiMethod POST

    ### 功能描述

    查询阿里云列表

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | keyid | string | 是    | 阿里云keyid |
    | key   | string | 是    | 阿里云key   |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb-test-app",
        "bk_app_secret": "xxx",
        "bk_token": "xxx-xxx-xxx-xxx-xxx",
        "keyid":  "xxxxxxxxxxxxxxxxxxxxxx",
        "key": "xxxxxxxxxxxxxxxxxxx"
    }
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20001
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "公有云地区列表获取成功",
        "data": [
            {
              "RegionId": "cn-qingdao",
              "RegionEndpoint": "ecs.aliyuncs.com",
              "LocalName": "华北 1"
            },
            {
              "RegionId": "cn-beijing",
              "RegionEndpoint": "ecs.aliyuncs.com",
              "LocalName": "华北 2"
            }
        ]
    }
    ```

    """
    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        keyid = forms.CharField(label=u'keyid', required=True)
        key = forms.CharField(label=u'key', required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=['keyid', 'key'])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}ali-regin/'.format(base_api_url),
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
