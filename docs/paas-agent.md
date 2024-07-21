# PaaSAgent安装部署文档

> PaaSAgent 用于从SVN/Git拉取最新的代码，并进行部署和运行，是应用管理的代理服务，使用Golang编写，默认监听端口

## 系统要求

- Python版本: python2.7/python3.6.7
- Go
- Nginx
- Linux环境

## 安装部署
    PaaSAgent需要部署在满足系统要求的app服务器上。建议最少准备两台服务器，分别用于测试和正式环境。

### 1. 基础环境初始化

- CentOS

```
[root@linux-node1 ~]# yum install -y gcc glibc make zlib-devel openssl-devel curl-devel mysql-devel
```

- Ubuntu

```
apt install -y redis-server mariadb-server rabbitmq-server
```

**准备Python 2环境**
```
# 确认基础python环境是python2.7
[root@ops ~]# python --version
Python 2.7.15

# 执行以下命令确定python的安装路径
[root@ops ~]# which python

# 安装 virtualenv 及 预装包
[root@ops ~]# pip install -r /opt/opsany-paas/paas-ce/paasagent/etc/build/packages/requirements.txt
[root@ops ~]# pip install virtualenv virtualenvwrapper supervisor==3.3.3
```

**准备Python3环境**

```
[root@linux-node1 ~]# cd /usr/local/src
[root@linux-node1 src]# wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
[root@linux-node1 src]# tar zxf Python-3.6.8.tgz
[root@linux-node1 src]# cd Python-3.6.8/
[root@linux-node1 Python-3.6.8]# ./configure --prefix=/usr/local/Python-3.6.8 --enable-ipv6 --enable-optimizations
[root@linux-node1 Python-3.6.8]# make && make install
[root@linux-node1 Python-3.6.8]# ln -s /usr/local/Python-3.6.8/ /opt/py36
[root@linux-node1 Python-3.6.8]# cd /opt/py36/bin
[root@ops bin]# ln -s python3.6 python
[root@ops bin]# ln -s pip3 pip
```

确认Python版本
```
[root@ops ~]# /opt/py36/bin/python --version
Python 3.6.8
```

构建目录及新建用户
```
# 构建app的部署路径，用户可自定义
[root@ops ~]# export AGENT_ROOT=/opt/opsany-paas/paas-agent/
[root@ops ~]# mkdir -p $AGENT_ROOT

# 创建app进程的执行账户apps
[root@ops ~]# adduser apps
```

#### 2. 编译并安装PaaSAgent

```
# 确定已经安装好了golang并设置好了GOPATH
[root@ops ~]# yum install -y golang
[root@ops ~]# go version
go version go1.13.3 linux/amd64
[root@ops ~]# mkdir /opt/gopath
[root@ops ~]# export GOPATH=/opt/gopath/
[root@ops paas-ce]# mkdir -p $GOPATH/src

[root@ops ~]# cd /opt/dev-paas/paas-ce/
[root@ops paas-ce]# ln -s $PWD/paasagent $GOPATH/src/paasagent
[root@ops paas-ce]# cd $GOPATH/src/paasagent
[root@ops paasagent]# make
[root@ops paasagent]# mkdir -p $AGENT_ROOT/paas_agent /opt/dev-paas/paas-agent/logs
[root@ops paasagent]# cp -r bin etc $AGENT_ROOT/paas_agent/

# 更新配置文件
[root@ops paasagent]# cd $AGENT_ROOT/paas_agent/etc
[root@ops etc]# sed -i "s#TPL_AGENT_ROOT#${AGENT_ROOT}#g" paas_agent_config.yaml nginx/paasagent.conf
# build 和 buildsaas 中的 VIRTUALENVWRAPPER_PYTHON 变量需要设置正确的 python 路径，默认/usr/bin/python
[root@ops etc]# chmod +x build/virtualenv/build  build/virtualenv/saas/buildsaas

```

注意: `build` 和 `buildsaas` 中的 `VIRTUALENVWRAPPER_PYTHON` 变量需要设置正确的 python 路径，默认`/usr/bin/python`, 如果上一步`which python`的返回结果不是`/usr/bin/python`, 需要修改为对应正确的路径；如果用到了python3，`PYTHON3_PATH`也需要设置成正确的路径，默认`/opt/py36`

#### 3. 开发者中心注册服务器

开发者中心部署成功后, 访问`PAAS_DOMAIN`配置的域名，在**开发者中心->服务器信息**页面中，点击`添加服务器信息`按钮, 添加一台测试和正式app服务器。后台会自动生成服务器对应的`服务器ID(sid)`和`Token(stoken)`字段

注意: 开发者中心所在的服务器需要保证网络与app服务器互通

#### 4. 配置etc/paas_agent_config.yaml文件

```
auth:
  sid: 196f212f-0d27-41a2-851e-00d7ed08e3d8
  token: b8d3f955-b344-447f-a81c-aa07b9117f33
settings:
  CONTROLLER_SERVER_URL: 'http://dev.womaiyun.com' # App Engine地址
  BASE_PATH: '/opt/dev-paas/paas-agent/' # eg. /data/paas
  BASE_APP_PATH: '/opt/dev-paas/paas-agent/paas_agent'
  USE_PYPI: 'true'
  AGENT_LOG_PATH: '/opt/dev-paas/paas-agent/logs/agent.log'
  TEMPLATE_PATH: 'etc/templates'
  BUILD_PATH: 'etc/build'
  EXECUTE_TIME_LIMIT: 300
  PYTHON_PIP: 'http://pypi.douban.com/simple/'
port: 4245
ip: ''
```

#### 5. 启动PaaSAgent服务

```
# 直接启动PaaSAgent服务，或用supervisor等方式托管进程
[root@ops ~]# /opt/dev-paas/paas-agent/paas_agent/bin/paas_agent &
```
PaaSAgent启动后，日志记录在了`paas_agent_config.yaml`配置的`AGENT_LOG_PATH`文件中，如`/opt/dev-paas/logs/paas_agent/agent.log`，用户可通过日志内容查看服务状态

#### 6. 开发者中心激活服务器
PaaSAgent服务启动成功后，在**开发者中心->服务器信息**页面中，找到服务器**操作**栏中的激活按钮，激活服务器

#### 7. 部署nginx反向代理
```
[root@ops ~]# yum install -y nginx
[root@ops ~]# cd /opt/dev-paas/paas-agent/paas_agent/etc/nginx/
[root@ops nginx]# cp paasagent.conf /etc/nginx/conf.d/
[root@ops nginx]# systemctl restart nginx
```

注意：nginx建议以root用户启动，避免因文件权限导致访问异常，同时需要保证listen的端口和开发者中心注册的app服务端口一致


### 对应环境的数据库准备

不管是测试环境还是生产环境都需要使用数据库，我买云-技术运营中台使用了MongoDB和MySQL数据库。

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
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
MariaDB [(none)]> grant all on cmdb.* to cmdb@localhost identified by 'cmdb';
```

### 4.初始化MongoDB数据库
```
[root@paas-node-1 ~]# systemctl enable mongod && systemctl start mongod
[root@linux-node1 ~]# netstat -ntlp | grep 27017
tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      28513/mongod
[root@linux-node1 ~]# mongo
> use cmdb
switched to db cmdb
> db.createUser({user: "cmdb",pwd: "cmdb",roles: [ { role: "readWrite", db: "cmdb" } ]});
Successfully added user: {
	"user" : "cmdb",
	"roles" : [
		{
			"role" : "readWrite",
			"db" : "cmdb"
		}
	]
}
> exit

```
