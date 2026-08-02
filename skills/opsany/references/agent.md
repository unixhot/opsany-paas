# 资源纳管指南

OpsAny的基本使用流程是：资源录入->资源纳管->资源管理，当你将资源都梳理完毕并录入之后，接下来就可以进行纳管（纳入OpsAny的管理）。本手册介绍【管控平台】的资源纳管使用和常见问题解答，OpsAny遵循（Server-Proxy-Agent）三层架构，默认安装OpsAny平台会自动部署一个内置的Proxy。

## OpsAny Proxy纳管原理

### Proxy网络连接

OpsAny支持多控制器（Proxy）模式，每个控制器负责管理本地区域的主机、网络设备和数据库等，所有的Proxy全部连接到OpsAny上。

Proxy监听端口：

  - 4505、4506: Agent模式服务监听端口
  - 8010: Proxy服务进程监听端口
  - 8011: OpenResty代理Proxy监听https端口
  - 8012: OpenResty代理Proxy监听的http端口。

主机纳管：

  - OpsAny平台需要连接到Proxy的8011端口。被纳管主机需要连接到Proxy的8011和8012端口（用于下载文件和脚本）。
  - SSH模式： Proxy需要连接到所有主机的22端口（目标被动模式）。
  - Agent模式： 所有主机需要连接到Proxy的4505和4506端口（目标主动模式）。

其它资源纳管：

  - Telnet协议：在网络设备纳管中，可能涉及到通过Telnet协议连接目标网络设备。
  - 数据库协议：在数据库纳管中，设计通过MySQL、Redis、MongoDB协议连接到目标实例中。

Proxy还需要连接到OpsAny平台获取用户上传的文件和脚本等，多Proxy模式如果有Proxy在公网，OpsAny平台是需要公网可以访问的。

### Proxy下的主机纳管

OpsAny的主机纳管支持以下四种方式：

- Agent：通过Agent进行纳管操作。
- SSH：通过SSH进行纳管操作
- Agent/SSH：双通道模式，Agent优先，首先判断Agent是否可以连接，正常即使用Agent进行执行。Agent异常，使用SSH进行执行。
- SSH/Agent：双通道模式，SSH优先，首先判断SSH是否可以连接，正常即使用SSH进行执行。SSH异常。使用Agent进行执行。

验证方式：

- 密码验证：密码验证，需要输入正确的用户名和密码。
- 密钥验证：密钥验证，需要提前放置好公钥。可以使用工作台自动生成密钥对，然后根据以下方法放置公钥的目标主机：
    - 1.在用户家目录创建 .ssh/authorized_keys文件，.ssh目录权限700 authorized_keys权限600
    - 2.将公钥写入"/root/.ssh/authorized_keys"或"/home/普通用户/.ssh/authorized_keys"
    - 3.使用凭据登录时用户名或者资源账号必须是对应的用户名

### 请求调用原理

例如用户在作业平台执行了一个快速脚本执行、文件分发、作业执行，调用链路如下：

【作业平台】-【ESB】-【管控平台】-【Proxy】-（通过SSH或者Agent）-【主机】

例如用户在资源平台执行了资产采集任务，调用链路如下：

【资源平台】-【ESB】-【管控平台】-【Proxy】-（通过SSH或者Agent）-【主机】

当出现问题时，也可以根据调用链路进行逐一故障诊断，管控平台和Proxy是整个执行的核心。

## OpsAny主机纳管操作

### Linux主机纳管

Linux主机支持SSH和Agent两种方式，SSH支持普通用户和root用户。Agent支持自动安装和手工安装，手工安装完毕之后，需要手工在“操作”也点击“纳管”。

- 强烈建议使用SSH密钥进行纳管，如果使用用户名/密码，那么如果用户名和密码发生变化，需要手工在管控平台进行更新。

#### Linux主机SSH密码纳管

SSH密码纳管，直接在【管控平台】-【主机管理】

在纳管主机时直接输入用户名和密码即可。注意如果使用普通用户，请提前配置好允许sudo。并开启sudo。

#### Linux主机SSH密钥纳管

1.登录Proxy主机创建SSH密钥对

```
# 进入Proxy容器 
docker exec -it opsany-paas-proxy /bin/bash

# 创建密钥对
ssh-keygen -t rsa 3072
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /root/.ssh/id_rsa
Your public key has been saved in /root/.ssh/id_rsa.pub
```

2.从Proxy上将密钥推送到目标主机

```
# 手工推送
ssh-copy-id root@192.168.56.11
```

3.在【工作台】-【个人设置】-【密钥管理】-上传私钥。

4.在【管控平台】-【主机管理】-配置选择对应的私钥。

#### Linux主机Agent纳管

Linux Agent纳管，支持自动部署Agent和手工部署Agent两种方式，如果遇到自动部署不成功的问题，可以选择手工部署。

- 自动部署Agent：该方式需要用户输入用户名/密码或者密钥。平台将自动连接目标主机执行脚本进行Agent安装。
- 手工部署Agent：该方式需要用户手工复制生成的命令，到目标主机进行执行。

