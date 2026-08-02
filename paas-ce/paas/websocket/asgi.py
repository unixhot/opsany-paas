# -*- coding: utf-8 -*-
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
import logging
import signal
import sys
#from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
#application = get_default_application()
from bastion.routing import application

# 注册优雅关闭信号处理器
app_logging = logging.getLogger("app")

def _handle_sigterm(signum, frame):
    """SIGTERM/SIGINT 信号处理 - 优雅关闭"""
    app_logging.warning(
        "[SHUTDOWN] Received signal {}, performing graceful shutdown...".format(
            signal.Signals(signum).name
        )
    )
    # 给工作线程 5 秒时间完成清理
    import time
    time.sleep(5)
    sys.exit(0)

signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)
app_logging.info("[SHUTDOWN] Graceful shutdown handlers registered")

"""
uvicorn --proxy-headers --host 192.168.0.13 --port 8012 asgi:application --log-level=info --access-log

"""
# uvicorn --proxy-headers --host 192.168.0.13 --port 8012 asgi:application
# uvicorn asgi:application
