# -*- coding: utf-8 -*-
import threading
import json
import time
import logging
import ast
import socket
from bastion.core.terminal.component import SSHBaseComponent
try:
    long = int
except NameError:
    long = int
try:
    unicode = str
except NameError:
    unicode = str
from six import string_types as basestring

logger = logging.getLogger("guacamole")


class GuacamoleThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, websocket):
        super(GuacamoleThread, self).__init__()
        self.websocket = websocket
        self._stop_event = self.websocket.closed
        self.queue = self.redis_queue()
        self.client = self.websocket.GUACD_CLIENT
        self.read_lock = threading.RLock()
        self.write_lock = threading.RLock()

    def stop(self):
        self._stop_event.set()
        self.websocket.disconnect(1000)

    def stopped(self):
        return self._stop_event.is_set()

    def redis_queue(self):
        redis_instance = SSHBaseComponent().get_redis_instance()
        redis_sub = redis_instance.pubsub()
        redis_sub.subscribe(self.websocket.channel_name)
        return redis_sub

    def run(self):
        with self.read_lock:
            try:
                while not self.stopped():
                    try:
                        instruction = self.client.receive()
                    except socket.timeout:
                        # 超时是正常的，重新检查停止标志
                        continue
                    except Exception as e:
                        logger.warning("[GuacamoleThread] receive error: {}".format(str(e)))
                        break
                    if instruction is None:
                        # 连接已断开
                        break
                    if instruction:
                        try:
                            self.websocket.send(instruction)
                        except Exception:
                            break
            finally:
                # 清理 Redis pub/sub
                try:
                    self.queue.unsubscribe()
                    self.queue.close()
                except Exception:
                    pass


class GuacamoleThreadWrite(GuacamoleThread):

    def run(self):
        try:
            while True:
                if self.stopped():
                        break
                # 使用阻塞式消息获取替代忙等轮询（性能优化：减少 CPU 空转）
                text = self.queue.get_message(timeout=1.0)
                if text:
                    logger.debug('******recv info from redis: %s' % text)
                    try:
                        data = json.loads(text['data'])
                    except (json.JSONDecodeError, TypeError):
                        try:
                            data = ast.literal_eval(text['data'])
                        except (ValueError, SyntaxError, MemoryError):
                            data = text.get('data', text)

                    if data:
                        if isinstance(data, (list, tuple)):
                            if data[0] == 'close':
                                self.stop()
                                continue  # 不继续发送 close 到 guacd
                        if isinstance(data, (long, int)) and data == 1:
                            pass
                        else:
                            with self.write_lock:
                                self.client.send(data)
        finally:
            # 清理 Redis pub/sub
            try:
                self.queue.unsubscribe()
                self.queue.close()
            except Exception:
                pass
