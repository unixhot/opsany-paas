# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
"""  # noqa

from django.http import JsonResponse
from django.views import View
import json
from django.db.models import Q
from datetime import datetime
import time
from django_redis import get_redis_connection
import uuid
import re
from .decorator import user_sync
from control.utils.status_code import *
from control.models import *
from control.utils.salt_ssh_file import *
from control.utils.esb_api import EsbApi
from control.celery_tasks import *
from control.utils.encryption import PasswordEncryption

# Create your views here.


class CreateControllerAdmin(View):
    """
    测试数据：
    {
        "name": "测试",
        "type": "本地",
        "api1": "127.0.0.1",
        "api2": "127.0.0.2",
        "username1": "test1",
        "username2": "test2",
        "password1": "123456",
        "password2": "123456",
        "port1": "8011",
        "port2": "8012",
        "state1": true,
        "state2": false,
        "zabbix_url": "http://monitor.opsany.cn/",
        "zabbix_username": "admin",
        "zabbix_password": "123456.coM",
        "zabbix_state": ""
    }
    """

    def get(self, request):
        """
        获取控制器节点
        """
        data = request.GET.dict()
        name = data.pop("name", None)
        id = data.pop("id", None)
        page = data.pop("page", 1)
        per_page = data.pop("per_page", 10)
        if page:
            page = int(page)
        if not page:
            page = 1
        if per_page:
            per_page = int(per_page)
        if not per_page:
            per_page = 10
        if name:
            b = ControllerAdmin.objects.filter(name=name).first()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, b.to_dict()))
        if id:
            c = ControllerAdmin.objects.filter(id=id).first()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, c.to_dict()))
        end_data = []
        flag = data.pop("data", None)
        lt = ControllerAdmin.fetch_all(**data)
        if flag == "all":
            for i in lt:
                end_data.append(i.to_safe_dict())
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
        current_page = lt[(page - 1) * per_page: page * per_page]
        for i in current_page:
            end_data.append(i.to_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": len(lt),
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))

    def post(self, request):
        data = json.loads(request.body)
        name = data.get("name")
        try:
            c = ControllerAdmin.objects.get(name=name)
        except:
            a = ControllerAdmin.objects.create(**data)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, a.to_dict()))
        return JsonResponse(error(ErrorStatusCode.NAME_IS_UNIQUE))

    def put(self, request):
        data = json.loads(request.body)
        id = data.get("id")
        data.pop("id")
        data["update_time"] = datetime.now()
        ControllerAdmin.objects.filter(id=id).update(**data)
        a = ControllerAdmin.objects.filter(id=id).first()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, a.to_dict()))

    def delete(self, request):
        data = json.loads(request.body)
        id = data.get("id")
        a = ControllerAdmin.objects.get(id=id)
        a.delete()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS))


class UpdateControllerStatusView(View):
    def get(self, request):
        data = ControllerAdmin.objects.all()

        for i in data:
            salt_obj = SaltSshBase(i.to_dict())

            try:
                session = ZabbixApi(i.zabbix_username, i.zabbix_password, i.zabbix_url).session
                if session:
                    zabbix_state = True
                else:
                    zabbix_state = False
            except:
                zabbix_state = False
            ControllerAdmin.objects.filter(id=i.id).update(
                **{"state1": salt_obj.state1,
                   "state2": salt_obj.state2,
                   "update_time": datetime.now(),
                   "zabbix_state": zabbix_state}
            )
        return JsonResponse(success(SuccessStatusCode.CONTROLLER_STATE_UPDATE_SUCCESS))


class GetAllHost(View):
    def get(self, request):
        end_data = []
        lt = AgentAdmin.objects.all().exclude(controller=None)
        for j in lt:
            end_data.append(j.base_to_dict())
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetAgent(View):
    def get(self, request):
        """
        从资源平台获取节点
        """
        token = request.COOKIES.get("bk_token")
        a = EsbApi(token)
        data = a.get_all_host()
        # cmdb_list = []
        end_data = []
        agent_lt = []
        if data:
            for i in data:
                model_code = i.get("model_code")
                if model_code == "CLOUD_SERVER":
                    key2 = model_code + "_INSTANCE_ID"

                else:
                    key2 = model_code + "_name"

                key1 = model_code + "_PUBLIC_IP"
                key7 = model_code + "_INTERNAL_IP"
                key3 = model_code + "_OS"
                key4 = model_code + "_VISIBLE_NAME"
                # key5 = model_code + "_OS_TYPE"
                ip1 = i.get("data").get(key1)
                ip1_type = "外"
                ip2 = i.get("data").get(key7)
                ip2_type = "内"
                # cmdb_list.append(ip)
                dt = {
                    "opt_os": i.get("data").get(key3),
                    "show_name": i.get("data").get(key4),
                    "name": i.get("data").get(key2),
                    "ip1": ip1,
                    "ip2": ip2,
                    # "system_type": i.get("data").get(key3, ""),
                    # "system_name": i.get("data").get(key5, ""),
                    "host_type": model_code,
                    "ip1_type": ip1_type,
                    "ip2_type": ip2_type,
                }
                agent_lt.append(dt)
        #         dt["platform"] = "cmdb"
        #         if b and not b.controller:
        #             dt.pop("name")
        #             AgentAdmin.objects.filter(ip=i.get("data").get(key2)).update(**dt)
        #         if ip and not a:
        #             a = AgentAdmin.objects.create(**dt)
        #             lt.append(a)
        #         if a and a.platform == "control":
        #             AgentAdmin.objects.filter(ip=ip).update(**dt)
        for i in agent_lt:
            ip1 = i.get("ip1")
            _name = i.get("name")
            a = AgentAdmin.objects.filter(name=_name)
            if not a:
                ip2 = i.get("ip2")
                b = AgentAdmin.objects.filter(name=_name)
                if not b:
                    i["add_type"] = "从资源平台导入"
                    end_data.append(i)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))

    """
    {
        "name": "dev-agent.opsany.com",
        "ip": "47.94.196.36",
        "host_type": "CLOUD_SERVER",
        "ip_type": "外",
        "add_type": "从资源平台导入",
        "username": "root",
        "system_type": "Linux",
        "ssh_port": "22",
        "control_type": "Agent",
        "password": "password",
        "controller_id": 1,
    }
    """

    def post(self, request):
        data = json.loads(request.body)
        token = request.COOKIES.get("bk_token")
        ip = data.get("ip")
        controller_id = data.get("controller_id")
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        master = ControllerAdmin.fetch_one(id=controller_id)
        if not controller_id or not master:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_NULL))
        if not AgentAdmin.fetch_one(ip=ip):
            a = AgentAdmin.create(**data)
            try:
                zabbix_obj = ZabbixApi(master.zabbix_username, master.zabbix_password, master.zabbix_url)
                group_id = zabbix_obj.get_default_group()
                if zabbix_obj.session:
                    zabbix_host_id = zabbix_obj.create_host(**a.to_zabbix_dict(group_id))
                    a.update(**{"zabbix_host_id": zabbix_host_id})
            except:
                pass
            data = a.to_dict("all")
            master.update(**{"count": AgentAdmin.fetch_all(controller_id=controller_id).count()})
            ssh_link.delay(master, data, token, cache_key)
            conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, cache_key))

    def put(self, request):
        data = json.loads(request.body)
        id = data.pop("id")
        data["update_time"] = datetime.now()
        data["add_type"] = "手工添加"
        AgentAdmin.objects.filter(id=id).update(**data)
        master = AgentAdmin.objects.filter(id=id).first().controller
        if master:
            salt_obj = SaltSshBase(master.to_dict())
            if salt_obj.salt:
                response = salt_obj.pass_key(data)
                if response:
                    AgentAdmin.objects.filter(id=id).update(**{"agent_state": "SSH已连接"})
                else:
                    AgentAdmin.objects.filter(id=id).update(**{"agent_state": "SSH连接失败"})
            else:
                AgentAdmin.objects.filter(id=id).update(**{"agent_state": "SSH连接失败"})
        else:
            AgentAdmin.objects.filter(id=id).update(**{"agent_state": "SSH未连接"})
        a = AgentAdmin.objects.filter(id=id).first()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, a.to_dict()))


class CreateGroup(View):
    """
    测试数据：
    {
        "name": "分组1",
        "type": "静态",
        "host_list": [
            id1, id2, id3
        ]
    }
    """

    def get(self, request):
        data = request.GET.dict()
        page = int(data.pop("current", 1))
        per_page = int(data.pop("pageSize", 10))
        flag = data.pop("data", "other")
        if data:
            for key in list(data):
                if not data.get(key):
                    del data[key]
            lt = HostGroup.objects.filter(**data).order_by("create_time")
        else:
            lt = HostGroup.objects.all().order_by("create_time")
        end_data = []
        if flag == "all":
            for i in lt:
                end_data.append(i.to_dict())
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
        current_page = lt[(page - 1) * per_page: page * per_page]
        for i in current_page:
            end_data.append(i.to_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": len(lt),
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))

    def post(self, request):
        data = json.loads(request.body)
        host_list = data.pop("host_list")
        end_data = []
        name = data.get("name")
        if name in ["默认分组", "全部分组"]:
            return JsonResponse(error(ErrorStatusCode.GROUP_NAME_NOT_USE))
        # 判断分组是否存在    
        host_group_exist = HostGroup.objects.filter(name=name).exists()
        if host_group_exist:
            return JsonResponse(error(ErrorStatusCode.GROUP_NAME_NOT_USE))
        # 创建分组    
        a = HostGroup.objects.create(**data)
        
        end_data.append({"group": a.to_dict()})
        # 修改当前主机的分组
        if host_list:
            AgentAdmin.objects.filter(id__in=host_list).update(**{"group_id": a.id})

        # 展示所选择的分组的主机
        lt = AgentAdmin.objects.filter(group_id=a.id)
        host = []
        for kk in lt:
            host.append(kk.to_dict())
        end_data.append({"this_group_host": host})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, end_data))

    def put(self, request):
        
        data = json.loads(request.body)
        host_list = data.pop("host_list")
        g_id = data.pop("id")
        # 确认当前分组实例
        is_exists = HostGroup.objects.filter(id=g_id)
        if not is_exists:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_GROUP_MESSAGE))
        # 查询当前分组下的主机
        group_all_host = [each.id for each in AgentAdmin.objects.filter(group_id=int(g_id))]

        # 查询从当前分组删除后的主机
        insert_default_group = []
        for switch_host_group in group_all_host:
            if str(switch_host_group) not in host_list:
                insert_default_group.append(switch_host_group)
        # 把从分组中删除的主机放在默认分组下
    
        default_group_obj = HostGroup.objects.filter(name="默认分组").first()
        AgentAdmin.objects.filter(id__in=insert_default_group).update(group_id=default_group_obj.id)
        
        end_data = []
        # 如果有需要修改的主机分组, 则执行
        if host_list:
            AgentAdmin.objects.filter(id__in=host_list).update(group_id=g_id)
        # 更新分组的详细信息
        HostGroup.objects.filter(id=g_id).update(**data)

        end_data.append({"group": is_exists.first().to_dict()})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, end_data))
        

    def delete(self, request):
        data = json.loads(request.body)
        id = int(data.get("id"))
        default_group_obj = HostGroup.objects.filter(name="默认分组").first()
        AgentAdmin.objects.filter(group_id=id).update(group_id=default_group_obj.id)
        HostGroup.objects.filter(id=id).delete()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS))


class SelectAgentStatusView(View):
    """查询agent当前状态"""

    def get(self, request):
        data = request.GET.dict()
        agent_id = data.get("agent_id")
        print("agent_id", agent_id)
        if agent_id and agent_id != '':
            # a = AgentAdmin.fetch_one(id=id)
            selected_agent_status = AgentAdmin.fetch_one(id=int(agent_id))

            data = dict(
                id=selected_agent_status.id,
                agent_state=selected_agent_status.agent_state,
                update_time=selected_agent_status.update_time,
            )
            print("agent_data", data)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data=data))
        return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))


# 主机管理，高级搜索增加按照分组搜索-获取分组列表
class GroupNameListView(View):
    def get(self, request):
        host_group_queryset = HostGroup.objects.all().order_by("create_time")
        host_group_list = [{"code": group.id, "name": group.name} for group in host_group_queryset]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, host_group_list))


class AgentAdminView(View):
    """
    测试数据
    {
        "ip": "118.31.7.172",
        "name": "www.yukinoneko.com",
        "username": "root",
        "password": "873515490Qq",
        "syssh_linktem_type": "linux",
        "ssh_port": "22",
        "control_type": "Agent",
        "controller_id": "18"
    },{
        "ip": "106.15.50.194",
        "name": "iZuf60pu4nob127vcq5wdvZ",
        "username": "root",
        "password": "Ops@2020Anygo",
        "system_type": "linux",
        "ssh_port": "8022",
        "control_type": "Agent",
        "controller_id": "18"
    }
    """

    def get(self, request):
        data = request.GET.dict()
        token_data = data.get("token_data")
        token = request.COOKIES.get("bk_token", '')
        get_data_type = data.get("type", None)  # CMDB获取管控平台主机时bug
        if token_data:
            token = token_data
        bk_user = EsbApi(token).get_user_info_from_workbench()  # 获取当前登录用户的信息
        user_obj = UserInfo.fetch_one(username=bk_user.get("username"))
        system_type = data.get("system_type")
        control_type = data.get("control_type")
        agent_id = data.get("id")
        controller_id = data.get("controller_id")
        search_type = data.get("search_type")
        search_data = data.get("search_data")
        page = data.pop("page", None)
        per_page = data.pop("per_page", None)
        state_type = data.pop("state_type", None)
        group_name = data.pop("group_name", None)
        if page:
            page = int(page)
        if not page:
            page = 1
        if per_page:
            per_page = int(per_page)
        if not per_page:
            per_page = 10
        if agent_id:
            single_agent_info = AgentAdmin.fetch_one(id=agent_id).to_all_dict()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, single_agent_info))
        if user_obj.role == 1:  # if type == "esb":
            # 如果用户是管理员，获取全部的节点，不需要权限分配过程
            temp_conditions = {}
            if system_type and system_type != "all":
                temp_conditions.update(system_type=system_type)
            if control_type and control_type != "all":
                temp_conditions.update(control_type=control_type)
            if controller_id and controller_id != "all":
                temp_conditions.update(controller_id=int(controller_id))
            if search_type and search_data:
                temp_conditions[search_type + "__contains"] = search_data
            if state_type and state_type != "all":
                temp_conditions["agent_state__contains"] = state_type
            if group_name:
                if group_name == "all":
                    pass
                else:
                    temp_conditions["group_id"] = group_name

            if get_data_type == "esb":  # 发送主机数据至CMDB
                all_host_list = []
                get_cmdb_host_data = AgentAdmin.objects.filter(**temp_conditions).exclude(controller=None)
                for each_to_cmdb in get_cmdb_host_data:
                    all_host_list.append(each_to_cmdb.to_dict())
                _dt = {
                    "total": len(all_host_list),
                    "data": all_host_list
                }
                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, _dt))
                
            lt = AgentAdmin.objects.filter(**temp_conditions)
            current_page_data = []
            for each in lt:
                if each.controller:
                    current_page_data.append(each.to_dict())
            end_data = current_page_data[(page - 1) * per_page: page * per_page]  # data
            _dt = {
                "current": page,
                "pageSize": per_page,
                "total": len(current_page_data),
                "data": end_data
            }
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, _dt))
        temp_conditions = {}  # 创建筛选条件
        if system_type and system_type != "all":
            temp_conditions.update(system_type=system_type)
        if control_type and control_type != "all":
            temp_conditions.update(control_type=control_type)
        if controller_id and controller_id != "all":
            temp_conditions.update(controller_id=int(controller_id))
        if search_type and search_data:
            temp_conditions[search_type + "__contains"] = search_data
        if state_type and state_type != "all":
            temp_conditions["agent_state__contains"] = state_type
        if group_name:
            if group_name == "all":
                pass
            else:
                temp_conditions["group_id"] = group_name

        if get_data_type == "esb":  # 发送主机数据至CMDB
                all_host_list = []
                # 用户不是管理员时获取的主机数据
                not_admin_host_list = UserAgentModel.fetch_all(user_id=user_obj.id).exclude(agent__controller=None)
                
                tmp_end_data = [] # 临时获取主机ID
                for i in not_admin_host_list:
                    tmp_end_data.append(i.agent_id)
                temp_conditions.update(id__in=tmp_end_data)
                get_cmdb_host_data = AgentAdmin.objects.filter(**temp_conditions)
                for each_to_cmdb in get_cmdb_host_data:
                    all_host_list.append(each_to_cmdb.to_dict())
                _dt = {
                    "total": len(all_host_list),
                    "data": all_host_list
                }
                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, _dt))

        # 获取到当前用户权限下的主机列表
        current_agent = UserAgentModel.fetch_all(user_id=user_obj.id).exclude(agent__controller=None)
        total = current_agent.count()
        current_page_data = current_agent[(page - 1) * per_page: page * per_page]  # data
        tmp_end_data = []
        for i in current_page_data:
            tmp_end_data.append(i.agent_id)
        temp_conditions.update(id__in=tmp_end_data)
        _data = AgentAdmin.objects.filter(**temp_conditions)
        end_data = []
        for i in _data:
            end_data.append(i.to_dict())
        _dt = {
            "current": page,
            "pageSize": per_page,
            "total": total,
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, _dt))

    def post(self, request):
        data = json.loads(request.body)
        master_id = data.get("controller_id")
        token = request.COOKIES.get("bk_token")
        bk_user = EsbApi(token).get_user_info_from_workbench()  # 获取当前登录用户的信息
        user_obj = UserInfo.fetch_one(username=bk_user.get("username"))
        ip = data.get("ip")
        name = data.get('name')
        group_id = data.pop("group_id", None)

        # 选择分组 
        group_query = HostGroup.objects.filter(id=group_id).order_by("create_time")
        if not group_query:
            return JsonResponse(error(ErrorStatusCode.GROUP_NOT_FOUND))
        data["group"] = group_query.first()

        system_type = data.get("system_type", "Linux")

        master = ControllerAdmin.objects.filter(id=master_id).first()

        name_exists = AgentAdmin.objects.filter(name=name).exists()
        if name_exists:
            return JsonResponse(error(ErrorStatusCode.AGENT_NAME_IS_UNIQUE, {"error_name": 0}))
        agent_if_exists = AgentAdmin.objects.filter(name=name, controller=master).exists()

        # 如果主机的唯一标识和IP重复，不能导入主机
        if agent_if_exists:
            return JsonResponse(error(ErrorStatusCode.NAME_IS_UNIQUE, {"error_name": 0}))

        # 创建主机
        try:
            if data.get("password"):
                new_password = PasswordEncryption().encrypt(data.get("password"))
                data["password"] = new_password
            new_host = AgentAdmin.objects.create(**data)
        except Exception as e:
            print(e)
            return JsonResponse(error(ErrorStatusCode.NAME_IS_UNIQUE, {"error_name": 0}))

        if user_obj.role != 1:
            UserAgentModel.create(**{"user_id": user_obj.id, "agent": new_host})

        # 同步zabbix主机信息
        try:
            zabbix_obj = ZabbixApi(master.zabbix_username, master.zabbix_password, master.zabbix_url)
            if zabbix_obj.session:
                group_id = zabbix_obj.get_default_group()
                zabbix_host_id = zabbix_obj.create_host(**new_host.to_zabbix_dict(group_id))
                new_host.update(**{"zabbix_host_id": zabbix_host_id})
        except Exception as e:
            print("同步zabbix主机失败", e)
        
        # 更改控制器控制主机的数目
        count = AgentAdmin.objects.filter(controller_id=master_id).count()
        ControllerAdmin.objects.filter(id=master_id).update(**{"count": count, "update_time": datetime.now()})
        data = new_host.to_dict("all")
        data.pop("group", None)
        if data.get("controller_name"):
            del data["controller_name"]
        # 更新agent状态和增加监控模块
        data.update(agent_state='Agent未安装')
        AgentAdmin.fetch_one(id=data.get('id')).update(**data)
        if system_type == "Linux":
            self.update_zabbix(new_host, {
                "template_list": [{"temp_id": 10284, "temp_name": "Template OS Linux by Zabbix agent active"}]})
        else:
            self.update_zabbix(new_host, {
                "template_list": [{"temp_id": 10299, "temp_name": "Template OS Windows by Zabbix agent active"}]})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS))

    def delete(self, request):
        data = json.loads(request.body)
        host_list = data.get("host_list")
        token = request.COOKIES.get('bk_token')
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        master = []
        current_agent_state = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            if a.agent_state == "Agent未安装":
                current_agent_state.append(i)
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        # 判定如果主机是未安装状态就直接删除
        AgentAdmin.objects.filter(id__in=current_agent_state).delete()
        host_list = [each_one for each_one in host_list if each_one not in current_agent_state]
        delete_agent.delay(master, host_list, token, cache_key)
        conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.AGENT_DELETE_SUCCESS, cache_key))

    """
    {
        "id": 456,
        "ip": "124.70.31.19",
        "name": "guan-demo",
        "show_name": "测试",
        "username": "root",
        "system_type": "Linux",
        "ssh_port": "22",
        "control_type": "Agent",
        "agent_state": "SSH已连接",
        "key_url": "",
        "update_time": "2020-09-18T16:25:13",
        "platform": "control",
        "controller_name": "Local-Master",
        "controller_id": 1,
        "zabbix_agent_state": true,
        "zabbix_host_id": null,
        "ssh_type": "key",
        "ssh_key_id": "key",
        "add_type": "",
        "template_list": [
            {
                "id": 1,
                "temp_id": "10284",
                "temp_name": ""
            {
                "temp_id": "10283",
                "temp_name": ""
            }
        ],
        "sign_list": [
            {
                "id": 1,
                "key": "a",
                "value": "a"
            },
            {
                "key": "a",
                "value": "b"
            }
        ],
        "variable_list": [
            {
                "id": 1,
                "key": "$SNMP_COMMUNITY",
                "value": "public",
                "describe": "描述"
            },
            {
                "key": "a",
                "value": "b",
                "describe": "描述"
            }
        ]
    }
    """

    def put(self, request):
        data = json.loads(request.body)
        agent_id = data.get("id")
        group_id = data.pop("group_id", None)
        if group_id:
            group_query = HostGroup.objects.filter(id=group_id).order_by("create_time")
            if not group_query:
                return JsonResponse(error(ErrorStatusCode.GROUP_NOT_FOUND))
            else:
                data["group"] = group_query.first()

        try:
            data_obj = AgentAdmin.fetch_one(id=int(agent_id))
        except:
            data_obj = None
        if data_obj:
            new_a = self.update_info(data_obj, data, request.COOKIES.get("bk_token"))
            return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, new_a))
        return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))

    def update_info(self, a, data, token):
        id = data.get("id")
        ip = data.get("ip")
        name = data.get("name")
        show_name = data.get("show_name")
        username = data.get("username")
        password = data.get("password")
        system_type = data.get("system_type")
        ssh_port = data.get("ssh_port")
        ssh_type = data.get("ssh_type")
        controller_id = data.get("controller_id")
        ssh_key_id = ""
        if ssh_type == "key":
            ssh_key_id = data.get("ssh_key_id")
        control_type = data.get("control_type")

        new_data = {
            "system_type": system_type,
            "show_name": show_name,
            "username": username,
            "ssh_type": ssh_type,
            "ssh_key_id": ssh_key_id,
            "ssh_port": ssh_port,
            "control_type": control_type,
            "name": name,
            "ip": ip,
            "group": data.get("group"),
            "controller_id": controller_id
        }
        if password and password != "******":
            new_password = PasswordEncryption().encrypt(password)
            new_data.update(**{"password": new_password})
        new_a = a.update(**new_data).to_dict()
        return new_a

    # 在监控平台可以修改--AgentAdminUpdateZabbixView-POST-esb
    def update_zabbix(self, a, data):
        
        template_list = data.get("template_list", [])  # 模板
        sign_list = data.get("sign_list", [])  # 标记
        variable_list = data.get("variable_list", [])  # 宏
        zabbix_host_id = a.zabbix_host_id
        master = a.controller

        # 标记更新
        zabbix_sign_list = []
        agent_sign = AgentSignModel.fetch_all(agent=a)
        for k in agent_sign:
            k.delete()
        for kk in sign_list:
            kk.pop("id", None)
            kk.pop("times", None)
            kk["agent_id"] = a.id
            AgentSignModel.create(**kk)
            zabbix_sign_list.append({
                "tag": kk.get("key"),
                "value": kk.get("value")
            })
        # 模板更新
        zabbix_temp_list = []
        agent_temp = AgentTemplate.fetch_all(agent=a)
        for i in agent_temp:
            i.delete()
        for ii in template_list:
            ii.pop("id", None)
            ii["agent_id"] = a.id
            AgentTemplate.create(**ii)
            zabbix_temp_list.append({
                "templateid": str(ii.get("temp_id"))
            })
        # 宏更新
        zabbix_variable_list = []
        agent_variable = AgentVariableModel.fetch_all(agent=a)
        for j in agent_variable:
            j.delete()
        for jj in variable_list:
            jj.pop("id", None)
            jj.pop("times", None)
            jj["agent_id"] = a.id
            AgentVariableModel.create(**jj)
            zabbix_variable_list.append({
                "macro": jj.get("key"),
                "value": jj.get("value"),
                "description": jj.get("describe")
            })

        try:
            zabbix_obj = ZabbixApi(master.zabbix_username, master.zabbix_password, master.zabbix_url)
            zabbix_obj.update_host(zabbix_host_id, zabbix_sign_list, zabbix_temp_list, zabbix_variable_list)
        except:
            pass


class AgentAdminUpdateZabbixView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            token_data = data.get("token_data")
            agent_id = data.get("id")
            template_list = json.loads(data.get("template_list", "[]"))  # 模板
            sign_list = json.loads(data.get("sign_list", "[]"))  # 标记
            variable_list = json.loads(data.get("variable_list", "[]"))  # 宏
            try:
                data_obj = AgentAdmin.fetch_one(id=int(agent_id))
            except:
                data_obj = None
            if not data_obj:
                return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))
            zabbix_host_id = data_obj.zabbix_host_id
            master = data_obj.controller
            # 标记更新
            zabbix_sign_list = []
            agent_sign = AgentSignModel.fetch_all(agent=data_obj)
            for k in agent_sign:
                k.delete()
            for kk in sign_list:
                kk.pop("id", None)
                kk.pop("times", None)
                kk["agent_id"] = data_obj.id
                AgentSignModel.create(**kk)
                zabbix_sign_list.append({
                    "tag": kk.get("key"),
                    "value": kk.get("value")
                })
            # 模板更新
            zabbix_temp_list = []
            agent_temp = AgentTemplate.fetch_all(agent=data_obj)
            for i in agent_temp:
                i.delete()
            for ii in template_list:
                ii.pop("id", None)
                ii["agent_id"] = data_obj.id
                AgentTemplate.create(**ii)
                zabbix_temp_list.append({
                    "templateid": str(ii.get("temp_id"))
                })
            # 宏更新
            zabbix_variable_list = []
            agent_variable = AgentVariableModel.fetch_all(agent=data_obj)
            for j in agent_variable:
                j.delete()
            for jj in variable_list:
                jj.pop("id", None)
                jj.pop("times", None)
                jj["agent_id"] = data_obj.id
                AgentVariableModel.create(**jj)
                zabbix_variable_list.append({
                    "macro": jj.get("key"),
                    "value": jj.get("value"),
                    "description": jj.get("describe")
                })

            try:
                zabbix_obj = ZabbixApi(master.zabbix_username, master.zabbix_password, master.zabbix_url)
                zabbix_obj.update_host(zabbix_host_id, zabbix_sign_list, zabbix_temp_list, zabbix_variable_list)
            except:
                pass
            return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS))
        except Exception as e:
            return JsonResponse(error(ErrorStatusCode.AGENT_STATE_ERROR, str(e)))


class RestartView(View):
    def post(self, request):
        data = json.loads(request.body)
        host_list = data.get("host_list")
        token = request.COOKIES.get('bk_token')
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        master = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        if not master:
            return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
        for k in host_list:
            AgentAdmin.objects.filter(id=k).update(**{"agent_state": "Agent正在重启"})
        restart_agent.delay(master, host_list, token, cache_key)
        conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.HOST_RESTART_SUCCESS, cache_key))


class UninstallAgentView(View):
    def post(self, request):
        data = json.loads(request.body)
        host_list = data.get("host_list")
        token = request.COOKIES.get('bk_token')
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        master = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        if not master:
            return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
        host_list_ok = []
        for k in host_list:
            tmp_a = AgentAdmin.objects.filter(id=k).first()
            if tmp_a.system_type == "Windows":
                continue
            if tmp_a.control_type == "Agent" and tmp_a.system_type != "Windows":
                tmp_a.update(**{"agent_state": "Agent正在卸载"})
                host_list_ok.append(k)
        uninstall_agent.delay(master, host_list_ok, token, cache_key)
        conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.AGENT_UNINSTALL_SUCCESS, cache_key))


class InstallAgentView(View):
    def post(self, request):
        data = json.loads(request.body)
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        host_list = data.get("host_list")
        token = request.COOKIES.get('bk_token')
        master = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        if not master:
            return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))

        host_list_ok = []
        for k in host_list:
            agent_admin_query = AgentAdmin.objects.filter(id=k).first()
            print("agent_admin_query", agent_admin_query.username)
            if agent_admin_query.username != "root":
                continue
            if agent_admin_query.system_type == "Windows":
                continue
            if agent_admin_query.control_type == "Agent" and agent_admin_query.system_type != "Windows":
                agent_admin_query.update(**{"agent_state": "Agent开始安装"})
                host_list_ok.append(k)
        print("host_list_ok", host_list_ok)
        # if host_list_ok:
        install_salt_agent.delay(master, host_list_ok, token, cache_key)
        conn.set(cache_key, "false")
        print("conn", cache_key)
        return JsonResponse(success(SuccessStatusCode.AGENT_INSTALL_SUCCESS, cache_key))


class StopAgentView(View):
    def post(self, request):
        data = json.loads(request.body)
        host_list = data.get("host_list")
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        token = request.COOKIES.get('bk_token')
        master = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        if not master:
            return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
        for k in host_list:
            a = AgentAdmin.objects.filter(id=k).first()
            if a.control_type == "Agent":
                AgentAdmin.objects.filter(id=k).update(**{"agent_state": "正在关闭Agent"})
        stop_agent.delay(master, host_list, token, cache_key)
        conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.HOST_STOP_SUCCESS, cache_key))


class CheckPingView(View):

    def post(self, request):
        """
        测试节点是否可以ping通
        """
        data = json.loads(request.body)
        target_host = data.get("target_host")

        # 获取当前所有控制器
        agent_obj = AgentAdmin.objects.filter(id=int(target_host)).first()

        if not agent_obj:
            return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_ERROR, {"agent_state": "Agent异常", 
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))
        controller_obj = ControllerAdmin.fetch_one(id=agent_obj.controller_id)

        obj = SaltSshBase(controller_obj.to_dict())
        # 测试test.ping
        check_res = obj.salt.ping_check(agent_obj.name)

        # 若是Windows主机，存在如果是睡眠模式，则会获取不到信息
        if check_res.get(agent_obj.name) and ("纳管" in agent_obj.ip):
            agent_obj.update(agent_state="Agent已安装")
            return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_INSTALLED, {"agent_state": "Agent已安装", 
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))
        
        if check_res.get(agent_obj.name):
            agent_obj.update(agent_state="Agent运行中")
            return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_SUCCESS, {"agent_state": "Agent运行中", 
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))

        salt_key_data = obj.salt.list_all_key()  # 获取所有的key

        # 检测已通过的key
        accept_key = salt_key_data.get("minions")
        if agent_obj.name in accept_key:
            agent_obj.update(agent_state="Agent异常")
            return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_ERROR, {"agent_state": "Agent异常", 
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))

        # 检测未通过的key
        no_accept_key = salt_key_data.get("minions_pre")
        if agent_obj.name in no_accept_key:
            agent_obj.update(agent_state="Agent已安装")
            return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_INSTALLED, {"agent_state": "Agent已安装", 
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))

        # 检测master自动拒绝的key
        denied_key = salt_key_data.get("minions_denied")
        if agent_obj.name in denied_key:
            obj.salt.delete_key(agent_obj.name)
            agent_obj.update(agent_state="Agent异常")
        agent_obj.update(agent_state="Agent异常")
        return JsonResponse(success(SuccessStatusCode.AGENT_PING_CHECK_ERROR, {"agent_state": "Agent异常", 
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))


class PassKeyView(View):
    def post(self, request):
        data = json.loads(request.body)
        host_list = data.get("host_list")
        conn = get_redis_connection("default")
        cache_key = str(uuid.uuid4())
        token = request.COOKIES.get('bk_token')
        master = []
        for i in host_list:
            a = AgentAdmin.objects.filter(id=i).first()
            controller_id = a.controller_id
            master.append(controller_id)
        master = list(set(master))
        if not master:
            return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
        for k in host_list:
            AgentAdmin.objects.filter(id=k).update(**{"agent_state": "正在连接Agent"})
        agent_paas_key.delay(master, host_list, token, cache_key)
        conn.set(cache_key, "false")
        return JsonResponse(success(SuccessStatusCode.CONTROL_SUCCESS, cache_key))


class AcquireGrainsView(View):
    def get(self, request):
        """
        信息采集（采集grains录入资源平台）
        :param request:
        :return:
        """
        try:
            token = request.COOKIES.get('bk_token')
            esb_obj = EsbApi(token)
            id = request.GET.get("id")
            agent_admin = AgentAdmin.fetch_one(id=id)

            if not agent_admin:
                return JsonResponse(error(ErrorStatusCode.AGENT_STATE_ERROR))
            name = agent_admin.name
            controller_id = agent_admin.controller_id

            if not controller_id:
                return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
            controller = ControllerAdmin.fetch_one(id=controller_id)
            if not controller:
                return JsonResponse(error(ErrorStatusCode.CONTROLLER_STATE_ERROR))

            obj = SaltSshBase(controller.to_dict())
            all_key = obj.salt.list_all_key()
            minions_list = all_key.get("minions")

            if name not in minions_list:
                return JsonResponse(error(ErrorStatusCode.NOT_PASSKEY))
            grains = obj.salt.grains(name)

            if grains.get("data") and grains.get("data").get(name):

                grains_data = self.proccess_grains(grains, agent_admin.host_type, name, agent_admin.ip)

                # 如果是Windows不采集fqdn (_HOSTNAME)
                update_dt = dict()
                if "纳管后" in agent_admin.ip:
                    update_dt["ip"] = grains_data.get("data").get(agent_admin.host_type + "_INTERNAL_IP")
                    update_dt["ip_type"] = "内"

                if grains.get("data").get(name).get("os") == "Windows":
                    update_dt["system_type"] = "Windows"
                else:
                    update_dt["system_type"] = "Linux"
                esb_obj.import_cloud_server_grains(grains_data)
                AgentAdmin.fetch_one(id=id).update(**update_dt)

                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, grains_data))
            return JsonResponse(error(ErrorStatusCode.ACQUIRE_GRAINS_ERROR))
        except Exception as e:
            print("AcquireGrinsView", e)
            return JsonResponse(error(ErrorStatusCode.ACQUIRE_GRAINS_ERROR))

    def proccess_grains(self, grains_data, model_code, host_name, ip=None):
        """ new_data 增加 model_code + "_HOSTNAME"""
        all_data = grains_data.get("data")
        data = all_data.get(host_name)
        # virtual = data.get("virtual")
        selinux = data.get("selinux", None)
        dns = data.get("dns", None)
        if dns:
            dns = dns.get("nameservers")
        else:
            dns = ""
        if selinux:
            selinux = str(selinux.get("enabled")).lower()
        else:
            selinux = ""
        re_internal_ip_tmp_list = data.get("ip4_interfaces").keys()
        internal_ip = list()
        for each in re_internal_ip_tmp_list:
            reg_netcard = re.compile(r'^(eth|ens|enp|bond)[\d]+', re.M)
            netcard = reg_netcard.search(each)
            if netcard:
                tmp_ip = data.get("ip4_interfaces").get(netcard.group())
                internal_ip.append(tmp_ip[0] if tmp_ip else '')
        # print("=================", internal_ip)

        if data.get("os") == "Windows":
            print("++++++++++++++++++++", data.get("fqdn_ip4"), type(data.get("fqdn_ip4")))
            ip = data.get("fqdn_ip4")[-1] if data.get("fqdn_ip4") else ''

        re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
        c = re.findall(re_rule, ip)
        # print('---------------ip', ip)
        new_data = {
            "data": {
                model_code + "_HOSTNAME": data.get("fqdn"),
                # model_code + "_INSTANCE_NAME": data.get("id"),
                # model_code + "_INTERNAL_IP": ",".join(internal_ip) if internal_ip else '',
                model_code + "_INTERNAL_IP": internal_ip[0] if internal_ip else ip,
                model_code + "_PUBLIC_IP": '' if len(c) > 0 else ip,
                model_code + "_MEMORY": data.get("mem_total"),
                model_code + "_SWAP": data.get("swap_total"),
                model_code + "_CPU_MODEL": data.get("cpu_model"),
                model_code + "_CPU_NUM": data.get("num_cpus"),
                model_code + "_CPU_ARCH": data.get("cpuarch"),
                model_code + "_OS": data.get("os"),
                model_code + "_OS_TYPE": data.get("kernel"),
                model_code + "_OS_FAMILY": data.get("os_family"),
                model_code + "_OS_ARCH": data.get("osarch"),
                model_code + "_OS_RELEASE": data.get("osrelease"),
                model_code + "_SELINUX": selinux,
                model_code + "_KERNEL_RELEASE": data.get("kernelrelease"),
                model_code + "_BIOS_RELEASEDATA": data.get("biosreleasedate"),
                model_code + "_BIOS_VERSION": data.get("biosversion"),
                model_code + "_NAME_SERVER": dns,
                model_code + "_CPU_FLAGS": data.get("cpu_flags"),
                model_code + "_AGENT_VERSION": data.get("saltversion"),
                model_code + "_AGENT_PATH": data.get("saltpath"),
                model_code + "_SERIAL_NUMBER": data.get("serialnumber"),
                model_code + "_PRODUCT_NAME": data.get("productname"),
                model_code + "_VIRTUAL": data.get("virtual"),
                model_code + "_MANUFACTURER": data.get("manufacturer"),
                model_code + "_AGENT_STATE": "Agent运行中",
            },
            "pk_name": model_code + "_INTERNAL_IP",
            # "pk_value": ",".join(internal_ip) if internal_ip else '',
            "pk_value": internal_ip[0] if internal_ip else '',
            "model_code": model_code,
            "import_type": "Agent采集",
            "position": "zc"
        }
        # 如果云主机就采集实例名
        if model_code == "CLOUD_SERVER":
            new_data["data"][model_code + "_INSTANCE_ID"] = host_name
        # 如果不是云主机 需要存入唯一标识  字段名为名称
        if model_code != "CLOUD_SERVER":
            new_data["data"][model_code + "_name"] = host_name
        # 如果是Windows不采集fqdn (_HOSTNAME)
        # if data.get("os") not in "Windows":
        #     new_data["data"][model_code + "_HOSTNAME"] = data.get("fqdn")
        return new_data


class HomePageView(View):
    def get(self, request):
        token = request.COOKIES.get('bk_token')
        a = ControllerAdmin.objects.all()
        dt1 = {"item": "控制器", "count": a.count()}
        b = AgentAdmin.objects.filter(~Q(controller=None))
        n = 0
        e = 0
        linux = 0
        windows = 0
        for k in b:
            if k.agent_state == "Agent运行中":
                n += 1
            else:
                e += 1
        for kk in b:
            if kk.system_type.lower() == "linux":
                linux += 1
            else:
                windows += 1
        dt2 = {"item": "主机总数", "count": len(b), "normal": n, "error": e}
        c = HostGroup.objects.count()
        c1 = HostGroup.objects.filter(type="静态").order_by("create_time")
        c2 = HostGroup.objects.filter(type="动态").order_by("create_time")
        dt3 = {"item": "主机分组", "count": c, "static": len(c1), "dynamic": len(c2)}
        no_agent = 0
        for each in b:
            if each.agent_state != "Agent运行中":
                no_agent += 1
        dt4 = {"item": "未纳管主机", "count": no_agent}
        count_data = []
        count_data.append(dt1)
        count_data.append(dt2)
        count_data.append(dt3)
        count_data.append(dt4)
        end_data = []
        controller_data = []
        for i in a:
            controller_data.append(i.to_base_dict())
        end_data.append({"count_data": count_data})
        end_data.append({"controller_data": controller_data})
        pie = []
        pie.append({"item": "Linux", "count": linux})
        pie.append({"item": "Windows", "count": windows})
        end_data.append({"pie": pie})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetHostInstanceByCmdb(View):
    def get(self, request):
        data = request.GET
        code = data.get("code")
        token = request.COOKIES.get('bk_token')
        if not token:
            token = "vgizevQWjDKNvg7LQp23Kzv2fqDPy2SjXihH9YHYtuE"
        a = EsbApi(token)
        pass


class GetTaskRunState(View):
    def get(self, request):
        key = request.GET.get("key")
        if not key:
            return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))
        conn = get_redis_connection("default")
        value = conn.get(key)
        value = value.decode("utf-8")
        return JsonResponse(success(SuccessStatusCode.GET_RUN_STATE_SUCCESS, value))


