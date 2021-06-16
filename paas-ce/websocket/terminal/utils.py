import threading, socket
import os, ast
import re
import time
import redis
from channels.layers import get_channel_layer
from six import string_types as basestring
import struct
import paramiko
import logging
from .models import CommandBlockList, CommandBlockHistory
from django.conf import settings

logger = logging.getLogger('django.server')
logger.setLevel(logging.DEBUG)
try:
    unicode = str
except NameError:
    unicode = str

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
channel_layer = get_channel_layer()


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
        passwd, host = host_str.split(":")[1].split('@')
        return redis.StrictRedis(host=host, port=port, password=passwd, db=db)


class CommandDeal(object):
    @staticmethod
    def remove_obstruct_char(cmd_str):
        '''delete some special control delimiter'''
        control_char = re.compile(r'\x07 | \x1b\[1P | \r ', re.X)
        cmd_str = control_char.sub('', cmd_str.strip())
        # 'delete left and right delete'
        patch_char = re.compile('\x08\x1b\[C')
        while patch_char.search(cmd_str):
            cmd_str = patch_char.sub('', cmd_str.rstrip())
        return cmd_str

    @staticmethod
    def deal_backspace(match_str, result_command, pattern_str, backspace_num):
        '''
        deal with delete key
        '''
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
        '''
        deal and replace command
        '''
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

    def deal_command(self, str_r, session_obj):
        """
            deal with command special key
        """
        str_r = self.remove_obstruct_char(str_r)

        result_command = ''  # final result
        backspace_num = 0               # cursor num
        reach_backspace_flag = False    # detect if there is cursor key
        pattern_str = ''
        while str_r:
            tmp = re.match(r'\s*\w+\s*', str_r)
            if tmp:
                str_r = str_r[len(str(tmp.group(0))):]
                if reach_backspace_flag:
                    pattern_str += str(tmp.group(0))
                    continue
                else:
                    result_command += str(tmp.group(0))
                    continue

            tmp = re.match(r'\x1b\[K[\x08]*', str_r)
            if tmp:
                result_command, del_len = self.deal_backspace(
                    str(tmp.group(0)), result_command, pattern_str, backspace_num)
                reach_backspace_flag = False
                backspace_num = 0
                pattern_str = ''
                str_r = str_r[del_len:]
                continue

            tmp = re.match(r'\x08+', str_r)
            if tmp:
                str_r = str_r[len(str(tmp.group(0))):]
                if len(str_r) != 0:
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

            # deal with replace command
            tmp = re.match(r'(\x1b\[1@\w)+', str_r)
            if tmp:
                result_command, del_len = self.deal_replace_char(
                    str(tmp.group(0)), result_command, backspace_num)
                str_r = str_r[del_len:]
                backspace_num = 0
                continue

            if reach_backspace_flag:
                pattern_str += str_r[0]
            else:
                result_command += str_r[0]
            str_r = str_r[1:]

        if backspace_num > 0:
            result_command = result_command[0:-backspace_num] + pattern_str

        result_command = self.remove_control_char(result_command)
        result_command = self.generate_final_command(result_command)
        return result_command

    def remove_control_char(self, result_command):
        """
        deal with special key
        """
        control_char = re.compile(r"""
                                          \x1b[ #%()*+\-.\/]. |
                                          \r |                                               #enter key(CR)
                                          (?:\x1b\[|\x9b) [ -?]* [@-~] |                     #enter control key(CSI)... Cmd
                                          (?:\x1b\]|\x9d) .*? (?:\x1b\\|[\a\x9c]) | \x07 |   #enter system control key(OSC)...terminate key(ST|BEL)
                                          (?:\x1b[P^_]|[\x90\x9e\x9f]) .*? (?:\x1b\\|\x9c) | #enter serial communication key(DCS|PM|APC)...terminate key(ST)
                                          \x1b.                                              #special key
                                          [\x80-\x9f] | (?:\x1b\]0.*) | \[.*@.*\][\$#] | (.*mysql>.*)      #enter every special key
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
                command_res.pop(index-1)
                index -= 1
            elif v == '\x15':
                for n in range(0,index):
                    command.pop(0)
                index = 0
            else:
                command_res.insert(index,v)
                index += 1
        return ''.join(command_res)


class SshTerminalThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, websocket, sshchan, opt_name, elementid=None):
        super(SshTerminalThread, self).__init__()
        self._stop_event = threading.Event()
        self.channel_name = websocket.channel_name
        self.websocket = websocket
        self.chan = sshchan
        self.elementid = elementid
        self.opt_name = opt_name
        self.queue = self.redis_queue()
        self.chan.vim_flag = False

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def redis_queue(self):
        redis_instance = get_redis_instance()
        redis_sub = redis_instance.pubsub()
        if self.elementid:
            redis_sub.subscribe(self.elementid.rsplit('_')[0])
        else:
            redis_sub.subscribe(self.channel_name)
        return redis_sub

    def check_blocklist(self, command):
        while command.find('  ') >= 0:
            command = command.replace('  ', ' ')
        for command_info in CommandBlockList.objects.values():
            command_ = command_info["command"]
            while command_.find('  ') >= 0:
                command_ = command_.replace('  ', ' ')
            pattern = '\\b' + command_ + '\\b'
            if command_ == command or re.search(pattern, command):
                return True, command_info["block_type"].strip(), command_info["block_info"], command_info["command"]
        return False, '', '', ''

    def check_timeout_close(self):
        # 空闲超时退出
        current_time = time.time()
        if int(current_time - self.websocket.wait_time) > settings.TERMINAL_TIMEOUT:
            self.websocket.send("\r\nTimeout...\r\nconnection closed...")
            self.websocket.disconnect(1001)

    def run(self):
        logger = logging.getLogger('django.server')
        logger.setLevel(logging.DEBUG)
        # fix the first login 1 bug
        first_flag = True
        block_flag = False
        block_type = ''
        command = list()
        try:
            session_obj = SessionLog.objects.get(channel=self.channel_name)
        except Exception:
            # DoesNotExist
            self.websocket.send("{'opsany_ssh_error':'channel创建失败'}")
            self.stop()
            self.websocket.disconnect(1000)
            return
        command_history_obj = None
        while (not self._stop_event.is_set()):
            self.check_timeout_close()
            text = self.queue.get_message()
            if text:
                self.websocket.wait_time = time.time()
                if isinstance(text['data'], (str, basestring, unicode, bytes)):
                    if isinstance(text['data'], bytes):
                        try:
                            data = ast.literal_eval(text['data'].decode('utf8'))
                        except Exception as e:
                            data = text['data']
                    else:
                        try:
                            data = ast.literal_eval(text['data'])
                        except Exception as e:
                            data = text['data']
                else:
                    data = text['data']
                if isinstance(data, (list, tuple)):
                    if data[0] == 'command':
                        command.append(data[1])
                    elif data[0] == 'close' or data[0] == "'close'":
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
                            # fix command record duplicate
                            if len(data) >= 3 and data[2] == 'command':
                                pass
                        self.chan.send(data[1])
                else:
                    try:
                        try:
                            new_data = str(data, encoding = "utf8")
                        except:
                            new_data = str(data)
                        if self.chan.vim_flag:
                            # in vim or 多行输入
                            pass
                        elif '\r' in new_data and len(command) > 0 and command[len(command)-1] == '\\':
                            # 多行输入 换行处理
                            command.pop(len(command)-1)
                        else:
                            if block_flag and block_type == 'confirm':
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
                                    self.websocket.send('\r\n\033[31m' + block_info + ': [Y/N] \033[0m')
                                    continue
                            block_flag = False
                            block_type = ''
                            if new_data == '\r':
                                # 特殊控制字符处理
                                record_command = CommandDeal().deal_command(''.join(command).strip().replace('\\\r', '\r'), session_obj)
                                # 命令拦截匹配策略
                                block_flag, block_type, block_info, intercept_command = self.check_blocklist(record_command.strip())
                                if block_flag:
                                    command_history_obj = CommandBlockHistory.objects.create(
                                            opt_user=self.opt_name,
                                            user=self.websocket.username,
                                            block_type=block_type,
                                            hostname=self.websocket.hostname,
                                            command=record_command,
                                            intercept_command=intercept_command
                                    )
                                    command = list()
                                    if block_type == 'confirm':
                                        self.websocket.send('\r\n\033[31m' + block_info + ': [Y/N] \033[0m')
                                        continue
                                    elif block_type == 'cancle':
                                        self.websocket.send('\r\n\033[31m' + block_info + '\033[0m')
                                        data = '\x03'
                                else:
                                    if len(record_command) != 0:
                                        command = list()

                        if first_flag:
                            first_flag = False
                            command = list()
                        elif isinstance(data, bytes):
                            self.chan.send(data)
                        else:
                            self.chan.send(str(data))
                    except socket.error:
                        self.websocket.disconnect(1000)
                        logger.error('close threading error')
                        self.stop()
            # avoid cpu usage always 100%
            time.sleep(0.001)

try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False
    # raise Exception('This project does\'t support windows system!')
import select
import sys
import json
import codecs
import traceback
from paramiko.py3compat import u
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode
import errno
from .models import CommandLog, SessionLog


def mkdir_p(path):
    """
    Pythonic version of "mkdir -p".  Example equivalents::

        >>> mkdir_p('/tmp/test/testing') # Does the same thing as...
        >>> from subprocess import call
        >>> call('mkdir -p /tmp/test/testing')

    .. note:: This doesn't actually call any external commands.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise  # The original exception


class CustomeFloatEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float):
            return format(obj, '.6f')
        return json.JSONEncoder.encode(self, obj)


