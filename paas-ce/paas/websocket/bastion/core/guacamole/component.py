# -*- coding: utf-8 -*-
import threading
try:
    import simplejson as json
except ImportError:
    import json
from bastion.core.terminal.component import SSHBaseComponent
import ast
from bastion.core.guacamole.client import guac_logger as logger
import time
try:
    long = int
except NameError:
    long = int
try:
    unicode = str
except NameError:
    unicode = str
from six import string_types as basestring


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
            while True:
                try:
                    instruction = self.client.receive()
                except:
                    break
                if instruction:
                    self.websocket.send(instruction)


class GuacamoleThreadWrite(GuacamoleThread):

    def run(self):
        while True:
            if self.stopped():
                    break
            text = self.queue.get_message()
            if text:
                logger.debug('******recv info from redis: %s' % text)
            try:
                data = ast.literal_eval(text['data'])
            except Exception:
                if isinstance(text, dict) and 'data' in text:
                    data = text['data']
                elif isinstance(text, (unicode, basestring)):
                    data = text
                else:
                    data = text

            if data:
                if isinstance(data, (list, tuple)):
                    if data[0] == 'close':
                        self.stop()
                if isinstance(data, (long, int)) and data == 1:
                    pass
                else:
                    with self.write_lock:
                        self.client.send(data)
            else:
                time.sleep(0.001)