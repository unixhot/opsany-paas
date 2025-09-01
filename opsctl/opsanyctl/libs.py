import os
import sys
from difflib import get_close_matches
from pathlib import Path

import typer
import yaml
from requests import request

import urllib3

urllib3.disable_warnings()


class Request:
    def __init__(self, config):
        self.api_service = config.get("apiService")
        self.url = self.api_service.get("url")
        self.bk_app_code = self.api_service.get("bk_app_code")
        self.bk_app_secret = self.api_service.get("bk_app_secret")
        self.bk_username = self.api_service.get("bk_username")

    def _request(self, url_path, method, params, body, headers=None, timeout=10):
        if not headers:
            headers = {"Content-Type": "application/json; charset=utf-8"}
        url = str(self.url) + url_path
        params.update({
            "bk_app_code": self.bk_app_code,
            "bk_app_secret": self.bk_app_secret,
            "bk_username": self.bk_username,
        })
        try:
            res = request(method, url, data=body, params=params, headers=headers, timeout=timeout, verify=False)
            try:
                json_data = res.json()
                if not json_data.get("result"):
                    return False, [], json_data.get("message")
                return True, res.json().get("data"), "Success"
            except Exception as e:
                return False, [], f"HTTP 响应解析失败: {res.content.decode()}"
        except Exception as e:
            return False, [], f"HTTP 请求失败: {str(url)} {str(e)}"


def load_yaml_config() -> tuple:
    file_path = os.path.join(str(Path.home()), ".opsanyctl/config")
    base = "，请使用 opsanyctl config 命令获取到配置文件并正确配置！"
    if len(sys.argv) > 1 and (sys.argv[1] in ["config"]):
            return True, {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        if not isinstance(config, dict):
            return False, f"错误: 配置文件 config 格式不正确" + base

        api_service = config.get("apiService")
        if not isinstance(api_service, dict):
            return False, f"错误: 配置文件 config.apiService 格式不正确" + base
        if not all([k in api_service for k in ["url", "bk_app_code", "bk_app_secret", "bk_username"]]):
            return False, f"错误: 配置文件 config.apiService 缺少必要项" + base
        return True, config
    except FileNotFoundError:
        return False, f"错误: 配置文件 '{file_path}' 不存在" + base
    except yaml.YAMLError as e:
        return False, f"错误: 无法解析 YAML 文件 '{file_path}': {e}" + base
    except Exception as e:
        return False, f"错误: 未知的错误: {str(e)}" + base


def check_command(supported_commands):
    try:
        if len(sys.argv) > 1:
            unknown_command = sys.argv[1]
            if unknown_command in ["--help", "-h"]:
                return
            if unknown_command not in supported_commands:
                matches = get_close_matches(unknown_command, supported_commands, n=2, cutoff=0.4)
                if matches:
                    typer.echo("")
                    typer.echo(f"unknown command \"{unknown_command}\" for opsanyctl, Did you mean this?")
                    for match in matches:
                        typer.echo(f"\t{match}")
                    sys.exit()
                else:
                    c_str = ", ".join(supported_commands)
                    typer.echo(f"error: unknown command \"{unknown_command}\" for opsanyctl, supported commands {c_str}")
                    sys.exit()
    except Exception as e:
        pass
