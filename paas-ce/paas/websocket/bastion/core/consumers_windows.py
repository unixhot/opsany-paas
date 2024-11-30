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
    from django.utils.encoding import smart_text as smart_unicode

from bastion.core.terminal.component import SSHBaseComponent
from bastion.core.status_code import WebSocketStatusCode
from bastion.component.core import CheckUserHostComponent
from bastion.component.common import GetUserInfo
from bastion.models import HostModel, SessionLogModel, HostCredentialRelationshipModel, NetworkProxyModel
from bastion.utils.encryption import PasswordEncryption
from bastion.core.guacamole.component import GuacamoleThread, GuacamoleThreadWrite
from bastion.core.guacamole.client import GuacamoleClient

app_logging = logging.getLogger("app")


class GuacamoleWebsocket(WebsocketConsumer):
    GUACD_CLIENT = None
    width = 1920
    height = 1080
    dpi = 900
    wait_time = time.time()
    token = ""
    cache = get_redis_connection("cache")
    user = None
    recording_path = os.path.join(settings.GUACD_PATH, "logfile")
    recording_name = "UUID"

    def get_request_param_dict(self):
        query_string = self.scope.get("query_string").decode()
        request_param = dict([x.split('=', 1) for x in query_string.split('&')])
        return request_param

    def get_user(self):
        # token = "VdM0Qc5j2JOXCeociGMm9moDoiHblwIF3m1X58rwkzc"
        # user = GetUserInfo().get_user_info(bk_token=token)
        user = GetUserInfo().get_user_info(bk_token=self.scope.get("cookies").get("bk_token"))
        return user

    def get_cookie(self):
        cookie = {}
        cookies = next((header[1].decode() for header in self.scope['headers'] if header[0] == b'cookie'), None)

        if cookies:
            cookie = dict([cookie.split('=', 1) for cookie in cookies.split('&')])
        return cookie

    def get_link_config(self, token):
        try:
            data = get_redis_dict_data(self.cache, token.split("/")[0])
            return True, data
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, get_link_config error: {}, param: {}".format(
                str(e), str(token))
            )
            return False, {}

    def check_link_user(self, user_id):
        self.user = self.get_user()
        if self.user:
            try:
                if self.user.id == user_id:
                    return True
                return False
            except Exception as e:
                app_logging.error("[ERROR] SSH web socket, check_link_user error: {}, param: {}".format(
                    str(e), str(user_id))
                )
                return False
        return False

    def check_link_time(self, data):
        """
        使用Token从缓存中读取验证数据
        """
        access_data = data.get("access_data")
        try:
            access_ip = self.scope.get("client")[0]
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, check_link_time error: {}".format(str(e)))
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

    def connect(self):  # sourcery skip: raise-specific-error
        self.accept('guacamole')
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
        guacamole_host, guacamole_port = None, None
        try:
            timeout = int(data.get("timeout", 10))
        except Exception:
            timeout = 10
        if not data.get("cache"):
            server_ = HostModel.fetch_one(id=data.get("host_id"))
            credential_host = HostCredentialRelationshipModel.fetch_one(id=data.get("credential_host_id"))
            drive_path = os.path.join(settings.GUACD_PATH, str(server_.id))
            ori_drive_path = os.path.join(settings.ORI_GUACD_PATH, str(server_.id))
            network_proxy = server_.network_proxy
            if network_proxy:
                guacamole_host = network_proxy.windows_ip
                guacamole_port = network_proxy.windows_port
        else:
            server_ = None
            credential_host = None
            drive_path = os.path.join(settings.GUACD_PATH, str(data.get("host_id")))
            ori_drive_path = os.path.join(settings.ORI_GUACD_PATH, str(data.get("host_id")))
            network_proxy_id = data.get("host_info", {}).get("network_proxy")
            if network_proxy_id:
                try: network_proxy_id = int(network_proxy_id)
                except: raise Exception(WebSocketStatusCode.PROXY_LINK_ERROR)
                network_proxy = NetworkProxyModel.fetch_one(id=network_proxy_id)
                if not network_proxy:
                    raise Exception(WebSocketStatusCode.PROXY_LINK_ERROR)
                guacamole_host = network_proxy.windows_ip
                guacamole_port = network_proxy.windows_port
        if (not guacamole_host) and (not guacamole_port):
            guacamole_host = settings.GUACD_HOST
            guacamole_port = settings.GUACD_PORT

        self.GUACD_CLIENT = GuacamoleClient(guacamole_host, guacamole_port, timeout=timeout)
        # if not os.path.exists(ori_drive_path + "/Download"):
        #     os.makedirs(ori_drive_path + "/Download")
        if not os.path.exists(self.recording_path):
            os.makedirs(self.recording_path)
        args = {
            "enable_drive": "true",
            "create_drive_path": "true",
            "client_name": "OpsAny",    # 目标主机显示 OpsAny 上的 Downloads
            "drive_name": "Downloads",
            "drive_path": drive_path
        }
        if server_:
            credential = credential_host.credential
            hostname = server_.host_address.strip()
            port = server_.port
            username = credential.login_name.strip()
            if credential.login_type == credential.LOGIN_AUTO:
                if credential.login_password:
                    password = PasswordEncryption().decrypt(credential.login_password.strip())
                else:
                    password = ""

            else:
                password = data.get("password")
            if server_.resource_type == HostModel.RESOURCE_NETWORK:
                if server_.protocol_type == HostModel.PROTOCOL_SSH:
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
            # app_logging.info(hostname, port, username, password)
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
        handshake_dict = dict(
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
        self.GUACD_CLIENT.handshake(**handshake_dict)
        # print("dicdic", dic)
        self.closed = threading.Event()
        guacamolethread = GuacamoleThread(self)
        guacamolethread.setDaemon = True
        guacamolethread.start()
        guacamolethreadwrite = GuacamoleThreadWrite(self)
        guacamolethreadwrite.setDaemon = True
        guacamolethreadwrite.start()
        if server_:
            SessionLogModel.objects.create(
                user=self.user.username,
                host=server_,
                channel=self.channel_name,
                host_name=server_.host_name,
                system_type=server_.system_type,
                host_address=server_.host_address,
                login_name=credential_host.credential.login_name,
                log_name=self.recording_name,
                guacamole_client_id=self.GUACD_CLIENT.id,
                width=self.width,
                height=self.height
            )
        else:
            SessionLogModel.objects.create(
                user=self.user.username,
                channel=self.channel_name,
                host_name=data.get("host_info").get("host_name"),
                system_type="Windows",
                host_address=data.get("host_info").get("ip"),
                login_name=data.get("host_info").get("username"),
                log_name=self.recording_name,
                guacamole_client_id=self.GUACD_CLIENT.id,
                width=self.width,
                height=self.height
            )

    def disconnect(self, code):
        self.closed.set()
        audit_log = SessionLogModel.objects.filter(channel=self.channel_name)
        if audit_log:
            audit_log.update(
                is_finished=True,
                end_time=datetime.datetime.now()
            )
            # width = str(audit_log[0].width)
            # height = str(audit_log[0].height)
            # full_path = os.path.join(self.recording_path, self.recording_name)
            # command = '/opt /guacamole-server-1.2.0/src/guacenc/guacenc -s ' \
            #           + width + "x" + height + ' -r 1000000 -f ' + full_path
            # os.system(command)
        else:
            app_logging.error(
                "[ERROR] Windows Terminal Not Find Session Log, Channel name: {}".format(self.channel_name))
        with contextlib.suppress(Exception):
            self.close()
        self.GUACD_CLIENT.client.close()
        with contextlib.suppress(Exception):
            self.close()
        self.closeguacamole()

    def queue(self):
        queue = SSHBaseComponent().get_redis_instance()
        queue.pubsub()
        return queue

    def closeguacamole(self):
        self.queue().publish(self.channel_name, json.dumps(['close']))

    def check_timeout_close(self):
        # 空闲超时退出
        current_time = time.time()
        if int(current_time - self.wait_time) > settings.TERMINAL_TIMEOUT:
            self._extracted_from_receive_5()

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        self.check_timeout_close()
        # status, _, _ = self.check_token()
        status = True
        if status:
            self.queue().publish(self.channel_name, text_data)
            if not text_data.startswith("4.sync,1"):
                self.wait_time = time.time()
            if text_data == '10.disconnect;':
                self.disconnect(1000)
        else:
            self._extracted_from_receive_5()

    # TODO Rename this here and in `check_timeout_close` and `receive`
    def _extracted_from_receive_5(self):
        self.send("10.disconnect;")
        self.queue().publish(self.channel_name, "10.disconnect;")
        self.disconnect(1001)
