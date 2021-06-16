# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('blueapps.account.urls')),
    url(r'^api/control/v0_1/', include('control.urls')),
    url(r'^api/terminal/v0_1/', include('terminal.urls')),
    url('', include('index.urls')),
]
