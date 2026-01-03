# -*- coding: utf-8 -*-
import settings
base_api_url = "/{}/pipeline/api/pipeline/v0_1/".format(getattr(settings, "BK_ENV", "o"))