def interactive_shell(chan, channel, log_name=None, width=90, height=40, elementid=None):
    if has_termios:
        posix_shell(chan, channel, log_name=log_name,
                    width=width, height=height, elementid=elementid)
    else:
        sys.exit(1)

zmodemszstart = b'rz\r**\x18B00000000000000\r\x8a'
zmodemszend = b'**\x18B0800000000022d\r\x8a'
zmodemrzstart = b'rz waiting to receive.**\x18B0100000023be50\r\x8a'
#zmodemrzstart = b'rz waiting to receive.**\x18B01000'
zmodemrzend = b'**\x18B0800000000022d\r\x8a'
#zmodemrzwait = b'**\x18B03010000009866\r\x8a'
zmodemcancel = b'\x18\x18\x18\x18\x18\x08\x08\x08\x08\x08'
#zmodemcancel1 = b'\r\n\x11\x18@\x18k\xdd\xcd'


# chan is  ssh channel
# channel  is websocket
def posix_shell(sshchan, channel, log_name=None, width=90, height=40, elementid=None):
    # 是否进入了rzsz状态中
    zmodem = False
    # 是否sz结束
    zmodemOO = False
    stdout = list()
    begin_time = time.time()
    last_write_time = {'last_activity_time': begin_time}
    session_obj = SessionLog.objects.get(channel=channel.channel_name)
    command = list()
    queue = get_redis_instance()
    redis_channel = queue.pubsub()

    vim_data = ''
    try:
        # 执行超时
        #sshchan.settimeout(20.0)
        sshchan.settimeout(0)
        data = None
        while True:
            try:
                r, w, x = select.select([sshchan], [], [])
                data = sshchan.recv(1024)
                if zmodemOO:
                    zmodemOO = False
                    if data == b'rz\r' or data == b'OO':
                        continue
                    else:
                        data = data.replace(b'OO',b'')
                        channel.send(bytes_data=data)
                else:
                    if not len(data):
                        break
                if zmodem:
                    if zmodemszend in data or zmodemrzend in data:
                        zmodem = False
                        if zmodemszend in data:
                            zmodemOO = True
                    if zmodemcancel in data:
                        zmodem = False
                    channel.send(bytes_data=data)
                else:
                    if data == b'rz\r':
                        continue
                        #data = data + sshchan.recv(4096)
                    if zmodemszstart in data or zmodemrzstart in data or b'**\x18B00000000000000\r\x8a\x11' in data:
                        zmodem = True
                        channel.send(bytes_data=data)
                    else:
                        if len(data) == 0:
                            channel.send({'text_data': json.dumps(['disconnect', smart_unicode('\r\n*** EOF\r\n')])})
                            break
                        x = u(data)
                        now = time.time()
                        delay = now - last_write_time['last_activity_time']
                        last_write_time['last_activity_time'] = now
                        if x == "exit\r\n" or x == "\r\nlogout\r\n" or x == '<<<close>>>':
                            channel.send(x)
                            break
                        else:
                            if sshchan.vim_flag:
                                vim_data += x
                                if re.compile('\[.*@.*\][\$#]').search(vim_data):
                                    sshchan.vim_flag = False
                                    vim_data = ''
                            if not sshchan.vim_flag and '\r\n' not in x and not re.compile('\[.*@.*\][\$#]').search(x) and not re.compile('\x1b]0;.*@.*\x07').search(x):
                                command.append(x)
                                queue.publish(channel.channel_name, json.dumps(['command', x]))
                            elif data==b'\r\n> ' and len(command) > 0 and command[len(command)-1] == '\\':
                                # 多行命令 输入
                                command.pop(len(command)-1)
                            else:
                                if len(command) == 0 and '\\\r\n>' in x and (x.endswith(']# ') or x.endswith(']$ ')):
                                    # 多行命令 粘贴输入
                                    command_result = ''.join(x.split('\\\r\n>')).split('\r\n')[0]
                                else:
                                    command_result = CommandDeal().deal_command(''.join(command), session_obj)
                                if len(command_result) != 0:
                                    if command_result.strip().startswith('vi') or command_result.strip().startswith('fg'):
                                        sshchan.vim_flag = True
                                    CommandLog.objects.create(log=session_obj, command=command_result[0:255])
                                    command = list()
                            if isinstance(x, unicode):
                                stdout.append([delay, x])
                            else:
                                stdout.append([delay, codecs.getincrementaldecoder('UTF-8')('replace').decode(x)])
                        if isinstance(x, unicode):
                            if elementid:
                                channel.send(json.dumps(['stdout', x, elementid.rsplit('_')[0]]))
                            else:
                                channel.send(str(x))
                        else:
                            if elementid:
                                channel_layer.send(channel, {'text_data': json.dumps(
                                    ['stdout', smart_unicode(x), elementid.rsplit('_')[0]])})
                            else:
                                channel_layer.send(channel, {'bytes_data': data})
            except socket.timeout:
                # exit threading
                channel.disconnect(1000)
                break
            except UnicodeDecodeError:
                channel.send(bytes_data=data)
            except Exception as e:
                logger.error(traceback.print_exc())
                if elementid:
                    channel.send(json.dumps(['stdout', 'A bug find,You can report it to me' + smart_unicode(e), elementid.rsplit('_')[0]]))
                else:
                    channel.send("\r")
    finally:
        channel.send('\r\nconnection closed...')
        time.sleep(2)
        sshchan.close()
        channel.close()
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
        mkdir_p('/'.join(os.path.join(settings.TERMINAL_PATH, log_name).rsplit('/')[0:-1]))
        with open(os.path.join(settings.TERMINAL_PATH, log_name), "a") as f:
            f.write(json.dumps(attrs, ensure_ascii=True,
                               cls=CustomeFloatEncoder, indent=2))


class InterActiveShellThread(threading.Thread):
    def __init__(self, chan, channel, log_name=None, width=90, height=40, elementid=None):
        super(InterActiveShellThread, self).__init__()
        self.chan = chan
        self.channel = channel
        self.log_name = log_name
        self.width = width
        self.height = height
        self.elementid = elementid

    def run(self):
        interactive_shell(self.chan, self.channel, log_name=self.log_name,
                          width=self.width, height=self.height, elementid=self.elementid)