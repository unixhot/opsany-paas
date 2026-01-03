import os

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse

default_notify_policy = {
    "name": "默认通知策略",
    "prom": 1,
    "condition": [{
        "conditionList": [{
            "key": "severity",
            "operator": "3",
            "value": ["Warning", "Average", "High", "Disaster"]
        }]
    }],
    "group_by_type": "1",
    "group_by": [],
    "group_interval": "1",
    "group_interval_type": "1",
    "notify_time_type": "1",
    "custom_weeks_time_dict": {
        "weeks": []
    },
    "notify_frequency": "10",
    "notify_frequency_type": "1",
    "notify_resolved": "1",
    "inform_type_dict": [],
    "need_repeat_notice": "2",
    "need_upgrade_strategy": "1",
    "notify_policy_upgrade": None,
    "enabled": True,
    "notify_object_list": [{
        "type": "1",
        "target_value": "admin",
        "checked_message_type": ["1", "2", "3", "4", "5"],
        "is_activate": True
    }]
}


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.username = username
        self.password = password
        self.init_alert_rule_url = "/{}/prom//api/prom/v0_1/init-alert-rule/"
        self.init_notify_policy_url = "/{}/prom//api/prom/v0_1/init-notify-policy/"
        self.run_env = "o" if env == "prod" else "t"
        self.login_url = self.paas_domain + "/login/api/v3/login/"
        self.status, self.token, self.csrfmiddlewaretoken = self.login()

    def login(self, verify_code=""):
        try:
            json_data = {"username": self.username, "password": self.password, "verify_code": verify_code, "auth_type": "1"}
            resp = self.session.post(self.login_url, data=json.dumps(json_data), verify=False)
            try:
                res_json = resp.json()
                if resp.status_code != 200:
                    return False, res_json, ""
                bk_token = (res_json.get("data") or {}).get("bk_token")
                code = res_json.get("code")
                message = res_json.get("message")
                if bk_token:
                    return True, bk_token, resp.cookies.get("bklogin_csrftoken")
                elif code != 200:
                    return False, message, ""
                else:
                    return False, res_json, ""
            except Exception as e:
                return False, str(resp.content.decode()), ""
        except Exception as e:
            return False, str(e), ""


    def init_alert_rule(self, prom, name, yml_str):
        api = self.paas_domain + self.init_alert_rule_url.format(self.run_env)
        try:
            data = {
                "prom": prom,
                "yml_str": yml_str
            }
            res = self.session.post(api, data=json.dumps(data), verify=False)
            try:
                res_data = res.json()
            except Exception as e:
                raise Exception(res.content.decode())
            if res.status_code == 200:
                if res_data.get("code") == 200:
                    return True, res_data.get("message")
            raise Exception(res_data.get("message"))
        except Exception as e:
            return False, "初始化应用监控告警规则失败: {}, {}".format(name, str(e))

    def init_notify_policy(self, data):
        name = data.get("name")
        api = self.paas_domain + self.init_notify_policy_url.format(self.run_env)
        try:
            res = self.session.post(api, data=json.dumps(data), verify=False)
            try:
                res_data = res.json()
            except Exception as e:
                raise Exception(res.content.decode())
            if res.status_code == 200:
                if res_data.get("code") == 200:
                    return True, res_data.get("message")
            raise Exception(res_data.get("message"))
        except Exception as e:
            return False, "初始化应用监控通知规则失败: {}, {}".format(name, str(e))

    def get_alert_rule_list(self, target_path, file_type=".yml"):
        try:
            target_file_dict = {}
            if target_path:
                files = os.listdir(target_path)
                for file in files:
                    if file.lower().endswith(file_type):
                        full_path = os.path.join(target_path, file)
                        with open(full_path, "r", encoding="utf-8") as f:
                            target_file_dict[full_path] = f.read()
            if target_file_dict:
                print("Find Rule: {}, total: {} files, the import will be performed.".format(
                    ", ".join(list(target_file_dict.keys())), len(target_file_dict)))
                return target_file_dict
            else:
                print("Not find valid file.")
                return {}
                # sys.exit(0)
        except Exception as e:
            print("Get target file error, error info: {}".format(str(e)))
            # sys.exit(1)
            return {}


def run(domain, paas_username, paas_password, prom_name, notify_name, target_path="./alert-rules", env="prod"):
    api = OpsAnyApi(domain, paas_username, paas_password, env=env)

    # 初始化应用监控告警规则
    alert_yml_dict = api.get_alert_rule_list(target_path)
    success, error = 0, 0
    error_message = ""
    for k, v in alert_yml_dict.items():
        status, message = api.init_alert_rule(prom_name, k, v)
        if status: success += 1
        else:
            error += 1
            error_message += f"{k}: {message}\n"
    print(f"初始化应用监控告警规则结束: 成功: {success} 个规则组!, 失败: {error} 个规则组!")
    if error: print(error_message)

    # 初始化应用监控通知规则
    data = default_notify_policy
    data["prom"] = prom_name
    data["name"] = notify_name
    status, message = api.init_notify_policy(data)
    print(f"初始化应用监控通知规则 {f'成功: {notify_name}' if status else f'失败: {message}'}!")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    prom_name = "内置Prometheus"  # 管控平台-采控管理-Prometheus实例名称
    notify_name = "默认通知策略"  # 应用监控-通知规则-名称
    rules_path = "alert-rules"
    run(options.domain, options.paas_username, options.paas_password, prom_name, notify_name, target_path=rules_path, env="prod")
    # 初始化 告警规则和通知规则
    # python init_alert_rule.py  --domain https://DOMAIN --paas_username admin --paas_password 123456
