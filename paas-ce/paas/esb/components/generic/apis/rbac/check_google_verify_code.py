# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class CheckGoogleVerifyCode(Component):
    """
    apiMethod POST

    ### 功能描述

    验证用户的验证码是否正确

    ### 请求参数
    {{ common_args_desc }}


    ### 返回结果示例

    ```python
    ```
    """#

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        username = forms.CharField(required=True)
        verify_code = forms.CharField(required=True)
        seven_days_free = forms.CharField(required=False)
        auth_type = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["username", "verify_code", "seven_days_free", "auth_type"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}check-google-verify-code/'.format(configs.base_api_url),
            data=json.dumps(params),
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

