# -*- coding: utf-8 -*-
import settings
base_api_url = "/{}/cmdb/api/cmdb/v0_1/".format(getattr(settings, "BK_ENV", "o"))
