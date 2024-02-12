# -*- coding: utf-8 -*-
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs
from .toolkit.tools import base_api_url


class GetNexusRepositoryGuide(Component):
    """
    apiMethod GET

    ### 功能描述

    获取制品库使用指引

    ### 请求参数
    {{ common_args_desc }}

    #### 接口参数

    | 字段    | 类型     | 必选   | 描述       |
    | ----- | ------ | ---- | -------- |
    | code | int | 是 | 应用id |
    | repository_format | str | 是 | 制品库类型 |
    | repository_id | str | 是 | 制品库名称 |

    ```

    ### 返回结果示例

    ```python
    {
        "code": 200,
        "successcode": 20002,
        "message": "信息获取成功",
        "data": {
            "code": 2,
            "format": "raw",
            "content": "#### 推送\n\n##### 使用 curl 推送\n\n```\ncurl -T <FILE.EXT> -u [USERNAME] 
            \"http://127.0.0.1:8000/repository/test-test/<PACKAGE>?version=<VERSION>\"\n```
            \n\n- `<VERSION>` 为**非必填**项，默认为 **latest**。\n- 支持 直接上传 或拖拽到当前页面进行上传。
            \n\n##### 使用Generic 插件进行推送\n\n- 安装 Generic 插件（依赖 [Node.js](https://nodejs.org/)）
            \n\n  ```\n  npm install generic -g\n  ```\n\n- 推送到当前制品库\n\n  ```
            \n  generic -u=[USERNAME] --path=<FILE.EXT> --registry=
            \"http://http://127.0.0.1:8000/repository/test-test/chunks/<PACKAGE>?version=<VERSION>\"\n  ```
            \n\n#### 拉取\n\n```\ncurl --fail -L -u [USERNAME] 
            \"http://http://127.0.0.1:8000/repository/test-test/<PACKAGE>?version=<VERSION>\" -o <FILE.EXT>\n```
            \n\n- `<VERSION>` 为**非必填**项，默认为 **latest**。\n\n#### 删除\n\n```\ncurl -X DELETE -u [USERNAME] 
            \"http://http://127.0.0.1:8000/repository/test-test/<PACKAGE>?version=<VERSION>\"\n```
            \n\n- `<VERSION>` 为**非必填**项，默认为 **latest**。"
        }
    }
    ```
    """  #

    # 组件所属系统的系统名
    sys_name = configs.SYSTEM_NAME

    # Form处理参数校验
    class Form(BaseComponentForm):
        code = forms.IntegerField(required=True)
        repository_format = forms.CharField(required=True)
        repository_id = forms.CharField(required=True)

        # clean方法返回的数据可通过组件的form_data属性获取
        def clean(self):
            return self.get_cleaned_data_when_exist(keys=["code", "repository_format", "repository_id"])

    # 组件处理入口
    def handle(self):
        # 获取Form clean处理后的数据
        params = self.form_data

        # 设置当前操作者
        params['operator'] = self.current_user.username

        # 请求系统接口
        response = self.outgoing.http_client.get(
            host=configs.host,
            path='{}get-nexus-repository-guide/'.format(base_api_url),
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
