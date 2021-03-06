# PaaS平台社区版之API网关

## 简介

API网关是PaaS平台中的API接口服务总线。它将底层原子平台或第三方系统接口，以自助对接的方式或编码的方式封装成一个个原子组件，以统一的云API规范为上层SaaS应用提供API服务。esb目录是API网关的源码目录。

API网关的主要作用是：

- 为SaaS应用开发者提供蓝鲸官方服务云API
- 为管理员提供自助接入API到API网关的服务
- 为管理员提供网关管理入口
- 提供组件开发模板，支持编码形式开发API组件对接API网关

## 技术栈

- framework: Django 1.8.11
- database: mysql
- cache: redis

## 依赖说明

- mysql: 平台数据库
- redis: 缓存服务
- login: 调用统一登录服务接口，判定用户登录态
- paas: 访问PaaS平台数据库，认证SaaS应用

## 支持的组件列表

项目默认支持的蓝鲸官方系统组件列表：

- bk_login: 统一登录
- bk_paas: 蓝鲸PaaS平台
- cc: 配置平台
- fta: 故障自愈
- sops: 标准运维

如要使用这些系统的组件，需要在项目配置文件 configs/default.py 中更新对应系统的服务域名地址
