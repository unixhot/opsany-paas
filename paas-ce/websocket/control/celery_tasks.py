# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from celery import task
from django_redis import get_redis_connection
import time
import re
from control.utils.esb_api import *
from control.models import *
from control.utils.salt_ssh_file import *
from control.utils.zabbix_api import *
# from control.utils.saltstack_api import SaltAPI as salt_api
from datetime import datetime


@task
def install_salt_agent(master_list, host_list, token, cache_key):
    lt = []
    esb_obj = EsbApi(token)
    conn = get_redis_connection("default")
    for j in master_list:
        b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.objects.filter(controller_id=j, id__in=host_list)
        obj = SaltSshBase(b.to_dict())
        ControllerAdmin.fetch_one(id=j).update(
            **{"state1": obj.state1, "state2": obj.state2})
        if not obj.state1 and not obj.state2:
            for k in lt1:
                AgentAdmin.fetch_one(id=k.id).update(**{"agent_state": "控制器连接失败"})
                lt.append(dict(
                    name=k.name,
                    agent_state="控制器连接失败",
                    controller_name=k.controller.name,
                ))

            continue

        for k in lt1:
            current_obj = AgentAdmin.fetch_one(id=k.id)
            current_obj.update(**{"agent_state": "SSH连接中"})
            data_dict = k.to_dict('all')
            ssh_type = data_dict.get("ssh_type")
            if ssh_type == "key":
                ssh_key_id = data_dict.get("ssh_key_id")
                ssh_key_info = esb_obj.get_user_ssh_key(ssh_key_id)
                data_dict["ssh_key_info"] = ssh_key_info
            res = obj.pass_key(data_dict)  # 写入roster文件
            if res:
                current_obj.update(**{"agent_state": "SSH已连接"})
                time.sleep(0.5)
                current_obj.update(**{"agent_state": "Agent安装中"})
                obj.salt.delete_key(data_dict.get("name"))
                response = obj.install_salt(data_dict)
                tmp_flag = False
                time.sleep(12)
                minions_pre_list = obj.salt.list_all_key().get("minions_pre")
                if k.name in minions_pre_list:
                    tmp_flag = True

                if response or tmp_flag:
                    # 纳管 接受key 
                    obj.salt.accept_key(data_dict.get("name"))
                    # 采集信息
                    current_obj.update(**{"agent_state": "正在采集数据"})
                    grains = obj.salt.grains(k.name)
                    if grains.get("data") and grains.get("data").get(k.name):
                        # 整理采集到的数据
                        grains_data = proccess_grains(grains, k.host_type, k.name, k.ip)

                        esb_obj.import_cloud_server_grains(grains_data)
                        update_dt = {"agent_state": "Agent运行中"}
                        if "纳管后" in k.ip:
                            
                            update_dt["ip"] = grains_data.get("data").get(k.host_type + "_INTERNAL_IP")
                            update_dt["ip_type"] = "内"
                            if grains.get("data").get(k.name).get("os") == "Windows":
                                update_dt["system_type"] = "Windows"
                                update_dt["username"] = "Administrator"
                                update_dt['agent_state'] = "Agent运行中"
                                update_dt['ssh_port'] = '3389'
                            else:
                                update_dt["system_type"] = "Linux"
                                update_dt["username"] = "root"
                                update_dt['agent_state'] = "Agent运行中"
                                update_dt['ssh_port'] = '22'
                        current_obj.update(**update_dt)
                        dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": k.controller.name}
                        lt.append(dt)
                    else:
                        time.sleep(2)
                        grains = obj.salt.grains(k.name)
                        if not grains.get("data").get(k.name):
                            time.sleep(3)
                            grains = obj.salt.grains(k.name)
                            if not grains.get("data").get(k.name):
                                current_obj.update(**{"agent_state": "Agent安装失败"})
                                lt.append(dict(
                                    name=k.name,
                                    agent_state="Agent安装失败",
                                    controller_name=k.controller.name,
                                ))
                            else:
                                grains_data = proccess_grains(grains, k.host_type, k.name, k.ip)
                                esb_obj.import_cloud_server_grains(grains_data)
                                update_dt = {"agent_state": "Agent运行中"}
                                if "纳管后" in k.ip:
                                    
                                    update_dt["ip"] = grains_data.get("data").get(k.host_type + "_INTERNAL_IP")
                                    update_dt["ip_type"] = "内"
                                    if grains.get("data").get(k.name).get("os") == "Windows":
                                        update_dt["system_type"] = "Windows"
                                        update_dt["username"] = "Administrator"
                                        update_dt['agent_state'] = "Agent运行中"
                                        update_dt['ssh_port'] = '3389'
                                    else:
                                        update_dt["system_type"] = "Linux"
                                        update_dt["username"] = "root"
                                        update_dt['agent_state'] = "Agent运行中"
                                        update_dt['ssh_port'] = '22'
                                current_obj.update(**update_dt)
                                dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": k.controller.name}
                                lt.append(dt)
                        else:
                            
                            grains_data = proccess_grains(grains, k.host_type, k.name, k.ip)
                            esb_obj.import_cloud_server_grains(grains_data)
                            update_dt = {"agent_state": "Agent运行中"}
                            if "纳管后" in k.ip:
                                
                                update_dt["ip"] = grains_data.get("data").get(k.host_type + "_INTERNAL_IP")
                                update_dt["ip_type"] = "内"
                                if grains.get("data").get(k.name).get("os") == "Windows":
                                    update_dt["system_type"] = "Windows"
                                    update_dt["username"] = "Administrator"
                                    update_dt['agent_state'] = "Agent运行中"
                                    update_dt['ssh_port'] = '3389'
                                else:
                                    update_dt["system_type"] = "Linux"
                                    update_dt["username"] = "root"
                                    update_dt['agent_state'] = "Agent运行中"
                                    update_dt['ssh_port'] = '22'
                            current_obj.update(**update_dt)
                            dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": k.controller.name}
                            lt.append(dt)
                else:

                    current_obj.update(**{"agent_state": "Agent安装失败"})
                    lt.append(dict(name=k.name, agent_state="Agent安装失败", controller_name=k.controller.name))
            else:
                current_obj.update(**{"agent_state": "Agent安装失败"})
                
                lt.append(dict(
                    name=k.name,
                    agent_state="Agent安装失败",
                    controller_name=k.controller.name,
                ))
    if lt:     # 判断当前如有主机在更新
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


