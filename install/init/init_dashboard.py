import os

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class GrafanaBasicApi:
    def __init__(self, grafana_url, grafana_token="", username=None, password=None):
        self.username = username
        self.password = password
        self.grafana_token = grafana_token
        self.grafana_url = str(grafana_url) + ("/" if str(grafana_url)[-1] != "/" else "")

    def create_or_update_dashboard(self, dashboard):
        # 需要使用requests去做
        try:
            headers = {}
            url = "{}api/dashboards/db/".format(self.grafana_url)
            if self.grafana_token:
                headers = {"Authorization": "Bearer {0}".format(self.grafana_token)}
            else:
                url = url.replace("https://", "https://{}:{}@".format(self.username, self.password))
            res = requests.post(url, json=dashboard, headers=headers, verify=False)
            json_res = res.json()
            if json_res.get("status") == "success":
                return True, "{}: {}".format(json_res.get("status"), json_res.get("uid"))
            else:
                return False, res.json().get("message")
        except Exception as e:
            return False, str(e)

    def get_dashboard_list(self, target_path, file_type=".json"):
        try:
            target_file_list = []
            dashboard_json_list = []
            if target_path:
                files = os.listdir(target_path)
                for file in files:
                    if file.lower().endswith(file_type):
                        full_path = os.path.join(target_path, file)
                        target_file_list.append(full_path)
                        with open(full_path, "r", encoding="utf-8") as f:
                            dashboard_json_list.append(json.loads(f.read()))
            if target_file_list:
                print("Find dashboard: {}, total: {} files, the import will be performed.".format(
                    target_file_list, len(target_file_list)
                ))
                return dashboard_json_list
            else:
                print("Not find valid file.")
                return []
        except Exception as e:
            print("Get target file error, error info: {}".format(str(e)))
            return []


def run(grafana_url, grafana_token, grafana_username=None, grafana_password=None, target_path="./dashboard-init", overwrite=True):
    grafana_api = GrafanaBasicApi(grafana_url, grafana_token, grafana_username, grafana_password)
    dashboard_json_list = grafana_api.get_dashboard_list(target_path)
    success, error = 0, 0
    for dashboard_json in dashboard_json_list:
        name = dashboard_json.get("title") or "无名"

        last_json = {
            "dashboard": dashboard_json,
            "message": "init_dashboard初始化导入",
            "overwrite": overwrite,
            "folderId": 0
        }
        status, message = grafana_api.create_or_update_dashboard(last_json)
        if status:
            success += 1
            print("[SUCCESS] Create or update dashboard success: {} {}".format(name, message))
        else:
            error += 1
            print("[ERROR] Create or update all dashboard, error info:{} {}".format(name, message))
    print("[SUCCESS] Create or update all dashboard end: success: {}, error: {}".format(success, error))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--grafana_url", help="Grafana Url.", required=True)
    parameter.add_argument("--grafana_token", help="Grafana Token.", required=False)
    parameter.add_argument("--grafana_username", help="Grafana Username.", required=False)
    parameter.add_argument("--grafana_password", help="Grafana Password.", required=False)
    parameter.add_argument("--dashboard_path", help="Grafana Dashboard Path.", required=False)
    parameter.add_argument("--overwrite", help="Grafana Dashboard overwrite.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    dashboard_path = options.dashboard_path
    overwrite = True if options.overwrite=="true" else False
    if not dashboard_path:
        dashboard_path = "./dashboard-init"
    run(
        options.grafana_url,
        options.grafana_token,
        options.grafana_username,
        options.grafana_password,
        target_path=dashboard_path,
        overwrite=overwrite,
    )
    # target_path:脚本路径 overwrite:覆盖原数据(更新-标识依据 id,uid,title )
    # 1. 传入id时当id不存在报错导入失败, id存在直接覆盖更新
    # 2. 不传入id判断uid,title不存在创建，存在更新
    # 使用token操作 dashboard_path 默认路径./dashboard-init  overwrite 是否覆盖
    # 使用用户名密码操作  dashboard_path 默认路径./dashboard-init  overwrite 是否覆盖

    # 社区版大屏
    # 使用密码: python3 init_dashboard.py  --grafana_url https://domain/grafana/ --grafana_username admin --grafana_password grafana_password --overwrite true --dashboard_path ./dashboard-init
    # 使用Token: python3 init_dashboard.py  --grafana_url https://domain/grafana --grafana_token grafana_token --overwrite true --dashboard_path ../opsany-ee/init/dashboard-init

    # 企业版大屏
    # 使用密码: python3 init_dashboard.py  --grafana_url https://domain/grafana/ --grafana_username admin --grafana_password grafana_password --overwrite true --dashboard_path ../opsany-ee/init/dashboard-init
    # 使用Token: python3 init_dashboard.py  --grafana_url https://domain/grafana/ --grafana_token grafana_token --overwrite true  --dashboard_path ../opsany-ee/init/dashboard-init
