# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

import requests
import json
from config import *
from control.models import UserInfo


class EsbApi(object):
    def __init__(self, token):
        self.token = token
        self.app_code = APP_CODE
        self.app_secret = SECRET_KEY
        self.url = ESB_BASE_URL
        self.headers = {
            "Cookie": "bk_token={}".format(self.token)
        }

    def get_user_id(self):
        API = "/api/c/compapi/v2/bk_login/get_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)

        user_id = None
        if end_data.get("result"):
            user_id = UserInfo.objects.get(username=end_data.get("data").get("bk_username")).id
        return user_id

    def get_all_host(self):
        API = "/api/c/compapi/cmdb/get_all_host/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "model_code": "esb"
        }
        print(req)
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        # print(end_data)
        end_data = end_data.get("data")
        return end_data

    def import_inst(self, data: dict):
        API = "/api/c/compapi/cmdb/import_inst/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "data": data
        }
        URL = self.url + API
        req = json.dumps(req)
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        print(end_data)
        end_data = end_data.get("data")
        return end_data

    def update_agent_state(self, lt: list):
        """
        模拟请求参数
         {
            "bk_app_code": "control",
            "bk_app_secret": "45037a36-81e8-450d-a7b7-f44eb711769a",
            "bk_token": "nO1Cb5lC0L_vBVT60DkM6_ExO2MjrzHgjfw49vvq7pQ",
            "update_list":[
                {
                    "ip": "118.31.7.172",
                    "agent": "Agent正常",
                    "controller_name": "default.None"
                },
                {
                    "ip": "127.0.0.2",
                    "agent": "Agent未安装",
                    "controller_name": "default.None"
                }
            ]
        }
        """
        API = "/api/c/compapi/cmdb/update_agent_state/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "update_list": lt
        }
        
        URL = self.url + API
        req = json.dumps(req)

        print("req", req)
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        print("update_list", end_data)
        return end_data

    def import_cloud_server_grains(self, grains_data: dict):
        API = "/api/c/compapi/cmdb/import_grains_from_control/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "grains_data": grains_data
        }
        URL = self.url + API
        req = json.dumps(req)
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        end_data = end_data.get("data")
        return end_data

    def get_nav_and_collection(self):
        API = "/api/c/compapi/workbench/get_nav_and_collection/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        dt = {}
        if end_data.get("result"):
            end_data = end_data.get("data")
            return end_data
        return dt

    def collection_nav(self, nav_id):
        API = "/api/c/compapi/workbench/post_collection/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "nav_id": nav_id
        }
        URL = self.url + API
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        if end_data.get("result"):
            return end_data
        return None

    def get_user_message_info(self, current=1, pageSize=10):
        API = "/api/c/compapi/workbench/get_message_info/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "current": str(current),
            "pageSize": str(pageSize)
        }
        URL = self.url + API
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        if end_data.get("result"):
            data = end_data.get("data")
            return data
        return None

    def get_user_info(self):
        API = "/api/c/compapi/v2/bk_login/get_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        dt = {}
        if end_data.get("result"):
            dt["phone"] = end_data.get("data").get("phone")
            dt["username"] = end_data.get("data").get("bk_username")
            dt["email"] = end_data.get("data").get("email")
            dt["ch_name"] = end_data.get("data").get("chname")
            dt["role"] = end_data.get("data").get("bk_role")
        return dt

    def post_menu_privilege(self, platform_cname, menu_code):
        API = "/api/c/compapi/rbac/post_menu_privilege/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "platform_cname": platform_cname,
            "menu_code": menu_code
        }
        URL = self.url + API
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        print(end_data)
        if end_data.get("result"):
            data = end_data.get("data")
            return data
        return None

    def get_user_menu(self):
        API = "/api/c/compapi/rbac/post_menu_tree/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "platform_cname": "control"
        }
        URL = self.url + API
        response = requests.post(url=URL, data=json.dumps(req), headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        return end_data.get("data")

    def get_user_info_from_workbench(self):
        API = "/api/c/compapi/workbench/get_user_info_from_workbench/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        return end_data.get("data")

    def read_all_message(self):
        API = "/api/c/compapi/workbench/get_read_all_message/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        return end_data.get("data")

    def get_user_ssh_key(self, ssh_key_id=""):
        API = "/api/c/compapi/workbench/get_user_ssh_key/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "ssh_key_id": ssh_key_id,
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        return end_data.get("data")

    def send_out_message(self, temp_id, parameter, operator):
        API = "/api/c/compapi/workbench/post_info_to_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token,
            "operator": operator,
            "temp_id": temp_id,
            "parameter": parameter
        }
        URL = self.url + API
        response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        if end_data.get("result"):
            return end_data
        return None


if __name__ == "__main__":
    a = EsbApi("SGb28LwjRSOYrn39PjnFi-vVNVQ9Lk-BqKiLgHZ6OMw")
    data = a.get_user_ssh_key("")
    print(data)
    # print(data)
    # b = a.get_all_host()
    # print(b)
    # b = a.import_inst(data)
