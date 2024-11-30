import ast
import time
import json
import logging
import uuid
import redis
import sshtunnel
import settings
import threading
from six import string_types as basestring

from bastion.component.redis_client_conn import get_redis_dict_data

try:
    unicode = str
except NameError:
    unicode = str
import socket
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection

from bastion import constant

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

from bastion.core.terminal.component import SSHBaseComponent
from bastion.core.status_code import MySQLWebSocketStatusCode
from bastion.component.core import CheckUserHostComponent
from bastion.component.common import GetUserInfo
from bastion.models import HostModel, CredentialModel, HostCredentialRelationshipModel
from bastion.utils.encryption import PasswordEncryption

app_logging = logging.getLogger("app")


class DatabaseRedisWeb(WebsocketConsumer):
    data_type_dict = {
        "command": "输入Redis命令",
        "result": "后获取剩余结果",
        "select_database": "切换数据库",
        "default_data": "默认数据",
        "close": "手动关闭数据库",
        "error": "连接错误关闭连接",
    }
    ssh = None
    redis_conn = None
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

    def connect(self):
        # 连接 Websocket
        self.wait_time = time.time()
        self.accept()
        # 验证token
        status, code, data = self.check_token()
        if not status and status is not None:
            self.close_connect(code)
        else:
            # self.session_log = self.create_session_log(data)
            self.start_ssh(data)

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
                return False, MySQLWebSocketStatusCode.ACCESS_ERROR, {}
            return False, MySQLWebSocketStatusCode.USER_ERROR, {}
        return False, MySQLWebSocketStatusCode.PARAM_ERROR, {}

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
        # self.scope["cookies"]["bk_token"] = "joCppIpMU5T5nIwbQmo37xHPOo_b7YRwnwCWwbuCaA8"

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

    def close_connect(self, text):
        if text:
            try:
                text = json.dumps(text)
            except:
                pass

            self.send(text_data=text)
        time.sleep(1)
        self.close()
        if self.ssh:
            self.ssh.close()
        return

    def start_ssh(self, data):
        try:
            timeout = int(data.get("timeout", 10))
        except Exception:
            timeout = 10
        if not data.get("cache"):
            host_id = data.get("host_id")
            credential_host_id = data.get("credential_host_id")
            password = data.get("password")
            credential_host = HostCredentialRelationshipModel.fetch_one(id=credential_host_id)
            self.database = HostModel.fetch_one(id=host_id, resource_type=HostModel.RESOURCE_DATABASE, )
            if (not self.database) or (not credential_host):
                self.close_connect(MySQLWebSocketStatusCode.PARAM_ERROR)
            if self.database.resource_type != HostModel.RESOURCE_DATABASE:
                self.close_connect(MySQLWebSocketStatusCode.HOST_TYPE_ERROR)
            network_proxy = self.database.network_proxy
            dic = {
                "host": self.database.host_address,
                "port": self.database.port,
                "socket_connect_timeout": timeout,
                # "port": "16379",
                "password": password,
                "decode_responses": True
            }
            if credential_host.credential.login_type == CredentialModel.LOGIN_AUTO:
                username = credential_host.credential.login_name
                password = self.get_password(credential_host.credential.login_password)
                if username:
                    dic.update(username=username)
                if password:
                    dic.update(password=password)
            if network_proxy:
                network_dict = {
                    "ssh_address_or_host": (network_proxy.linux_ip, network_proxy.linux_port),
                    "ssh_username": network_proxy.linux_login_name,
                    "ssh_password": self.get_password(network_proxy.linux_login_password),
                    "remote_bind_address": (self.database.host_address, self.database.port),
                }
                try:
                    self.ssh = sshtunnel.SSHTunnelForwarder(**network_dict)
                    self.ssh.start()
                    dic["port"] = self.ssh.local_bind_port
                except Exception as e:
                    print("ssh_tunnel_forwarder_error", str(e))
                    self.close_connect(MySQLWebSocketStatusCode.DATABASE_PROXY_ERROR)
            try:
                self.redis_conn = redis.Redis(**dic)
                try:
                    default_data = json.dumps(self._get_default_data())
                    self.send(text_data=(default_data))
                except Exception as e:
                    if "this user has no permissions" in str(e):
                        MySQLWebSocketStatusCode.USER_PERMISSIONS_ERROR["message"] += str(e)
                        self.close_connect(json.dumps(MySQLWebSocketStatusCode.USER_PERMISSIONS_ERROR))
                    else:
                        MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR["message"] += str(e)
                        self.close_connect(json.dumps(MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR))
                    return
            except Exception as e:
                MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR["message"] += str(e)
                self.close_connect(MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR)
                return

        sshterminal = RedisThread(self, self.redis_conn, self.user.username, self.token,
                                  ssh_type=self.database.resource_type)
        sshterminal.setDaemon = True
        sshterminal.start()

    def _get_default_data(self, database=None):
        try:
            all_dbs_command = "config get databases"
            select_dbs_command = "select {}"
            dic = {"data_type": "default_data"}
            all_databases = self._clean_databases(self.redis_conn.execute_command(all_dbs_command))
            dic["databases"] = all_databases
            if database:
                db = database
            else:
                db = 0
            res = self.redis_conn.execute_command(select_dbs_command.format(db))
            dic["select_database"]=db
            dic["data"]= "Databases {}".format(db) + " " + res
            return dic
        except Exception as e:
            MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR["message"] += str(e)
            self.close_connect(MySQLWebSocketStatusCode.LINK_DATA_CHECK_ERROR)


    def _clean_databases(self, all_databases):
        li = []
        if isinstance(all_databases, list):
            if len(all_databases) == 2:
                for i in range(int(all_databases[1])):
                    li.append("Databases {}".format(i))
            return li

        return all_databases

    def disconnect(self, close_code):
        self.close()

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
            self.queue.publish(self.channel_name, text_data)
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


class RedisThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, websocket, redis_conn: redis.StrictRedis, opt_name, token, elementid=None, ssh_type="host"):
        super(RedisThread, self).__init__()
        self._stop_event = threading.Event()
        self.websocket = websocket
        self.redis_conn = redis_conn
        self.ssh_base_component = SSHBaseComponent()
        self.token = token
        self.elementid = elementid
        self.opt_name = opt_name
        self.queue = self.redis_queue()
        self.result_dict = {}
        self.ssh_type = ssh_type  # ssh  mysql  redis  mongo
        self.run_command = False  # 防止执行超长命令超过待机时间时退出问题
        self.command_all_list = constant.ALL_REDIS_COMMAND_LIST
        self.command_can_list = constant.REDIS_SUPPORT_KEY_LIST
        self.command_piece_dict = constant.PIECE_COMMAND_DICT
        self.command_lower_dict = constant.COMMAND_CLEAN_LOWER_COMMAND_LIST
        self.command_return_dict = constant.COMMAND_CLEAN_RETURN_DICT

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

    def check_timeout_close(self):
        # 空闲超时退出
        current_time = time.time()
        if int(current_time - self.websocket.wait_time) > settings.TERMINAL_TIMEOUT:
            # self.websocket.send(json.dumps(MySQLWebSocketStatusCode.LEAVE_TIME_OUT))
            # self.websocket.disconnect(1001)
            self.websocket.close_connect(MySQLWebSocketStatusCode.LEAVE_TIME_OUT)

    def sql_queryset_id(self):
        return str(uuid.uuid4())

    def _check_command(self, command: str):
        """
        命令校验，仅可以执行授权过的命令，处理两个单词的命令
        """
        command_list = command.rsplit()
        try:
            new_command = command_list[0].upper()
            if new_command in self.command_can_list:
                return True
            else:
                if new_command in self.command_piece_dict.keys():
                    if len(command_list) >= 2:
                        new_command = command_list[0].upper() + " " + command_list[1].upper()
                        if new_command in self.command_can_list:
                            return True
                if new_command not in self.command_all_list:
                    return True
                return False
        except Exception as e:
            print("_check_command", str(e))
            return False

    def _clean_command(self, command_str: str):
        # 有些命令小写输出更加友好，将其使用小写执行
        if command_str.strip().upper() in self.command_lower_dict:
            return command_str.strip().lower()
        else:
            return command_str

    def _run_command(self, data):
        command_str = str(data.get("command", "")).strip()
        command_return = {"data_type": "command", "command": command_str}
        self.result_dict = {}
        t1 = time.time()
        status = self._check_command(command_str)
        if not status:
            t2 = time.time()
            # print("command_str", command_str)
            command_return.update({"data": "不支持的命令", "execute_time": t2 - t1, "message": "不支持的命令", "status": 0})
            self.websocket.send(json.dumps(command_return))
            return
        try:
            res = self.redis_conn.execute_command(self._clean_command(command_str))
            t2 = time.time()
            command_return.update(
                {"data": self._clean_command_res(res, command_str), "execute_time": t2 - t1, "message": "OK", "status": 1})
        except Exception as e:
            print("_run_command_run_command", type(e), e)
            t2 = time.time()
            command_return.update({"data": "", "execute_time": t2 - t1, "message": str(e), "status": 0})
        self.websocket.send(json.dumps(command_return))
        return

    def _clean_command_res(self, res, command_str=None):
        # print("resres", res)
        # print("command_str", command_str)
        # 有些命令小写输出不一致，将其统一
        command_str_end = command_str.rsplit()[0]
        if command_str_end in self.command_return_dict.keys():
            if res is True:
                return self.command_return_dict.get("command_str_end", "OK!")
        # 当数据是列表时处理列表内部数据转为固定格式字符串
        if isinstance(res, list):
            new_list = []
            for d in res:
                if isinstance(d, dict):
                    new_list.append(" ".join([str(k) + "=" + str(v) for k, v in d.items()]))
                else:
                    new_list.append(d)
            return new_list
        elif isinstance(res, dict):
            return res
        else:
            return res

    def _handler_command(self, text):
        # print("从前端Web取出命令(原生)：", text)
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
        # print("从前端Web取出命令处理成字符串：", data, type(data))
        try:
            if not isinstance(data, (dict, list)):
                data = json.loads(data)
        except Exception as e:
            print("_handler_command_error", text, e)
            # self.websocket.send(str(e))
        return data

    def _handler_sql_result(self, res_list):
        if res_list:
            new_list = []
            if isinstance(res_list, list):
                for res in res_list:
                    if isinstance(res, dict):
                        for k, v in res.items():
                            # datetime.datetime
                            if not isinstance(v, (int, bool, float)):
                                res[k] = str(v)
                        # new_list.append(list(res.values()))
                # new_list.insert(0, list(res_list[0].keys()))

            # return new_list
        # else:
        #     return res_list
        return res_list

    def _sql_result(self, data):
        result_id = data.get("result_id")
        try:
            limit = int(data.get("limit"))
        except:
            limit = 20
        try:
            offset = int(data.get("offset"))
        except:
            offset = 0
        # res = self.mysql_cursor.fetchmany(size)
        if self.result_dict.get(result_id):
            res = self.result_dict.get(result_id)[offset: offset + limit]
        else:
            res = []

        sql_return = {"data_type": "result",
                      "data_list": [{"rowcount": len(self.result_dict.get(result_id)), "result_data": res}]}
        self.websocket.send(json.dumps(sql_return))

    def _select_database(self, data):
        self.result_dict = {}
        database = data.get("database")
        self.websocket.send(json.dumps(self.websocket._get_default_data(database)))

    def _default_data(self, data):
        self.result_dict = {}
        self.websocket.send(json.dumps(self.websocket._get_default_data()))

    def run(self):
        try:
            while not self._stop_event.is_set():
                if self.run_command is False:
                    self.check_timeout_close()
                else:
                    self.run_command = False
                    self.websocket.send(json.dumps({"data_type": "sql_run", "status": 0}))
                text = self.queue.get_message()
                if text:
                    try:
                        data = self._handler_command(text)
                        if isinstance(data, dict):
                            data_type = data.get("data_type")  # sql, default_data, open_database
                            """
                            命令查询传参：{"data_type": "command", "command": "keys *"}
                            1sql语句查询返回：{
                                'data_type': 'command', 
                                'data': [
                                    {
                                        'rowcount': 287596, 
                                        'result_data': [{'id': 609}]
                                    }
                                ], 
                                "command": "keys *",
                                "execute_time": 11.332820177078247
                                "message": "OK",
                                "status": 1
                            }
                            2sql获取剩余返回值传参: {"data_type": "result", "size": 20}
                            2sql获取剩余返回值返回: {"data_type": "result", "data_list": [
                                    {
                                        "rowcount": 287596, 
                                        "result_data": [{"id": 609}]
                                    }
                                ], 

                            3sql切换数据库传参：{"data_type": "open_database", "database": "control"}
                            3sql切换数据库返回：{
                                "data_type": "default_data",
                                "databases": ["information_schema", "agile",],
                                "open_database": "bastion",
                                "open_database_tables": {
                                    "tables": {
                                        [
                                            {"table_name": "account_user", "column_list": [["id", "int(11)"], ["password", "varchar(128)"],]},
                                            {"table_name": "account_user_groups", "column_list": [["id", "int(11)"], ["user_id", "int(11)"],]}
                                        ]
                                    }
                                }
                            }
                            """

                            if data_type == "command":  # 执行SQL语句
                                # data = {"data_type": "command", "command": "keys *"}

                                self.run_command = True
                                self._run_command(data)
                            elif data_type == "result":  # 获取上一次查询集
                                self._sql_result(data)
                            elif data_type == "select_database":  # 切换数据库
                                self._select_database(data)
                            elif data_type == "default_data":  # 初始数据
                                self._default_data(data)
                            elif data_type == "close":  # 主动关闭
                                self.websocket.close_connect(MySQLWebSocketStatusCode.CLOSE_SUCCESS)
                    except Exception as e:
                        app_logging.warning("MySQLThread_run_ while_not_self._stop_event.is_set" + str(e))
                        dic = MySQLWebSocketStatusCode.SERVER_ERROR
                        dic["message"] = dic["message"].format(str(e))
                        self.websocket.send(json.dumps(dic))

                time.sleep(0.001)
        except Exception as e:
            app_logging.warning("RedisThread_run_redis_error" + str(e))
            dic = MySQLWebSocketStatusCode.SERVER_ERROR
            dic["message"] = dic["message"].format(str(e))
            self.websocket.send(json.dumps(dic))
        finally:
            try:
                self.websocket.send(json.dumps(MySQLWebSocketStatusCode.CHANNEL_CREATE_ERROR))
            except:
                pass
            try:
                self.websocket.close_connect()
            except:
                pass
            time.sleep(2)
