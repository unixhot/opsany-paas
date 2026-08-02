# OpsAny MCP Server

基于 OpsAny 平台的 MCP (Model Context Protocol) Server，提供通过 MCP 协议访问 OpsAny 平台资源、工单、脚本等能力。

## 功能特性

OpsAny MCP Server 提供了以下功能平台的 API 工具，按平台分类如下：

### CMDB（配置管理数据库/资源平台）
- **opsany_cmdb_api_resources**: 资源平台，获取全部资源模型, 包括资源类型名称，资源类型标识，资源分组名称，资源分组标识，资源名称，资源标识，资源简称，资源实例总数，字段总数, 当不要求获取资源实例总数，字段总数时output为空！
- **opsany_cmdb_get_resource_fields**: 资源平台，获取指定资源的字段信息，获取资源仓库数据，创建修改资源仓库数据时需要拉取字段信息。
- **opsany_cmdb_get_resource**: 资源平台，获取资源仓库数据。
- **opsany_cmdb_get_model_group**: 资源平台，获取资源模型分组(创建模型时使用)。
- **opsany_cmdb_get_model**: 资源平台，获取资源模型列表。
- **opsany_cmdb_create_model**: 资源平台，创建资源模型，创建资源模型后创建属性(字段)就可以在资源仓库创建该模型数据！
- **opsany_cmdb_update_model**: 资源平台，修改资源模型，支持修改名称分组和是否内置！
- **opsany_cmdb_delete_model**: 资源平台，删除资源模型，谨慎删除，当模型没有数据才可以删除！
- **opsany_cmdb_create_model_fields**: 资源平台，创建资源模型属性(字段)，仅支持创建普通字段。
- **opsany_cmdb_update_model_field**: 资源平台，修改资源模型属性(字段)，支持修改名称分组和是否内置。
- **opsany_cmdb_delete_model_field**: 资源平台，删除资源模型字段，谨慎删除，删除后该模型当前字段数据也会被清空！
- **opsany_cmdb_get_resource_link_inst_count**: 资源平台，获取某一资源的所有关联关系数据字段和实例总数，包括从属关系(is_relationship_field=1)和关联关系(is_relationship_field=2)！
- **opsany_cmdb_get_resource_link_inst_list**: 资源平台，获取资源仓库某一数据的指定关联关系字段数据列表。
- **opsany_cmdb_get_can_add_link_inst_list**: 资源平台，添加资源的关联关系数据时，拉取指定关联关系字段的待添加数据列表(拉取关联关系对端模型数据，已过滤添加过的数据)。
- **opsany_cmdb_resource_add_link_inst**: 资源平台，资源仓库给指定数据添加关联关系数据。
- **opsany_cmdb_resource_remove_link_inst**: 资源平台，资源仓库给指定数据移除关联关系数据。
- **opsany_cmdb_create_resource**: 资源平台，资源仓库新建数据，需要获取该模型字段后整理数据, 创建普通字段需要将字段数据写入data。
- **opsany_cmdb_update_resource**: 资源平台，资源仓库修改数据，需要获取该模型字段后整理数据，修改普通字段需要将字段数据写入data！
- **opsany_cmdb_delete_resource**: 资源平台，资源仓库删除数据，需要传入资源ID。

### RBAC（统一权限平台）
- **opsany_rbac_get_or_search_all_user**: 统一权限平台，获取平台全部用户信息，仅支持管理员用户查看，普通用户可能会返回没有操作权限；支持用户名精准查找，中文名精准查找，用户名模糊搜索，中文名称模糊搜索，中文名或用户名联合模糊搜索，支持扩展字段，包括部门用户认证来源等全部字段，使用 all。
- **opsany_rbac_get_my_user_info**: 统一权限平台，获取自己的用户信息，当前用户信息，我是谁，支持扩展字段，包括部门用户认证来源等全部字段，使用 all。
- **opsany_rbac_create_user**: 统一权限平台，批量创建用，仅支持管理员用户操作，普通用户可能会返回没有操作权限；仅支持创建普通用户，创建管理员请前往统一权限平台操作！
- **opsany_rbac_update_user**: 统一权限平台，批量修改用户，仅支持管理员用户操作，普通用户可能会返回没有操作权限；仅支持修改普通用户信息，暂时仅支持修改启用禁用。
- **opsany_rbac_delete_user**: 统一权限平台，批量删除用户，仅支持管理员用户操作，普通用户可能会返回没有操作权限；仅支持删除普通用户，和被禁用的用户。

### Monitor（基础监控）
- **opsany_monitor_alert_info**: 基础监控，获取基础监控平台的实例告警，需要管控平台监控并纳管后，实例包括管控平台主机，网络设备！

### Workbench（工作台/ITSM）
- **opsany_workbench_work_order_inst**: 工作台，ITSM平台，获取全部工单，待办工单，我的已办工单，我提交的工单！
- **opsany_workbench_work_order_folder**: 工作台，ITSM平台，获取全部服务分类，用来搜索指定分类下的工单！
- **opsany_workbench_work_order_temp**: 工作台，ITSM平台，获取全部服务目录，包含全部服务，用来提单使用，会拉取授权的全部服务和服务相关字段！
- **opsany_workbench_work_order_submit**: 工作台，ITSM平台，提单，根据opsany_workbench_work_order_temp拉取到的服务id和表单字段(field_list)提单！

### Job（作业平台）
- **opsany_job_get_tool_market_list**: 作业平台 获取作业平台工具市场，包括作业列表和脚本列表！
- **opsany_job_get_job_list**: 作业平台 获取作业平台作业列表，只需要作业ID就可以执行的作业列表！
- **opsany_job_get_script_list**: 作业平台 获取作业平台脚本列表，该脚本执行需要脚本ID执行主机等参数！
- **opsany_job_run_job_by_id**: 作业平台 根据作业ID执行作业， 返回的为任务ID, 可以根据任务ID获取执行结果, 根据返回的字段flag判断是否执行完成 True: 完成 False: 未完成。
- **opsany_job_run_script_by_id**: 作业平台 根据脚本ID执行脚本， 返回的为任务ID, 可以根据任务ID获取执行结果！
- **opsany_job_run_script_by_script**: 作业平台 输入脚本内容和主机信息执行脚本，返回任务ID，可根据任务ID获取执行结果！
- **opsany_job_create_script_library**: 作业平台，创建脚本到脚本仓库，仅支持创建私有脚本！
- **opsany_job_get_run_result_by_log_id**: 作业平台 获取执行的作业或脚本结果， 根据返回的任务ID获取！