class GetAgentNetWork(View):
    def get(self, request):
        host_name = request.GET.get("name")
        ip = request.GET.get("ip")
        agent_list = AgentAdmin.objects.filter(name=host_name)
        if agent_list:
            agent = agent_list.first()
            controller = agent.controller
            if not controller:
                return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))
            else:
                salt_obj = SaltSshBase(controller.to_dict())
                if salt_obj.salt:
                    response = salt_obj.salt.network(agent.name)
                    if response.get(agent.name):
                        end_data = self.process_network_data(response.get(agent.name))
                        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
                    return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))
                return JsonResponse(error(ErrorStatusCode.CONTROLLER_STATE_ERROR))
        else:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))

    def process_network_data(self, data):
        end_data = []
        for i in data:
            port = i.get("port")
            if not port:
                try:
                    port = i.get("local-address").split(":")[1]
                except:
                    port = ""
            address = i.get("local-address")
            if ":" in address:
                if len(i.get("local-address").split(":")) == 2:
                    address = i.get("local-address").split(":")[0]
                else:
                    address = i.get("local-address").rsplit(":", 1)[0]
                    port = i.get("local-address").rsplit(":", 1)[-1]
            else:
                address = address
            try:
                program = i.get("program").split("/")[1]
            except:
                program = i.get("program")
            dt = {
                "port": port,
                "address": address,
                "proto": i.get("proto"),
                "pid": i.get("program").split("/")[0],
                "program": program
            }
            end_data.append(dt)
        return end_data


