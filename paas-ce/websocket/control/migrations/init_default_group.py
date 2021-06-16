from django.db import migrations

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))
path = os.path.join(os.path.join(BASE_DIR, "utils"), "init_script.py")
path_2 = os.path.join(os.path.join(BASE_DIR, "utils"), "init_script.pyc")
import logging
logger = logging.getLogger(__name__)


def run_init(apps, schema_editor):
    if os.path.isfile(path):
        command = "python {}".format(path)
    else:
        command = "python {}".format(path_2)
    logger.info("file path %s" % command)
    os.system(command)


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0040_auto_20210413_1104'),
    ]

    operations = [
        migrations.RunPython(run_init)
    ]
