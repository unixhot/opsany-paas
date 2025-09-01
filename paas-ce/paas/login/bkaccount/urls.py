# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa


from django.urls import include, path

from bkaccount import views, views_api


urlpatterns = [
    # 用户信息相关
    path('user/', include([
        # 用户管理
        path('list/', include([
            path('', views.UserPageView.as_view()),
            path('query/', views.UserListPage.as_view()),
        ])),
        # [post] user create
        path('', views.UserView.as_view()),
        # [put/delete] userinfo modify / user delete
        path('<int:user_id>/', views.UserView.as_view()),
        # [put] user password
        path('<int:user_id>/password/', views.UserPasswordView.as_view()),
        # export/import users
        path('export/', views.UserExportView.as_view()),
        path('import/', views.UserImportView.as_view()),

        # API for user center in paas with bktoken cookies
        # [put] user password reset
        path('password/', views_api.CurrentUserPasswordView.as_view()),
        # [post] user info modify
        path('baseinfo/', views_api.CurrentUserBaseInfoView.as_view()),
        # [post/delete] weixin user_id bind/unbind
        path('weixin_info/', views_api.CurrentUserWeixinInfoView.as_view()),
    ])),

    # API 接口
    path('is_login/', views_api.CheckLoginView.as_view()),
    path('get_vx_work_config/', views_api.GetVxWorkConfigView.as_view()),
    path('get_auth_config/', views_api.GetAuthConfigView.as_view()),
    path('get_user/', views_api.UserView.as_view()),
    path('get_all_user/', views_api.AllUsersView.as_view()),
    path('get_batch_user/', views_api.BatchUsersView.as_view()),

    # for legency system,  keep below
    # user/list
    path('', views.UserPageView.as_view()),
]
