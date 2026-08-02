---
name: opsany
description: 通过 opsany-mcp-server 连接 OpsAny 运维平台，实现 CMDB 资源查询和操作、模型管理、工单管理、用户管理、作业执行及主机纳管等全栈运维操作。
---

# OpsAny

## 1. 概述

OpsAny SKILL 通过 opsany-mcp-server（MCP Server 协议）连接 OpsAny 平台，将 AI 对话能力与企业级运维平台打通。支持对配置管理数据库（CMDB）、作业平台、统一权限、基础监控、应用监控、事件中心、知识库等九大 SaaS 服务的数据查询与操作，覆盖日常运维工作。

### 核心能力

- **工作台（ITSM）**：运维工作台，支持自定义工单流程、自定义工单（表单、字段设计），是企业服务流程管理的入口。
- **堡垒机**：运维堡垒机，支持 4A 审计，是企业手工运维的入口也是企业安全等保建设必备产品。
- **资产管理（CMDB）**：查询资产模型、字段定义及实例数据，管理资产间的关联与从属关系。支持创建/修改/删除资源模型及其字段。
- **管控平台**：自动添加主机至管控平台，完成对运维对象的纳管操作，通过 SSH 或者 Agent 两种方式进行控制，配置监控插件（Zabbix/Prometheus）及堡垒机同步。
- **作业执行**：通过 ID 或脚本内容执行作业，支持 Shell/Python 等脚本类型，并获取执行结果。支持将脚本存入脚本仓库。
- **基础监控**：完成对运维对象的多层级监控工作，目前采集器采用 Zabbix。
- **应用监控**：基于 Prometheus 的组件监控和服务拨测告警。
- **事件中心**：统一的告警事件管理，聚合 Prometheus、Zabbix 及第三方告警。
- **统一权限（RBAC）**：查询与管理平台用户信息（需管理员权限）。
- **知识库（KBase）**：管理运维知识库文章和文档。
- **云管平台**：多云统一管理，支持阿里云、腾讯云、华为云、AWS、金山云，资产自动导入至 CMDB（资源平台）。

## 2. 配置管理

### MCP 服务器配置

请在 MCP 客户端配置文件中添加以下配置，替换对应环境变量。

```json
{
  "mcpServers": {
    "opsany-mcp-server": {
      "url": "http://${DOMAIN_NAME}:8020/sse",
      "headers": {
        "username": "admin",
        "user-api-token": "${USER_ACCESS_TOKEN}",
        "mcp-auth-token": "${MCP_AUTH_TOKEN}"
      }
    }
  }
}
```

**参数说明：**

- `DOMAIN_NAME`：OpsAny 平台的访问域名或 IP 地址。
- `USER_ACCESS_TOKEN`：登录平台后，在"工作台 -> 个人设置 -> API Token"中创建。
- `MCP_AUTH_TOKEN`：MCP Server 配置文件中的认证 Token（默认路径：`/data/opsany/conf/opsany-paas/mcp-server/config.yaml`）。

## 3. 工具明细（Tools）

### 3.1 资源平台（CMDB）

用于管理 IT 资源模型与数据。

**资源实例操作：**

- `opsany_cmdb_api_resources`：获取全部资源模型（类型、分组、标识等）。传 `output=extend` 可获取实例总数和字段总数。
- `opsany_cmdb_get_resource_fields`：获取指定资源模型的字段详情（类型、配置）。创建/修改数据前必须调用。
- `opsany_cmdb_get_resource`：查询资源实例数据，支持分页、关键词搜索、指定返回字段。
- `opsany_cmdb_get_resource_link_inst_count`：获取资源的关联/从属关系实例总数。
- `opsany_cmdb_get_resource_link_inst_list`：获取资源指定关联关系的数据列表。
- `opsany_cmdb_get_can_add_link_inst_list`：查询可添加的关联关系数据列表（已过滤已添加数据）。
- `opsany_cmdb_resource_add_link_inst`：为资源添加关联关系数据。
- `opsany_cmdb_resource_remove_link_inst`：移除资源的关联关系数据。
- `opsany_cmdb_create_resource`：创建新的资源数据（需先拉取字段信息）。
- `opsany_cmdb_update_resource`：更新资源数据。
- `opsany_cmdb_delete_resource`：删除资源数据。

**资源模型管理（元数据）：**

