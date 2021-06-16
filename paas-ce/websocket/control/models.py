# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from django.db import models

from control.utils.base_model import BaseModel
from control.utils.zabbix_api import ZabbixApi

# Create your models here.


# 用户表
class UserInfo(BaseModel):
    phone = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    email = models.CharField(max_length=255)
    ch_name = models.CharField(max_length=20)
    role = models.IntegerField()
    icon_url = models.CharField(max_length=255, default="/static/user_icon/edfb99ee-08d6-41b8-ac5f-117fb86b0912.png")

    class Meta:
        db_table = "user_info"

    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "username": self.username,
            "email": self.email,
            "ch_name": self.ch_name,
            "role": self.role,
            "icon_url": self.icon_url
        }


class ControllerAdmin(BaseModel):
    name = models.CharField(unique=True, max_length=16)
    type = models.CharField(max_length=10)
    api1 = models.CharField(max_length=50)
    api2 = models.CharField(max_length=50)
    username1 = models.CharField(max_length=20)
    username2 = models.CharField(max_length=20)
    password1 = models.CharField(max_length=20)
    password2 = models.CharField(max_length=20)
    port1 = models.CharField(max_length=20, default="")
    port2 = models.CharField(max_length=20, default="")
    state1 = models.BooleanField(default=True)
    state2 = models.BooleanField(default=True)
    zabbix_url = models.CharField(max_length=255, null=True)
    zabbix_username = models.CharField(max_length=50, null=True)
    zabbix_password = models.CharField(max_length=30, null=True)
    zabbix_state = models.BooleanField(default=True)
    count = models.IntegerField(default=0)

    class Meta:
        db_table = 'controller_admin'

    def to_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["type"] = self.type
        dt["api1"] = self.api1
        dt["api2"] = self.api2
        dt["username1"] = self.username1
        dt["username2"] = self.username2
        dt["password1"] = self.password1
        dt["password2"] = self.password2
        dt["port1"] = self.port1
        dt["port2"] = self.port2
        dt["state1"] = self.state1
        dt["state2"] = self.state2
        dt["zabbix_username"] = self.zabbix_username
        dt["zabbix_password"] = self.zabbix_password
        dt["zabbix_url"] = self.zabbix_url
        dt["zabbix_state"] = self.zabbix_state
        dt["count"] = self.count
        return dt

    def to_safe_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["type"] = self.type
        dt["api1"] = self.api1
        dt["api2"] = self.api2
        dt["username1"] = self.username1
        dt["username2"] = self.username2
        dt["port1"] = self.port1
        dt["port2"] = self.port2
        dt["state1"] = self.state1
        dt["state2"] = self.state2
        dt["zabbix_username"] = self.zabbix_username
        dt["zabbix_state"] = self.zabbix_state
        dt["zabbix_url"] = self.zabbix_url
        dt["count"] = self.count
        return dt

    def to_base_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["state1"] = self.state1
        dt["state2"] = self.state2
        dt["count"] = self.count
        return dt


