#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from opsanymcp import load_yaml_config
from opsanymcp.api import get_opsany_api
from opsanymcp.libs import check_auth
from tool_list import _get_tool

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Scope, Receive, Send

import uvicorn
import argparse
import contextvars

# 全局上下文变量
current_username = contextvars.ContextVar("username", default=None)
current_api_token = contextvars.ContextVar("api_token", default=None)


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8020
    config: Dict = field(default_factory=dict)
    auth_token: Optional[str] = None


class AuthenticatedPostMessageApp:
    """为 /messages POST 请求添加认证的 ASGI 包装器"""
    def __init__(self, inner_app: ASGIApp, expected_token: Optional[str]):
        self.inner_app = inner_app
        self.expected_token = expected_token

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or scope["method"] != "POST":
            await self.inner_app(scope, receive, send)
            return

        if check_auth(scope, self.expected_token):
            await self._send_unauthorized(send)
            return

        await self.inner_app(scope, receive, send)

    async def _send_unauthorized(self, send: Send):
        body = json.dumps({"error": "Unauthorized"}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer realm=\"mcp\""),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })


class OpsAnyMCPServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server("opsany-mcp-server")
        self.opsany_config = config.config
        self.licence = self.opsany_config.get("apiService", {}).get("licence", "ce")
        self._register_handlers()

    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [Tool(**i) for i in _get_tool(self.licence)]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            username = current_username.get()
            api_token = current_api_token.get()
            api_params = {"config": self.opsany_config, "username": username, "api_token": api_token}
            try:
                status, api, msg = get_opsany_api(name, **api_params)
                if status:
                    result = api.run(arguments)
                else:
                    result = msg
            except Exception as e:
                result = json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result)]


async def main():
    parser = argparse.ArgumentParser(description="OpsAny MCP Server")
    parser.add_argument("--host", help="Host to bind to (overrides config)")
    parser.add_argument("--port", type=int, help="Port to listen on (overrides config)")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    config_path = args.config or "config/config.yaml"
    config_status, opsany_config = load_yaml_config(config_path)
    if not config_status:
        print(f"Error loading config: {opsany_config}")
        return

    server_cfg = opsany_config.get("server", {})
    url = opsany_config.get("apiService", {}).get("url")
    licence = opsany_config.get("apiService", {}).get("licence")
    version = opsany_config.get("apiVersion", "-")
    host = args.host or server_cfg.get("host", "0.0.0.0")
    port =  args.port or server_cfg.get("port", 8020)
    auth_token = server_cfg.get("auth_token")  # ← 读取 token

    if not host or not port:
        print(f"Error loading server config (host/port): {opsany_config}")
        return

    config = ServerConfig(
        host=host,
        port=port,
        config=opsany_config,
        auth_token=auth_token
    )

    server_instance = OpsAnyMCPServer(config)
    sse = SseServerTransport("/messages")

    # --- 路由处理函数 ---
    async def index(request: Request):
        # 可选：是否对 / 做认证？这里选择不做（用于健康检查）
        return Response(
            content=json.dumps({
                "success": True,
                "name": "OpsAny MCP Server",
                "version": opsany_config.get("apiVersion", "unknown")
            }),
            media_type="application/json"
        )

    async def handle_sse(request: Request):
        auth_error = check_auth(request, config.auth_token)
        if auth_error:
            return auth_error
        username = request.headers.get("username")
        api_token = request.headers.get("user-api-token")
        # 设置上下文
        token1 = current_username.set(username)
        token2 = current_api_token.set(api_token)
        try:
            async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
                await server_instance.server.run(
                    read_stream,
                    write_stream,
                    server_instance.server.create_initialization_options()
                )
        finally:
            # 清理上下文
            current_username.reset(token1)
            current_api_token.reset(token2)
        return Response()

    async def handle_sse_tools(request: Request):
        auth_error = check_auth(request, config.auth_token)
        if auth_error:
            return auth_error
        return Response(
            content=json.dumps({"success": True, "tools": _get_tool(licence)}),
            media_type="application/json"
        )

    # --- 构建应用 ---
    app = Starlette(
        debug=True,
        routes=[
            Route("/", endpoint=index, methods=["GET"]),
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages", app=AuthenticatedPostMessageApp(sse.handle_post_message, config.auth_token)),
            Route("/sse/tools", endpoint=handle_sse_tools, methods=["GET"]),
        ]
    )
    print(f"MCP Version {version}, OpsAny apiService Url: {url}")
    print(f"Starting OpsAny MCP Server on {host}:{port}")

    config_uv = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config_uv)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
