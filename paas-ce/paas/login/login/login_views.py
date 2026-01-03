from datetime import datetime, timedelta
import json
import logging
import time
import uuid

import unicodedata
from django.template.response import TemplateResponse
from six.moves.urllib.parse import urlparse
from django.contrib.auth import (login as auth_login, logout as auth_logout)
from django.utils import timezone

from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import resolve_url, render
from django.views import View

import settings
from bkaccount.encryption import encrypt, salt, decrypt
from bkaccount.models import BkUser, BkToken, Loignlog, UserAuthToken
from common.mixins.exempt import LoginExemptMixin, CsrfExemptMixin, CsrfAndLoginExemptMixin

from login.status_code import success, SuccessStatusCode, error, ErrorStatusCode

logger = logging.getLogger("root")

from bkaccount.opsany_user_auth import OpsAnyRbacUserAuth
from bkaccount.forms import AuthenticationAndRegisterForm


class AuthConfigView(CsrfAndLoginExemptMixin, View):
    def get(self, request):
        auth_type = request.GET.get("auth_type", "")
        res, data = OpsAnyRbacUserAuth().get_auth_config(auth_type)
        default_data = [
            {
                "auth_type": "1",
                "auth_name": "本地登录",
                "auth_show_name": "本地登录",
                "auth_index": 1,
                "enabled": True
            }
        ]
        if not res:
            logger.info(f"AuthConfigView, {res}, {data}")
            if auth_type == "all":
                data = default_data
            else:
                data = []
        if not data and auth_type == "all":
            data = default_data
        
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, data))


