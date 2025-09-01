# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa



from django.urls import include, path, re_path

from common.constants import SAAS_CODE_REGEX
from release import views


# release/{app_code}/operation/
urlpatterns = [
    re_path(r'^(?P<app_code>' + SAAS_CODE_REGEX + ')/', include([
        # 发布部署页
        path('', views.HomeView.as_view()),

        # 提测
        path('test/', views.ReleaseTestView.as_view()),
        # 上线
        path('online/', views.ReleaseProductionView.as_view()),

        # 下架
        path('offline/', views.ReleaseOfflineView.as_view()),

        # 删除
        path('delete/', views.ApplicationDeleteView.as_view()),

        # 查询未完成任务的状态, 更新数据库
        path('task/unfinished/', views.UnfinishedTaskView.as_view()),

        # deploy page
        re_path(r'^deploy_page/(?P<page_type>\w+)/$', views.DeployPageView.as_view()),


        # 发布记录 页面及列表
        path('record/', views.RecordPageView.as_view()),
        re_path(r'^record/list/(?P<operate_code>\d)/$', views.AppRecordView.as_view()),

        path('record/last_release/', views.LastReleaseRecordView.as_view()),

        # 轮询查询状态
        path('task/', views.EventStatusView.as_view()),

        # 版本记录
        path('version/', views.ReleaseVersion.as_view()),
    ])),


    # for legency system
    # 轮询查询状态
    re_path(r'^get_app_poll_task/(?P<app_code>' + SAAS_CODE_REGEX + ')/$', views.EventStatusView.as_view()),
]
