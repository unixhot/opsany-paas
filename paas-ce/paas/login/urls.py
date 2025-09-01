# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

paas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
""" # noqa



from bkaccount import views, views_api_v2

from django.urls import include, path, re_path
from django.http import HttpResponse
from django.views.i18n import JavaScriptCatalog
from django.views import i18n as django_i18n_views
from rest_framework_simplejwt.views import (
            TokenObtainPairView,
                TokenRefreshView,
                )


base_urlpatterns = [
    # 登录页面
    path('', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    # 用户管理
    path('accounts/', include("bkaccount.urls")),

    # 登陆模块 API，V2
    path('api/v2/is_login/', views_api_v2.CheckLoginView.as_view()),
    path('api/v2/get_user/', views_api_v2.UserView.as_view()),
    path('api/v2/get_batch_users/', views_api_v2.BatchUsersView.as_view()),
    re_path(r'^api/login-register/', views_api_v2.LoginRegisterView.as_view()),
    re_path(r'^api/login/', views_api_v2.LoginApiView.as_view()),
    path('api/v2/get_all_users/', views_api_v2.AllUsersView.as_view()),
]

urlpatterns = [
    path('', include(base_urlpatterns)),
    # 支持本地开发
    path('login/', include(base_urlpatterns)),
    # 检查统一登录是否正常运行
    path('healthz/', include("healthz.urls")),
    # 反搜索
    re_path(r'^robots\.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /', content_type='text/plain')),

    # 无登录态下切换语言
    path('i18n/setlang/', django_i18n_views.set_language, name='set_language'),
    # 处理JS翻译
    #re_path(r'^jsi18n/(?P<packages>\S+?)/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('jsi18n/i18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    
    # 增加JWT验证
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa
urlpatterns += staticfiles_urlpatterns()