### Control（管控平台）
- **opsany_control_get_managed_host_list**: 管控平台 获取管控平台纳管的主机列表，该数据来自资源平台主机组内三个模型的数据(SERVER,CLOUD_SERVER,VIRTUAL_SERVER)！
- **opsany_control_get_controller_list**: 管控平台 获取管控平台控制器(Proxy)列表，纳管主机时使用，将主机纳管在该控制器下。
- **opsany_control_get_host_group_list**: 管控平台 获取管控平台主机分组列表，纳管主机时使用，将主机添加至该分组，分组支持嵌套。
- **opsany_control_get_zabbix_list**: 管控平台 获取管控平台监控插件 基础监控插件ZabbixServer列表，纳管主机添加监基础控插件时使用，将主机使用该插件监控，可在基础监控平台查看。
- **opsany_control_get_prometheus_list**: 管控平台 获取管控平台监控插件 应用监控插件PrometheusServer列表，纳管主机添加应用监控插件时使用，将主机使用该插件监控，可在应用监控平台查看。
- **opsany_control_get_dashboard_list**: 管控平台 获取管控平台监控大屏列表，纳管主机添加监控插件时使用，根据标签判断 将主机使用该插件监控，可在应用监控平台查看。
- **opsany_control_get_zabbix_temp_list**: 管控平台 获取管控平台Zabbix监控模板列表，纳管主机添加Zabbix监控插件时使用。
- **opsany_control_create_host**: 管控平台 添加纳管主机，需要输入主机唯一标识， 主机IP,主机端口，系统用户，需要选择控制器，选择操作系统，管控方式，分组主机类型等，也可以添加Zabbix监控插件或Prometheus监控插件，需要传入指定参数。

### Event（事件中心）
- **opsany_event_alert_info**: 事件中心，获取事件中心我的告警和全部告警，可获取到待处理、处理中、已关闭告警；包括Prometheus(应用监控)，Zabbix(基础监控)纳管和监控的实例和第三方接入的告警！

### Prometheus（应用监控）
- **opsany_prom_alert_info**: 应用监控，获取应用监控平台的实例告警，包括管控平台纳管并使用Prometheus的组件监控实例告警和服务拨测告警！

### KBase（知识库）
- **opsany_kbase_read_kbase_list**: 知识库，获取知识库平台全部知识库，知识库内有各类文章和文档！
- **opsany_kbase_read_kbase_article**: 知识库，获取知识库平台某一知识库内文章和文档，可获取列表和单条数据！

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd opsany-mcp-server
```

2. 创建虚拟环境并安装依赖：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

在项目目录下创建 `config/config.yaml` 文件（参考config.yaml.example）：

```yaml
apiVersion: v1
apiService:
  url: https://DOMAIN_NAME
  bk_app_code: cmdb
  bk_app_secret: CMDB_SECRET_KEY
  super_username: admin  # 管理员用户名 用作部分API接口内部调用
  api_version: 4.0.2  # esb api服务版本
server:
  host: 0.0.0.0
  port: 8020
  auth_token: "MCP_AUTH_TOKEN"  # MCP Server的认证Token，安装时自动生成，调用时需要添加在Header中。
  version: 2.3.2
config:
  resourceIdDefaultField: "code,VISIBLE_NAME,name"
  resourceIdFieldSearch: false
  resourceDefaultLimit: 20
  apiResourcesDefaultLimit: 100


