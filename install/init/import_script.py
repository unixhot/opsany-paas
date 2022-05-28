#!/usr/bin/env python3
'''
python import_script.py 
--domain https://dev.opsany.cn 
--paas_username guoyuchen
--paas_password 123456
--target_type collection/script/task/patrol    collection/script/patrol则扫描目标路径下为json的文件，task则扫描目标路径下为zip的文件
  user参数比较特殊，用于刚部署完SaaS后，SaaS中没有第一个用户，导致导入内容时报错：没有获取到用户信息. 当target_type为user的时候，APP_CODE不能为空
--target_file   目标文件
--target_path   目标文件夹       target_path和target_file两者不能同时为空
--run_env prod/dev  非必填，为空则使用prod url 即/o/
'''

import requests
import sys
import os
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()
        self.run_env = "o" if env == "prod" else "t"

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

    def get_menu(self, app_code):
        API = self.paas_domain + "/{}/{}/api/{}/v0_1/get-menu/".format(self.run_env, app_code, app_code)
        try:
            # 用于初次创建用户
            res = self.session.get(API)
            if res.status_code == 200 and res.json().get("code") == 200:
                print("Create first user success.")
                return True
            raise Exception(res.json().get("message"))
        except Exception as e:
            print("Api error, error info: {}, api url: {}.".format(str(e), API))
            sys.exit(1)

    def get_script_default_group_id(self):
        script_group_api = self.paas_domain + "/{}/job/api/job/v0_1/script-group/".format(self.run_env)
        status, data = self.get_group_info(script_group_api)
        if status:
            for _data in data:
                if _data.get("name") == "默认分组":
                    return _data.get("id")
            print("Not find script default group.")
            sys.exit(0)
        else:
            print("Api error, error info: {}, api url: {}.".format(data, script_group_api))
            sys.exit(0)

    def get_group_info(self, API):
        try:
            response = self.session.get(url=API, verify=False)
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

    def get_task_default_group_id(self):
        task_group_api = self.paas_domain + "/{}/job/api/job/v0_1/new-tool-admin/".format(self.run_env)
        status, data = self.get_group_info(task_group_api)
        if status:
            for _data in data:
                if _data.get("name") == "默认分组":
                    return _data.get("id")
            print("Not find task default group.")
            sys.exit(0)
        else:
            print("Api error, error info: {}, api url: {}.".format(data, task_group_api))

    def upload_file(self, api, form_data, file_form):
        api = self.paas_domain + api.format(self.run_env)
        try:
            res = self.session.post(api, data=form_data, files=file_form, verify=False)
            if res.status_code == 200:
                if res.json().get("code") != 200:
                    raise Exception(res.json().get("message"))
                return True, res.json().get("data", {})
            raise Exception("上传文件失败，请检查您的文件是否有效")
        except Exception as e:
            return False, "Upload api error, error info: {}. api url: {}".format(str(e), api)

    def import_info(self, api, data):
        api = self.paas_domain + api.format(self.run_env)
        try:
            res = self.session.post(api, json=data, verify=False)
            if res.status_code == 200:
                if res.json().get("code") == 200:
                    return True, res.json().get("data", {})
                raise Exception(res.json().get("message"))
            else:
                raise Exception("导入文件失败，请检查您导入的文件是否有效")
        except Exception as e:
            return False, "Import api error, error info: {}. api url: {}".format(str(e), api)

    def import_script(self, target_list):
        self.get_menu("job")
        group_id = self.get_script_default_group_id()
        for target in target_list:
            print("-" * 30)
            file_form = {
                "script": (os.path.split(target)[-1], open(target, 'rb'), "application/json"),
            }
            upload_form = {
                "import_type": "file",
                "group_id": group_id
            }
            status, res = self.upload_file("/{}/job/api/job/v0_1/import-export-script/", upload_form, file_form)
            if status:
                res["import_type"] = "json"
                res["script_from"] = "1"
                status, res = self.import_info("/{}/job/api/job/v0_1/import-export-script/", res)
                if status:
                    print("Script {} import success.".format(target))
                else:
                    print("Script {} import error.".format(target))
                    print(res)
            else:
                print("Script {} import error.".format(target))
                print(res)
        print("Import script run over.")

    def get_control_server_default_group(self):
        server_group_api = self.paas_domain + "/{}/control/api/control/v0_1/host-group/".format(self.run_env)
        status, data = self.get_group_info(server_group_api)
        if status:
            for _data in data:
                if _data.get("name") == "默认分组":
                    return _data.get("id")
            print("Not find server default group.")
            sys.exit(0)
        else:
            print("Api error, error info: {}, api url: {}.".format(data, server_group_api))
            sys.exit(0)

    def import_asset_collection(self, target_list):
        self.get_menu("control")
        for target in target_list:
            print("-" * 30)
            file_form = {
                "json_file": (os.path.split(target)[-1], open(target, 'rb'), "application/json"),
            }
            upload_form = {}
            status, res = self.upload_file("/{}/control/api/control/v0_1/import-plugin/", upload_form, file_form)
            if status:
                print("Asset collection {} import success.".format(target))
            else:
                print("Asset collection {} import error.".format(target))
                print(res)
        print("Import asset collection run over.")

    def import_patrol_template(self, target_list):
        self.get_menu("auto")
        for target in target_list:
            print("-" * 30)
            file_form = {
                "file": (os.path.split(target)[-1], open(target, 'rb'), "application/json"),
            }
            upload_form = {}
            status, res = self.upload_file("/{}/auto/api/auto/v0_1/patrol-template-import-export/", upload_form, file_form)
            if status:
                print("Patrol template {} import success.".format(target))
            else:
                print("Patrol template {} import error.".format(target))
                print(res)
        print("Import patrol template run over.")

    def import_task(self, target_list):
        self.get_menu("job")
        self.get_menu("control")
        task_group_id = self.get_task_default_group_id()
        server_default_group_id = self.get_control_server_default_group()
        for target in target_list:
            print("-" * 30)
            file_form = {
                "task": (os.path.split(target)[-1], open(target, 'rb'), "application/zip"),
            }
            upload_form = {
                "import_type": "file",
                "group_id": task_group_id
            }
            status, res = self.upload_file("/{}/job/api/job/v0_1/import-export-task/", upload_form, file_form)
            if status:
                res["import_type"] = "json"
                jobs = res.get("job")
                for job in jobs:
                    job["group_id_list"] = [server_default_group_id]
                    job["script_id"] = job.get("script", {}).get("id")
                    job["file_id_list"] = [file.get("id") for file in job.get("file", [])]
                status, res = self.import_info("/{}/job/api/job/v0_1/import-export-task/", res)
                if status:
                    print("Task {} import success.".format(target))
                else:
                    print("Task {} import error.".format(target))
                    print(res)
            else:
                print("Task {} import error.".format(target))
                print(res)
        print("Import task run over.")