class GetHostInfo(View):
    def post(self, request):
        # user_id = request.COOKIES.get("user_id")
        # token = request.GET.get("token_data")
        token = json.loads(request.body).get("token_data")
        system_type = json.loads(request.body).get("system_type")
        group_type = json.loads(request.body).get("group_type")
        dic = {}
        # dic["agent_state"] = "Agent运行中"

        if system_type:
            if system_type != "all":
                dic["system_type"] = system_type

        if group_type:

            if group_type == "all":
                pass
            else:
                dic["group_id"] = group_type

        bk_user = EsbApi(token).get_user_info_from_workbench()  # 获取当前登录用户的信息
        print("bk_user-GetHostInfo", bk_user)
        user_obj = UserInfo.fetch_one(username=bk_user.get("username"))
        # a = AgentAdmin.objects.filter(~Q(controller=None), control_type="Agent")
        if user_obj.role == 1:  # if type == "esb":
            # 如果用户是管理员，获取全部的节点，不需要权限分配过程
            agent_all_list = AgentAdmin.fetch_all(controller__isnull=False, **dic)
            print("agent_all_list", agent_all_list)
            # a = AgentAdmin.fetch_all(agent_user__user_id=user_id, control_type="Agent").exclude(controller=None)

        # 不是管理员的主机列表
        else:
            current_agent = UserAgentModel.fetch_all(user_id=user_obj.id).exclude(agent__controller=None)
            agent_all_list = AgentAdmin.objects.filter(id__in=[each.agent_id for each in current_agent], **dic)

        data = []
        end_data = []
        normal = 0
        not_normal = 0
        for i in agent_all_list:
            dt = i.to_dict_for_job()
            if dt.get("agent_state") == "Agent运行中":
                normal += 1
            else:
                not_normal += 1
            data.append(dt)
        end_data.append({"agent_info": data, "normal": normal, "not_normal": not_normal})
        print("end_data----", end_data)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetHostFileInfo(View):
    def get(self, request):
        host_name = request.GET.get("host_name")
        file_name = request.GET.get("file_name")
        a = AgentAdmin.objects.filter(name=host_name).first()
        if a and a.controller:
            controller = a.controller
            salt_obj = SaltSshBase(controller.to_dict())
            if salt_obj.salt:
                if file_name:
                    bb = salt_obj.salt.filestats(host_name, file_name)
                else:
                    bb = salt_obj.salt.filestats(host_name)
                if bb:
                    res = bb.get(host_name)
                    return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, res))
                return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))
            return JsonResponse(error(ErrorStatusCode.AGENT_STATE_ERROR))
        return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))


