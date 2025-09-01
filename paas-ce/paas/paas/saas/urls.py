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
from saas import views

urlpatterns = [

    # 应用列表
    path('list/', include([
        path('', views.SaaSListPageView.as_view(), name="saas_list"),
        path('query/', views.SaaSListView.as_view()),
    ])),

    # 应用基本信息
    re_path(r'^(?P<app_code>' + SAAS_CODE_REGEX + ')/', include([
        path('info/', views.InfoView.as_view()),
        # FIXME: change to restful-like api if more action on saas
        # 删除SaaS应用
        path('delete/', views.DeleteSaaSView.as_view()),

        path('logo/', views.ModifyAppLogoView.as_view()),

        # 上传SaaS应用
        path('upload/', views.UploadView.as_view()),

        # 发布相关
        # 发布部署页面
        path('release/', include([
            path('', views.ReleasePageView.as_view()),

            # 发布记录页面
            path('record/', views.RecordView.as_view()),

            # 下架页面
            path('offline/', views.OfflinePageView.as_view()),

            # 执行发布
            path('online/<int:saas_app_version_id>/', views.OnlineView.as_view()),
        ])),

    ])),

    path('0/release/', views.ReleasePageView.as_view(), {'app_code': 0}),

    # for legency system,  keep below
    # saas/release/online,
    # saas/upload,
    path('release/online/<int:saas_app_version_id>/', views.OnlineView.as_view()),
    re_path(r'^upload/(?P<app_code>' + SAAS_CODE_REGEX + ')/$', views.UploadView.as_view()),
    path('register-online-saas-app/', views.UploadAndRegisterView.as_view()),
]
