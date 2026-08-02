import json
import time

from channels.generic.websocket import WebsocketConsumer
from threading import Thread, Event

import threading
from django.conf import settings
from django.contrib import auth

from bastion.component.redis_client_conn import get_redis_dict_data
from k8s_api import K8sApi


class K8SStreamThread(Thread):
    def __init__(self, websocket, container_stream):
        Thread.__init__(self)
        self.start_time = time.time()
        self.websocket = websocket
        self.stream = container_stream
        self.daemon = True
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        try:
            while self.stream.is_open() and not self.stopped():
                if self.check_timeout():
                    break
                try:
                    if self.stream.peek_stdout():
                        stdout = self.stream.read_stdout()
                        self.websocket.send(stdout)
                        self.start_time = time.time()
                except Exception:
                    pass
                try:
                    if self.stream.peek_stderr():
                        stderr = self.stream.read_stderr()
                        self.websocket.send(stderr)
                        self.start_time = time.time()
                except Exception:
                    pass
                # 无数据时短暂休眠，避免忙等
                if not self.stream.peek_stdout() and not self.stream.peek_stderr():
                    time.sleep(0.01)
            else:
                if not self.stopped():
                    self.websocket._close_ws_connect("\nPod断开连接!")
        except Exception:
            pass

    def check_timeout(self):
        stop = False
        now = time.time()
        if now - self.start_time >= self.websocket.long_time_break_time:
            self.websocket._close_ws_connect("\nPod断开连接: 长时间没有任何操作")
            stop = True
        if now >= self.websocket.invalid_timestamp:
            self.websocket._close_ws_connect("\nPod断开连接: 登录令牌已过期,请重新登录!")
            stop = True
        return stop


class PodConsumer(WebsocketConsumer):
    def connect(self):
        # self.scope["cookies"]["bk_token"] = "wBWDmiR5rM1pHcIf3lqWs7OERpXE8gFVgdoRngDyoCk"
        self._update_scope_user()
        # ["set_size", 466, 2133]
        self.height = 240
        self.width = 300
        self.stream = None
        self.token = None
        self.invalid_timestamp = 0
        self.long_time_break_time = 60 * 30
        self.kub_stream = None
        self.accept()

        check_status, api, namespace, pod, container, message = self._check_pod_auth()
        if not check_status:
            self._close_ws_connect("\nPod登录失败: " + message)
            return
        status, self.stream = api.pod_exec(namespace, pod, self.height, self.width, container)
        if not status:
            self._close_ws_connect(str("\nPod登录失败: " + self.stream))
            return
        self.kub_stream = K8SStreamThread(self, self.stream)
        self.kub_stream.daemon = True
        self.kub_stream.start()

    def _update_scope_user(self):
        user = auth.authenticate(request=None, bk_token=self.get_token())
        if user:
            self.scope["user"] = user
        return user

    def _close_ws_connect(self, close_code):
        try:
            self.send(close_code)
        except Exception:
            pass
        try:
            self.disconnect(close_code)
        except Exception:
            pass
        try:
            self.close()
        except Exception:
            pass

    def disconnect(self, close_code):
        if self.kub_stream:
            try:
                self.kub_stream.stop()
            except Exception:
                pass
        if self.stream:
            try:
                self.stream.write_stdin('exit\r')
            except Exception:
                pass
        if self.kub_stream:
            try:
                self.kub_stream.join(timeout=3)
            except Exception:
                pass
        self.stream = None
        self.kub_stream = None

    def receive(self, text_data=None, bytes_data=None):
        # print("text_data", text_data)
        is_change = self.change_size(text_data)
        if not is_change:
            try:
                self.stream.write_stdin(text_data)
            except Exception:
                pass

    def change_size(self, text_data):
        # ["set_size", 466 , 2133]
        # ["set_size", 120, 120]
        is_change = False
        try:
            if "set_size" not in text_data:
                return False
            import ast
            li = ast.literal_eval(text_data)
            if isinstance(li, list) and len(li) == 3:
                name = li[0]
                height = li[1]
                width = li[2]
                if name == "set_size":
                    self.height = height
                    self.width = width
                    is_change = True
                    if self.stream:
                        self.stream.write_channel(4, json.dumps({"Height": int(height), "Width": int(width)}))

        except Exception:
            pass
        return is_change

    def get_token(self):
        cookies = self.scope.get("cookies") or {}
        bk_token = cookies.get("bk_token")
        # 开发环境下允许使用 settings.BK_TOKEN 兜底
        if not bk_token:
            try:
                if getattr(settings, 'DEBUG', False):
                    bk_token = settings.BK_TOKEN
            except Exception:
                pass
        return bk_token

    def get_request_param_dict(self):
        try:
            query_string = self.scope.get("query_string").decode()
        except Exception:
            query_string = self.scope.get("query_string")

        request_param = dict([x.split('=', 1) for x in query_string.split('&')])
        return request_param

    def _check_pod_auth(self):
        params = self.get_request_param_dict()
        pod_token = params.get("token")  # pod_login_48289284298b4e8faf3ab4cf76287c45
        bk_token = self.get_token()
        user = self.scope.get("user")
        data = get_redis_dict_data("pod_login", str(pod_token))
        if not data:
            return False, None, None, None, None, "登录令牌已过期,请重新登录"

        cluster_config = data.get("cluster_config")
        long_time_break_time = data.get("long_time_break_time")
        if long_time_break_time and isinstance(long_time_break_time, int):
            self.long_time_break_time = long_time_break_time
        namespace = data.get("namespace")
        pod = data.get("pod")
        container = data.get("container")
        username = data.get("username")
        cache_bk_token = data.get("bk_token")
        if bk_token != cache_bk_token:
            return False, None, None, None, None, "当前用户无访问权限,请重新登录或联系管理员授权"
        if not user:
            return False, None, None, None, None, "当前用户已失效,请重新登录或联系管理员授权!"
        api = K8sApi(cluster_config)
        self.invalid_timestamp = data.get("invalid_timestamp")
        return True, api, namespace, pod, container, "Success"
