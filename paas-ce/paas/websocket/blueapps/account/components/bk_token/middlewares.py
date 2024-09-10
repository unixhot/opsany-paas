# -*- coding: utf-8 -*-
import datetime
import logging
import time

from django.http import HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
from django.contrib import auth
import json

from bastion.models import UserInfo

try:
    from django.utils.deprecation import MiddlewareMixin
except Exception:
    MiddlewareMixin = object
from config import BK_URL, APP_CODE, SECRET_KEY
import settings as env_config
from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.components.bk_token.forms import AuthenticationForm

logger = logging.getLogger('component')


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        request.COOKIES.update(**{"bk_token_username": None})
        request.COOKIES.update(**{"bk_esb_username": None})
        try:
            from django.conf import settings
            request.COOKIES.update(**{"bk_token": settings.BK_TOKEN})
        except Exception as e:
            pass

        if getattr(view, 'login_exempt', False):
            return None
        form = AuthenticationForm(request.COOKIES)
        if form.is_valid():
            bk_token = form.cleaned_data['bk_token']
            user = None
            if bk_token:
                user = auth.authenticate(request=request, bk_token=bk_token)
            if not user:
                if self._check_app_token(request):
                    return None

                return HttpResponseForbidden("Token无效！")
            if user.username and user.is_active:
                request.COOKIES.update(**{"bk_token_username": user.username})
                return None
            return HttpResponseForbidden("Token无效！")

        if self._check_app_token(request):
            return None
        
        if request.path_info == "/":
            handler = ResponseHandler(ConfFixture, env_config)
            return handler.build_401_response(request)
        else:
            return HttpResponseForbidden("Token无效！")

    def _check_app_token(self, request):
        headers = request.headers
        app_code = headers.get("X-APP-CODE")
        app_token = headers.get("X-APP-TOKEN")
        if APP_CODE == app_code and app_token == SECRET_KEY:
            try:
                data = json.loads(request.body)
            except:
                data = {}
            bk_esb_username = request.GET.get("operator") or request.POST.get("operator") or data.get(
                "operator")
            query = UserInfo.objects.filter(username=bk_esb_username).first()
            if query:
                if query.username and query.is_activate:
                    request.COOKIES.update(**{"bk_esb_username": bk_esb_username})
                    return True
        return False

    def process_response(self, request, response):
        # if self.bk_token:
        #     now_time = int(time.time())
        #     expire_time = now_time + 60 * 60 * 24
        #     response.set_cookie("bk_token", self.bk_token,
        #                         expires=datetime.datetime.fromtimestamp(expire_time, timezone.get_current_timezone()),
        #                         domain="192.168.0.19",
        #                         httponly=True)
        return response