def get_target(target_path="", target_file="", file_type=".json"):
    try:
        target_file_list = []
        if target_path:
            files = os.listdir(target_path)
            for file in files:
                if file.lower().endswith(file_type):
                    target_file_list.append(os.path.join(target_path, file))
        if target_file:
            if target_file.lower().endswith(file_type) and os.path.exists(target_file):
                if target_file not in target_file_list:
                    target_file_list.append(target_file)
        if target_file_list:
            print("Find valid files: {}, total: {} files, the import will be performed.".format(
                target_file_list, len(target_file_list)
            ))
            return target_file_list
        else:
            print("Not find valid file.")
            sys.exit(0)
    except Exception as e:
        print("Get target file error, error info: {}".format(str(e)))
        sys.exit(1)


def run(options):
    target_type = options.target_type
    target_path = options.target_path
    target_file = options.target_file
    run_env = options.run_env if options.run_env else "prod"
    if not target_file and not target_path:
        print("Target file or Target path must select one.")
        sys.exit(0)
    api_object = OpsAnyApi(
        options.domain,
        options.paas_username,
        options.paas_password,
        run_env
    )
    if target_type.lower() == "script":
        target_list = get_target(target_path, target_file)
        api_object.import_script(target_list)
    elif target_type.lower() == "task":
        target_list = get_target(target_path, target_file, "zip")
        api_object.import_task(target_list)
    elif target_type.lower() == "collection":
        target_list = get_target(target_path, target_file)
        api_object.import_asset_collection(target_list)
    elif target_type.lower() == "patrol":
        target_list = get_target(target_path, target_file)
        api_object.import_patrol_template(target_list)
    else:
        print("Nonexistent parameter, please use [Script/Task/Collection/Patrol/User].")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.add_argument("--target_type", help="Import Target Type.", required=True)
    parameter.add_argument("--target_path", help="Target Path", required=False)
    parameter.add_argument("--target_file", help="Target file", required=False)
    parameter.add_argument("--run_env", help="Run env", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

