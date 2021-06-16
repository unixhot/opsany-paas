import os
import sys
import yaml


def run():
    command = 'salt-run manage.status'

    all_control = ControllerAdmin.fetch_all()

    for i in all_control:
        salt_obj = SaltSshBase(i.to_dict())
        data = salt_obj.salt.shell_remote_execution("master-local", command)
        yaml_str = data.get("master-local")
        yaml_state = yaml.safe_load(yaml_str)
        down_hosts = yaml_state.get("down", [])
        up_hosts = yaml_state.get("up", [])
        if up_hosts:
            for each_up in up_hosts:

                if not AgentAdmin.objects.filter(name=each_up).exists():
                    continue

                AgentAdmin.objects.filter(name=each_up).update(agent_state="Agent运行中")
        if down_hosts:
            for each_down in down_hosts:

                if not AgentAdmin.objects.filter(name=each_down).exists():
                    continue

                AgentAdmin.objects.filter(name=each_down).update(agent_state="Agent异常")


    # minion_status_data = os.popen("salt-run manage.status")
    #
    # yaml_state = yaml.safe_load(minion_status_data)
    #
    # down_hosts = yaml_state.get("down", [])
    # up_hosts = yaml_state.get("up", [])
    #
    # for each_up in up_hosts:
    #
    #     if not AgentAdmin.objects.filter(name=each_up).exists():
    #         continue
    #
    #     AgentAdmin.objects.filter(name=each_up).update(agent_state="Agent运行中")
    #
    # for each_down in down_hosts:
    #
    #     if not AgentAdmin.objects.filter(name=each_down).exists():
    #         continue
    #
    #     AgentAdmin.objects.filter(name=each_down).update(agent_state="Agent异常")


if __name__ == '__main__':
    # parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # print(os.getenv("BK_ENV"))
    # os.environ["BK_ENV"] = os.getenv("BK_ENV")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import datetime
    print(" [Success] {} scheduled_update_status Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
    os.environ["BK_ENV"] = os.getenv("BK_ENV", "development")
    # os.environ.setdefault("BK_ENV", "production")     # 生产环境解注改行
    # os.environ.setdefault("BK_ENV", "testing")        # 开发环境解注改行
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import django
    django.setup()
    from control.models import AgentAdmin, ControllerAdmin
    from control.utils.salt_ssh_file import SaltSshBase
    run()
    print(" [Success] {} scheduled_update_status Execution Complete".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))

