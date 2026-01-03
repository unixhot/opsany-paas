# -*- coding: utf-8 -*-
import settings
base_api_url = "/{}/repo/api/repo/v0_1/".format(getattr(settings, "BK_ENV", "o"))
