import os
import sys


def init_info():
    dt = {
        "minute": "*/10",
        "hour": "*",
        "day_of_week": "*",
        "day_of_month": "*",
        "month_of_year": "*",
    }
    schedule_obj, _ = CrontabSchedule.objects.update_or_create(**dt)
    schedule = schedule_obj.schedule
    create_or_update_task = DatabaseScheduler.create_or_update_task
    schedule_dict = {
        'schedule': schedule,
        'args': [],
        'kwargs': {},
        'task': "control.celery_tasks.run_task",
        'enabled': True,
        'description': "",
        'last_run_at': datetime.datetime.now()
    }
    crontab_task_name = "OpsAny system default task."
    create_or_update_task(crontab_task_name, **schedule_dict)


def init_default_group():
    dic = {
        "name": "默认分组",
        "type": "静态",
        "describe": "系统分组，不可修改和删除",
        "create_time": "2008-08-08 10:10:42.145301",
        "update_time": "2008-08-08 10:10:42.145301",
    }

    if not HostGroup.objects.filter(name=dic.get("name")).first():
        HostGroup(**dic).save()
    host_group = HostGroup.objects.filter(name=dic.get("name"))
    host_group.update(**dic)

    #  将未分组主机纳入到默认分组
    agent_admin_queryset = AgentAdmin.objects.filter(group=None).exclude(controller=None).all()
    if agent_admin_queryset:
        for agent_admin in agent_admin_queryset:
            agent_admin.update(group=host_group.first())
    print("agent_admin_queryset", agent_admin_queryset)
    print(" [Success] {} init_default_group Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import datetime

    print(" [Success] {} init_script Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
    os.environ["BK_ENV"] = os.getenv("BK_ENV", "development")
    # os.environ.setdefault("BK_ENV", "production")     # 生产环境解注改行
    # os.environ.setdefault("BK_ENV", "testing")        # 开发环境解注改行
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import django

    django.setup()
    from djcelery.models import CrontabSchedule
    from djcelery.schedulers import DatabaseScheduler
    from control.models import HostGroup, AgentAdmin

    init_info()
    init_default_group()
    print(" [Success] {} init_script Execution Complete".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
