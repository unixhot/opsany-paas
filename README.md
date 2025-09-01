# OpsAny运维PAAS平台

OpsAny-PaaS是基于腾讯开源[bk-PaaS](https://github.com/Tencent/bk-PaaS) 二次开发的运维开发平台，让运维开发者可以方便快捷地创建、开发、部署和管理运维SaaS应用。**你可以把PaaS看作是Spring CLoud这样的开发框架**，它提供了应用引擎、前后台开发框架、API网关、统一登录、公共组件等模块，帮助用户快速、低成本、免运维地构建支撑工具和运营系统（统称为SaaS应用），它为一个SaaS应用从创建到部署，再到后续的维护管理提供了完善的自动化和自助化服务，从而使开发者可以集中精力关注SaaS应用的逻辑开发。

> 如果你正在使用Python Django框架进行开发工作，几乎可以零成本的切换到PaaS上来，不要怀疑，现在就部署进行实践吧。

## 变更介绍

我们在bk-PaaS的基础上做了以下修改和变更：

- 升级Python2到Python 3.12。
- 升级Django1.8到Django 4.2.16。
- 修改了appengine的saas应用上传和部署逻辑，支持指定SAAS的Secret Key，不使用白名单机制。
- 修改了login部分逻辑，用于和统一权限配合，增加MFA，移动端适配等。
- 修改了paasagent的agent代码，增加了配置参数，修改了默认的SAAS配置文件。
- 增加了esb的API接口等。
- 增加了MFA、多语言、动态主题等。
- 增加WebSocket功能，用于堡垒机底层通信。
- 增加了容器化部署支持和一键部署脚本。
- 增加了OpsAny前后端开发框架，前端基于Vue3.0。

## 我们提供的产品和服务

1. 【产品】OpsAny数字化运维平台，你可以理解OpsAny是：轻量级腾讯蓝鲸平台。
2. 【服务】提供开源软件源代码级别商业技术支持。

## 代码结构

源码组成如下：

```
paas-ce
├── paas 包含4大服务（python、Django）
│   ├── appengine  应用引擎 端口：8000
│   ├── esb        API网关 端口：8002
│   ├── login      统一登录服务 端口：8003
│   └── paas       开发中心&web工作台 端口：8001
└── paasagent      应用引擎Agent (golang) 端口：4245 Nginx：8085
└── websocket      堡垒机服务 端口：8004
```

## Docker容器在线部署

> 仅部署PaaS平台需要2C、4G内存的主机，部署OpsAny SaaS需要4C、8G内存的干净主机。生产使用推荐8C、16G内存。请检查是否关闭了SELinux和防火墙！

1. 安装Docker和初始化使用的软件包

- 【CentOS 7】部署

  安装Docker和MySQL客户端

  ```
  curl -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
  curl -o /etc/yum.repos.d/docker-ce.repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  yum install -y git wget docker-ce mariadb jq python3 python3-pip python3-devel ntpdate
  systemctl enable --now docker
  ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
  ntpdate time1.aliyun.com
  ```

- 【CentOS 8】部署

  安装Docker和MySQL客户端

  ```
  dnf config-manager --add-repo=http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  dnf -y install docker-ce --nobest
  dnf -y install mariadb jq git
  systemctl enable --now docker
  ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
  ```

- 【Ubuntu】 部署

    安装Docker和MySQL客户端

    ```
    # step 1: 安装必要的一些系统工具
    sudo apt-get update
    sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common
    # step 2: 安装GPG证书
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
    # Step 3: 写入软件源信息
    sudo add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
    # Step 4: 更新并安装Docker-CE
    sudo apt-get -y update
    sudo apt-get -y install docker-ce jq wget mysql-client git ntpdate
    systemctl enable --now docker
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    ntpdate time1.aliyun.com
    ```

2. 选择一个代码仓库克隆代码

```
# Gitee
cd /opt && sudo git clone https://gitee.com/unixhot/opsany-paas.git

# Github
cd /opt && sudo git clone https://github.com/unixhot/opsany-paas.git
```

3. 修改配置文件

> 注意！注意！注意！切记修改install.config中所有的IP地址，可以批量查找替换。

```
cd /opt/opsany-paas/install && cp install.config.example install.config
vim /opt/opsany-paas/install/install.config

# 安装OpsAny的本机内网IP地址。请批量查找替换将192.168.56.11修改为部署OpsAny的本机IP地址。
LOCAL_IP="192.168.56.11"

# 访问OpsAny PaaS的域名，如果是在内网访问请修改为和LOCAL_IP一样，如果是外网访问，请修改为真实访问的域名或者公网IP。
安装后暂不支持修改，此配置会作为Cookie的作用域的域名，所以如果配置的和访问的不同，会导致无法通过验证。官方文档中有修改域名的办法。
DOMAIN_NAME="192.168.56.11"
```

4. 执行安装脚本进行PAAS平台部署

```
cd /opt/opsany-paas/install/
./paas-install.sh 
```

5. 访问域名测试，默认用户名admin 密码admin

  http://192.168.56.11/

> 再次强调，访问的地址和在install.config中配置的DOMAIN_NAME必须一致，不一致无法登录。

6. 验证PAAS部署

- 访问平台：查看【开发中心】-【服务器信息】 查看状态
- 访问平台：查看【开发中心】-【第三方服务】 查看状态


## 下载OpsAny社区版本

安装完毕OpsAny PaaS之后，就可以进行运维开发工作了，不过PaaS仅仅是一个开发平台，并没有任何运维功能。你也可以继续部署OpsAny社区版本，进行日常运维工作，OpsAny社区版是OpsAny产品团队，自主研发的智能运维平台：支持自定义插件，支持用户使用Python、Shell、Powershell编写例如工具脚本、资产采集插件、智能巡检插件、指标采集插件等。

> OpsAny社区版本v2.2.1正式发布 >> [免费下载](https://opsany.com/#/download)

