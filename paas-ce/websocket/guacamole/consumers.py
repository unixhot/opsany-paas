# -*- coding: utf-8 -*-
from channels.generic.websocket import WebsocketConsumer
from django.utils.timezone import now
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

import uuid
import json
import threading
import os
import time

from django.conf import settings
from control.models import AgentAdmin
from terminal.models import SessionLog
from guacamole.guacamolethreading import GuacamoleThread, GuacamoleThreadWrite
from guacamole.guacamolethreading import get_redis_instance
from guacamole.client import GuacamoleClient
from control.utils.esb_api import EsbApi
from control.utils.encryption import PasswordEncryption


class GuacamoleWebsocket(WebsocketConsumer):
    GUACD_CLIENT = None
    width = 1920
    height = 1080
    dpi = 900

    def connect(self):
        self.accept('guacamole')
        self.wait_time = time.time()
        protocol = None
        query_string = self.scope['query_string'].decode()
        if query_string:
            query_dict = dict([x.split('=', 1) for x in query_string.split('&')])
            if query_dict.get("width") and query_dict.get("height") and query_dict.get("dpi"):
                self.width = int(float(query_dict["width"]))
                self.height = int(float(query_dict["height"]))
                self.dpi = query_dict["dpi"]
            # if query_dict.get("ip"):
            #     self.hostname = query_dict["ip"]
            #     self.port = query_dict["port"]
            #     self.username = query_dict["username"]
            #     self.password = query_dict["password"]
            #     self.system_type = query_dict["system_type"]
            #     self.agent_name = query_dict['name']
            #     if self.system_type.strip() == "Linux":
            #         protocol = "ssh"
            #     else:
            #         protocol = "rdp"
            #     if AgentAdmin.objects.filter(ip=self.hostname).count() == 0:
            #         self.server = AgentAdmin.objects.create(
            #                 name=self.agent_name,
            #                 ip=self.hostname,
            #                 ssh_port=self.port,
            #                 system_type=self.system_type,
            #                 username=self.username,
            #                 password=self.password
            #         )
            #     else:
            #         self.server = AgentAdmin.objects.get(ip=self.hostname, name=self.agent_name)
            #     self.server_id = str(self.server.id)
            # else:
            self.server_id = str(self.scope['url_route']['kwargs']['server_id'])
        self.GUACD_CLIENT = GuacamoleClient(settings.GUACD_HOST, settings.GUACD_PORT)
        token = self.scope.get('cookies').get("bk_token")
        bk_user = EsbApi(token).get_user_info()  # 获取当前用户
        self.opt_username = bk_user.get("username")
        log_name = str(uuid.uuid4())
        drive_path = os.path.join(settings.GUACD_PATH, self.server_id)
        ori_drive_path = os.path.join(settings.ORI_GUACD_PATH, self.server_id)
        if not os.path.exists(ori_drive_path + "/Download"):
            os.makedirs(ori_drive_path + "/Download")
        args = {
            "enable_drive": "true",
            "create_drive_path": "true",
            "drive_name": "G",
            "drive_path": drive_path
        }
        if not protocol or protocol:
            server_ = AgentAdmin.objects.filter(id=int(self.server_id))
            if server_:
                self.server = server_[0]
                self.hostname = server_[0].ip.strip()
                self.port = server_[0].ssh_port.strip()
                username_list = server_[0].username.strip().split('\\')
                if len(username_list) == 2:
                    self.domain, self.username = username_list
                elif len(username_list) > 2:
                    raise Exception("账号输入错误，请检查!!!")
                else:
                    self.username = username_list[0]
                    self.domain = None
                self.password = server_[0].password.strip()
                if server_[0].system_type.strip() == "Linux":
                    protocol = "ssh"
                else:
                    protocol = "rdp"
                    self.recording_path = os.path.join(settings.GUACD_PATH, "logfile")
                    self.recording_name = log_name
                    if not os.path.exists(self.recording_path):
                        os.makedirs(self.recording_path)
                    args.update({
                        "security": 'any',
                        "ignore_cert": "true",
                        "disable_audio": "true",
                        "recording_path": self.recording_path,
                        "recording_name": self.recording_name,
                        "create_recording_path": 'true'
                    })
            else:
                raise Exception("Server not exist!!!")
        self.GUACD_CLIENT.handshake(
                protocol=protocol,
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=PasswordEncryption().decrypt(self.password),
                domain=self.domain,
                width=self.width,
                height=self.height,
                dpi=self.dpi,
                **args
            )

        self.closed = threading.Event()
        guacamolethread = GuacamoleThread(self)
        guacamolethread.setDaemon = True
        guacamolethread.start()

        guacamolethreadwrite=GuacamoleThreadWrite(self)
        guacamolethreadwrite.setDaemon = True
        guacamolethreadwrite.start()
        SessionLog.objects.create(
                user=self.opt_username,
                server=self.server,
                channel=self.channel_name,
                log_name=log_name,
                guacamole_client_id=self.GUACD_CLIENT.id,
                width=self.width,
                height=self.height
            )

    def disconnect(self, code):
        self.closed.set()
        audit_log = SessionLog.objects.filter(channel=self.channel_name)
        if audit_log:
            audit_log.update(
                    is_finished=True,
                    end_time=now()
                )
            width = str(audit_log[0].width)
            height = str(audit_log[0].height)
            full_path = os.path.join(self.recording_path, self.recording_name)
            command = '/opt /guacamole-server-1.2.0/src/guacenc/guacenc -s '\
                      + width + "x" + height + ' -r 1000000 -f ' + full_path
            os.system(command)
        self.close()
        self.GUACD_CLIENT.client.close()
        self.close()
        self.closeguacamole()
    
    def clean_host_record(self):
        host_info = AgentAdmin.objects.filter(id=int(self.server_id))
        if not host_info[0].controller_id:
            host_info.delete()

    def queue(self):
        queue = get_redis_instance()
        queue.pubsub()
        return queue
    
    def closeguacamole(self):
        self.queue().publish(self.channel_name, json.dumps(['close']))

    def check_timeout_close(self):
        # 空闲超时退出
        current_time = time.time()
        if int(current_time - self.wait_time) > settings.TERMINAL_TIMEOUT:
            self.send("10.disconnect;")
            self.queue().publish(self.channel_name, "10.disconnect;")
            self.disconnect(1001)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        self.check_timeout_close()
        self.queue().publish(self.channel_name, text_data)
        if not text_data.startswith("4.sync,1"):
            self.wait_time = time.time()
        if text_data == '10.disconnect;':
            self.disconnect(1000)


