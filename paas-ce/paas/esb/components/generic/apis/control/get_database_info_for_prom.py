# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetDatabaseInfoForProm(Component):
    """
    apiMethod GET

    ### 功能描述

    获取数据库组下的数据库（应用监控）

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型    | 必选    | 描述    |
    | ------ | ------ | ------ | ------ |
    | search_type | str | 否 | 筛选字段 |
    | search_data | str | 否 | 筛选数据 |
    | page | int | 是 | 要查询的当前页 |
    | per_page | int | 是 | 每页的数据数量 |
    | group_id | int | 否 | 查询指定分组下的数据 |
    | order_by | str | 否 | 按照指定字段进行排序 |
    | id | int | 否 | 获取数据库详情页 |
    | prom_state | str | 否 | 高级搜索-可用性 |
    | alert_count | str | 否 | 高级搜索-未恢复告警 |

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "apicode": 20012,
        "result": true,
        "request_id": xxxxxxxxxxxxxxxxxxxxxxxx,
        "message": "获取相关信息成功"
    }
    ```
    """

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        search_type = forms.Field(required=False)
        search_data = forms.Field(required=False)
        page = forms.Field()
        per_page = forms.Field()
        group_id = forms.Field(required=False)
        order_by = forms.Field(required=False)
        id = forms.Field(required=False)
        prom_state = forms.Field(required=False)
        alert_count = forms.Field(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["search_type", "search_data", "page", "per_page", "group_id", "order_by", "id", "prom_state", "alert_count"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username
        # 请求系统接口
        response = self.outgoing.http_client.post(
            host=configs.host,
            path='{}get-database-info-for-prom/'.format(base_api_url),
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
