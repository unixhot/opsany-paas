# 开发环境部署文档

## 系统要求

- 数据库: MySQL、MongoDB、Redis
- 消息队列：RabbitMQ
- Python版本: python2.7 (务必使用python2.7, 推荐2.7.15)

## 部署说明

- `paas-ce` web侧一共4个项目: paas/appengine/login/esb; 均是基于Django开发的
- 4个项目共用一个数据库
- 项目部署过程一致; 过程中需要注意每个项目的配置文件及拉起的端口号(每个项目需要使用不同的端口号)
- 可以部署在同一台机器上, 使用不同端口号即可

## 部署顺序

#### 1. 预分配端口号

预先分配每个服务的端口号, 假设部署机器IP为`127.0.0.1`

- appengine: 127.0.0.1:8000
- paas: 127.0.0.1:8001
- esb: 127.0.0.1:8002
- login: 127.0.0.1:8003

服务间是相互依赖的, 所以部署配置文件中需要将预先分配的服务地址填写到对应变量中

## 环境准备

### 1.系统初始化
```
[root@paas-node-1 ~]# cat /etc/redhat-release 
CentOS Linux release 7.9.2009 (Core) 
```
关闭SELinux、Iptables、可参考文档：http://k8s.unixhot.com/example-manual.html

### 2.安装依赖软件包
```
[root@paas-node-1 ~]# yum install -y git mariadb mariadb-server nginx supervisor \
 python-pip pycrypto gcc glibc python-devel mongodb mongodb-server
```

### 3.初始化MySQL数据库
```
[root@paas-node-1 ~]# vim /etc/my.cnf
default-storage-engine = innodb
innodb_file_per_table
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8
[root@paas-node-1 ~]# systemctl enable mariadb && systemctl start mariadb
[root@paas-node-1 ~]# mysql_secure_installation 
[root@paas-node-1 ~]# mysql -u root -p
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
MariaDB [(none)]> grant all on opsany_paas.* to opsany@localhost identified by '123456.coM';
```

### 4.初始化MongoDB数据库
```
cat > /etc/yum.repos.d/mongodb.repo <<"EOF"
[mongodb-org]
name=MongoDB Repository
#baseurl=https://mirrors.tuna.tsinghua.edu.cn/mongodb/yum/el$releasever/
baseurl=http://mirrors.cloud.tencent.com/mongodb/yum/el$releasever/
gpgcheck=0
enabled=1
EOF

[root@paas-node-1 ~]# yum install -y mongodb-org-shell mongodb-org-tools mongodb-org mongodb-org-server
[root@paas-node-1 ~]# systemctl enable mongod && systemctl start mongod
[root@linux-node1 ~]# netstat -ntlp | grep 27017
tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      28513/mongod
```

### 5. 部署Redis数据库

[root@opsany-paas ~]# vim /etc/redis.conf
bind 0.0.0.0
daemonize yes
requirepass 123456.coM

### 5.克隆代码
```
[root@paas-node-1 ~]# cd /opt
[root@paas-node-1 opt]# git clone https://github.com/unixhot/opsany-paas.git
[root@paas-node-1 opt]# pip install pip==9.0.3
[root@paas-node-1 opt]# pip install virtualenv
[root@paas-node-1 opt]# mkdir -p /opt/opsany/.runtime
```
> 注意：其它版本的PIP有兼容性问题，请根据文档操作。

## 部署paas服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@dev opsany]# cd /opt/opsany/.runtime/
[root@dev .runtime]# virtualenv paas

# 使用Python虚拟环境
[root@dev .runtime]# source /opt/opsany/.runtime/paas/bin/activate

# 安装依赖软件包
(paas) [root@dev .runtime]# cd /opt/opsany-paas/paas-ce/paas/paas/
(paas) [root@dev .runtime]# pip install -r requirements.txt 
```

### 2.配置paas

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(paas) [root@ops paas]# cd conf/
(paas) [root@ops conf]# vim settings_development.py
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
(paas) [root@ops paas]# python manage.py migrate
```
退出python虚拟环境
```
(runtime-paas) [root@paas-node-1 paas]# deactivate
```


## 部署login服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@ops ~]# cd /opt/opsany/.runtime/
[root@dev .runtime]# virtualenv login

# 使用Python虚拟环境
[root@dev .runtime]# source /opt/opsany/.runtime/login/bin/activate
(login) [root@dev .runtime]# cd /opt/opsany-paas/paas-ce/paas/login

