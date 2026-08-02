# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class KbaseArticle(Component):
    """
    apiMethod GET

    ### 功能描述

    知识库内文章

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | data_type     | string    |  是  | 脚本类型  all:全部文章, self:我的文章, folder:根据目录筛选文章, favorite:我收藏的文章, single:单条 |
    | kbase     | string    |  是  | 知识库唯一标识 |
    | unique_code     | string    |  否  | 文章唯一标识(单条文章) |
    | current     | string    |  否  | 当前页码 |
    | pageSize     | string    |  否  | 每页条数 |
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
        data_type = forms.CharField(required=False)
        kbase = forms.CharField()
        unique_code = forms.CharField(required=False)
        current = forms.CharField(required=False)
        pageSize = forms.CharField(required=False)
        search_type = forms.CharField(required=False)
        search_data = forms.CharField(required=False)
        params = forms.CharField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["data_type", "kbase", "unique_code", "current", "pageSize",
                                                          "search_type", "search_data", "kbase_role", "params"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}kbase-article/'.format(configs.base_api_url),
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
