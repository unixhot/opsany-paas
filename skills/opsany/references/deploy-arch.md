# OpsAny部署架构

## OpsAny部署架构

OpsAny整体上是有三部分组成：

- OpsAny平台：OpsAny平台由有两大部分组成：OpsAny PaaS平台和上面所有的SAAS平台应用。
- OpsAny-Proxy：OpsAny Proxy也有两大部分组成：1.自研的Proxy和集成的Zabbix、Prometheus。 2.其它集成的服务。
- OpsAny-Agent：OpsAny Agent是一个拥有独立的Python运行环境的Agent进程。同时又可以以插件的形式集成zabbix-agent和Node Exporter等。

默认部署完毕OpsAny平台后会自动部署一个内置的OpsAny Porxy，使用和OpsAny平台同样的MySQL、Redis，适合单一网络环境和主机数量规模较小的用户。当用户业务部署在不同的网络环境时，或者说主机数量超过万台，单台Proxy无法满足性能要求是，可以自行部署新的OpsAny Proxy。

![部署架构图](./static/deploy-arch.png)

### 多Proxy模式下的文件传输

很多同学有疑问，Proxy为啥必须要连接Server的8011和8012端口，这就要提到多Proxy模式下的文件如何进行同步，通常有以下几种模式：

- 文件分发：Server主动发到Proxy主机上。（Server需要判断目标主机所属Proxy，然后发送到对应的Proxy，发送有延迟，需要处理。）
- 文件共享：Server使用例如NFS的方式，将文件共享，所有Proxy挂载后，可以直接从“本地”进行文件读取。（配置复杂，而且NFS网络策略配置复杂。）
- 文件同步：Server使用例如Rsync的方式，将文件同步到所有Proxy上，所有Proxy，可以直接从本地进行文件读取。（同步有延迟，需要处理）
- OpsAny模式：用户上传的文件保存在Server上，Server通知Proxy来Server下载文件，Proxy通知Agent来Proxy下载文件。（逻辑简单，部署简单）

OpsAny模式的网络约束：
  OpsAny采用的模式类似于文件共享，但又不是传统的网络共享，这种模式最大的约束就是Proxy必须要访问到Server的端口，在某些场景下，就会不适用。例如将OpsAny部署在公司内网。然后分别在阿里云、腾讯云、华为云部署了Proxy，公司内网并没有固定的公网IP地址的时候，就无法进行文件传输。如果你有更完美的方案，欢迎在社区微信群提出来！

### 配置文件介绍

默认的部署路径：/data/opsany
安装后配置文件路径：/data/opsany/conf/该目录下有各个SaaS的SECRET_KEY，PaaS和SaaS的所有配置文件，所有容器的配置文件均在该目录下。像修改访问域名等需求，均是修改该目录下的相关配置文件完成的。






----
