# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa



from django.contrib import admin

from release.models import (Record, Version, UserOperateRecord)


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('app_code', 'operate_id', 'operate_user', 'operate_time', 'is_success')
    search_fields = ('app_code', 'operate_user')
    list_filter = ('operate_id', 'operate_user', 'operate_time', 'app_code')




@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('app', 'version', 'publisher', 'pubdate')
    search_fields = ('app__code', 'publisher')
    list_filter = ('app', 'publisher', 'pubdate')




@admin.register(UserOperateRecord)
class UserOperateRecordAdmin(admin.ModelAdmin):
    list_display = ('app_code', 'username', 'operate_type', 'operate_time')
    search_fields = ('username', 'app_code')
    list_filter = ('username', 'operate_type', 'operate_time', 'app_code')


