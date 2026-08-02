from opsanymcp.api.base_api import BaseObj
from opsanymcp.api.cmdb_api import CMDBApi
from opsanymcp.api.control_api import ControlApi
from opsanymcp.api.job_api import JobApi
from opsanymcp.api.rbac_api import RbacApi
from opsanymcp.api.monitor_api import MonitorApi
from opsanymcp.api.workbench_api import WorkbenchApi
from opsanymcp.api.event_api import EventApi
from opsanymcp.api.prom_api import PromApi
from opsanymcp.api.kbase_api import KbaseApi


__all__ = ["BaseObj", "CMDBApi", "RbacApi", "MonitorApi", "WorkbenchApi", "JobApi", "ControlApi",
           "EventApi", "PromApi", "KbaseApi"]


API_CLASS_DICT = {
    "opsany_cmdb": CMDBApi,
    "opsany_rbac": RbacApi,
    "opsany_monitor": MonitorApi,
    "opsany_workbench": WorkbenchApi,
    "opsany_job": JobApi,
    "opsany_control": ControlApi,
    "opsany_event": EventApi,
    "opsany_prom": PromApi,
    "opsany_kbase": KbaseApi,
}

_SORTED_PREFIXES = sorted(API_CLASS_DICT.keys(), key=len, reverse=True)


def get_opsany_api(name, config, username, api_token):

    api_class = BaseObj
    for prefix in _SORTED_PREFIXES:
        if name.startswith(prefix):
            api_class = API_CLASS_DICT[prefix]
            break
    api = api_class(name, config, username, api_token)
    # 检查请求状态
    if not api.request_status:
        return False, api, api.to_json(False, api.request_message)
    return True, api, "Success"


if __name__ == '__main__':
    from opsanymcp import load_yaml_config
    config_status, config = load_yaml_config("../../config/config.yaml")
    print(config_status, config)
    if not config_status:
        pass
    username, user_api_token = "huxingqi", "YKLiPy5Vwm_c_0a-lpc6z4dstA19YRagZdDEh0xtRt41oO3ulNattibKDNrp6jeduiSPnMXuzwTa3lJUdYOdLw"
    # username, user_api_token = "hu29", "wmMrlEujTCG2VE-Y_9V_nfxOyNv8YBjTIwi8Pnulgw80OM3-JWz3HdIJ_B92cQBUVoQvv-OBbh9xuH2Tp6DN3A"
