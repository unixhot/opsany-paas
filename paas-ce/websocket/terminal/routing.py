# -*- coding: utf-8 -*-

from .consumers import WebSSH
from guacamole.consumers import GuacamoleWebsocket

from django.urls import re_path, path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
            re_path('ws/control/terminalchanneld/', WebSSH),
            re_path(r'^ws/control/terminalchannel/(?P<server_id>\w+)/$', WebSSH),
            re_path('ws/control/guacamoled/', GuacamoleWebsocket),
            re_path(r'^ws/control/guacamole/(?P<server_id>\w+)/$', GuacamoleWebsocket),
        ]
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
