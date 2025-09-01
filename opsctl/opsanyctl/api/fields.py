from opsanyctl.api.base import BaseObj
from opsanyctl.constants import URL_DICT


class ResourceFields(BaseObj):
    def get_resource_field(self, resource):
        params = {
            "model_code": resource,
        }
        params.update(self.base_params)
        status, field_list, mess = self.this_request._request(URL_DICT.get("fields"), "GET", params=params, body={})
        if not status:
            return False, [], [], f"获取当前资源 {resource} 字段失败: {mess}，请使用 opsanyctl api-resources 获取支持的资源！"
        headers = {
            "model_name": "资源名称",
            "model_code": "资源标识",
            "name": "字段名称",
            "code": "字段标识",
            "index": "字段序号",
            "type_name": "字段类型",
            "field_group_code": "字段类分组",
            "is_relationship_field": "字段属性",
        }
        data = []
        for field in field_list:
            l = []
            for k, v in headers.items():
                v = str(field.get(k))
                if k == "is_relationship_field":
                    if v == "": v = "基本属性"
                    elif v == "1": v = "从属关系"
                    elif v == "2": v = "连接关系"
                l.append(v)
            data.append(l)
        return True, list(headers.values()), data, ""