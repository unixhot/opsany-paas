# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class CreateApplication(Component):
    """
    apiMethod POST

    ### 功能描述

    创建一ing用

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | data | dict | 是  | 应用相关参数 |

    ### 请求参数示例

    ```python
    {
        'model_code': 'APPLICATION',
        'data': {
            'APPLICATION_VISIBLE_NAME': 'XXX',
            'APPLICATION_name': 'OpsAny-Test-unique-20257311018',
            'APPLICATION_ID': 'OpsAny-Test-application-20207311018',
            'APPLICATION_STATUS': '运行中',
            'APPLICATION_COMMENT': '<p>comment</p>',
            'APPLICATION_CeShi': ''XXX'',
            'APPLICATION_XiaLaCaiDan': '001',
            'APPLICATION_DuoXingWenBen': ''XXX' ',
            'APPLICATION_ZhengShu': 5,
            'APPLICATION_FuDianXing': 3,
            'APPLICATION_RiQi': '2025-07-31 10:23:43',
            'APPLICATION_DaoQiShiJian': '2025-07-31 10:18:59',
            'APPLICATION_FuHeShuJu': [{
                '01': '002'
            }, {
                '01': '001'
            }],
            'APPLICATION_MiMa': 'password123',
            'APPLICATION_LianJie': 'www.xxx.com',
            'APPLICATION_FuDianXingShuZi': 4,
            'APPLICATION_ZhengShu01': 3,
            'APPLICATION_ZiFuChuan': 'dsfafgdsafsdaf sfdsf',
            'APPLICATION_FuWenBen': '<p>dsaagfdg富文本</p>',
            'APPLICATION_IN_BUSINESS': 1
        }
    }
    ```

    ### 返回结果示例

    ```python
    {
        code: 200
        data: {code: 49, model_code: "APPLICATION", ......}
        message: "信息创建成功"
        successcode: 20001
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        data = forms.Field(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["data"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}application/'.format(base_api_url),
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
