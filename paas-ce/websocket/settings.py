# -*- coding: utf-8 -*-
"""
请不要修改该文件
如果你需要对settings里的内容做修改，config/default.py 文件中 添加即可
"""

import os

run_env = ""

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
    run_env = "dev"
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {
        'development': 'dev',
        'testing': 'stag',
        'production': 'prod',
    }.get(PAAS_V2_ENVIRONMENT)
    run_env = ENVIRONMENT
DJANGO_CONF_MODULE = 'config.{env}'.format(env=ENVIRONMENT)

try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ['*'])
except ImportError as e:
    raise ImportError("Could not import config '%s' (Is it on sys.path?): %s"
                      % (DJANGO_CONF_MODULE, e))

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