- `opsany_cmdb_get_model_group`：获取资源模型分组，用于创建模型时选择分组。
- `opsany_cmdb_get_model`：获取资源模型列表，获取模型 code 后可进行字段管理。
- `opsany_cmdb_create_model`：创建资源模型，创建后需创建属性（字段）才可写入数据。支持克隆已有模型字段。
- `opsany_cmdb_update_model`：修改资源模型名称、分组和是否内置。
- `opsany_cmdb_delete_model`：删除资源模型（仅当模型无数据时可删除）。
- `opsany_cmdb_create_model_fields`：创建资源模型属性（字段），支持 str/int/float/date/dropDown 等类型，详见字段说明附录。
- `opsany_cmdb_update_model_field`：修改资源模型字段名称、分组和配置。
- `opsany_cmdb_delete_model_field`：删除资源模型字段（删除后该字段数据也会被清空）。

### 3.2 统一权限（RBAC）

用于管理平台用户。

- `opsany_rbac_get_or_search_all_user`：获取或搜索全部用户信息（需管理员权限）。
- `opsany_rbac_get_my_user_info`：获取当前登录用户信息。
- `opsany_rbac_create_user`：批量创建用户（管理员权限，仅支持创建普通用户）。
- `opsany_rbac_update_user`：批量更新用户状态（启用/禁用）。
- `opsany_rbac_delete_user`：批量删除用户（管理员权限，仅支持删除普通用户或被禁用的用户）。

### 3.3 基础监控（Monitor）

- `opsany_monitor_alert_info`：获取 Zabbix 基础监控告警信息，支持按主机、级别（严重/警告等）筛选。

### 3.4 应用监控（Prometheus）

- `opsany_prom_alert_info`：获取应用监控平台的实例告警，包括 Prometheus 组件监控实例告警和服务拨测告警。

### 3.5 事件中心（Event）

- `opsany_event_alert_info`：获取事件中心告警（待处理、处理中、已关闭），聚合 Prometheus、Zabbix 及第三方告警。

### 3.6 工作台/ITSM（Workbench）

用于工单服务管理。

- `opsany_workbench_work_order_inst`：查询工单实例（全部、待办、已办、我提交的）。
- `opsany_workbench_work_order_folder`：获取全部服务分类，用于搜索指定分类下的工单。
- `opsany_workbench_work_order_temp`：获取服务目录及表单字段（用于提单）。
- `opsany_workbench_work_order_submit`：提交新工单。

### 3.7 作业平台（Job）

用于脚本与作业执行。

- `opsany_job_get_tool_market_list`：获取工具市场（作业/脚本列表）。
- `opsany_job_get_job_list`：获取可执行的作业列表。
- `opsany_job_get_script_list`：获取脚本列表。
- `opsany_job_run_job_by_id`：根据 ID 执行作业，返回任务 ID。
- `opsany_job_run_script_by_id`：根据 ID 在指定主机上执行脚本。
- `opsany_job_run_script_by_script`：直接输入脚本内容和主机信息执行脚本。
- `opsany_job_create_script_library`：创建脚本到脚本仓库（仅支持私有脚本）。
- `opsany_job_get_run_result_by_log_id`：根据任务 ID 获取执行结果。

### 3.8 管控平台（Control）

用于主机纳管与环境配置。

- `opsany_control_get_managed_host_list`：获取已纳管主机列表。
- `opsany_control_get_controller_list`：获取控制器（Proxy）列表。
- `opsany_control_get_host_group_list`：获取主机分组列表。
- `opsany_control_get_zabbix_list`：获取 Zabbix 实例列表。
- `opsany_control_get_prometheus_list`：获取 Prometheus 实例列表。
- `opsany_control_get_dashboard_list`：获取监控大屏列表。
- `opsany_control_get_zabbix_temp_list`：获取 Zabbix 模板列表。
- `opsany_control_create_host`：**核心操作**，添加主机纳管，支持配置 SSH/Agent、监控插件及堡垒机同步。

### 3.9 知识库（KBase）

用于管理运维知识库文章和文档。

- `opsany_kbase_read_kbase_list`：获取知识库平台全部知识库列表。
- `opsany_kbase_read_kbase_article`：获取某一知识库内的文章和文档，支持列表查看和单条获取。

## 4. 场景案例

### 4.1 资源深度查询（CMDB）

**场景：** 查询特定业务模型下的主机资源，并查看其关联的网络设备。

**步骤：**

1. **发现模型**：调用 `opsany_cmdb_api_resources`，筛选 `resource_type` 为 `yw`（业务模型），找到目标业务的 `model_code`。
2. **查询资源**：使用 `opsany_cmdb_get_resource`，传入 `model_code` 和搜索关键词（如主机 IP），获取主机 ID（`resource_id`）。
3. **查看关联**：
   - 调用 `opsany_cmdb_get_resource_fields` 获取该模型的字段，找到 `is_relationship_field=2`（关联关系）的字段 `field_code`。
   - 调用 `opsany_cmdb_get_resource_link_inst_list`，传入主机 ID 和 `field_code`，获取关联的网络设备列表。