#     name, arguments = "opsany_cmdb_create_resource", {
#   "model_code": "REGION",
#   "parent_inst": "41761",
#   "data": {
#     "REGION_VISIBLE_NAME": "测试区域5",
#     "REGION_name": "test_region5",
#     "REGION_ID": "R0015",
#     "REGION_TYPE": "公共区域"
#   }
# }
    # name, arguments = "opsany_cmdb_get_resource_fields", {"model_code": "SERVER", "field_type": ""}
    # name, arguments = "opsany_cmdb_update_resource", {"model_code": "SERVER", "code": "918", "parent_inst": "4193"}
    # name, arguments = "opsany_cmdb_create_resource", {"model_code": "SERVER", "data": {"SERVER_name": "hu1122", "SERVER_VISIBLE_NAME": "胡1122", "SERVER_IN_RACK": "4193"}}
    # name, arguments = "opsany_cmdb_get_can_add_link_inst_list", {"field_code": "APPLICATION_IN_SERVER", "code": 3979}
    # name, arguments = "opsany_cmdb_get_resource_link_inst_count", {"field_code": "APPLICATION_IN_SERVER", "code": 3979}
    # name, arguments = "opsany_cmdb_resource_add_link_inst", {"field_code": "APPLICATION_IN_SERVER", "code": 360, "target_code_list": [4194, 4179, 4201]}
    # name, arguments = "opsany_cmdb_resource_add_link_inst", {"field_code": "APPLICATION_IN_SERVER", "code": 29, "target_code_list": [52]}
    # name, arguments = "opsany_cmdb_get_model", {"model_type": "yw"}
    name, arguments = "opsany_cmdb_delete_model", {
        "code": "HUXINGQI1",
        "built_in": False,
        "name": "胡兴起1",
        "model_type": "zc",
        "model_group": "HOST",
        "clone_model": "",
    }
    name, arguments = "opsany_cmdb_update_model", {
        "code": "HUXINGQI1",
        "built_in": True,
        "name": "胡兴起11111",
        "model_type": "zc",
        "model_group": "HOST",
        "clone_model": "",
    }
    name, arguments = "opsany_job_create_script_library", {
        "script_type": "sh",
        "script_name": "自动创建1",
        "version_remarks": "大模型创建",
        "script": """#!/bin/bash
#------内置脚本方法，可以直接调用------
anynowtime=$(date +'%Y-%m-%d %H:%M:%S')
NOW="echo [$anynowtime][PID:$$]""",
    }
    name, arguments = "opsany_cmdb_get_model_group", {}
    # name, arguments = "opsany_kbase_read_kbase_article", {
    #     "kbase": "7072d695cd1f331a83292474345cab79",
    #     "data_type": "all",
    #     "unique_code": "6171c642b7bf3b26b4249b27787a18f3"
    # }


    # name, arguments = "opsany_cmdb_delete_model", {
    #     "code": "HUXINGQI",
    # }
    # name, arguments = "opsany_cmdb_update_resource", {"code": "47", "model_code": "IDC", "data":{}, "parent_inst": "46"}
    # name, arguments = "opsany_cmdb_get_resource_link_inst_list", {"field_code": "APPLICATION_IN_SERVER", "code": 3979}
    # name, arguments = "opsany_cmdb_update_resource", {"model_code": "SERVER", "code": "918", "data": {"SERVER_IN_RACK": "4193"}}
    # name, arguments = "opsany_cmdb_get_resource", {"model_code": "SERVER"}
