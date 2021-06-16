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
    init_info()
    print(" [Success] {} init_script Execution Complete".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
