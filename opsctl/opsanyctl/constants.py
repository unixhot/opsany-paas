
# DEFAULT_SHORT_RESOURCE = {
#     "ser": "SERVER",  # 物理机
#     "server": "SERVER",  # 物理机
#     "virser": "VIRTUAL_SERVER",  # 虚拟机
#     "clser": "CLOUD_SERVER",  # 云主机
#     "idc": "IDC",  # 机房
#     "reg": "REGION",  # 区域
#     "rack": "RACK",  # 机柜
#     "pub": "PUBLIC_CLOUD",  # 公有云账号
#     "pubreg": "CLOUD_REGION",  # 区域
#     "pubza": "CLOUD_AZ",  # 可用区
#     "buss": "BUSINESS",  # 业务
#     "app": "APPLICATION",  # 应用
#     "serv": "SERVICE",  # 服务
# }

url_startswith = "/api/c/compapi/cmdb/"
URL_DICT = {
    "fields": url_startswith + "get_model_field/",
    "resource": url_startswith + "model_data_get/",
    "resource_type": url_startswith + "get_cmdb_model_tree/",
}
