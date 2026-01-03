"""
脚本说明：部署SaaS脚本
文件命名要求：必须为 app_code + "-" + paas_domain + "-" + version + ".tar.gz"
执行说明：python deploy.py --domain [paas_domain] --username [paas_admin_user_name] --password [paas_admin_user_password] --file_name [file1] [file2] [file3]
      例：python deploy.py --domain 192.168.56.11 --file_name rbac-192.168.56.11-1.1.4.tar.gz workbench-192.168.56.11-1.1.4.tar.gz
参数说明：
    domain  必填
    username   非必填    未填写会使用 line 165  default配置
    password   非必填    未填写会使用 line 166  default配置
    file_name  非必填    未填写则会扫描当前文件夹下所有符合要求的文件
账号说明：必须使用权限为管理员的账号，普通账号不能使用
第三方依赖：requests==2.25.0
"""
import json
import os
import sys
import time
import requests
import re
import argparse

# 去除本地python3 windows环境报错
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HTTP_SCHEMA = os.environ.get("HTTP_SCHEMA", "https")


class Deploy(object):
    def __init__(self, paas_domain, file_name=[], username="", password="", verify_code=""):
        self.paas_domain = paas_domain
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'referer': "%s://%s" % (HTTP_SCHEMA, paas_domain)})
        self.session.verify = False
        self.file_list = self.get_upload_file(file_name)
        self.login_url = "{}://{}/login/".format(HTTP_SCHEMA, self.paas_domain)
        self.status, self.token, self.csrfmiddlewaretoken = self.login(verify_code)

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

    # 获取上传文件
    def get_upload_file(self, file_name_list):
        if file_name_list:
            file_list = [os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name) for file_name in file_name_list if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)) and file_name.endswith("tar.gz") and len(file_name.split("-")) == 3]
        else:
            file_list = [os.path.join(os.path.dirname(os.path.abspath(__file__)), file) for file in os.listdir(os.path.dirname(os.path.abspath(__file__))) if file.endswith("tar.gz") and len(file.split("-")) == 3]
        if not file_list:
            print("未发现有效文件")
            sys.exit(1)
        return file_list

    # 部署
    def deploy(self):
        for file_path in self.file_list:
            _, file_name = os.path.split(file_path)
            app_code = file_name.split("-")[0]
            check_res = self.check_app_code(app_code)
            if check_res:       # 第一次部署
                app_code = "0"
            else:               # 第二次部署
                app_code = app_code
            status, version = self.upload_file(file_path, app_code)
            if not status or not version:
                continue
            url_app_code = app_code if app_code else "0"
            deploy_url = "{}://{}/saas/{}/release/online/{}/".format(HTTP_SCHEMA, self.paas_domain, url_app_code, version)
            res = self.session.post(deploy_url, json={"csrfmiddlewaretoken": self.csrfmiddlewaretoken},
                                    verify=False, headers={"X-CSRFToken": self.session.cookies.get("bk_csrftoken")})
            if res.status_code == 200:
                event_id = res.json().get("event_id")
                if event_id:
                    print("开始部署: {}".format(file_name.split("-")[0]))
                    self.get_result(event_id, file_name.split("-")[0])
                else:
                    print("部署失败，请手工部署: {}".format(file_name))
                    print("失败信息: {}".format(res.json().get("message")))
                    if url_app_code == "0":
                        self.delete_first_error_saas(file_name.split("-")[0])

    # 用于删除第一次部署时，部署错误造成的遗留数据
    def delete_first_error_saas(self, app_code):
        delete_url = "{}://{}/saas/{}/delete/".format(HTTP_SCHEMA, self.paas_domain, app_code)
        res = self.session.post(delete_url, json={"csrfmiddlewaretoken": self.csrfmiddlewaretoken},
                            verify=False, headers={"X-CSRFToken": self.session.cookies.get("bk_csrftoken")})

    # 轮询部署状态
    def get_result(self, event_id, app_code):
        while True:
            time.sleep(2)
            url = "{}://{}/release/{}/task/".format(HTTP_SCHEMA, self.paas_domain, app_code)
            reqs = self.session.get(url, params={
                "event_id": event_id,
                "app_state": 1
            })
            if reqs.json().get("result"):
                if reqs.json().get("data").get("status") == 1:
                    print("部署完毕: {}".format(app_code))
                    break
                elif reqs.json().get("data").get("status") == 0:
                    print("部署失败: {}".format(app_code))
                    break

    # 检查APPCODE是否存在，存在的话即为：已经部署成功，后续部署应为更新部署
    def check_app_code(self, app_code):
        check_url = "{}://{}/app/check/app_code/?app_code={}".format(HTTP_SCHEMA, self.paas_domain, app_code)
        res = self.session.get(check_url)
        try:
            json_res = res.json()
            return json_res.get("result")
        except Exception:
            print("Paas服务异常")
            sys.exit(1)

    # 上传SaaS包
    def upload_file(self, file_path, app_code="0"):
        print("开始上传文件: {}".format(os.path.split(file_path)[-1]))
        upload_url = "{}://{}/saas/{}/upload/".format(HTTP_SCHEMA, self.paas_domain, app_code)
        upload_form = {
            "saas_file": (os.path.split(file_path)[-1], open(file_path, 'rb'), "application/gzip"),
        }
        res = self.session.post(upload_url, json={"csrfmiddlewaretoken": self.csrfmiddlewaretoken}, files=upload_form,
                                verify=False, headers={"X-CSRFToken": self.session.cookies.get("bk_csrftoken")})
        res.encoding = 'utf-8'
        if res.status_code == 200:
            res_text = res.text.encode('utf-8').decode('utf-8')
            search_upload_info = re.search(r"></i>.*?</span>", res_text)
            search_version_info = re.search(r"saas_app_version_id\"\)\.innerHTML=\".*?\"", res_text)
            if search_upload_info and search_version_info:
                if search_upload_info.group()[5: -7].strip() == "上传成功":
                    print("{} 上传成功".format(os.path.split(file_path)[-1]))
                    return True, search_version_info.group()[33: -1]
                else:
                    print(search_upload_info.group()[5: -7].strip())
                    return False, None
        else:
            print("Paas服务异常，请手工上传")
            return False, None


# 增加脚本参数
def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--username", help="Admin user username.", default="admin")
    parameter.add_argument("--password", help="Admin user password.", default="admin")
    parameter.add_argument("--file_name", help="Deploy file_name.", nargs='*', type=str)
    parameter.parse_args()
    return parameter

if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain
    username = options.username
    password = options.password
    file_name = options.file_name
    dep = Deploy(domain, file_name, username, password)
    dep.deploy()
