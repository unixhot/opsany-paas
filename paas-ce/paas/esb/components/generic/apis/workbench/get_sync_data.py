# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetSyncData(Component):
    """
    apiMethod GET

    ### 功能描述

    同步用户信息和组织信息

    ### 请求参数

    #### 接口参数

    ### 请求参数示例

    ### 返回结果示例

    ```python
 	
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
        try:
            response = self.outgoing.http_client.get(
                host=configs.host,
                path=configs.base_api_url + 'get_sync_data/',
                params=params,
                data=None,
                cookies=self.request.wsgi_request.COOKIES,	            
            )
        except:
            pass

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
