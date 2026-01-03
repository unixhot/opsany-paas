# PaaS开发环境部署文档

提示：本文档适合开发者在本地开发主机部署PaaS开发环境，大部分情况下是不需要进行PaaS开发的。如果仅仅是开发SaaS平台，不需要参考此文档，可以使用容器化部署OpsAny，然后查看官方文档-开发手册-SaaS平台开发手册即可。

## 系统要求

- 操作系统：Ubunut 20.04、22.04、24.04
- 数据库: MySQL、MongoDB、Redis、Elasticsearch
- 消息队列：RabbitMQ、Redis
- Python版本: Python 3.12.4(PaaS使用)、Python 3.7.17（部分SaaS使用）

1. 部署说明

- `paas-ce` web侧一共5个项目: paas/appengine/login/esb/websocket; 均是基于Django开发的
- 项目部署过程一致; 过程中需要注意每个项目的配置文件及拉起的端口号(每个项目需要使用不同的端口号)
- 可以部署在同一台机器上, 使用不同端口号即可。
- 后续所有操作均以Ubuntu操作系统为准，其它操作系统请自行调整。

2. 预分配端口号

预先分配每个服务的端口号, 假设部署机器IP为`192.168.0.111`

- appengine: 192.168.0.111:8000 
- paas: 192.168.0.111:8001
- esb: 192.168.0.111:8002
- login: 192.168.0.111:8003 
- websocket: 192.168.0.111:8004

服务间是相互依赖的, 所以部署配置文件中需要将预先分配的服务地址填写到对应变量中。

## 开发环境准备（Ubuntu）

1. 基础软件包安装和Redis、RabbitMQ、Nginx、Mariadb等安装。

```
apt-get update
apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
libgdbm-dev libnss3-dev libedit-dev libc6-dev screen wget uuid unzip \
redis-server mariadb-server rabbitmq-server nginx supervisor tcl-dev \
libmariadb-dev-compat libmariadb-dev libsasl2-dev libldap2-dev libssl-dev \
gcc libjpeg-dev libtiff5-dev libpng-dev libfreetype6-dev
```

2. 初始化MySQL数据库。

```
# 修改配置文件
[root@linux-node1 ~]# vim vim /etc/mysql/mariadb.conf.d/50-server.cnf 
bind-address            = 192.168.0.111
default-storage-engine = innodb
innodb_file_per_table
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8

# 启动MySQL并进行初始化
[root@linux-node1 ~]# systemctl enable mariadb && systemctl start mariadb
[root@linux-node1 ~]# mysql_secure_installation 

# 创建数据库
[root@linux-node1 ~]# mysql -u root -p
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS opsany_proxy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
MariaDB [(none)]> CREATE USER opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";
MariaDB [(none)]> grant all on opsany_paas.* to opsany@'%';
MariaDB [(none)]> grant all on opsany_proxy.* to opsany@'%';
MariaDB [(none)]> exit;
```

3. 部署Redis数据库

- 配置Redis

```
[root@linux-node1 ~]# vim /etc/redis/redis.conf
bind 0.0.0.0
daemonize yes
requirepass 123456.coM
```

- 启动Redis

```
[root@linux-node1 ~]# systemctl enable --now redis-server
```

4. 部署RabbitMQ消息队列

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
[root@linux-node1 ~]# rabbitmqctl set_user_tags opsany administrator
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


5. 克隆代码并准备Python环境

已知CentOS 7由于GCC版本比较低，无法成功编译Python3.12，推荐使用Ubuntu 22.04。

- 5.1 准备Python3环境

```
# 编译安装Python 3.12.4
[root@linux-node1 ~]# yum install -y abc abc-devel
[root@linux-node1 ~]# cd /usr/local/src
[root@linux-node1 src]# wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tgz
[root@linux-node1 src]# tar zxf Python-3.12.4.tgz
[root@linux-node1 src]# cd Python-3.12.4/
[root@linux-node1 Python-3.6.8]# ./configure --prefix=/usr/local/Python-3.12.4 --enable-ipv6 --enable-optimizations
[root@linux-node1 Python-3.6.8]# make && make install

# 编译安装Python 3.7.17
[root@linux-node1 ~]# yum install -y abc abc-devel
[root@linux-node1 ~]# cd /usr/local/src
[root@linux-node1 src]# wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
[root@linux-node1 src]# tar zxf Python-3.7.17.tgz
[root@linux-node1 src]# cd Python-3.7.17/
[root@linux-node1 Python-3.6.8]# ./configure --prefix=/usr/local/Python-3.7.17 --enable-ipv6 --enable-optimizations
[root@linux-node1 Python-3.6.8]# make && make install
```

- 5.2 确认Python版本

```
[root@ops ~]# ln -s /usr/local/Python-3.12.4 /opt/py312
[root@ops ~]# /opt/py312/bin/python3 --version
Python 3.12.4
[root@ops ~]# ln -s /usr/local/Python-3.7.17 /opt/py37
[root@ops ~]# /opt/py37/bin/python3 --version
Python 3.7.17
```

