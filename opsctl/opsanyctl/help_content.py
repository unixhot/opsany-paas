typer_help_content = """这是 OpsAny 用于查看或管理资源的命令行工具!\n
----------------------------\n\n
需要将config配置文件(opsanyctl config获取)修改后放置在 /HOME/.opsanyctl/config 下\n
"""

command_config_help = """获取配置文件模板\n
需要将config配置文件修改后放置在 /HOME/.opsanyctl/config 下\n
url: https://www.domian.com                         # OpsAny平台地址\n
bk_app_code: cmdb                                   # OpsAny 应用ID(开发中心)\n
bk_app_secret: 00000000-0000-0000-0000-000000000000 # OpsAny secret_key(开发中心)\n
bk_username: admin                                  # 获取数据用户\n
"""
default_api_resources = """

"""

command_api_resources_help = """查看支持的资源模型和相关汇总数据\n
案例：\n
- opsanyctl api_resources                      # 查看支持的资源模型\n
- opsanyctl api_resources --output extend      # 查看支持的资源模型和扩展字段包括展示字段数量资源数量等\n
- opsanyctl api_resources --limit 20           # 分页查看支持的资源模型\n
"""
command_re_help = """查看支持的资源模型和相关汇总数据 api-resources 简写\n
案例：\n
- opsanyctl res                                # 查看支持的资源模型\n
- opsanyctl res --output extend                # 查看支持的资源模型和扩展字段包括展示字段数量资源数量等\n
- opsanyctl res --limit 20                     # 分页查看支持的资源模型\n
"""
command_get_help = """获取支持的资源模型数据列表或单条数据\n
案例：\n
- opsanyctl get ser.field                      # 查看ser(SERVER)字段\n
- opsanyctl get ser                            # 获取ser(SERVER)数据, 使用简写需要添加到配置文件\n
- opsanyctl get SERVER                         # 获取SERVER数据\n
- opsanyctl get ser linux-node16               # 获取ser(SERVER)实例名为 linux-node16 的数据\n
- opsanyctl get ser code=10021                 # 获取ser(SERVER)code为 10021 的数据\n
- opsanyctl get ser SERVER_name=linux-node12   # 获取ser(SERVER)SERVER_name linux-node12 的数据\n
- opsanyctl get ser --search linux-node        # 搜索ser(SERVER)所有字段包含 linux-node 的数据\n
- opsanyctl get ser --fields code,SERVER_name  # 获取ser(SERVER)指定字段数据\n
- opsanyctl get ser --page 2 --limit 5         # 获取ser(SERVER)第二页数据。每页5条\n
- opsanyctl get ser --limit 5                  # 获取ser(SERVER) 首页五条数据\n
"""

command_api_resources_arg_output_help = """扩展输出字段使用 extend\n"""
command_api_resources_arg_limit_help = "指定输出数量 默认 100条, 支持配置文件配置默认值 apiResourcesDefaultLimit"
command_get_arg_resource_type_help = "资源类型 SERVER SERVER.fields"
command_get_arg_resource_id_help = "资源实例默认(code,SERVER_VISIBLE_NAME,SERVER_name)联合搜索, 支持使用fields=search(code=10012), 支持配置文件配置默认值 resourceIdDefaultField"
command_get_opt_search_help = "字段搜索，全文检索！"
command_get_opt_fields_help = "要显示的字段，用逗号分隔 SERVER_VISIBLE_NAME,SERVER_name"
command_get_opt_page_help = "指定页码 默认 1"
command_get_opt_limit_help = "指定页码输出数量 默认 20条, 支持配置文件配置默认值 resourceDefaultLimit"

config_content_title = """
将以下配置修改后放置在家目录 .opsanyctl/config 中
url,bk_app_code,bk_app_secret,bk_username 需要修改，其他配置根据需求修改
"""

config_content = """apiVersion: v1
apiService:
  url: https://www.domian.com
  bk_app_code: bk_app_code
  bk_app_secret: bk_app_secret
  bk_username: bk_username
config:
  resourceIdDefaultField: "code,VISIBLE_NAME,name"  # 默认搜索三个字段, 指定 code 或者 name 可以保证查询到的数据唯一
  resourceIdFieldSearch: false  # 默认关闭 RESOURCE_ID 字段 支持 fields=value方式精准字段获取资源
  resourceDefaultLimit: 20  # 资源默认每页数量
  apiResourcesDefaultLimit: 100  # 资源模型默认每页数量
resourceShort:
  ser: SERVER  # 物理机
  virser: VIRTUAL_SERVER  # 虚拟机
  clser: CLOUD_SERVER  # 云主机
  idc: IDC  # 机房
  reg: REGION  # 区域
  rack: RACK  # 机柜
  pub: PUBLIC_CLOUD  # 公有云账号
  pubreg: CLOUD_REGION  # 区域
  pubza: CLOUD_AZ  # 可用区
  buss: BUSINESS  # 业务
  app: APPLICATION  # 应用
  serv: SERVICE  # 服务
"""