class BaseLoginView(CsrfAndLoginExemptMixin, View):
    # cookie名称
    BK_COOKIE_NAME = settings.BK_COOKIE_NAME
    # cookie 有效期，默认为1天
    BK_COOKIE_AGE = settings.BK_COOKIE_AGE
    # cookie 有效期，默认为1天
    MFA_CACHE_COOKIE_AGE = 60 * 5
    # 登录回调链接
    REDIRECT_FIELD_NAME = 'c_url'
    # 登录连接
    BK_LOGIN_URL = str(settings.LOGIN_URL)
    # 允许误差时间，防止多台机器时间误差， 1分钟
    BK_TOKEN_OFFSET_ERROR_TIME = settings.BK_TOKEN_OFFSET_ERROR_TIME
    
    def first_error_message(self, form):
        error_data = form.errors.as_data()
        error_data_list = list(error_data.items())
        error_message = error_data_list[0][1][0].message
        message = "{}".format(error_message)
        return message
    
    def _check_white_list(self, username, request, auth_object):
        import ipaddress
        if username == "admin":
            return True, "管理员admin忽略白名单!"
        try:
            status, res_data = auth_object.get_auth_config(auth_type="white_list")
            if not status:
                return True, "Success"
            white_list = res_data.get("white_list") or ""
            
            if not isinstance(res_data, dict):  return True, "Success"
            if res_data.get("enabled") is False: return True, "Success"
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]  # 第一个IP是原始客户端
            else:
                ip = request.META.get('REMOTE_ADDR')
            networks = []
            for entry in str(white_list).split(","):
                try:
                    # 尝试解析为CIDR网段
                    if '/' in entry:
                        networks.append(ipaddress.ip_network(entry, strict=False))
                    # 解析为单IP (自动转换为/32或/128)
                    else:
                        networks.append(ipaddress.ip_address(entry))
                except ValueError:
                    continue
                    # networks.append(entry)
            ip_obj = ipaddress.ip_address(ip)
            if any(
                (isinstance(net, ipaddress.IPv4Network) and (ip_obj in net)) or
                (isinstance(net, ipaddress.IPv6Network) and (ip_obj in net)) or
                (isinstance(net, ipaddress.IPv4Address) and (ip_obj == net)) or
                (isinstance(net, ipaddress.IPv6Address) and (ip_obj == net))
                for net in networks
            ):
                return True, "Success"
            return False, "IP登录限制({}), 请联系管理员加入白名单!".format(ip)
        except Exception as e:
            logger.exception('Login _check_white_list, error: {}'.format(str(e)))
            return True, str(e)
    
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
    
    def login_success_response(self, request, user_or_form, redirect_to, app_id, res_data=None):
        
        if isinstance(user_or_form, AuthenticationForm):
            user = user_or_form.get_user()
            username = user_or_form.cleaned_data.get('username', '')
        else:
            user = user_or_form
            username = user.username
        if not self.is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url("/")

        try:
            auth_login(request, user)
        except:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth_login(request, user)
        
        bk_token, expire_time = self.get_bk_token(username)
        # response = HttpResponseRedirect(redirect_to)
        if not res_data:
            res_data = {}
        res_data.update({self.REDIRECT_FIELD_NAME: redirect_to, "bk_token": bk_token})
        json_data = {
            'code': 200,
            'successcode': 20000,
            'message': 'Success',
            'data': res_data
        }
        # print("JsonResponse_json_data", json_data)
        response = JsonResponse(json_data)
        response.set_cookie(self.BK_COOKIE_NAME, bk_token,
                            expires=expire_time,
                            domain=settings.BK_COOKIE_DOMAIN,
                            httponly=True)
        self.record_login_log(request, user, app_id, bk_token)
        return response
    
    def login_success_redirect_response(self, request, user_or_form, redirect_to, app_id, res_data=None):
        
        if isinstance(user_or_form, AuthenticationForm):
            user = user_or_form.get_user()
            username = user_or_form.cleaned_data.get('username', '')
        else:
            user = user_or_form
            username = user.username
        
        if not self.is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url("/")
        
        try:
            auth_login(request, user)
        except:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth_login(request, user)
        
        bk_token, expire_time = self.get_bk_token(username)
        # response = HttpResponseRedirect(redirect_to)
        if not res_data:
            res_data = {}
        res_data.update({self.REDIRECT_FIELD_NAME: redirect_to, "bk_token": bk_token})
        response = HttpResponseRedirect(redirect_to)
        response.set_cookie(self.BK_COOKIE_NAME, bk_token,
                            expires=expire_time,
                            domain=settings.BK_COOKIE_DOMAIN,
                            httponly=True)
        self.record_login_log(request, user, app_id, bk_token)
        return response
    
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
            plain_token = '%s|%s|%s' % (expire_time, username, salt(20))
            bk_token = encrypt(plain_token)
            try:
                BkToken.objects.create(token=bk_token)
            except Exception as error:
                logger.exception('Login ticket failed to be saved during ticket generation, error: {}'.format(error))
                # 循环结束前将bk_token置空后重新生成
                bk_token = '' if retry_count < 4 else bk_token
            retry_count += 1
        return bk_token, datetime.fromtimestamp(expire_time, timezone.get_current_timezone())
    
    def encrypt_cache_token(self, username):
        now_time = int(time.time())
        expire_time = now_time + self.MFA_CACHE_COOKIE_AGE
        plain_token = '%s|%s|%s' % (expire_time, username, salt(50))
        bk_token = encrypt(plain_token)
        return bk_token, datetime.fromtimestamp(expire_time, timezone.get_current_timezone())
    
    def decrypt_cache_token(self, cache_token):
        try:
            plain_bk_token = decrypt(cache_token)
        except Exception as error:
            return False, "验证失败, 请重新登录!", ""
        try:
            token_info = plain_bk_token.split('|')
        except Exception as error:
            return False, "验证失败, 请重新登录!!", ""
        if len(token_info) != 3:
            return False, "验证失败, 请重新登录!!!", ""
        expire_time = int(token_info[0])
        now_time = int(time.time())
        if now_time > expire_time:
            return False, "验证时间过长, 请重新登录!"
        if expire_time - now_time > self.BK_COOKIE_AGE:
            return False, "登录态有效期不合法, 请重新登录!"
        return True, "Success", token_info[1]
    
    def login_ip_and_browser(self, request):
        host = request.get_host()
        login_browser = request.META.get('HTTP_USER_AGENT') or 'unknown'
        # 获取用户ip request.META.get('HTTP_X_REAL_IP')
        login_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        try:
            if login_ip and "," in login_ip:
                login_ip = login_ip.split(",")[0].split()
        except Exception:
            pass
        return login_ip, login_browser, host
    
    def record_login_log(self, request, user, app_id, token=None):
        """
        记录用户登录日志
        """
        host = request.get_host()
        login_browser = request.META.get('HTTP_USER_AGENT') or 'unknown'
        # 获取用户ip request.META.get('HTTP_X_REAL_IP')
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
            print("Login log error: {}".format(str(e)))


