# 本地开发环境部署文档

本文档适合开发者在本地开发主机部署开发环境，有一些共享服务需要部署在专用的开发环境主机。

## 系统要求

- 数据库: MySQL、MongoDB、Redis、Elasticsearch
- 消息队列：RabbitMQ、Redis
- Python版本: python3.7

1. 部署说明

- `paas-ce` web侧一共4个项目: paas/appengine/login/esb; 均是基于Django开发的
- 4个项目共用一个数据库
- 项目部署过程一致; 过程中需要注意每个项目的配置文件及拉起的端口号(每个项目需要使用不同的端口号)
- 可以部署在同一台机器上, 使用不同端口号即可

2. 预分配端口号

预先分配每个服务的端口号, 假设部署机器IP为`192.168.0.101`

- appengine: 192.168.0.101:8000 Python2
- paas: 192.168.0.101:8001 Python2
- esb: 192.168.0.101:8002 Python2
- login: 192.168.0.101:8003 Python2
- websocket: 192.168.0.101:8004 Python3

服务间是相互依赖的, 所以部署配置文件中需要将预先分配的服务地址填写到对应变量中。

## 开发环境准备

1. 系统初始化

```
[root@linux-node1 ~]# cat /etc/redhat-release 
CentOS Linux release 7.9.2009 (Core) 
```
关闭SELinux、Iptables、可参考文档：http://k8s.unixhot.com/example-manual.html

2. 安装依赖软件包

```
[root@linux-node1 ~]# yum install -y git mariadb mariadb-server nginx supervisor openssl-devel \
 python3-pip pycrypto gcc glibc python-devel rabbitmq-server python3 python3-devel redis
[root@linux-node1 ~]# mkdir -p /opt/opsany/{logs,uploads}
```

3. 初始化MySQL数据库

```
[root@linux-node1 ~]# vim /etc/my.cnf
default-storage-engine = innodb
innodb_file_per_table
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8

[root@linux-node1 ~]# systemctl enable mariadb && systemctl start mariadb
[root@linux-node1 ~]# mysql_secure_installation 
[root@linux-node1 ~]# mysql -u root -p
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
MariaDB [(none)]> grant all on opsany_paas.* to opsany@localhost identified by '123456.coM';
MariaDB [(none)]> exit;
```

4. 初始化MongoDB数据库

- 配置MongoDB

```
cat > /etc/yum.repos.d/mongodb.repo <<"EOF"
[mongodb-org]
name=MongoDB Repository
#baseurl=https://mirrors.tuna.tsinghua.edu.cn/mongodb/yum/el$releasever/
baseurl=http://mirrors.cloud.tencent.com/mongodb/yum/el$releasever/
gpgcheck=0
enabled=1
EOF
```

- 安装MongoDB

```
[root@linux-node1 ~]# yum install -y mongodb-org-shell mongodb-org-tools mongodb-org mongodb-org-server
[root@linux-node1 ~]# systemctl enable mongod && systemctl start mongod
[root@linux-node1 ~]# netstat -ntlp | grep 27017
tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      28513/mongod
```

5. 部署Redis数据库

- 配置Redis

```
[root@linux-node1 ~]# vim /etc/redis.conf
bind 0.0.0.0
daemonize yes
requirepass 123456.coM
```

- 启动Redis

```
[root@linux-node1 ~]# systemctl enable --now redis
```

6. 部署RabbitMQ消息队列

- 安装RabbitMQ

```
[root@linux-node1 ~]# yum install -y rabbitmq-server
```

- 设置开启启动，并启动RabbitMQ

```
[root@linux-node1 ~]# systemctl enable rabbitmq-server.service
[root@linux-node1 ~]# systemctl start rabbitmq-server.service
```

- 添加用户。

创建一个opsany用户，密码为123456.coM。注意实际使用中进行密码修改，这里设置的用户名和密码在后面配置OpenStack组件的时候需要在配置文件里面设置。
```
[root@linux-node1 ~]# rabbitmqctl add_user opsany 123456.coM
Creating user "opsany" ...
```

- 给刚才创建的openstack用户，创建权限。

```
[root@linux-node1 ~]# rabbitmqctl set_permissions opsany ".*" ".*" ".*"
Setting permissions for user "opsany" in vhost "/" ...
```

- 启用Web监控插件

RabbitMQ自带了一个Web监控插件，可以通过Web界面监控RabbitMQ的运行状态。同时也提供了HTTP API。可以方便的集成到Nagios、Zabbix等监控平台上。
Web监控插件启用后就可以通过http://IP:15672/来访问web管理界面。

```
[root@linux-node1 ~]# rabbitmq-plugins list
[root@linux-node1 ~]# rabbitmq-plugins enable rabbitmq_management
[root@linux-node1 ~]# systemctl restart rabbitmq-server
（注：如果主机名不能解析，rabbitMQ将无法启动。在生产应用时建议设置为集群模式，建议三个节点。1个硬盘节点、两个内存节点。）
[root@linux-node1 ~]# lsof -i:15672
COMMAND  PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
beam    2620 rabbitmq   15u  IPv4  16805      0t0  TCP *:15672 (LISTEN)
```
默认情况下RabbitMQ服务使用5672端口，而Web管理插件监听15672端口，直接在浏览器输入http://192.168.56.11:15672

> RabbitMQ默认的用户名和密码均为guest。之前创建的openstack的用户是无法通过Web界面登录的。


7. 克隆代码

```
[root@linux-node1 ~]# cd /opt
[root@linux-node1 opt]# git clone https://github.com/unixhot/opsany-paas.git
[root@linux-node1 opt]# pip install pip==9.0.3
[root@linux-node1 opt]# pip3 install virtualenv
[root@linux-node1 opt]# mkdir -p /opt/opsany/.runtime
```
> 注意：其它版本的PIP有兼容性问题，请根据文档操作。

