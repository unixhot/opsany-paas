#-*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
from esb.utils import SmartHost
import settings

# 系统名的小写形式要与系统包名保持一致
SYSTEM_NAME = 'job'

host = SmartHost(
    # 需要填入系统正式环境的域名地址
    host_prod=settings.PAAS_DOMAIN,
)

base_api_url = "/{}/job/api/job/v0_1/".format(getattr(settings, "BK_ENV", "o"))
