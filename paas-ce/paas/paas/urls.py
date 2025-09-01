# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""  # noqa
"""paas URL Configuration

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
"""

from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

from account.decorators import login_exempt


wx_verify_code = "glbPQflGmIr9nFCj"
wx_verify_code_url = "WW_verify_glbPQflGmIr9nFCj.txt"

@login_exempt
def wx_verify(request):
    return HttpResponse(content=wx_verify_code)


urlpatterns = [
    # 首页, 重定向到首页, pattern => /platform/  permanent => 301
    path(wx_verify_code_url, wx_verify),
    path('', RedirectView.as_view(pattern_name="platform", permanent=True)),
    path(wx_verify_code_url, wx_verify),
    # url(r'^$', RedirectView.as_view(url='/o/workbench/', permanent=True)),

    # 首页
    path('platform/', include("home.urls")),

    # 用户账号相关
    path('accounts/', include("account.urls")),

    # 服务器信息
    path('engine/', include("engine.urls")),

    # 应用相关
    path('app/', include("app.urls")),

    # SaaS 服务相关
    path('saas/', include("saas.urls")),

    # 发布相关
    path('release/', include("release.urls")),

    # 资源下载
    path('resource/', include("resource.urls")),
    # 指南
    path('guide/', include("guide.urls")),

    # API 相关
    path('paas/api/', include("api.urls")),
    # ESB
    path('esb/', include("esb.configs.urls")),
    # 服务检测
    path('healthz/', include("healthz.urls")),

    # 个人中心 - 微信相关
    path('console/user_center/', include("user_center.urls")),

    # admin
    path('admin/', admin.site.urls),

    # 反搜索
    re_path(r'^robots\.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /', content_type='text/plain')),

    # i18n
    #re_path(r'^jsi18n/(?P<packages>\S+?)/$', JavaScriptCatalog.as_view, name='javascript-catalog'),
    path('jsi18n/i18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

# for upload/download
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from account.decorators import login_exempt  # noqa
import django.views  # noqa

static_serve = login_exempt(django.views.static.serve)
urlpatterns.append(re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}))

# for static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa

urlpatterns += staticfiles_urlpatterns()

