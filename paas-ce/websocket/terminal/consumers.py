# -*- coding:utf-8 -*-
from channels.generic.websocket import WebsocketConsumer
from django.utils.timezone import now
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

import time
import socket
import uuid
import traceback
import json
import paramiko
import io

from terminal.models import SessionLog
from .utils import get_redis_instance, SshTerminalThread, InterActiveShellThread, channel_layer
from control.models import AgentAdmin
from control.utils.esb_api import EsbApi
from control.utils.encryption import PasswordEncryption


# for webterminal 
class WebSSH(WebsocketConsumer):
    ssh = paramiko.SSHClient()
    http_user = True
    channel_session = True
    channel_session_user = True
    first_flag = True

    def get_cookie(self):
        cookie = None
        for a in self.scope['headers']:
            if a[0] == b'cookie':
                cookie = a[1].decode()
                break
        if cookie:
            cookie = dict([x.split('=',1) for x in cookie.split('&')])
        return cookie

    def close_connect(self, text):
        self.send(text_data=text)
        self.close()
        return

    def connect(self, *args, **kwargs):
        self.wait_time = time.time()
        self.accept()
        # self.opt_username = self.get_user(self.scope)
        token = self.scope.get('cookies').get("bk_token")
        bk_user = EsbApi(token).get_user_info()  # 获取当前用户
        self.opt_username = bk_user.get("username")
        self.protocol = None
        self.server_id = self.scope['url_route']['kwargs'].get('server_id')
        query_string = self.scope['query_string'].decode()
        if query_string:
            query_dict = dict([x.split('=',1) for x in query_string.split('&')])
            width = int(float(query_dict["width"]))
            height = int(float(query_dict["height"]))
            password = None
            pri_key = None
            ssh_key_id = None
            session_uuid = None
            # if query_dict.get("ip"):
            #     self.hostname = query_dict["ip"]
            #     port = query_dict.get("port")
            #     self.username = query_dict.get("username")
            #     system_type = query_dict.get("system_type")
            #     session_uuid = query_dict.get("session_uuid")
            #     ssh_key_id = query_dict.get("ssh_key")
            #     password = query_dict.get("password")
            if self.server_id:
                if AgentAdmin.objects.filter(id=self.server_id).count() == 0:
                    self.close_connect("{'opsany_ssh_error':'主机不存在!'}")
                else:
                    session_uuid = query_dict.get("session_uuid")
                    host_obj = AgentAdmin.objects.get(id=int(self.server_id))
                    system_type = host_obj.system_type
                    ssh_key_id = host_obj.ssh_key_id
                    self.hostname = host_obj.ip
                    port = host_obj.ssh_port
                    self.username = host_obj.username
                    password = PasswordEncryption().decrypt(host_obj.password) if host_obj.password and host_obj.ssh_type == "password" else ""
            else:
                self.close_connect("{'opsany_ssh_error':'请添加主机信息'}")
            if system_type.strip() == "Linux":
                self.protocol = "ssh"
            else:
                self.close_connect("{'opsany_ssh_error':'system_type必须为Linux!'}")
            try:
                if ssh_key_id:
                    cookies = self.scope["cookies"]
                    if not cookies or not cookies.get("bk_token"):
                        self.close_connect("{'opsany_ssh_error':'未找到cookie或bk_token!'}")
                    bk_token = cookies.get("bk_token")
                    esb_obj = EsbApi(bk_token)
                    res = esb_obj.get_user_ssh_key(str(ssh_key_id))
                    if not res:
                        self.close_connect("{'opsany_ssh_error':'无法获取到ssh_key!'}")
                    pri_key_ = res.get('private_key')
                    pri_key = io.StringIO(pri_key_)
                    pri_key = paramiko.RSAKey.from_private_key(pri_key)
                if not (pri_key or password):
                    self.close_connect("{'opsany_ssh_error':'请提供登录验证密码或秘钥!'}")
                if session_uuid:
                    log_name = session_uuid
                else:
                    log_name = str(uuid.uuid4())
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(
                        self.hostname,
                        port=port,
                        username=self.username,
                        password=password,
                        pkey=pri_key,
                        timeout=3
                )
                self.session_log = SessionLog.objects.create(user=self.opt_username, server=host_obj, channel=self.channel_name,
                                        log_name=log_name)
            except socket.timeout:
                self.close_connect("{'opsany_ssh_error':'连接服务器超时!'}")
            except Exception as e:
                self.close_connect("{'opsany_ssh_error':'SSH验证失败!'}")
            chan = self.ssh.invoke_shell(width=width, height=height, term='xterm')
            sshterminal = SshTerminalThread(self, chan, self.opt_username)
            sshterminal.setDaemon = True
            sshterminal.start()
            log_name = log_name + '.log'
            interactivessh = InterActiveShellThread(chan, self, log_name=log_name, width=width, height=height)
            interactivessh.setDaemon = True
            interactivessh.start()

    def disconnect(self, close_code):
        self.closessh()
        time.sleep(3)
        audit_log = SessionLog.objects.filter(channel=self.channel_name)
        if audit_log:
            audit_log.update(is_finished=True, end_time = now())
        self.close()

    @property
    def queue(self):
        queue = get_redis_instance()
        queue.pubsub()
        return queue

    def closessh(self):
        self.queue.publish(self.channel_name, json.dumps(['close']))

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            if text_data is not None:
                data = json.loads(text_data)
                begin_time = time.time()
                if isinstance(data, list) and data[0] == 'username':
                    self.username = data[1]
                elif isinstance(data, list) and data[0] == 'ip' and (len(data) == 5 or len(data) == 6):
                    ip = data[1]
                    width = data[2]
                    height = data[3]
                    session_uuid = data[4]
                    self.hostname = ip
                    try:
                        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        server = AgentAdmin.objects.get(ip=ip)
                        port = server.ssh_port
                        if len(data) == 6:
                            port = data[5]
                        self.ssh.connect(ip, port=port, username=server.username, password=server.password, timeout=3)
                        if len(session_uuid) == 36:
                            log_name = session_uuid
                        else:
                            log_name = str(uuid.uuid4())
                        SessionLog.objects.create(user=self.opt_username, server=server, channel=self.channel_name,
                                                  log_name=log_name)
                    except socket.timeout:
                        self.send(text_data="Can not connect to server, timeout!")
                        self.disconnect(1000)
                        return
                    except Exception as e:
                        self.send(text_data="Can not connect to server, Authentication failed.")
                        self.disconnect(1000)
                        return
                    ssh_chan = self.ssh.invoke_shell(width=width, height=height, term='xterm')
                    sshterminal = SshTerminalThread(self, ssh_chan, self.opt_username)
                    sshterminal.setDaemon = True
                    sshterminal.start()
                    log_name = log_name + '.log'
                    interactivessh = InterActiveShellThread(ssh_chan, self, log_name=log_name, width=width, height=height)
                    interactivessh.setDaemon = True
                    interactivessh.start()
                elif isinstance(data, list) and data[0] in ['stdin', 'stdout']:
                    self.queue.publish(self.channel_name, json.loads(text_data)[1])
                elif isinstance(data, list) and data[0] == u'set_size':
                    self.queue.publish(self.channel_name, text_data)
                elif isinstance(data, list) and data[0] == u'close':
                    self.disconnect(1000)
                    return
                else:
                    self.queue.publish(self.channel_name, text_data)
            elif bytes_data:
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
