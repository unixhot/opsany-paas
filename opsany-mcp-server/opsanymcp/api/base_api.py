import json
import urllib3
urllib3.disable_warnings()
from requests import request


class APIEndpoints:
    url_startswith = "/api/c/compapi/"

    cmdb = url_startswith + "cmdb/"
    rbac = url_startswith + "rbac/"
    control = url_startswith + "control/"
    workbench = url_startswith + "workbench/"
    job = url_startswith + "job/"
    prom = url_startswith + "prom/"
    evnet = url_startswith + "event/"
    kbase = url_startswith + "kbase/"

    check_api_token = "/login/accounts/is_login/"
    opsany_cmdb_api_resources = cmdb + "get_cmdb_model_tree/"
    opsany_cmdb_get_resource_fields = cmdb + "get_model_field/"

    opsany_cmdb_get_model_group = cmdb + "get_model_group/"

    opsany_cmdb_get_model = cmdb + "model_get/"
    opsany_cmdb_create_model = cmdb + "model_create/"
    opsany_cmdb_update_model = cmdb + "model_update/"
    opsany_cmdb_delete_model = cmdb + "model_delete/"

    opsany_cmdb_get_resource = cmdb + "model_data_get/"
    opsany_cmdb_create_model_fields = cmdb + "model_field_create/"
    opsany_cmdb_update_model_fields = cmdb + "model_field_update/"
    opsany_cmdb_delete_model_fields = cmdb + "model_field_delete/"

    opsany_cmdb_get_model_field = cmdb + "model_field_get/"
    opsany_cmdb_create_model_field = cmdb + "model_field_create/"
    opsany_cmdb_update_model_field = cmdb + "model_field_update/"
    opsany_cmdb_delete_model_field = cmdb + "model_field_delete/"

    opsany_cmdb_create_resource = cmdb + "model_data_create/"
    opsany_cmdb_update_resource = cmdb + "model_data_update/"
    opsany_cmdb_delete_resource = cmdb + "model_data_delete/"

    opsany_cmdb_get_can_add_link_inst_list = cmdb + "get_link_inst/"
    opsany_cmdb_get_resource_link_inst_count = cmdb + "get_model_rel_field/"
    opsany_cmdb_get_resource_link_inst_list = cmdb + "get_inst_by_rel_data/"
    opsany_cmdb_resource_add_link_inst = cmdb + "update_link_inst/"
    opsany_cmdb_resource_remove_link_inst = cmdb + "update_link_inst/"

    opsany_rbac_get_or_search_all_user = opsany_rbac_get_my_user_info = rbac + "get_all_user/"
    opsany_rbac_create_user = rbac + "post_create_user/"
    opsany_rbac_delete_user = rbac + "post_delete_user/"
    opsany_rbac_update_user = rbac + "post_update_user/"
    opsany_monitor_alert_info = control + "problem_info/"
    opsany_workbench_work_order_inst = workbench + "get_work_order_inst/"
    opsany_workbench_work_order_folder = workbench + "get_work_order_temp_folder_list/"
    opsany_workbench_work_order_temp = workbench + "get_work_order_temp_list/"
    opsany_workbench_work_order_submit = workbench + "work_order_submit/"
    opsany_job_get_tool_market_list = opsany_job_get_job_list = opsany_job_get_script_list = job + "get_tool_market_list/"
    opsany_job_run_job_by_id = job + "run_job_by_id/"
    opsany_job_run_script_by_id = job + "run_script_by_id/"
    opsany_job_run_script_by_script = job + "run_script_by_script/"
    opsany_job_get_run_result_by_log_id = job + "get_run_result_by_log_id/"
    opsany_job_create_script_library = job + "script_library_create/"
    opsany_control_get_managed_host_list = control + "get_control_agent_info/"
    opsany_control_get_controller_list = control + "get_controller_proxy/"
    opsany_control_get_host_group_list = control + "get_agent_group_list/"
    opsany_control_get_zabbix_list = control + "get_zabbix_server_list/"
    opsany_control_get_prometheus_list = control + "post_prom_tree_to_prom/"
    opsany_control_get_dashboard_list = control + "get_grafana_dashboard_list/"
    opsany_control_get_zabbix_temp_list = control + "get_zabbix_template_list/"
    opsany_control_create_host = control + "post_create_host/"

    opsany_prom_alert_info = prom + "get_alert/"
    opsany_event_alert_info = evnet + "get_event_alert/"
    opsany_kbase_read_kbase_list = kbase + "kbase_list/"
    opsany_kbase_read_kbase_article = kbase + "kbase_article/"


