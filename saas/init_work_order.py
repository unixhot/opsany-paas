import argparse
import json

import requests
import urllib3

urllib3.disable_warnings()

class InitData:
    work_order_list = {
        "work_order_list": [
            {
                "update_public_fields_type": "1",
                "update_public_fields_form_type": "2",
                "update_public_api_type": "2",
                "update_role_type": "2",
                "is_online": "2",
                "can_cancel": "2",
                "work_flow_info_dict": {
                    "id": 34,
                    "create_user": "admin",
                    "update_user": "admin",
                    "describe": "通用服务请求流程，职能经理审批。",
                    "name": "通用服务请求流程-有审批",
                    "can_delete": False,
                    "status": True,
                    "director": "admin",
                    "public_table_id": 1,
                    "update_time": "2023-08-24 07:43:44"
                },
                "work_flow_fields_group_dict": {},
                "work_flow_fields_dict": {
                    "241": {
                        "id": 241,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 137,
                        "field_from": "2",
                        "public_field": 1,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": "请输入标题",
                        "required": True,
                        "index": 1,
                        "group": None,
                        "can_delete": False,
                        "can_update": True
                    },
                    "242": {
                        "id": 242,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 137,
                        "field_from": "2",
                        "public_field": 2,
                        "default": None,
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "field_type": None,
                        "describe": "请选择紧急程度",
                        "required": True,
                        "index": 2,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "243": {
                        "id": 243,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 137,
                        "field_from": "2",
                        "public_field": 3,
                        "default": None,
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "field_type": None,
                        "describe": "请选择优先级",
                        "required": True,
                        "index": 3,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "244": {
                        "id": 244,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 137,
                        "field_from": "2",
                        "public_field": 4,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": "请输入申请内容",
                        "required": True,
                        "index": 4,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "245": {
                        "id": 245,
                        "code": "e12b209f-2d9b-43bb-a911-71973fe27717",
                        "name": "审批意见",
                        "field_rule": None,
                        "work_flow_step": 138,
                        "field_from": "2",
                        "public_field": None,
                        "default": "1",
                        "other_info": {
                            "selectOptions": [
                                {
                                    "name": "通过",
                                    "key": "1"
                                },
                                {
                                    "name": "拒绝",
                                    "key": "2"
                                }
                            ]
                        },
                        "field_type": "radio",
                        "describe": None,
                        "required": True,
                        "index": 1,
                        "group": None,
                        "can_delete": False,
                        "can_update": False
                    },
                    "246": {
                        "id": 246,
                        "code": "81df9c7f-a7e1-44d0-b5f9-46bfc053e22a",
                        "name": "备注",
                        "field_rule": None,
                        "work_flow_step": 138,
                        "field_from": "2",
                        "public_field": None,
                        "default": "通过",
                        "other_info": {},
                        "field_type": "textarea",
                        "describe": None,
                        "required": True,
                        "index": 2,
                        "group": None,
                        "can_delete": False,
                        "can_update": False
                    },
                    "247": {
                        "id": 247,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 139,
                        "field_from": "2",
                        "public_field": 9,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": None,
                        "required": True,
                        "index": 1,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    }
                },
                "work_flow_field_public_fields_dict": {
                    "1": {
                        "id": 1,
                        "code": "title",
                        "name": "标题",
                        "other_info": {},
                        "rule": None,
                        "field_type": "string",
                        "default": "",
                        "describe": "请输入标题",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "2": {
                        "id": 2,
                        "code": "urgency",
                        "name": "紧急程度",
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "rule": None,
                        "field_type": "select",
                        "default": "",
                        "describe": "请选择紧急程度",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "3": {
                        "id": 3,
                        "code": "priority",
                        "name": "优先级",
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "rule": None,
                        "field_type": "select",
                        "default": "",
                        "describe": "请选择优先级",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "4": {
                        "id": 4,
                        "code": "apply_content",
                        "name": "申请内容",
                        "other_info": {},
                        "rule": None,
                        "field_type": "richtext",
                        "default": "",
                        "describe": "请输入申请内容",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "9": {
                        "id": 9,
                        "code": "RESULT",
                        "name": "处理结果",
                        "other_info": {},
                        "rule": None,
                        "field_type": "richtext",
                        "default": None,
                        "describe": "填写处理结果",
                        "built_in": False,
                        "create_user": "admin",
                        "update_user": "admin"
                    }
                },
                "work_flow_field_public_form_dict": {
                    "1": {
                        "id": 1,
                        "name": "基础表单",
                        "describe": "该表单为内置公共表单",
                        "built_in": True,
                        "update_user_username": "admin",
                        "update_user_ch_name": "管理员",
                        "public_field_list": [
                            1,
                            2,
                            3,
                            4
                        ]
                    }
                },
                "work_flow_role_dict": {},
                "work_flow_department_dict": {},
                "work_flow_field_rule_dict": {},
                "work_flow_public_api_dict": {},
                "work_flow_step_list": [
                    {
                        "id": 135,
                        "name": "开始",
                        "step_type": "0",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": None,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": []
                    },
                    {
                        "id": 136,
                        "name": "结束",
                        "step_type": "0",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": None,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": []
                    },
                    {
                        "id": 137,
                        "name": "提交工单",
                        "step_type": "3",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": 0,
                        "visible_type": "0",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": [
                            241,
                            242,
                            243,
                            244
                        ]
                    },
                    {
                        "id": 138,
                        "name": "部门经理审批",
                        "step_type": "2",
                        "can_delete": True,
                        "index": 0,
                        "other_info": {},
                        "approval_method": 1,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [
                            "admin"
                        ],
                        "director": None,
                        "fields_list": [
                            245,
                            246
                        ]
                    },
                    {
                        "id": 139,
                        "name": "工程师处理",
                        "step_type": "1",
                        "can_delete": True,
                        "index": 0,
                        "other_info": {},
                        "approval_method": 0,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [
                            "admin"
                        ],
                        "director": None,
                        "fields_list": [
                            247
                        ]
                    }
                ],
                "work_flow_step_line_list": [
                    {
                        "id": 109,
                        "name": "",
                        "other_info": {},
                        "work_flow_id": 34,
                        "use_line": {
                            "start": 135,
                            "end": 137
                        }
                    },
                    {
                        "id": 113,
                        "name": "默认",
                        "other_info": {},
                        "work_flow_id": 34,
                        "use_line": {
                            "start": 138,
                            "end": 139
                        }
                    },
                    {
                        "id": 114,
                        "name": "默认",
                        "other_info": {},
                        "work_flow_id": 34,
                        "use_line": {
                            "start": 139,
                            "end": 136
                        }
                    },
                    {
                        "id": 115,
                        "name": "默认",
                        "other_info": {},
                        "work_flow_id": 34,
                        "use_line": {
                            "start": 137,
                            "end": 138
                        }
                    }
                ],
                "work_order_list": [
                    {
                        "name": "云资源申请",
                        "director": "admin",
                        "order_type": "请求管理",
                        "visible_type": "0",
                        "describe": None,
                        "icon_id": 4,
                        "folder_name": "默认分组",
                        "department_id": None,
                        "role_list_id": [],
                        "user_list_id": [],
                        
                    }
                ]
            },
            {
                "update_public_fields_type": "1",
                "update_public_fields_form_type": "2",
                "update_public_api_type": "2",
                "update_role_type": "2",
                "is_online": "2",
                "can_cancel": "2",
                "work_flow_info_dict": {
                    "id": 36,
                    "create_user": "admin",
                    "update_user": "admin",
                    "describe": "通用服务请求流程，无审批。",
                    "name": "通用服务请求流程-无审批",
                    "can_delete": False,
                    "status": True,
                    "director": "admin",
                    "public_table_id": 1,
                    "update_time": "2023-08-24 07:44:40"
                },
                "work_flow_fields_group_dict": {},
                "work_flow_fields_dict": {
                    "261": {
                        "id": 261,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 148,
                        "field_from": "2",
                        "public_field": 1,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": "请输入标题",
                        "required": True,
                        "index": 1,
                        "group": None,
                        "can_delete": False,
                        "can_update": True
                    },
                    "262": {
                        "id": 262,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 148,
                        "field_from": "2",
                        "public_field": 2,
                        "default": None,
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "field_type": None,
                        "describe": "请选择紧急程度",
                        "required": True,
                        "index": 2,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "263": {
                        "id": 263,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 148,
                        "field_from": "2",
                        "public_field": 3,
                        "default": None,
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "field_type": None,
                        "describe": "请选择优先级",
                        "required": True,
                        "index": 3,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "264": {
                        "id": 264,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 148,
                        "field_from": "2",
                        "public_field": 4,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": "请输入申请内容",
                        "required": True,
                        "index": 4,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    },
                    "267": {
                        "id": 267,
                        "code": None,
                        "name": None,
                        "field_rule": None,
                        "work_flow_step": 150,
                        "field_from": "2",
                        "public_field": 9,
                        "default": None,
                        "other_info": {},
                        "field_type": None,
                        "describe": None,
                        "required": True,
                        "index": 1,
                        "group": None,
                        "can_delete": True,
                        "can_update": True
                    }
                },
                "work_flow_field_public_fields_dict": {
                    "1": {
                        "id": 1,
                        "code": "title",
                        "name": "标题",
                        "other_info": {},
                        "rule": None,
                        "field_type": "string",
                        "default": "",
                        "describe": "请输入标题",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "2": {
                        "id": 2,
                        "code": "urgency",
                        "name": "紧急程度",
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "rule": None,
                        "field_type": "select",
                        "default": "",
                        "describe": "请选择紧急程度",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "3": {
                        "id": 3,
                        "code": "priority",
                        "name": "优先级",
                        "other_info": {
                            "selectOptions": [
                                {
                                    "key": "1",
                                    "name": "低"
                                },
                                {
                                    "key": "2",
                                    "name": "中"
                                },
                                {
                                    "key": "3",
                                    "name": "高"
                                }
                            ]
                        },
                        "rule": None,
                        "field_type": "select",
                        "default": "",
                        "describe": "请选择优先级",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "4": {
                        "id": 4,
                        "code": "apply_content",
                        "name": "申请内容",
                        "other_info": {},
                        "rule": None,
                        "field_type": "richtext",
                        "default": "",
                        "describe": "请输入申请内容",
                        "built_in": True,
                        "create_user": "admin",
                        "update_user": "admin"
                    },
                    "9": {
                        "id": 9,
                        "code": "RESULT",
                        "name": "处理结果",
                        "other_info": {},
                        "rule": None,
                        "field_type": "richtext",
                        "default": None,
                        "describe": "填写处理结果",
                        "built_in": False,
                        "create_user": "admin",
                        "update_user": "admin"
                    }
                },
                "work_flow_field_public_form_dict": {
                    "1": {
                        "id": 1,
                        "name": "基础表单",
                        "describe": "该表单为内置公共表单",
                        "built_in": True,
                        "update_user_username": "admin",
                        "update_user_ch_name": "管理员",
                        "public_field_list": [
                            1,
                            2,
                            3,
                            4
                        ]
                    }
                },
                "work_flow_role_dict": {},
                "work_flow_department_dict": {},
                "work_flow_field_rule_dict": {},
                "work_flow_public_api_dict": {},
                "work_flow_step_list": [
                    {
                        "id": 146,
                        "name": "开始",
                        "step_type": "0",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": None,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": []
                    },
                    {
                        "id": 147,
                        "name": "结束",
                        "step_type": "0",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": None,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": []
                    },
                    {
                        "id": 148,
                        "name": "提交工单",
                        "step_type": "3",
                        "can_delete": False,
                        "index": 0,
                        "other_info": {},
                        "approval_method": 0,
                        "visible_type": "0",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [],
                        "director": None,
                        "fields_list": [
                            261,
                            262,
                            263,
                            264
                        ]
                    },
                    {
                        "id": 150,
                        "name": "工程师处理",
                        "step_type": "1",
                        "can_delete": True,
                        "index": 0,
                        "other_info": {},
                        "approval_method": 0,
                        "visible_type": "3",
                        "department": None,
                        "department_name": None,
                        "role_list": [],
                        "handler": [
                            "admin"
                        ],
                        "director": None,
                        "fields_list": [
                            267
                        ]
                    }
                ],
                "work_flow_step_line_list": [
                    {
                        "id": 123,
                        "name": "",
                        "other_info": {},
                        "work_flow_id": 36,
                        "use_line": {
                            "start": 146,
                            "end": 148
                        }
                    },
                    {
                        "id": 125,
                        "name": "默认",
                        "other_info": {},
                        "work_flow_id": 36,
                        "use_line": {
                            "start": 150,
                            "end": 147
                        }
                    },
                    {
                        "id": 126,
                        "name": "默认",
                        "other_info": {},
                        "work_flow_id": 36,
                        "use_line": {
                            "start": 148,
                            "end": 150
                        }
                    }
                ],
                "work_order_list": [
                    {
                        "name": "Nginx配置变更",
                        "director": "admin",
                        "order_type": "变更管理",
                        "visible_type": "0",
                        "describe": None,
                        "icon_id": 1,
                        "folder_name": "默认分组",
                        "department_id": None,
                        "role_list_id": [],
                        "user_list_id": [],
                    },
                    {
                        "name": "数据库创建申请",
                        "director": "admin",
                        "order_type": "请求管理",
                        "visible_type": "0",
                        "describe": None,
                        "icon_id": 4,
                        "folder_name": "默认分组",
                        "department_id": None,
                        "role_list_id": [],
                        "user_list_id": [],
                    },
                    {
                        "name": "域名解析申请",
                        "director": "admin",
                        "order_type": "请求管理",
                        "visible_type": "0",
                        "describe": None,
                        "icon_id": 4,
                        "folder_name": "默认分组",
                        "department_id": None,
                        "role_list_id": [],
                        "user_list_id": [],
                    }
                ]
            },
        ]
    }


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
            if resp.status_code in [200, 400]:
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

    def workbench_work_order_init(self):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/work-order-init/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data = InitData()
            work_order_list = data.work_order_list
            data_json = json.dumps(work_order_list)
            response = self.session.post(url=NAV_GROUP_URL, data=data_json, verify=False)
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


def start(paas_domain, username, password):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)

    # 初始化工作台工单流程和工单
    add_work_order_status, add_work_order_data = run_obj.workbench_work_order_init()
    print("[SUCCESS] add work order success") if add_work_order_status else print(
        "[ERROR] add work order error, error info: {}".format(add_work_order_data))




def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="OpsAny URL.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    start(
        options.domain,
        options.paas_username,
        options.paas_password,
    )


"""
python3 init_work_order.py --domain https://demo.opsany.com --paas_username admin --paas_password 123456
python init_work_order.py --domain http://192.168.0.13:8004 --paas_username huxingqi --paas_password 123456
"""
