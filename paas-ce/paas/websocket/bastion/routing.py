from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from bastion.core.consumers import WebSSH
from bastion.core.consumers_database_shell import Database
from bastion.core.consumers_database_redis_web import DatabaseRedisWeb
from bastion.core.consumers_database_mysql_web import DatabaseMysqlWeb
from bastion.core.consumers_network import GuacamoleNetWorkWebsocket
from bastion.core.consumers_windows import GuacamoleWebsocket
from bastion.core.consumers_namespace_pod import PodConsumer

websocket_urlpatterns = [
    # 堡垒机登录
    re_path(r'^ws/bastion/terminalchannel/$', WebSSH),  # linux： ssh
    re_path(r'^ws/bastion/guacamole/$', GuacamoleWebsocket),  # Windows：rdp
    re_path(r'^ws/bastion/network/guacamole/$', GuacamoleNetWorkWebsocket),  # 网络设备: telnet
    re_path(r'^ws/bastion/databases/$', Database),  # 数据库SHELL： ssh
    re_path(r'^ws/bastion/databases/web/$', DatabaseMysqlWeb),
    re_path(r'^ws/bastion/database/mysql/web/$', DatabaseMysqlWeb),  # 数据库-MySQL-WEB: SSHTunnelForwarder
    re_path(r'^ws/bastion/database/redis/web/$', DatabaseRedisWeb),  # 数据库Redis-WEB: SSHTunnelForwarder
    
    # k8s容器登录
    re_path(r'^ws/bastion/namespace/pod/container/login/$', PodConsumer),  # 容器平台登录到Pdo中
]
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
