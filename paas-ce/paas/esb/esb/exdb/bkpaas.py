# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""
from sqlalchemy import text  # 必须导入text包装器
from sqlalchemy.exc import SQLAlchemyError
from .connections import get_connections

db = get_connections('default')


class AppSecureInfo(object):
    """
    Helper for AppSecureInfo
    """

    @classmethod
    def get_by_app_code(cls, app_code):
        secure_key_list = []

        # SQL必须使用text()包装，参数使用:命名占位符
        sql_queries = [
            text("SELECT code, auth_token FROM paas_app WHERE code = :app_code"),
            text("SELECT app_code, app_token FROM esb_app_account WHERE app_code = :app_code")
        ]

        try:
            with db.begin() as connection:  # 使用上下文管理器确保事务
                for sql in sql_queries:
                    # 使用字典参数传递，且参数名与占位符一致
                    result = connection.execute(sql, {"app_code": app_code})
                    obj = result.first()
                    if obj:
                        secure_key_list.append(obj[1])
        except SQLAlchemyError as e:
            # 添加错误日志
            print(f"Database query failed: {str(e)}")
        return {'app_code': app_code, 'secure_key_list': secure_key_list} if secure_key_list else None