@task
def agent_paas_key(master_list, host_list, token, cache_key):
    print("进入纳管阶段", master_list, host_list)
    
    esb_obj = EsbApi(token)
    lt = []
    conn = get_redis_connection("default")

    for j in master_list:
        b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.fetch_all(controller_id=j, id__in=host_list)
        control_admin_res = b.to_dict()
        obj = SaltSshBase(control_admin_res)
        ControllerAdmin.fetch_one(id=j).update(
            **{"state1": obj.state1, "state2": obj.state2})

        if not obj.state1 and not obj.state2:
            print("当前控制器不能使用")
            for k in lt1:
                AgentAdmin.fetch_one(id=k.id).update(**{"agent_state": "控制器连接失败"})
                dt = {"name": k.name, "agent_state": "Agent纳管失败", "controller_name": k.controller.name}
                lt.append(dt)
            continue
        print("校验控制器成功")
        minions_pre_obj = obj.salt.list_all_key()
        minions_pre_list = minions_pre_obj.get("minions_pre")  # 获取所有未通过的key
        minions_list = minions_pre_obj.get("minions")  # 获取已经通过的key
        print("获得所有未通过的key", minions_pre_list)

        for k in lt1:

            current_obj = AgentAdmin.fetch_one(id=k.id)
            if (k.name not in minions_pre_list) and (k.name not in minions_list):
                current_obj.update(**{"agent_state": "Agent纳管失败"})
                dt = {"name": k.name, "agent_state": "Agent纳管失败", "controller_name": k.controller.name}
                lt.append(dt)
                continue
            response = None
            if k.name in minions_list: # 如果Agent
                response = True
            if k.name not in minions_list:
                response = obj.salt.accept_key(k.name)

            print("控制器接受key", response)
            if response:      # 通过key了
                
                current_obj.update(**{"agent_state": "正在采集数据"})
                time.sleep(3)
                grains = obj.salt.grains(k.name)

                # 判断grains信息是否采集成功
                if grains.get("data") and grains.get("data").get(k.name):
                    # 整理采集到的数据
                    print("time.sleep(3)")
                    grains_data = proccess_grains(grains, k.host_type, k.name, k.ip)

                    esb_obj.import_cloud_server_grains(grains_data)
                    update_dt = {"agent_state": "Agent运行中"}
                    if "纳管后" in k.ip:
                        update_dt["ip"] = grains_data.get("data").get(k.host_type + "_INTERNAL_IP")
                        update_dt["ip_type"] = "内"
                        if grains.get("data").get(k.name).get("os") == "Windows":
                            update_dt["system_type"] = "Windows"
                            update_dt["username"] = "Administrator"
                            update_dt['agent_state'] = "Agent运行中"
                            update_dt['ssh_port'] = '3389'
                        else:
                            update_dt["system_type"] = "Linux"
                            update_dt["username"] = "root"
                            update_dt['agent_state'] = "Agent运行中"
                            update_dt['ssh_port'] = '22'
                    current_obj.update(**update_dt)
                    
                    dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": current_obj.controller.name}
                    lt.append(dt)
                    
                else:
                    time.sleep(5.5)
                    grains = obj.salt.grains(k.name)
                    print("time.sleep(5.5)")
                    if not grains.get("data").get(k.name):
                        current_obj.update(**{"agent_state": "Agent异常"})
                        dt = {"name": k.name, "agent_state": "Agent异常", "controller_name": k.controller.name}
                        lt.append(dt)
                    else:
                        grains_data = proccess_grains(grains, k.host_type, k.name, k.ip)
                        esb_obj.import_cloud_server_grains(grains_data)
                        update_dt = {"agent_state": "Agent运行中"}
                        if "纳管后" in k.ip:
                            update_dt["ip"] = grains_data.get("data").get(k.host_type + "_INTERNAL_IP")
                            update_dt["ip_type"] = "内"
                            if grains.get("data").get(k.name).get("os") == "Windows":
                                update_dt["system_type"] = "Windows"
                                update_dt["username"] = "Administrator"
                                update_dt['agent_state'] = "Agent运行中"
                                update_dt['ssh_port'] = '3389'
                            else:
                                update_dt["system_type"] = "Linux"
                                update_dt["username"] = "root"
                                update_dt['agent_state'] = "Agent运行中"
                                update_dt['ssh_port'] = '22'
                        current_obj.update(**update_dt)
                        
                        dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": k.controller.name}
                        lt.append(dt)
                # 如果是Windows主机需要把主机导入到zabbix中
                zabbix_create_host(b, current_obj)
            else:
                current_obj.update(**{"agent_state": "Agent纳管失败"})
                dt = {"name": k.name, "agent_state": "Agent纳管失败", "controller_name": k.controller.name}
                lt.append(dt)
    if lt:
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


