# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import auth
try:
    from django.utils.deprecation import MiddlewareMixin
except Exception:
    MiddlewareMixin = object
from config import BK_URL, APP_CODE
import settings as env_config
from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.components.bk_token.forms import AuthenticationForm
from control.utils.status_code import ErrorStatusCode, error
from django.http import JsonResponse
ENV = {"dev": "", "prod": "o", "stag": "t"}
logger = logging.getLogger('component')


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        Login paas by two ways
        1. views decorated with 'login_exempt' keyword
        2. User has logged in calling auth.login
        """
        # request.COOKIES["bk_token"] = "yZvemD7spIMZBnlq8tAfC0VzG1-_p5UbJ4_gY2yrEUI"
        if hasattr(request, 'is_wechat') and request.is_wechat():
            return None

        if hasattr(request, 'is_bk_jwt') and request.is_bk_jwt():
            return None

        if getattr(view, 'login_exempt', False):
            return None
        login_out_url = "https%3A//" + BK_URL.split("https://")[-1] + "/" + ENV.get(getattr(env_config, "run_env", "dev")) +"/{}/&is_from_logout=1".format(APP_CODE)
        form = AuthenticationForm(request.COOKIES)
        # if form.is_valid():
        #     bk_token = form.cleaned_data['bk_token']
        #     user = auth.authenticate(request=request, bk_token=bk_token)
        #     if user:
        #         # Succeed to login, recall self to exit process
        #         if user.username != request.user.username:
        #             auth.login(request, user)
        #         return None

        # print("request.path_info_1", request.path_info)
        if form.is_valid():
            bk_token = form.cleaned_data['bk_token']
            user = auth.authenticate(request=request, bk_token=bk_token)

            if not user:
                operator_admin = request.GET.get("operator")
                if operator_admin:
                    return None
                return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN, login_out_url))
            # UFO
            # if user:
            # print("user_info", user.username, user.is_superuser, user.is_active, request.user.username)
            # if user.is_superuser or request.path_info.find("/auth/") >= 0:
            if user.username and user.is_active:
                # Succeed to login, recall self to exit process
                # if user.username != request.user.username:
                #     auth.login(request, user)
                return None
            return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN, login_out_url))

        print("request.path_info_2", request.path_info)
        if request.path_info == "/":
            handler = ResponseHandler(ConfFixture, settings)
            return handler.build_401_response(request)
        else:
            return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN, login_out_url))

    def process_response(self, request, response):
        return response