```

## 使用

### 启动服务器

```bash
python server.py
```


或覆盖主机和端口：

```bash
python server.py --host 0.0.0.0 --port 8020
```

### MCP 工具

# OpsAny 平台 API 文档

---

### 1. CMDB（配置管理数据库）接口

#### 1.1 获取全部资源模型信息
**接口名称**：`opsany_cmdb_api_resources`
**功能描述**：获取平台中全部资源模型信息，包括资源类型名称、资源类型标识、资源分组名称等。若未传 `output=extend`，则不会返回“资源实例总数”和“字段总数”。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **output** | String | 否 | `""` | 若需获取资源实例总数与字段总数，请传 `"extend"`；否则留空。 |
| **limit** | Integer | 否 | `100` | 返回的资源模型数量上限。 |
| **resource_type** | String | 否 | `zc,zz,yw,gl` | 资源模型类型：`zc`(资产) `zz`(组织) `yw`(业务) `gl`(其他)，支持多选。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |


#### 1.2 获取指定资源字段信息
**接口名称**：`opsany_cmdb_get_resource_fields`
**功能描述**：获取指定资源模型的字段定义详情（如字段类型、配置）。在创建/修改数据前，必须调用此接口拉取字段信息以符合校验规则。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_code** | String | **是** | - | 资源类型标识（Code）。 |
| **field_type** | String | 否 | `01` | 字段类型过滤：`0`(普通) `1`(连接) `2`(从属)，支持组合如 `012`。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 1.3 获取资源仓库数据
**接口名称**：`opsany_cmdb_get_resource`
**功能描述**：分页查询资源仓库中的具体实例数据。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_code** | String | **是** | - | 资源类型标识（必填）。 |
| **resource_id** | String | 否 | - | 资源 ID，精准查询单条数据。 |
| **search** | String | 否 | - | 搜索关键词，用于模糊匹配。 |
| **link_data** | String | 否 | - | 是否获取连接关系数据。 |
| **fields** | String | 否 | 前8个字段 | 指定返回的字段列表，多个用逗号分隔；显示全部传 `"all"`。 |
| **page** | Integer | 否 | `1` | 页码。 |
| **limit** | Integer | 否 | `20` | 每页数量。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

#### 1.4 获取资源关联关系实例总数
**接口名称**：`opsany_cmdb_get_resource_link_inst_count`
**功能描述**：获取某一资源的所有关联关系数据字段和实例总数，包括从属关系（`is_relationship_field=1`）和关联关系（`is_relationship_field=2`）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | Integer | **是** | - | 资源 ID。 |
| **field_code** | String | **是** | - | 关联关系字段（需为 `is_relationship_field=2` 的字段）。 |
| **current** | Integer | 否 | `1` | 页码，打开第几页。 |
| **pageSize** | Integer | 否 | `20` | 页数，每页多少条。 |
| **search_type** | Integer | 否 | - | 搜索字段。 |
| **search_data** | Integer | 否 | - | 搜索数据。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

#### 1.5 获取资源关联关系实例列表
**接口名称**：`opsany_cmdb_get_resource_link_inst_list`
**功能描述**：资源平台，获取资源仓库某一数据的指定关联关系字段数据列表, 包括opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | Integer | **是** | - | 资源 ID。 |
| **field_code** | String | **是** | - | 关联关系字段（需为 `is_relationship_field=2` 的字段）。 |
| **current** | Integer | 否 | `1` | 页码，打开第几页。 |
| **pageSize** | Integer | 否 | `20` | 页数，每页多少条。 |
| **search_type** | Integer | 否 | - | 搜索字段。 |
| **search_data** | Integer | 否 | - | 搜索数据。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

#### 1.6 获取可添加的关联关系数据列表
**接口名称**：`opsany_cmdb_get_can_add_link_inst_list`
**功能描述**：资源平台，添加资源的关联关系字段数据时，拉取指定关联关系字段的待添加数据列表(拉取关联关系对端模型数据，已过滤添加过的数据)，包括opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | Integer | **是** | - | 资源 ID。 |
| **field_code** | String | **是** | - | 关联关系字段（需为 `is_relationship_field=2` 的字段）。 |
| **current** | Integer | 否 | `1` | 页码，打开第几页。 |
| **pageSize** | Integer | 否 | `20` | 页数，每页多少条。 |
| **search_type** | Integer | 否 | - | 搜索字段。 |
| **search_data** | Integer | 否 | - | 搜索数据。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

#### 1.7 添加资源关联关系数据
**接口名称**：`opsany_cmdb_resource_add_link_inst`
**功能描述**：资源平台，资源仓库给指定数据添加关联关系字段数据，opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系， 使用该工具操作。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | Integer | **是** | - | 资源 ID。 |
| **model_code** | String | **是** | - | 资源类型。 |
| **field_code** | String | **是** | - | 关联关系字段（需为 `is_relationship_field=2` 的字段）。 |
| **target_code_list** | Array | **是** | - | 目标实例 ID 列表，例如 `[10, 11, 12]`。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

#### 1.8 移除资源关联关系数据
**接口名称**：`opsany_cmdb_resource_remove_link_inst`
**功能描述**：资源平台，资源仓库给指定数据移除关联关系字段数据，opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系， 使用该工具操作。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | Integer | **是** | - | 资源 ID。 |
| **model_code** | String | **是** | - | 资源类型。 |
| **field_code** | String | **是** | - | 关联关系字段（需为 `is_relationship_field=2` 的字段）。 |
| **target_code** | Array | **是** | - | 目标实例 ID 列表，例如 `[10, 11, 12]`。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |


#### 1.9 创建资源实例
**接口名称**：`opsany_cmdb_create_resource`
**功能描述**：在资源仓库中新建一条数据。必须先获取模型字段后整理数据，普通字段数据写入 `data`。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_code** | String | **是** | - | 资源类型（必填）。 |
| **import_type** | String | 否 | - | 导入来源。 |
| **parent_inst** | String | 否 | - | 从属关系资源 ID；置空传 `set_null`。 |
| **data** | Object | **是** | - | 数据对象。Key 为字段标识 (code)，Value 为具体数据。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

#### 1.10 更新资源实例
**接口名称**：`opsany_cmdb_update_resource`
**功能描述**：更新资源仓库中的现有数据。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_code** | String | **是** | - | 资源类型（必填）。 |
| **code** | Integer | **是** | - | 资源 ID。 |
| **parent_inst** | String | 否 | - | 从属关系资源 ID（不在 data 内写）。 |
| **data** | Object | **是** | - | 数据对象。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

#### 1.11 删除资源实例
**接口名称**：`opsany_cmdb_delete_resource`
**功能描述**：从资源仓库中删除指定数据。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_code** | String | **是** | - | 资源类型（必填）。 |
| **code** | Integer | **是** | - | 资源 ID。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---

### 1.12 获取资源模型分组
**接口名称**：`opsany_cmdb_get_model_group`
**功能描述**：获取资源模型分组，用于创建模型时选择分组。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_type** | String | 否 | - | 资源分组类型：`zc`(资产) `yw`(业务) `zz`(组织)。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.13 获取资源模型列表
**接口名称**：`opsany_cmdb_get_model`
**功能描述**：获取资源模型列表，获取到模型 code 后可以进行模型字段管理。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **model_type** | String | 否 | - | 资源分组类型：`zc`(资产) `yw`(业务) `zz`(组织)。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.14 创建资源模型
**接口名称**：`opsany_cmdb_create_model`
**功能描述**：创建资源模型，创建后需要创建属性(字段)才可以在资源仓库创建该模型数据。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | String | **是** | - | 模型 code（模型唯一标识，建议全大写，下划线间隔，如 `CLOUD_SERVER`）。 |
| **name** | String | **是** | - | 模型名称。 |
| **model_type** | String | **是** | - | 资源分组类型：`zc`(资产) `yw`(业务) `zz`(组织)。 |
| **model_group** | String | **是** | - | 模型分组 code（通过 `opsany_cmdb_get_model_group` 获取）。 |
| **clone_model** | String | 否 | - | 克隆该模型字段信息，传入要克隆的模型 code。 |
| **built_in** | Boolean | 否 | `false` | 是否为内置模型。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.15 修改资源模型
**接口名称**：`opsany_cmdb_update_model`
**功能描述**：修改资源模型，支持修改名称、分组和是否内置。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | String | **是** | - | 模型 code（模型唯一标识）。 |
| **name** | String | **是** | - | 模型名称。 |
| **model_group** | String | **是** | - | 模型分组 code（通过 `opsany_cmdb_get_model_group` 获取）。 |
| **built_in** | Boolean | 否 | `false` | 是否为内置模型。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.16 删除资源模型
**接口名称**：`opsany_cmdb_delete_model`
**功能描述**：删除资源模型，谨慎删除，当模型没有数据才可以删除。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | String | **是** | - | 模型 code（模型唯一标识）。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.17 创建资源模型字段
**接口名称**：`opsany_cmdb_create_model_fields`
**功能描述**：创建资源模型属性(字段)，仅支持创建普通字段（`is_relationship_field=''`），不支持创建关联关系字段。字段类型及配置请参考「字段类型与后端请求字段说明」附录。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明                                                  |
| :--- | :--- | :--- | :--- |:----------------------------------------------------|
| **code** | String | **是** | - | 字段 code，格式：`{model_code}_{code}`。                   |
| **name** | String | **是** | - | 字段名称。                                               |
| **type_name** | String | **是** | - | 字段类型 code（如 `str`、`int`、`float`、`date` 等）。          |
| **model_code** | String | **是** | - | 模型 code（通过 `opsany_cmdb_get_model` 获取）。             |
| **field_group_code** | String | **是** | - | 字段分组 code（通过 `opsany_cmdb_get_resource_fields` 获取）。 |
| **attribute** | Object | **是** | - | 属性配置（默认值、提示、校验规则、下拉选项等），不同字段类型格式不同，详见 100.1 字段说明。             |
| **not_null** | Boolean | 否 | `false` | 是否必填。                                               |
| **built_in** | Boolean | 否 | `false` | 是否为内置属性。                                            |
| **index** | Number | 否 | - | 排序索引。                                               |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。                                        |

---

### 1.18 修改资源模型字段
**接口名称**：`opsany_cmdb_update_model_field`
**功能描述**：修改资源模型属性(字段)，支持修改名称、分组和是否内置。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | String | **是** | - | 字段 code。 |
| **name** | String | **是** | - | 字段名称。 |
| **type_name** | String | **是** | - | 字段类型 code。 |
| **model_code** | String | **是** | - | 模型 code。 |
| **attribute** | Object | **是** | - | 属性配置，固定格式（提示、默认值、校验规则、下拉框数据等）详见 100.1 字段说明。。 |
| **field_group_code** | String | 否 | - | 字段分组 code。 |
| **not_null** | Boolean | 否 | - | 是否必填。 |
| **built_in** | Boolean | 否 | - | 是否为内置属性。 |
| **index** | Number | 否 | - | 排序索引。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 1.19 删除资源模型字段
**接口名称**：`opsany_cmdb_delete_model_field`
**功能描述**：删除资源模型字段，谨慎删除，删除后该模型当前字段数据也会被清空。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **code** | String | **是** | - | 字段 code。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---


### 2. RBAC（统一权限）接口

#### 2.1 获取全部用户信息
**接口名称**：`opsany_rbac_get_or_search_all_user`
**功能描述**：获取平台全部用户信息（仅管理员）。支持精准查找、模糊搜索及扩展字段（部门、认证来源等）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **username** | String | 否 | - | 用户名精准查找。 |
| **chname** | String | 否 | - | 中文名精准查找。 |
| **search_username** | String | 否 | - | 用户名模糊搜索。 |
| **search_chname** | String | 否 | - | 中文名称模糊搜索。 |
| **search_username_or_chname** | String | 否 | - | 中文名或用户名联合模糊搜索。 |
| **extend** | String | 否 | `all` | 扩展字段，包括部门用户认证来源等全部字段。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

#### 2.2 获取当前用户信息
**接口名称**：`opsany_rbac_get_my_user_info`
**功能描述**：获取当前登录用户（自己）的详细信息。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **extend** | String | 否 | - | 扩展字段，包括部门用户认证来源等全部字段，使用 `"all"`。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 2.3 创建用户
**接口名称**：`opsany_rbac_create_user`
**功能描述**：批量创建用户（仅管理员）。仅支持创建普通用户。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **user_info_list** | Array | **是** | - | 用户信息列表（数组）。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

*   **`user_info_list` 元素结构 (Object)**:
    *   `username` (String, 必填): 用户名。
    *   `chname` (String, 必填): 中文名。
    *   `password` (String, 必填): 密码 (8-20位, 大小写字母+数字)。
    *   `phone` (String): 手机号。
    *   `email` (String): 邮箱。
    *   `position` (String): 职位。
    *   `description` (String): 描述。

#### 2.4 更新用户信息
**接口名称**：`opsany_rbac_update_user`
**功能描述**：批量修改用户信息（仅管理员）。目前仅支持修改启用/禁用状态。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **user_info_list** | Array | **是** | - | 用户信息列表。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

*   **`user_info_list` 元素结构 (Object)**:
    *   `username` (String): 用户名。
    *   `is_activate` (Boolean, 必填): 启用禁用状态。

#### 2.5 删除用户
**接口名称**：`opsany_rbac_delete_user`
**功能描述**：批量删除用户（仅管理员）。仅支持删除普通用户或被禁用的用户。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **user_info_list** | Array | **是** | - | 用户名列表 (Array)。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间（秒）。 |

---


### 3. Monitor（基础监控）接口

#### 3.1 获取实例告警信息
**接口名称**：`opsany_monitor_alert_info`
**功能描述**：获取基础监控平台的实例告警信息（需管控平台纳管）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **page** | String | 否 | - | 页码。 |
| **pageSize** | String | 否 | - | 每页条数。 |
| **host_name** | String | 否 | - | 主机唯一标识/实例名称模糊搜索。 |
| **name** | String | 否 | - | 告警名称模糊搜索。 |
| **severity** | String | 否 | - | 告警级别：`0`(未分类) `1`(信息) `2`(警告) `3`(一般严重) `4`(严重) `5`(灾难)。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 4. Workbench（工作台/ITSM）接口

#### 4.1 获取工单列表
**接口名称**：`opsany_workbench_work_order_inst`
**功能描述**：获取全部工单、待办、已办或我提交的工单。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **current** | String | 否 | - | 页码。 |
| **pageSize** | String | 否 | - | 每页条数。 |
| **data** | String | 否 | - | 分类：`all`(全部) `will`(待办) `already`(已办) `self`(我提交的)。 |
| **order_by** | String | 否 | - | 排序字段。 |
| **status** | String | 否 | - | 工单状态：`0`(进行中) `1`(已结束)。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |


#### 4.2 获取服务分类
**接口名称**：`opsany_workbench_work_order_folder`
**功能描述**：获取全部服务分类，用于搜索指定分类下的工单。
**请求参数**：
*(无特定业务参数)*

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |


#### 4.3 获取服务目录/模板
**接口名称**：`opsany_workbench_work_order_temp`
**功能描述**：获取全部服务目录及表单字段，用于提单前获取字段详情。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **id** | Integer | 否 | - | 服务 ID，获取单条详情。 |
| **form_fields** | Boolean | 否 | - | 是否包含表单字段（提单必选）。 |
| **current** | Integer | 否 | - | 页码。 |
| **pageSize** | Integer | 否 | - | 每页条数。 |
| **folder_id** | String | 否 | - | 服务分类 ID (`all` 或具体 ID)。 |
| **data_type** | String | 否 | - | 服务类型：`all`, `tags`, `request`, `change` 等。 |
| **name_or_describe** | String | 否 | - | 名称或描述模糊搜索。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 4.4 提交工单
**接口名称**：`opsany_workbench_work_order_submit`
**功能描述**：根据服务 ID 和表单字段提交新工单。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **submit_from** | String | **是** | - | 提交来源。 |
| **work_order_id** | Integer | **是** | - | 服务 ID。 |
| **follow** | Boolean | 否 | - | 是否跟踪（状态变更通知）。 |
| **field_dict** | Object | **是** | - | 表单内容。Key 为字段 ID，Value 为数据。下拉/级联等需传入 `{"key": "value"}` 格式。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

### 5. Job（作业平台）接口

#### 5.1 获取工具市场列表
**接口名称**：`opsany_job_get_tool_market_list`
**功能描述**：获取作业平台工具市场（作业列表和脚本列表）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **data_type** | String | 否 | - | 类型：`job`(作业) `script`(脚本) `all`(全部)。 |
| **script_name** | String | 否 | - | 脚本或作业名称模糊搜索。 |
| **create_user** | String | 否 | - | 创建人模糊搜索。 |
| **job_id** | Integer | 否 | - | 查询特定作业详情。 |
| **script_id** | Integer | 否 | - | 查询特定脚本详情。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 5.2 获取作业列表
**接口名称**：`opsany_job_get_job_list`
**功能描述**：获取仅需作业 ID 即可执行的作业列表。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **name** | String | 否 | - | 作业名称模糊搜索。 |
| **create_user** | String | 否 | - | 创建人模糊搜索。 |
| **job_id** | Integer | 否 | - | 查询特定作业详情。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 5.3 获取脚本列表
**接口名称**：`opsany_job_get_script_list`
**功能描述**：获取脚本列表（执行需脚本 ID 及主机等参数）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **script_name** | String | 否 | - | 脚本名称模糊搜索。 |
| **create_user** | String | 否 | - | 创建人模糊搜索。 |
| **script_id** | Integer | 否 | - | 查询特定脚本详情。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 5.4 根据 ID 执行作业
**接口名称**：`opsany_job_run_job_by_id`
**功能描述**：根据作业 ID 执行作业，返回任务 ID。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **job_id** | Integer | **是** | - | 作业 ID。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

#### 5.5 根据 ID 执行脚本
**接口名称**：`opsany_job_run_script_by_id`
**功能描述**：根据脚本 ID 在指定主机上执行脚本。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **script_id** | Integer | **是** | - | 脚本 ID。 |
| **server** | String | **是** | - | 主机唯一标识（多台用逗号隔开）。 |
| **parameter** | String | 否 | `""` | 脚本参数。 |
| **run_describe** | String | 否 | - | 执行原因。 |
| **time_out** | Integer | 否 | `120` | 脚本执行超时时间（秒）。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |


#### 5.6 获取执行结果
**接口名称**：`opsany_job_get_run_result_by_log_id`
**功能描述**：根据任务 ID 获取作业或脚本的执行结果。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **log_id** | Integer | **是** | - | 执行后返回的任务 ID。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

#### 5.7 根据脚本内容执行脚本
**接口名称**：`opsany_job_run_script_by_script`
**功能描述**：直接输入脚本内容和主机信息执行脚本，返回任务 ID，可根据任务 ID 获取执行结果。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **server** | String | **是** | - | 主机唯一标识或主机 IP，多台用逗号隔开。主机需为管控平台纳管的主机。 |
| **task_name** | String | 否 | - | 任务名称，简短的任务名称，后续执行任务会根据该名称拼接执行记录。 |
| **server_type** | String | 否 | `host_name` | 主机类型：`host_name`(主机唯一标识)、`ip`(主机IP)。 |
| **script_type** | String | 否 | `sh` | 脚本类型：`sh`(Shell)、`ps1`(PowerShell)、`py`(Python)、`bat`(Bat)。 |
| **script** | String | 否 | - | 脚本内容，直接输入脚本内容。 |
| **parameter** | String | 否 | `""` | 脚本参数。 |
| **run_describe** | String | 否 | - | 执行原因。 |
| **timeout** | Integer | 否 | `120` | 超时时间（秒）。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---

#### 5.8 创建脚本到脚本仓库
**接口名称**：`opsany_job_create_script_library`
**功能描述**：创建脚本到脚本仓库，仅支持创建私有脚本。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **script_type** | Integer | 否 | - | 脚本类型。 |
| **script_name** | String | 否 | - | 脚本名称。 |
| **version_remarks** | String | 否 | - | 版本备注。 |
| **script** | String | 否 | - | 脚本内容。 |
| **tool_timeout** | Integer | 否 | `30` | 工具请求超时时间（秒）。 |

---


### 6. Control（管控平台）接口

---

#### 6.1 获取纳管主机列表
**接口名称**：`opsany_control_get_managed_host_list`
**功能描述**：获取管控平台纳管的主机列表，数据来自资源平台主机组内三个模型的数据(SERVER, CLOUD_SERVER, VIRTUAL_SERVER)。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **host_name_search** | String | 否 | - | 根据主机唯一标识模糊搜索纳管主机。 |
| **show_name_search** | String | 否 | - | 根据主机名称模糊搜索纳管主机。 |
| **ip_search** | String | 否 | - | 根据主机名唯一标识模糊搜索纳管主机。 |
| **id** | Integer | 否 | - | 根据主机ID查询纳管主机，精准查询。 |
| **host_name** | String | 否 | - | 根据主机ID查询纳管主机，精准查询。 |
| **show_name** | String | 否 | - | 根据主机ID查询纳管主机，精准查询。 |
| **ip** | String | 否 | - | 根据主机IP查询纳管主机，精准查询。 |
| **system_type** | String | 否 | - | 根据主机系统类型查询，Linux 或 Windows。 |
| **host_type** | String | 否 | - | 根据主机类型查询，支持 SERVER, CLOUD_SERVER, VIRTUAL_SERVER，多个使用逗号隔开。 |
| **tool_timeout** | Integer | 否 | 30 | 工具请求超时时间。 |

---

#### 6.2 获取控制器列表
**接口名称**：`opsany_control_get_controller_list`
**功能描述**：获取管控平台控制器(Proxy)列表，用于纳管主机时指定控制器。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **name** | String | 否 | - | 根据控制名称搜索。 |
| **id** | Integer | 否 | - | 根据控制ID获取控制器详情。 |
| **tool_timeout** | Integer | 否 | 10 | 工具请求超时时间。 |

---

#### 6.3 获取主机分组列表
**接口名称**：`opsany_control_get_host_group_list`
**功能描述**：获取管控平台主机分组列表，用于纳管主机时添加至该分组（支持嵌套）。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **tool_timeout** | Integer | 否 | 10 | 工具请求超时时间。 |

---

#### 6.4 获取 Zabbix 监控列表
**接口名称**：`opsany_control_get_zabbix_list`
**功能描述**：获取管控平台基础监控插件 ZabbixServer 列表，用于纳管主机时添加基础监控插件。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **tool_timeout** | Integer | 否 | 10 | 工具请求超时时间。 |

---

#### 6.5 获取 Prometheus 监控列表
**接口名称**：`opsany_control_get_prometheus_list`
**功能描述**：获取管控平台应用监控插件 PrometheusServer 列表，用于纳管主机时添加应用监控插件。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **tool_timeout** | Integer | 否 | 10 | 工具请求超时时间。 |

---

#### 6.6 获取监控大屏列表
**接口名称**：`opsany_control_get_dashboard_list`
**功能描述**：获取管控平台监控大屏列表，根据标签判断将主机使用该插件监控。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **dashboard_type** | String | **是** | - | 大屏类型，必填：Prometheus 或 Zabbix。 |
| **tool_timeout** | Integer | 否 | 10 | 工具请求超时时间。 |

---

#### 6.7 获取 Zabbix 模板列表
**接口名称**：`opsany_control_get_zabbix_temp_list`
**功能描述**：获取管控平台 Zabbix 监控模板列表，纳管主机添加 Zabbix 监控插件时使用。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **zabbix_id** | String | **是** | - | 通过 `opsany_control_get_zabbix_list` 获取 Zabbix 实例 ID。 |
| **tool_timeout** | Integer | 否 | 20 | 工具请求超时时间。 |

---

#### 6.8 创建纳管主机
**接口名称**：`opsany_control_create_host`
**功能描述**：添加纳管主机，支持批量纳管，并可配置 Zabbix 或 Prometheus 监控插件。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **host_info_list** | Array | **是** | - | 批量纳管主机列表，主机信息在列表中。 |
| **tool_timeout** | Integer | 否 | 30 | 工具请求超时时间，每增加一台建议延长 2 秒。 |

**`host_info_list` 数组内对象参数详情**：

*   **基础信息**：
    *   `name` (String, **必填**): 主机唯一标识。
    *   `show_name` (String, **必填**): 主机显示名。
    *   `ip` (String, **必填**): 主机 IP 地址。
    *   `system_type` (String, **必填**): 操作系统，仅支持 `Linux` 或 `Windows`。
    *   `controller_id` (Integer, **必填**): 控制器 ID（通过 `opsany_control_get_controller_list` 获取）。
    *   `control_type` (Integer, **必填**): 管控方式，1: SSH, 2: Agent, 3: SSH/Agent, 4: Agent/SSH。
    *   `group_id` (Integer, **必填**): 主机分组 ID（通过 `opsany_control_get_host_group_list` 获取）。
    *   `host_type` (String, **必填**): 主机类型，`SERVER` (物理机) 或 `VIRTUAL_SERVER` (虚拟机)。
    *   `username` (String, 可选): 主机系统用户，默认 `root`。
    *   `password` (String, 可选): 主机密码。

*   **端口配置**：
    *   `ssh_port` (String): SSH 端口，Linux 默认 `22`。
    *   `login_port` (String): RDP 端口，Windows 默认 `3389`。

*   **特权提升 (Sudo/Su)**：
    *   `privilege` (Boolean): 是否开启特权提升。
    *   `privilege_type` (String): 特权类型，`sudo` 或 `su`。
    *   `privilege_username` (String): 特权用户名。
    *   `privilege_password` (String): 特权密码。

*   **监控插件配置**：
    *   `monitor_type` (String): 监控类型，`Zabbix` 或 `Prometheus`。
    *   `controller_zabbix` (String): monitor_type 为 Zabbix 时必填。
    *   `controller_prom` (String): monitor_type 为 Prometheus 时必填。
    *   `bind_port` (Integer): Prometheus 自定义端口，默认 `9101`。
    *   `template_list` (Array): Zabbix 模板列表（包含 temp_name 和 temp_id）。
    *   `dashboard_dict` (Object): 大屏信息（uid, title, url, tags）。

*   **其他配置**：
    *   `is_bastion` (Boolean): 是否同步到堡垒机。
    *   `is_bastion_group` (Boolean): 是否同步分组到堡垒机。
    *   `reinstall_zabbix_agent` (Boolean): 是否自动安装 Zabbix 插件。
    *   `reinstall_prom_exporter` (Boolean): 是否自动安装 Prometheus 插件。
---


### 7. Event（事件中心）接口

#### 7.1 获取事件中心告警
**接口名称**：`opsany_event_alert_info`
**功能描述**：获取事件中心我的告警和全部告警，可获取待处理、处理中、已关闭告警。包括管控平台 Prometheus(应用监控)、Zabbix(基础监控)纳管和监控的实例以及第三方接入的告警。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **alert_type** | String | 否 | - | 告警类型：`node`(主机/组件告警)、`blackbox`(服务拨测告警)、`all`(全部告警)。 |
| **severity** | String | 否 | - | 告警级别：`NotClassified`(未分类)、`Information`(信息)、`Warning`(警告)、`Average`(一般严重)、`High`(严重)、`Disaster`(灾难)。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间，告警过多建议增加。 |

---

### 8. Prometheus（应用监控）接口

#### 8.1 获取应用监控告警
**接口名称**：`opsany_prom_alert_info`
**功能描述**：获取应用监控平台的实例告警，包括管控平台纳管并使用 Prometheus 后在组件监控接入的实例告警和服务拨测告警。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **alert_type** | String | 否 | - | 告警类型：`node`(主机/组件告警)、`blackbox`(服务拨测告警)、`all`(全部告警)。 |
| **severity** | String | 否 | - | 告警级别：`NotClassified`(未分类)、`Information`(信息)、`Warning`(警告)、`Average`(一般严重)、`High`(严重)、`Disaster`(灾难)。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间，告警过多建议增加。 |

---

### 9. KBase（知识库）接口

#### 9.1 获取知识库列表
**接口名称**：`opsany_kbase_read_kbase_list`
**功能描述**：获取知识库平台全部知识库，知识库内有各类文章和文档。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **data_type** | String | 否 | - | 数据类型：`all`(全部)、`public`(公共)、`involved`(我参与的)、`favorite`(我收藏的)、`owner`(我拥有的)。 |
| **search_type** | String | 否 | - | 搜索字段：`name`(名称)、`description`(描述)。 |
| **search_data** | String | 否 | - | 搜索数据，与 search_type 同时使用。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间。 |

---

#### 9.2 获取知识库文章
**接口名称**：`opsany_kbase_read_kbase_article`
**功能描述**：获取知识库平台某一知识库内的文章和文档，可获取列表和单条数据。
**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **unique_code** | String | 否 | - | 文章唯一标识，获取单条文章内容。 |
| **data_type** | String | 否 | - | 数据类型：`all`(全部文章)、`self`(我的文章)、`folder`(按目录筛选)、`favorite`(我收藏的)、`single`(单条)。 |
| **kbase** | String | 否 | - | 知识库唯一标识（通过 `opsany_kbase_read_kbase_list` 获取的 `unique_code` 字段）。 |
| **current** | String | 否 | - | 当前页码。 |
| **pageSize** | String | 否 | - | 每页条数。 |
| **search_type** | String | 否 | - | 搜索字段：`title`(文章标题)。 |
| **search_data** | String | 否 | - | 搜索数据，与 search_type 同时使用。 |
| **tool_timeout** | Integer | 否 | `60` | 工具请求超时时间。 |

---

#### 100.1 字段说明


model_fields_attribute_md = """
字段类型与后端请求字段说明

## 概述

---

## 公共基础字段（所有类型通用）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `name` | `form.name` | string | 字段名称 |
| `code` | `form.code` (新增时拼接: `{model_code}_{code}`) | string | 字段标识 |
| `type_name` | `form.type_name` | string | 字段类型 code |
| `not_null` | `form.not_null` | boolean | 是否必填 |
| `built_in` | `form.built_in` | boolean | 是否内置属性 |
| `model_code` | `this.model_code` | string | 所属模型 code |
| `field_group_code` | `form.field_group_code` | string | 所属字段组 code |
| `index` | `this.fieldLength` | number | 排序索引 |
| `attribute.rule_id` | `form2.rule_id` | string\|number | 校验规则ID ("empty" 表示无校验) |
| `attribute.rule` | `form2.rule` | object | 校验规则 `{ re: "正则表达式" }` |

---

## 一、str（单行文本） / textarea（多行文本） / link（链接）


| 字段 | 来源 | 类型 | 适用类型 | 说明 |
|------|------|------|----------|------|
| `attribute.默认值` | `form2["默认值"]` | string | str/textarea/link | 默认值 |
| `attribute.maxLen` | `form2.maxLen` | number | str/textarea | 最大长度（link 无此字段） |
| `attribute.用户提示` | `form2["用户提示"]` | string | 全部 | 占位提示文本 |

**JSON 示例（str）：**
```json
{
  "name": "主机名",
  "code": "host_name",
  "type_name": "str",
  "not_null": true,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 0,
  "attribute": {
    "默认值": "",
    "maxLen": 100,
    "用户提示": "请输入主机名",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 二、int（整数）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.单位` | `form2["单位"]` | string | 单位（如 "个"、"台"） |
| `attribute.默认值` | `form2["默认值"]` | number | 默认值 |
| `attribute.minLen` | `form2.minLen` | number | 最小值 |
| `attribute.maxLen` | `form2.maxLen` | number | 最大值 |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "CPU核数",
  "code": "cpu_cores",
  "type_name": "int",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 1,
  "attribute": {
    "单位": "核",
    "默认值": 4,
    "minLen": 1,
    "maxLen": 128,
    "用户提示": "请输入CPU核数",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 三、float（浮点型）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.rule_id` | `form2.rule_id` | string\|number | 校验规则ID |

**JSON 示例：**
```json
{
  "name": "内存大小",
  "code": "memory_size",
  "type_name": "float",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 2,
  "attribute": {
    "rule_id": 1,
    "rule": { "re": "[1-9][0-9]*.[0-9]*|0\\.[0-9]*[1-9][0-9]*" }
  }
}
```

---

## 四、date（日期时间）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.默认值` | `form2["默认值"]` | string | 默认值，格式 `YYYY-MM-DD HH:mm:ss` |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "采购日期",
  "code": "purchase_date",
  "type_name": "date",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 3,
  "attribute": {
    "默认值": "2024-01-01 00:00:00",
    "用户提示": "请选择日期",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 五、expiredDate（到期时间）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.默认值` | `form2["默认值"]` | string | 默认值，格式 `YYYY-MM-DD HH:mm:ss` |
| `attribute.expire_day` | `form2.expire_day` | number | 到期天数（选择此类型时自动设为 30） |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "维保到期",
  "code": "warranty_expire",
  "type_name": "expiredDate",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 4,
  "attribute": {
    "默认值": "2025-01-01 00:00:00",
    "expire_day": 30,
    "用户提示": "请选择到期时间",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 六、richText（富文本）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.富文本` | `form2["富文本"]` | string | 富文本 HTML 内容（由 editor 组件回调设置） |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "备注",
  "code": "description",
  "type_name": "richText",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 5,
  "attribute": {
    "富文本": "<p>详细说明</p>",
    "用户提示": "请输入备注",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 七、dropDown（下拉菜单）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.选项` | `dropDownList` | `[{name, id}]` | 选项列表（name=选项名(显示名), id=选项值(唯一标识)，id使用变量格式，理论上不可修改） |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "状态",
  "code": "status",
  "type_name": "dropDown",
  "not_null": true,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 6,
  "attribute": {
    "选项": [
      { "name": "运行中", "id": "running" },
      { "name": "已停止", "id": "stop" },
      { "name": "故障", "id": "fault" }
    ],
    "用户提示": "请选择状态",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 八、复合数据（复合数据）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.tableData` | `this.tableData` | `[{name, key, type, uuid}]` | 复合数据结构体子字段列表（name=名称, key=标识, type=类型, uuid=唯一标识） |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

注意：`composite_type`（1=手动新建, 2=从模型导入）仅用于 UI 交互，**不会**发送到后端。

**JSON 示例：**
```json
{
  "name": "扩展信息",
  "code": "ext_info",
  "type_name": "复合数据",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 7,
  "attribute": {
    "tableData": [
      { "name": "字段A", "key": "field_a", "type": "str", "uuid": "xxx-xxx" },
      { "name": "字段B", "key": "field_b", "type": "str", "uuid": "yyy-yyy" }
    ],
    "用户提示": "",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 九、password（密码）

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `attribute.minLen` | `form2.minLen` | number | 最小长度 |
| `attribute.maxLen` | `form2.maxLen` | number | 最大长度 |
| `attribute.用户提示` | `form2["用户提示"]` | string | 占位提示文本 |

**JSON 示例：**
```json
{
  "name": "密码",
  "code": "password",
  "type_name": "password",
  "not_null": true,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 8,
  "attribute": {
    "minLen": 6,
    "maxLen": 32,
    "用户提示": "请输入密码",
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

## 十、file（附件）


```json
{
  "name": "附件",
  "code": "attachment",
  "type_name": "file",
  "not_null": false,
  "built_in": false,
  "model_code": "host",
  "field_group_code": "basic",
  "index": 9,
  "attribute": {
    "rule_id": "empty",
    "rule": {}
  }
}
```

---

**编辑（PUT）：** 新增参数基础上增加以下顶层字段：

| 字段 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `field_name` | `form.name` | string | 字段名称 |
| `field_code` | `form.code` | string | 字段 code |
| `is_relationship_field` | `form2["关系类型"]` | string | 固定为 `"1"` |
| `not_null` | `form.not_null` | boolean | 是否必填 |
| `built_in` | `form.built_in` | boolean | 是否内置 |
| `describe` | `form2["用户提示"]` | string | 描述提示 |

---

## 附录：校验规则


| 规则名称 | field_type | 正则 |
|----------|-----------|------|
| 正浮点数 | float | `[1-9][0-9]*.[0-9]*\|0\.[0-9]*[1-9][0-9]*` |
| 负浮点数 | float | `-([1-9][0-9]*.[0-9]*\|0\.[0-9]*[1-9][0-9]*)` |
| 仅小写字母 | str | `^[a-z]*$` |
| 仅大写字母 | str | `^[A-Z]*$` |
| 仅包含英文字母和数字 | str | `^[a-zA-Z0-9]*$` |
| 仅包含英文字母和数字、下划线、中划线、英文小数点 | str | `^[\.a-zA-Z0-9_-]*$` |
| 仅包含中文 | str | `^[\u4e00-\u9fa5]*$` |
| 邮件 | str | `\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}` |
| 手机 | str | `0?(13\|14\|15\|18\|17)[0-9]{9}` |
| 身份证号 | str | `[0-9]{17}[[0-9]\|x]\|[0-9]{15}` |
| QQ号码 | str | `[1-9]([0-9]{4,10})` |
| IP地址 | str | `^((25[0-5]\|2[0-4]\d\|[1]{1}\d{1}\d{1}\|[1-9]{1}\d{1}\|\d{1})($\|(?!\.$)\.)){4}$` |
| 正整数 | int | `[1-9][0-9]*` |
| 负整数 | int | `-[1-9][0-9]*` |
| 整数 | int | `-?[1-9][0-9]*` |

"""

---


## 在 TRAE 中配置使用

### 1. 启动 MCP Server

首先启动 OpsAny MCP Server：

```bash
cd opsany-mcp-server
python server.py --config config/config.yaml
```

服务器启动后会显示：

```
Starting OpsAny MCP Server on 192.168.0.111:8020
```

### 2. 在 TRAE 中配置 MCP Server

1. 打开 TRAE IDE
2. 进入 **设置** → **MCP Servers**
3. 点击 **添加 MCP Server**
4. 填写配置信息：

```json
{
    "name": "opsany-mcp-server",
    "url": "http://192.168.0.111:8020/sse",
    "headers": {
        "username": "username",
        "user-api-token": "7IecXVZHrk7t0jQ6lAUwBSULnScfVrRJpM7ZtPi5Wk73Fw",
        "mcp-auth-token": "7e84a67d-e97a-4986-a5c9-393837089c12"
  }
}
```

- username： OpsAny当前用户名
- user-api-token： OpsAny工作台-个人设置 创建的API Token
- mcp-auth-token： config.yaml配置中auth_token值


5. 点击 **保存** 并 **连接**

### 3. 验证连接

在 TRAE 的聊天界面中输入测试命令：

```
请使用 api_resources 工具获取所有可用的资源模型
```

如果连接成功，将返回所有资源模型的列表。


### 6. 常见问题排查

#### 连接失败

- 确认 MCP Server 正在运行
- 检查配置的 URL 是否正确（应为 `http://192.168.0.11:8020/sse`）
- 查看服务器日志确认是否有错误

#### 认证失败

- 检查 `config.yaml` 中的 API 凭证是否正确
- 确认 OpsAny 平台地址可访问
- 验证用户权限是否足够

#### 数据返回为空

- 确认 OpsAny 平台中有相关资源数据
- 检查搜索关键词是否正确
- 尝试不使用搜索参数获取全部数据

## 开发

项目结构：

```
opsany-mcp-server/
├── opsanymcp/               # 核心模块
│   ├── api/                 # API 接口
│   │   ├── __init__.py
│   │   ├── base_api.py      # API核心组件
│   │   ├── cmdb_api.py      # 资源平台API
│   │   ├── control_api.py   # 管控平台API
│   │   ├── event_api.py     # 事件中心API
│   │   ├── job_api.py       # 作业平台API
│   │   ├── kbase_api.py     # 知识库API
│   │   ├── monitor_api.py   # 基础监控API
│   │   ├── prom_api.py      # 应用监控(Prometheus)API
│   │   ├── rbac_api.py      # 统一权限API
│   │   └── workbench_api.py # 工作台API
│   ├── __init__.py
│   ├── constants.py         # 常量定义
│   └── libs.py              # 工具函数
├── config/                  # 配置文件
│   └── config.yaml          # 配置文件
├── server.py                # MCP Server 主入口
├── tool_list.py             # MCP 工具列表
└── requirements.txt         # Python 依赖
```

## 许可证

MIT License