def zabbix_create_host(controller_master, current_host):

    if not current_host.system_type == "Windows":
        return None
    # 创建zabbix主机
    try:
        zabbix_obj = ZabbixApi(controller_master.zabbix_username, controller_master.zabbix_password, controller_master.zabbix_url)
        print("zabbix_obj", zabbix_obj)
        if zabbix_obj.session:
            group_id = zabbix_obj.get_default_group()
            print("group_id", group_id)
            zabbix_host_id = zabbix_obj.create_host(**current_host.to_zabbix_dict(group_id))
            print("zabbix_host_id", zabbix_host_id)
            current_host.update(**{"zabbix_host_id": zabbix_host_id})
    except Exception as e:
        print("同步zabbix主机失败", e)
    
    template_list=[]
    # 更改zabbix 标记 宏 模板
    print("current_host", current_host.system_type)
    if current_host.system_type == "Windows":
        template_list = [{"temp_id": 10299, "temp_name": "Template OS Windows by Zabbix agent active"}]
    
    if current_host.system_type == "Linux":
        template_list = [{"temp_id": 10284, "temp_name": "Template OS Linux by Zabbix agent active"}]
    zabbix_host_id = current_host.zabbix_host_id

    # 标记更新
    zabbix_sign_list = []

    # 宏更新
    zabbix_variable_list = []
    
    # 模板更新
    zabbix_temp_list = []
    agent_temp = AgentTemplate.fetch_all(agent=current_host)
    for i in agent_temp:
        i.delete()
    for ii in template_list:
        ii.pop("id", None)
        ii["agent_id"] = current_host.id
        AgentTemplate.create(**ii)
        zabbix_temp_list.append({
            "templateid": str(ii.get("temp_id"))
        })
    
    try:
        zabbix_obj = ZabbixApi(controller_master.zabbix_username, controller_master.zabbix_password, controller_master.zabbix_url)
        zabbix_obj.update_host(zabbix_host_id, zabbix_sign_list, zabbix_temp_list, zabbix_variable_list)
    except Exception as e:
        print("update_host", e)
    


