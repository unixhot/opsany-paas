import inspect

from opsanymcp.api.base_api import BaseObj

a = ["alert_subject", "alert_message", "event_id", "hostname", "show_name", "host_ip", "trigger_severity"]
class PromApi(BaseObj):
    def opsany_prom_alert_info(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        # page = kwargs.get("page", 1)
        # page_size = kwargs.get("page_size", 50)
        alert_type = kwargs.get("alert_type", "all")  # node blackbox all
        severity = kwargs.get("severity")

        params = {"alert_type": alert_type}
        if severity:
            params["severity"] = severity
        status, data_list, mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, mess)
        headers = {
            "instance": "实例唯一标识",
            "show_name": "实例名称",
            "ip": "IP地址",
            "visible_name": "可见名",
            "job": "实例类型(node: 主机，blackbox_http_1m：HTTP(S)，blackbox_tcp_1m：ICMP，blackbox_icmp_1m：TCP，blackbox_grpc_1m：gRPC，blackbox_ssh_1m：SSH)；1m:一分钟，5m: 五分钟，10m:十分钟",
            "consul_service_id": "consul id",
            "name": "告警分组名称",
            "alert_name": "告警名称",
            "model_code": "资源平台模型code",
            "severity": "告警级别(NotClassified: 未分类 Information: 信息 Warning: 警告 Average: 一般严重 High: 严重 Disaster: 灾难)",
            "query": "告警条件语句",
            "rule_labels": "告警标签",
            "summary": "告警摘要",
            "description": "告警描述",
            "state": "状态(firing: 告警中)",
            "activeAt": "发生事件",
            "value": "数值",
            "service_check": "服务拨测(blackbox: 服务拨测告警)",
            "service_check_url": "服务拨测地址",
            "prom_name": "Prometheus实例名称",
            "alert_type": "告警类型(metric_alert: 组件监控或服务拨测告警 node: 主机告警)",
        }

        if self.real_data_type == "table_header":
            result = {"columns": headers, "rows": data_list}
        else:
            result = []
            new_user_list = []
            for i in data_list:
                new_user_list.append([str(i.get(h) or "") for h in headers])
            for row in new_user_list:
                row_dict = dict(zip(headers.values(), row))
                result.append(row_dict)
        if not result:
            return self.to_json(False, "获取当前告警数据为空", result)
        return self.to_json(True, mess, result)
