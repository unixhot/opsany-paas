"""
Copyright © 2012-2020 OpsAny. All Rights Reserved. 河南我买云信息技术有限公司版权所有
""" # noqa
from django.shortcuts import render

from blueapps.account.decorators import login_exempt_v2
# Create your views here.

@login_exempt_v2
def vue(request):
    return render(request, 'index.html')
    # return render(request, 'index.html', {"SITE_URL": ""})


def swagger_editor(request):
    return render(request, 'swagger/index.html')