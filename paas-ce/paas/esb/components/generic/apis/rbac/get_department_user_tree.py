# -*- coding: utf-8 -*-
"""
"""
import json

from django import forms

from common.forms import BaseComponentForm
from components.component import Component
from .toolkit import configs


class GetDepartmentUserTree(Component):
    """
    apiMethod GET

    ### 功能描述

    获取部门人员树

    ### 请求参数

    #### 接口参数

    ### 请求参数示例

    ### 返回结果示例

    ```python
    {
        "status_code": 0,
        "status_info": "错误信息",
        "data": {
            "dep_name":"xxx",
            "id":1, 
            "user_list":[
                {
                    "username":"user1",
                    "chname":"user1",
                    "phone":"11111111111",
                    "email":"user1@opsany.com",
                    "description":"user1",
                    "bk_role":0
                },
            ],
            children:[
                {
                    "dep_name":"xxx",
                    "id": 2, 
                    "user_list":[
                        {
                            "username":"user2",
                            "chname":"user2",
                            "phone":"11111111112",
                            "email":"user2@opsany.com",
                            "description":"user2",
                            "bk_role":0
                        },
                    ],
                    children:[ ]
                }
            ]
        }
    }
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
                path=configs.base_api_url + 'auth/department_user_tree/',
                params=params,
                data=None,
                cookies=self.request.wsgi_request.COOKIES,	            
            )
        except:
            pass

        # 对结果进行解析
        code = response['status_code']
        if code == 0:
            result = {
                'status_code': 0,
                'data': response['data'],
            }
        else:
            result = {
                'status_code': 1,
                'status_info': response['status_info']
            }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result
