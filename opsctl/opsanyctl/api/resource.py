from rich.text import Text

from opsanyctl.api.base import BaseObj
from opsanyctl.constants import URL_DICT


class Resource(BaseObj):
    def get_resource(self, resource, resource_id, search, fields, page=1, limit=20, resource_id_default_field=None, resource_id_field_search=True):
        headers = []
        field_code_list = []
        data = []

        params = {
            "model_code": resource,
            "page": page,
            "per_page": limit,
        }
        if resource_id and ("=" in resource_id) and resource_id_field_search:
            find_fields, find_value = resource_id.split("=")[:2]
            if resource_id:
                params["find_fields"] = find_fields
                params["find_value"] = find_value

        elif resource_id:
            resource_id_field = resource_id_default_field.split(",")
            new_list = []
            for i in resource_id_field:
                if i == "code": new_list.append(i)
                else: new_list.append(resource + "_" + i)
            params["find_fields"] = ",".join(new_list)
            params["find_value"] = resource_id
        if search:
            params["search_type"] = "all"
            params["search_data"] = search

        params.update(self.base_params)
        status, field_list, mess = self.this_request._request(URL_DICT.get("fields"), "GET", params=params, body={})
        if not status:
            return False, [], [], f"获取当前资源 {resource} 字段失败: {mess}，请使用 opsanyctl api-resources 获取支持的资源！"
        status, data_dict, mess = self.this_request._request(URL_DICT.get("resource"), "GET", params=params, body={})
        if not fields:
            field_list = field_list[:8]
        else:
            fields = fields.split(",")
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

        if not data_dict:
            return Text, headers, [], "没有数据！"

        current = data_dict.get("current")
        page_size = data_dict.get("pageSize")
        total = data_dict.get("total")
        data_list = data_dict.pop("data", [])

        for d in data_list:
            json_data = d.get("data") or {}
            new = [str(d.get("code"))]
            for code in field_code_list:
                j = json_data.get(code)
                if j is None: new.append("null")
                else: new.append(str(j) or "-")
            data.append(new)
        total_pages = (total + page_size - 1) // page_size
        message = f"第 {current} 页，共 {total_pages} 页；当前页 {len(data_list)} 条，总共 {total} 条。"
        # message = f"{current}页/{total_pages}页  {len(data_list)}条/{total}条"
        return True, headers, data, message
