#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
opsctl 命令行工具的主入口文件

该文件负责初始化命令行应用，定义支持的命令，并调用相应的处理逻辑。
"""

# 导入必要的系统模块
import os
import sys

# 添加当前文件所在目录和父目录到 Python 路径，确保能正确导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入第三方库和项目模块
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from opsanyctl.api.resource_type import ResourceType
from opsanyctl.api.fields import ResourceFields
from opsanyctl.api.resource import Resource
from opsanyctl.help_content import *
from opsanyctl.libs import load_yaml_config, check_command

# 定义支持的命令列表
supported_commands = [
    "--help",          # 帮助命令
    "config",          # 获取配置文件模板
    "get",             # 获取各类资源数据
    "res",             # api-resources 命令的简写
    "api-resources",   # 获取全部资源模型
]

# 创建 Typer 应用实例
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},  # 设置帮助选项名称
    # help=typer_help_content,  # 应用帮助内容（已注释）
    add_completion=True  # 启用命令自动补全功能
)

# 检查命令是否支持
check_command(supported_commands)

# 初始化 rich 控制台，用于美化输出
console = Console()

# 加载配置文件
config_status, opsanyctl_config = load_yaml_config()
if not config_status:
    # 配置加载失败，输出错误信息并退出
    typer.echo(typer.style(opsanyctl_config, fg=typer.colors.YELLOW, bold=True))
    sys.exit(1)

# 提取默认配置参数
default_config = opsanyctl_config.get('config') or {}
# 资源类型短名称映射
default_resource_short = opsanyctl_config.get('resourceShort') or {}
# 资源 ID 默认字段
resource_id_default_field = default_config.get('resourceIdDefaultField') or "code,VISIBLE_NAME,name"
# 是否启用资源 ID 字段搜索
resource_id_field_search = default_config.get('resourceIdFieldSearch') or False
# 资源默认每页数量
resource_default_limit = default_config.get('resourceDefaultLimit') or 20
# 资源模型默认每页数量
api_resources_default_limit = default_config.get('apiResourcesDefaultLimit') or 100

@app.command("config", help=command_config_help)
def config():
    """
    输出配置文件模板

    该命令会显示配置文件的模板内容，用户可以根据模板创建自己的配置文件。
    """
    # 输出配置标题（绿色加粗）
    typer.echo(typer.style(config_content_title, fg=typer.colors.GREEN, bold=True))
    # 输出配置内容
    typer.echo(config_content)

@app.command("api-resources", help=command_api_resources_help)
def api_resources(
        output: str = typer.Option("", "--output", "-o", help=command_api_resources_arg_output_help),
        limit: int = typer.Option(api_resources_default_limit, "--limit", "-l",
                                  help=command_api_resources_arg_limit_help)
):
    """
    获取全部资源模型

    Args:
        output: 输出格式（目前未使用）
        limit: 返回的资源模型数量限制

    该命令用于获取系统支持的所有资源模型信息，并以表格形式展示。
    """
    # 创建资源类型 API 实例
    res = ResourceType(opsanyctl_config)
    # 获取资源类型数据
    status, headers, data, mess = res.get_resources_type(output, limit, default_short=default_resource_short)
    if not status:
        # 获取失败，输出错误信息
        typer.echo(typer.style(mess, fg=typer.colors.YELLOW, bold=True))
        return
    # 创建表格并设置表头
    table = Table(show_header=True, header_style="bold magenta", expand=False)
    for header in headers:
        table.add_column(header, no_wrap=False, overflow="fold")
    # 添加数据行
    for row in data:
        table.add_row(*row)
    # 打印表格
    console.print(table)

@app.command("res", help=command_re_help)
def res(
        output: str = typer.Option("", "--output", "-o", help=command_api_resources_arg_output_help),
        limit: int = typer.Option(api_resources_default_limit, "--limit", "-l",
                                  help=command_api_resources_arg_limit_help)
):
    """
    api-resources 命令的简写

    Args:
        output: 输出格式（目前未使用）
        limit: 返回的资源模型数量限制

    该命令是 api-resources 命令的简写形式，功能完全相同。
    """
    api_resources(output, limit)

@app.command("get", help=command_get_help)
def get(
        resource_type: str = typer.Argument(..., help=command_get_arg_resource_type_help),
        resource_id: str = typer.Argument(None, help=command_get_arg_resource_id_help),
        search: str = typer.Option(None, "--search", "-s", help=command_get_opt_search_help),
        fields: str = typer.Option(None, "--fields", "-f", help=command_get_opt_fields_help),
        page: int = typer.Option(1, "--page", "-p", help=command_get_opt_page_help),
        limit: int = typer.Option(resource_default_limit, "--limit", "-l", help=command_get_opt_limit_help)
):
    """
    获取资源数据

    Args:
        resource_type: 资源类型（必填）
        resource_id: 资源 ID（可选）
        search: 搜索关键词（可选）
        fields: 要显示的字段（可选）
        page: 页码（默认为 1）
        limit: 每页数量（默认为 20）

    该命令用于获取指定类型的资源数据，并支持搜索、分页等功能。
    """
    # 处理资源类型和字段（如 ser.fields 格式）
    if "." in resource_type:
        resource, field = resource_type.split(".")
    else:
        resource, field = resource_type, ""
    # 检查是否有资源类型短名称映射
    if resource in default_resource_short:
        resource = default_resource_short[resource]
    # 处理字段查询
    if field:
        if field == "fields":
            # 获取资源字段信息
            res = ResourceFields(opsanyctl_config)
            status, headers, data, mess = res.get_resource_field(resource)
        else:
            # 不支持的字段
            mess = f"当前资源 {resource} 不支持属性 {field}，请使用 {resource}.fields 等"
            typer.echo(typer.style(mess, fg=typer.colors.YELLOW, bold=True))
            return
    else:
        # 获取资源数据
        res = Resource(opsanyctl_config)
        status, headers, data, mess = res.get_resource(resource, resource_id, search, fields, page, limit,
                                                       resource_id_default_field, resource_id_field_search)
    # 检查请求状态
    if not status:
        typer.echo(typer.style(mess, fg=typer.colors.YELLOW, bold=True))
        return
    # 创建表格并设置表头
    table = Table(show_header=True, header_style="bold magenta", expand=False)
    for header in headers:
        if isinstance(header, list):
            # 处理复合表头
            header_text = Text(justify="center")
            for h in header:
                header_text.append(h, style="bold magenta")
                header_text.append("\n")
        else:
            header_text = header
        table.add_column(header_text, no_wrap=False, overflow="fold")
    # 添加数据行
    for row in data:
        table.add_row(*row)
    # 打印表格和信息
    console.print(table)
    console.print(Text(mess, style="italic green"))

if __name__ == "__main__":
    """
    主程序入口

    当脚本直接运行时，启动命令行应用。
    """
    # 示例用法:
    # python main.py api-resources --help
    # python main.py get ser
    app()