- 5.3 克隆项目代码

```
[root@linux-node1 ~]# cd /opt
[root@linux-node1 opt]# git clone https://gitee.com/unixhot/opsany-paas.git
[root@linux-node1 opt]# cd /opt/opsany-paas/
[root@linux-node1 opt]# /opt/py312/bin/pip3 install virtualenv -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
[root@linux-node1 opt]# mkdir -p /opt/opsany-paas/.runtime
```

## 部署paas服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 opt]# screen -S paas
[root@linux-node1 opt]# cd /opt/opsany-paas/.runtime/
[root@linux-node1 .runtime]# /usr/local/Python-3.12.4/bin/python3 -m venv paas

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany-paas/.runtime/paas/bin/activate

# 安装依赖软件包
(paas) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/paas/
(paas) [root@linux-node1 .runtime]# pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 2.配置paas

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(paas) [root@linux-node1 paas]# cp conf/settings_development.py.sample
(paas) [root@linux-node1 paas]# vim conf/settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'opsany',
        'PASSWORD': '123456.coM',
        'HOST': '192.168.0.111',
        'PORT': '3306',
    }
}

PAAS_DOMAIN = '192.168.0.111'
BK_COOKIE_DOMAIN = '192.168.0.111'
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(paas) [root@linux-node1 paas]# python manage.py migrate
(paas) [root@linux-node1 paas]# python manage.py runserver --skip-checks 0.0.0.0:8001
```

- 退出Screen(Ctrl + A + D)

## 部署login服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 ~]# screen -S login
[root@linux-node1 ~]# cd /opt/opsany-paas/.runtime/
[root@linux-node1 .runtime]# /usr/local/Python-3.12.4/bin/python3 -m venv login

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany-paas/.runtime/login/bin/activate
(login) [root@linux-node1 .runtime]# cd /opt/opsany-paas/paas-ce/paas/login/

# 安装依赖软件包
(login) [root@linux-node1 login]# pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 2.配置login

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。

```
(login) [root@linux-node1 login]# cp conf/settings_development.py.sample conf/settings_development.py
(login) [root@linux-node1 login]# vim conf/settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'opsany_paas',
        'USER': 'paas',
        'PASSWORD': '123456.coM',
        'HOST': '192.168.0.111',
        'PORT': '3306',
    }
}
# cookie访问域
BK_COOKIE_DOMAIN = '192.168.0.111'
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）

```
(login) [root@linux-node1 login]# python3 manage.py migrate
(login) [root@linux-node1 login]# python3 manage.py runserver 0.0.0.0:8003
```

- 退出Screen(Ctrl + A + D)


## 部署appengine服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 conf]# screen -S appengine
[root@linux-node1 conf]# cd /opt/bk-paas/.runtime/
[root@linux-node1 .runtime]# /usr/local/Python-3.12.4/bin/python3 -m venv appengine

# 使用Python虚拟环境
[root@linux-node1 opt]# source /opt/bk-paas/.runtime/appengine/bin/activate

# 安装依赖软件包
(appengine) [root@linux-node1 paas-runtime]# cd /opt/opsany-paas/paas-ce/paas/appengine/
(appengine) [root@linux-node1 appengine]# pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 2.配置appengine

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
 (appengine) [root@linux-node1 appengine]# cp controller/settings_sample.py controller/settings.py
(appengine) [root@linux-node1 appengine]# vim controller/settings.py
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
(appengine) [root@linux-node1 appengine]# python manage.py migrate
(appengine) [root@linux-node1 appengine]# python manage.py runserver 0.0.0.0:8000
```

- 退出Screen(Ctrl + A + D)

## 部署esb服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@linux-node1 ~]# screen -S esb
[root@linux-node1 ~]# cd /opt/opsany-paas/.runtime/
[root@linux-node1 .runtime]# /usr/local/Python-3.12.4/bin/python3 -m venv esb

# 使用Python虚拟环境
[root@linux-node1 .runtime]# source /opt/opsany-paas/.runtime/esb/bin/activate

# 安装依赖软件包
(esb) [root@linux-node1 esb]# cd /opt/opsany-paas/paas-ce/paas/esb/
(esb) [root@linux-node1 esb]# pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 2.配置esb

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(esb) [root@linux-node1 esb]# cp configs/default_template.py configs/default.py
(esb) [root@linux-node1 esb]# vim configs/default.py 
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

### 配置Nginx访问

```
[root@ops ~]# cd /opt/opsany-paas/paas-ce/paas/examples/
[root@ops examples]# cp nginx_paas.conf /etc/nginx/conf.d/
[root@ops examples]# vim /etc/nginx/conf.d/nginx_paas.conf
[root@paas-node-1 ~]# nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
[root@paas-node-1 ~]# systemctl start nginx

# 登录页面的图片需要放置在uploads下面，不然打开登录页图片无法展示。
[root@paas-node-1 ~]# cp -r /opt/opsany-paas/install/uploads/login /opt/opsany/uploads/
```

### 访问PAAS平台。
 - http://192.168.0.111/
 - 默认用户名密码：admin admin
