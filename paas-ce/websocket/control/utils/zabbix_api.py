# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

import requests
import json
import time
import datetime


class ZabbixApi(object):
    def __init__(self, username, password, url, use_authenticate=False, session='', timeout=None):
        self.username = username
        self.passworld = password
        self.url = url
        self.session = self.login()

    def get_default_group(self):
        host_id = self.get_host_group("Opsany_Group")
        if not host_id:
            host_id = self.create_host_group("Opsany_Group")
        return host_id

    def login(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        body = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.passworld
            },
            "id": 1,
            "auth": None
        }
        a = session.post(self.url, data=json.dumps(body), verify=False)
        if a.status_code == 200:
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return ""
        return ""

    def create_host_group(self, name):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "hostgroup.create",
                "params": {
                    "name": name
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result").get("groupids")[0]
            else:
                return None
        return None

    def get_host_item_count(self, hostids):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output": "extend",
                    "hostids": hostids,
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                data = a.json().get("result")
                return len(data)
            else:
                return None
        return None

    def create_host(self, host_name, name, ip, group_id, description='', templateid=10284, **kwargs):
        if kwargs:
            host_name = kwargs.get("host_name")
            name = kwargs.get("name")
            ip = kwargs.get("ip")
            group_id = kwargs.get("group_id")
            description = kwargs.get("description")
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.create",
                "params": {
                    "host": host_name,                  # 主机名
                    "name": name,                       # 显示名
                    "description": description,
                    "interfaces": [
                        {
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": ip,
                            "dns": "",
                            "port": "10050",
                        }
                    ],
                    "groups": [
                        {
                            "groupid": group_id,
                        }
                    ],
                    "tags": [
                    ],
                    "templates": [
                    ],
                    "macros": [
                    ],
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")["hostids"][0]
            else:
                return None
        return None

    def get_host_group(self, name):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "output": "extend",
                    "filter": {
                        "name": [
                            name
                        ]
                    }
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                print(a.json())
                return a.json().get("result")[0].get("groupid")
            else:
                return None
        return None

    def get_host_by_name(self, ip=''):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {
                        "host": [
                            ip
                        ]
                    }
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")[0]
            else:
                return None
        return None

    def create_net_equipment(self, host_name, name, description, ip, group_id, templateid, team_name):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.create",
                "params": {
                    "host": host_name,                  # 主机名
                    "name": name,                       # 显示名
                    "description": description,
                    "interfaces": [
                        {
                            "type": "2",
                            "main": "1",
                            "useip": "1",
                            "ip": str(ip),
                            "dns": "",
                            "hostid": "10333",
                            "port": "161"
                        }
                    ],
                    "groups": [
                        {
                            "groupid": str(group_id),
                        }
                    ],
                    "templates": [
                        {
                            "templateid": "10226"
                        }
                    ],
                    "macros": [
                        {
                            "macro": "{$SNMP_COMMUNITY}",
                            "value": team_name
                        }
                    ],
                },
                "auth": self.session,
                "id": 1
            }
            # print(body)
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")["hostids"][0]
            else:
                return None
        return None

    def update_host(self, host_id, tags_list, temp_list, macros_list):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": host_id,
                    "tags": tags_list,
                    "templates": temp_list,
                    "macros": macros_list,
                },
                "auth": self.session,
                "id": 1
            }
            res = session.post(self.url, data=json.dumps(body), verify=False)
            print("res", res.json())
            if res.json().get("result"):
                return res.json().get("result")["hostids"][0]
            else:
                return None
        return None

    def delete_host(self, host_list):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.delete",
                "params": host_list,
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_all_template(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "template.get",
                "params": {
                    "output": "extend",
                    "limitSelects": [
                        "name",
                        "templateid"
                    ]
                    },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_host_state(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": [
                        "host",
                        "status",
                        "available",
                        "ipmi_available",
                        "jmx_available",
                        "snmp_available"
                        ],
                    },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_trigger_count(self, hostids):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "trigger.get",
                "params": {
                    "hostids": hostids,
                    "output": "extend",
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body))
            if a.json().get("result"):
                return len(a.json().get("result"))
            else:
                return None
        return None

    def stop_or_start_zabbix(self, host_id, status):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": host_id,
                    "status": status        # 0为启用，1为禁用
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def level_count(self, host_id):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "event.get",
                "params": {
                    "output": ["hostids", "acknowledged", "objectid", "name", "severity", "acknowledged", "clock", "value"],
                    "acknowledged": False,
                    "sortfield": [
                        "clock"
                    ],
                    "hostids": host_id
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def problem_info(self, host_id=None, application_id=None, trigger_id=None):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "problem.get",
                "params": {
                    "output": "extend",
                    "recent": "true"
                },
                "auth": self.session,
                "id": 1
            }
            if host_id:
                body["params"]["hostids"] = host_id
            if application_id:
                body["params"]["applicationids"] = application_id
            if trigger_id:
                body["params"]["objectids"] = trigger_id
            a = session.post(self.url, data=json.dumps(body), verify=False)
            print(a.json())
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_application(self, host_id):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "application.get",
                "params": {
                    "output": "extend",
                    "sortfield": "name",
                    "hostids": host_id
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_trigger(self, host_id):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "trigger.get",
                "params": {
                    "output": [
                        "triggerid",
                        "description",
                        "priority"
                    ],
                    # "hostids": host_id,
                    "triggerids": host_id,
                    "expandDescription": True,
                    "expandExpression": True,
                    # "selectDependencies": {
                    #     "output": [
                    #         "triggerid",
                    #         "description"
                    #     ],
                    #     "expandDescription": True,
                    #     "expandExpression": True,
                    # }
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            # print(a.json())
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_history(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "event.get",
                "params": {
                    "output": "extend",
                    # "eventids": "",
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            # print(a.json())
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def zabbix_agent_status(self, host_id):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["status"],
                    "hostids": host_id
                },
                "auth": self.session,
                "id": 1
            }
            res = session.post(self.url, data=json.dumps(body), verify=False)
            if res.json().get("result"):
                return res.json().get("result")
            else:
                return None
        return None

    def get_action(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "action.get",
                "params": {
                    "output": "extend",
                    "actionids": "3"
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                print(a.json())
                return a.json().get("result")
            else:
                return None
        return None

    def test(self):
        """
        调用alert通过actionids去查告警信息
        """
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "alert.get",
                "params": {
                    "output": "extend",
                    # "actionids": "7"
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            # print(a.json())
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_event_top_count(self, host_id, time_from="", time_till=""):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "event.get",
                "params": {
                    "output": [
                        "severity",
                        "name",
                        "clock",
                        "objectid",
                        "eventid"
                    ],
                    "hostids": host_id
                },
                "auth": self.session,
                "id": 1
            }
            if time_from:
                # time_from = "2020-12-23 10:55:24"
                d = datetime.datetime.strptime(time_from, "%Y-%m-%d %H:%M:%S")
                body["params"]["time_from"] = str(time.mktime(d.timetuple())).rsplit(".")[0]
            if time_till:
                f = datetime.datetime.strptime(time_till, "%Y-%m-%d %H:%M:%S")
                body["params"]["time_till"] = str(time.mktime(f.timetuple())).rsplit(".")[0]
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None


def count_func(count_list, count_field):
    lt1 = []
    end_data = []
    for i in count_list:
        lt1.append(i.get(count_field))
    list(set(lt1))
    for j in lt1:
        for k in count_list:
            if k.get(count_field) == j:
                pass


# if __name__ == "__main__":
#     master = {
#                 "id": 1,
#                 "name": "Local-Master",
#                 "type": "本地",
#                 "api1": "https://106.15.50.194:8011",
#                 "api2": "https://106.15.50.194:8012",
#                 "username1": "saltapi",
#                 "username2": "saltapi",
#                 "password1": "123456.coM",
#                 "password2": "123456.coM",
#                 "port1": "",
#                 "port2": "",
#                 "state1": True,
#                 "state2": True,
#                 "zabbix_username": "admin",
#                 "zabbix_password": "123456.coM",
#                 "zabbix_url": "http://monitor.opsany.cn/api_jsonrpc.php",
#                 "zabbix_state": True,
#                 "count": 4
#             }
#     zabbix_obj = ZabbixApi(
#             "admin",      # user
#             "123456.coM",      # password
#             "http://monitor.opsany.com/api_jsonrpc.php",           # url
#             )
#     host_list = ["10354", "10356"]
#     dt = {}
#     for i in host_list:
#         a = zabbix_obj.get_event_top_count(i)
#         dt[i] = a
#     print(dt)
#     lt = []
#
#
#     for k, v in dt.items():
#         for i in v:
#             i["zabbix_host_id"] = k
#             pass




    # dt = {}
    # lt = []
    # for i in a:
    #     print(i)
    #     key = "objectid"
    #     value = i.get(key)
    #     lt.append(value)
    # for j in lt:
    #     if dt.get(j, 0):
    #         index = dt[j]
    #         index += 1
    #         dt[j] = index
    #     else:
    #         dt[j] = 1
    # print(dt)
    # asd = 0
    # for k, v in dt.items():
    #     if zabbix_obj.get_trigger(k):
    #         asd += 1
    #         print("asd:", asd)
    #         print(zabbix_obj.get_trigger(k))
    #         print(v)
    #         print("=========================")
    # print(zabbix_obj.get_trigger("16992"))
    # b = zabbix_obj.get_trigger("16671")
    # print(b)
    # host_name, name, ip, group_id, description='', templateid=10284, **kwargs
    # host_centos_six = {
    #     "ip": "81.70.152.26",
    #     "host_name": "ins-cuy1ngqt",
    #     "name": "centos6-agent",
    #     "group_id": "4",
    #     "templateid": "10284",
    # }
    # a = zabbix_obj.create_host(
    #     host_centos_six.get("host_name"),
    #     host_centos_six.get("name"),
    #     host_centos_six.get("ip"),
    #     host_centos_six.get("group_id"),
    #     host_centos_six.get("description", "描述"),
    #     host_centos_six.get("templateid")
    # )
    # print(a)
    # host_id, tags_list, temp_list, macros_list
    # a = zabbix_obj.update_host("10332", [], ["10284"], [
    #     {
    #         "macro": "{$PASS}",
    #         "value": "password"
    #     }
    # ])
    # print(a)
#     c = zabbix_obj.zabbix_agent_status("11346")
#     if c:
#         for i in c:
#             print(i)




    # c = zabbix_obj.problem_info("11167")       # 获取监控类型
    # c = zabbix_obj.problem_info("10084")       # 获取监控类型
    # print(c)
    # c = zabbix_obj.level_count("10084")
    # dict = {}
    # for i in c:
    #     if not dict.get(i.get("objectid")):
    #         dict[i.get("objectid")] = {"name": i.get("name"), "value": i.get("value"), "level": i.get("severity")}
    #     else:
    #         dict[i.get("objectid")] = {"name": i.get("name"), "value": i.get("value"), "level": i.get("severity")}
    # for k, v in dict.items():
    #     if v.get("value") == "1":
    #         print(k, v)
    # dt = {'actionid': '2', 'name': 'Auto discovery. Linux servers.', 'eventsource': '1', 'status': '1', 'esc_period': '0', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [{'conditiontype': '10', 'operator': '0', 'value': '0', 'value2': '', 'formulaid': 'B'}, {'conditiontype': '8', 'operator': '0', 'value': '9', 'value2': '', 'formulaid': 'C'}, {'conditiontype': '12', 'operator': '2', 'value': 'Linux', 'value2': '', 'formulaid': 'A'}], 'eval_formula': 'A and B and C'}, 'operations': [{'operationid': '1', 'actionid': '2', 'operationtype': '6', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'optemplate': [{'templateid': '10001'}]}, {'operationid': '2', 'actionid': '2', 'operationtype': '4', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opgroup': [{'groupid': '2'}]}], 'recoveryOperations': []}, {'actionid': '3', 'name': 'Report problems to Zabbix administrators', 'eventsource': '0', 'status': '1', 'esc_period': '1h', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [], 'eval_formula': ''}, 'operations': [{'operationid': '3', 'actionid': '3', 'operationtype': '0', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}, 'opmessage_grp': [{'usrgrpid': '7'}], 'opmessage_usr': []}], 'recoveryOperations': [{'operationid': '7', 'actionid': '3', 'operationtype': '11', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}}]}, {'actionid': '4', 'name': 'Report not supported items', 'eventsource': '3', 'status': '1', 'esc_period': '1h', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [{'conditiontype': '23', 'operator': '0', 'value': '0', 'value2': '', 'formulaid': 'A'}], 'eval_formula': 'A'}, 'operations': [{'operationid': '4', 'actionid': '4', 'operationtype': '0', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}, 'opmessage_grp': [{'usrgrpid': '7'}], 'opmessage_usr': []}], 'recoveryOperations': [{'operationid': '8', 'actionid': '4', 'operationtype': '11', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}}]}, {'actionid': '5', 'name': 'Report not supported low level discovery rules', 'eventsource': '3', 'status': '1', 'esc_period': '1h', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [{'conditiontype': '23', 'operator': '0', 'value': '2', 'value2': '', 'formulaid': 'A'}], 'eval_formula': 'A'}, 'operations': [{'operationid': '5', 'actionid': '5', 'operationtype': '0', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}, 'opmessage_grp': [{'usrgrpid': '7'}], 'opmessage_usr': []}], 'recoveryOperations': [{'operationid': '9', 'actionid': '5', 'operationtype': '11', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}}]}, {'actionid': '6', 'name': 'Report unknown triggers', 'eventsource': '3', 'status': '1', 'esc_period': '1h', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [{'conditiontype': '23', 'operator': '0', 'value': '4', 'value2': '', 'formulaid': 'A'}], 'eval_formula': 'A'}, 'operations': [{'operationid': '6', 'actionid': '6', 'operationtype': '0', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}, 'opmessage_grp': [{'usrgrpid': '7'}], 'opmessage_usr': []}], 'recoveryOperations': [{'operationid': '10', 'actionid': '6', 'operationtype': '11', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}}]}, {'actionid': '7', 'name': '测试', 'eventsource': '0', 'status': '0', 'esc_period': '1h', 'pause_suppressed': '1', 'filter': {'evaltype': '0', 'formula': '', 'conditions': [{'conditiontype': '4', 'operator': '5', 'value': '0', 'value2': '', 'formulaid': 'A'}], 'eval_formula': 'A'}, 'operations': [{'operationid': '11', 'actionid': '7', 'operationtype': '0', 'esc_period': '0', 'esc_step_from': '1', 'esc_step_to': '1', 'evaltype': '0', 'opconditions': [], 'opmessage': {'default_msg': '1', 'subject': '', 'message': '', 'mediatypeid': '0'}, 'opmessage_grp': [], 'opmessage_usr': [{'userid': '1'}]}], 'recoveryOperations': []}
