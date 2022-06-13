# coding=utf-8
"""
执行前请执行
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany/uploads/workbench/icon/
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany-paas/paas-ce/paas/paas/media/applogo/
"""

import os
import shutil

import requests
import json

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class InitData:
    # 公司/企业
    # DEPARTMENT
    DEPARTMENT = {
        "dep_name": "测试企业",
        "dep_level": 0
    }

    # 初始化用户，关联DEPARTMENT
    ADMIN = {
        "username": "admin",
        "chname": "管理员",
        "position": "管理员",
        "phone": "12345678910",
        "email": "123456@qq.com",
        "bk_role": "1",
    }

    # 事件中心-概览页
    event_home = [
        {
            "button_name": "查看页面",
            "button_code": "8.1",
            "is_required": 1
        }
    ]

    # 事件中心-事件查询-事件历史
    event_RouteView1_eventHistory = [
        {
            "button_name": "查看页面",
            "button_code": "8.2.1"
        }
    ]

    # 事件中心-事件查询-告警事件
    event_RouteView1_alarmEvent = [
        # {
        #     "button_name": "查看页面",
        #     "button_code": "8.2.2"
        # }
    ]

    # 事件中心-事件运营-事件接入
    event_RouteView2_eventTriggers = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.1"
        }

    ]

    # 事件中心-事件运营-触发规则
    event_RouteView2_eventRules = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.2"
        },
        {
            "button_name": "新建规则",
            "button_code": "event_rule_create"
        },
        {
            "button_name": "修改规则",
            "button_code": "event_rule_update"
        },
        {
            "button_name": "规则开关",
            "button_code": "event_rule_on_off"
        },
        {
            "button_name": "删除规则",
            "button_code": "event_rule_delete"
        }
    ]

    # 事件中心-事件运营-执行动作
    event_RouteView2_eventActions = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.3"
        },
        {
            "button_name": "执行动作",
            "button_code": "event_action_create"
        }
    ]

    # 事件中心-智能告警-告警事件
    event_RouteView4_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.1"
        },
        {
            "button_name": "认领",
            "button_code": "event_claim_event"
        },
        {
            "button_name": "转派",
            "button_code": "event_delivery_event"
        },
        {
            "button_name": "关闭",
            "button_code": "event_close_event"
        }
    ]

    # 事件中心-智能告警-分派策略
    event_RouteView4_dispatchStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.2"
        },
        {
            "button_name": "新建分派策略",
            "button_code": "event_assign_create"
        },
        {
            "button_name": "修改分派策略",
            "button_code": "event_assign_update"
        },
        {
            "button_name": "删除分派策略",
            "button_code": "event_assign_delete"
        },
        {
            "button_name": "分派策略开关",
            "button_code": "event_assign_on_off"
        }
    ]

    # 事件中心-智能告警-通知策略
    event_RouteView4_notificationStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.3"
        },
        {
            "button_name": "新建通知策略",
            "button_code": "event_inform_create"
        },
        {
            "button_name": "修改通知策略",
            "button_code": "event_inform_update"
        },
        {
            "button_name": "删除通知策略",
            "button_code": "event_inform_delete"
        },
        {
            "button_name": "新建通知组",
            "button_code": "event_inform_group_create"
        },
        {
            "button_name": "修改通知组",
            "button_code": "event_inform_group_update"
        },
        {
            "button_name": "删除通知组",
            "button_code": "event_inform_group_delete"
        }
    ]

    # 事件中心-平台设置-事件模板
    event_RouteView3_packs = [
        {
            "button_name": "查看页面",
            "button_code": "8.5.1"
        },
        {
            "button_name": "卸载",
            "button_code": "event_pack_uninstall"
        },
        {
            "button_name": "安装",
            "button_code": "event_pack_install"
        }
    ]

    # 事件中心-平台设置-系统设置
    event_RouteView3_systemSetting = [
        {
            "button_name": "查看页面",
            "button_code": "8.5.2"
        },
        {
            "button_name": "修改配置",
            "button_code": "event_settings"
        }
    ]

    # 智能巡检-概览页
    auto_home = [
        {
            "button_name": "查看页面",
            "button_code": "9.1",
            "is_required": 1
        }
    ]
    # 智能巡检-智能巡检-快速巡检
    auto_RouteView_fastPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.1"
        }
    ]
    # 智能巡检-智能巡检-定时巡检
    auto_RouteView_timingPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.2"
        },
        {
            "button_name": "启用定时巡检",
            "button_code": "auto_timing_patrol_start"
        },
        {
            "button_name": "暂停定时巡检",
            "button_code": "auto_timing_patrol_stop"
        },
        {
            "button_name": "新建定时巡检",
            "button_code": "auto_timing_patrol_create"
        },
        {
            "button_name": "修改定时巡检",
            "button_code": "auto_timing_patrol_update"
        },
        {
            "button_name": "删除定时巡检",
            "button_code": "auto_timing_patrol_delete"
        }
    ]
    # 智能巡检-智能巡检-巡检历史
    auto_RouteView_patrolLog = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.3"
        },
        {
            "button_name": "删除巡检历史",
            "button_code": "auto_patrol_delete"
        }
    ]
    # 智能巡检-巡检管理-巡检模板
    auto_RouteView1_patrolTemplate = [
        {
            "button_name": "查看页面",
            "button_code": "9.3.1"
        },
        {
            "button_name": "新建巡检模板",
            "button_code": "auto_patrol_template_create"
        },
        {
            "button_name": "修改巡检模板",
            "button_code": "auto_patrol_template_update"
        },
        {
            "button_name": "删除巡检模板",
            "button_code": "auto_patrol_template_delete"
        },
        {
            "button_name": "导入巡检模板",
            "button_code": "auto_patrol_template_import"
        },
        {
            "button_name": "导出巡检模板",
            "button_code": "auto_patrol_template_export"
        },
        {
            "button_name": "执行巡检模板",
            "button_code": "auto_patrol_template_execute"
        },
        {
            "button_name": "查看模板内容",
            "button_code": "auto_patrol_template_details"
        },
        {
            "button_name": "修改模板内容",
            "button_code": "auto_patrol_template_details_update"
        }
    ]

    event = event_home + event_RouteView1_eventHistory + event_RouteView1_alarmEvent + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView3_packs + event_RouteView4_alarmEvent + event_RouteView4_dispatchStrategy + event_RouteView4_notificationStrategy + event_RouteView3_systemSetting

    auto = auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate

    general = event_home + event_RouteView1_eventHistory + event_RouteView1_alarmEvent + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView4_alarmEvent + auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate

    #  菜单
    MENU_LIST = [
        {
            "menu_name": "事件中心",
            "menu_code": "event",
            "menu_type": "platform",
            "menu_address": "/o/event",
            "priority": "8",
            "platform_cname": "event",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "8.1",
                    "platform_cname": "event",
                    "children": [],
                    "buttons": event_home
                },
                {
                    "menu_name": "事件查询",
                    "menu_code": "RouteView1",
                    "menu_type": "directory",
                    "menu_address": "/eventQuery",
                    "priority": "8.2",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件历史",
                            "menu_code": "eventHistory",
                            "menu_type": "menu",
                            "menu_address": "/eventQuery/eventHistory",
                            "priority": "8.2.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView1_eventHistory
                        }
                    ]
                },
                {
                    "menu_name": "事件运营",
                    "menu_code": "RouteView2",
                    "menu_type": "directory",
                    "menu_address": "/eventOperation",
                    "priority": "8.3",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件接入",
                            "menu_code": "eventTriggers",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventTriggers",
                            "priority": "8.3.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventTriggers
                        },
                        {
                            "menu_name": "触发规则",
                            "menu_code": "eventRules",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventRules",
                            "priority": "8.3.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventRules
                        },
                        {
                            "menu_name": "执行动作",
                            "menu_code": "eventActions",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventActions",
                            "priority": "8.3.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventActions
                        }
                    ]
                },
                {
                    "menu_name": "智能告警",
                    "menu_code": "RouteView4",
                    "menu_type": "directory",
                    "menu_address": "/intelligentAlarm",
                    "priority": "8.4",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/alarmEvent",
                            "priority": "8.4.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_alarmEvent
                        },
                        {
                            "menu_name": "分派策略",
                            "menu_code": "dispatchStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/dispatchStrategy",
                            "priority": "8.4.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_dispatchStrategy
                        },
                        {
                            "menu_name": "通知策略",
                            "menu_code": "notificationStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/notificationStrategy",
                            "priority": "8.4.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_notificationStrategy
                        }
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView3",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "8.5",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件模板",
                            "menu_code": "packs",
                            "menu_type": "menu",
                            "menu_address": "/setting/packs",
                            "priority": "8.5.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView3_packs
                        },
                        {
                            "menu_name": "系统设置",
                            "menu_code": "systemSetting",
                            "menu_type": "menu",
                            "menu_address": "/setting/systemSetting",
                            "priority": "8.5.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView3_systemSetting
                        }
                    ]
                }
            ]
        },
        {
            "menu_name": "智能巡检",
            "menu_code": "auto",
            "menu_type": "platform",
            "menu_address": "/o/auto",
            "priority": "9",
            "platform_cname": "auto",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "9.1",
                    "platform_cname": "auto",
                    "children": [],
                    "buttons": auto_home
                },
                {
                    "menu_name": "智能巡检",
                    "menu_code": "RouteView",
                    "menu_type": "directory",
                    "menu_address": "smartPatrol",
                    "priority": "9.2",
                    "platform_cname": "auto",
                    "children": [
                        {
                            "menu_name": "快速巡检",
                            "menu_code": "fastPatrol",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/fastPatrol",
                            "priority": "9.2.1",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_fastPatrol
                        },
                        {
                            "menu_name": "定时巡检",
                            "menu_code": "timingPatrol",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/timingPatrol",
                            "priority": "9.2.2",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_timingPatrol
                        },
                        {
                            "menu_name": "巡检历史",
                            "menu_code": "patrolLog",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/patrolLog",
                            "priority": "9.2.3",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_patrolLog
                        }
                    ]
                },
                {
                    "menu_name": "巡检管理",
                    "menu_code": "RouteView1",
                    "menu_type": "directory",
                    "menu_address": "patrolManage",
                    "priority": "9.3",
                    "platform_cname": "auto",
                    "children": [
                        {
                            "menu_name": "巡检模板",
                            "menu_code": "patrolTemplate",
                            "menu_type": "menu",
                            "menu_address": "/patrolManage/patrolTemplate",
                            "priority": "9.3.1",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView1_patrolTemplate
                        }
                    ]
                }
            ]
        }
    ]

    # 内置权限
    BUILD_IN_STRATEGY_LIST = [
        {
            "strategy_name": "超级管理员",
            "strategy_type": "built-in",
            "description": "拥有所有平台的所有权限，并登陆【统一权限】",
            "platform_name_list": ["event", "auto"],
            "buttons": event + auto
        },
        {
            "strategy_name": "事件中心管理员",
            "strategy_type": "built-in",
            "description": "拥有【事件中心】所有权限",
            "platform_name_list": ["event"],
            "buttons": event
        },
        {
            "strategy_name": "智能巡检管理员",
            "strategy_type": "built-in",
            "description": "拥有【智能巡检】所有权限",
            "platform_name_list": ["auto"],
            "buttons": auto
        },
        {
            "strategy_name": "普通用户",
            "strategy_type": "built-in",
            "description": "普通用户，仅可以访问工作台和授权的平台",
            "platform_name_list": ["event", "auto"],
            "buttons": general
        },
    ]

    # 导航分组
    NAV_GROUP = {
        "group_name": "智能运维",
        "nav_list": [
            {
                "nav_name": "事件中心",
                "nav_url": "/o/event/",
                "describe": "事件中心和故障自愈",
                "icon_name": "event.png"
            },
            {
                "nav_name": "智能巡检",
                "nav_url": "/o/auto/",
                "describe": "运维自动化巡检",
                "icon_name": "auto.png"
            }
        ]
    }

    PLATFORM_TEMPLATE = [
        {
            "platform_name": "事件中心",
            "platform_code": "event",
            "template_list": [
                {
                    "id": 8001,
                    "type": "事件中心告警通知",
                    "title_one": "事件中心告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8002,
                    "type": "事件中心认领告警通知",
                    "title_one": "事件中心认领告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_claim_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8003,
                    "type": "事件中心关闭告警通知",
                    "title_one": "事件中心关闭告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_close_alert_info",
                    "platform": "事件中心"
                },
            ]
        },
    ]


