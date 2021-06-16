# -*- coding: utf-8 -*-
VERSION = '3.1.0'
__version__ = VERSION


RUN_VER = ""


def get_run_ver():
    from django.conf import settings
    try:
        return settings.RUN_VER
    except AttributeError:
        return RUN_VER
