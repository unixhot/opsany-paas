# Websocket服务

Websocket服务用于通过Web界面（HTTP/HTTPS协议）连接到目标设备上，支持RDP、SSH、Telnet、MySQL、Redis协议，是堡垒机的底层支持服务。

## 安装部署

- 环境：

  - CentOS 7
  - Python 3.6.8
  - Supervisord 3.4.0

### OpsAny Bastion 后端手工部署

1. 创建Python虚拟环境：

```
[root@opsany ~]# yum install -y supervisor
[root@opsany ~]# mkdir -p /opt/opsany/logs
[root@opsany ~]# cd /opt/
[root@opsany ~]# git clone https://github.com/unixhot/opsany-bastion.git
[root@opsany opt]# python3 -m venv /opt/bastion-runtime/
[root@opsany opt]# source /opt/bastion-runtime/bin/activate
(bastion-runtime) [root@opsany opt]# pip install -r /opt/opsany-bastion/requirements.txt
```

2. 配置Supervisord：

- 生成bastion.ini

```
[root@opsany ~]# vim /opt/opsany-bastion/bastion.ini
logdate = true
log-format = [%(addr)] [%(ctime)] [%(method)] [%(uri)] [%(proto)] [%(status)] [%(msecs)] [%(referer)] [%(uagent)]
memory-report = true
master = true
vacuum = true
chdir = /opt/opsany-bastion
module = wsgi:application
      
#cheaper = 4
#cheaper-initial = 4
      
#workers = 4
processes = 4
threads = 2
#cheaper-algo = busyness
#cheaper-overload = 5
#cheaper-step = 2
#cheaper-busyness-multiplier = 60
      
#buffer-size = 8192
#post-buffering = 8192
      
max-requests = 1024
mount = /t/bastion=wsgi.py
manage-script-name = true
```

- 增加bastion的Supervisor配置

```
[root@opsany ~]# vim /etc/supervisord.d/bastion.ini

[program: bastion_uwsgi]
command = /opt/bastion-runtime/bin/uwsgi --ini /opt/opsany-bastion/bastion.ini
stdout_logfile = /opt/opsany/logs/uwsgi.log
redirect_stderr = true
autorestart = true
stopsignal = QUIT
environment = BK_ENV="production",BK_LOG_DIR="/opt/opsany/logs/",BK_PAAS_INNER_HOST="http://",APP_ID="bastion",BK_PAAS_HOST="https://",APP_TOKEN="",BK_CC_HOST="https://",BK_JOB_HOST="https://"
```

- 增加bastion websocket的Supervisor配置

```
[root@opsany ~]# vim /etc/supervisord.d/websocket.ini

[program:websocket]
command=/opt/bastion-runtime/bin/daphne --proxy-headers -b 0.0.0.0 -p 8004 asgi:application
directory=/opt/opsany-bastion
environment=BK_ENV="production",BK_LOG_DIR="/opt/opsany/logs",APP_ID="bastion",BK_PAAS_HOST="https://",APP_TOKEN="4f49d205-87fc-4137-a446-27ab878bfa4c"
startsecs=0
stopwaitsecs=0
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/opsany/logs/websocket.log
```

> 注意：需要补齐APP_TOKEN，BK_PAAS_HOST，或使用PaaS部署，即可忽略uwsgi的supervisord配置，仅需配置websocket的内容即可.

3. 启动Supervisor

```
[root@opsany bastion]# systemctl enable --now supervisord
[root@opsany bastion]# supervisorctl status
websocket                        RUNNING   pid 30554, uptime 0:00:00
```

#### 目录结构

- 本项目基于蓝鲸SaaS开发框架进行开发，框架代码内容概不介绍，仅介绍本项目所用内容

  ```
  ├── bastion  # 主要业务逻辑代码目录
  │   ├── component  # 业务组件目录
  │   │   ├── __init__.py
  │   │   ├── common.py
  │   │   ├── core.py
  │   │   └── redis_client_conn.py
  │   ├── core  # 堡垒机核心组件
  │   │   ├── guacamole
  │   │   │   ├── client.py
  │   │   │   ├── component.py
  │   │   │   ├── exceptions.py
  │   │   │   ├── __init__.py
  │   │   │   └── instruction.py
  │   │   ├── terminal
  │   │   │   ├── __init__.py
  │   │   │   └── component.py
  │   │   ├── __init__.py
  │   │   ├── consumers.py
  │   │   ├── consumers_database_mysql_web.py
  │   │   ├── consumers_database_redis_web.py
  │   │   ├── consumers_database_shell.py
  │   │   ├── consumers_namespace_pod.py
  │   │   ├── consumers_network.py
  │   │   ├── consumers_windows.py
  │   │   └── status_code.py
  │   ├── migrations
  │   │   └── __init__.py
  │   ├── utils  # 常用工具目录
  │   │   ├── __init__.py
  │   │   ├── base_model.py
  │   │   ├── constants.py
  │   │   ├── encryption.py
  │   │   ├── esb_api.py
  │   ├── __init__.py
  │   ├── admin.py
  │   ├── apps.py
  │   ├── constants.py
  │   ├── models.py  # 项目模型
  │   ├── routing.py  # Webscocket路由文件
  │   ├── tests.py
  ├── config  # 项目配置文件目录
  │   ├── __init__.py
  │   ├── default.py
  │   ├── dev.py
  │   ├── prod.py
  │   └── stag.py
  ├── manage.py
  ├── README.md
  ├── requirements.txt
  ├── runtime.txt
  ├── app.yml
  ├── asgi.py
  ├── settings.py
  ├── urls.py
  ├── VERSION
  └── wsgi.py
  ```
