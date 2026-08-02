# OpsAny SAAS应用架构

OpsAny SaaS应用是基于PaaS平台构建的各个独立的平台，可以使用PaaSAgent进行部署，也可以单独使用容器进行部署。

- 使用PaaSAgent部署SaaS平台（目前已经被弃用，仅用于开发和测试环境。）
- 使用独立容器部署SaaS平台（v2.0.0版本之后默认部署方式，适用于生产环境。）

## 独立容器部署SaaS（生产）

自v2.0.0之后，独立容器部署SaaS成为了默认的方式，独立容器部署SaaS的方式为单个SaaS平台独立启动，监听一个Web端口，然后通过Nginx将请求转发至该端口。

    案例：工作台访问

    监听端口：7002
    请求地址：/o/workbench
    请求转发：192.168.56.11:7002

为了方便后期运维进行配置优化和性能调优，在部署时，会将每个SaaS需要挂载的配置放置在'${INSTALL_PATH}/conf/opsany-saas/${APPID}'目录下。然后挂载到个各个SAAS平台容器中。

### SaaS配置介绍

SaaS的配置位于opsany-paas的代码仓库中，当SaaS启动时进行挂载，每个SaaS均有5个配置文件。

```
# 配置目录
[root@opsany-prod ~]# tree /opt/opsany/conf/opsany-saas/workbench/
/opt/opsany/conf/opsany-saas/workbench/
├── workbench-init.py         # 工作台workbench项目配置文件（修改访问域名时使用，记录了SaaS的APPID和Secret Key）
├── workbench-nginx.conf      # 请求转发到uwsgi的Nginx配置文件（通常不修改）
├── workbench-prod.py         # 工作台workbench项目配置文件（修改例如数据库配置时使用）
├── workbench-supervisor.ini。# 工作台workbench服务启动配置文件，配置主进程、Celery等进程（通常不修改）
└── workbench-uwsgi.ini       # 工作台workbench的uwsgi配置文件（性能调优时使用）

# 日志目录
ls /opt/opsany/logs/workbench
```

独立容器部署的SaaS的更新目前官方也提供了脚本，原理本质上是删除旧的容器，重新启动新的容器，并执行数据库更新操作。所以当遇到有SaaS平台不能正常运行，执行一次更新操作也是一种解决方案。

### SaaS的日常管理

- 1.SaaS的健康检查

  每个SaaS均对外开放健康检查接口。
    - 访问地址为https://DOMAIN_NAME/o/APPID/healthz/
    - 如统一权限的APPID为rbac，健康检查接口为：https://demo.opsany.com/o/rbac/healthz/
    
  由于该接口默认是对外公开的，如果您的平台部署在公网，请运维人员可以通过修改Nginx配置，从而修改接口的访问权限。

- 2.SaaS的日常运维

  每个SaaS平台都是一个独立的Docker容器，原则上有任何问题，只需要重启容器即可恢复。对于用户来说，除非是根据上述内容进行性能调优外，几乎是免运维的。

- 3.SaaS的升级更新

  OpsAny会定期发布新的版本，通过opsany-ce-update.sh脚本进行SaaS升级，该脚本升级的本质是删除旧的容器，重新启动新的容器，所以如果SaaS再遇到一些奇怪的问题，是可以通过更新脚本进行重建操作。

- 4.SaaS的数据备份

  SaaS容器不存储任何数据，日志是挂载的INSTALL_PATH（安装目录，默认/opt/opsany/）/logs，上传的数据是挂载INSTALL_PATH/uploads，其它数据保存在MySQL和MongDB数据库中，所以不存在单个SaaS的备份，应该是全平台备份，需要备份的有：MySQL、MongoDB、uploads目录。

### SaaS端口明细

所有SaaS在容器内部都监听的是80端口，通过Docker映射后，每个SaaS拥有独立的端口，用于访问入口（opsany-base-openresty容器中）Nginx进行负载均衡。

- 统一权限 (APPID: rbac）- 7001
- 工作台  （APPID: workbench）- 7002
- 资源平台（APPID: cmdb）- 7003
- 管控平台（APPID: control）- 7004
- 作业平台（APPID: job）- 7005
- 基础监控（APPID: monitor）- 7006
- 云管平台（APPID: cmp）- 7007
- 堡垒机  （APPID: bastion）- 7008
- 应用平台（APPID: devops）- 7009
- 代码仓库（APPID: dashboard）- 7010
- 流水线（APPID: pipeline ）- 7017
- 制品仓库（APPID: repo）- 7020
- 持续部署（APPID: deploy）- 7018

在实际工作中，你可以将SaaS部署在不同的主机上，仅需要修改Nginx的配置即可，同时需要保证uploads目录同步，例如可以使用NFS挂载等方式，官方建议是使用Kubernetes部署OpsAny。

## PaaSAgent部署SaaS（测试）

v2.0.0之前版本的SaaS的部署和更新，主要依靠PaaSAgent服务，PaaSAgent顾名思义是PaaS的Agent，是PaaS平台执行SaaS维护的一个Agent，一个PaaS平台可以有测试环境和正式环境的PaaSAgent。

### PaaSAgent简介

paasagent目录是PaaS平台中应用引擎(appengine)对应的agent模块源码目录

主要作用是:

- agent需要部署在应用服务器上
- 负责接收上层应用引擎(appengine)的请求指令，执行SaaS应用的部署和下架等任务操作(应用运行时环境的构建和进程托管)

技术栈：

- framework: labstack/echo
- python run time: virtualenv, uwsgi

依赖说明：

- paas: 使用内置应用时，从paas服务下载用户上传的saas部署包。
- appengine: 需要调用appengine的接口, 回写SaaS应用的部署日志。

### PaaSAgent模式的部署脚本原理

  当前该脚本已经归档，当你执行./saas-base-install.sh install都干了什么？

  1. 创建SaaS需要的MySQL数据库（所以，安装PaaS的时候需要安装MySQL客户端，就是为了执行初始化）
  2. 创建SaaS需要的MongoDB数据库（所以，安装PaaS的时候需要安装MongoDB客户端，也是为了执行初始化）
  3. 导入资源平台（CMDB）的内置模型。（所以，安装完毕之后，打开资源平台-资源模型，有很多内置的数据）
  4. 增加SaaS应用的环境变量到PaaS平台中。（SaaS的数据库等配置是保存在PaaS平台上，安装的时候从PaaS平台获取，然后以环境变量的形式传递给程序）
  5. 执行deploy.py进行SaaS部署。该脚本的本质就是帮你上传和点击部署按钮。

### SaaS包部署流程

不管是使用saas-base-install.sh调用deploy.py进行部署还是手工在开发中心-内置应用-进行部署，流程是一致的。
PaaSAgent会为每个SaaS创建Python虚拟环境，并且使用Supervisor+uwsgi启动，通过PaaSAgent的Nginx进行转发。所以PaaSAgent容器重启后，需要使用脚本手工启动所有的SaaS平台。

1. 点击上传按钮时，上传SaaS包。包会被保存到PaaS容器中的/opt/opsany/paas/paas/media/saas_files/目录下。
2. 点击部署按钮时，PaaSAgent从paas服务下载该文件，保存到paasagent容器的目录下。 具体paas的地址是在paas_agent_config.yaml中配置的PAAS_SERVER_URL参数获取。
3. paasagent在目录下创建对应saas的Python虚拟环境。
4. paasagent解压下载的saas包，并安装pkgs下所有的依赖包。
5. paasagent为saas创建一个supervisor服务，自动生成supervisor的ini配置文件。
6. paasagent通过supervisor启动saas服务。
7. 执行django migration操作。
