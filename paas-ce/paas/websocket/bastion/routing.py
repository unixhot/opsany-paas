from django.urls import path

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
    path('ws/bastion/terminalchannel/', WebSSH.as_asgi()), 
    path('ws/bastion/guacamole/', GuacamoleWebsocket.as_asgi()),
    path('ws/bastion/network/guacamole/', GuacamoleNetWorkWebsocket.as_asgi()), 
    path('ws/bastion/databases/', Database.as_asgi()), 
    path('ws/bastion/databases/web/', DatabaseMysqlWeb.as_asgi()),
    path('ws/bastion/database/mysql/web/', DatabaseMysqlWeb.as_asgi()), 
    path('ws/bastion/database/redis/web/', DatabaseRedisWeb.as_asgi()), 
    
    # k8s容器登录
    path('ws/bastion/namespace/pod/container/login/', PodConsumer.as_asgi()),
]
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