class GetAgentAndGroup(View):
    # 此api暂时不用
    def get(self, request):
        group = HostGroup.objects.all().order_by("create_time")
        end_data = []
        for i in group:
            agent_list = AgentAdmin.objects.filter(group=i).exclude(controller=None)
            data_list = []
            for j in agent_list:
                if j:
                    data_list.append(j.to_dict_for_job())
            i_dt = i.to_dict()
            i_dt["children"] = data_list
            end_data.append(i_dt)
        other_group_list_agent = [agent.to_dict() for agent in
                                  AgentAdmin.objects.filter(group=None).exclude(controller=None)]
        other_group_list_children = [agent.to_dict_for_job() for agent in
                                     AgentAdmin.objects.filter(group=None).exclude(controller=None)]
        end_data.append(
            {"id": 0, "name": "默认分组", "agent_list": [other_group_list_agent], "children": other_group_list_children})

        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetAgentPsInfo(View):
    def get(self, request):
        host_name = request.GET.get("host_name")
        a = AgentAdmin.objects.filter(name=host_name).first()
        if a and a.controller:
            controller = a.controller
            salt_obj = SaltSshBase(controller.to_dict())
            if salt_obj.salt:
                bb = salt_obj.salt.psinfo(host_name)
                if bb:
                    res = bb.get(host_name)
                    end_data = self.proccess_data(res)
                    return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
                return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))
            return JsonResponse(error(ErrorStatusCode.AGENT_STATE_ERROR))
        return JsonResponse(error(ErrorStatusCode.AGENT_NOT_HAVE_CONTROLLER))

    def proccess_data(self, s: str):
        lt = s.split("\n")
        c = lt[0].split(" ")
        key = []
        for i in c:
            if i:
                key.append(i)
        end_data = []
        for j in range(1, len(lt)):
            c = re.compile(r'\s+')
            f = c.split(lt[j], 10)
            if len(f) == len(key):
                dt = {}
                for jj in range(len(f)):
                    dt[key[jj]] = f[jj]
                end_data.append(dt)
        return end_data