### Windows主机纳管

Windows主机纳管仅支持Agent模式，需要用户提前手工在目标Windows主机上进行配置。

#### Windows主机SSH纳管（不支持）

暂不支持Windows的SSH纳管，后续版本会支持。

#### Windows主机Agent纳管

Windows Agent纳管需要手工在Windows主机安装Agent，请注意确保被纳管的Windows主机可以访问Proxy的4505和4506端口。
操作方法：管控平台-添加主机，操作系统选择Windoows，并选择Agent方式纳管。添加完毕后，在操作-更多中，可以有手工纳管选项，会出现手工安装Agent的命令。

如果你纳管的主机版本比较低，例如Windows 2003，可能需要手工安装早期版本的SaltStack，下载地址如下：
- https://mirrors.tuna.tsinghua.edu.cn/saltstack/windows/archive/
- Windows Server 2003建议使用2015.8版本。

## 主机纳管异常排查手册

### SSH异常排查手册

SSH通过Ansible进行纳管和连接测试，如果SSH异常，可以直接通过Ansible进行测试，查看日志。

异常原因统计：

- 主机无法访问，Ping不同。
- 主机可以访问，ping正常，但是端口不通。
- 主机IP和端口均正常，但是验证失败（密码验证失败、密钥验证失败）
- 主机IP和端口均正常，验证信息确定输入正确，可能SSH版本导致相关算法不支持。需要修改/etc/ssh/ssh_config配置支持 

以上几种异常，均可以通过下面的排查手段，查看到日志进行处理。

- 调整SSH参数支持老版本的SSH，例如CentOS 6

```
# 进入Proxy容器
docker exec -it opsany-paas-proxy /bin/bash
# 如果下面文件不存在，可以新建。
vi /etc/ssh/ssh_config
Host *
  HostKeyAlgorithms ssh-rsa,ssh-dss
  PubkeyAcceptedKeyTypes +ssh-rsa,ssh-dss
```

- 进入OpsAny Proxy容器。

```
# For Docker
docker exec -it opsany-paas-proxy /bin/bash

# For Kubernetes
kubectl exec -it PodName -n opsany -- /bin/bash
```

- 执行下面命令

```
# 执行Ansible进行测试是否可以正常通信。
ansible -vvv -i /opt/opsany-proxy/invscript_proxy.py 节点唯一标识 -m ping

# 执行Ansible测试获取数据。
ansible -vvv -i /opt/opsany-proxy/invscript_proxy.py 节点唯一标识 -m setup
```

### Agent异常排查手册

OpsAny的Agent是一个自定义封装好的Python环境，无需任何依赖，不需要主机已经安装Python，也不会对已经存在的Python环境有任何影响。默认安装在/usr/local/opsany-agent目录下，不可更改。使用Supervisor进行进程管理，会自动注册到Service或者Systemd系统服务中。并且仅支持Python3。不会对操作系统原有的Python环境产生任何影响，而且Agent也不存在内存泄露或者将CPU跑慢等情况，可以放心的进行安装。

#### Agent介绍

1.Agent包存放位置。

Agent的包存放在OpsAny Proxy（控制器）的/opt/opsany/uploads/agent目录下，该目录在OpenResty上设置了可以下载。

```
cd /opt/opsany/conf/nginx-conf.d
cat nginx_paas.conf
...
    location ~ ^/uploads/(.*) {
        autoindex off;
        root /opt/opsany/;
    }
...
```

> 如果你遇到了安装Agent的时候失败了，请检查你是否放置了agent的包到uploads目录下，在安装文档中有步骤，你可能少了。

2.Agent包构成

Agent是自定义的一个Python包，免安装直接解压即可，无需任何依赖。

### Agent纳管状态说明

Agent纳管是出现问题可能性比较多的方式，主要集中在网络配置的问题。下面为Agent的所有状态，请对照进行故障的排查。

- 正常： Agent连接正常，可以执行远程命令。
- 开始安装： 开始安装Agent，请确定需要提前部署Agent的包到upload下。
- 安装中：正在进行Agent安装操作。下一个状态为：安装成功或者安装失败。
- 安装成功： 安装脚本执行成功，一般不会显示该状态，会马上进入纳管操作。
- 安装失败： 安装脚本执行失败，一般是因为系统原因导致，需要重新安装或者人工处理失败。
- 纳管中： 开始接受Agent注册过来的Key，如果失败会重试1次。
- 纳管成功： 接受Agent的Key成功，一般不会显示该状态，会马上进行纳管操作。
- 纳管失败： 接受Agent的Key出现问题导致纳管失败，通常的原因如：主机的唯一标识重复。
- 异常： 上面所有操作都成功，但是Agent连接异常，一般造成该原因如：网络防火墙导致Agent无法连接Proxy的4505，4506端口、网络波动等。

#### OpsAny Agent管理

1.查看Agent状态

```
systemctl status opsany-agent
```