class LoginIndexView(BaseLoginView):
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
    
    def get(self, request):
        params = request.GET.dict()
        c_url = params.get("c_url")
        is_from_logout = params.get("is_from_logout")
        
        if (c_url and len(params) == 1) or (is_from_logout and len(params) == 1) or (not params):
            response = TemplateResponse(request, "login/login.html", {"auth_type": "1", "error": ""})
            return self.set_bk_token_invalid(request, response)
        
        auth_type = params.get("auth_type")
        domain = params.get("domain")
        ad_domain = params.get("ad_domain")
        appid = params.get("appid")
        code = params.get("code")
        sso_code = params.get("sso_code")
        sso_sign = params.get("sso_sign")
        auth_obj = None
        if (auth_type == "8") and sso_code and sso_sign:  # 8 SSO
            auth_obj = OpsAnyRbacUserAuth(domain=domain, auth_type=auth_type, sso_code=sso_code, sso_sign=sso_sign)
        elif auth_type == "3":  # 3 企业微信
            auth_obj = OpsAnyRbacUserAuth(auth_type=auth_type, code=code, app_id=appid, ad_domain=ad_domain)
        elif auth_type == "6":  # 6 Oauth
            auth_obj = OpsAnyRbacUserAuth(auth_type=auth_type, domain=domain, code=code)
        elif auth_type in ["9", "10"]:  # 9 10 IDAAS IAM
            auth_obj = OpsAnyRbacUserAuth(auth_type=auth_type, domain=domain, params=params)
        elif code and domain:  # AD(auth_by_oauth)
            auth_obj = OpsAnyRbacUserAuth(code=code, domain=domain, ad_domain=ad_domain)
        if auth_obj:
            status, res = auth_obj.check_users()
            if status and res.get("auth_status") and res.get("domain_status") and res.get("have_user"):
                user_info = res.get("user_info")
                user = self.get_user(res, user_info.get("username"))
                return self.login_success_redirect_response(request, user, c_url, "")
            else:
                msg = res.get("message") or "登录失败, 请联系管理员!"
                logger.info(f"LoginIndexView.get.1: {auth_type}, {domain}, {params.keys()}, lock_msg: {msg}")
                return render(request, "login/login.html", {"auth_type": auth_type, "error": msg})
        
        else:
            msg = "暂不支持该登录方式!"
            logger.info(f"LoginIndexView.get.2: {auth_type}, {domain}, {params.keys()}, lock_msg: {msg}")
        response = TemplateResponse(request, "login/login.html", {"auth_type": "1", "error": msg})
        return self.set_bk_token_invalid(request, response)
    
    # 暂时保留旧接口, 防止初始化相关脚本调用失败
    def post(self, request):
        return LoginV3View().post(request)