class GetAllZabbixAgentView(View):
    def get(self, request):
        lt = AgentAdmin.objects.filter(~Q(zabbix_host_id=None))
        end_data = []
        for i in lt:
            end_data.append(i.to_dict())
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class NetWorkEquipmentView(View):
    def get(self, request):
        data = request.GET
        page = data.get("page")
        per_page = data.get("per_page")
        if page:
            page = int(page)
        if not page:
            page = 1
        if per_page:
            per_page = int(per_page)
        if not per_page:
            per_page = 10
        lt = NetWorkEquipment.objects.filter()
        total = lt.count()
        current_page = lt[(page - 1) * per_page: page * per_page]  # data
        end_data = []
        for i in current_page:
            if i:
                end_data.append(i.to_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": total,
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))

    def post(self, request):
        data = json.loads(request.body)
        token = request.COOKIES.get("bk_token")
        name = data.get("name")
        obj = NetWorkEquipment.objects.filter(name=name)
        if not obj:
            a = NetWorkEquipment.objects.create(**data)
            zabbix = DefaultZabbix()
            host_id = zabbix.create_net_equipment(a.name, a.name, a.ip, a.team_name)
            if host_id:
                NetWorkEquipment.objects.filter(id=a.id).update(**{"zabbix_id": host_id, "zabbix_status": "已连接"})
                a = NetWorkEquipment.objects.filter(id=a.id).first()
            data = self.process_data(a)
            esb_obj = EsbApi(token)
            esb_obj.import_inst(data)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS, a.to_dict()))
        return JsonResponse(error(ErrorStatusCode.RECORD_HAS_EXISTED))

    def put(self, request):
        data = json.loads(request.body)
        id = data.get("id")
        obj = NetWorkEquipment.objects.filter(id=id)
        if not obj:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))
        data["update_time"] = datetime.now()
        obj.update(**data)
        a = NetWorkEquipment.objects.filter(id=id).first()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, a.to_dict()))

    def delete(self, request):
        data = json.loads(request.body)
        id = data.get("id")
        obj = NetWorkEquipment.objects.filter(id=id)
        if not obj:
            return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))
        obj.delete()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS))

    def process_data(self, a):
        if a.equipment_type == "交换机":
            model_code = "SWITCH"
        elif a.equipment_type == "路由器":
            model_code = "ROUTER"
        else:
            model_code = "FIREWALL"
        dt = {
            "model_code": model_code,
            "data": {
                model_code + "_name": a.name,
                model_code + "__HOSTNAME": a.name,
                model_code + "_PUBLIC_IP": a.ip,
                model_code + "_SNMP_COMMUNITY": a.team_name
            },
            "pk_name": model_code + "_name",
            "pk_value": a.name,
            "import_type": "自动采集"
        }
        return dt