class HostGroup(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    name = models.CharField(unique=True, max_length=255)
    type = models.CharField(max_length=10)
    describe = models.CharField(max_length=255)

    class Meta:
        db_table = 'host_group'

    def to_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["type"] = self.type
        dt["describe"] = self.describe
        agent_list = []
        if self.group_agent:
            for i in self.group_agent.all():
                agent_list.append(i.to_dict())
        dt["agent_list"] = agent_list
        return dt

    def to_base_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["type"] = self.type
        dt["describe"] = self.describe
        return dt

    def to_job_dict(self):
        dt = dict()
        dt["id"] = self.id
        dt["name"] = self.name
        dt["type"] = self.type
        dt["describe"] = self.describe
        host_count = 0
        if self.group_agent:
            host_count = self.group_agent.all().count()
        dt["host_count"] = host_count


        return dt


class UserHostGroupModel(BaseModel):
    user = models.ForeignKey(UserInfo, to_field="id", on_delete=models.CASCADE, related_name="user_group")
    group = models.ForeignKey(HostGroup, to_field="id", on_delete=models.CASCADE, related_name="group_user")

    class Meta:
        db_table = "user_host_group"


class AgentAdmin(BaseModel):
    ip = models.CharField(max_length=50)
    ip_type = models.CharField(max_length=50, null=True)
    show_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=255, default="root")
    system_type = models.CharField(max_length=20, default="Linux")
    system_name = models.CharField(max_length=30, null=True)
    ssh_port = models.CharField(max_length=255, null=True)
    control_type = models.CharField(max_length=20)
    agent_state = models.CharField(max_length=20, default="", null=True)
    password = models.CharField(max_length=30, default="", null=True)
    key_url = models.CharField(max_length=125, default="", null=True)
    group = models.ForeignKey(HostGroup, to_field='id', related_name="group_agent", on_delete=models.SET_NULL, null=True)
    controller = models.ForeignKey(ControllerAdmin, to_field='id', on_delete=models.SET_NULL, null=True)
    platform = models.CharField(max_length=30, default="control", null=True)
    host_type = models.CharField(max_length=30, default="SERVER", null=True)
    zabbix_agent_state = models.BooleanField(default=True)
    zabbix_host_id = models.CharField(max_length=20, null=True)
    add_type = models.CharField(max_length=20, default="")
    ssh_key_id = models.CharField(max_length=20, default="")
    ssh_type = models.CharField(max_length=20, default="password")

    class Meta:
        db_table = 'agent_admin'
        unique_together = ['ip', 'name']

    def base_to_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["ip"] = self.ip
        dt["name"] = self.name
        dt["show_name"] = self.show_name
        dt["group_id"] = self.group_id
        dt["ssh_key_id"] = self.ssh_key_id
        dt["ssh_type"] = self.ssh_type
        dt["agent_state"] = self.agent_state
        dt["system_type"] = self.system_type
        return dt

    def to_dict(self, type=None):
        dt = {}
        dt["id"] = self.id
        dt["ip"] = self.ip
        dt["name"] = self.name
        dt["show_name"] = self.show_name
        dt["username"] = self.username
        dt["system_type"] = self.system_type
        dt["ssh_port"] = self.ssh_port
        dt["control_type"] = self.control_type
        dt["agent_state"] = self.agent_state
        dt["key_url"] = self.key_url
        dt["update_time"] = str(self.update_time).rsplit(".", 1)[0]
        dt["platform"] = self.platform
        try:
            dt["controller_name"] = self.controller.name
        except:
            # 没有控制器
            pass
        if type:
            dt["password"] = self.password
        dt["controller_id"] = self.controller_id
        dt["zabbix_agent_state"] = self.zabbix_agent_state
        dt["zabbix_host_id"] = self.zabbix_host_id
        dt["add_type"] = self.add_type
        dt["ssh_type"] = self.ssh_type
        dt["ssh_key_id"] = self.ssh_key_id
        if self.group:
            dt["group"] = self.group.to_base_dict()
        else:
            dt["group"] = "默认分组"
        return dt

    def to_dict_for_cmdb(self):
        dt = {}
        dt["id"] = self.id
        dt["ip"] = self.ip
        dt["name"] = self.name
        dt["system_type"] = self.system_type
        dt["system_name"] = self.system_name
        dt["agent_state"] = self.agent_state
        dt["host_type"] = self.host_type
        return dt

    def to_dict_for_job(self):
        dt = {}
        dt["ip"] = self.ip
        dt["host_name"] = self.name
        dt["show_name"] = self.show_name
        dt["system_type"] = self.system_type
        dt["system_name"] = self.system_name
        dt["agent_state"] = self.agent_state
        if self.group:
            dt["group"] = self.group.name
        else:
            dt["group"] = "默认分组"
        if self.ip_type:
            dt["ip_type"] = "(" + str(self.ip_type) + ")"
        else:
            dt["ip_type"] = "(不明)"
        try:
            dt["controller_name"] = self.controller.name
        except:
            # 没有控制器
            pass
        try:
            dt["controller_id"] = self.controller.id
        except:
            # 没有控制器
            pass
        return dt

    def to_zabbix_dict(self, group_id=None):
        if group_id:
            return {
                "host_name": self.name,
                "name": self.show_name,
                "ip": self.ip,
                "description": "Opsany",
                "group_id": group_id
            }
        return {
            "host_name": self.name,
            "name": self.show_name,
            "ip": self.ip,
            "description": "Opsany"
        }

    def to_all_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["ip"] = self.ip
        dt["name"] = self.name
        dt["show_name"] = self.show_name
        dt["username"] = self.username
        dt["system_type"] = self.system_type
        dt["ssh_port"] = self.ssh_port
        dt["control_type"] = self.control_type
        dt["agent_state"] = self.agent_state
        dt["key_url"] = self.key_url
        dt["update_time"] = self.update_time
        dt["platform"] = self.platform
        dt["ssh_type"] = self.ssh_type
        dt["ssh_key_id"] = self.ssh_key_id
        try:
            dt["controller_name"] = self.controller.name
        except:
            # 没有控制器
            pass
        dt["controller_id"] = self.controller_id
        dt["zabbix_agent_state"] = self.zabbix_agent_state
        dt["zabbix_host_id"] = self.zabbix_host_id
        dt["add_type"] = self.add_type
        lt1 = []
        if self.agent_sign.get_queryset():
            for i in self.agent_sign.get_queryset():
                lt1.append(i.to_base_dict())
        dt["agent_sign"] = lt1
        lt2 = []
        if self.agent_temp.get_queryset():

            for i in self.agent_temp.get_queryset():
                lt2.append(i.to_base_dict())
        dt["agent_temp"] = lt2
        lt3 = []
        if self.agent_variable.get_queryset():
            for i in self.agent_variable.get_queryset():
                lt3.append(i.to_base_dict())
        dt["agent_variable"] = lt3

        if self.group:
            dt["group"] = self.group.to_base_dict()
        else:
            dt["group"] = "默认分组"
        return dt

    def to_monitor_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["ip"] = self.ip
        dt["name"] = self.name
        dt["show_name"] = self.show_name
        trigger_count = 0
        item_count = 0
        if self.zabbix_host_id and self.controller:
            dt["zabbix_host_id"] = self.zabbix_host_id
            zabbix_obj = ZabbixApi(self.controller.zabbix_username, self.controller.zabbix_password, self.controller.zabbix_url)
            trigger_count = zabbix_obj.get_trigger_count(self.zabbix_host_id)
            item_count = zabbix_obj.get_host_item_count(self.zabbix_host_id)
        dt["item_count"] = item_count
        dt["trigger_count"] = trigger_count
        agent_temp, agent_variable, agent_sign = list(), list(), list()
        if self.agent_temp.get_queryset():
            a = self.agent_temp.get_queryset()
            for i in a:
                agent_temp.append({"temp_id":i.temp_id, "temp_name":i.temp_name})
            dt["agent_temp"] = agent_temp
        else:
            dt["agent_temp"] = agent_temp

        if self.agent_variable.get_queryset():
            for i in self.agent_variable.get_queryset():
                agent_variable.append(i.to_base_dict())
        dt["agent_variable"] = agent_variable

        if self.agent_sign.get_queryset():
            for i in self.agent_sign.get_queryset():
                agent_sign.append(i.to_base_dict())
        dt["agent_sign"] = agent_sign

        dt["zabbix_agent_state"] = self.zabbix_agent_state
        if self.group:
            dt["group"] = self.group.name
        else:
            dt["group"] = "默认分组"
        return dt


