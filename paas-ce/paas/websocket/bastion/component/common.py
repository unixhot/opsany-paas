import logging

from bastion.models import UserInfo
from bastion.utils.esb_api import EsbApi

logger = logging.getLogger("app")


class GetUserInfo:
    def get_user_info(self, request=None, bk_token=None):
        try:
            from django.conf import settings
            # 只在 DEBUG 模式下使用 settings.BK_TOKEN 作为开发快捷方式
            # 生产环境下必须通过 cookie 中的 bk_token 进行用户认证
            if getattr(settings, 'DEBUG', False):
                bk_token = settings.BK_TOKEN
        except Exception as e:
            logger.debug("[GetUserInfo] BK_TOKEN not available: %s", e)
        if not bk_token and request:
            bk_token = request.COOKIES.get("bk_token")
        if not bk_token:
            logger.warning("[GetUserInfo] No bk_token available for authentication")
            return None
        esb_obj = EsbApi(bk_token)
        user_info = esb_obj.get_user_info()
        if not user_info:
            return None
        return UserInfo.fetch_one(username=user_info.get("username"))