class GetControllerByHostInfo(View):
    def post(self, request):
        aaa = json.loads(request.body)
        data = aaa.get("data")
        ip = data.get("ip")
        ip_type = data.get("ip_type")
        host_name = data.get("host_name")
        if ip_type:
            ip_type = ip_type[1: -1]
            dt = {
                "name": host_name,
                "ip_type": ip_type,
                "ip": ip
            }
        else:
            dt = {
                "name": host_name,
                "ip": ip
            }
        obj = AgentAdmin.objects.filter(**dt).first()
        if obj:
            if obj.controller:
                return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, obj.controller.to_dict()))
            return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))
        return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))


class GetInfoForWorkbenchView(View):

    @user_sync
    def get(self, request):
        static = HostGroup.objects.filter(type="静态").count()
        dynamic = HostGroup.objects.filter(type="动态").count()
        group_count = [{"item": "静态分组", "count": static}, {"item": "动态分组", "count": dynamic}]
        agent_count = []
        agent = AgentAdmin.fetch_all().count()
        agent_count.append({"item": "主机数量", "count": agent})
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS,
                                    {
                                        "group": group_count, "agent_count": agent_count
                                    }))


class GetNavCollectionView(View):
    def get(self, request):
        token = request.COOKIES.get("bk_token")
        print("control_token", token)
        end_data = EsbApi(token).get_nav_and_collection()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class CollectionNavView(View):
    def post(self, request):
        token = request.COOKIES.get("bk_token")
        data = json.loads(request.body)
        nav_id = data.get("nav_id")
        end_data = EsbApi(token).collection_nav(nav_id)
        if isinstance(end_data, dict):
            successcode = end_data.pop("api_code")
            return JsonResponse({"code": 200, "successcode": successcode, "message": end_data.get("message"),
                                 "data": end_data.get("data")
                                 })
        else:
            return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN))


class GetUserMessageView(View):
    def get(self, request):
        kwargs = request.GET.dict()
        page = int(kwargs.pop("current", 1))
        per_page = int(kwargs.pop("pageSize", 10))
        token = request.COOKIES.get("bk_token")
        data = EsbApi(token).get_user_message_info(page, per_page)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data))


# class UserCanSeeAgentView(View):
#     def get(self, request):
#         id = request.GET.get("id")
#         user_id = request.COOKIES.get("user_id")
#         if not id:
#             return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE))
#         end_data = []
#         for i in lt:
#             end_data.append(i.user.to_dict())
#         return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))
#
#     def post(self, request):
#         data = json.loads(request.body)
#         user_id = request.COOKIES.get("user_id")
#         script_id = data.get("script_id")
#         return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS))


class ControlMenuStrategyCtrl(View):

    @user_sync
    def get(self, request):
        """ 获取当前平台使用者的菜单列表 """
        token = request.COOKIES.get("bk_token")
        esb_obj = EsbApi(token)
        res_data = esb_obj.get_user_menu()  # 调用ESB接口获取到当前用户的在资源平台的菜单列表

        return JsonResponse(success(SuccessStatusCode.MENU_GET_SUCCESS, res_data[0] if res_data else {}))


class GetZabbixTemplateView(View):
    def get(self, request):
        data = request.GET.dict()
        id = data.get("id")
        try:
            controller = AgentAdmin.fetch_one(id=id).controller
        except:
            controller = None
        if controller:
            try:
                zabbix_obj = ZabbixApi(controller.zabbix_username, controller.zabbix_password, controller.zabbix_url)
                end_data = zabbix_obj.get_all_template()
            except:
                end_data = []
            return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, self.proccess_end_data(end_data)))
        return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))

    def proccess_end_data(self, end_data):
        lt = []
        if not end_data:
            return []
        for i in end_data:
            lt.append({
                "temp_name": i.get("name"),
                "temp_id": i.get("templateid")
            })
        return lt


class GetUserInfoCtrl(View):

    def get(self, request):
        """
        获取当前用户信息
        """
        token = request.COOKIES.get("bk_token")

        bk_user = EsbApi(token).get_user_info()  # 获取当前用户

        username = bk_user.get("username")

        user_objects = UserInfo.fetch_one(**{"username": username})

        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, user_objects.to_dict()))


class ReadAllMessageView(View):
    def get(self, request):
        bk_token = request.COOKIES.get("bk_token")
        a = EsbApi(bk_token).read_all_message()
        print(a)
        return JsonResponse(success(SuccessStatusCode.OPERATION_SUCCESS))


class GetAllHostGroupView(View):
    def get(self, request):
        queryset = HostGroup.objects.all().order_by("create_time")
        children = []
        end_data = []
        # children.append({
        #     "id": 0,
        #     "name": "默认分组",
        #     "type": "静态",
        #     "describe": "默认分组",
        # })
        for i in queryset:
            children.append(i.to_base_dict())
        # lt = AgentAdmin.fetch_all(group=None)
        # agent_list = []
        # for i in lt:
        #     agent_list.append(i.to_dict())
        end_data.append({
            "id": "all",
            "name": "全部主机",
            "type": "静态",
            "describe": "全部主机",
            "children": children,
        })
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetHostInfoForMonitorView(View):
    def post(self, request):
        data = json.loads(request.body)
        page = data.pop("page", 1)
        pageSize = data.pop("pageSize", 10)
        filter = data.get("filter", {})
        end_data = []
        queryset, total = AgentAdmin.pagination(page, pageSize, exclude={"controller": None}, **filter)
        for k in queryset:
            end_data.append(k.to_monitor_dict())
        dt = {
            "current": page,
            "pageSize": pageSize,
            "total": total,
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class StopZabbixView(View):
    def post(self, request):
        data = json.loads(request.body)
        host_id = data.get("host_id")
        a = AgentAdmin.fetch_one(id=host_id)
        if a:
            i = a.controller
            zabbix_host_id = a.zabbix_host_id
            zabbix_obj = ZabbixApi(i.zabbix_username, i.zabbix_password, i.zabbix_url)
            if a.zabbix_agent_state == True:  # 启用变停用
                status = 1
                zabbix_agent_state = False
            else:
                status = 0
                zabbix_agent_state = True
            zabbix_obj.stop_or_start_zabbix(zabbix_host_id, status)
            new_a = a.update(**{"zabbix_agent_state": zabbix_agent_state})
            return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS, new_a.to_monitor_dict()))
        return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))


class MonitorHostCountView(View):
    def get(self, request):
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            lt = AgentAdmin.fetch_all().exclude(controller_id=None)
        else:
            lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
        is_monitor = 0
        not_monitor = 0
        for i in lt:
            if i.zabbix_agent_state:
                is_monitor += 1
            else:
                not_monitor += 1
        data = [
            {"item": "已启用", "count": is_monitor},
            {"item": "未启用", "count": not_monitor},
            # {"item": "监控主机", "count": is_monitor + not_monitor},
        ]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, data))


class HostMonitorTypeView(View):
    def get(self, request):
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            lt = AgentAdmin.fetch_all().exclude(controller_id=None)
        else:
            lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
        # lt = AgentAdmin.fetch_all().exclude(controller_id=None, agent_user__user_id=user_id)
        dt = {}
        for i in lt:
            if dt.get(i.controller):
                lt = dt.get(i.controller)
                lt.append(i)
            else:
                lt = [i]
            dt[i.controller] = lt
        count = []
        for key, value in dt.items():
            if not key:
                continue
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            host_ids = []
            for v in value:
                host_ids.append(v.zabbix_host_id)
            data = zabbix_obj.get_host_state()
            count_info = self.count_type(data, host_ids)
            count.extend(count_info)
        end_data = self.count_list(count)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))

    def count_type(self, data, host_ids):
        """
        data: 是从zabbix获取所有的主机情况
        host_ids: 是这个控制器下所有节点的zabbix_host_id
        """
        available = 0  # Agent
        jmx_available = 0  # JMX
        ipmi_available = 0  # IPMI
        snmp_available = 0  # SNMP
        for i in data:
            if i.get("hostid") in host_ids:
                if i.get("available") == "1":
                    available += 1
                elif i.get("ipmi_available") == "1":
                    ipmi_available += 1
                elif i.get("jmx_available") == "1":
                    jmx_available += 1
                elif i.get("snmp_available") == "1":
                    snmp_available += 1
                else:
                    available += 1
        return [
            {"item": "Agent", "count": available},
            {"item": "JMX", "count": jmx_available},
            {"item": "IPMI", "count": ipmi_available},
            {"item": "SNMP", "count": snmp_available}
        ]

    def count_list(self, lt):
        dt = {}
        for i in lt:
            if not dt.get(i.get("item")):
                dt[i.get("item")] = i.get("count")
            else:
                count = dt[i.get("item")]
                count += i.get("count")
                dt[i.get("item")] = count
        end_data = []
        for k, v in dt.items():
            end_data.append({"item": k, "count": v})
        return end_data


