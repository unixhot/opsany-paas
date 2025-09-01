import datetime
import threading
import uuid

import pymysql
from sqlparse import parsestream

import settings
import socket
import ast
import re
import time
import redis
from six import string_types as basestring
import struct
import paramiko
import select
import sys
import json
import codecs
# from paramiko.py3compat import u
import errno
import os

from bastion.component.redis_client_conn import get_redis_str_data

try:
    unicode = str
except NameError:
    unicode = str
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_str as smart_unicode
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False
    if getattr(settings, "run_env") == "dev":
        has_termios = True
    else:
        raise Exception('This project does\'t support windows system!')

from bastion.models import SessionLogModel, CommandLogModel, SessionCommandHistoryModel, SessionLogInfoModel
from bastion.core.status_code import WebSocketStatusCode
from bastion.component.core import CheckUserHostComponent
import logging

app_logger = logging.getLogger("app")

try:
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
except:
    pass


class SSHBaseComponent:
    @staticmethod
    def get_redis_instance():
        redis_server = channel_layer.hosts[0]["address"]
        redis_list = redis_server.split('/')
        db = 0
        if len(redis_list) == 4:
            db = redis_list[3]
        host_str = redis_list[2]
        if len(host_str.split(":")) < 3:
            port = host_str.split(":")[1]
            host = host_str.split(":")[0]
            return redis.StrictRedis(host=host, port=port, db=db)
        else:
            port = host_str.split(":")[2]
            password, host = host_str.split(":")[1].split('@')
            return redis.StrictRedis(host=host, port=port, password=password, db=db)

    @staticmethod
    def remove_obstruct_char(cmd_str):
        """
        Delete some special control delimiter
        """
        control_char = re.compile(r'\x07 | \x1b\[1P | \r ', re.X)
        cmd_str = control_char.sub('', cmd_str.strip())
        patch_char = re.compile('\x08\x1b\[C')
        while patch_char.search(cmd_str):
            cmd_str = patch_char.sub('', cmd_str.rstrip())
        return cmd_str

    @staticmethod
    def deal_backspace(match_str, result_command, pattern_str, backspace_num):
        """
        Deal with delete key
        """
        if backspace_num > 0:
            if backspace_num > len(result_command):
                result_command += pattern_str
                result_command = result_command[0:-backspace_num]
            else:
                result_command = result_command[0:-backspace_num]
                result_command += pattern_str
        del_len = len(match_str) - 3
        if del_len > 0:
            result_command = result_command[0:-del_len]
        return result_command, len(match_str)

    @staticmethod
    def deal_replace_char(match_str, result_command, backspace_num):
        """
        Deal and replace command
        """
        str_lists = re.findall(r'(?<=\x1b\[1@)\w', match_str)
        tmp_str = ''.join(str_lists)
        result_command_list = list(result_command)
        if len(tmp_str) > 1:
            result_command_list[-backspace_num:-
                                (backspace_num - len(tmp_str))] = tmp_str
        elif len(tmp_str) > 0:
            if result_command_list[-backspace_num] == ' ':
                result_command_list.insert(-backspace_num, tmp_str)
            else:
                result_command_list[-backspace_num] = tmp_str
        result_command = ''.join(result_command_list)
        return result_command, len(match_str)

    def remove_control_char(self, result_command):
        """
        deal with special key
        """
        control_char = re.compile(r"""
            \x1b[ #%()*+\-.\/]. |
            \r |                                               # enter key(CR)
            (?:\x1b\[|\x9b) [ -?]* [@-~] |                     # enter control key(CSI)... Cmd
            (?:\x1b\]|\x9d) .*? (?:\x1b\\|[\a\x9c]) | \x07 |   # enter system control key(OSC)...terminate key(ST|BEL)
            (?:\x1b[P^_]|[\x90\x9e\x9f]) .*? (?:\x1b\\|\x9c) | # enter serial communication key(DCS|PM|APC)...terminate key(ST)
            \x1b.                                              # special key
            [\x80-\x9f] | (?:\x1b\]0.*) | \[.*@.*\][\$#] | (.*mysql>.*)      # enter every special key
            """, re.X)
        result_command = control_char.sub('', result_command.strip())
        try:
            return result_command.decode('utf8', "ignore")
        except:
            return result_command

    def generate_final_command(self, command):
        command_res = []
        index = 0
        for i,v in enumerate(list(command)):
            if v == '\x1b[D':
                if index > 0:
                    index -= 1
            elif v == '\x1b[C':
                if index < len(command_res):
                    index += 1
            elif v == '\x7f':
                if index < len(command_res):
                    command_res.pop(index-1)
                    index -= 1
            elif v == '\x15':
                for n in range(0, index):
                    command.pop(0)
                index = 0
            else:
                command_res.insert(index, v)
                index += 1
        return ''.join(command_res)

    def deal_command(self, command):
        """
        deal with command special key
        """
        command = self.remove_obstruct_char(command)
        result_command = ''  # final result
        backspace_num = 0               # cursor num
        reach_backspace_flag = False    # detect if there is cursor key
        pattern_str = ''
        while command:
            tmp = re.match(r'\s*\w+\s*', command)
            if tmp:
                command = command[len(str(tmp.group(0))):]
                if reach_backspace_flag:
                    pattern_str += str(tmp.group(0))
                    continue
                else:
                    result_command += str(tmp.group(0))
                    continue
            tmp = re.match(r'\x1b\[K[\x08]*', command)
            if tmp:
                result_command, del_len = self.deal_backspace(
                    str(tmp.group(0)), result_command, pattern_str, backspace_num)
                reach_backspace_flag = False
                backspace_num = 0
                pattern_str = ''
                command = command[del_len:]
                continue
            tmp = re.match(r'\x08+', command)
            if tmp:
                command = command[len(str(tmp.group(0))):]
                if len(command) != 0:
                    if reach_backspace_flag:
                        result_command = result_command[0:-
                                                        backspace_num] + pattern_str
                        pattern_str = ''
                    else:
                        reach_backspace_flag = True
                    backspace_num = len(str(tmp.group(0)))
                    continue
                else:
                    break
            tmp = re.match(r'(\x1b\[1@\w)+', command)
            if tmp:
                result_command, del_len = self.deal_replace_char(
                    str(tmp.group(0)), result_command, backspace_num)
                command = command[del_len:]
                backspace_num = 0
                continue
            if reach_backspace_flag:
                pattern_str += command[0]
            else:
                result_command += command[0]
            command = command[1:]
        if backspace_num > 0:
            result_command = result_command[0:-backspace_num] + pattern_str
        result_command = self.remove_control_char(result_command)
        result_command = self.generate_final_command(result_command)
        return result_command


class SshTerminalThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, websocket, sshchan, opt_name, token, elementid=None, ssh_type="host"):
        super(SshTerminalThread, self).__init__()
        self._stop_event = threading.Event()
        self.ssh_base_component = SSHBaseComponent()
        self.websocket = websocket
        self.chan = sshchan
        self.token = token
        self.elementid = elementid
        self.opt_name = opt_name
        self.queue = self.redis_queue()
        self.chan.vim_flag = False
        self.ssh_type = ssh_type  # ssh  mysql  redis  mongo

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def redis_queue(self):
        redis_instance = self.ssh_base_component.get_redis_instance()
        redis_sub = redis_instance.pubsub()
        if self.elementid:
            redis_sub.subscribe(self.elementid.rsplit('_')[0])
        else:
            redis_sub.subscribe(self.websocket.channel_name)
        return redis_sub

    # def check_command(self, command):
    #     while command.find('  ') >= 0:
    #         command = command.replace('  ', ' ')
    #     # Check command
    #     return True, "", "", ""

    def check_timeout_close(self):
        # 空闲超时退出
        current_time = time.time()
        if int(current_time - self.websocket.wait_time) > settings.TERMINAL_TIMEOUT:
            self.websocket.send("\r\nTimeout...\r\nconnection closed...")
            self.websocket.disconnect(1001)

    def get_block_info(self, block: dict):
        block_info = ""
        for key, value in block.items():
            block_info += "{}: {}".format(key, value)
            block_info += "\n"
        return block_info

    def _clean_text_data(self, text):
        text_data = text.get("data")
        if isinstance(text_data, (str, basestring, unicode, bytes)):
            # print("1. 数据类型是字符串字节进入....")
            if isinstance(text_data, bytes):
                try:
                    data = ast.literal_eval(text_data.decode('utf8'))
                except Exception as e:
                    data = text_data
            else:
                try:
                    data = ast.literal_eval(text_data)
                except Exception as e:
                    data = text_data
        else:
            data = text_data
        return data

    def send_large_text_or_bytes(self, text, chunk_size=2048):
        if isinstance(text, bytes):
            self.chan.send(text)
            # print("发送字节", len(str(text)))
            return "send-bytes"
        else:
            text = str(text)
            for i in range(0, len(text), chunk_size):
                self.chan.send(text[i:i + chunk_size])
                if i > 1:
                    time.sleep(0.1)  # 等待一段时间确保数据被处理
            return "send-string"

    def run(self):
        first_flag = True
        command = list()
        try:
            session_obj = SessionLogModel.objects.get(channel=self.websocket.channel_name)
        except Exception:
            # DoesNotExist
            self.websocket.send(WebSocketStatusCode.CHANNEL_CREATE_ERROR)
            self.stop()
            self.websocket.disconnect(1000)
            return
        block_flag = True
        block_type = 0
        block_info = {}
        command_history_obj = None
        while not self._stop_event.is_set():
            self.check_timeout_close()
            text = self.queue.get_message()
            if text:
                self.websocket.wait_time = time.time()
                # print("tttttttttttttttttttttttttttt", len(str(text['data'])), type(text['data']), (text['type']), text['data'])
                data = self._clean_text_data(text)
                if isinstance(data, (list, tuple)):
                    if data[0] == 'command':
                        command.append(data[1])
                    elif data[0] in ['close', 'exit'] or data[0] in ["'close'", "'exit'", '"exit"']:
                        try:
                            self.chan.send('<<<close>>>')  # close flag
                            break
                        except OSError:
                            pass
                        self.stop()
                    elif data[0] == 'set_size':
                        try:
                            self.chan.resize_pty(
                                width=data[3], height=data[4], width_pixels=data[1], height_pixels=data[2])
                        except (TypeError, struct.error, paramiko.SSHException):
                            pass
                    elif data[0] in ['stdin', 'stdout']:
                        if '\r' not in str(data[1]):
                            command.append(data[1])
                        else:
                            if len(data) >= 3 and data[2] == 'command':
                                pass
                        self.chan.send(data[1])
                else:
                    try:
                        try:
                            new_data = str(data, encoding="utf8")
                        except:
                            new_data = str(data)
                        # command.append(new_data)
                        app_logger.info("{}".format(new_data))
                        if self.chan.vim_flag:
                            # in vim or 多行输入
                            pass
                        elif '\r' in new_data and len(command) > 0 and command[len(command)-1] == '\\':
                            # 多行输入 换行处理
                            command.pop(len(command)-1)
                        else:
                            if not block_flag and block_type == 2:
                                if new_data.lower() == 'y':
                                    command_history_obj.status = "y"
                                    command_history_obj.save()
                                    self.websocket.send(new_data)
                                    data = '\r'
                                elif new_data.lower() == 'n' or new_data == '\x03':
                                    if new_data == '\x03':
                                        new_data = '^C'
                                    self.websocket.send(new_data+'\r')
                                    self.websocket.send('\r\n\033[31m命令未执行!! \033[0m')
                                    data = '\x03'
                                else:
                                    self.websocket.send(new_data+'\r')
                                    self.websocket.send(
                                            '\r\n\033[31m' + self.get_block_info(block_info) + ': [Y/N] \033[0m'
                                    )
                                    continue
                            # 重置block_flag
                            block_flag = True
                            block_type = 0
                            if new_data == '\r':
                                # 特殊控制字符处理
                                record_command = self.ssh_base_component.deal_command(
                                        ''.join(command).strip().replace('\\\r', '\r')
                                )
                                if isinstance(record_command, str):
                                    record_command = str(record_command).encode('utf-16', errors='ignore').decode('utf-16')
                                # 命令拦截匹配策略
                                block_flag, block_type, block_info = CheckUserHostComponent().check_command(
                                        command=record_command.strip(), token=self.token
                                )
                                if record_command.strip():
                                    SessionCommandHistoryModel.create(**{
                                        "session_log": session_obj,
                                        "command": str(record_command).strip()
                                    })
                                    if self.ssh_type == "database":
                                        quits = record_command.strip()
                                        if quits in ["exit", "quit"] or ("quit;" in quits) or ("exit;" in quits):
                                            try:
                                                self.websocket.send('\n\r<<<close>>>')  # close flag
                                                self.websocket.close_connect()
                                                self.chan.close()
                                                break
                                            except OSError:
                                                pass
                                            self.stop()
                                            break
                                if not block_flag:
                                    command_history_obj = CommandLogModel.objects.create(
                                            command=record_command.strip(),
                                            block_type=str(block_type),
                                            intercept_command=record_command.strip(),
                                            hostname=self.websocket.host.host_address,
                                            user=self.websocket.user.username,
                                            opt_user=self.websocket.user.username
                                    )
                                    command = list()
                                    if block_type == 2:
                                        self.websocket.send(
                                                '\r\n\033[31m' + self.get_block_info(block_info) + ': [Y/N] \033[0m'
                                        )
                                        continue
                                    elif block_type == 1:
                                        self.websocket.send(
                                                '\r\n\033[31m' + self.get_block_info(block_info) + '\033[0m'
                                        )
                                        data = '\x03'
                                else:
                                    if len(record_command) != 0:
                                        command = list()
                        if first_flag:
                            first_flag = False
                            command = list()
                        else:
                            self.send_large_text_or_bytes(data)
                            # self.chan.send(str(data))
                    except socket.error:
                        self.websocket.disconnect(1000)
                        self.stop()
            time.sleep(0.001)


class FloatEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float):
            return format(obj, '.6f')
        return json.JSONEncoder.encode(self, obj)


class InterActiveShellThread(threading.Thread):
    SZ_START = b'rz\r**\x18B00000000000000\r\x8a'
    SZ_END = b'**\x18B0800000000022d\r\x8a'
    RZ_START = b'rz waiting to receive.**\x18B0100000023be50\r\x8a'
    RZ_END = b'**\x18B0800000000022d\r\x8a'
    CANCEL = b'\x18\x18\x18\x18\x18\x08\x08\x08\x08\x08'

    def __init__(self, chan, channel, log_name=None, width=90, height=40, elementid=None, database_client="",
                 stop_key=""):
        super(InterActiveShellThread, self).__init__()
        self.chan = chan
        self.channel = channel
        self.log_name = log_name
        self.width = width
        self.height = height
        self.elementid = elementid
        self.ssh_base_component = SSHBaseComponent()
        self.database_client = database_client
        self.database_flag = False
        self.error_flag = False
        self.stop_key = stop_key
        self.database_command = ""      # 用于监听用户退出Mysql 命令行

    def make_log_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise  # The original exception

    def u(self, s, encoding="utf8"):
        """cast bytes or unicode to unicode"""
        if isinstance(s, bytes):
            return s.decode(encoding)
        elif isinstance(s, str):
            return s
        else:
            raise TypeError("Expected unicode or bytes, got {!r}".format(s))

    def create_log(self, width, height, begin_time, stdout, log_name):
        attrs = {
            "version": 1,
            "width": width,
            "height": height,
            "duration": round(time.time() - begin_time, 6),
            "command": os.environ.get('SHELL', None),
            'title': None,
            "env": {
                "TERM": os.environ.get('TERM'),
                "SHELL": os.environ.get('SHELL', 'sh')
            },
            'stdout': list(map(lambda frame: [round(frame[0], 6), frame[1]], stdout))
        }
        SessionLogInfoModel.create(**{
            "log_name": log_name,
            "info": str(json.dumps(attrs, ensure_ascii=True, cls=FloatEncoder, indent=2)),
        })

    def handle_sz_end(self, data, channel):
        if data == b'rz\r' or data == b'OO':
            return False
        else:
            data = data.replace(b'OO',b'')
            channel.send(bytes_data=data)
            return True

    def handle_rz_sz_status(self, data, channel):
        rz_sz_status = True
        sz_end = False
        if self.SZ_END in data or self.RZ_END in data:
            rz_sz_status = False
            if self.SZ_END in data:
                sz_end = True
        if self.CANCEL in data:
            rz_sz_status = False
        channel.send(bytes_data=data)
        return rz_sz_status, sz_end

    def posix_shell(self, sshchan, channel, log_name=None, width=90, height=40, elementid=None):
        if not has_termios:
            sys.exit(1)
        rz_sz_status = sz_end = False
        stdout = []
        command = []
        begin_time = time.time()
        last_write_time = {'last_activity_time': begin_time}
        # session_obj = SessionLog.objects.get(channel=channel.channel_name)
        session_obj = None
        database_re = "^ERROR \d+ .*?: \S+"
        queue = self.ssh_base_component.get_redis_instance()
        queue.pubsub()
        vim_data = ''
        try:
            sshchan.settimeout(0)
            data = None
            while True:
                if get_redis_str_data("cache", self.stop_key):
                    break
                try:
                    try:
                        r, w, x = select.select([sshchan], [], [])
                    except Exception as e:
                        pass

                    data = sshchan.recv(102400)
                    # print("dddddddddddddddddddddddd", data)
                    if self.database_client:
                        # app_logger.info("self.database_client: ||||{}||||".format(self.database_client))
                        # 获取命令行样式
                        data_str = data.decode("utf-8")
                        if self.database_client in data_str:
                            data_str = data_str.split(self.database_client)
                            if data_str:
                                data_str = data_str[-1]
                            # self.database_command = res.split(self.database_client)[0]
                        # app_logger.info("data:||{}||".format(data.decode("utf-8")))
                        self.database_flag = True
                        channel.send(data_str)
                        continue
                    if self.database_flag and not self.error_flag:
                        # if "ERROR 1045 (28000): Access denied for user" in data.decode("utf-8"):
                        if re.match(database_re, data.decode("utf-8")):
                            self.error_flag = True
                            self.database_flag = False
                            data = data.decode("utf-8").split("\r\n")[0].encode("utf-8")
                    elif self.database_flag and self.error_flag:
                        break
                    # 该判定还存在缺陷
                    if self.database_flag and self.database_command.split("\n")[-1] in data.decode("utf-8"):
                        break
                    if sz_end:
                        sz_end = False
                        status = self.handle_sz_end(data, channel)
                        if not status:
                            continue
                    else:
                        if not len(data):
                            break
                    if rz_sz_status:
                        rz_sz_status, sz_end = self.handle_rz_sz_status(data, channel)
                    else:
                        if data == b'rz\r':
                            continue
                        if self.SZ_START in data or self.RZ_START in data or b'**\x18B00000000000000\r\x8a\x11' in data:
                            rz_sz_status = True
                            channel.send(bytes_data=data)
                        else:
                            if len(data) == 0:
                                channel.send({'text_data': json.dumps(['disconnect', smart_unicode('\r\n*** EOF\r\n')])})
                                break
                            x = self.u(data)
                            now = time.time()
                            delay = now - last_write_time['last_activity_time']
                            last_write_time['last_activity_time'] = now
                            if x == "exit\r\n" or x == "\r\nlogout\r\n" or x == '<<<close>>>':
                                try:
                                    channel.send(x)
                                except Exception as e:
                                    print("posix_shell /bastion/core/terminal/component.py 784", str(e))
                                break
                            else:
                                re_pro1 = re.compile('\[.*@.*\][\$#]')
                                re_pro2 = re.compile('\x1b]0;.*@.*\x07')
                                if sshchan.vim_flag:
                                    # vim_data 持续在Vi中操作数据量会变大
                                    vim_data += x
                                    vim_data = vim_data[-500:]
                                    if re_pro1.search(vim_data):
                                        sshchan.vim_flag = False
                                        del vim_data
                                        # global vim_data
                                        vim_data = ''
                                if not sshchan.vim_flag and '\r\n' not in x and not re_pro1.search(x) and not re_pro2.search(x):
                                    # app_logger.debug("Line 690 DEBUG {}".format(str(x)))
                                    command.append(x)
                                    queue.publish(channel.channel_name, json.dumps(['command', x]))
                                elif data == b'\r\n> ' and len(command) > 0 and command[len(command)-1] == '\\':
                                    # 多行命令 输入
                                    command.pop(len(command)-1)
                                else:
                                    if len(command) == 0 and '\\\r\n>' in x and (x.endswith(']# ') or x.endswith(']$ ')):
                                        # 多行命令 粘贴输入
                                        command_result = ''.join(x.split('\\\r\n>')).split('\r\n')[0]
                                    else:
                                        command_result = self.ssh_base_component.deal_command(''.join(command))
                                    if len(command_result) != 0:
                                        if command_result.strip().startswith('vi') or command_result.strip().startswith('fg'):
                                            sshchan.vim_flag = True
                                        # CommandLog.objects.create(log=session_obj, command=command_result[0:255])
                                        # 创建命令日志
                                        command = []
                                # stdout 持续使用列表数量递增
                                if isinstance(x, unicode):
                                    stdout.append([delay, x])
                                else:
                                    stdout.append([delay, codecs.getincrementaldecoder('UTF-8')('replace').decode(x)])
                            if isinstance(x, unicode):
                                if elementid:
                                    channel.send(json.dumps(['stdout', x, elementid.rsplit('_')[0]]))
                                else:
                                    try:
                                        channel.send(str(x))
                                    except Exception as e:
                                        pass
                            else:
                                if elementid:
                                    channel_layer.send(channel, {'text_data': json.dumps(
                                        ['stdout', smart_unicode(x), elementid.rsplit('_')[0]])})
                                else:
                                    channel_layer.send(channel, {'bytes_data': data})
                except socket.timeout as e:
                    print("socket.timeout", e)
                    channel.disconnect(1000)
                    break
                except UnicodeDecodeError:
                    channel.send(bytes_data=data)
                # except Exception as e:
                #     print("Exception", e)
                #     try:
                #         if elementid:
                #             channel.send(json.dumps(['stdout', 'A bug find,You can report it to me' + smart_unicode(e),
                #                                      elementid.rsplit('_')[0]]))
                #         else:
                #             channel.send("\r")
                #     except:
                #         pass
        # except Exception as e:
        #     print("finallyfinally", e)
        finally:
            try:
                channel.send('\r\nconnection closed....')
            except:
                pass
            try:
                channel.close()
            except:
                pass
            sshchan.close()
            time.sleep(2)
            self.create_log(width, height, begin_time, stdout, log_name)

    def run(self):
        self.posix_shell(self.chan, self.channel, self.log_name, self.width, self.height, elementid=self.elementid)
