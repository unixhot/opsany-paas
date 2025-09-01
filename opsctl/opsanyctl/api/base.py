from opsanyctl.libs import Request


class BaseObj:
    def __init__(self, config):
        self.this_request = Request(config)
        self.base_params = {
            "username": self.this_request.bk_username,
        }