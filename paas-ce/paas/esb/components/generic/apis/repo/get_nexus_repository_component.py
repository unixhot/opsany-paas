
# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetNexusRepositoryComponent(Component):
    """
    apiMethod GET

    ### 功能描述

    获取制品库的组件

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | continuationToken | str | 否 | 分页获取组件列表 |
    | repository_id | str | 是 | 制品库id |
    | id | int | 否 |  |
    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20002,
        "message": "信息获取成功",
        "data": {
            "items": [
                {
                    "id": "dGVzdC10ZXN0OjI5NWQzNTRiNzEzYTA5MjQ3YWRjYTE1YjEzMDZkOTlm",
                    "repository": "test-test",
                    "format": "raw",
                    "group": "/",
                    "name": "2.txt",
                    "version": null,
                    "assets": [
                        {
                            "downloadUrl": "http://127.0.0.1:8000/repository/test-test/2.txt",
                            "path": "2.txt",
                            "id": "dGVzdC10ZXN0OjBiNjUzMmFhNjRjNzZiOGMyMWM4ZTZkMjM2NmQwYWY0",
                            "repository": "test-test",
                            "format": "raw",
                            "checksum": {
                                "sha1": "e3e862c2009d70cc6d5c76504d39dd29362eb18b",
                                "sha512": "da15460d61635710e15e1a2b29d435ff07617073a59531d3ba1ea53ddf911f01e7107d9",
                                "sha256": "e98f147de4ee22b924dda0a14300de565305bb4f33f8675edaf83a1297e145e9",
                                "md5": "e2430a18f44397a85598674d6469c1ca"
                            },
                            "contentType": "text/plain",
                            "lastModified": "2024-01-09T03:11:55.842+00:00",
                            "blobCreated": "2024-01-09T03:11:55.842+00:00",
                            "lastDownloaded": "2024-01-09T08:58:13.281+00:00"
                        }
                    ]
                },
                ......
    }
    ```
    """  #

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        continuationToken = forms.CharField(required=False)
        repository_id = forms.CharField(required=True)
        id = forms.IntegerField(required=False)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["continuationToken", "repository_id", "id"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-nexus-repository-component/'.format(base_api_url),
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