# 安装依赖软件包
(login) [root@dev login]# pip install -r requirements.txt 
```

### 2.配置login

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。

```
(login) [root@ops login]# cd conf/
(login) [root@ops conf]# vim vim settings_development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_paas',
        'USER': 'paas',
        'PASSWORD': 'dev_paas',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
# cookie访问域
BK_COOKIE_DOMAIN = '192.168.0.101'
```

- 进行数据库初始化（如果遇到权限问题请检查数据库授权）
```
(login) [root@ops conf]# cd ..
(login) [root@ops login]# python manage.py migrate
```
#退出python虚拟环境
```
(runtime-login) [root@paas-node-1 login]# deactivate
```

## 部署appengine服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@dev conf]# cd /opt/opsany/.runtime/
[root@dev .runtime]# virtualenv appengine

# 使用Python虚拟环境
[root@paas-node-1 opt]# source /opt/opsany/.runtime/appengine/bin/activate

# 安装依赖软件包
(appengine) [root@ops paas-runtime]# cd /opt/opsany-paas/paas-ce/paas/appengine/
(appengine) [root@dev appengine]# pip install -r requirements.txt 
```

### 2.配置appengine

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
[root@paas-node-1 appengine]# vim controller/settings.py
(appengine) [root@ops appengine]# vim controller/settings.py 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_paas',
        'USER': 'paas',
        'PASSWORD': 'dev_paas',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

- 退出python虚拟环境
```
(appengine) [root@ops login]# python manage.py migrate
(appengine) [root@ops appengine]# deactivate
```


## 部署esb服务

### 1.初始化Python虚拟环境
```
# 创建Python虚拟环境
[root@ops ~]# cd /opt/opsany/.runtime/
[root@dev .runtime]# virtualenv esb

# 使用Python虚拟环境
[root@dev .runtime]# source /opt/opsany/.runtime/esb/bin/activate

# 安装依赖软件包
(esb) [root@dev .runtime]# cd /opt/opsany-paas/paas-ce/paas/esb/
(esb) [root@dev esb]# pip install -r requirements.txt 
```

### 2.配置esb

- 修改数据库配置，可以根据需求修改域名和端口，这里保持默认。
```
(esb) [root@ops esb]# cd configs/
(esb) [root@ops configs]# cp default_template.py default.py
(runtime-esb) [root@paas-node-1 configs]# vim default.py 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'open_paas',
        'USER': 'paas',
        'PASSWORD': 'open_paas',
        'HOST': 'localhost',
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


## 使用screen启动服务

   对于screen不熟悉的用户可以参考https://www.ibm.com/developerworks/cn/linux/l-cn-screen/index.html

### 启动paas
```
[root@paas-node-1 ~]# screen -t paas
[root@paas-node-1 ~]# source /opt/opsany/.runtime/paas/bin/activate
(runtime-paas) [root@paas-node-1 ~]# cd /opt/opsany-paas/paas-ce/paas/paas/
(runtime-paas) [root@paas-node-1 paas]# python manage.py runserver 0.0.0.0:8001
#按Ctrl+A+D退出screen

```
### 启动login
```
[root@paas-node-1 ~]# screen -t login
[root@paas-node-1 ~]# source /opt/opsany/.runtime/login/bin/activate
(runtime-login) [root@paas-node-1 ~]# cd /opt/opsany-paas/paas-ce/paas/login/
(runtime-login) [root@paas-node-1 login]# python manage.py runserver 0.0.0.0:8003
#按Ctrl+A+D退出screen
```

### 启动esb
```
[root@paas-node-1 ~]# screen -t esb
[root@paas-node-1 ~]# source /opt/opsany/.runtime/esb/bin/activate
(runtime-esb) [root@paas-node-1 ~]# cd /opt/opsany-paas/paas-ce/paas/esb/
(runtime-esb) [root@paas-node-1 esb]# python manage.py runserver 0.0.0.0:8002
#按Ctrl+A+D退出screen
```

### 启动appengine
```
[root@paas-node-1 ~]# screen -t appengine
[root@paas-node-1 ~]# source /opt/opsany/.runtime/appengine/bin/activate
(runtime-appengine) [root@paas-node-1 ~]# cd /opt/opsany-paas/paas-ce/paas/appengine/
(runtime-appengine) [root@paas-node-1 appengine]# python manage.py runserver 0.0.0.0:8000
#按Ctrl+A+D退出screen
```

## 生成环境使用supervisor进行启动

```
[root@ops ~]# cd /opt/dev-paas/paas-ce/paas/examples/supervisord.d/
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