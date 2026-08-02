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

from bastion.component.redis_client_conn import get_redis_dict_data

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_str as smart_unicode

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
    http_user = True
    channel_session = False
    channel_session_user = False
    cache = get_redis_connection("cache")
    _redis_instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh = None
        self.proxy_ssh = None  # 记录代理SSH连接，用于清理
        self.first_flag = True
        self.wait_time = time.time()
        self.user = None
        self.token = ""
        self.link_config = {}
        self.host = None
        self.session_log = None
        self.stop_key = ""
        self.chan = None  # SSH channel
        self._ssh_terminal = None  # 持有 SshTerminalThread 引用，disconnect 时显式释放
        self._interactive_shell = None  # 持有 InterActiveShellThread 引用

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
                self.link_config = get_redis_dict_data("cache", token)
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
        if status and data:
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
        根据Token获取的缓存数据记录登录日志
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
                "protocol_type": "SSH",
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
    def client_ssh_by_password(self, ip, port, username, password, sock=None, timeout=5):
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # self.ssh.load_system_host_keys()
            self.ssh.connect(hostname=ip, port=port, username=username, password=password, sock=sock, timeout=timeout)
            return True, ""
        except socket.timeout:
            return False, WebSocketStatusCode.TIME_OUT
        except paramiko.ssh_exception.AuthenticationException as e:
            return False, WebSocketStatusCode.SSH_AUTH_FAILED_ERROR
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            self._tmp_log("client_ssh_by_password", f"{username}@{ip}:{port} NoValidConnectionsError {e}\n")
            return False, WebSocketStatusCode.TARGET_HOST_RESET_PEER_ERROR
        except paramiko.ssh_exception.SSHException as e:
            self._tmp_log("client_ssh_by_password", f"{username}@{ip}:{port} SSHException {e}\n")
            if "Connection reset by peer" in str(e):
                return False, WebSocketStatusCode.TARGET_HOST_RESET_PEER_ERROR
            return False, WebSocketStatusCode.TARGET_HOST_SSH_ERROR
        except Exception as e:
            self._tmp_log("client_ssh_by_password", f"{username}@{ip}:{port} Exception {e}\n")
            return False, WebSocketStatusCode.TARGET_HOST_SSH_ERROR

    def _tmp_log(self, name, error):
        tmp = f"/tmp/{name}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(tmp, "a") as f:
            f.write(f"[SSH-ERROR]: {error}")

    # 通过key登录
    def client_ssh_by_ssh_key(self, ip, port, login_name, ssh_key, passphrase, sock=None, timeout=5):
        """
        创建秘钥登录SSH连接
        """
        app_logging.error("[INFO]:{}".format(str([ip, port, login_name, ssh_key, passphrase])))
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            io_pri_key = io.StringIO(ssh_key)
            pri_key = paramiko.RSAKey.from_private_key(io_pri_key, password=passphrase)
            self.ssh.connect(hostname=ip, port=port, username=login_name, pkey=pri_key, timeout=timeout, sock=sock)
            # /usr/local/lib/python3.7/site-packages/paramiko/transport.py +757
            # self.server_extensions = {"server-sig-algs": "ssh-rsa"}
            # t = paramiko.Transport(sock)
            # if hasattr(t, 'server_extensions'):
            #     t.server_extensions = {'server-sig-algs': 'ssh-rsa'}
            return True, ""
        except socket.timeout:
            return False, WebSocketStatusCode.TIME_OUT
        except paramiko.ssh_exception.AuthenticationException as e:
            return False, WebSocketStatusCode.SSH_AUTH_FAILED_ERROR
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            self._tmp_log("client_ssh_by_ssh_key", f"{login_name}@{ip}:{port} NoValidConnectionsError {e}\n")
            return False, WebSocketStatusCode.TARGET_HOST_RESET_PEER_ERROR
        except paramiko.ssh_exception.SSHException as e:
            self._tmp_log("client_ssh_by_ssh_key", f"{login_name}@{ip}:{port} SSHException {e}\n")
            if "Connection reset by peer" in str(e):
                return False, WebSocketStatusCode.TARGET_HOST_RESET_PEER_ERROR
            return False, WebSocketStatusCode.TARGET_HOST_SSH_ERROR
        except Exception as e:
            self._tmp_log("client_ssh_by_ssh_key", f"{login_name}@{ip}:{port} Exception {e}\n")
            return False, WebSocketStatusCode.TARGET_HOST_SSH_ERROR

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
    def create_proxy_sock_by_password(self, ip, port, username, password, host_ip, host_port, timeout=5):
        """
        通过密码创建代理连接
        """
        try:
            self.proxy_ssh = paramiko.SSHClient()
            self.proxy_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.proxy_ssh.connect(hostname=ip, port=port, username=username, password=self.get_password(password), timeout=timeout)
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, create_proxy_sock_by_password error: {}, param: {}".format(str(e), str(ip)))
            return False, 9
        try:
            sock = self.proxy_ssh.get_transport().open_channel('direct-tcpip', (host_ip, host_port), (ip, 0))
            return True, sock
        except Exception as e:
            return False, 10

    # 通过代理key连接
    def create_proxy_sock_by_ssh_key(self, ip, port, username, ssh_key, passphrase, host_ip, host_port, timeout=5):
        """
        通过key创建代理连接
        """
        try:
            self.proxy_ssh = paramiko.SSHClient()
            self.proxy_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            io_pri_key = io.StringIO(ssh_key)
            pri_key = paramiko.RSAKey.from_private_key(io_pri_key, password=self.get_password(passphrase))
            self.proxy_ssh.connect(hostname=ip, port=port, username=username, pkey=pri_key, timeout=timeout)
        except Exception as e:
            app_logging.error("[ERROR] SSH web socket, create_proxy_sock_by_ssh_key error: {}".format(str(e)))
            return False, 9
        try:
            sock = self.proxy_ssh.get_transport().open_channel('direct-tcpip', (host_ip, host_port), (ip, 0))
            return True, sock
        except Exception as e:
            return False, 10

    # 创建本地登录SSH连接
    def _create_ssh_link(self, credential, host, password, timeout=5):
        """
        创建SSH连接
        """
        network_proxy = host.network_proxy
        sock = None
        if network_proxy:
            try:
                linux_timeout = network_proxy.linux_timeout or 5
            except Exception:
                linux_timeout = 5
            if network_proxy.credential_type == network_proxy.CREDENTIAL_PASSWORD:
                status, sock = self.create_proxy_sock_by_password(
                    network_proxy.linux_ip, network_proxy.linux_port,
                    network_proxy.linux_login_name, network_proxy.linux_login_password,
                    self.host.host_address, self.host.port, linux_timeout
                )
            else:
                status, sock = self.create_proxy_sock_by_ssh_key(
                    network_proxy.linux_ip, network_proxy.linux_port,
                    network_proxy.linux_login_name, network_proxy.ssh_key,
                    network_proxy.passphrase, self.host.host_address,
                    self.host.port, linux_timeout
                )
            if not status:
                if sock == 9:
                    return False, WebSocketStatusCode.PROXY_LINK_ERROR
                else:
                    return False, WebSocketStatusCode.SSH_LINK_ERROR
        if credential.login_type == CredentialModel.LOGIN_AUTO:
            if credential.credential_type == CredentialModel.CREDENTIAL_PASSWORD:
                password = self.get_password(credential.login_password)
                login_name = credential.login_name
                status, code = self.client_ssh_by_password(host.host_address, host.port, login_name, password, sock, timeout)
            else:
                password = self.get_password(credential.passphrase)
                ssh_key = credential.ssh_key
                login_name = credential.login_name
                status, code = self.client_ssh_by_ssh_key(host.host_address, host.port, login_name, ssh_key, password, sock, timeout)
        else:
            login_name = credential.login_name
            if credential.credential_type == CredentialModel.CREDENTIAL_PASSWORD:
                status, code = self.client_ssh_by_password(host.host_address, host.port, login_name, password, sock, timeout)
            else:
                ssh_key = credential.ssh_key
                status, code = self.client_ssh_by_ssh_key(host.host_address, host.port, login_name, ssh_key, password, sock, timeout)
        if not status:
            return False, code
        return True, ""

    # 创建外部登录SSH连接
    def _create_cache_ssh_link(self, token_data, timeout=5):
        host_info = token_data.get("host_info")
        network_proxy_id = host_info.get("network_proxy")
        ip = host_info.get("ip")
        port = host_info.get("port")
        username = host_info.get("username", "root")
        ssh_key = host_info.get("ssh_key")
        password = host_info.get("password")
        sock = None
        if network_proxy_id:  # 使用代理登录
            try:
                network_proxy_id = int(network_proxy_id)
            except Exception:
                return False, WebSocketStatusCode.PROXY_LINK_ERROR
            network_proxy = NetworkProxyModel.fetch_one(id=network_proxy_id)
            if not network_proxy:
                return False, WebSocketStatusCode.PROXY_LINK_ERROR
            try:
                linux_timeout = network_proxy.linux_timeout or 5
            except Exception:
                linux_timeout = 5
            if network_proxy.credential_type == network_proxy.CREDENTIAL_PASSWORD:
                status, sock = self.create_proxy_sock_by_password(
                    network_proxy.linux_ip, network_proxy.linux_port,
                    network_proxy.linux_login_name, network_proxy.linux_login_password,
                    ip, port, linux_timeout
                )
            else:
                status, sock = self.create_proxy_sock_by_ssh_key(
                    network_proxy.linux_ip, network_proxy.linux_port,
                    network_proxy.linux_login_name, network_proxy.ssh_key,
                    network_proxy.passphrase, ip, port, linux_timeout
                )
            if not status:
                if sock == 9:
                    return False, WebSocketStatusCode.PROXY_LINK_ERROR
                else:
                    return False, WebSocketStatusCode.SSH_LINK_ERROR
        # 缓存模式：直接使用 host_info 凭据（修复：原代码引用未定义的 credential_host）
        if token_data.get("login_type") == "password":
            status, code = self.client_ssh_by_password(ip, port, username, password, sock, timeout=timeout)
        else:
            status, code = self.client_ssh_by_ssh_key(ip, port, username, ssh_key, password, sock, timeout=timeout)
        if not status:
            return False, code
        return True, ""

    # 创建SSH连接入口
    def create_ssh_link(self, data):
        """
        校验数据以及创建SSH连接
        """
        try:
            timeout = int(data.get("timeout", 5))
        except Exception:
            timeout = 5
        if not data.get("cache"):
            host_id = data.get("host_id")
            credential_host_id = data.get("credential_host_id")
            password = data.get("password")
            credential_host = HostCredentialRelationshipModel.fetch_one(id=credential_host_id)
            self.host = HostModel.fetch_one(id=host_id)
            if not self.host:
                return False, WebSocketStatusCode.PARAM_ERROR
            if not credential_host:
                return False, WebSocketStatusCode.PARAM_ERROR
            if self.host.system_type != HostModel.SYSTEM_LINUX:
                return False, WebSocketStatusCode.HOST_TYPE_ERROR
            status, code = self._create_ssh_link(credential_host.credential, self.host, password, timeout=timeout)
        else:
            status, code = self._create_cache_ssh_link(data, timeout)
        if not status:
            return False, code
        return True, ""

    def connect(self):
        self.wait_time = time.time()
        self.accept()
        # print("self.accept()")
        # 验证token
        self.ssh = paramiko.SSHClient()
        status, code, data = self.check_token()
        # print("3.status=%s, code=%s, data_keys=%s", status, code, list(data.keys()) if data else None)
        if status in [False]:
            self.close_connect(code)
            return
        try:
            status, code = self.create_ssh_link(data)
            # print("4.status, code", status, code, flush=True)
            if status:
                self.session_log = self.create_session_log(data)
                self.start_ssh()
            else:
                self.close_connect(code)
                return
        except ImportError as e:
            app_logging.error("[ERROR] Create ssh link error: {}".format(str(e)))
            self.close_connect(WebSocketStatusCode.SSH_LINK_ERROR)
            return

    # SSH开始工作，进入两个线程
    # SshTerminalThread
    # InterActiveShellThread
    def start_ssh(self):
        self.chan = self.ssh.invoke_shell(width=self.session_log.width, height=self.session_log.height, term='xterm')
        sshterminal = SshTerminalThread(self, self.chan, self.user.username, self.token)
        sshterminal.start()
        self._ssh_terminal = sshterminal  # 保存引用以便 disconnect 时显式清理
        log_name = self.session_log.log_name + '.log'
        self.stop_key = str(uuid.uuid4())
        interactivessh = InterActiveShellThread(self.chan, self, log_name=log_name, width=self.session_log.width,
                                                    height=self.session_log.height, stop_key=self.stop_key)
        interactivessh.start()
        self._interactive_shell = interactivessh  # 保存引用以便 disconnect 时显式清理

    def disconnect(self, close_code):
        # 1. 设置停止标志（让线程知晓）
        redis_client = get_redis_connection("cache")
        if self.stop_key:
            try:
                redis_client.set(self.stop_key, "true")
                redis_client.expire(self.stop_key, 10)
            except Exception:
                pass
        # 2. 停止 SshTerminalThread（设置 event）
        if self._ssh_terminal:
            try:
                self._ssh_terminal.stop()
            except Exception:
                pass
        # 3. 发送 Redis 消息（如果队列可用）
        try:
            self.queue.publish(self.channel_name, json.dumps(['close']))
        except Exception:
            pass
        # 4. **强制关闭 SSH 连接（先于线程 join）**
        self.close_ssh()  # 现在会强制 shutdown socket

        # 5. 等待线程退出（缩短超时，因为 socket 已中断）
        if self._ssh_terminal:
            try:
                self._ssh_terminal.join(timeout=1)  # 原为3秒，可缩短
            except Exception:
                pass
        if self._interactive_shell:
            try:
                self._interactive_shell.join(timeout=1)
            except Exception:
                pass
        # 6. 更新会话日志
        try:
            if self.session_log:
                self.session_log.update(**{
                    "is_finished": True,
                    "end_time": datetime.datetime.now()
                })
        except Exception as e:
            app_logging.error("[ERROR] Update Session Log error: %s", e)
        # 7. 释放引用，辅助 GC
        self._ssh_terminal = None
        self._interactive_shell = None
        # 8. 关闭 WebSocket
        with contextlib.suppress(Exception):
            self.close()

    def close_ssh(self):
        # ① 关闭 channel（先尝试优雅关闭，但不依赖）
        if self.chan:
            try:
                self.chan.shutdown_write()
                self.chan.close()
            except Exception:
                pass
            self.chan = None
        # ② 关闭主 SSH 连接（强制底层 socket）
        if self.ssh:
            try:
                transport = self.ssh.get_transport()
                if transport:
                    # 强制关闭 socket，使所有阻塞的 recv/select 立即抛出异常
                    sock = transport.sock
                    if sock:
                        try:
                            sock.shutdown(socket.SHUT_RDWR)
                        except Exception:
                            pass
                        try:
                            sock.close()
                        except Exception:
                            pass
                    # 关闭 transport
                    transport.close()
            except Exception:
                pass
            # 最后再调用 close 确保资源释放
            try:
                self.ssh.close()
            except Exception:
                pass
            self.ssh = None
        # ③ 关闭代理 SSH（同样强制）
        if self.proxy_ssh:
            try:
                transport = self.proxy_ssh.get_transport()
                if transport:
                    sock = transport.sock
                    if sock:
                        try:
                            sock.shutdown(socket.SHUT_RDWR)
                        except Exception:
                            pass
                        try:
                            sock.close()
                        except Exception:
                            pass
                    transport.close()
            except Exception:
                pass
            try:
                self.proxy_ssh.close()
            except Exception:
                pass
            self.proxy_ssh = None

    @property
    def queue(self):
        if self._redis_instance is None:
            self._redis_instance = SSHBaseComponent().get_redis_instance()
        return self._redis_instance

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            status, code, data = self.check_token(check_user=True)
            if status in [False]:
                self.close_connect(code)
                return
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