class LoginV3View(BaseLoginView):
    def login_error_times(self, username, types="get"):
        """types: get clean add"""
        now = timezone.now()
        query = UserAuthToken.objects.filter(username=username, app_code="login").first()
        if types == "clean":
            if query: query.delete()
            return 0, now
        if types == "get":
            if query:
                try:
                    return int(query.auth_token), query.last_accessed_time
                except Exception as e:
                    return 1, query.last_accessed_time
            else:
                return 0, now
        save_dict = {"app_code": "login", "username": username, "auth_token": "1", "expires": datetime.now()}
        if not query:
            auth_token = 1
            save_dict["created_time"] = now
            save_dict["last_accessed_time"] = now
            query = UserAuthToken.objects.create(**save_dict)
        else:
            try:
                auth_token = int(query.auth_token)
            except Exception as e:
                auth_token = 1
            auth_token += 1
            save_dict["auth_token"] = str(auth_token)
            save_dict["last_accessed_time"] = now
            for k, v in save_dict.items():
                setattr(query, k, v)
            query.save()
        return auth_token, now
    
    def check_verify_code_and_login_lock(self, auth_object, username):
        auth_dict = auth_object.get_rbac_auth_config(username)
        mfa_days_enabled = auth_dict.get("mfa_days_enabled")
        # mfa_days = auth_dict.get("mfa_days")
        verification_code_enabled = auth_dict.get("verification_code_enabled")
        try:
            verification_code_config = int(auth_dict.get("verification_code_config"))
        except Exception as e:
            verification_code_config, verification_code_enabled = 0, False
        password_retry_times_enabled = auth_dict.get("password_retry_times_enabled")
        try:
            password_retry_times_config = int(auth_dict.get("password_retry_times_config"))
            locking_times_config = auth_dict.get("locking_times_config")
            int(password_retry_times_config)
            if len(locking_times_config) > 2:
                locking_times_config = "1h"
            num, unit = int(locking_times_config[:-1]), locking_times_config[-1]
            d = {{"m": "minutes", "h": "hours", "d": "days"}.get(unit, "hours"): num}
            locking_times_config = timedelta(**d)
        except Exception as e:
            password_retry_times_config, password_retry_times_enabled, locking_times_config = 0, False, timedelta(hours=1)
        
        show_mfa_days, show_verify_code, show_login_lock, while_show_verify_code, while_show_login_lock = False, False, False, False, False
        if mfa_days_enabled:
            show_mfa_days = True
        error_count, last_accessed_time = self.login_error_times(username)
        if verification_code_enabled:
            if verification_code_config <= error_count:
                show_verify_code = True
            if verification_code_config <= error_count + 1:
                while_show_verify_code = True  # 8:00 1:00    8:30
        
        unlock_times = last_accessed_time + locking_times_config
        unlock_times_str = timezone.localtime(unlock_times).strftime("%Y-%m-%d %H:%M:%S")
        if password_retry_times_enabled and (unlock_times > timezone.now()):
            if password_retry_times_config <= error_count:
                show_login_lock = True
            if password_retry_times_config <= error_count + 1:
                while_show_login_lock = True
        if unlock_times < timezone.now():
            self.login_error_times(username, types="clean")
        return show_mfa_days, show_verify_code, show_login_lock, while_show_verify_code, while_show_login_lock, error_count, password_retry_times_enabled, password_retry_times_config, unlock_times_str
    
    def post(self, request):
        login_ip, login_browser, host = self.login_ip_and_browser(request)
        # print(11111111111111, login_ip, login_browser, host)
        data = json.loads(request.body)
        params = request.GET.dict()
        app_id = data.get('app_id', params.get('app_id', ''))
        # data["geetest_challenge"] = uuid.uuid4().hex
        # data["geetest_seccode"] = uuid.uuid4().hex
        # data["geetest_validate"] = uuid.uuid4().hex
        cache_token = data.get("cache_token")
        
        # 正常登录
        redirect_field_name = 'c_url'
        redirect_to = data.get(redirect_field_name, "/")
        auth_type = data.get("auth_type", "1")
        username = data.get("username", "")
        password = data.get("password", "")
        domain = data.pop("domain", None)
        google_auth_type = data.pop("google_auth_type", None)
        verify_code = data.pop("verify_code", None)
        secret = data.pop("secret", "")
        seven_days_free = data.pop("seven_days_free", 0)
        if domain:
            username = username + "@" + domain
        auth_object = OpsAnyRbacUserAuth(auth_type=auth_type, username=username, password=password)
        status, message = self._check_white_list(username, request, auth_object)
        if not status:
            return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS))
        (show_mfa_days, show_verify_code, show_login_lock,
         while_show_verify_code, while_show_login_lock, error_times, password_retry_times_enabled,
         password_retry_times_config, unlock_times_str) \
            = self.check_verify_code_and_login_lock(auth_object, username)
        # if ("@" not in username) or ((not domain) and ("@" in username)):  # 密码本地登录 第三方用户本地密码登录
        # mfa_check = False
        # if cache_token:
        #     status, message, u = self.decrypt_cache_token(cache_token)
        #     if not status:
        #         return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR,custom_message=message))
        #     mfa_check = True
        # if not mfa_check:
        show_dict = {"show_verify_code": show_verify_code, "show_mfa_days": show_mfa_days}
        lock_msg = "登录失败 {} 次, 已超上限, 账号锁定, 请 {} 后再次登录, 或联系管理员解锁!".format(error_times, unlock_times_str)
        if show_login_lock:
            logger.error(f"LoginV3View.post.1: {username}, {auth_type}, {login_ip}, {login_browser}, lock_msg: {lock_msg}")
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR2, custom_message=lock_msg, add_params=show_dict))
        
        if auth_type == "1":  # 本地登录
            form = AuthenticationAndRegisterForm(request, data=data)
            if not form.is_valid():
                if (not show_verify_code) and while_show_verify_code:
                    show_dict["show_verify_code"] = while_show_verify_code
                print("login_error_times_1_add: ", username, self.login_error_times(username, types="add"))
                msg = self.first_error_message(form)
                if password_retry_times_enabled:
                    retry_times = password_retry_times_config - error_times - 1
                    if retry_times <= 0:
                        msg += f"(登录失败 {password_retry_times_config} 次, 已超上限, 账号锁定)"
                    else:
                        msg += f"(还可以重试{retry_times}次)"
                    logger.error(f"LoginV3View.post.2: {username}, {auth_type}, {login_ip}, {login_browser}, lock_msg: {msg}")
                return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=msg, add_params=show_dict))
            user_or_form = form
        elif auth_type in ["2", "7"]:  # AD LDAP
            user_status, user_data = auth_object.check_users()
            # logger.error(f"{user_status}---{user_data}")
            if not user_status:
                msg = user_data.get("message") or "登录失败, 请联系管理员!"
                if password_retry_times_enabled:
                    retry_times = password_retry_times_config - error_times - 1
                    if retry_times <= 0:
                        msg += f"(登录失败 {password_retry_times_config} 次, 已超上限, 账号锁定)"
                    else:
                        msg += f"(还可以重试{retry_times}次)"
                    logger.error(f"LoginV3View.post.2: {username}, {auth_type}, {login_ip}, {login_browser}, lock_msg: {msg}")

                if (not show_verify_code) and while_show_verify_code:
                    show_dict["show_verify_code"] = while_show_verify_code
                print("login_error_times_27_add: ", username, self.login_error_times(username, types="add"))
                logger.info(f"LoginV3View.post.3: {username}, {auth_type}, lock_msg: {msg}")
                return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=msg, add_params=show_dict))
            user_info = user_data.get("user_info")
            user_or_form = self.get_user(user_data, user_info.get("username"))
        else:
            msg = "暂不支持该登录方式!"
            logger.info(f"LoginV3View.post.4: {username}, {auth_type}, lock_msg: {msg}")
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=msg, add_params=show_dict))
        google_auth_status = auth_object.get_user_google_auth_status()
        if google_auth_status == "9":
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="用户不存在!", add_params=show_dict))
        elif google_auth_status == "8":
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="用户禁止登录!", add_params=show_dict))
        elif google_auth_status in ["7", "6", "2", "0"]:  # 直接登录成功
            pass
            # 非MFA直接登录
            # return
        elif google_auth_status in ["5", "4", "1"]:  # MFA验证
            if not verify_code:
                cache_token, times = self.encrypt_cache_token(username)
                res_dict = {
                    "google_auth_type": "verify_google_auth",
                    "google_auth_status": google_auth_status,
                    "cache_token": cache_token,
                }
                res_dict.update(show_dict)
                return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, res_dict, add_params=show_dict))
            check_status = auth_object.check_google_verify_code(verify_code, seven_days_free)
            if not check_status:
                return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="授权码错误, 请重新输入!", add_params=show_dict))
            # FMA验证成功直接登录
            # return
        elif google_auth_status in ["3"]:
            if google_auth_type == "bind_google_auth":
                bind_google_auth = auth_object.bind_google_auth(secret=secret, verify_code=verify_code)
                if not bind_google_auth.get("result"):
                    msg = "授权码错误, 请重新输入!"
                    return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message=msg, add_params=show_dict))
                # FMA绑定成功直接登录
                # return
            else:
                cache_token, times = self.encrypt_cache_token(username)
                google_auth_pic = auth_object.get_google_auth()
                res_dict = {
                    "google_auth_url": google_auth_pic.get("url", ""),
                    "secret": google_auth_pic.get("secret", ""),
                    "google_auth_type": "bind_google_auth",
                    "google_auth_status": google_auth_status,
                    "google_auth_username": username,
                    "cache_token": cache_token,
                }
                res_dict.update(show_dict)
                return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, res_dict))
        else:
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR, custom_message="登录失败!", add_params=show_dict))
        print("login_error_times_clean: ", username, self.login_error_times(username, types="clean"))
        return self.login_success_response(request, user_or_form, redirect_to, app_id)
    
    def get(self, request):
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS))


