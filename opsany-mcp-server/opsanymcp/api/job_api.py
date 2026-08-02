import inspect
from datetime import datetime

from opsanymcp.api.base_api import BaseObj


class JobApi(BaseObj):
    job_fields = {
        "job_id": "作业ID(执行作业时使用该ID)",
        "name": "作业名称",
        "visible": "可见范围",
        "describe": "作业描述",
        "job_count": "作业步骤数量",
        "create_time": "创建时间",
        "update_time": "更新时间",
        "create_user": "创建人(用户名)",
        "create_user_ch_name": "创建人(中文名名)",
        "step_list": "执行步骤",
        "step_list.id": "执行步骤ID",
        "step_list.agent_count": "主机个数",
        "step_list.step_name": "步骤名称",
        "step_list.step_index": "步骤序号",
        "step_list.implement_type": "实现类型",
        "step_list.job_type": "脚本类型",
        "step_list.parameter": "执行参数",
        "step_list.time_out": "超时时间",
        "step_list.exception_handle": "执行逻辑处理：1：执行失败终止整个作业 2：任何情况都继续执行。",
        "step_list.script": "执行任务脚本信息",
        "step_list.script.id": "执行任务脚本ID",
        "step_list.script.create_time": "脚本创建时间",
        "step_list.script.update_time": "脚本更新时间",
        "step_list.script.script_name": "脚本名称",
        "step_list.script.file_name": "脚本文件名称",
        "step_list.script.create_user": "脚本创建人(用户名)",
        "step_list.script.create_user_ch_name": "脚本创建人(中文名)",
        "step_list.script.update_user": "脚本修改人(用户名)",
        "step_list.script.update_user_ch_name": "脚本修改人(中文名)",
        "step_list.script.version_remarks": "脚本备注",
        "step_list.script.script_from": "脚本来源",
        "step_list.script.version": "脚本版本号",
        "step_list.script.visible": "可见范围 1：私有 2：公开",
        "step_list.script.script_type": "脚本类型",
        "step_list.script.file_url": "脚本地址",
        "step_list.script.script": "脚本内容",
    }

    script_fields = {
        "script_id": "脚本ID(执行脚本时使用该ID)",
        "script_name": "脚本名称",
        "file_name": "脚本文件名",
        "file_url": "脚本文件路径",
        "version": "脚本版本号",
        "version_remarks": "版本备注，脚本描述。",
        "visible": "可见范围",
        "script_type": "脚本类型",
        "script_from": "脚本来源",
        "describe": "脚本描述",
        "create_time": "创建时间",
        "update_time": "更新时间",
        "create_user": "创建人(用户名)",
        "create_user_ch_name": "创建人(中文名名)",
        "script": "脚本内容",
    }

    def opsany_job_get_tool_market_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        data_type = kwargs.get("data_type")
        job_id = kwargs.get("job_id")
        script_id = kwargs.get("script_id")
        script_name = kwargs.get("script_name")
        create_user = kwargs.get("create_user")
        visible = kwargs.get("visible")
        script_type = kwargs.get("script_type")
        search_type = kwargs.get("search_type")
        search_data = kwargs.get("search_data")

        params = {}
        if data_type: params["data_type"] = data_type
        if job_id: params["job_id"] = job_id
        if script_id: params["script_id"] = script_id
        if script_name: params["script_name"] = script_name
        if create_user: params["create_user"] = create_user
        status, data_dict, msg = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"获取作业平台工具市场作业或脚本失败，失败原因：{msg}！")

        if self.real_data_type == "table_header":
            if job_id:
                result = {"columns": self.job_fields, "rows": data_dict}
            elif script_id:
                result = {"columns": self.script_fields, "rows": data_dict}
            else:
                result = {"columns": {"job_list": self.job_fields, "script_list": self.script_fields}, "rows": data_dict}
        else:
            data_dict["job_list_fields"] = self.job_fields
            data_dict["script_list_fields"] = self.script_fields
            result = data_dict
        return self.to_json(True, msg, result)

    def opsany_job_get_job_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        job_id = kwargs.get("job_id")
        script_name = kwargs.get("name")
        create_user = kwargs.get("create_user")
        visible = kwargs.get("visible")
        params = {"data_type": "job"}
        if job_id: params["job_id"] = job_id
        if script_name: params["script_name"] = script_name
        if create_user: params["create_user"] = create_user
        status, data_dict, msg = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"获取作业平台工具市场作业或脚本失败，失败原因：{msg}！")
        if not data_dict:
            data_dict = {}
        job_list = data_dict.get("job_list") or []

        if self.real_data_type == "table_header":
            if job_id:
                rows = data_dict
            else:
                rows = job_list
            result = {"columns": self.job_fields, "rows": rows}
        else:
            data_dict["fields"] = self.job_fields
            result = job_list
        return self.to_json(True, msg, result)

    def opsany_job_get_script_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        script_id = kwargs.get("script_id")
        script_name = kwargs.get("script_name")
        create_user = kwargs.get("create_user")
        visible = kwargs.get("visible")
        script_type = kwargs.get("script_type")
        search_type = kwargs.get("search_type")
        search_data = kwargs.get("search_data")

        params = {"data_type": "script"}
        if script_id: params["script_id"] = script_id
        if script_name: params["script_name"] = script_name
        if create_user: params["create_user"] = create_user
        status, data_dict, msg = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"获取作业平台工具市场作业或脚本失败，失败原因：{msg}！")
        if not data_dict:
            data_dict = {}
        script_list = data_dict.get("script_list") or []

        if self.real_data_type == "table_header":
            if script_id:
                result = {"columns": self.script_fields, "rows": data_dict}
            else:
                result = {"columns": self.script_fields, "rows": script_list}
        else:
            data_dict["fields"] = self.script_fields
            data_dict["script_list"] = script_list
            result = data_dict
        return self.to_json(True, msg, result)

    def opsany_job_run_job_by_id(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        job_id = kwargs.get("job_id")
        body = {"job_id": job_id}
        status, data_dict, msg = self.call(fun_name, "POST", params={}, body=body, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"执行作业失败，失败原因：{msg}！")
        return self.to_json(True, msg, {"log_id": data_dict})

    def opsany_job_run_script_by_id(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        script_id = kwargs.get("script_id")
        server = kwargs.get("server") or ""
        parameter = kwargs.get("parameter")
        run_describe = kwargs.get("run_describe") or f"CMP调用，执行人：{self.username}!"
        time_out = kwargs.get("time_out") or 60
        if not server:
            return self.to_json(False, f"执行作业失败，缺少主机信息(server: 多条用逗号隔开)！")

        # if "," in server:
        #     server = server.split(",")
        # else:
        #     server = [server]
        # server_list = [{"host_name": str(i).strip()} for i in server]
        body = {
            "script_id": script_id,
            "server": server,
            "parameter": parameter,
            "run_describe": run_describe,
            "time_out": time_out,
        }
        status, data_dict, msg = self.call(fun_name, "POST", params={}, body=body, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"执行作业失败，失败原因：{msg}！")

        return self.to_json(True, msg, {"log_id": data_dict})

    def opsany_job_run_script_by_script(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        task_name = kwargs.get("task_name")
        script_format = kwargs.get("script_format")
        script_type = kwargs.get("script_type") or "content"
        script = kwargs.get("script") or ""
        server_type = kwargs.get("server_type") or "host_name"
        server = kwargs.get("server") or ""
        parameter = kwargs.get("parameter")
        run_describe = kwargs.get("run_describe") or f"CMP调用，执行人：{self.username}!"
        timeout = kwargs.get("timeout") or 60
        if not server:
            return self.to_json(False, f"执行作业失败，缺少主机信息(server: 多条用逗号隔开)！")

        # if "," in server:
        #     server = server.split(",")
        # else:
        #     server = [server]
        # server_list = [{"host_name": str(i).strip()} for i in server]
        body = {
            "script_format": script_format,
            "task_name": task_name,
            "script_type": script_type,
            "script": script,
            "server_type": server_type,
            "server": server,
            "parameter": parameter,
            "run_describe": run_describe,
            "timeout": timeout,
        }
        status, data_dict, msg = self.call(fun_name, "POST", params={}, body=body, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"执行作业失败，失败原因：{msg}！")

        return self.to_json(True, msg, {"log_id": data_dict})

    def opsany_job_get_run_result_by_log_id(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        log_id = kwargs.get("log_id")
        params = {"task_log_id": log_id}
        status, data_dict, msg = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"获取执行结果失败，失败原因：{msg}！")

        log_field_list = {
            "id": "执行任务ID",
            "create_time": "执行任务开始时间",
            "time": "执行任务耗时",
            "end_time": "执行任务结束时间",
            "state": "执行任务状态",
            "name": "执行任务名称",
            "task_type": "执行任务类型",
            "run_user": "执行人",
            # "proccess": "进度",
            "flag": "是否完成标识",
            "task_status": "状态1：",
            "run_describe": "执行原因",
            "call_type": "执行方式",
            "step_list": "执行步骤",
            "step_list.id": "执行步骤ID",
            "step_list.time": "执行步骤耗时",
            "step_list.state": "执行步骤状态",
            "step_list.job_status": "状态码",
            "step_list.step_name": "执行步骤名称",
            "step_list.step_index": "执行步步骤序号",
            "step_list.implement_type": "实现类型",
            "step_list.script_from": "脚本来源",
            "step_list.parameter": "执行参数",
            "step_list.start_time": "开始时间",
            "step_list.end_time": "结束时间",
            "step_list.script": "执行任务脚本信息",
            "step_list.script.id": "执行任务脚本ID",
            "step_list.script.create_time": "脚本创建时间",
            "step_list.script.update_time": "脚本更新时间",
            "step_list.script.script_name": "脚本名称",
            "step_list.script.file_name": "脚本文件名称",
            "step_list.script.create_user": "脚本创建人(用户名)",
            "step_list.script.create_user_ch_name": "脚本创建人(中文名)",
            "step_list.script.update_user": "脚本修改人(用户名)",
            "step_list.script.update_user_ch_name": "脚本修改人(中文名)",
            "step_list.script.version_remarks": "脚本备注",
            "step_list.script.script_from": "脚本来源",
            "step_list.script.version": "脚本版本号",
            "step_list.script.script_type": "脚本类型",
            "step_list.script.file_url": "脚本地址",
            "step_list.script.script": "执行任务脚本内容",
            "step_list.run_server": "主机执行结果",
            "step_list.run_server.host_name": "主机唯一标识",
            "step_list.run_server.show_name": "主机名称",
            "step_list.run_server.ip": "主机IP",
            "step_list.run_server.agent_state": "主机Agent状态",
            "step_list.run_server.ssh_state": "主机SSH状态",
            "step_list.run_server.ssh_agent_state": "主机可执行状态",
            "step_list.run_server.state": "主机执行状态",
            "step_list.run_server.controller_name": "主机控制器名称",
            "step_list.run_server.controller_id": "主机控制器ID",
            "step_list.run_server.system_type": "主机操作系统类型",
            "step_list.run_server.server_status": "主机状态",
            "step_list.run_server.return_log": "主机执行结果",
        }
        if self.real_data_type == "table_header":
            result = {"columns": log_field_list, "rows": data_dict}
        else:
            result = {"fields": log_field_list, "data_dict": data_dict}
        return self.to_json(True, msg, result)

    def opsany_job_create_script_library(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        body = {
            "script_type": kwargs.get("script_type", "sh"),
            "script_name": kwargs.get("script_name"),
            "visible": kwargs.get("visible", "1"),
            "script": kwargs.get("script"),
            "version_remarks": "MCP创建：{}".format(kwargs.get("version_remarks") or ""),
            "script_from": "1",
            "version": "{}-{}2".format(self.username, datetime.now().strftime('%Y%m%d%H%M%S%f')),
        }
        result_headers = {
            "id": "脚本ID",
            "create_time": "创建时间",
            "update_time": "更新时间",
            "script_name": "脚本名称",
            "file_name": "脚本文件名称",
            "create_user": "创建用户名",
            "create_user_ch_name": "创建中文名",
            "update_user": "更新用户名",
            "update_user_ch_name": "更新中文名",
            "version_remarks": "版本备注",
            "script_from": "脚本来源 手工输入",
            "version": "版本号",
            "visible": "可见范围 1: 私有, 2: 公开",
            "script_type": "脚本类型 sh, py, ps1, bat",
            "file_url": "脚本地址",
            "script": "脚本内容",
        }
        return self._base_run(fun_name, "POST", {}, body, result_headers, kwargs)
