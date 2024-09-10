import datetime

import logging
from bastion.component.redis_client_conn import get_redis_dict_data


app_logging = logging.getLogger("app")


class CheckUserHostComponent:
    def check_access_strategy(self, access_strategy=None, access_ip=""):
        if access_strategy is None:
            access_strategy = []
        flag = False
        week_day = datetime.datetime.now().isoweekday()
        hour = datetime.datetime.now().hour
        data = {
            "access_ip": access_ip,
            "login_time_limit": []
        }
        for _access_strategy in access_strategy:
            _access_strategy["status"] = True
            if _access_strategy.get("status") and self.get_time(_access_strategy):
                check_ip = False
                check_time = False
                # 验证黑白名单
                if _access_strategy.get("ip_limit") == 2:
                    try:
                        if access_ip not in _access_strategy.get("limit_list"):
                            check_ip = True
                    except Exception as e:
                        app_logging.error("[ERROR] Check IP black list error: {}, param: {}".format(
                                str(e), str(_access_strategy.id))
                        )
                elif _access_strategy.get("ip_limit") == 3:
                    try:
                        if access_ip in _access_strategy.get("limit_list"):
                            check_ip = True
                    except Exception as e:
                        app_logging.error("[ERROR] Check IP white list error: {}, param: {}".format(
                                str(e), str(_access_strategy.id))
                        )
                else:
                    check_ip = True
                # 验证访问时间
                if _access_strategy.get("login_time_limit"):
                    try:
                        for _login_time_limit in _access_strategy.get("login_time_limit"):
                            if _login_time_limit.get("week") == week_day:
                                if hour in _login_time_limit.get("time"):
                                    check_time = True
                        data["login_time_limit"] = _access_strategy.get("login_time_limit")
                    except Exception as e:
                        app_logging.error("[ERROR] Check time error: {}, param: {}".format(
                                str(e), str(_access_strategy.id))
                        )
                if check_ip and check_time:
                    flag = True
        return flag, data

    def get_time(self, strategy):
        start_time = self._get_datetime_query(strategy.get("start_time"))
        end_time = self._get_datetime_query(strategy.get("end_time"))
        if start_time and end_time:
            if start_time < datetime.datetime.now() < end_time:
                return True
            return False
        elif start_time:
            if start_time < datetime.datetime.now():
                return True
            return False
        elif end_time:
            if datetime.datetime.now() < end_time:
                return True
            return False
        else:
            return True

    def _get_datetime_query(self, datetime_str):
        if not datetime_str:
            return datetime_str
        if datetime_str == "None":
            return None
        try:
            if not isinstance(datetime_str, datetime.datetime):
                return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            try:
                if not isinstance(datetime_str, datetime.datetime):
                    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
            except Exception as e:
                return datetime_str
        return datetime_str

    def check_command(self, info=None, command="", token=""):
        if info is None:
            info = {}
        if token:
            try:
                data = get_redis_dict_data("cache", token)
                # if not data:
                #     return False, 0, {}
                if data.get("admin") or data.get("cache"):
                    return True, 0, {}
                info = data.get("command_data")
            except Exception as e:
                app_logging.error("[ERROR] Check command, check_command error: {}".format(str(e))
                )
                info = {}
        flag = True
        level = 0
        message = {}
        current_time = datetime.datetime.now()
        # current_time = datetime.datetime.strptime("2021-08-31T13:06:24", "%Y-%m-%dT%H:%M:%S")
        week_day = current_time.isoweekday()
        hour = current_time.hour
        command_list = self.handle_command(command)
        # app_logging.debug("[DEBUG] Check command, check_command {}, {}".format(command, token))
        for _command in command_list:
            if info.get(_command):
                for strategy in info.get(_command):
                    start_time = strategy.get("start_time")
                    end_time = strategy.get("end_time")
                    login_time_limit = strategy.get("login_time_limit")
                    block_type = strategy.get("block_type")
                    block_info = strategy.get("block_info")
                    if self.check_time(start_time, end_time, current_time):
                        for _login_time_limit in login_time_limit:
                            if _login_time_limit.get("week") == week_day:
                                if hour in _login_time_limit.get("time"):
                                    flag = False
                                    if level:
                                        if level != 1:
                                            level = block_type
                                            message[_command] = block_info
                                    else:
                                        level = block_type
                                        message[_command] = block_info
                                    if block_type == 1:
                                        message[_command] = block_info
        return flag, level, message

    def handle_command(self, command: str):
        """
        处理|,&,||,&&,;的情况
        ls | rm && cp; ls
        ls && rm
        """
        command_list = [command]
        flag_list = ["|", "&", ";", " "]

        def get_status(flag_list, command):
            for flag in flag_list:
                if flag in command:
                    return True
            return False

        if command in flag_list:
            return command_list
        while get_status(flag_list, command):
            for command in command_list:
                command_index = command_list.index(command)
                for flag in flag_list:
                    if flag in command:
                        command = command_list.pop(command_index)
                        res = command.split(flag)
                        for _res in res:
                            if _res:
                                command_list.insert(command_index, _res.strip())
        command_list.reverse()
        return command_list

    def check_time(self, start_time, end_time, check_time):
        start_time = self._get_datetime_query(start_time)
        end_time = self._get_datetime_query(end_time)
        if start_time or end_time:
            if start_time and end_time:
                if start_time < check_time < end_time:
                    return True
                return False
            elif start_time and not end_time:
                if start_time < check_time:
                    return True
                return False
            elif not start_time and end_time:
                if check_time < end_time:
                    return True
                return False
            else:
                return False
        return True
