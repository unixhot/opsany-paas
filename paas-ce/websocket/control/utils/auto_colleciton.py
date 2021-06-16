import os
import sys
from threading import Thread
import re


class GetAgent(Thread):
    """
    Windows 服务器自动采集脚本

    V2版本新增：
        zabbix自动发现


    """
    def get_controller(self):
        lt = ControllerAdmin.objects.all()
        return lt

    def get_agent(self, lt):

        group_obj = HostGroup.objects.filter(name="默认分组").first()
        for i in lt:
            salt_obj = SaltSshBase(i.to_dict())
            data = salt_obj.salt.list_all_key()
            list_all_key = data.get("minions", [])
            not_pass_key = data.get("minions_pre", [])

            if list_all_key:
                try:
                    list_all_key.remove("master-local")
                except:
                    pass
            for j in list_all_key:
                obj = AgentAdmin.objects.filter(name=j)
                if obj:
                    continue
                grains = salt_obj.salt.grains(j)
                dt = {}
                if grains.get("data", {}).get(j):
                    grains_data = grains.get("data").get(j)
                    os = grains_data.get("os")

                    dt = {
                        "ip_type": "内",
                        "name": j,
                        "username": "Administrator" if grains_data.get("os_family") == "Windows" else "root",
                        "ssh_port": "3389" if grains_data.get("os_family") == "Windows" else "22",
                        "system_type": grains_data.get("os_family"),
                        "system_name": os,
                        "control_type": "Agent",
                        "controller": i,
                        "platform": "control",
                        "agent_state": "Agent运行中",
                        "add_type": "自动发现",
                        "show_name": j,
                        "group_id": group_obj.id,
                    }
                    
                    first_get_ip = grains_data.get("fqdn_ip4")[0] # 获取当前节点IP
                    if first_get_ip:
                        dt.update(ip=first_get_ip)
                    if not first_get_ip:
                        re_internal_ip_tmp_list = grains_data.get("ip4_interfaces").keys()
                        internal_ip = list()
                        for each in re_internal_ip_tmp_list:
                            reg_netcard = re.compile(r'^(eth|ens|enp|bond|Tencent VirtIO Ethernet Adapter)[\d]+', re.M)
                            netcard = reg_netcard.search(each)
                            if netcard:
                                tmp_ip = grains_data.get("ip4_interfaces").get(netcard.group())
                                internal_ip.append(tmp_ip[0] if tmp_ip else '')
                        dt.update(ip=internal_ip[0] if internal_ip else '') 
                    AgentAdmin.objects.create(**dt)

            # 未通过的key需要怎么做
            for jj in not_pass_key:
                not_pass_key_agent = AgentAdmin.objects.filter(name=jj)

                if not not_pass_key_agent:
                    dt = {
                        "ip": "纳管后可获取",
                        "name": jj,
                        "control_type": "Agent",
                        "controller": i,
                        "platform": "control",
                        "agent_state": "Agent已安装",
                        "add_type": "自动发现",
                        "show_name": jj,
                        'system_type': '纳管后可获取',
                        "group_id": group_obj.id,
                    }
                    AgentAdmin.objects.create(**dt)
                    continue
                
                if not_pass_key_agent:
                    not_pass_key_agent.update(agent_state="Agent已安装")
                    continue

                if jj in list_all_key:  # 判断之前主机信息对否是导入状态
                    not_pass_key_agent.update(agent_state="Agent已安装")
                    
            try:
                # 判定如果key在拒绝中 删除此key
                minions_rejected_key = data.get("minions_rejected")
                minions_denied_key = data.get("minions_denied")
                need_to_del_key = list(set(minions_rejected_key + minions_denied_key))
                for each_rejected_key in need_to_del_key:
                    salt_obj.salt.delete_key(each_rejected_key)
            except Exception as e:
                print(e)

            

                    

    def update_zabbix_status(self, lt):
        for i in lt:
            zabbix_obj = ZabbixApi(i.zabbix_username, i.zabbix_password, i.zabbix_url)
            agent_lt = AgentAdmin.fetch_all(controller=i)
            for k in agent_lt:
                if k.zabbix_host_id:
                    end_data = zabbix_obj.zabbix_agent_status(k.zabbix_host_id)
                    if not end_data:
                        k.update(**{"zabbix_agent_state": False})
                    elif end_data and end_data[0].get("status") != "0":
                        k.update(**{"zabbix_agent_state": False})
                    else:
                        k.update(**{"zabbix_agent_state": True})
                else:
                    k.update(**{"zabbix_agent_state": False})

    def run(self):
        self.get_agent(self.get_controller())
        try:
            self.update_zabbix_status(self.get_controller())
        except:
            pass


if __name__ == '__main__':
    # parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # print(os.getenv("BK_ENV"))
    # os.environ["BK_ENV"] = os.getenv("BK_ENV")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import datetime
    # import argparse
    print(" [Success] {} init_script Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))

    # parser = argparse.ArgumentParser(usage='确定变量填写正确', description='Set auto collection params, type is string.')
    # parser.add_argument('-E', '--env', help='testing  or production or development')
    # parser.print_help()
    # _params = parser.parse_args()
    # os.environ["BK_ENV"] = _params.env

    # if os.getenv("BK_ENV"):
    os.environ["BK_ENV"] = os.getenv("BK_ENV")
    # os.environ.setdefault("BK_ENV", "production")     # 生产环境解注改行
    # os.environ.setdefault("BK_ENV", "testing")        # 开发环境解注改行

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import django
    django.setup()
    from control.models import *
    from control.utils.salt_ssh_file import SaltSshBase
    GetAgent().start()
    print(" [Success] {} init_script Execution Complete".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
