import contextlib
import paramiko
import time
import json
import logging
import uuid
import datetime
import io
import socket
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection
from paramiko.ssh_exception import NoValidConnectionsError

from bastion.component.redis_client_conn import get_redis_dict_data

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

from bastion.core.terminal.component import SSHBaseComponent
from bastion.core.status_code import WebSocketStatusCode
from bastion.component.core import CheckUserHostComponent
from bastion.component.common import GetUserInfo
from bastion.models import HostModel, CredentialModel, SessionLogModel, HostCredentialRelationshipModel, \
    NetworkProxyModel
from bastion.core.terminal.component import SshTerminalThread, InterActiveShellThread
from bastion.utils.encryption import PasswordEncryption

app_logging = logging.getLogger("app")


class WebSSH(WebsocketConsumer):
    ssh = None
    http_user = True
    channel_session = False
    channel_session_user = False
    first_flag = True
    wait_time = time.time()
    user = None
    cache = get_redis_connection("cache")
    token = ""
    link_config = {}
    host = None
    session_log = None
    stop_key = ""

    # 从ws接口中获取cookies内用户信息
    def get_user_query(self):
        user = GetUserInfo().get_user_info(bk_token=self.scope.get("cookies").get("bk_token"))
        return user

    # 从ws接口中获取cookies
    def get_cookie(self):
        cookie = {}
        cookies = next((header[1].decode() for header in self.scope['headers'] if header[0] == b'cookie'), None)

        if cookies:
            cookie = dict([cookie.split('=', 1) for cookie in cookies.split('&')])
        return cookie

    # 处理ws接口上参数
    def get_request_param_dict(self):
        query_string = self.scope.get("query_string").decode()
        request_param = dict([x.split('=', 1) for x in query_string.split('&')])
        return request_param

    # 校验用户信息-登录用户是否与连接(登录前缓存用户主机相关信息)用户相同
    def check_link_user(self, user_id):
        self.user = self.get_user_query()
        if self.user:
            try:
                if self.user.id == user_id:
                    return True
                return False
            except Exception as e:
                app_logging.error("[ERROR] SSH web socket, check_link_user error: {}, param: {}".format(str(e), str(user_id)))
                return False
        return False

    # 获取登录前缓存的登录信息
    def get_link_config(self, token):
        try:
            if not self.link_config:
                self.link_config = get_redis_dict_data(self.cache, token)
            return True, self.link_config
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, get_link_config error: {}, param: {}".format(str(e), str(token)[:5]))
            return False, {}

    # 缓存中数据校验权限策略
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

    #校验token的可用性，用户是否管理员或外部登录，
    def check_token(self, check_user=False):
        request_param = self.get_request_param_dict()
        if not self.token:
            if request_param.get("token"):
                self.token = request_param.get("token")
            else:
                self.token = self.get_cookie().get("link_token")
        status, data = self.get_link_config(self.token)
        if status:
            if not check_user:
                status = self.check_link_user(data.get("user_id"))
            else:
                status = True
            if status:
                if data.get("admin") or data.get("cache"):
                    return None, "", data
                status = self.check_link_time(data)
                if status:
                    return True, "", data
                return False, WebSocketStatusCode.ACCESS_ERROR, {}
            return False, WebSocketStatusCode.USER_ERROR, {}
        return False, WebSocketStatusCode.PARAM_ERROR, {}

    def close_connect(self, text):
        try:
            self.send(text_data=str(text))
            self.close()
        except Exception as e:
            pass
        return

    # 创建会话
    def create_session_log(self, data):
        # sourcery skip: lift-return-into-if, remove-unnecessary-else, swap-if-else-branches
        try:
            query_string = self.scope['query_string'].decode()
            query_dict = dict([x.split('=', 1) for x in query_string.split('&')])
            width = int(float(query_dict["width"]))
            height = int(float(query_dict["height"]))
        except Exception:
            width = 175
            height = 55
        """
        根据Token获取的缓存数据记录登陆日志
        """
        log_name = str(uuid.uuid4())
        if not data.get("cache"):
            try:
                login_name = HostCredentialRelationshipModel.fetch_one(id=data.get("credential_host_id")).credential.login_name
            except Exception as e:
                app_logging.error("[ERROR] Ws api error, get credential error: {}".format(str(e)))
                login_name = "root"
            session_log = SessionLogModel.create(**{
                "host_id": data.get("host_id"),
                "channel": self.channel_name,
                "host_name": self.host.host_name,
                "system_type": self.host.system_type,
                "host_address": self.host.host_address,
                "protocol_type": self.host.protocol_type,
                "login_type": 1,
                "port": self.host.port,
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

    # 通过密码连接
    def client_ssh_by_password(self, ip, port, username, password, sock=None):
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # self.ssh.load_system_host_keys()
            self.ssh.connect(hostname=ip, port=port, username=username, password=password, sock=sock, timeout=3)
            return True, ""
        except socket.timeout:
            return False, WebSocketStatusCode.TIME_OUT
        except NoValidConnectionsError as e:
            app_logging.error("[ERROR] SSH web socket NoValidConnectionsError, client_ssh_by_password error: {}, param: {}".format(str(e), str([ip, port])))
            return False, WebSocketStatusCode.SSH_CHECK_ERROR
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, client_ssh_by_password error: {}, param: {}".format(str(e), str([ip, port])))
            return False, WebSocketStatusCode.SSH_CHECK_ERROR

    # 通过key登录
    def client_ssh_by_ssh_key(self, ip, port, login_name, ssh_key, passphrase, sock=None):
        """
        创建秘钥登陆SSH连接
        """
        app_logging.error("[INFO]:{}".format(str([ip, port, login_name, ssh_key, passphrase])))
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            io_pri_key = io.StringIO(ssh_key)
            pri_key = paramiko.RSAKey.from_private_key(io_pri_key, password=passphrase)
            self.ssh.connect(hostname=ip, port=port, username=login_name, pkey=pri_key, timeout=3, sock=sock)
            return True, ""
        except socket.timeout:
            return False, WebSocketStatusCode.TIME_OUT
        except NoValidConnectionsError as e:
            app_logging.error("[ERROR] SSH web socket NoValidConnectionsError, client_ssh_by_password error: {}, param: {}".format(str(e), str([ip, port])))
            return False, WebSocketStatusCode.SSH_CHECK_ERROR
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, client_ssh_by_ssh_key error: {}, param: {}".format(
                    str(e), str([ip, port, login_name, ssh_key, passphrase])
            ))
            return False, WebSocketStatusCode.SSH_CHECK_ERROR
            # return False, str(e)

    def get_password(self, password):
        """
        密码解密
        """
        try:
            password = PasswordEncryption().decrypt(password)
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, get_password error: {}".format(str(e)))
            password = ""
        return password

    # 通代理密码连接
    def create_proxy_sock_by_password(self, ip, port, username, password, host_ip, host_port):
        """
        通过密码创建代理连接
        """
        try:
            proxy = paramiko.SSHClient()
            proxy.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            proxy.connect(hostname=ip, port=port, username=username, password=self.get_password(password))
            sock = proxy.get_transport().open_channel('direct-tcpip', (host_ip, host_port), (ip, 0))
            return True, sock
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, create_proxy_sock_by_password error: {}, param: {}".format(str(e), str(ip)))
            return False, None

    # 通过代理key连接
    def create_proxy_sock_by_ssh_key(self, ip, port, username, ssh_key, passphrase, host_ip, host_port):
        """
        通过key创建代理连接
        """
        try:
            proxy = paramiko.SSHClient()
            proxy.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            io_pri_key = io.StringIO(ssh_key)
            pri_key = paramiko.RSAKey.from_private_key(io_pri_key, password=self.get_password(passphrase))
            proxy.connect(hostname=ip, port=port, username=username, pkey=pri_key)
            sock = proxy.get_transport().open_channel('direct-tcpip', (host_ip, host_port), (ip, 0))
            return True, sock
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, create_proxy_sock_by_ssh_key error: {}, param: {}".format(
                    str(e), str(ip)
            ))
            return False, None

    # 创建本地登录SSH连接
    def _create_ssh_link(self, credential, host, password):
        """
        创建SSH连接
        """
        network_proxy = host.network_proxy
        sock = None
        if network_proxy:
            if network_proxy.credential_type == network_proxy.CREDENTIAL_PASSWORD:
                status, sock = self.create_proxy_sock_by_password(
                        network_proxy.linux_ip,
                        network_proxy.linux_port,
                        network_proxy.linux_login_name,
                        network_proxy.linux_login_password,
                        self.host.host_address,
                        self.host.port
                    )
            else:
                status, sock = self.create_proxy_sock_by_ssh_key(
                        network_proxy.linux_ip,
                        network_proxy.linux_port,
                        network_proxy.linux_login_name,
                        network_proxy.ssh_key,
                        network_proxy.passphrase,
                        self.host.host_address,
                        self.host.port
                    )
            if not status:
                return False, WebSocketStatusCode.PROXY_LINK_ERROR
        if credential.login_type == CredentialModel.LOGIN_AUTO:
            if credential.credential_type == CredentialModel.CREDENTIAL_PASSWORD:
                password = self.get_password(credential.login_password)
                login_name = credential.login_name
                status, code = self.client_ssh_by_password(host.host_address, host.port, login_name, password, sock)
            else:
                password = credential.passphrase
                ssh_key = credential.ssh_key
                login_name = credential.login_name
                status, code = self.client_ssh_by_ssh_key(host.host_address, host.port, login_name, ssh_key, password, sock)
        else:
            login_name = credential.login_name
            if credential.credential_type == CredentialModel.CREDENTIAL_PASSWORD:
                status, code = self.client_ssh_by_password(host.host_address, host.port, login_name, password, sock)
            else:
                ssh_key = credential.ssh_key
                status, code = self.client_ssh_by_ssh_key(host.host_address, host.port, login_name, ssh_key, password, sock)
        if not status:
            return False, code
        return True, ""

    # 创建外部登录SSH连接
    def _create_cache_ssh_link(self, token_data):
        """
        创建SSH连接
        """
        host_info = token_data.get("host_info")
        network_proxy_id = host_info.get("network_proxy")
        ip = host_info.get("ip")
        port = host_info.get("port")
        username = host_info.get("username", "root")
        ssh_key = host_info.get("ssh_key")
        password = host_info.get("password")
        sock = None
        # app_logging.info("network_proxy_id--" + str(network_proxy_id))
        if network_proxy_id:  # 使用代理登录
            try: network_proxy_id = int(network_proxy_id)
            except: return False, WebSocketStatusCode.PROXY_LINK_ERROR
            network_proxy = NetworkProxyModel.fetch_one(id=network_proxy_id)
            # app_logging.info("network_proxy--" + str(network_proxy))

            if not network_proxy:
                return False, WebSocketStatusCode.PROXY_LINK_ERROR
            if network_proxy.credential_type == network_proxy.CREDENTIAL_PASSWORD:
                status, sock = self.create_proxy_sock_by_password(
                        network_proxy.linux_ip,
                        network_proxy.linux_port,
                        network_proxy.linux_login_name,
                        network_proxy.linux_login_password,
                        ip,
                        port
                    )
            else:
                status, sock = self.create_proxy_sock_by_ssh_key(
                        network_proxy.linux_ip,
                        network_proxy.linux_port,
                        network_proxy.linux_login_name,
                        network_proxy.ssh_key,
                        network_proxy.passphrase,
                        ip,
                        port
                    )
            if not status:
                return False, WebSocketStatusCode.PROXY_LINK_ERROR
        # app_logging.info(sock)

        if token_data.get("login_type") == "password":
            status, code = self.client_ssh_by_password(ip, port, username, password, sock)
        else:
            status, code = self.client_ssh_by_ssh_key(ip, port, username, ssh_key, password, sock)
        if not status:
            return False, code
        return True, ""

    # 创建SSH连接入口
    def create_ssh_link(self, data):
        """
        校验数据以及创建SSH连接
        """
        # app_logging.info(str(data))
        if not data.get("cache"):
            host_id = data.get("host_id")
            credential_host_id = data.get("credential_host_id")
            password = data.get("password")
            credential_host = HostCredentialRelationshipModel.fetch_one(id=credential_host_id)
            self.host = HostModel.fetch_one(id=host_id)
            if not self.host or not credential_host:
                self.close_connect(WebSocketStatusCode.PARAM_ERROR)
            if self.host.system_type != HostModel.SYSTEM_LINUX:
                self.close_connect(WebSocketStatusCode.HOST_TYPE_ERROR)
            status, code = self._create_ssh_link(credential_host.credential, self.host, password)
        else:
            status, code = self._create_cache_ssh_link(data)

        if not status:
            return False, code
        return True, ""

    def connect(self):
        self.wait_time = time.time()
        self.accept()
        # 验证token
        self.ssh = paramiko.SSHClient()
        status, code, data = self.check_token()
        if not status and status is not None:
            self.close_connect(code)
        try:
            status, code = self.create_ssh_link(data)
            if status:
                self.session_log = self.create_session_log(data)
                self.start_ssh()
            else:
                self.close_connect(code)
                return
        except Exception as e:
            app_logging.error("[ERROR] Create ssh link error: {}".format(str(e)))
            self.close_connect(WebSocketStatusCode.SSH_LINK_ERROR)
            return

    # SSH开始工作，进入两个线程
    # SshTerminalThread
    # InterActiveShellThread
    def start_ssh(self):
        chan = self.ssh.invoke_shell(width=self.session_log.width, height=self.session_log.height, term='xterm')
        sshterminal = SshTerminalThread(self, chan, self.user.username, self.token)
        # sshterminal.setDaemon = True
        sshterminal.start()
        log_name = self.session_log.log_name + '.log'
        self.stop_key = str(uuid.uuid4())
        interactivessh = InterActiveShellThread(chan, self, log_name=log_name, width=self.session_log.width,
                                                    height=self.session_log.height, stop_key=self.stop_key)
        # interactivessh.setDaemon = True
        interactivessh.start()

    def disconnect(self, close_code):
        self.close_ssh()
        time.sleep(0.5)
        try:
            if self.session_log:
                self.session_log.update(**{
                    "is_finished": True,
                    "end_time": datetime.datetime.now()
                })
        except Exception as e:
            app_logging.error("[ERROR] Update Session Log error: {}, param: {}".format(str(e), str(self.session_log)))
        with contextlib.suppress(Exception):
            self.close()

    def close_ssh(self):
        self.queue.publish(self.channel_name, json.dumps(['close']))
        redis_client = get_redis_connection("cache")
        redis_client.set(self.stop_key, "true")
        redis_client.expire(self.stop_key, 10)
        time.sleep(2)

    @property
    def queue(self):
        queue = SSHBaseComponent().get_redis_instance()
        queue.pubsub()
        return queue

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            status, code, data = self.check_token(check_user=True)
            if not status and status is not None:
                self.close_connect(code)
                return
            if text_data is not None:           # 普通命令执行
                self.queue.publish(self.channel_name, text_data)
            if bytes_data:                       # RZ SZ
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

