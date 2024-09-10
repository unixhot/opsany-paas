import ast
import time
import json
import logging
import uuid
import pymysql
import sshtunnel
from sqlparse import parsestream

import settings
import threading
import socket
from six import string_types as basestring

from bastion.component.redis_client_conn import get_redis_dict_data

try:
    unicode = str
except NameError:
    unicode = str
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection

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


class DatabaseMysqlWeb(WebsocketConsumer):
    data_type_dict = {
        "sql": "sql语句查询",
        "sql_run": "心跳：sql正在执行",
        "result": "sql语句查询后获取剩余结果",
        "open_database": "切换数据库",
        "default_data": "默认数据",
        "close": "手动关闭数据库",
        "error": "连接错误关闭连接",
    }
    ssh = None
    mysql_conn = None
    mysql_cursor = None
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
        if self.mysql_cursor:
            self.mysql_cursor.close()
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.ssh:
            self.ssh.close()
        return

    def start_ssh(self, data):
        if not data.get("cache"):
            host_id = data.get("host_id")
            credential_host_id = data.get("credential_host_id")
            password = data.get("password")
            credential_host = HostCredentialRelationshipModel.fetch_one(id=credential_host_id)
            self.database = HostModel.fetch_one(id=host_id)
            if (not self.database) or (not credential_host):
                self.close_connect(MySQLWebSocketStatusCode.PARAM_ERROR)
            if self.database.resource_type != HostModel.RESOURCE_DATABASE:
                self.close_connect(MySQLWebSocketStatusCode.HOST_TYPE_ERROR)
            if credential_host.credential.login_type == CredentialModel.LOGIN_AUTO:
                password = self.get_password(credential_host.credential.login_password)
            network_proxy = self.database.network_proxy
            dic = {
                "host": self.database.host_address,
                "port": self.database.port,
                "user": credential_host.credential.login_name,
                "password": password,
                "ssl_ca": False,
                "charset": "utf8"
            }
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
            # print("dicdic", dic)
            try:
                self.mysql_conn = pymysql.connect(**dic)
                self.mysql_cursor = self.mysql_conn.cursor(cursor=pymysql.cursors.DictCursor)
                try:
                    default_data = json.dumps(self._get_default_data())
                    self.send(text_data=(default_data))
                except Exception as e:
                    print("default_data_error", e)
                    self.send(text_data=json.dumps(MySQLWebSocketStatusCode.DATA_CHECK_ERROR))
            except Exception as e:
                logging.info("pymysql.connect_error" + str(e))
                self.close_connect(MySQLWebSocketStatusCode.DATABASE_CHECK_ERROR)
                return

        sshterminal = MySQLThread(self, self.mysql_conn, self.mysql_cursor, self.user.username, self.token,
                                  ssh_type=self.database.resource_type)
        sshterminal.setDaemon = True
        sshterminal.start()

    def _get_default_data(self, database=None):
        default_database = ["mysql", "information_schema", "performance_schema", "sys"]
        all_databases_sql = """show databases;"""
        database_table_fields_sql = """SELECT information_schema.COLUMNS.TABLE_SCHEMA,information_schema.COLUMNS.TABLE_NAME,information_schema.COLUMNS.COLUMN_NAME,information_schema.COLUMNS.COLUMN_TYPE FROM information_schema.COLUMNS where information_schema.COLUMNS.TABLE_SCHEMA=\"{}\";"""
        open_database_sql = """use `{}`;"""

        dic = {"data_type": "default_data"}
        all_databases = self._clean_databases(self._execute_sql(all_databases_sql))
        dic["databases"] = all_databases
        if database:
            if database not in all_databases:
                dic.update({"open_database": database, "open_database_tables": [],
                            "error": "1049 - Unknown database '{}'".format(database)})
                return dic
            open_database = database
        else:
            open_database = ""
            for database in all_databases:
                if database not in default_database:
                    open_database = database
                    break
            if not open_database:
                open_database = all_databases[0]

            # open_database = "bastion"

        dic.update(
            open_database=open_database,
            open_database_tables=self._clean_database_table(
                self._execute_sql(database_table_fields_sql.format(open_database)))
        )
        res = self._execute_sql(open_database_sql.format(open_database))
        return dic

    def _clean_databases(self, all_databases):
        li = []
        if isinstance(all_databases, list):
            for d in all_databases:
                li.append(d.get("Database"))
            return li

        return all_databases

    def _clean_database_table(self, tables_data):
        dic = {"tables": [], "database": ""}
        if tables_data:
            dic["database"] = tables_data[0].get("TABLE_SCHEMA")
        tables = {}  # type dict
        for i in tables_data:
            # fields = {"fields_name": i.get("COLUMN_NAME"), "fields_type": i.get("COLUMN_TYPE")}
            fields = [i.get("COLUMN_NAME"), i.get("COLUMN_TYPE")]
            table_name = i.get("TABLE_NAME")
            columns = tables.get(table_name) or []
            if columns:
                columns.append(fields)
                tables[table_name] = columns
            else:
                tables[table_name] = [fields]

        for k, v in tables.items():
            dic["tables"].append({"table_name": k, "column_list": v})
        return dic

    def _execute_sql(self, sql):
        self.mysql_cursor.execute(sql)
        self.mysql_conn.commit()
        return self.mysql_cursor.fetchall()

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


class MySQLThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, websocket, mysql_conn: pymysql.connect, mysql_cursor: pymysql.cursors.Cursor, opt_name, token,
                 elementid=None, ssh_type="host"):
        super(MySQLThread, self).__init__()
        self._stop_event = threading.Event()
        self.websocket = websocket
        self.mysql_conn = mysql_conn
        self.mysql_cursor = mysql_cursor
        self.ssh_base_component = SSHBaseComponent()
        self.token = token
        self.elementid = elementid
        self.opt_name = opt_name
        self.queue = self.redis_queue()
        self.result_dict = {}
        self.ssh_type = ssh_type  # ssh  mysql  redis  mongo
        self.run_sql = False  # 防止执行超长命令超过待机时间时退出问题

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

    def _run_sql(self, data):
        sql_str = data.get("sql")
        limit = data.get("limit")
        offset = data.get("offset")
        try:
            limit = int(limit)
        except:
            limit = 20
        # sql_list = [str(s.replace("\n", "").strip()) + ";" for s in sql_str.split(";") if s.replace("\n", "").strip()]
        sql_list = [str(sql).replace("\n", "").replace("\r", "").strip() for sql in parsestream(sql_str)]

        sql_return = {"data_type": "sql"}
        is_stop = False
        line = 0
        data_list = []
        message = []
        self.result_dict = {}
        for sql in sql_list:
            line += 1
            t1 = time.time()
            if not is_stop:
                try:
                    self.mysql_cursor.execute(sql)
                    self.mysql_conn.commit()
                    rowcount = self.mysql_cursor.rowcount
                    # res_list = self.mysql_cursor.fetchmany(size)
                    res_list = self.mysql_cursor.fetchall()

                    res_list = self._handler_sql_result(res_list)
                    if res_list:
                        result_id = self.sql_queryset_id()
                        self.result_dict[result_id] = res_list
                        limit_data = res_list[:limit]
                        data_list.append({"rowcount": rowcount, "result_data": limit_data, "result_id": result_id})
                    t2 = time.time()
                    message.append(
                        {"sql": sql, "message": "OK", "rowcount": rowcount, "execute_time": round(t2 - t1, 6),
                         "status": 1, "result": "结果集{}".format(line)})
                except Exception as e:
                    is_stop = True
                    try:
                        args = e.args
                        if isinstance(args, tuple):
                            error_str = " - ".join([str(i) for i in args])
                        else:
                            error_str = str(args)
                    except:
                        error_str = str(e)
                    t2 = time.time()
                    message.append(
                        {"sql": sql, "message": str(error_str), "execute_time": round(t2 - t1, 6), "status": 0})
            else:
                message.append({"sql": sql, "message": "终止执行", "execute_time": 0, "status": 2})
        sql_return.update(data_list=data_list, message=message)
        self.websocket.send(json.dumps(sql_return))

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

    def _cut_database(self, data):
        self.result_dict = {}
        database = data.get("database")
        self.websocket.send(json.dumps(self.websocket._get_default_data(database)))

    def _default_data(self, data):
        self.result_dict = {}
        self.websocket.send(json.dumps(self.websocket._get_default_data()))

    def run(self):
        try:
            while not self._stop_event.is_set():
                if self.run_sql is False:
                    self.check_timeout_close()
                else:
                    self.run_sql = False
                    self.websocket.send(json.dumps({"data_type": "sql_run", "status": 0}))
                text = self.queue.get_message()
                if text:
                    try:
                        data = self._handler_command(text)
                        if isinstance(data, dict):
                            data_type = data.get("data_type")  # sql, default_data, open_database
                            """
                            1sql语句查询传参：{"data_type": "sql", "sql": "use control;select * from task_record;", "size": 20} {"data_type": "sql", "sql": "select * from user_info", "size": 50}
                            1sql语句查询返回：{
                                'data_type': 'sql', 
                                'data_list': [
                                    {
                                        'rowcount': 287596, 
                                        'result_data': [{'id': 609}]
                                    }
                                ], 
                                "message": [
                                    {'sql': 'select * from task_record;', 'message': 'OK', 'execute_time': 11.332820177078247}
                                ]
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

                            if data_type == "sql":  # 执行SQL语句
                                self.run_sql = True
                                self._run_sql(data)
                            elif data_type == "result":  # 获取上一次查询集
                                self._sql_result(data)
                            elif data_type == "open_database":  # 切换数据库
                                self._cut_database(data)
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
            app_logging.warning("MySQLThread_run_mysql_error" + str(e))
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
