# PaaS平台之统一登录

## 简介

login目录是统一登录服务的源码目录

主要作用是:
- 为蓝鲸智云所有平台和SaaS应用提供统一的用户身份认证和单点登录服务
- 支持蓝鲸智云所有用户统一管理和简单授权
- 支持蓝鲸智云统一登录对接企业内部登录体系

由统一登录模块和自定义接入企业登录模块两部分组成:

- 统一登录模块: 提供蓝鲸智云用户登录入口，用户信息管理和简单授权管理
- 自定义接入企业登录模块: 支持将蓝鲸智云统一登录对接企业内部登录体系，让用户使用企业内部的身份认证


## 技术栈

- framework: Django 1.8.11
- database: mysql


## 依赖服务

- mysql: 平台数据库
