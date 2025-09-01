import contextlib
import paramiko
import time
import json
import logging
import uuid
import datetime
import socket
from channels.generic.websocket import AsyncWebsocketConsumer
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
from bastion.core.terminal.component import SshTerminalThread, InterActiveShellThread
from bastion.utils.encryption import PasswordEncryption

app_logging = logging.getLogger("app")


class Database(AsyncWebsocketConsumer):
    ssh = paramiko.SSHClient()
    http_user = True
    channel_session = True
    channel_session_user = True
    first_flag = True
    wait_time = time.time()
    user = None
    cache = get_redis_connection("cache")
    token = ""
    database = None
    session_log = None

    def get_request_param_dict(self):
        query_string = self.scope.get("query_string").decode()
        request_param = dict([x.split('=', 1) for x in query_string.split('&')])
        return request_param

    def get_cookie(self):
        cookies = None
        cookie = {}
        for header in self.scope['headers']:
            if header[0] == b'cookie':
                cookies = header[1].decode()
                break
        if cookies:
            cookie = dict([cookie.split('=', 1) for cookie in cookies.split('&')])
        return cookie

    def get_link_config(self, token):
        try:
            data = get_redis_dict_data(self.cache, token)
            return True, data
        except Exception as e:
            app_logging.error("[ERROR] Databases web socket, get_link_config error: {}, param: {}".format(
                str(e), str(token))
            )
            return False, {}

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
                app_logging.error("[ERROR] Databases web socket, check_link_user error: {}, param: {}".format(
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
            app_logging.error("[ERROR] Databases web socket, check_link_time error: {}".format(str(e)))
            access_ip = ""
        status, _ = CheckUserHostComponent().check_access_strategy(access_data, access_ip)
        return status

    def check_token(self):
        request_param = self.get_request_param_dict()
        if not self.token:
            if request_param.get("token"):
                self.token = request_param.get("token")
            else:
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

    def get_password(self, password):
        """
        密码解密
        """
        try:
            password = PasswordEncryption().decrypt(password)
        except Exception as e:
            app_logging.error("[ERROR] Databases web socket, get_password error: {}".format(str(e)))
            password = ""
        return password

    def client_proxy_or_local_link(self, ip="127.0.0.1", port=22, username="", password="", timeout=5):
        """
        创建本地连接或者代理连接
        """
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if username:
                self.ssh.connect(hostname=ip, port=port, username=username, password=password, timeout=timeout)
            else:
                self.ssh.connect(hostname=ip, port=port, password=password, timeout=timeout)
            return True, ""
        except socket.timeout:
            return False, WebSocketStatusCode.TIME_OUT
        except Exception as e:
            app_logging.error("[ERROR] Databases web socket, client_proxy_or_local_link error: {}, param: {}".format(
                str(e), str([ip, port])
            ))
            return False, WebSocketStatusCode.SSH_CHECK_ERROR

    def close_connect(self, text):
        self.send(text_data=str(text))
        self.close()
        return

    def get_login_database_command(self, database_type, ip="", port="", username="", password=""):
        try:
            database_type = database_type.lower()
        except Exception as e:
            app_logging.error("[ERROR] Databases web socket, get_login_database_command error: {}, param: {}".format(
                str(e), str(database_type)
            ))
            database_type = ""
        if database_type in ["mysql", "redis", "mongodb"]:
            if database_type == "mysql":
                command = "mysql -u{} -p{}".format(username, password)
                command += " -h{}".format(ip) if ip else ""
                command += " -P{}".format(port) if port else ""
                return True, command
            if database_type == "redis":
                command = "redis-cli -a {}".format(password)
                command += " -h {}".format(ip) if ip else ""
                command += " -p {}".format(port) if port else ""
                return True, command
            if database_type == "mongodb":
                command = "mongo --username {} --password {}".format(username, password)
                command += " --host {}".format(ip) if ip else ""
                command += " --port {}".format(port) if port else ""
                return True, command
        return False, WebSocketStatusCode.DATABASE_TYPE_ERROR

    def _create_databases_link(self, credential, database, password, timeout=5):
        """
        获取数据库连接命令，创建代理/本地连接
        """
        if credential.login_type == CredentialModel.LOGIN_AUTO:
            password = self.get_password(credential.login_password)
            login_name = credential.login_name
            port = database.port
            host_address = database.host_address
            database_type = database.database_type
            command_status, command = self.get_login_database_command(
                database_type,
                host_address,
                port,
                login_name,
                password
            )
        else:
            login_name = credential.login_name
            host_address = database.host_address
            database_type = database.database_type
            port = database.port
            command_status, command = self.get_login_database_command(
                database_type,
                host_address,
                port,
                login_name,
                password
            )
        if not command_status:
            self.close_connect(command)
            return ""
        # 如果有代理
        if database.network_proxy:
            network_proxy = database.network_proxy
            status, code = self.client_proxy_or_local_link(
                ip=network_proxy.linux_ip,
                port=network_proxy.linux_port,
                username=network_proxy.linux_login_name,
                password=self.get_password(network_proxy.linux_login_password),
                timeout=timeout
            )
        else:
            status, code = self.client_proxy_or_local_link(timeout=timeout)
        if not status:
            self.close_connect(code)
            return ""
        return command

    def _create_cache_databases_link(self, token_data, timeout):
        """
        创建外平台连接
        """
        host_info = token_data.get("host_info")

        command_status, command = self.get_login_database_command(
            host_info.get("database_type"),
            host_info.get("ip"),
            host_info.get("port"),
            host_info.get("username"),
            host_info.get("password")
        )
        if not command_status:
            self.close_connect(command)
            return ""
        status, code = self.client_proxy_or_local_link(timeout=timeout)
        if not status:
            self.close_connect(code)
            return ""
        return command

    def create_database_link(self, data):
        """
        校验数据以及创建SSH连接
        """
        try:
            timeout = int(data.get("timeout", 10))
        except Exception:
            timeout = 10
        if not data.get("cache"):
            host_id = data.get("host_id")
            credential_host_id = data.get("credential_host_id")
            password = data.get("password")
            credential_host = HostCredentialRelationshipModel.fetch_one(id=credential_host_id)
            self.database = HostModel.fetch_one(id=host_id)
            if not self.database or not credential_host:
                self.close_connect(WebSocketStatusCode.PARAM_ERROR)
            if self.database.resource_type != HostModel.RESOURCE_DATABASE:
                self.close_connect(WebSocketStatusCode.HOST_TYPE_ERROR)
            command = self._create_databases_link(credential_host.credential, self.database, password, timeout)
        else:
            command = self._create_cache_databases_link(data, timeout)
        return command

    def create_session_log(self, data):
        try:
            query_string = self.scope['query_string'].decode()
            query_dict = dict([x.split('=', 1) for x in query_string.split('&')])
            width = int(float(query_dict["width"]))
            height = int(float(query_dict["height"]))
        except:
            width = 175
            height = 55
        """
        根据Token获取的缓存数据记录登陆日志
        """
        log_name = str(uuid.uuid4())
        if not data.get("cache"):
            try:
                login_name = HostCredentialRelationshipModel.fetch_one(
                    id=data.get("credential_host_id")).credential.login_name
            except Exception as e:
                app_logging.error("[ERROR] Ws api error, get credential error: {}".format(str(e)))
                login_name = "root"
            session_log = SessionLogModel.create(**{
                "host_id": data.get("host_id"),
                "channel": self.channel_name,
                "host_name": self.database.host_name,
                "system_type": self.database.system_type,
                "host_address": self.database.host_address,
                "protocol_type": self.database.protocol_type,
                "login_type": 1,
                "port": self.database.port,
                "login_name": login_name,
                "log_name": log_name,
                "user": self.user.username,
                "width": width,
                "height": height
            })
        else:
            session_log = SessionLogModel.create(**{
                "channel": self.channel_name,
                "host_name": data.get("host_info").get("host_name"),
                "system_type": data.get("host_info").get("system_type"),
                "host_address": data.get("host_info").get("ip"),
                "protocol_type": "ssh",
                "login_type": 1,
                "port": data.get("host_info").get("port"),
                "login_name": data.get("host_info").get("username", ""),
                "log_name": log_name,
                "user": self.user.username,
                "width": width,
                "height": height
            })
        return session_log

    def start_ssh(self, command):
        chan = self.ssh.invoke_shell(width=self.session_log.width, height=self.session_log.height, term='xterm')
        chan.send(command + "\n")
        res = chan.recv(1024)
        sshterminal = SshTerminalThread(self, chan, self.user.username, self.token,
                                        ssh_type=self.database.resource_type)
        sshterminal.setDaemon = True
        sshterminal.start()
        log_name = self.session_log.log_name + '.log'
        interactivessh = InterActiveShellThread(chan, self, log_name=log_name, width=self.session_log.width,
                                                height=self.session_log.height,
                                                database_client=command)
        interactivessh.setDaemon = True
        interactivessh.start()

    def connect(self):
        self.wait_time = time.time()
        self.accept()
        # 验证token
        status, code, data = self.check_token()
        if not status and status is not None:
            self.close_connect(code)
        try:
            command = self.create_database_link(data)
        except Exception as e:
            app_logging.error("[ERROR] Create database link error: {}".format(str(e)))
            command = ""
            self.close_connect(WebSocketStatusCode.SSH_CHECK_ERROR)
        self.session_log = self.create_session_log(data)
        self.start_ssh(command)

    def disconnect(self, close_code):
        self.close_ssh()
        time.sleep(0.5)
        try:
            self.session_log.update(**{
                "is_finished": True,
                "end_time": datetime.datetime.now()
            })
        except Exception as e:
            app_logging.error("[ERROR] Update Session Log error: {}, param: {}".format(str(e), str(self.session_log)))
        self.close()

    def close_ssh(self):
        self.queue.publish(self.channel_name, json.dumps(['close']))

    @property
    def queue(self):
        queue = SSHBaseComponent().get_redis_instance()
        queue.pubsub()
        return queue

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        status, code, data = self.check_token()
        if not status and status is not None:
            self.close_connect(code)
        try:
            if text_data is not None:  # 普通命令执行
                self.queue.publish(self.channel_name, text_data)
            if bytes_data:  # RZ SZ
                self.queue.publish(self.channel_name, bytes_data)
        except socket.error:
            self.disconnect(1000)
            return
        except ValueError:
            if self.first_flag:
                self.first_flag = False
            self.queue.publish(self.channel_name, smart_unicode(text_data))
        except Exception as e:
            self.disconnect(1000)
            return
