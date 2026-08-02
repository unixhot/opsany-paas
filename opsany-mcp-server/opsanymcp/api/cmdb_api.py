import inspect
from datetime import datetime

from opsanymcp.api.base_api import BaseObj


class CMDBApi(BaseObj):
    def opsany_cmdb_api_resources(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        limit = kwargs.get("limit", 100)
        output = kwargs.get("output", "")
        resource_type = kwargs.get("resource_type", "zc,zz,yw,gl")
        try:
            limit = int(limit) or 100
        except Exception:
            limit = 100

        params = {"tree": "3"}
        if resource_type:
            params["resource_type"] = resource_type
        if output =="extend":
            params["model_type"] = "resource_count,field_count"
        status, model_list, mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, mess)
        headers = {
            "model_type_name": "资源类型名称",
            "model_type_code": "资源类型标识",
            "model_group_name": "资源分组名称",
            "model_group_code": "资源分组标识",
            "model_name": "资源名称",
            "model_code": "资源标识",
        }
        if output =="extend":
            headers.update({"resource_count": "资源实例总数", "field_count": "基本属性(字段数量)", "parent_field_count": "从属关系(字段数量)", "link_field_count": "连接关系(字段数量)"})
        dict_data_list = []
        list_data_list = []
        for type_dict in model_list:
            type_name = type_dict.get("value")
            type_code = type_dict.get("key")
            group_children = type_dict.get("children") or []
            for group in group_children:
                group_name = group.get("value")
                group_code = group.get("key")
                children = group.get("children") or []
                for child in children:
                    value =  child.get("value")
                    key =  child.get("key")
                    res_dict = {
                        "model_type_name": type_name,
                        "model_type_code": type_code,
                        "model_group_name": group_name,
                        "model_group_code": group_code,
                        "model_name": value,
                        "model_code": key,
                    }
                    base_li = [type_name, type_code, group_name, group_code, child.get("value"), key]
                    if output == "extend":
                        res_dict.update(**child)
                        base_li.extend([
                            str(child.get("resource_count") or 0),
                            str(child.get("field_count") or 0),
                            str(child.get("parent_field_count") or 0),
                            str(child.get("link_field_count") or 0)
                        ]
                    )
                    list_data_list.append(base_li)
                    dict_data_list.append(res_dict)
        list_data_list = list_data_list[:limit]
        dict_data_list = dict_data_list[:limit]
        if not list_data_list:
            return self.to_json(False, mess)
        result = []
        if self.real_data_type == "table_header":
            result = {"columns": headers, "rows": dict_data_list}
        else:
            for row in list_data_list:
                row_dict = dict(zip(headers.values(), row))
                result.append(row_dict)
        if not result:
            return self.to_json(False, "获取当前资源数据为空", result)
        return self.to_json(True, mess, result)

    def opsany_cmdb_get_resource_fields(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        model_code = kwargs.get("model_code")
        if not model_code:
            return self.to_json(False, "model_code parameter is required")
        params = {
            "model_code": model_code,
            "field_type": kwargs.get("field_type") or "01",
        }
        params.update(self.base_params)
        status, field_list, mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, f"获取当前资源 {model_code} 字段失败: {mess}，请使用 api-resources 获取支持的资源！")
        headers = {
            "model_name": "资源名称",
            "model_code": "资源标识",
            "name": "字段名称",
            "code": "字段标识",
            "index": "字段序号",
            "type_name": "字段类型",
            "not_null": "是否必填",
            "built_in": "是否内置",
            "describe": "字段描述",
            "field_group_code": "字段类分组",
            "is_relationship_field": "字段属性(1:从属 2：连接 空:普通字段)",
            "attribute": "字段相关配置",
            "attribute.关系类型": "字段关系类型配置",
            "attribute.用户提示": "字段提示",
            "attribute.校验规则": "字段校验规则",
            "attribute.rule": "字段校验规则",
        }
        dict_data_list = []
        list_data_list = []
        if self.real_data_type == "table_header":
            result = {"columns": headers, "rows": field_list}
        else:
            result = []
            for field in field_list:
                l = []
                for k, v in headers.items():
                    v = str(field.get(k))
                    if k == "is_relationship_field":
                        if v == "": v = "基本属性"
                        elif v == "1": v = "从属关系"
                        elif v == "2": v = "连接关系"
                    l.append(v)
                list_data_list.append(l)
            for row in list_data_list:
                row_dict = dict(zip(headers.values(), row))
                result.append(row_dict)
        return self.to_json(True, mess, result)

    def opsany_cmdb_get_resource(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        model_code = kwargs.get("model_code")
        resource_id = kwargs.get("resource_id")
        search = kwargs.get("search")
        fields = kwargs.get("fields")
        page = kwargs.get("page", 1)
        limit = kwargs.get("limit", 20)
        if model_code is None:
            return self.to_json(False, "model_code parameter is required")

        headers = []
        field_code_list = []
        params = {
            "model_code": model_code,
            "page": page,
            "per_page": limit,
        }
        if resource_id and ("=" in resource_id) and self.resource_id_field_search:
            find_fields, find_value = resource_id.split("=")[:2]
            if resource_id:
                params["find_fields"] = find_fields
                params["find_value"] = find_value

        elif resource_id:
            resource_id_field = self.resource_id_default_field.split(",")
            new_list = []
            for i in resource_id_field:
                if i == "code": new_list.append(i)
                else: new_list.append(model_code + "_" + i)
            params["find_fields"] = ",".join(new_list)
            params["find_value"] = resource_id
        if search:
            params["search_type"] = "all"
            params["search_data"] = search

        params.update(self.base_params)
        fields_dict = {"model_code": model_code, "field_type": "01"}
        fields_status, field_list, fields_mess = self.call("opsany_cmdb_get_resource_fields", "GET", params=fields_dict, body={})
        if not fields_status:
            return self.to_json(False, f"获取当前资源 {model_code} 字段失败: {fields_mess}，请使用 api-resources 获取支持的资源！")

        data_status, data_dict, data_mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {model_code} 数据失败: {data_mess}，请使用 api-resources 获取支持的资源！")

        if not data_dict:
            return self.to_json(False,f"获取当前资源 {model_code} 获取数据为空！")
        if fields == "all":
            new_field_list = field_list
        elif not fields:
            new_field_list = field_list[:8]
        else:
            new_field_list = []
            fields = fields.split(",")
            for i in field_list:
                if i.get("code") in fields:
                    new_field_list.append(i)

        current = data_dict.get("current")
        page_size = data_dict.get("pageSize")
        total = data_dict.get("total")
        data_list = data_dict.get("data", [])
        total_pages = (total + page_size - 1) // page_size
        mess = f"第 {current} 页，共 {total_pages} 页；当前页 {len(data_list)} 条，总共 {total} 条。"

        if self.real_data_type == "table_header":
            result = {"columns": new_field_list, "rows": data_dict}
        else:
            for field in field_list:
                field_code = field.get("code")
                field_name = field.get("name")
                if (fields and (field_code not in fields)) and (fields and (field_name not in fields)):
                    continue
                is_relationship_field = field.get("is_relationship_field")
                if is_relationship_field:
                    continue
                headers.append([field_name, field_code])
                field_code_list.append(field_code)
            headers.insert(0, ["序号", "code"])
            data_list.insert(0, headers)
            result = data_list
        return self.to_json(True, mess, result)

    def opsany_cmdb_get_can_add_link_inst_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        code = kwargs.get("code")
        field_code = kwargs.get("field_code")
        search = kwargs.get("search")
        current = kwargs.get("current", 1)
        pageSize = kwargs.get("pageSize", 10)
        search_type = kwargs.get("search_type")
        search_data = kwargs.get("search_data")
        if not code:
            return self.to_json(False,f"code 参数必传！")
        if not field_code:
            return self.to_json(False,f"field_code 参数必传！")

        params = {
            "code": code,
            "field_code": field_code,
            "search": search,
            "current": current,
            "pageSize": pageSize,
            "search_type": search_type,
            "search_data": search_data,
        }
        data_status, data_dict, data_mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {code} 数据失败: {data_mess}！")

        if not data_dict:
            return self.to_json(False,f"获取当前资源 {code} 获取数据为空！")

        # new_field_list = {
        #     "field_list": "关联关系实例字段",
        #     "field_list.code": "字段标识",
        #     "field_list.name": "字段名称",
        #     "field_list.attribute": "字段相关配置",
        #     "field_list.index": "字段序号",
        #     "field_list.type_name": "字段类型",
        #     "inst_data": "关联关系实例数据",
        #     "inst_data.total": "关联关系实例数据",
        #     "inst_data.current": "关联关系实例数据",
        #     "inst_data.pageSize": "关联关系实例数据",
        #     "inst_data.data": "关联关系实例数据",
        #     "inst_data.data.name": "实例唯一标识",
        #     "inst_data.data.visible_name": "实例名称",
        #     "inst_data.data.code": "实例ID",
        #     "inst_data.data.model_code": "实例模型code",
        #     "inst_data.data.data": "实例数据对象",
        #     "inst_data.data.parent_inst": "实例从属标识",
        #     "inst_data.data.created_at": "实例创建时间",
        #     "inst_data.data.updated_at": "实例更新时间",
        # }
        field_list = data_dict.get("field_list") or {}
        inst_data = data_dict.get("inst_data") or {}
        current = inst_data.get("current")
        page_size = inst_data.get("pageSize")
        total = inst_data.get("total")
        data_list = inst_data.get("data", [])
        for i in inst_data.get("data", []):
            i.pop("link_inst", None)
        total_pages = (total + page_size - 1) // page_size
        mess = f"第 {current} 页，共 {total_pages} 页；当前页 {len(data_list)} 条，总共 {total} 条。"

        result = {"columns": field_list, "rows": inst_data}

        return self.to_json(True, mess, result)

    def opsany_cmdb_get_resource_link_inst_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        code = kwargs.get("code")
        field_code = kwargs.get("field_code")
        search = kwargs.get("search")
        current = kwargs.get("current", 1)
        pageSize = kwargs.get("pageSize", 10)
        search_type = kwargs.get("search_type")
        search_data = kwargs.get("search_data")
        if not code:
            return self.to_json(False,f"code 参数必传！")
        if not field_code:
            return self.to_json(False,f"field_code 参数必传！")

        params = {
            "code": code,
            "field_code": field_code,
            "search": search,
            "current": current,
            "pageSize": pageSize,
            "search_type": search_type,
            "search_data": search_data,
        }
        data_status, data_dict, data_mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {code} 数据失败: {data_mess}！")

        if not data_dict:
            return self.to_json(False,f"获取当前资源 {code} 获取数据为空！")

        # new_field_list = {
        #     "field_list": "关联关系实例字段",
        #     "field_list.code": "字段标识",
        #     "field_list.name": "字段名称",
        #     "field_list.attribute": "字段相关配置",
        #     "field_list.index": "字段序号",
        #     "field_list.type_name": "字段类型",
        #     "inst_data": "关联关系实例数据",
        #     "inst_data.total": "关联关系实例数据",
        #     "inst_data.current": "关联关系实例数据",
        #     "inst_data.pageSize": "关联关系实例数据",
        #     "inst_data.data": "关联关系实例数据",
        #     "inst_data.data.name": "实例唯一标识",
        #     "inst_data.data.visible_name": "实例名称",
        #     "inst_data.data.code": "实例ID",
        #     "inst_data.data.model_code": "实例模型code",
        #     "inst_data.data.data": "实例数据对象",
        #     "inst_data.data.parent_inst": "实例从属标识",
        #     "inst_data.data.created_at": "实例创建时间",
        #     "inst_data.data.updated_at": "实例更新时间",
        # }
        field_list = data_dict.get("field_list") or {}
        inst_data = data_dict.get("inst_data") or {}
        current = inst_data.get("current")
        page_size = inst_data.get("pageSize")
        total = inst_data.get("total")
        data_list = inst_data.get("data", [])
        for i in inst_data.get("data", []):
            i.pop("link_inst", None)
        total_pages = (total + page_size - 1) // page_size
        mess = f"第 {current} 页，共 {total_pages} 页；当前页 {len(data_list)} 条，总共 {total} 条。"

        result = {"columns": field_list, "rows": inst_data}

        return self.to_json(True, mess, result)

    def opsany_cmdb_get_resource_link_inst_count(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        code = kwargs.get("code")
        if not code:
            return self.to_json(False,f"code 参数必传！")
        params = {
            "code": code,
        }
        data_status, data_dict, data_mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {code} 数据失败: {data_mess}！")

        if not data_dict:
            return self.to_json(False,f"获取当前资源 {code} 获取数据为空！")

        field_list = {
            "parent": "从属关系",
            "parent.code": "字段标识",
            "parent.name": "字段名称",
            "parent.attribute": "字段相关配置",
            "parent.index": "字段序号",
            "parent.type_name": "字段类型",
            "parent.type": "关联关系类型(1: 从属 2: 连接)",
            "parent.count": "实例数量",
            "link": "关联关系实例数据",
            "link.code": "字段标识",
            "link.name": "字段名称",
            "link.attribute": "字段相关配置",
            "link.index": "字段序号",
            "link.type_name": "字段类型",
            "link.type": "关联关系类型(1: 从属 2: 连接)",
            "link.count": "实例数量",
        }
        result = {"columns": field_list, "rows": data_dict}
        return self.to_json(True, "Success", result)

    def opsany_cmdb_resource_add_link_inst(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        code = kwargs.get("code")
        if not code:
            return self.to_json(False,f"code 参数必传！")
        body = {
            "code": code,
            "api_from": "mcp",
            "model_code": kwargs.get("model_code"),
            "field_code": kwargs.get("field_code"),
            "target_code_list": kwargs.get("target_code_list"),
            "method": "POST",
        }
        data_status, data_list, data_mess = self.call(fun_name, "POST", params={}, body=body, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {code} 数据失败: {data_mess}！")

        field_list = {}

        result = {"columns": field_list, "rows": data_list}

        return self.to_json(True, data_mess, result)

    def opsany_cmdb_resource_remove_link_inst(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 60)
        code = kwargs.get("code")
        if not code:
            return self.to_json(False,f"code 参数必传！")
        body = {
            "code": code,
            "api_from": "mcp",
            "model_code": kwargs.get("model_code"),
            "field_code": kwargs.get("field_code"),
            "target_code_list": kwargs.get("target_code_list"),
            "method": "DELETE",
        }
        data_status, data_list, data_mess = self.call(fun_name, "POST", params={}, body=body, timeout=tool_timeout)
        if not data_status:
            return self.to_json(False,f"获取当前资源 {code} 数据失败: {data_mess}！")

        field_list = {}
        result = {"columns": field_list, "rows": data_list}
        return self.to_json(True, data_mess, result)

    def opsany_cmdb_create_resource(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        body = {
            "model_code": kwargs.get("model_code"),
            "username": self.username,
            "parent_inst": kwargs.get("parent_inst"),
            "import_type": kwargs.get("import_type", "API创建"),
            "data": kwargs.get("data"),
        }
        result_headers = {
            "code": "资源ID",
            "model_code": "资源类型",
            "data": "数据Dict",
            "parent_inst": "从属实例",
        }
        return self._base_run(fun_name, "POST", {}, body, result_headers, kwargs)

    def opsany_cmdb_update_resource(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        body = {
            "model_code": kwargs.get("model_code"),
            "username": self.username,
            "code": kwargs.get("code"),
            "data": kwargs.get("data"),
            "parent_inst": kwargs.get("parent_inst"),
        }
        result_headers = {
            "code": "资源ID",
            "model_code": "资源类型",
            "data": "数据Dict",
            "parent_inst": "从属实例",
        }
        return self._base_run(fun_name, "POST", {}, body, result_headers, kwargs)

    def opsany_cmdb_delete_resource(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        body = {
            "model_code": kwargs.get("model_code"),
            "username": self.username,
            "code": kwargs.get("code"),
        }

        result_headers = {
            "code": "资源ID",
            "model_code": "资源类型",
            "data": "数据Dict",
            "parent_inst": "从属实例",
        }
        return self._base_run(fun_name, "POST", {}, body, result_headers, kwargs)

    def opsany_cmdb_get_model_group(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        params = {
            "model_type": kwargs.get("model_type"),
        }
        result_headers = {
            "code": "资源ID",
            "name": "资源类型",
            "index": "数据Dict",
            "built_in": "数据Dict",
            "model_type": "模型类型(zc:资产 yw:业务 zz:组织 gl:其他)",
        }
        return self._base_run(fun_name, "GET", params, {}, result_headers, kwargs)

    def opsany_cmdb_get_model(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        params = {
            "model_type": kwargs.get("model_type"),
        }
        result_headers = {
            "code": "资源ID",
            "name": "资源类型",
            "index": "数据Dict",
            "built_in": "数据Dict",
            "model_type": "模型类型(zc:资产 yw:业务 zz:组织 gl:其他)",
        }
        return self._base_run(fun_name, "GET", params, {}, result_headers, kwargs)

    def opsany_cmdb_create_model(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        params = {
            "code": kwargs.get("code"),
            "name": kwargs.get("name"),
            "model_type": kwargs.get("model_type"),
            "model_group": kwargs.get("model_group"),
            "clone_model": kwargs.get("clone_model"),
            "built_in": kwargs.get("built_in"),
        }
        result_headers = {
            "code": "模型code",
            "name": "模型名称",
            "index": "模型排序",
            "description": "模型描述",
            "built_in": "是否内置",
            "model_group": "模型分组",
            "is_stop": "是否停用",
            "is_display": "是否展示",
            "icon_code": "图标",
            "model_type": "模型类型(zc:资产 yw:业务 zz:组织 gl:其他)",
        }
        return self._base_run(fun_name, "POST", {}, params, result_headers, kwargs)

    def opsany_cmdb_update_model(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        params = {
            "code": kwargs.get("code"),
            "built_in": kwargs.get("built_in"),
            "name": kwargs.get("name"),
            "model_group": kwargs.get("model_group"),
        }
        result_headers = {
            "code": "模型code",
            "name": "模型名称",
            "index": "模型排序",
            "description": "模型描述",
            "built_in": "是否内置",
            "model_group": "模型分组",
            "is_stop": "是否停用",
            "is_display": "是否展示",
            "icon_code": "图标",
            "model_type": "模型类型(zc:资产 yw:业务 zz:组织 gl:其他)",
        }
        return self._base_run(fun_name, "POST", {}, params, result_headers, kwargs)

    def opsany_cmdb_delete_model(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        params = {
            "code": kwargs.get("code"),
        }
        result_headers = {}
        return self._base_run(fun_name, "POST", {}, params, result_headers, kwargs)

    def opsany_cmdb_create_model_fields(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        data = {
            "code": kwargs.get("code"),
            "name": kwargs.get("name"),
            "type_name": kwargs.get("type_name"),
            "model_code": kwargs.get("model_code"),
            "field_group_code": kwargs.get("field_group_code"),
            "not_null": kwargs.get("not_null"),
            "built_in": kwargs.get("built_in"),
            "index": kwargs.get("index"),
            "attribute": kwargs.get("attribute"),
        }
        result_headers = {
            "code": "字段code",
            "name": "字段名称",
            "index": "字段排序",
            "type_name": "字段类型",
            "built_in": "是否必填",
            "model_code": "模型code",
            "field_group_code": "字段分组",
            "not_null": "排序",
            "attribute": "字段属性(包括规则下拉数据等相关配置)",
            "attribute.关系类型": "关系类型",
            "attribute.rule_id": "规则类型",
            "attribute.默认值": "默认值",
            "attribute.用户提示": "用户提示",
            "attribute.rule": "规则",
            "attribute.选项": "下拉框选项",
        }
        return self._base_run(fun_name, "POST", {}, data, result_headers, kwargs)

    def opsany_cmdb_update_model_fields(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        data = {
            "code": kwargs.get("code"),
            "name": kwargs.get("name"),
            "type_name": kwargs.get("type_name"),
            "model_code": kwargs.get("model_code"),
            "field_group_code": kwargs.get("field_group_code"),
            "not_null": kwargs.get("not_null"),
            "built_in": kwargs.get("built_in"),
            "index": kwargs.get("index"),
            "attribute": kwargs.get("attribute"),
        }
        result_headers = {
            "code": "字段code",
            "name": "字段名称",
            "index": "字段排序",
            "type_name": "字段类型",
            "built_in": "是否必填",
            "model_code": "模型code",
            "field_group_code": "字段分组",
            "not_null": "排序",
            "attribute": "字段属性(包括规则下拉数据等相关配置)",
            "attribute.关系类型": "关系类型",
            "attribute.rule_id": "规则类型",
            "attribute.默认值": "默认值",
            "attribute.用户提示": "用户提示",
            "attribute.rule": "规则",
            "attribute.选项": "下拉框选项",
        }
        return self._base_run(fun_name, "POST", {}, data, result_headers, kwargs)

    def opsany_cmdb_delete_model_fields(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        data = {
            "code": kwargs.get("code"),
        }
        result_headers = {}
        return self._base_run(fun_name, "POST", {}, data, result_headers, kwargs)
