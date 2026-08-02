import inspect

from opsanymcp.api.base_api import BaseObj


class EventApi(BaseObj):
    def opsany_event_alert_info(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        tool_timeout = kwargs.pop("tool_timeout", 30)
        params = {
            "code": kwargs.get("code"),
            "current": kwargs.get("current"),
            "pageSize": kwargs.get("pageSize"),
            "alert_type": kwargs.pop("alert_type", "my_alert"),  # my_alert all_alert
            "status": kwargs.get("status", "1"),  # 1：待处理 2：处理中 3：已关闭
            "alert_source": kwargs.get("alert_source"),  # Prometheus Zabbix alert_service
            "alert_subject": kwargs.get("alert_subject"),
            "alert_message": kwargs.get("alert_message"),
            "event_id": kwargs.get("event_id"),
            "hostname": kwargs.get("hostname"),
            "show_name": kwargs.get("show_name"),
            "host_ip": kwargs.get("host_ip"),
            "trigger_severity": kwargs.get("trigger_severity"),
        }

        status, data_list, mess = self.call(fun_name, "GET", params=params, body={}, timeout=tool_timeout)
        if not status:
            return self.to_json(False, mess)
        headers = {
            "current": "当前页码",
            "pageSize": "每页数量",
            "total": "当前搜索告警总数",
            "pending_count": "待处理告警数量",
            "claim_count": "处理中告警数量",
            "close_count": "已关闭告警数量",
            "data.code": "告警code",
            "data.alert_source": "告警来源 ",
            "data.alert_subject": "告警标题",
            "data.alert_message": "告警内容",
            "data.alert_description": "告警描述",
            "data.event_id": "告警ID",
            "data.host_id": "主机ID",
            "data.hostname": "node/主机唯一标识 组件/组件唯一标识 服务拨测/服务拨测唯一标识",
            "data.show_name": "node/关联主机可见名 组件/组件可见名 服务拨测/服务拨测名称",
            "data.event_duration": "持续时间",
            "data.event_date": "告警事件创建的时间",
            "data.ends_at": "Prometheus原生结束时间字符串",
            "data.ends_date": "告警事件结束的时间",
            "data.acknowledged": "告警认领(Zabbix 问题知晓状态0-不知道 1-知道)",
            "data.trigger_severity": "告警级别 0: 未分类 1: 信息 2: 警告 3: 一般严重 4: 严重 5: 灾难。",
            "data.status": "告警状态",
            "data.updated_at": "告警接入事件中心时间",
            "data.created_at": "告警更新时间",
            "data.handler_user": "操作人",
            "data.close_description": "关闭原因",
            "data.job": "实例类型",
            "data.model_code": "实例资源平台模型code",
            "data.alert_service": "第三方告警接入",
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
