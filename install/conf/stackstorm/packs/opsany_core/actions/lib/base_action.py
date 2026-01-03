import json
import time

import requests
from st2common.runners.base_action import Action

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class OpsAnyCoreRestAPI(Action):
    def __init__(self, *args, **kwargs):
        super(OpsAnyCoreRestAPI, self).__init__(*args, **kwargs)
        self.app_code = self.config["app_code"]
        self.app_secret = self.config["app_secret"]
        self.api_url = self.config["api_url"]
        self.access_token = self.config["access_token"]
        self.headers = {
            "Cookie": "bk_token={}".format(None)
        }

    def _get_request_id_status(self, requests_id, retry=3):
        status, res_list = True, []
        for i in range(retry):
            time.sleep(0.1)
            status, res_list = self.get_request_id_status(requests_id)
            if status:
                return status, res_list
        return status, res_list

    def get_return(self, requests_id):
        error_count, success_count = [], []
        while True:
            time.sleep(0.5)
            status, res_list = self._get_request_id_status(requests_id, 3)  # 重试三次，防止域名解析失败
            if not status:
                return False, {"success": success_count, "error": {"message": str(res_list)}}

            count = len(res_list)
            finish_count = 0
            for res in res_list:
                if res.get("status") == "2":
                    finish_count += 1
                    continue
            if count == finish_count:
                break
        for res in res_list:
            if res.get("success"):
                """
                # error
                "info": {
                    "stderr": "error",
                    "stdout": ""
                    }
                    
                # success
                "info": {
                    "stderr": "",
                    "stdout": ""
                    }
                
                # success
                "info": {
                    "stderr": "error",
                    "stdout": "success"
                    }
                
                success null is error
                info null is error
                """
                # if (not res.get("info")) or (not res.get("info", {}).get("stderr")):
                #     success_count.append(res)

                # info = res.get("info", {})
                # if info:
                    # if info.get("stderr") and (info.get("stdout") == ""):
                    #     error_count.append(res)
                    # else:
                    #     success_count.append(res)
                # else:
                    # error_count.append(res)
                success_count.append(res)
            else:
                error_count.append(res)
        dic = {"success": success_count, "error": error_count}
        if success_count:
            return True, dic
        else:
            if not error_count:
                return False, {"success": success_count, "error": {"message": "获取日志失败，请联系管理员: {}".format(str(res_list))}}
            return False, dic

    def run_shell(self, host_list, command):
        API = "/api/c/compapi/control/post_shell/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "host_list": host_list,  # [unique1, unique2, unique3]
            "command": command
        }
        URL = self.api_url + API
        try:
            response = requests.post(
                url=URL,
                json=req,
                headers=self.headers,
                verify=False)
        except Exception as e:
            return False, str(e)
        end_data = response.json()
        if end_data.get("data"):
            return True, end_data.get("data")
        return False, end_data.get("message")

    def run_script(self, host_list, script_url, script_arg=None, timeout=1800):
        API = "/api/c/compapi/control/post_script/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "host_list": host_list,  # [unique1, unique2, unique3]
            "script_url": script_url,
            "script_arg": script_arg,
            "timeout": timeout
        }
        URL = self.api_url + API
        try:
            response = requests.post(
                url=URL,
                json=req,
                headers=self.headers,
                verify=False)
        except Exception as e:
            return False, str(e)
        end_data = response.json()
        if end_data.get("data"):
            return True, end_data.get("data")
        return False, end_data.get("message")

    def send_out_message(self, temp_id, subscribe_type, parameter, operator, alert_info, result=True):
        API = "/api/c/compapi/workbench/post_info_to_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_username": operator,
            # "bk_access_token": self.access_token,
            "operator": operator,
            "temp_id": temp_id,
            "subscribe_type": subscribe_type,
            "parameter": parameter,
            "result": result,
            "alert_info": json.dumps(alert_info),
        }
        URL = self.api_url + API
        print("esb接口", req)
        try:
            response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
        except Exception as e:
            return None
        end_data = json.loads(response.text)
        if end_data.get("result"):
            return end_data
        return None

    # 给企微、钉钉群发消息
    def send_robot(self, temp_id, parameter, robot_list, alert_info=None, robot_type="qw"):
        API = "/api/c/compapi/workbench/send_robot/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_username": "admin",
            "bk_access_token": self.access_token,
            "robot_type": robot_type,  # qw dd
            "temp_id": temp_id,  # 20
            "parameter": parameter,  # "('', '')"
            "robot_list": robot_list,
            "alert_info": alert_info or {},
        }
        URL = self.api_url + API
        try:
            response = requests.post(url=URL, data=req, headers=self.headers, verify=False)
            end_data = json.loads(response.text)
            if end_data.get("result"):
                end_data = end_data.get("data") or []
                return end_data
            return []
        except Exception as e:
            return []

    def download_nexus_project(self, download_url):
        API = "/api/c/compapi/devops/nexus_project/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "download_url": download_url
        }
        URL = self.api_url + API
        try:
            response = requests.post(
                url=URL,
                json=req,
                headers=self.headers,
                verify=False)
        except Exception as e:
            return False, str(e)
        end_data = response.json()
        if end_data.get("data"):
            return True, end_data.get("data")
        return False, end_data.get("message")

    def post_file(self, host_list, file_url, file_path):
        API = "/api/c/compapi/control/post_file/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "host_list": host_list,  # [unique1, unique2, unique3]
            "file_url": file_url,
            "file_path": file_path
        }
        URL = self.api_url + API
        try:
            response = requests.post(
                url=URL,
                json=req,
                headers=self.headers,
                verify=False)
        except Exception as e:
            return False, str(e)
        end_data = response.json()
        if end_data.get("data"):
            return True, end_data.get("data")
        return False, end_data.get("message")

    def send_mail(self, receiver, subject, text, text_type):
        API = "/api/c/compapi/workbench/send_mail/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "operator": "admin",
            "receiver": receiver,
            "subject": subject,
            "text": text,
            "text_type": text_type  # 1 Text  2 Html
        }
        URL = self.api_url + API
        response = requests.post(
            url=URL,
            json=req,
            headers=self.headers,
            verify=False)

        end_data = response.json()
        if end_data.get("result"):
            return True, end_data.get("message") or "success"
        else:
            return False, end_data.get("message")

    def get_request_id_status(self, request_id):
        API = "/api/c/compapi/control/get_request_id_status/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_access_token": self.access_token,
            "request_id": request_id
        }
        URL = self.api_url + API
        try:
            response = requests.get(
                url=URL,
                params=req,
                headers=self.headers,
                verify=False,
                timeout=30,
            )
            end_data = response.json()
            if end_data.get("data"):
                return True, end_data.get("data")
            else:
                return False, "获取日志失败({})，请联系管理员，或重新执行.".format(request_id)
        except Exception as e:
            return False, "获取日志失败({})，请联系管理员，或重新执行: {}".format(request_id, str(e))