class AgentSignModel(BaseModel):
    agent = models.ForeignKey(AgentAdmin, to_field="id", on_delete=models.CASCADE, related_name="agent_sign") #
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta:
        db_table = 'agent_sign_model'

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "key": self.key,
            "value": self.value
        }

    def to_base_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value
        }


class AgentVariableModel(BaseModel):
    agent = models.ForeignKey(AgentAdmin, to_field="id", on_delete=models.CASCADE, related_name="agent_variable")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    describe = models.CharField(max_length=255)

    class Meta:
        db_table = 'agent_variable_model'

    def to_base_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "describe": self.describe
        }


class AgentTemplate(BaseModel):
    agent = models.ForeignKey(AgentAdmin, to_field="id", on_delete=models.CASCADE, related_name="agent_temp")
    temp_id = models.CharField(max_length=100, default="")
    temp_name = models.CharField(max_length=100, default="")

    class Meta:
        db_table = 'agent_template'

    def to_base_dict(self):
        return {
            "temp_id": self.temp_id,
            "temp_name": self.temp_name
        }


# class UserCanSeeAgentModel(BaseModel):
#     user = models.ForeignKey(UserInfo, to_field="id", on_delete=models.CASCADE)
#     task = models.ForeignKey(AgentAdmin, to_field="id", on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = "user_can_see_agent"


class NetWorkEquipment(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, null=True)
    ip = models.CharField(max_length=50, null=True)
    equipment_type = models.CharField(max_length=50, default="SWITCH")
    team_name = models.CharField(max_length=50, null=True)
    user = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    describe = models.CharField(max_length=50, null=True)
    zabbix_id = models.CharField(max_length=50, null=True)
    zabbix_status = models.CharField(max_length=50, default="未连接")

    class Meta:
        db_table = 'net_equipment'

    def to_dict(self):
        dt = {}
        dt["id"] = self.id
        dt["name"] = self.name
        dt["ip"] = self.ip
        dt["equipment_type"] = self.equipment_type
        dt["team_name"] = self.team_name
        dt["user"] = self.user
        dt["password"] = self.password
        dt["describe"] = self.describe
        dt["zabbix_id"] = self.zabbix_id
        dt["zabbix_status"] = self.zabbix_status
        return dt


class UserAgentModel(BaseModel):
    user = models.ForeignKey(UserInfo, to_field="id", on_delete=models.CASCADE, related_name="user_agent")
    agent = models.ForeignKey(AgentAdmin, to_field="id", on_delete=models.CASCADE, related_name="agent_user")

    class Meta:
        db_table = 'user_agent'

    def to_user_dict(self):
        return self.user.to_dict()

    def to_agent_dict(self):
        return self.agent.to_dict()

    def to_all_dict(self):
        return self.agent.to_all_dict()

    def base_to_dict(self):
        return self.agent.base_to_dict()

    def to_dict_for_job(self):
        return self.agent.to_dict_for_job()