class EventTypeCountView(View):
    def get(self, request):
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        # lt = AgentAdmin.fetch_all().exclude(controller_id=None, agent_user__user_id=user_id)
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            lt = AgentAdmin.fetch_all().exclude(controller_id=None)
        else:
            lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
        dt = {}
        for i in lt:
            if dt.get(i.controller):
                lt = dt.get(i.controller)
                lt.append(i)
            else:
                lt = [i]
            dt[i.controller] = lt
        count = []  # 用于存放有报警信息但是没有处理的
        for key, value in dt.items():
            if not key:
                continue
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            c = zabbix_obj.problem_info(None)
            for iii in value:
                if iii.zabbix_host_id:
                    c = zabbix_obj.problem_info(iii.zabbix_host_id)
                    count.extend(c)
            # c = zabbix_obj.level_count(value.zabbix_host_id)
            # dict = {}
            # for i in c:
            #     if not dict.get(i.get("objectid")):
            #         dict[i.get("objectid")] = {"name": i.get("name"), "value": i.get("value"), "level": i.get("severity")}
            #     else:
            #         dict[i.get("objectid")] = {"name": i.get("name"), "value": i.get("value"), "level": i.get("severity")}
            # for k, v in dict.items():
            #     if v.get("value") == "1":
            #         count.append(v)
        # for kkk in count:
        #     print(kkk)
        end_data = self.count_list(count)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))

    def count_list(self, lt):
        """
        level值说明：
            0 - 未分类;
            1 - 信息;
            2 - 警告;
            3 - 一般严重;
            4 - 严重;
            5 - 灾难.
        """
        not_group = 0  # 未分类
        info = 0  # 信息
        warning = 0  # 警告
        average = 0  # 一般严重
        high = 0  # 严重
        disaster = 0  # 灾难
        for i in lt:
            if i.get("severity") == "0":
                not_group += 1
            elif i.get("severity") == "1":
                info += 1
            elif i.get("severity") == "2":
                warning += 1
            elif i.get("severity") == "3":
                average += 1
            elif i.get("severity") == "4":
                high += 1
            elif i.get("severity") == "5":
                disaster += 1
            else:
                not_group += 1
        return [
            {"item": "未分类", "count": not_group},
            {"item": "信息", "count": info},
            {"item": "警告", "count": warning},
            {"item": "一般严重", "count": average},
            {"item": "严重", "count": high},
            {"item": "灾难", "count": disaster}
        ]


class HostProblemInfoView(View):
    def get(self, request):
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        # lt = AgentAdmin.fetch_all().exclude(controller_id=None, agent_user__user_id=user_id)
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            lt = AgentAdmin.fetch_all().exclude(controller_id=None)
        else:
            lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
        dt = {}
        for i in lt:
            if dt.get(i.controller):
                lt = dt.get(i.controller)
                lt.append(i)
            else:
                lt = [i]
            dt[i.controller] = lt
        end_data = []
        for key, value in dt.items():
            if not key:  # 暂时屏蔽掉取不到数据的主机
                continue
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            for iii in value:
                if iii.zabbix_host_id and iii.zabbix_agent_state:
                    c = zabbix_obj.problem_info(iii.zabbix_host_id)
                    if c:
                        for iiii in c:
                            iiii["host_name"] = iii.name
                            iiii["zabbix_host_id"] = iii.zabbix_host_id
                            iiii["show_name"] = iii.show_name
                        end_data.extend(c)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class ProblemInfoView(View):
    def post(self, request):
        """
        支持筛选：
            主机名筛选
            主机组筛选
            if host_id:     # 高级搜索
            filter = {
                "group_id": group_id,
                "host_id": host_id,
                "application_id": application_id,
                "trigger_id": trigger_id
            }
            elif host_name:           # 普通模糊搜索
                filter = {
                    "host_name": host_name
                }
            else:
                filter = {}
        """
        data = json.loads(request.body)
        page = data.pop("page", 1)
        pageSize = data.pop("pageSize", 10)
        filter = data.get("filter", {})
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        user = UserInfo.fetch_one(id=user_id)
        application_id = None
        trigger_id = None
        problem = None
        level_id = None
        if filter:
            if filter.get("host_name"):
                print("aaaaaaaaa")
                host_name = filter.get("host_name")
                # lt = AgentAdmin.fetch_all(name__contains=host_name, agent_user__user_id=user_id)
                if user.role == 1:
                    lt = AgentAdmin.fetch_all(name__contains=host_name).exclude(controller_id=None)
                else:
                    lt = AgentAdmin.fetch_all(name__contains=host_name, agent_user__user_id=user_id).exclude(
                        controller_id=None)
            else:
                group_id = filter.get("group_id", None)
                host_id = filter.get("host_id", None)
                application_id = filter.get("application_id", None)
                trigger_id = filter.get("trigger_id", None)
                problem = filter.get("problem", None)
                level_id = filter.get("level_id", None)
                cache_dict = {
                    "group_id": group_id,
                    "id": host_id
                }
                search_dict = {}
                for k, v in cache_dict.items():
                    if v:
                        search_dict[k] = v
                if user.role != 1:
                    search_dict["agent_user__user_id"] = user_id
                lt = AgentAdmin.fetch_all(**search_dict).exclude(controller_id=None)
        else:
            if user.role != 1:
                lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
            else:
                lt = AgentAdmin.fetch_all().exclude(controller_id=None)
        dt = {}
        for i in lt:
            if dt.get(i.controller):
                lt = dt.get(i.controller)
                lt.append(i)
            else:
                lt = [i]
            dt[i.controller] = lt
        end_data = []
        for key, value in dt.items():
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            for iii in value:
                if iii.zabbix_host_id:
                    c = zabbix_obj.problem_info(iii.zabbix_host_id, application_id, trigger_id)
                    if c:
                        for iiii in c:
                            if problem:
                                if problem.lower() not in iiii.get("name").lower():
                                    c.remove(iiii)
                                    continue
                            if level_id:
                                if not int(level_id) <= int(iiii.get("severity")):
                                    c.remove(iiii)
                                    continue
                            iiii["host_name"] = iii.name
                            iiii["zabbix_host_id"] = iii.zabbix_host_id
                            iiii["show_name"] = iii.show_name
                        end_data.extend(c)
        total = len(end_data)
        current_page = end_data[(page - 1) * pageSize: page * pageSize]
        dt = {
            "current": page,
            "pageSize": pageSize,
            "total": total,
            "data": current_page
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class SearchHostGroupView(View):
    def get(self, request):
        data = request.GET.dict()
        if not data.get("search"):
            lt = HostGroup.objects.all().order_by("create_time")
        else:
            search = data.get("search")
            lt = HostGroup.objects.filter(name__contains=search).order_by("create_time")
        end_data = []
        for i in lt:
            end_data.append(i.to_base_dict())
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class SearchHostView(View):
    def get(self, request):
        data = request.GET.dict()
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        user = UserInfo.fetch_one(id=user_id)
        if not data.get("search") and not data.get("group_id"):
            if user.role == 1:
                lt = AgentAdmin.fetch_all().exclude(controller_id=None)
            else:
                lt = AgentAdmin.fetch_all(agent_user__user_id=user_id).exclude(controller_id=None)
        elif data.get("group_id"):
            group_id = data.get("group_id")
            if user.role == 1:
                lt = AgentAdmin.fetch_all(group_id=group_id).exclude(controller_id=None)
            else:
                lt = AgentAdmin.fetch_all(group_id=group_id, agent_user__user_id=user_id).exclude(controller_id=None)
        else:
            search = data.get("search")
            if user.role == 1:
                lt = AgentAdmin.objects.filter((Q(show_name__contains=search) | Q(name__contains=search)) & Q(
                    agent_user__user_id=user_id)).exclude(controller_id=None)
            else:
                lt = AgentAdmin.objects.filter((Q(show_name__contains=search) | Q(name__contains=search)) & Q(
                    agent_user__user_id=user_id)).exclude(controller_id=None)
        end_data = []
        for i in lt:
            end_data.append(i.base_to_dict())
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class SearchApplicationView(View):
    def get(self, request):
        data = request.GET.dict()
        host_id = data.get("host_id")
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            a = AgentAdmin.fetch_one(id=host_id)
        else:
            a = AgentAdmin.fetch_one(id=host_id, agent_user__user_id=user_id)
        end_data = []
        if a:
            key = a.controller
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            data = zabbix_obj.get_application(a.zabbix_host_id)
            if a.zabbix_agent_state and a.zabbix_host_id and data:
                for i in data:
                    i["host_id"] = host_id
                    end_data.append(i)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class SearchTriggerView(View):
    def get(self, request):
        data = request.GET.dict()
        host_id = data.get("host_id")
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        # a = AgentAdmin.fetch_one(id=host_id, agent_user__user_id=user_id)
        user = UserInfo.fetch_one(id=user_id)
        if user.role == 1:
            a = AgentAdmin.fetch_one(id=host_id)
        else:
            a = AgentAdmin.fetch_one(id=host_id, agent_user__user_id=user_id)
        end_data = []
        if a:
            key = a.controller
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            data = zabbix_obj.get_trigger(a.zabbix_host_id)
            if a.zabbix_agent_state and a.zabbix_host_id and data:
                for i in data:
                    i["host_id"] = host_id
                    end_data.append(i)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


class GetUserSshKeyView(View):
    def get(self, request):
        token = request.COOKIES.get("bk_token")
        a = EsbApi(token)
        b = a.get_user_ssh_key("")
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, b))


