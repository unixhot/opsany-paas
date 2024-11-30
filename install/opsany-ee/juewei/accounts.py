# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import unicode_literals
import datetime
import time
import unicodedata
import urllib
import uuid
import json

from django.conf import settings
from django.utils.translation import ugettext as _
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (login as auth_login,
                                 logout as auth_logout)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import resolve_url, render
from django.template.response import TemplateResponse
from django.utils.six.moves.urllib.parse import urlparse
from django.utils import timezone

from common.log import logger
from bkaccount.encryption import encrypt, decrypt, salt
from bkaccount.models import Loignlog, BkToken
from bkaccount.forms import AuthenticationAndRegisterForm
from bkaccount.opsany_user_auth import OpsAnyRbacUserAuth
from bkaccount.models import BkUser

class AccountSingleton(object):
    """
    单例基类
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class Account(AccountSingleton):
    """
    账号体系相关的基类Account

    提供通用的账号功能
    """
    # cookie名称
    BK_COOKIE_NAME = settings.BK_COOKIE_NAME
    # cookie 有效期，默认为1天
    BK_COOKIE_AGE = settings.BK_COOKIE_AGE
    # 登录回调链接
    REDIRECT_FIELD_NAME = 'c_url'
    # 登录连接
    BK_LOGIN_URL = str(settings.LOGIN_URL)
    # 允许误差时间，防止多台机器时间误差， 1分钟
    BK_TOKEN_OFFSET_ERROR_TIME = settings.BK_TOKEN_OFFSET_ERROR_TIME

    def is_safe_url(self, url, host=None):
        """
        判断url是否与当前host的根域一致

        以下情况返回False：
            1)根域不一致
            2)url的scheme不为：https(s)
            3)url为空
        """
        if url is not None:
            url = url.strip()
        if not url:
            return False
        # Chrome treats \ completely as /
        url = url.replace('\\', '/')
        # Chrome considers any URL with more than two slashes to be absolute, but
        # urlparse is not so flexible. Treat any url with three slashes as unsafe.
        if url.startswith('///'):
            return False
        url_info = urlparse(url)
        # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
        # In that URL, example.com is not the hostname but, a path component. However,
        # Chrome will still consider example.com to be the hostname, so we must not
        # allow this syntax.
        if not url_info.netloc and url_info.scheme:
            return False
        # Forbid URLs that start with control characters. Some browsers (like
        # Chrome) ignore quite a few control characters at the start of a
        # URL and might consider the URL as scheme relative.
        if unicodedata.category(url[0])[0] == 'C':
            return False
        url_domain = url_info.netloc.split(':')[0].split('.')[-2] if url_info.netloc else ''
        host_domain = host.split(':')[0].split('.')[-2] if host else ''
        return ((not url_info.netloc or url_domain == host_domain) and
                (not url_info.scheme or url_info.scheme in ['http', 'https']))

    def get_bk_token(self, username):
        """
        生成用户的登录态
        """
        bk_token = ''
        expire_time = int(time.time())
        # 重试5次
        retry_count = 0
        while not bk_token and retry_count < 5:
            now_time = int(time.time())
            expire_time = now_time + self.BK_COOKIE_AGE
            plain_token = '%s|%s|%s' % (expire_time, username, salt())
            bk_token = encrypt(plain_token)
            try:
                BkToken.objects.create(token=bk_token)
            except Exception as error:
                logger.exception('Login ticket failed to be saved during ticket generation, error: {}'.format(error))
                # 循环结束前将bk_token置空后重新生成
                bk_token = '' if retry_count < 4 else bk_token
            retry_count += 1
        return bk_token, datetime.datetime.fromtimestamp(expire_time, timezone.get_current_timezone())

    def _decrypt_token(self, bk_token):
        try:
            if bk_token == "None":
                plain_bk_token = ''
            else:
                plain_bk_token = decrypt(bk_token)
        except Exception as error:
            plain_bk_token = ''
            logger.exception("Parameter parse failed, error: {}".format(error))

        # 参数bk_token非法
        error_msg = _("参数bk_token非法")
        if not plain_bk_token:
            return False, error_msg, None

        try:
            token_info = plain_bk_token.split('|')
        except Exception as error:
            token_info = []
            logger.exception("token info wrong, error: {}".format(error))

        return True, None, token_info

    def _is_bk_token_valid(self, bk_token):
        """
        验证用户登录态
        """
        if not bk_token:
            error_msg = _("缺少参数bk_token")
            return False, None, error_msg

        ok, error_msg, token_info = self._decrypt_token(bk_token)
        if not ok:
            return False, None, error_msg

        if not token_info or len(token_info) < 3:
            return False, None, error_msg

        try:
            is_logout = BkToken.objects.get(token=bk_token).is_logout
        except BkToken.DoesNotExist:
            error_msg = _("不存在该bk_token的记录")
            return False, None, error_msg

        expire_time = int(token_info[0])
        now_time = int(time.time())
        # token已注销
        if is_logout:
            error_msg = _("登录态已注销")
            return False, None, error_msg
        # token有效期已过
        if now_time > expire_time + self.BK_TOKEN_OFFSET_ERROR_TIME:
            error_msg = _("登录态已过期")
            return False, None, error_msg
        # token有效期大于当前时间的有效期
        if expire_time - now_time > self.BK_COOKIE_AGE + self.BK_TOKEN_OFFSET_ERROR_TIME:
            error_msg = _("登录态有效期不合法")
            return False, None, error_msg

        username = token_info[1]
        return True, username, ""

    def is_bk_token_valid(self, request):
        bk_token = request.COOKIES.get(self.BK_COOKIE_NAME)
        return self._is_bk_token_valid(bk_token)

    def set_bk_token_invalid(self, request, response=None):
        """
        将登录票据设置为不合法
        """
        bk_token = request.COOKIES.get(self.BK_COOKIE_NAME)
        if bk_token:
            BkToken.objects.filter(token=bk_token).update(is_logout=True)
        if response is not None:
            # delete cookie
            response.delete_cookie(self.BK_COOKIE_NAME, domain=settings.BK_COOKIE_DOMAIN)
            return response
        return None

    def record_login_log(self, request, user, app_id, token=None):
        """
        记录用户登录日志
        """
        host = request.get_host()
        login_browser = request.META.get('HTTP_USER_AGENT') or 'unknown'
        # 获取用户ip
        login_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        try:
            if login_ip and "," in login_ip:
                login_ip = login_ip.split(",")[0].split()
        except Exception:
            pass
            # logger.info("IP地址[ID:%s]解析失败", login_ip)
        Loignlog.objects.record_login(user, login_browser, login_ip, host, app_id)
        auth_object = OpsAnyRbacUserAuth(user.username, "")
        try:
            auth_object.update_login_log(token, login_ip, login_browser, host)
        except Exception as e:
            print "Login log error: {}".format(str(e))
    
    def redirect_login(self, request):
        """
        重定向到登录页面.

        登录态验证不通过时调用
        """
        if request.is_ajax():
            return HttpResponse(status=401)

        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(self.BK_LOGIN_URL)
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
            path = settings.SITE_URL[:-1] + request.get_full_path()
        return redirect_to_login(
            path, resolved_login_url, self.REDIRECT_FIELD_NAME)

    def login(self, request, template_name='login/login.html',
              authentication_form=AuthenticationForm,
              #authentication_form=AuthenticationAndRegisterForm,
              current_app=None, extra_context=None):
        """
        登录页面和登录动作
        """
        redirect_field_name = self.REDIRECT_FIELD_NAME
        redirect_to = request.POST.get(redirect_field_name,
                                       request.GET.get(redirect_field_name, ''))
        app_id = request.POST.get('app_id', request.GET.get('app_id', ''))
        c_url = request.POST.get('c_url', request.GET.get('c_url', '/'))
        tab_key = request.POST.get('tab_key', request.GET.get('tab_key', 1))
        # print("tab_key", tab_key)
        error_message = ""
        if request.method == 'POST':
            # 改写request中密码内容
            request.POST = request.POST.copy()
            request.POST["password"] = request.POST["password"].strip()
            data = request.POST.dict()
            next = data.get("next", "")
            username = data.get("username", "")
            password = data.get("password", "")
            google_auth_url = data.pop("google_auth_url", {})
            google_auth_type = data.pop("google_auth_type", None)
            secret = data.pop("secret", "")
            geetest_challenge = data.pop("geetest_challenge", None)
            geetest_seccode = data.pop("geetest_seccode", None)
            geetest_validate = data.pop("geetest_validate", None)
            mfa = data.pop("mfa", None)
            verify_code = data.pop("verify_code", None)
            seven_days_free = data.pop("seven_days_free", 0)
            domain = data.pop("domain", None)
            form = authentication_form(request, data=request.POST)
            if domain:
                username = username + "@" + domain

            return_data = {"app_id": app_id, "next": next, "IMG_URL": settings.IMG_URL, "SITE_URL": settings.SITE_URL, "tab_key": tab_key}
            if data.has_key("next") and data.has_key("app_id"):
                if not geetest_challenge or not geetest_seccode or not geetest_validate:
                    return_data.update(**{"data": "1"})
                    return render(request, "login/login.html", return_data)
            auth_object = OpsAnyRbacUserAuth(username, password)
            google_auth_status = auth_object.get_user_google_auth_status()
            #print("google_auth_status", google_auth_status, username)

            if google_auth_status in ["8", "9"]:
                return_data.update(**{"data": "2"})
                return render(request, "login/login.html", return_data)

            if "@" not in username:
                if form.is_valid():
                    # if google_auth_status == "1":
                    if google_auth_status in ["1", "3", "4", "5", "7"]:
                        if google_auth_status in ["3"]:
                            if google_auth_url:
                                return_data["google_auth_url"] = google_auth_url
                                return_data["secret"] = secret
                            else:
                                google_auth_pic = auth_object.get_google_auth()
                                return_data["google_auth_url"] = google_auth_pic.get("url", "")
                                return_data["secret"] = google_auth_pic.get("secret", "")
                        if google_auth_type == "bind_google_auth":
                            bind_google_auth = auth_object.bind_google_auth(secret=secret, verify_code=verify_code)
                            return_data["bind_google_auth"] = bind_google_auth.get("data", {})
                            if bind_google_auth.get("result"):
                                return self.login_success_response(request, form, redirect_to, app_id)
                            else:
                                return_data["username"] = username
                                return_data["password"] = password
                                return_data["mfa"] = "start"
                                return_data["domain"] = domain
                                return_data["c_url"] = c_url
                                return_data["verfiy_code"] = verify_code
                                return_data["seven_days_free"] = seven_days_free
                                return_data["google_auth_status"] = google_auth_status
                                return_data["geetest_challenge"] = geetest_challenge
                                return_data["geetest_seccode"] = geetest_seccode
                                return_data["geetest_validate"] = geetest_validate
                                return render(request, "login/login.html", return_data)
                        mfa = "start" if not mfa else mfa
                    if mfa == "start":
                        check_status = auth_object.check_google_verify_code(verify_code, seven_days_free)
                        if check_status:
                            return self.login_success_response(request, form, redirect_to, app_id)
                        else:
                            return_data["username"] = username
                            return_data["password"] = password
                            return_data["mfa"] = "start"
                            return_data["domain"] = domain
                            return_data["c_url"] = c_url
                            return_data["verfiy_code"] = ""
                            return_data["seven_days_free"] = seven_days_free
                            return_data["google_auth_status"] = google_auth_status
                            return_data["geetest_challenge"] = geetest_challenge
                            return_data["geetest_seccode"] = geetest_seccode
                            return_data["geetest_validate"] = geetest_validate
                            if verify_code:
                                return_data["check_status"] = False
                            else:
                                return_data["check_status"] = None
                            return render(request, "login/login.html", return_data)
                    else:
                        return self.login_success_response(request, form, redirect_to, app_id)
            else:
                res, data = auth_object.check_users()
                user = self.get_user(data, username)
                #print("get_user", res, data, user)

                if res:
                    # if google_auth_status == "1":
                    if google_auth_status in ["1", "3", "4", "5", "7"]:
                        if google_auth_status in ["3"]:
                            if google_auth_url:
                                return_data["google_auth_url"] = google_auth_url
                                return_data["secret"] = secret
                            else:
                                google_auth_pic = auth_object.get_google_auth()
                                return_data["google_auth_url"] = google_auth_pic.get("url", "")
                                return_data["secret"] = google_auth_pic.get("secret", "")
                            
                        if google_auth_type == "bind_google_auth":
                            bind_google_auth = auth_object.bind_google_auth(secret=secret, verify_code=verify_code)
                            return_data["bind_google_auth"] = bind_google_auth.get("data", {})
                            if bind_google_auth.get("result"):
                                return self.login_success_response(request, user, redirect_to, app_id)
                            else:
                                return_data["username"] = username
                                return_data["password"] = password
                                return_data["mfa"] = "start"
                                return_data["domain"] = domain
                                return_data["c_url"] = c_url
                                return_data["verfiy_code"] = verify_code
                                return_data["seven_days_free"] = seven_days_free
                                return_data["google_auth_status"] = google_auth_status
                                return_data["geetest_challenge"] = geetest_challenge
                                return_data["geetest_seccode"] = geetest_seccode
                                return_data["geetest_validate"] = geetest_validate
                                return render(request, "login/login.html", return_data)
                        mfa = "start" if not mfa else mfa
                    if mfa == "start":
                        check_status = auth_object.check_google_verify_code(verify_code, seven_days_free)
                        if check_status:
                            return self.login_success_response(request, user, redirect_to, app_id)
                        else:
                            return_data["username"] = username
                            return_data["password"] = password
                            return_data["mfa"] = "start"
                            return_data["domain"] = domain
                            return_data["c_url"] = c_url
                            return_data["verfiy_code"] = ""
                            return_data["seven_days_free"] = seven_days_free
                            return_data["google_auth_status"] = google_auth_status
                            return_data["geetest_challenge"] = geetest_challenge
                            return_data["geetest_seccode"] = geetest_seccode
                            return_data["geetest_validate"] = geetest_validate
                            if verify_code:
                                return_data["check_status"] = False
                            else:
                                return_data["check_status"] = None
                            return render(request, "login/login.html", return_data)
                    else:
                        return self.login_success_response(request, user, redirect_to, app_id)
        #elif request.method == 'GET' and request.GET.get("code") and request.GET.get("auth_type"):
        elif (request.method == 'GET' and request.GET.get("code") and (request.GET.get("auth_type") or request.GET.get("domain") or (request.GET.get("appid")))) or \
                (request.method == 'GET' and request.GET.get("domain") and request.GET.get("auth_type") and request.GET.get("sso_code") and request.GET.get("sso_sign")):

            appid = request.GET.get("appid")
            code = request.GET.get("code")
            domain = request.GET.get("domain")
            ad_domain = request.GET.get("ad_domain")
            auth_type = request.GET.get("auth_type")
            sso_code = request.GET.get("sso_code")
            sso_sign = request.GET.get("sso_sign")
            return_data = {"tab_key": tab_key, "app_id": "", "next": "", "IMG_URL": settings.IMG_URL, "SITE_URL": settings.SITE_URL}
            #if auth_type in ["3", "6"]:
            #    if auth_type == "6":
            #        auth_obj = OpsAnyRbacUserAuth(code=code, domain=domain)
            #    else:
            #        auth_obj = OpsAnyRbacUserAuth(code=code, app_id=appid)
            auth_obj = None
            if sso_code and sso_sign and auth_type in ["8"]:
                auth_obj = OpsAnyRbacUserAuth(domain=domain, auth_type=auth_type, sso_code=sso_code, sso_sign=sso_sign)
            elif code and domain:
                auth_obj = OpsAnyRbacUserAuth(code=code, domain=domain, ad_domain=ad_domain)
            elif auth_type in ["3", "6"]:
                auth_obj = OpsAnyRbacUserAuth(code=code, app_id=appid, ad_domain=ad_domain)
            if auth_obj:
                status, res = auth_obj.check_users()
                if status and res.get("auth_status") and res.get("domain_status") and res.get("have_user"):
                    user_info = res.get("user_info")
                    user = self.get_user(res, user_info.get("username"))
                    redirect_to = "/"
                    return self.login_success_response(request, user, redirect_to, app_id)
                else:
                    return_data["message"] = res.get("message")
                    form = authentication_form(request)
                    error_message = res.get("message")
            else:
                return_data["message"] = "Unsupported auth type."
                form = authentication_form(request)
                error_message = "Unsupported auth type."
        else:
            form = authentication_form(request)
        current_site = get_current_site(request)
        context = {
            'form': form,
            redirect_field_name: redirect_to,
            'site': current_site,
            'site_name': current_site.name,
            'tab_key': tab_key,
            'error_message': error_message,
            'app_id': app_id
        }
        if extra_context is not None:
            context.update(extra_context)
        if current_app is not None:
            request.current_app = current_app

        response = TemplateResponse(request, template_name, context)
        response = self.set_bk_token_invalid(request, response)
        return response

    def get_user(self, data, username):
        """
        {
            'have_user': False,
            'auth_status': False,
            'domain_status': False,
            'user_info': {}
        }
        """
        have_user = data.get("have_user")
        user_info = data.get("user_info")
        if have_user:
            username = user_info.get("username")
            password = str(uuid.uuid4()).split("-")[-1]
            status, user_dict, msg = BkUser.objects.get_user_info_v2(username)
            if status:
                user_id = user_dict.get("id")
            else:
                user_id = None
            result, user_id, message = BkUser.objects.modify_or_create_user_by_userid(
                user_id,
                user_info.get("username"),
                user_info.get("chname", ""),
                user_info.get("phone", ""),
                "" if user_info.get("email", "") is None else user_info.get("email", ""),
                user_info.get("bk_role", "0"),
                password
            )
            return BkUser.objects.filter(id=user_id).first()
        else:
            user = BkUser.objects.filter(username=username).first()
            if user:
                user.delete()
            return None

    def logout(self, request, next_page=None):
        """
        登出并重定向到登录页面
        """
        redirect_field_name = self.REDIRECT_FIELD_NAME
        auth_logout(request)

        if (redirect_field_name in request.POST or redirect_field_name in request.GET):
            next_page = request.POST.get(redirect_field_name,
                                         request.GET.get(redirect_field_name))
            # Security check -- don't allow redirection to a different host.
            if not self.is_safe_url(url=next_page, host=request.get_host()):
                next_page = request.path

        if next_page:
            # Redirect to this page until the session has been cleared.
            response = HttpResponseRedirect(next_page)
        else:
            # Redirect to login url.
            response = HttpResponseRedirect("{}?{}".format(self.BK_LOGIN_URL, "is_from_logout=1"))

        # 将登录票据设置为不合法
        response = self.set_bk_token_invalid(request, response)
        return response

    def login_failed_response(self, request, redirect_to, app_id):
        """
        登录失败跳转，目前重定向到登录，后续可返还支持自定义的错误页面
        """
        redirect_url = self.BK_LOGIN_URL
        query = {}
        if redirect_to:
            query[self.REDIRECT_FIELD_NAME] = redirect_to
        if app_id:
            query['app_id'] = app_id
        if len(query):
            redirect_url = "{}?{}".format(self.BK_LOGIN_URL, urllib.urlencode(query))
        response = HttpResponseRedirect(redirect_url)
        response = self.set_bk_token_invalid(request, response)
        return response

    def login_success_response(self, request, user_or_form, redirect_to, app_id):
        """
        用户验证成功后，登录处理
        """
        # 判读是form还是user
        if isinstance(user_or_form, AuthenticationForm):
            user = user_or_form.get_user()
            username = user_or_form.cleaned_data.get('username', '')
        else:
            user = user_or_form
            username = user.username

        # 检查回调URL是否安全，防钓鱼
        if not self.is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url('{}accounts/user/list/'.format(settings.SITE_URL))
        # 设置用户登录
        try:
            auth_login(request, user)
        except:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth_login(request, user)
        # 记录登录日志
        bk_token, expire_time = self.get_bk_token(username)
        response = HttpResponseRedirect(redirect_to)
        response.set_cookie(self.BK_COOKIE_NAME, bk_token,
                            expires=expire_time,
                            domain=settings.BK_COOKIE_DOMAIN,
                            httponly=True)
        self.record_login_log(request, user, app_id, bk_token)
        # NOTE: DO NOT SET THE LANGUAGE COOKIE HERE BEFORE I18N is AVAILABLE
        # set cookie for app or platform
        # bk_user_info, is_created = UserInfo.objects.get_or_create(user=user)
        # response.set_cookie(settings.LANGUAGE_COOKIE_NAME, bk_user_info.language,
        #                     # max_age=settings.LANGUAGE_COOKIE_AGE,
        #                     expires=expire_time,
        #                     path=settings.LANGUAGE_COOKIE_PATH,
        #                     domain=settings.LANGUAGE_COOKIE_DOMAIN)
        return response

    def login_redirect_response(self, request, redirect_url, is_from_logout):
        """
        登录重定向
        """
        response = HttpResponseRedirect(redirect_url)
        # 来自注销，则需清除蓝鲸bk_token
        if is_from_logout:
            response = self.set_bk_token_invalid(request, response)
        return response

    def _login_success(self, request, username):
        response = JsonResponse({"code": 200, "successcode": 20000, "data": {}})
        bk_token, expire_time = self.get_bk_token(username)
        response.set_cookie(self.BK_COOKIE_NAME, bk_token,
                            expires=expire_time,
                            domain=settings.BK_COOKIE_DOMAIN,
                            httponly=True)
        user = BkUser.objects.filter(username=username).first()
        self.record_login_log(request, user, "", bk_token)
        return response

    def login_api(self, request):
        data = request.POST.dict()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        domain = data.get("domain", "").strip()
        verify_code = data.get("verify_code", "").strip()
        seven_days_free = data.get("seven_days_free", 0)
        if domain:
            username = username + "@" + domain
        auth_object = OpsAnyRbacUserAuth(username, password)
        if domain:
            status, data = auth_object.check_users()
            # LDAP用户如果没在蓝鲸创建则创建
            self.get_user(data, username)
        else:
            status = AuthenticationForm(request, data=request.POST).is_valid()
        if status:
            # 检查MFA状态
            res = auth_object.get_user_google_auth_status()
            if res in ["0", "2"]:
                return self._login_success(request, username)
            elif res in ["1", "3", "4", "5", "7"]:
                res = auth_object.check_google_verify_code(verify_code, seven_days_free)
                if res:
                    return self._login_success(request, username)
                return JsonResponse({"code": 401, "error_code": 40101, "message": "MFA验证码错误"})
            else:
                if username == "admin":
                    return self._login_success(request, username)
                return JsonResponse({"code": 400, "error_code": 40000,
                                     "message": "ESB组件错误，请先联系管理员修复ESB后再做登录"})
        return JsonResponse({"code": 401, "error_code": 40100, "message": "账号密码错误"})