class CheckPasswordView(View):
    def first_error_message(self, form):
        error_data = form.errors.as_data()
        error_data_list = list(error_data.items())
        error_message = error_data_list[0][1][0].message
        message = "{}".format(error_message)
        return message

    # def get(self, request):
    #     data = request.GET.dict()
    #     return self._check(request, data)
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception as e:
            data = request.POST.dict()

        return self._check(request, data)

    def _check(self, request, data):
        data["username"] = request.user.username
        form = AuthenticationAndRegisterForm(request, data=data)
        if not form.is_valid():
            msg = self.first_error_message(form)
            return JsonResponse(error(ErrorStatusCode.CUSTOM_ERROR,custom_message=msg))
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS))


class UserLoginUnlockView(View):
    def get(self, request):
        data = request.GET.dict()
        username = data.get("username")
        unlock_type = data.get("unlock_type", "disabled_this_user_lock")  # disabled_all_user_lock
        user = request.user
        if user and not isinstance(user, BkUser):
            return JsonResponse(error(ErrorStatusCode.PERMISSION_DENIED))
        
        if user.role_code != 1:
            return JsonResponse(error(ErrorStatusCode.PERMISSION_DENIED))
        
        if unlock_type == "disabled_all_user_lock":
            count, res_dict = UserAuthToken.objects.filter(app_code="login").delete()
            return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, count))
        else:
            query = UserAuthToken.objects.filter(app_code="login", username=username).first()
            if not query:
                res_dict = {}
            else:
                query.delete()
                res_dict = query.to_rbac_unlock_dict()
            return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS, res_dict))