def proccess_grains(grains_data, model_code, host_name, ip=None):
    """ new_data 增加 model_code + "_HOSTNAME"""
    all_data = grains_data.get("data")
    data = all_data.get(host_name)
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
        reg_netcard = re.compile(r'^(eth|ens|enp|bond|Tencent VirtIO Ethernet Adapter)[\d]+', re.M)
        netcard = reg_netcard.search(each)
        if netcard:
            tmp_ip = data.get("ip4_interfaces").get(netcard.group())
            internal_ip.append(tmp_ip[0] if tmp_ip else '')

    # 如果是Windows 采集 ip 使用fqdn_ip4
    if data.get("os") == "Windows":
        print("fqdn_ip4", data.get("fqdn_ip4"), type(data.get("fqdn_ip4")))
        ip = data.get("fqdn_ip4")[-1] if data.get("fqdn_ip4") else ''

    re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
    c = re.findall(re_rule, ip)

    new_data = {
        "data": {
            model_code + "_HOSTNAME": data.get("fqdn"),
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
        "pk_name": model_code + "_name",
        "pk_value": host_name,
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
    return new_data


@task
def restart_agent(master_list, host_list, token, cache_key):
    esb_obj = EsbApi(token)
    lt = []
    conn = get_redis_connection("default")
    for j in master_list:
        # b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.fetch_all(controller_id=j, id__in=host_list)
        obj = SaltSshBase(ControllerAdmin.fetch_one(id=j).to_dict())
        ControllerAdmin.fetch_one(id=j).update(
            **{"state1": obj.state1, "state2": obj.state2})

        for k in lt1:
            data_dict = k.to_dict('all')
            ssh_type = data_dict.get("ssh_type")
            ssh_key_id = data_dict.get("ssh_key_id")
            if ssh_type == "key" and ssh_key_id:
                ssh_key_info = esb_obj.get_user_ssh_key(ssh_key_id)
                data_dict["ssh_key_info"] = ssh_key_info
            response = obj.restart_salt(data_dict)

            if response:
                dt = {"name": k.name, "agent_state": "Agent运行中", "controller_name": k.controller.name}
                AgentAdmin.fetch_one(id=k.id).update(
                    **{"agent_state": "Agent运行中"})
                lt.append(dt)
            else:
                dt = {"name": k.name, "agent_state": "Agent重启失败", "controller_name": k.controller.name}
                AgentAdmin.fetch_one(id=k.id).update(
                    **{"agent_state": "Agent重启失败"})
                lt.append(dt)
    if lt:
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


@task
def uninstall_agent(master_list, host_list, token, cache_key):
    esb_obj = EsbApi(token)
    lt = []
    conn = get_redis_connection("default")
    for j in master_list:
        b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.fetch_all(controller_id=j, id__in=host_list)
        obj = SaltSshBase(b.to_dict())
        ControllerAdmin.fetch_one(id=j).update(
            **{"state1": obj.state1, "state2": obj.state2 })
        for k in lt1:

            data_dict = k.to_dict('all')
            ssh_type = data_dict.get("ssh_type")
            ssh_key_id = data_dict.get("ssh_key_id")
            if ssh_type == "key" and ssh_key_id:
                ssh_key_info = esb_obj.get_user_ssh_key(ssh_key_id)
                data_dict["ssh_key_info"] = ssh_key_info
            response = obj.uninstall_salt(data_dict)
            if response:
                obj.salt.delete_key(k.name)
                dt = {"name": k.name, "agent_state": "Agent未安装", "controller_name": k.controller.name}
                AgentAdmin.fetch_one(id=k.id).update(
                    **{"agent_state": "Agent未安装"})
                lt.append(dt)

                obj.delete_ssh_key(data_dict)
            else:
                dt = {"name": k.name, "agent_state": "Agent卸载失败", "controller_name": k.controller.name}
                AgentAdmin.fetch_one(id=k.id).update(
                    **{"agent_state": "Agent卸载失败"})
                lt.append(dt)
    
    if lt:
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


@task
def stop_agent(master_list, host_list, token, cache_key):
    esb_obj = EsbApi(token)
    lt = []
    conn = get_redis_connection("default")
    for j in master_list:
        b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.fetch_all(controller_id=j, id__in=host_list)
        obj = SaltSshBase(b.to_dict())
        ControllerAdmin.fetch_one(id=j).update(
            **{"state1": obj.state1, "state2": obj.state2})
        for k in lt1:
            try:
                data_dict = k.to_dict('all')
                ssh_type = data_dict.get("ssh_type")
                ssh_key_id = data_dict.get("ssh_key_id")
                if ssh_type == "key" and ssh_key_id:
                    ssh_key_info = esb_obj.get_user_ssh_key(ssh_key_id)
                    data_dict["ssh_key_info"] = ssh_key_info
                response = obj.stop_salt(data_dict)
                if response:
                    dt = {"name": k.name, "agent_state": "Agent未启用", "controller_name": k.controller.name}
                    AgentAdmin.fetch_one(id=k.id).update(
                        **{"agent_state": "Agent未启用"})
                    lt.append(dt)
                else:
                    dt = {"name": k.name, "agent_state": "Agent停用失败", "controller_name": k.controller.name}
                    AgentAdmin.fetch_one(id=k.id).update(
                        **{"agent_state": "Agent停用失败"})
            except:
                dt = {"name": k.name, "agent_state": "Agent停用失败", "controller_name": k.controller.name}
                AgentAdmin.fetch_one(id=k.id).update(
                    **{"agent_state": "Agent停用失败"})
            lt.append(dt)
    if lt:
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


@task
def delete_agent(master_list, host_list, token, cache_key):
    esb_obj = EsbApi(token)
    for k in host_list:
        AgentAdmin.objects.filter(id=k).update(**{"agent_state": "开始执行删除操作"})
    
    lt = []
    conn = get_redis_connection("default")
    for j in master_list:
        b = ControllerAdmin.fetch_one(id=j)
        lt1 = AgentAdmin.fetch_all(controller_id=j, id__in=host_list)
        if not b:  # 如果控制器被删除 直接删除节点
            for each_agent in lt1:
                lt.append(dict(
                    name=each_agent.name,
                    agent_state="Agent已删除",
                    controller_name=each_agent.controller.name,
                ))
            lt1.delete()
            continue
        
        # 删除zabbix_agent host
        try:
            zabbix_obj = ZabbixApi(b.zabbix_username, b.zabbix_password, b.zabbix_url)
            zabbix_host_list = []
            for jjjj in lt1:
                if jjjj.zabbix_host_id:
                    zabbix_host_list.append(jjjj.zabbix_host_id)
            zabbix_obj.delete_host(zabbix_host_list)
        except Exception as e:
            print(e)

        obj = SaltSshBase(b.to_dict())
        if obj.salt:
            ControllerAdmin.fetch_one(id=j).update(
                **{"state1": obj.state1, "state2": obj.state2})
            for i in lt1:
                data_dict = i.to_dict('all')
                if i.control_type == "Agent":
                    ssh_type = data_dict.get("ssh_type")
                    ssh_key_id = data_dict.get("ssh_key_id")
                    if ssh_type == "key" and ssh_key_id:
                        ssh_key_info = esb_obj.get_user_ssh_key(ssh_key_id)
                        data_dict["ssh_key_info"] = ssh_key_info

                    AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在停止Agent服务"})

                    try:
                        if not (i.system_type == "Windows" or i.system_type == "纳管后可获取"):
                            obj.delete_salt(data_dict)
                        time.sleep(2)
                        AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在删除公钥"})
                        obj.salt.delete_key(i.name)          # 删除AgentKey
                        obj.delete_ssh_key(data_dict)          # 删除roster文件内容
                        AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在删除该节点"})
                        time.sleep(1)
                        obj.salt.delete_key(i.name)
                        lt.append(dict(
                            name=i.name,
                            agent_state="Agent已删除",
                            controller_name=i.controller.name,
                        ))
                        i.delete()
                        
                    except:
                        AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在删除该节点"})
                        time.sleep(1)
                        lt.append(dict(
                            name=i.name,
                            agent_state="Agent已删除",
                            controller_name=i.controller.name,
                        ))
                        i.delete()
        else:
            ControllerAdmin.fetch_one(id=j).update(
                **{"state1": obj.state1, "state2": obj.state2})
            for i in lt1:
                data_dict = i.to_dict('all')
                if i.control_type == "Agent":
                    try:
                        c = obj.delete_ssh_key(data_dict)          # 删除roster文件内容
                        if c:
                            AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在删除该节点"})
                            time.sleep(1)
                            lt.append(dict(
                                name=i.name,
                                agent_state="Agent已删除",
                                controller_name=i.controller.name,
                            ))
                            i.delete()
                    except:
                        AgentAdmin.fetch_one(id=i.id).update(**{"agent_state": "正在删除该节点"})
                        time.sleep(1)
                        lt.append(dict(
                            name=i.name,
                            agent_state="Agent已删除",
                            controller_name=i.controller.name,
                        ))
                        i.delete()
        time.sleep(1)
        count = AgentAdmin.fetch_all(controller_id=j).count()
        ControllerAdmin.fetch_one(id=j).update(
            **{"count": count})
    
    if lt:
        esb_obj.update_agent_state(lt)
    conn.set(cache_key, "true")
    return "success"


@task
def ssh_link(master, data, token, cache_key):
    data["agent_state"] = "SSH连接中"
    conn = get_redis_connection("default")
    master_id = master.id
    id = data.get("id")
    salt_obj = SaltSshBase(master.to_dict())
    if salt_obj.salt:
        response = salt_obj.pass_key(data)
        if response:
            data["agent_state"] = "SSH已连接"
        else:
            data["agent_state"] = "SSH连接失败"
    else:
        data["agent_state"] = "SSH连接失败"
    data["controller_id"] = master_id
    if data.get("controller_name"):
        del data["controller_name"]
    AgentAdmin.fetch_one(id=id).update(**data)
    ControllerAdmin.fetch_one(id=master_id).update(**{"state1": salt_obj.state1, "state2": salt_obj.state2})
    conn.set(cache_key, "true")
    return "success"


@task
def run_task():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
        __file__)))
    path = os.path.join(os.path.join(os.path.join(BASE_DIR, "control"), "utils"), "auto_colleciton.py")
    path_2 = os.path.join(os.path.join(os.path.join(BASE_DIR, "control"), "utils"), "auto_colleciton.pyc")
    path_3 = os.path.join(os.path.join(os.path.join(BASE_DIR, "control"), "utils"), "scheduled_update_status.py")
    path_4 = os.path.join(os.path.join(os.path.join(BASE_DIR, "control"), "utils"), "scheduled_update_status.pyc")
    if os.path.isfile(path):
        command = "python {}".format(path)
    else:
        command = "python {}".format(path_2)
    if os.path.isfile(path_3):
        command1 = "python {}".format(path_3)
    else:
        command1 = "python {}".format(path_4)
    os.system(command)
    os.system(command1)
