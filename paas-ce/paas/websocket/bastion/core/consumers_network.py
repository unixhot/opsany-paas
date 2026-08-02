# -*- coding: utf-8 -*-
import contextlib
import time
import json
import logging
import uuid
import datetime
import settings
import threading
import os
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection

from bastion.component.redis_client_conn import get_redis_dict_data

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_str as smart_unicode

from bastion.core.terminal.component import SSHBaseComponent
from bastion.core.status_code import WebSocketStatusCode
from bastion.component.core import CheckUserHostComponent
from bastion.component.common import GetUserInfo
from bastion.models import HostModel, CredentialModel, SessionLogModel, HostCredentialRelationshipModel
from bastion.utils.encryption import PasswordEncryption
from bastion.core.guacamole.component import GuacamoleThread, GuacamoleThreadWrite
from bastion.core.guacamole.client import GuacamoleClient

app_logging = logging.getLogger("app")


class GuacamoleNetWorkWebsocket(WebsocketConsumer):
    GUACD_CLIENT = None
    width = 1920
    height = 1080
    dpi = 900
    wait_time = time.time()
    token = ""
    cache = get_redis_connection("cache")
    user = None
    recording_path = os.path.join(settings.GUACD_PATH, "logfile")
    recording_name = str(uuid.uuid4())

    def connect(self):  # sourcery skip: raise-specific-error
        self.accept('guacamole')
        # py3.7老版本修复bug
        self.recording_name = str(uuid.uuid4())
        self.wait_time = time.time()
        status, code, data = self.check_token()
        if not status and status is not None:
            raise Exception(code)
        query_string = self.scope['query_string'].decode()
        if query_string:
            query_dict = dict([x.split('=', 1) for x in query_string.split('&')])
            if query_dict.get("width") and query_dict.get("height") and query_dict.get("dpi"):
                self.width = int(float(query_dict["width"]))
                self.height = int(float(query_dict["height"]))
                self.dpi = int(float(query_dict["dpi"]))
        try:
            timeout = int(data.get("timeout", 10))
        except Exception:
            timeout = 10
        if not data.get("cache"):
            server_ = HostModel.fetch_one(id=data.get("host_id"))
            credential_host = HostCredentialRelationshipModel.fetch_one(id=data.get("credential_host_id"))
            drive_path = os.path.join(settings.GUACD_PATH, str(server_.id))
            ori_drive_path = os.path.join(settings.ORI_GUACD_PATH, str(server_.id))
        else:
            server_ = None
            credential_host = None
            drive_path = os.path.join(settings.GUACD_PATH, str(data.get("host_id")))
            ori_drive_path = os.path.join(settings.ORI_GUACD_PATH, str(data.get("host_id")))
        guacamole_host = settings.GUACD_HOST
        guacamole_port = settings.GUACD_PORT
        if server_:
            network_proxy = server_.network_proxy
            if network_proxy:
                guacamole_host = network_proxy.windows_ip
                guacamole_port = network_proxy.windows_port
        self.GUACD_CLIENT = GuacamoleClient(guacamole_host, guacamole_port, timeout=timeout)
        if not os.path.exists(self.recording_path):
            os.makedirs(self.recording_path)
        # 创建驱动目录（guacd 通过 RDP 映射给 Windows 的共享目录）
        # 注意：guacd 容器内进程可能以非 root 用户运行，因此给 777 权限
        if not os.path.exists(ori_drive_path):
            os.makedirs(ori_drive_path, mode=0o777)
        else:
            os.chmod(ori_drive_path, 0o777)
        args = {
            "enable_drive": "true",
            "create_drive_path": "true",
            "client_name": "OpsAny",
            "drive_name": "Downloads",
            "drive_path": drive_path
        }
        if server_:
            credential = credential_host.credential
            hostname = server_.host_address.strip()
            port = server_.port
            username = credential.login_name.strip()
            if credential.login_type == credential.LOGIN_AUTO:
                password = PasswordEncryption().decrypt(credential.login_password.strip())
            else:
                password = data.get("password")
            if server_.resource_type == HostModel.RESOURCE_NETWORK:
                if server_.protocol_type == "SSH":
                    protocol = "ssh"
                else:
                    protocol = "telnet"
            elif server_.system_type.strip() == "Linux":
                protocol = "ssh"
            else:
                protocol = "rdp"
        elif data.get("cache"):
            protocol = "rdp"
            hostname = data.get("host_info").get("ip")
            port = int(data.get("host_info").get("port"))
            username = data.get("host_info").get("username")
            password = data.get("host_info").get("password")
        else:
            raise Exception("Server not exist!!!")
        args.update({
            "security": 'any',
            "ignore_cert": "true",
            "disable_audio": "true",
            "recording_path": self.recording_path,
            "recording_name": self.recording_name,
            "create_recording_path": 'true'
        })
        dic = dict(
            protocol=protocol,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            width=self.width,
            height=self.height,
            dpi=self.dpi,
            **args
        )
        self.GUACD_CLIENT.handshake(**dic)
        self.closed = threading.Event()
        guacamolethread = GuacamoleThread(self)
        guacamolethread.daemon = True
        guacamolethread.start()
        self._guacamole_thread = guacamolethread
        guacamolethreadwrite = GuacamoleThreadWrite(self)
        guacamolethreadwrite.daemon = True
        guacamolethreadwrite.start()
        self._guacamole_write_thread = guacamolethreadwrite
        save_dict = {
            "user": self.user.username,
            "channel": self.channel_name,
            "resource_type": "network",
            "login_type": 1,
            "system_type": "",
            "log_name": self.recording_name,
            "guacamole_client_id": self.GUACD_CLIENT.id,
            "width": self.width,
            "height": self.height
        }
        if server_:
            save_dict.update({
                "host": server_,
                "host_name": server_.host_name,
                "host_name_code": server_.host_name_code,
                "protocol_type": server_.protocol_type,
                "network_type": server_.network_type,
                "host_address": server_.host_address,
                "port": server_.port,
                "login_name": credential_host.credential.login_name,
            })
        else:
            host_info = data.get("host_info") or {}
            save_dict.update({
                "host_name": host_info.get("host_name"),
                "host_name_code": host_info.get("host_name_code"),
                "protocol_type": host_info.get("protocol_type"),
                "network_type": host_info.get("network_type"),
                "host_address": host_info.get("ip"),
                "port": host_info.get("port"),
                "login_name": host_info.get("username"),
            })
        SessionLogModel.objects.create(**save_dict)

    def disconnect(self, code):
        # 1. 发送停止信号
        self.closed.set()
        self.closeguacamole()
        # 2. 等待写线程退出
        if self._guacamole_write_thread:
            try:
                self._guacamole_write_thread.join(timeout=2)
            except Exception:
                pass
        # 3. 关闭 TCP socket → 读线程 recv() 退出
        if self.GUACD_CLIENT and self.GUACD_CLIENT._client is not None:
            try:
                self.GUACD_CLIENT.client.close()
            except Exception:
                pass
        # 4. 等待读线程退出
        if self._guacamole_thread:
            try:
                self._guacamole_thread.join(timeout=2)
            except Exception:
                pass
        audit_log = SessionLogModel.objects.filter(channel=self.channel_name)
        if audit_log:
            audit_log.update(
                    is_finished=True,
                    end_time=datetime.datetime.now()
                )
        else:
            app_logging.error("[ERROR] Windows Terminal Not Find Session Log, Channel name: %s", self.channel_name)
        with contextlib.suppress(Exception):
            self.close()
        self._run_guacenc()
        self._guacamole_thread = None
        self._guacamole_write_thread = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue_instance = None
        self.GUACD_CLIENT = None
        self._guacamole_thread = None
        self._guacamole_write_thread = None

    _queue_instance_class = None

    def queue(self):
        cls = type(self)
        if cls._queue_instance_class is None:
            cls._queue_instance_class = SSHBaseComponent().get_redis_instance()
        return cls._queue_instance_class

    def closeguacamole(self):
        try:
            self.queue().publish(self.channel_name, json.dumps(['close']))
        except Exception:
            pass

    def check_timeout_close(self):
        current_time = time.time()
        if int(current_time - self.wait_time) > settings.TERMINAL_TIMEOUT:
            self._extracted_from_receive_5()

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        self.check_timeout_close()
        self.queue().publish(self.channel_name, text_data)
        if not text_data.startswith("4.sync,1"):
            self.wait_time = time.time()
        if text_data == '10.disconnect;':
            self.disconnect(1000)

    def _extracted_from_receive_5(self):
        self.send("10.disconnect;")
        self.queue().publish(self.channel_name, "10.disconnect;")
        self.disconnect(1001)

    def _run_guacenc(self):
        try:
            pass
        except Exception as e:
            app_logging.error("[ERROR] guacenc execution error: %s", str(e))

    def get_request_param_dict(self):
        query_string = self.scope.get("query_string").decode()
        request_param = dict([x.split("=", 1) for x in query_string.split("&")])
        return request_param

    def get_cookie(self):
        cookies = None
        cookie = {}
        for header in self.scope['headers']:
            if header[0] == b'cookie':
                cookies = header[1].decode()
                break
        if cookies:
            cookie = dict([cookie.split("=", 1) for cookie in cookies.split("&")])
        return cookie

    def get_user(self):
        user = GetUserInfo().get_user_info(bk_token=self.scope.get("cookies").get("bk_token"))
        return user

    def check_link_user(self, user_id):
        self.user = self.get_user()
        if self.user:
            try:
                if self.user.id == user_id:
                    return True
                return False
            except Exception as e:
                app_logging.error("[ERROR] check_link_user error: {}".format(str(e)))
                return False
        return False

    def get_link_config(self, token):
        try:
            data = get_redis_dict_data(self.cache, token)
            return True, data
        except Exception as e:
            app_logging.error("[ERROR] get_link_config error: {}".format(str(e)))
            return False, {}

    def check_link_time(self, data):
        access_data = data.get("access_data")
        try:
            access_ip = self.scope.get("client")[0]
        except Exception:
            access_ip = ""
        status, _ = CheckUserHostComponent().check_access_strategy(access_data, access_ip)
        return status

    def check_token(self):
        request_param = self.get_request_param_dict()
        self.token = request_param.get("token")
        if not self.token:
            self.token = self.get_cookie().get("link_token")
        status, data = self.get_link_config(self.token)
        if status:
            status = self.check_link_user(data.get("user_id"))
            if status:
                if data.get("admin") or data.get("cache"):
                    return None, "", data
                status = self.check_link_time(data)
                if status:
                    return True, "", data
                return False, WebSocketStatusCode.ACCESS_ERROR, {}
            return False, WebSocketStatusCode.USER_ERROR, {}
        return False, WebSocketStatusCode.PARAM_ERROR, {}