class UserExternalLoginView(BaseLoginView):
    def get(self, request, **kwargs):
        auth_name = kwargs.get("auth_name")
        domain = kwargs.get("domain")
        params = request.GET.dict() or {}
        params["auth_name"] = auth_name
        params["api"] = "v3"
        c_url = params.get("c_url") or "/"
        auth_type_dict = {
            "qw": "3",  # code appid
            "oauth": "6",  # code
            "sso": "8",  # sso_code sso_sign
            "idaas": "9",  # params token参数自定义
            "iam": "10",  # params token参数自定义
            "ad_by_oauth": "7",  # code ad_domain
        }
        auth_type = auth_type_dict.get(auth_name)
        if not auth_type:
            msg = "暂不支持该登录方式!"
            logger.info(f"UserExternalLoginView.get1: {msg}, auth_name: {auth_name}")
            response = TemplateResponse(request, "login/login.html", {"auth_type": "1", "error": msg})
            return self.set_bk_token_invalid(request, response)
        rbac_dict = {"auth_type": auth_type, "domain": domain, "params": params}
        auth_obj = OpsAnyRbacUserAuth(**rbac_dict)
        status, res = auth_obj.check_users()
        if status and res.get("auth_status") and res.get("domain_status") and res.get("have_user"):
            user_info = res.get("user_info")
            user = self.get_user(res, user_info.get("username"))
            return self.login_success_redirect_response(request, user, c_url, "")
        else:
            msg = res.get("message") or "登录失败, 请联系管理员!"
            return render(request, "login/login.html", {"auth_type": auth_type, "error": msg})

