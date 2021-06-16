from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json

import settings
from config import BK_URL, APP_CODE
from control.models import UserInfo
from control.utils.esb_api import EsbApi
from control.utils.status_code import error, ErrorStatusCode

ENV = {"dev": "", "prod": "o", "stag": "t"}


class CreateUserMiddleware(MiddlewareMixin):
    def process_view(self, request, view, arg, kwarg):
        # if not request.COOKIES:
        import platform
        # print("platform.system()", platform.system())
        if (not request.COOKIES.get("bk_token")) and (platform.system() == "Windows"):
            print("------------")
            request.COOKIES.update(**{"bk_token": "2uS4eEqUwwLx6BlN60u7413UKoodchijl7SlTLgeXaM"})

        if getattr(view, 'login_exempt_v2', False):
            return None
        username = None
        # handler = ResponseHandler(ConfFixture, settings)
        if request.method == "GET":     # ESB
            operator = request.GET.get("operator")
            if operator:
                username = operator
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                operator = data.get("operator")
                if operator:
                    username = operator
            except:
                # 上传文件
                pass

        if not username:
            token = request.COOKIES.get("bk_token")
            bk_user = EsbApi(token).get_user_info_from_workbench()
            if not bk_user:
                login_out_url = "https%3A//" + BK_URL.split("https://")[-1] + "/" + ENV.get(getattr(settings, "run_env", "dev")) +"/{}/&is_from_logout=1".format(APP_CODE)
                return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN, login_out_url))
            bk_user.pop("id", None)
            # print("bk_user_control", bk_user)
            username = bk_user.get("username")
            user = UserInfo.fetch_one(username=username)
            if not user:
                # user = UserInfo.create(**bk_user)
                UserInfo.create(**bk_user)
            else:
                user.update(**bk_user)
                # user = user.update(**bk_user)
            request.COOKIES["user_id"] = user.id
        else:
            user = UserInfo.fetch_one(username=username)
            token = request.COOKIES.get("bk_token")
            if not user and token:
                bk_user = EsbApi(token).get_user_info_from_workbench()
                bk_user.pop("id", None)
                username = bk_user.get("username")
                user = UserInfo.fetch_one(username=username)
                if not user:
                    # user = UserInfo.create(**bk_user)
                    UserInfo.create(**bk_user)
                else:
                    # user = user.update(**bk_user)
                    user.update(**bk_user)
                request.COOKIES["user_id"] = user.id
            elif user:
                pass
                request.COOKIES["user_id"] = user.id
            else:
                login_out_url = "https%3A//" + BK_URL.split("https://")[-1] + "/" + ENV.get(getattr(settings, "run_env", "dev")) +"/{}/&is_from_logout=1".format(APP_CODE)
                return JsonResponse(error(ErrorStatusCode.NOT_HAVE_USER_IFNO, login_out_url))
        return None