class SendMessageView(View):
    def post(self, request):
        token = request.COOKIES.get("bk_token")
        data = json.loads(request.body)
        name = data.get("name", None)
        ip = data.get("ip", None)
        zabbix_host_id = data.get("zabbix_host_id", None)
        message = data.get("message")
        filter = {
            "name": name,
            "ip": ip,
            "zabbix_host_id": zabbix_host_id,
        }
        end_filter = {}
        for k, v in filter.items():
            if k and v:
                end_filter[k] = v
        a = AgentAdmin.fetch_one(**end_filter)
        esb = EsbApi(token)
        parameter = "('{}', )".format(message)
        if a:
            lt = UserAgentModel.fetch_all(agent=a)
            for k in lt:
                esb.send_out_message(5, parameter, k.user.username)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_SEND_SUCCESS))
        return JsonResponse(error(ErrorStatusCode.MESSAGE_NOT_FIND))


class AddAgentToUserView(View):
    def post(self, request):
        """
        # 绑定用户
        {
            "user_id_list": [],
            "agent_id": ""
        }
        """
        data = json.loads(request.body)
        user_id_list = data.get("user_id_list")
        agent_id = data.get("agent_id")
        lt = UserAgentModel.fetch_all(agent_id=agent_id)
        old_user_list = []
        for i in lt:
            old_user_list.append(i.user.id)
        for j in user_id_list:
            if j not in old_user_list:
                UserAgentModel.create(**{"user_id": j, "agent_id": agent_id})
        for k in old_user_list:
            if k not in user_id_list:
                a = UserAgentModel.fetch_one(**{"user_id": k, "agent_id": agent_id})
                if a:
                    a.delete()
        return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS))


class GetAllUserView(View):

    @user_sync
    def get(self, request):
        data = request.GET.dict()
        search = data.get("search")
        page = int(data.pop("current", 1))
        per_page = int(data.pop("pageSize", 10))
        if search:
            filter = {
                "username__contains": search
            }
            lt, total = UserInfo.pagination(page, per_page, exclude={"role": 1}, **filter)
        else:
            lt, total = UserInfo.pagination(page, per_page, exclude={"role": 1})
        end_data = []
        for i in lt:
            end_data.append(i.to_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": len(lt),
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class GetAllAgentView(View):
    def get(self, request):
        data = request.GET.dict()
        system_type = data.get("system_type")
        search = data.get("search")
        page = int(data.pop("current", 1))
        per_page = int(data.pop("pageSize", 10))
        filter = {}
        if search:
            filter["name__contains"] = search
        if system_type == "Linux" or system_type == "Windows":
            filter["system_type"] = system_type
            lt, total = AgentAdmin.pagination(page, per_page, exclude={"controller": None}, **filter)
        else:
            lt, total = AgentAdmin.pagination(page, per_page, exclude={"controller": None}, **filter)
        end_data = []
        for i in lt:
            end_data.append(i.base_to_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": total,
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class GetUserByAgentView(View):
    def get(self, request):
        data = request.GET.dict()
        agent_id = data.get("agent_id")
        search = data.get("search")
        page = int(data.pop("current", 1))
        per_page = int(data.pop("pageSize", 10))
        filter = {
            "agent_id": agent_id
        }
        if search:
            filter["user__username__contains"] = search
        lt, total = UserAgentModel.pagination(page, per_page, exclude={"user__role": 1}, **filter)
        end_data = []
        for i in lt:
            end_data.append(i.to_user_dict())
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": len(lt),
            "data": end_data
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class AlarmRankView(View):
    def get(self, request):
        data = request.GET.dict()
        user_id = EsbApi(request.COOKIES.get("bk_token")).get_user_id()
        search_type = data.get("search_type", "")
        search_data = data.get("search_data", "")
        group_id = data.get("group_id", None)
        host_id = data.get("host_id", "")
        create_min_time = data.get("create_min_time", "")
        create_max_time = data.get("create_max_time", "")
        severity = request.GET.getlist("severity", [])
        a = UserInfo.fetch_one(id=user_id)
        filter = {
            search_type + "__contains": search_data,
            "id": host_id,
            "group_id": group_id,
        }
        end_filter = {}
        for k, v in filter.items():
            if k and v:
                end_filter[k] = v
        if a.role == 1:
            agent_list = AgentAdmin.fetch_all(**end_filter).exclude(controller_id=None)
        else:
            end_filter["agent_user__user_id"] = user_id
            agent_list = AgentAdmin.fetch_all(**end_filter).exclude(controller_id=None)
        dt = {}
        for i in agent_list:
            if dt.get(i.controller):
                lt = dt.get(i.controller)
                lt.append(i)
            else:
                lt = [i]
            dt[i.controller] = lt
        end_data = []
        count_dict = {}
        for key, value in dt.items():
            zabbix_obj = ZabbixApi(key.zabbix_username, key.zabbix_password, key.zabbix_url)
            for iii in value:
                if iii.zabbix_host_id:
                    a = zabbix_obj.get_event_top_count(iii.zabbix_host_id, create_min_time, create_max_time)
                    if severity and a:
                        end_a = []
                        for i in a:
                            if i.get("severity") in severity:
                                end_a.append(i)
                        count_dict[iii] = end_a
                    else:
                        count_dict[iii] = a
        for kk, vv in count_dict.items():
            if vv:
                cc = self.count_func(vv, "objectid")
                for i in cc:
                    i["host_name"] = kk.name
                    i["host_id"] = kk.id
                    i["show_name"] = kk.show_name
                    i["zabbix_host_id"] = kk.zabbix_host_id
                    time_local = time.localtime(int(i.get("clock")))
                    i["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                end_data.extend(cc)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))

    def count_func(self, count_list, count_field):
        lt1 = []
        end_data = []
        for i in count_list:
            lt1.append(i.get(count_field))
        lt2 = list(set(lt1))
        for j in lt2:
            cache_list = []
            count = 0
            for k in count_list:
                if k.get(count_field) == j:
                    count += 1
                    cache_list.append(k)
            cache_list[0]["count"] = count
            end_data.append(cache_list[0])
        return end_data


class ReceiveActionInfoView(View):
    def post(self, request):
        data = json.loads(request.body)
        print(data)
        return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS))


class DataForScreenView(View):
    def get(self, request):
        agent_count = AgentAdmin.fetch_all().exclude(controller=None).count()
        linux_count = AgentAdmin.fetch_all(system_type="Linux").exclude(controller=None).count()
        windows_count = AgentAdmin.fetch_all(system_type="Windows").exclude(controller=None).count()
        normal_count = AgentAdmin.fetch_all(agent_state="Agent运行中").exclude(controller=None).count()
        all_agent = AgentAdmin.objects.filter(~Q(controller=None))
        error_list = []
        for i in all_agent:
            if i.agent_state != "Agent运行中":
                error_list.append({
                    "show_name": i.show_name,
                    "ip": i.ip,
                    "system_type": i.system_type,
                    "agent_state": i.agent_state,
                })
        end_data = {
            "count": [
                {"item": "异常节点", "count": len(error_list)},
                {"item": "正常节点", "count": normal_count},
                {"item": "所有节点", "count": agent_count},
            ],
            "system_count": [
                {"item": "Linux", "count": linux_count},
                {"item": "Windows", "count": windows_count},
            ],
            "error_list": error_list
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, end_data))


# 作业平台使用，获取分组信息
class HostGroupView(View):
    def post(self, request):
        kwargs = json.loads(request.body)
        # group_list = json.loads(kwargs.get("group_list", "[]"))
        # filter = json.loads(kwargs.get("filter", "{}"))
        group_list = kwargs.get("group_list")
        filters = kwargs.get("filters", {})
        print("kwargs_kwargs", group_list, filters)
        print("group_list1", group_list)
        if not group_list:
            return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE))
        dic = filters if filters else dict()
        print("group_list1", group_list)
        # 全部分组信息
        if "all" in group_list:
            pass
        else:
            try:
                group_list = [int(id) for id in group_list]
            except:
                return JsonResponse(error(ErrorStatusCode.MUST_INPUT_MESSAGE))
            dic["id__in"] = group_list
        print("group_list2", group_list)
        print("filter", filter)

        host_group_queryset = HostGroup.objects.filter(**dic).order_by("create_time")
        host_group_list = [host_group.to_job_dict() for host_group in host_group_queryset]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, host_group_list))


class HostView(View):
    def get(self, request):
        group_id = request.GET.get("group_id")

        # 获取当前调用者用户信息
        token = request.GET.get("token_data", "")
        # token = request.COOKIES.get("bk_token")
        bk_user = EsbApi(token).get_user_info_from_workbench()
        if not bk_user:
            return JsonResponse(error(ErrorStatusCode.INVALID_TOKEN))
        user_obj = UserInfo.fetch_one(username=bk_user.get("username"))
        dic = {"group_id": group_id, "controller__isnull": False}

        # 非管理员筛选授权表
        if user_obj.role != 1:
            user_agent_queryset = UserAgentModel.fetch_all(user_id=user_obj.id).exclude(agent__controller=None)
            dic["id__in"] = [each.agent_id for each in user_agent_queryset]
        agent_admin_queryset = AgentAdmin.fetch_all(**dic)
        agent_admin_list = [agent_admin.to_dict_for_job() for agent_admin in agent_admin_queryset]
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, agent_admin_list))