#     name, arguments = "opsany_workbench_work_order_temp", {
#   "id": 1,
#   "form_fields": True,
#   "tool_timeout": 30
# }
    # name, arguments = "opsany_workbench_work_order_folder", {}
    # name, arguments = "opsany_cmdb_api_resources", {"resource_type": "zc"}
    # name, arguments = "opsany_cmdb_create_resource", {
    #     "model_code": "SERVER",
    #     "username": "huxingqi",
    #     "import_type": "API批量创建",
    #     "data": {
    #         "SERVER_name": "huxingqi5",
    #         "SERVER_VISIBLE_NAME": "胡兴起5"
    #     }
    # }


    # username, user_api_token = "hu29", "JdowNwGoyg2-YUxPk6JtPEZno8GSnKVMHCxAYOmDfTRkuBtZpaQ_KWTsAuHVAuau"
    # username, user_api_token = "hu23", "6qd7z3nQ1ESXASyz2-_f9m2EyQ3J_e7cUByBAuvnVdJuMH0etVRP-VL1B_sBHfMpIkLHtcc-MUUruYZ3bpQz1w"

    # name, arguments = "opsany_workbench_work_order_inst", {}
    # name, arguments = "opsany_job_run_script_by_id", {"script_id": 57, "server": "192.168.0.111,192.168.0.112,192.168.0.119"}
    # name, arguments = "opsany_control_get_managed_host_list", {"host_type": "SERVER"}
    # name, arguments = "opsany_job_run_script_by_script", {"server": "192.168.0.116,192.168.0.115", "script": "df -h && free -m"}
    # name, arguments = "opsany_control_get_controller_list", {"name": "外"}
    # name, arguments = "opsany_control_get_controller_list", {"id": "1"}
    # name, arguments = "opsany_control_get_host_group_list", {"id": "1"}
    # name, arguments = "opsany_control_get_zabbix_list", {}
    # name, arguments = "opsany_control_get_prom_prometheus_list", {}
    # name, arguments = "opsany_control_get_dashboard_list", {}
    # name, arguments = "opsany_control_get_zabbix_temp_list", {"zabbix_id": 1}
    d = {
    "show_name": "192.168.0.111",
    "name": "192.168.0.111-6379",
    "ip": "192.168.0.111",

    "system_type": "Linux",
    "controller_id": 1,
    "control_type": 1,
    "ssh_port": "22",
    "login_port": "3389",
    "username": "root",
    "group_id": 1,
    "ssh_type": "password",
    "password": "******",
    "host_type": "SERVER",
    "monitor_type": "Zabbix",
    "controller_zabbix": "1",
    "privilege": False,
    "privilege_username": "",
    "privilege_password": "",
    "template_list": [{
        "temp_name": "Linux by Zabbix agent",
        "temp_id": "10001"
    }],
    "ipmi_address": "",
    "ipmi_username": "",
    "impi_password": "******",
    "is_bastion": False,
    "is_bastion_group": False,
    "timeout": 5,
    "id": 28,
    "controller_prom": None,
    "privilege_type": None,
    "dashboard_dict": {
        "uid": "opsany-zabbix-linux-host",
        "title": "Linux主机大屏",
        "url": "/grafana/d/opsany-zabbix-linux-host/linuxzhu-ji-da-ping",
        "tags": ["HOST", "Zabbix"],
        "value": "opsany-zabbix-linux-host",
        "searchData": "Linux主机大屏HOSTZabbix"
    },
    "variable_list": []
}
    # name, arguments = "opsany_control_get_zabbix_temp_list", {"zabbix_id": 1}

    # name1, arguments1 = "opsany_job_run_script_by_script", {
    #   "run_describe": "执行主机巡检脚本，检查磁盘、内存、负载等信息",
    #   "script": "#!/bin/bash\n# 主机巡检脚本\n# 功能：检查主机的磁盘、内存、负载、CPU、网络等关键信息\n\n df -h",
    #   "server": "192.168.0.111,192.168.0.112,192.168.0.119",
    #   "timeout": 300
    # }

    # name, arguments = "opsany_job_get_run_result_by_log_id", {"log_id": 1479}
    # name, arguments = "opsany_rbac_create_user", {
    # 	"user_info_list": [
    # 		{
    # 			"username": "hu249",
    # 			"chname": "hu249",
    # 			"password": "123456.coM",
    # 			"phone": "18339303172",
    # 			"email": "hu5427@163.com",
    # 			"position": "dev",
    # 			"description": "devvv"
    # 		},
    # 		{
    # 			"username": "huxingqi",
    # 			"chname": "hu25",
    # 			"password": "",
    # 			"phone": "",
    # 			"email": "",
    # 			"position": "dev",
    # 			"description": "devvv"
    # 		},
    #
    # 		{
    # 			"username": "hu20",
    # 			"chname": "hu20",
    # 			"password": "123456.coM"
    # 		}
    # 	]
    # }
    # name, arguments = "opsany_rbac_create_user", {
    #     "user_info_list": [
    #         {
    #           "username": "staff01",
    #           "chname": "测试用户1",
    #           "password": "Test123456",
    #           "phone": "13800138001",
    #           "email": "staff01@example.com",
    #           "description": "测试用户1",
    #           "position": "测试工程师"
    #         },
    #         {
    #           "username": "staff02",
    #           "chname": "测试用户2",
    #           "password": "Test123456",
    #           "phone": "13800138002",
    #           "email": "staff02@example.com",
    #           "position": "测试工程师",
    #           "description": "测试用户2"
    #         },
    #       ]
    # }
    # name, arguments = "opsany_rbac_delete_user", {"user_info_list": ["111"]}
    # name, arguments = "opsany_rbac_update_user", {"user_info_list": [{"username": "test01", "is_activate": False}]}

    status, api, msg = get_opsany_api(name, config, username, user_api_token)
    print(777777, api.run(arguments))
    print(666666, status, api, msg)
    print(len("opsany_cmdb_get_resource_link_inst_count"))