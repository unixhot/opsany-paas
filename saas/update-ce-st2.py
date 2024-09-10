import time

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class StackStormApi:
    def __init__(self, st2_url, st2_username, st2_password, timeout=8):
        self.url = st2_url
        self.username = st2_username
        self.password = st2_password
        self.timeout = timeout
        self.AUTH_TOKENS = "/auth/tokens/"  # 登录 POST
        self.API_KEYS = "/api/v1/apikeys/"  # api key list GET POST
        self.GET_PACK = "/api/v1/packs/{ref_or_id}"
        self.EXECUTION_LOG = "/api/v1/executions/{execution_id}/"
        self.INSTALL_PACK = "/api/v1/packs/install"
        self.CONFIG_PACK = "/api/v1/configs/{ref_or_id}"

        self.headers = {
            'accept': 'application/json'
        }

    def get_token(self):
        """Login and get token"""
        try:
            req = requests.session()
            req.auth = (self.username, self.password)
            url = self.url + self.AUTH_TOKENS
            headers = {
                'accept': 'application/json'
            }
            res = req.post(url, headers=headers, timeout=self.timeout, verify=False)
            if res.status_code in [200, 201]:
                return True, res.json().get("token")

            else:
                return False, res.json()
        except Exception as e:
            return False, e

    def update_headers(self):
        """update headers token"""
        status, message = self.get_token()
        if not status:
            return self.headers
        return self.headers.update({"x-auth-token": message})

    def get_workflow_execution_log(self, execution_id):
        """get execution log"""
        try:
            url = self.url + self.EXECUTION_LOG.format(execution_id=execution_id)
            self.update_headers()
            res = requests.get(url, headers=self.headers, timeout=5, verify=False)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                return True, res.json()
            else:
                return False, res.json()
        except Exception as e:
            return False, str(e)

    def install_pack(self, packs):
        print("开始执行install_pack", packs)
        """install pack"""
        try:
            url = self.url + self.INSTALL_PACK
            data_dic = {
                "packs": packs
            }
            data_dic = json.dumps(data_dic)
            status, message = self.get_token()
            if not status:
                return False, message
            self.headers.update({"x-auth-token": message})
            res = requests.post(url, headers=self.headers, timeout=self.timeout, data=data_dic, verify=False)
            res.encoding = 'utf-8'

            if res.status_code == 202:
                return True, res.json()
            else:
                return False, res.json()
        except Exception as e:
            return 0, e


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, st2_url, st2_username, st2_password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.st2_url = st2_url
        self.st2_api = StackStormApi(st2_url, st2_username, st2_password)
        self.token = self.login()

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code in [200, 400]:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except Exception:
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
        except Exception:
            return False

    def init_st2_pack(self, opsany_core_pack_source_dict, st2_pack_install_type="file"):
        print("开始执行init_st2_pack")
        """install opsany_core and opsany_workflow"""
        if st2_pack_install_type in ["git", "gitee"]:
            pack_url = opsany_core_pack_source_dict.get("gitee")
        elif st2_pack_install_type in ["github"]:
            pack_url = opsany_core_pack_source_dict.get("github")
        # elif st2_pack_install_type in ["gitlab"]:
        #     pack_url = opsany_core_pack_path_dict.get("gitlab")
        else:
            pack_url = opsany_core_pack_source_dict.get("file")
        print("Downloading the OpsAny core package is expected to take 60 seconds...")
        status, message = self.st2_api.install_pack(pack_url)
        print("执行install_pack结果", status, message)
        if not status:
            return False, message
        start_time = time.time()
        while True:
            status, res_dic = self.st2_api.get_workflow_execution_log(message.get("execution_id", ""))
            if not status:
                if status == 0:
                    return False, res_dic
                continue
            if res_dic.get("status") == "succeeded":
                return True, ""
            if res_dic.get("status") in ["failed", "timeout"]:
                try:
                    errors = res_dic.get("result", {}).get("errors", [])[0].get("result").get("stderr", "")
                except Exception:
                    errors = "Install error please contact the developer"
                return False, errors
        end_time = time.time()
        if (end_time - start_time) > 120:
            return False, "The installation time exceeds 120 seconds"
        return True, message


def start(paas_domain, username, password, st2_url, st2_username, st2_password,
          app_code="devops", app_secret="", st2_pack_install_type="file"):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password, st2_url=st2_url,
                        st2_username=st2_username, st2_password=st2_password)

    # 初始化StackStorm核心包路径
    # opsany_core_pack_path = "/opt/stackstorm-packs/opsany_core/"
    # opsany_workflow_pack_path = "/opt/stackstorm-packs/opsany_workflow/"
    opsany_core_pack_source_dict = {
        "file": ["/opt/stackstorm-packs/opsany_core/", "/opt/stackstorm-packs/opsany_workflow/"],
        "gitee": ["https://gitee.com/opsany/opsany_core.git", "https://gitee.com/opsany/opsany_workflow.git"],
        "github": ["https://github.com/unixhot/opsany_core.git", "https://github.com/unixhot/opsany_workflow.git"],
    }
    # 配置核心包参数
    pack = "opsany_core"
    api_url = paas_domain
    # app_code = "devops"
    # app_secret = "f64f3fae-b335-11eb-a88b-00163e105ceb"
    access_token = "opsany-esb-auth-token-9e8083137204"
    # 1. 初始化应用平台初始化StackStorm服务

    # 2. 初始化StackStorm包 opsany_core, opsany_workflow（需要提前将该两个包放入st2服务器指定路径）
    st2_status, st2_data = run_obj.init_st2_pack(opsany_core_pack_source_dict, st2_pack_install_type)
    print("[SUCCESS] init st2 pack success.") if st2_status else print(
        "[ERROR] init st2 pack error info, error info: {}".format(str(st2_data)))

    # 3. 配置 opsany_core包参数


def add_parameter():
    parameter = argparse.ArgumentParser("init_ce_st2")
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--st2_url", help="StackStorm service url.", required=True)
    parameter.add_argument("--st2_username", help="StackStorm service username.", required=True)
    parameter.add_argument("--st2_password", help="StackStorm service password.", required=True)
    parameter.add_argument("--app_code", help="app code.", required=True)
    parameter.add_argument("--app_secret", help="app secret.", required=True)
    parameter.add_argument("--st2_core_pack_source", default="StackStorm",
                           help="St2 core pack source [file|git|gitee|github].", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain  # 域名
    username = options.username  # 平台用户名
    password = options.password  # s平台密码
    st2_url = options.st2_url  # st2地址
    st2_username = options.st2_username  # st2用户名
    st2_password = options.st2_password  # st2密码
    app_code = options.app_code  # 平台code(可以使用devops)
    app_secret = options.app_secret  # 平台code对应secret
    st2_core_pack_source = options.st2_core_pack_source  # st2用户名
    start(domain, username, password, st2_url=st2_url, st2_username=st2_username, st2_password=st2_password,
          app_code=app_code, app_secret=app_secret, st2_pack_install_type=st2_core_pack_source)
