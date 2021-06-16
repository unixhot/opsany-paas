import os
import sys


class GetAgent(object):
    def get_controller(self):
        lt = ControllerAdmin.objects.all()
        return lt

    def get_all_agent_zabbix_state(self):
        lt = self.get_controller()
        for i in lt:
            agent_list = AgentAdmin.fetch_all(controller=i)
            zabbix_host_list = []
            for k in agent_list:
                if not k.zabbix_host_id:
                    k.update(**{"zabbix_agent_state": False})
                else:
                    zabbix_host_list.append(k.zabbix_host_id)
            if zabbix_host_list:
                zabbix_obj = ZabbixApi(i.zabbix_username, i.zabbix_password, i.zabbix_url)
                # zabbix_obj.



if __name__ == '__main__':
    parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ["BK_ENV"] = "production"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    sys.path.append(parent_path)
    import django
    django.setup()
    from control.models import *
    from control.utils.zabbix_api import ZabbixApi