class BaseObj:
    def __init__(self, name, config, username=None, api_token=None):
        self.name = name
        self.username = username
        self.api_token = api_token

        self.api_service = config.get("apiService")
        self.url = self.api_service.get("url")
        self.licence = self.api_service.get("licence")
        self.super_username = self.api_service.get("super_username")
        self.bk_username = username
        self.is_bk_username = False
        self.bk_role = 0
        self.headers = {"Content-Type": "application/json; charset=utf-8", "User-Agent": "OpsAny MCP Server v2.3.3"}
        self.bk_app_code = self.api_service.get("bk_app_code")
        self.bk_app_secret = self.api_service.get("bk_app_secret")

        self.resource_id_default_field = config.get('resourceIdDefaultField') or "code,VISIBLE_NAME,name"
        self.resource_id_field_search = config.get('resourceIdFieldSearch') or False
        self.real_data_type =config.get('realDataType') or "table_header"
        self.base_params = {"username": self.username}
        self.request_status, self.request_message = self._check_user()

    def _check_user(self):
        if not self.username:
            return False, "MCP Client headers缺少参数用户名(username)"
        if not self.api_token:
            return False, "MCP Client headers缺少参数APIToken(user-api-token), 工作台-个人设置-API Token"

        check_url = APIEndpoints.check_api_token
        params = {"bk_token": self.api_token, "request_api_from": "esb", "username": self.bk_username}
        err_title = "用户认证失败: {}"
        try:
            url = str(self.url) + check_url
            res = request("GET", url, data={}, params=params, headers=self.headers, timeout=5, verify=False)
            try:
                json_data = res.json()
                message = json_data.get("message") or "Success"
                if json_data.get("result"):
                    user_dict = json_data.get("data") or {}
                    if isinstance(user_dict, dict):
                        if self.bk_username == user_dict.get("username"):
                            self.bk_role = user_dict.get("bk_role") or 0
                            return True, message
                        else:
                            return False, err_title.format("无效的令牌，请检查后重试！")
                    else:
                        return False, err_title.format(message)
                else:
                    return False, err_title.format(message) + "(工作台-个人设置-API Token，创建并获取Token)"
            except Exception as e:
                return False, err_title.format(str(res.content.decode()))
        except Exception as e:
            return False, err_title.format(str(e))

    def _base_run(self, fun_name, method, params, body, headers, kwargs):
        tool_timeout = kwargs.pop("tool_timeout", 60)
        status, data_list, mess = self.call(fun_name, method, params=params, body=body, timeout=tool_timeout)
        if not status:
            return self.to_json(False, mess)
        if self.real_data_type == "table_header":
            result = {"columns": headers, "rows": data_list}
        else:
            result = []
        return self.to_json(True, mess, result)

    def call(self, url_fun, method, params=None, body=None, headers=None, timeout=None):
        if not timeout:
            timeout = 30
        if not params:
            params = dict()
        if not body:
            body = dict()
        if not headers:
            headers = self.headers
        url_path = getattr(APIEndpoints, url_fun, None)
        if not url_path:
            return False, [], f"HTTP 请求失败: 工具 {url_fun}中函数API(APIEndpoints)未定义！"

        url = str(self.url) + url_path
        base_params = {
            "bk_app_code": self.bk_app_code,
            "bk_app_secret": self.bk_app_secret,
        }
        if self.is_bk_username:
            base_params["bk_username"] = self.bk_username
        else:
            base_params["bk_token"] = self.api_token
            headers["Cookie"] = f"bk_token={self.api_token};opsany_language=chinese_simplified"
        params.update(base_params)
        body.update(base_params)
        try:
            res = request(method, url, data=json.dumps(body), params=params, headers=headers, timeout=timeout, verify=False)
            # print("call_url", res.url)
            # print("body.body", body)
            # print("call_res", res.content.decode())
            try:
                json_data = res.json()
                result = json_data.get("result")
                message = json_data.get("message")
                data = json_data.get("data")
                if not result:
                    return False, [], message
                return True, data, message or "Success"
            except Exception as e:
                return False, [], f"HTTP 响应解析失败: {res.content.decode()}"
        except Exception as e:
            return False, [], f"HTTP 请求失败: {str(url)} {str(e)}"

    def to_json(self, success=False, msg="", result=None, ensure_ascii=False, indent=2):
        res_data = {"success": success, "error": msg, "data": result}
        return json.dumps(res_data, ensure_ascii=ensure_ascii, indent=indent)

    def run(self, arguments: dict):
        fun = getattr(self, self.name, None)
        if fun:
            try:
                return fun(**arguments)
            except Exception as e:
                return self.to_json(False, f"Tool {self.name} error, arguments {arguments}, msg: {e}")
        return self.to_json(False, f"Unknown OpsAny Tool: {self.name}")