class OpsAnyApi:
    def __init__(self, paas_domain, username, password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code == 200:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):
        try:
            login_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(self.login_url, data=login_form, verify=False)
            if resp.status_code == 200:
                return self.session.cookies.get("bk_token")
            return ""
        except:
            return False

    def init_event_auto_menu_strategy(self):
        """rbac 初始化菜单，权限策略"""
        try:
            API = "/o/rbac//api/rbac/v0_1/init_ee_data/"
            URL = self.paas_domain + API
            data = InitData()

            data = {
                "ADMIN": data.ADMIN,
                "DEPARTMENT": data.DEPARTMENT,
                "MENU_LIST": data.MENU_LIST,
                "BUILD_IN_STRATEGY_LIST": data.BUILD_IN_STRATEGY_LIST
            }
            response = self.session.post(url=URL, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def workbench_add_nav(self):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data = InitData()
            nav_data = data.NAV_GROUP
            nav_data.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps(nav_data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def workbench_add_message_template(self):
        """工作台初始化站内信模板"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-message-template/"
            TEMPLATE_API = self.paas_domain + NAV_API

            data = InitData()
            platform_data = {"platform_list": data.PLATFORM_TEMPLATE}

            response = self.session.post(url=TEMPLATE_API, data=json.dumps(platform_data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def init_event_st2(self, st2_url, st2_username, st2_password):
        """初始化事件中心st2"""
        try:
            API = "/o/event//api/event/v0_1/init-st2/"
            URL = self.paas_domain + API
            if not all([st2_url, st2_username, st2_password]):
                return 0, "初始化失败，缺失参数"
            data = {
                "STACK_STORM_URL": st2_url,
                "STACK_STORM_USERNAME": st2_username,
                "STACK_STORM_PASSWORD": st2_password
            }
            response = self.session.post(url=URL, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)


def start(paas_domain, username, password, st2_url="", st2_username="", st2_password=""):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)

    # 初始化事件中心，智能巡检菜单，权限策略
    rbac_status, rbac_data = run_obj.init_event_auto_menu_strategy()
    print("[SUCCESS] init menu strategy success") if rbac_status else print(
        "[ERROR] init menu strategy error, error info: {}".format(rbac_data))

    # 初始化工作台导航目录
    add_nav_status, add_nav_data = run_obj.workbench_add_nav()
    print("[SUCCESS] add nav success") if add_nav_status else print(
        "[ERROR] add nav error, error info: {}".format(add_nav_data))

    # 初始化工作台站内信模板
    add_nav_status, add_nav_data = run_obj.workbench_add_message_template()
    print("[SUCCESS] add message_template success") if add_nav_status else print(
        "[ERROR] add message_template error, error info: {}".format(add_nav_data))

    # 初始化StackStorm
    st2_status, st2_data = run_obj.init_event_st2(st2_url, st2_username, st2_password)
    print("[SUCCESS] init st2 success:") if st2_status else print(
        "[ERROR] init st2 error info, error info: {}".format(str(st2_data)))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--st2_url", help="StackStorm service url.", required=False)
    parameter.add_argument("--st2_username", help="StackStorm service username.", required=False)
    parameter.add_argument("--st2_password", help="StackStorm service password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain
    username = options.username
    password = options.password
    st2_url = options.st2_url
    st2_username = options.st2_username
    st2_password = options.st2_password
    start(domain, username, password, st2_url=st2_url, st2_username=st2_username, st2_password=st2_password)