2.停止Agent

```
systemctl stop opsany-agent
```

3.查看Agent中插件状态

Agent的插件将被Agent以Supervisor的方式进行管理，这里单独有一个脚本封装了supervisorctl查看状态。

```
/usr/local/opsany-agent/agent.sh status
```

4.重启所有Agent服务

```
/usr/local/opsany-agent/agent.sh restart all
```

5.卸载Agent

```
/usr/local/opsany-agent/agent.sh remove
rm -rf /usr/local/opsany-agent/
```

6.手工安装的Agent如何自动发现？

手工安装的Agent起来之后会自动注册到Proxy，然后需要手工的在【管控平台】主机管理--操作（更多）--点击纳管操作进行主机纳管。纳管完毕待状态正常后，可以点击资产采集进行采集。

#### Agent异常排查步骤

1.管理纳管主机列表

```
列出所有Agent纳管的主机
# docker exec -it opsany-paas-proxy /bin/bash   
# salt-key
Accepted Keys:（该项下面是是已经纳管的主机）
Denied Keys: （该项下面是Agent已经连接上来，但是拒绝纳管的主机。）
Unaccepted Keys:（该项下面是Agent已经连接上来，但是还没有纳管的主机。）

移除某台主机的纳管
# salt-key -d 节点的ID名称

接受某台主机的纳管
# salt-key -i 'linux-node2'
```

2.查看连接到Proxy的Agent状态

```
# docker exec -it opsany-paas-proxy /bin/bash    
# salt '*' test.ping （查看所有Agent状态）
# salt 'linux-node1' test.ping  (查看指定Agent状态)
```

3.常见的Agent纳管异常原因

- 1.手工安装了agent但是salt-key中没有，请检查Agent的配置文件。有可能节点ID设置的和其它主机的节点ID相同导致，或者连接的Proxy地址不对。
- 2.执行salt-key未发现任何的主机，请检查是不是登录错了Proxy（如果你有多个Proxy的情况下）。
- 3.被纳管主机，重新安装过操作系统。这个时候正确的做法一定是先移除纳管，再重新纳管，而不是在老的主机上进行修改。


## 网络设备纳管

   管控平台网络设备纳管属于社区版测试功能，不建议生产使用，原因是网络设备厂商和型号众多，无法进行兼容，通常在企业版项目实施中进行调试和兼容。

## 数据库纳管

   OpsAny社区版v1.6.7开始支持MySQL、Redis数据库的纳管操作，通过MySQL和Redis的纳管，可以展示MySQL、Redis实例的基本信息，进行基本的页面操作。

## 堡垒机纳管

  堡垒机纳管和通过Proxy纳管主机、网络设备、数据库是完全不同的，彼此之间也毫无关系。例如你可能通过堡垒机可以成功纳管主机，但是通过控制器可能纳管失败。反之，你通过控制器纳管成功主机，通过堡垒机也可能失败。

  - 堡垒机纳管是通过opsany-paas-websocket容器。
  - 控制器纳管是通过opsany-paas-proxy容器。
  
  当堡垒机出现验证失败，最直接的测试办法就是，到opsany-paas-websocket中进行连接测试。通常有的操作系统因为SSH协议算法的问题可能会导致，无法连接的情况出现，和主机纳管类似。

```
# 进入Websocket容器
docker exec -it opsany-paas-websocket /bin/bash

# 手工进行网络和SSH连接测试
ping 192.168.56.11
ssh root@192.168.56.11
```

### 堡垒机授权

  堡垒机通过权限策略进行授权，管理员角色的用户默认可以看到所有的资源，普通用户角色的用户是需要通过堡垒机的访问策略进行授权，可以授权某个用户在某个时间范围的具体某个时间段内，以什么身份，登录什么目标主机。访问策略可以进行非常灵活的授权。

### Linux主机上传和下载文件

  Linux主机在右侧文件管理栏，默认仅展示用户家目录，进行上传和下载，如果需要上传到其它目录或者从其它目录下载，均需要将文件移动到用户家目录。（此限制是安全考虑）注意： 如果你安装了lrzsz的软件包。支持直接使用rz和sz进行上传和下载。

### Windows主机上传和下载文件。

  Windows主机，默认会在【我的电脑】创建一个网络盘，名称为： OpsAny上的Downloads，在页面右侧文件管理栏，上传的文件在该网络盘下面。如果需要从Windows主机下载文件到本地，也需要将文件复制或者移动到该共享盘下即可。注：早期版本在网络盘下面有一个Download的目录，新版本已经去掉了。


## 常见问题

### 纳管后修改密码为密钥

如果你之前已经使用了密码纳管成功了。现在想修改为密钥管理，可以直接使用以下方式

```
# docker exec -it opsany-paas-proxy /bin/bash
# ansible -i /opt/opsany-proxy/invscript_proxy.py 192.168.4.108 -m authorized_key -a "user=root state=present key={{ lookup('file', '/root/.ssh/id_rsa.pub') }}"
```

---
