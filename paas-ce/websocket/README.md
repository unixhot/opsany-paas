# 管控平台后端工程

管控平台是OpsAny运维平台中用于节点纳管的模块，通过管控平台将节点纳管之后就可以在作业平台进行作业的执行。

### 节点管理

管控平台节点管理是通过salt-ssh执行salt-ssh 'nodename' state.sls 'agent.install'实现。

### 控制器管理

控制器管理是直接对接的SaltStack API。分别今天8011和8012端口。
- chreeypy 8011
- tonado 8012
目前使用的主要是8011端口。

### 部署文档

- [SaltStack 部署](docs/salt-deploy.md)
- [SaltStack 模块开发](docs/salt-dev.md)
- [SaltStack API接口](docs/salt-api.md)


## 堡垒机

基于[Guacamole](]http://guacamole.apache.org/)编写一个Guacamole CLient来实现，使用原生的[JS接口](http://guacamole.apache.org/doc/guacamole-common-js/)

![avatar](/docs/static/guac-arch.png)

