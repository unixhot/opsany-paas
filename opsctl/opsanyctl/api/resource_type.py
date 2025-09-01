from opsanyctl.api.base import BaseObj
from opsanyctl.constants import URL_DICT


class ResourceType(BaseObj):
    def get_resources_type(self, output=None, limit=100, default_short=None):
        if not default_short: default_short = {}
        try:
            limit = int(limit) or 100
        except Exception:
            limit = 100

        params = {"tree": "3"}
        if output =="extend":
            params["model_type"] = "resource_count,field_count"
        status, model_list, mess = self.this_request._request(URL_DICT.get("resource_type"), "GET", params=params, body={})
        if not status:
            return False, [], [], mess
        headers = {
            "model_type_name": "资源类型名称",
            "model_type_code": "资源类型标识",
            "model_group_name": "资源分组名称",
            "model_group_code": "资源分组标识",
            "model_name": "资源名称",
            "model_code": "资源标识",
            "short_name": "资源简称",
        }
        if output =="extend":
            headers.update({"field_count": "基本属性(字段数量)", "parent_field_count": "从属关系(字段数量)", "link_field_count": "连接关系(字段数量)", "resource_count": "资源总数"})
        data = []
        short_dict = {}
        for k, v in default_short.items():
            li = short_dict.get(v) or []
            li.append(k)
            short_dict[v] = li
            pass
        for type_dict in model_list:
            type_name = type_dict.get("value")
            type_code = type_dict.get("key")
            group_children = type_dict.get("children") or []
            for group in group_children:
                group_name = group.get("value")
                group_code = group.get("key")
                children = group.get("children") or []
                for child in children:
                    key =  child.get("key")
                    base_li = [type_name, type_code, group_name, group_code, child.get("value"), key]
                    base_li.append(",".join(short_dict.get(key) or []))
                    if output == "extend":
                        base_li.extend([str(child.get("field_count") or 0), str(child.get("parent_field_count") or 0),
                                        str(child.get("link_field_count") or 0), str(child.get("resource_count") or 0)])
                    data.append(base_li)
        return True, list(headers.values()), data[:limit], "Success"
