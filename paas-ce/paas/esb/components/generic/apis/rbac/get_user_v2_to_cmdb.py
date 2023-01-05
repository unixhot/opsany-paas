# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetUserV2ToCmdb(Component):
    """
    apiMethod GET

    ### 功能描述

    获取当前部门下的全部普通用户信息

    ### 请求参数

    #### 接口参数

    ### 请求参数示例

    ### 返回结果示例

    ```
    {
        "code": 200,
        "successcode": 20005,
        "message": "相关信息信息获取成功",
        "data": {
            "id": 1,
            "content": "Copyright © 2019-2022 OpsAny. All Rights Reserved"
        }
    } 
 	
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        current= forms.Field(required=False)
        pageSize= forms.Field(required=False)
        id= forms.Field(required=False)
        data_type= forms.Field(required=True)
        dep_type= forms.Field(required=False)
        search_type= forms.Field(required=False)
        search_data= forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["current", "pageSize", "id", "data_type", "dep_type", "search_type", "search_data"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path=configs.base_api_url + 'user-v2-to-cmdb/',
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

