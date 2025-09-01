# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

def patch_mysql(pool_options={}):
    from django.db.backends.mysql import base as mysql_base

    POOL_SETTINGS = pool_options

    if not hasattr(mysql_base, "_Database"):
        mysql_base._Database = mysql_base.Database
        
        def create_pool():
            return QueuePool(creator=mysql_base._Database.connect,
                             **POOL_SETTINGS)
        
        engine = create_engine('mysql://', poolclass=create_pool)
        mysql_base.Database = ManagerProxy(engine.pool)

class ManagerProxy(object):
    def __init__(self, pool):
        self.pool = pool

    def __getattr__(self, key):
        return getattr(self.pool, key)

    def connect(self, *args, **kwargs):
        return self.pool.connect(*args, **kwargs)

    def dispose(self):
        self.pool.dispose()
