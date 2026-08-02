# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class KbaseList(Component):
    """
    apiMethod GET

    ### 功能描述

    知识库列表

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | data_type     | string    |  是  | 脚本类型  all:全部知识库, public:公共知识库, involved:我参与的知识库, favorite:我收藏的知识库, owner: 我拥有的知识库 |
    | search_type     | string    |  否  | 搜索字段 |
    | search_data     | string    |  否  | 搜索值 |
    | kbase_role     | string    |  否  | 知识库权限 |
    | params     | string    |  否  | 额外参数 |

    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20005,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "相关信息获取成功",
        "data": [
            {
				...
            }
        ]
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        data_type = forms.CharField()
        search_type = forms.CharField(required=False)
        search_data = forms.CharField(required=False)
        kbase_role = forms.CharField(required=False)
        params = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["data_type", "search_type", "search_data", "kbase_role", "params"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}kbase-list/'.format(configs.base_api_url),
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
                'message': response['message'],
                'response': response,
                'data': response.get("data", None),
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
