# -*- coding: utf-8 -*-
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
#from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
#application = get_default_application()
from bastion.routing import application

"""
uvicorn --proxy-headers --host 192.168.0.13 --port 8012 asgi:application --log-level=info --access-log

"""
# uvicorn --proxy-headers --host 192.168.0.13 --port 8012 asgi:application
# uvicorn asgi:application

a =  ('VERSION_1_5_0', 'hostname', 'port', 'domain', 'username', 'password', 'width', 'height', 'dpi', 'initial-program', 'color-depth', 'disable-audio', 'enable-printing', 'printer-name', 'enable-drive', 'drive-name', 'drive-path', 'create-drive-path', 'disable-download', 'disable-upload', 'console', 'console-audio', 'server-layout', 'security', 'ignore-cert', 'disable-auth', 'remote-app', 'remote-app-dir', 'remote-app-args', 'static-channels', 'client-name', 'enable-wallpaper', 'enable-theming', 'enable-font-smoothing', 'enable-full-window-drag', 'enable-desktop-composition', 'enable-menu-animations', 'disable-bitmap-caching', 'disable-offscreen-caching', 'disable-glyph-caching', 'preconnection-id', 'preconnection-blob', 'timezone', 'enable-sftp', 'sftp-hostname', 'sftp-host-key', 'sftp-port', 'sftp-username', 'sftp-password', 'sftp-private-key', 'sftp-passphrase', 'sftp-directory', 'sftp-root-directory', 'sftp-server-alive-interval', 'sftp-disable-download', 'sftp-disable-upload', 'recording-path', 'recording-name', 'recording-exclude-output', 'recording-exclude-mouse', 'recording-exclude-touch', 'recording-include-keys', 'create-recording-path', 'resize-method', 'enable-audio-input', 'enable-touch', 'read-only', 'gateway-hostname', 'gateway-port', 'gateway-domain', 'gateway-username', 'gateway-password', 'load-balance-info', 'disable-copy', 'disable-paste', 'wol-send-packet', 'wol-mac-addr', 'wol-broadcast-addr', 'wol-udp-port', 'wol-wait-time', 'force-lossless', 'normalize-clipboard')
