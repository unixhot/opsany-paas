from bastion.models import UserInfo
from bastion.utils.esb_api import EsbApi


class GetUserInfo:
    def get_user_info(self, request=None, bk_token=None):
        try:
            from django.conf import settings
            bk_token = settings.BK_TOKEN
        except Exception as e:
            pass
        if not bk_token:
            bk_token = request.COOKIES.get("bk_token")
        esb_obj = EsbApi(bk_token)
        user_info = esb_obj.get_user_info()
        return UserInfo.fetch_one(username=user_info.get("username"))