## 部署paas服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 opt]# screen -S paas
[root@linux-node1 opt]# cd /opt/opsany/.runtime/
[root@linux-node1 .runtime]# python3 -m venv paas

# 使用Python虚拟环境

[root@linux-node1 .runtime]# source /opt/opsany/.runtime/paas/bin/activate

# 安装依赖软件包
(paas) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/paas/
(paas) [root@linux-node1 .runtime]# pip3 install -r requirements.txt 
```

### 2.配置paas

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(paas) [root@linux-node1 paas]# vim conf/settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': '123456.coM',
        'HOST': '192.168.0.101',
        'PORT': '3306',
    }
}

PAAS_DOMAIN = '192.168.0.101'
BK_COOKIE_DOMAIN = '192.168.0.101'
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(paas) [root@linux-node1 paas]# python manage.py migrate
(paas) [root@linux-node1 paas]# python manage.py runserver 0.0.0.0:8001
```

- 退出Screen(Ctrl + A + D)


## 部署login服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 ~]# screen -S login
[root@linux-node1 ~]# cd /opt/opsany/.runtime/
[root@linux-node1 .runtime]# virtualenv login

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany/.runtime/login/bin/activate
(login) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/login

# 安装依赖软件包
(login) [root@linux-node1 login]# pip install -r requirements.txt 
```

### 2.配置login

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。

```
(login) [root@linux-node1 login]# vim conf/settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'paas',
        'PASSWORD': '123456.coM',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
# cookie访问域
BK_COOKIE_DOMAIN = '192.168.0.101'
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(login) [root@linux-node1 login]# python manage.py migrate
(login) [root@linux-node1 login]# python manage.py runserver 0.0.0.0:8003
```

- 退出Screen(Ctrl + A + D)


## 部署appengine服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 conf]# screen -S appengine
[root@linux-node1 conf]# cd /opt/opsany/.runtime/
[root@linux-node1 .runtime]# virtualenv appengine

# 使用Python虚拟环境
[root@linux-node1 opt]# source /opt/opsany/.runtime/appengine/bin/activate

# 安装依赖软件包
(appengine) [root@linux-node1 paas-runtime]# cd /opt/opsany-paas/paas-ce/paas/appengine/
(appengine) [root@linux-node1 appengine]# pip install -r requirements.txt 
```

### 2.配置appengine

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(appengine) [root@linux-node1 appengine]# vim conf/settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': '123456.coM',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

- 退出python虚拟环境
```
(appengine) [root@linux-node1 appengine]# python manage.py migrate
(appengine) [root@linux-node1 appengine]# python manage.py runserver 0.0.0.0:8000
```

- 退出Screen(Ctrl + A + D)

## 部署esb服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 ~]# screen -S esb
[root@linux-node1 ~]# cd /opt/opsany/.runtime/
[root@linux-node1 .runtime]# virtualenv esb

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany/.runtime/esb/bin/activate

# 安装依赖软件包
(esb) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/esb/
(esb) [root@linux-node1 esb]# pip install -r requirements.txt 
```

### 2.配置esb

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(esb) [root@linux-node1 esb]# cd configs/
(esb) [root@linux-node1 configs]# cp default_template.py default.py
(runtime-esb) [root@paas-node-1 configs]# vim default.py 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': '123456.coM',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(esb) [root@linux-node1 esb]# python manage.py migrate
(esb) [root@linux-node1 esb]# python manage.py runserver 0.0.0.0:8002
```

- 退出Screen(Ctrl + A + D)


## 启动apigateway

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 ~]# screen -S apigw
[root@linux-node1 ~]# cd /opt/opsany/.runtime/
[root@linux-node1 .runtime]# virtualenv apigw

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany/.runtime/apigw/bin/activate

# 安装依赖软件包
(esb) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/apigw/
(esb) [root@linux-node1 esb]# pip install -r requirements.txt 
```

### 2.配置apigw

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(esb) [root@ops esb]# cd configs/
(esb) [root@ops configs]# cp default_template.py default.py
(runtime-esb) [root@paas-node-1 configs]# vim default.py 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': '123456.coM',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(esb) [root@ops esb]# python manage.py migrate
```
退出python虚拟环境
```
(esb) [root@ops esb]# deactivate
```

## 生成环境使用supervisor进行启动

```
[root@opsany-paas ~]# cd /opt/opsany-paas/paas-ce/paas/examples/supervisord.d/
[root@ops supervisord.d]# cp *.ini /etc/supervisord.d/
[root@ops ~]# mkdir /opt/dev-paas/paas-runtime/logs
[root@ops ~]# systemctl start supervisord
[root@ops ~]# supervisorctl status
appengine                        RUNNING   pid 4170, uptime 0:00:13
esb                              RUNNING   pid 4169, uptime 0:00:13
login                            RUNNING   pid 4168, uptime 0:00:13
paas                             RUNNING   pid 4167, uptime 0:00:13
```

### 配置Nginx访问

```
[root@ops ~]# cd /opt/opsany-paas/paas-ce/paas/examples/
[root@ops examples]# cp nginx_paas.conf /etc/nginx/conf.d/
[root@ops examples]# vim /etc/nginx/conf.d/nginx_paas.conf

#在location / 下面增加
location /static {
        proxy_pass http://OPEN_PAAS_LOGIN;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
[root@paas-node-1 ~]# nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
[root@paas-node-1 ~]# systemctl start nginx
```

### 访问PAAS
 - 设置本地Hosts绑定
 - http://dev.example.com/
 - 默认用户名密码：admin admin