### 4.2 批量纳管主机（管控平台）

**场景：** 将一批新服务器添加到运维平台，并自动安装监控插件。

**步骤：**

1. **环境准备**：
   - 调用 `opsany_control_get_controller_list` 获取 `controller_id`。
   - 调用 `opsany_control_get_host_group_list` 获取目标分组 `group_id`。
   - 调用 `opsany_control_get_zabbix_list` 获取 `controller_zabbix` ID。
2. **执行纳管**：调用 `opsany_control_create_host`。
   - 构造 `host_info_list` 数组，包含多台主机信息。
   - 配置 `monitor_type` 为 `Zabbix`。
   - 设置 `reinstall_zabbix_agent` 为 `true`。
   - 填写 `controller_zabbix` 和 `template_list`（Zabbix 模板 ID 列表）。

### 4.3 创建自定义资源模型（CMDB 模型管理）

**场景：** 为新的业务类型创建一个自定义资源模型并添加字段。

**步骤：**

1. **获取分组**：调用 `opsany_cmdb_get_model_group` 获取模型分组 code。
2. **创建模型**：调用 `opsany_cmdb_create_model`，传入 `code`（如 `NEW_SERVER`）、`name`、`model_type`、`model_group` 创建模型。
3. **获取字段分组**：调用 `opsany_cmdb_get_resource_fields` 获取模型的字段分组 code（`field_group_code`）。
4. **添加字段**：调用 `opsany_cmdb_create_model_fields` 逐个创建字段，指定 `type_name`（如 `str`、`int`、`dropDown`）和 `attribute` 配置（默认值、校验规则、下拉选项等）。
5. **写入数据**：调用 `opsany_cmdb_create_resource` 在该模型下创建实例数据。

### 4.4 远程执行脚本并获取结果（作业平台）

**场景：** 直接在对话中编写并执行运维脚本，获取执行结果。

**步骤：**

1. **执行脚本**：调用 `opsany_job_run_script_by_script`，传入 `script`（脚本内容）、`server`（目标主机 IP）、`script_type`（如 `sh` 或 `py`），获取返回的 `log_id`。
2. **查询结果**：调用 `opsany_job_get_run_result_by_log_id`，传入 `log_id` 获取执行日志和结果。

### 4.5 查看告警和提交工单（监控 + ITSM）

**场景：** 查看当前告警，针对告警主机提交维修工单。

**步骤：**

1. **查看告警**：
   - 调用 `opsany_monitor_alert_info` 或 `opsany_prom_alert_info` 获取告警列表，按 `severity` 筛选严重级别。
   - 或调用 `opsany_event_alert_info` 获取聚合后的全部告警。
2. **查看服务目录**：调用 `opsany_workbench_work_order_temp` 获取服务目录，找到维修类服务 ID。
3. **提交工单**：调用 `opsany_workbench_work_order_submit`，传入 `work_order_id` 和 `field_dict` 表单内容提交工单。

### 4.6 查询知识库文档（KBase）

**场景：** 搜索与故障处理相关的知识库文章。

**步骤：**

1. **获取知识库列表**：调用 `opsany_kbase_read_kbase_list` 获取全部知识库，找到目标知识库的 `unique_code`。
2. **搜索文章**：调用 `opsany_kbase_read_kbase_article`，传入 `kbase`（知识库唯一标识）和搜索条件获取相关文档内容。

## 5. 常用工作流速查

| 目标 | 推荐工具 |
|------|---------|
| 查看平台有哪些资源模型 | `opsany_cmdb_api_resources` |
| 查询某类资源的具体数据 | `opsany_cmdb_get_resource` |
| 查看资源间的关联关系 | `opsany_cmdb_get_resource_link_inst_list` |
| 创建自定义资源模型 | `opsany_cmdb_get_model_group` → `create_model` → `create_model_fields` |
| 纳管新主机 | `opsany_control_get_controller_list` → `get_host_group_list` → `create_host` |
| 远程执行 Shell 脚本 | `opsany_job_run_script_by_script` → `get_run_result_by_log_id` |
| 查看平台全部告警 | `opsany_event_alert_info` |
| 提交 IT 服务工单 | `opsany_workbench_work_order_temp` → `work_order_submit` |
| 查询用户信息 | `opsany_rbac_get_or_search_all_user` |
| 搜索知识库文档 | `opsany_kbase_read_kbase_list` → `read_kbase_article` |

## 6. 相关资源

- [OpsAny 官网](https://www.opsany.com/)
- [OpsAny 官方文档](https://docs.opsany.com/)
- [MCP 协议文档](https://spec.modelcontextprotocol.io/)
