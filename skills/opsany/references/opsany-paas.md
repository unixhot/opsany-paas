#OpsAny平台PaaS架构

## PaaS平台中的paas服务

paas服务是PaaS平台中的开发者中心及web工作台的功能。

主要作用:

- 为SaaS应用使用者提供访问SaaS应用入口
- 为SaaS应用开发者提供开发及管理SaaS应用的功能
- 为平台管理员提供用户管理入口

由web工作台和开发者中心两部分组成:

- web工作台: 已发布SaaS的应用列表, 作为统一的入口, 并且包含一系列常用链接等, 同时管理员可以进行用户管理
- 开发者中心: 包含SaaS应用创建/部署/下架等功能入口, 同时可以对服务器信息/第三方服务信息等进行管理, 同时包含SaaS开发必须的文档及资源下载入口

**技术栈**

- framework: Django 1.8.11
- template: mako
- database: mysql

**依赖说明**

- mysql: 平台数据库
- appengine: 需要调用appengine接口, 进行应用部署、下架等操作
- login: 调用统一登录服务接口, 判定用户登录态

## PaaS平台中的login服务

login服务是统一登录服务

主要作用是:
- 为PaaS平台和SaaS应用提供统一的用户身份认证和单点登录服务
- 支持所有用户统一管理和简单授权
- 支持统一登录对接企业内部登录体系

由统一登录模块和自定义接入企业登录模块两部分组成:

- 统一登录模块: 提供用户登录入口，用户信息管理和简单授权管理
- 自定义接入企业登录模块: 支持将PaaS统一登录对接企业内部登录体系，让用户使用企业内部的身份认证


**技术栈**

- framework: Django 1.8.11
- database: mysql


**依赖服务**

- mysql: 平台数据库

## PaaS平台中的Appengine

appengine目录是PaaS平台中, 负责托管 SaaS 应用的后台服务模块（应用引擎）源码目录。

主要作用是:

- 提供SaaS应用生命周期的管理功能，包括提测、上线、下架等，与PaaSAgent交互
- 提供SaaS应用依赖的第三方服务的管理功能，包括服务申请，服务配置等

**技术栈**

- framework: Django 1.8.11
- database: mysql

**依赖说明**

- paasagent: 需要调用paasagent接口, 完成对SaaS应用生命周期的管理功能
- mysql: 平台数据库

## PaaS平台中的ESB

ESB是PaaS平台中的API接口服务总线。它将底层原子平台或第三方系统接口，以自助对接的方式或编码的方式封装成一个个原子组件，以统一的云API规范为上层SaaS应用提供API服务。esb目录是API网关的源码目录。

API网关的主要作用是：

- 为SaaS应用开发者提供API
- 为管理员提供自助接入API到API网关的服务
- 为管理员提供网关管理入口
- 提供组件开发模板，支持编码形式开发API组件对接API网关

**技术栈**

- framework: Django 1.8.11
- database: mysql
- cache: redis

**依赖说明**

- mysql: 平台数据库
- redis: 缓存服务
- login: 调用统一登录服务接口，判定用户登录态
- paas: 访问PaaS平台数据库，认证SaaS应用
