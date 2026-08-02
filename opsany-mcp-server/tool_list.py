"""
enum: 限定参数的值必须是数组中的某一个。例如，"enum": ["add", "subtract", "multiply", "divide"]。
minimum / maximum: 为 number 或 integer 类型设置最小值和最大值。
minLength / maxLength: 为 string 类型设置最小和最大长度。
pattern: 使用正则表达式来验证字符串的格式，常用于邮箱、电话号码等。
items: 当属性类型为 array 时，items 用于定义数组中每个元素的类型和结构。

string: 字符串
number: 数字（包括浮点数）
integer: 整数
boolean: 布尔值 (true 或 false)
array: 数组
object: 对象（嵌套结构）
null: 空值
"""

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



TOOL_CMDB_DICT = {
    "opsany_cmdb_api_resources": {
        "name": "opsany_cmdb_api_resources",
        "description": "资源平台，获取全部资源模型, 包括资源类型名称，资源类型标识，资源分组名称，资源分组标识，资源名称，资源标识，资源简称，资源实例总数，字段总数, 当不要求获取资源实例总数，字段总数时output为空！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output": {
                    "type": "string",
                    "description": "资源实例总数和字段总数:使用参数：extend, 默认为空字符串。",
                    "default": ""
                },
                "limit": {
                    "type": "integer",
                    "description": "返回的资源模型数量限制",
                    "default": 100
                },
                "resource_type": {
                    "type": "string",
                    "description": "返回的资源模型类型，zc：资产模型 zz：组织模型 yw：业务模型 gl：其他 如 zc zc,zz zc,zz,yw,gl。",
                    "default": "zc,zz,yw,gl"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            }
        }
    },
    "opsany_cmdb_get_resource_fields": {
        "name": "opsany_cmdb_get_resource_fields",
        "description": """资源平台，获取指定资源的字段信息，获取资源仓库数据，创建修改资源仓库数据时需要拉取字段信息；
        字段描述：
        1. 字段类型(type_name)
            str : 字符串, 
            textarea: 多行文本,
            int: 整数,
            float: 浮点型,
            date: 日期,
            expiredDate: 到期时间,
            richText: 富文本,
            dropDown: 下拉菜单,
            composite: 复合数据, 数据类型为List，元素为Dict。
            复合数据: 复合数据, 数据类型为List，元素为Dict。
            file: 附件,
            password: 密码,
            link: 链接 可以访问的链接地址，以字符串保存,
            引用: 从属/连接 is_relationship_field=1 从属 is_relationship_field=2 连接
        2. 字段相关配置(attribute)
            关系类型: 1 普通关系 2 连接关系
            
        """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_code": {"type": "string", "description": "资源类型标识"},
                "field_type": {"type": "string", "description": "字段类型， 默认 01： 0 普通字段 1 连接关系字段 2 从属关系字段，案例： 0 01 012。"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": ["model_code"]
        }
    },
    "opsany_cmdb_get_resource": {
        "name": "opsany_cmdb_get_resource",
        "description": "资源平台，获取资源仓库数据",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "resource_id": {"type": "string", "description": "资源 ID（可选）"},
                "search": {"type": "string", "description": "搜索关键词（可选）"},
                "link_data": {"type": "string", "description": "是否获取连接关系数据"},
                "fields": {"type": "string", "description": "要显示的字段，逗号分隔（可选），默认显示前8个字段 只作为查询获取可以使用默认最少字段，显示全部使用all。"},
                "page": {"type": "integer", "description": "页码（默认为 1）", "default": 1},
                "limit": {"type": "integer", "description": "每页数量（默认为 20）", "default": 20},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["model_code"]
        }
    },
    "opsany_cmdb_get_model_group": {
        "name": "opsany_cmdb_get_model_group",
        "description": "资源平台，获取资源模型分组(创建模型时使用)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_type": {"type": "string", "description": "资源分组类型类型(zc:资产 yw:业务 zz:组织)"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": []
        }
    },
    "opsany_cmdb_get_model": {
        "name": "opsany_cmdb_get_model",
        "description": "资源平台，获取资源模型列表",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_type": {"type": "string", "description": "资源分组类型类型(zc:资产 yw:业务 zz:组织)"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": []
        }
    },
    "opsany_cmdb_create_model": {
        "name": "opsany_cmdb_create_model",
        "description": "资源平台，创建资源模型，创建资源模型后创建属性(字段)就可以在资源仓库创建该模型数据！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "模型code(模型唯一标识，建议使用全大写单词间隔为_ 如：CLOUD_SERVER)"},
                "name": {"type": "string", "description": "模型名称"},
                "model_type": {"type": "string", "description": "资源分组类型类型(zc:资产 yw:业务 zz:组织)", "default": "zc"},
                "model_group": {"type": "string", "description": "模型分组opsany_cmdb_get_model_group中code字段"},
                "clone_model": {"type": "string", "description": "克隆该模型字段信息，传入的是要克隆的模型code"},
                "built_in": {"type": "boolean", "description": "是否为内置", "default": False},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "name", "model_type", "model_group"]
        }
    },
    "opsany_cmdb_update_model": {
        "name": "opsany_cmdb_update_model",
        "description": "资源平台，修改资源模型，支持修改名称分组和是否内置！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "模型code(模型唯一标识，建议使用全大写单词间隔为_ 如：CLOUD_SERVER)"},
                "name": {"type": "string", "description": "模型名称"},
                "model_group": {"type": "string", "description": "模型分组opsany_cmdb_get_model_group中code字段"},
                "built_in": {"type": "boolean", "description": "是否为内置", "default": False},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "name", "model_type", "model_group"]
        }
    },
    "opsany_cmdb_delete_model": {
        "name": "opsany_cmdb_delete_model",
        "description": "资源平台，删除资源模型，谨慎删除，当模型没有数据才可以删除！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "模型code(模型唯一标识，建议使用全大写单词间隔为_ 如：CLOUD_SERVER)"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "name", "model_type", "model_group"]
        }
    },
    "opsany_cmdb_create_model_fields": {
        "name": "opsany_cmdb_create_model_fields",
        "description": f"资源平台，创建资源模型属性(字段)，仅支持创建普通字段is_relationship_field=''; 不支持创建关联关系字段 is_relationship_field=1 or ; {model_fields_attribute_md}",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "字段code,与model_code格式一致为大写(字段唯一标识格式为：{model_code}_{code}"},
                "name": {"type": "string", "description": "字段名称"},
                "type_name": {"type": "string", "description": "资源分组类型类型(zc:资产 yw:业务 zz:组织)", "default": "zc"},
                "model_code": {"type": "string", "description": "模型code opsany_cmdb_get_model中model_code"},
                "field_group_code": {"type": "string", "description": "字段分组opsany_cmdb_get_resource_fields中field_group_code"},
                "not_null": {"type": "boolean", "description": "是否为空(True为必填)", "default": False},
                "built_in": {"type": "boolean", "description": "是否为内置", "default": False},
                "index": {"type": "boolean", "description": "排序"},
                "attribute": {"type": "object", "description": "属性相关配置，固定格式，如提示 默认值 检验规则 下拉框数据等"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "name", "type_name", "model_code", "field_group_code", "attribute"]
        }
    },
    "opsany_cmdb_update_model_field": {
        "name": "opsany_cmdb_update_model_field",
        "description": f"资源平台，修改资源模型属性(字段)，支持修改名称分组和是否内置: {model_fields_attribute_md}！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "字段code,与model_code格式一致为大写(字段唯一标识格式为：{model_code}_{code}"},
                "name": {"type": "string", "description": "字段名称"},
                "type_name": {"type": "string", "description": "资源分组类型类型(zc:资产 yw:业务 zz:组织)", "default": "zc"},
                "model_code": {"type": "string", "description": "模型code opsany_cmdb_get_model中model_code"},
                "field_group_code": {"type": "string", "description": "字段分组opsany_cmdb_get_resource_fields中field_group_code"},
                "not_null": {"type": "boolean", "description": "是否为空(True为必填)", "default": False},
                "built_in": {"type": "boolean", "description": "是否为内置", "default": False},
                "index": {"type": "boolean", "description": "排序"},
                "attribute": {"type": "object", "description": "属性相关配置，固定格式，如提示 默认值 检验规则 下拉框数据等"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "name", "type_name", "model_code", "attribute"]
        }
    },
    "opsany_cmdb_delete_model_field": {
        "name": "opsany_cmdb_delete_model_field",
        "description": "资源平台，删除资源模型字段，谨慎删除，删除后该模型当前字段数据也会被清空！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "字段code"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code"]
        }
    },
    "opsany_cmdb_get_resource_link_inst_count": {
        "name": "opsany_cmdb_get_resource_link_inst_count",
        "description": "资源平台，获取某一资源的所有关联关系数据字段和实例总数，包括从属关系(is_relationship_field=1)和关联关系(is_relationship_field=2)！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": "资源ID（必填）"},
                "field_code": {"type": "string", "description": "关联关系字段（必填），opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系字段！"},
                # "search": {"type": "string", "description": "搜索关键词（可选）"},
                "current": {"type": "integer", "description": "页码， 打开第几页", "default": 1},
                "pageSize": {"type": "integer", "description": "页数，每页多少条！", "default": 20},
                "search_type": {"type": "integer", "description": "搜索字段"},
                "search_data": {"type": "integer", "description": "搜索数据"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "field_code"]
        }
    },
    "opsany_cmdb_get_resource_link_inst_list": {
        "name": "opsany_cmdb_get_resource_link_inst_list",
        "description": "资源平台，获取资源仓库某一数据的指定关联关系字段数据列表, 包括opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": "资源ID（必填）"},
                "field_code": {"type": "string", "description": "关联关系字段（必填），opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系字段！"},
                "current": {"type": "integer", "description": "页码， 打开第几页", "default": 1},
                "pageSize": {"type": "integer", "description": "页数，每页多少条！", "default": 20},
                "search_type": {"type": "integer", "description": "搜索字段"},
                "search_data": {"type": "integer", "description": "搜索数据"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "field_code"]
        }
    },
    "opsany_cmdb_get_can_add_link_inst_list": {
        "name": "opsany_cmdb_get_can_add_link_inst_list",
        "description": "资源平台，添加资源的关联关系字段数据时，拉取指定关联关系字段的待添加数据列表(拉取关联关系对端模型数据，已过滤添加过的数据)，包括opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": "资源ID（必填）"},
                "field_code": {"type": "string",
                               "description": "关联关系字段（必填），opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系字段！"},
                "current": {"type": "integer", "description": "页码， 打开第几页", "default": 1},
                "pageSize": {"type": "integer", "description": "页数，每页多少条！", "default": 20},
                "search_type": {"type": "integer", "description": "搜索字段"},
                "search_data": {"type": "integer", "description": "搜索数据"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "field_code"]
        }
    },
    "opsany_cmdb_resource_add_link_inst": {
        "name": "opsany_cmdb_resource_add_link_inst",
        "description": "资源平台，资源仓库给指定数据添加关联关系字段数据，opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系， 使用该工具操作。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": "资源ID（必填）"},
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "field_code": {"type": "string", "description": "关联关系字段（必填），opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系字段！"},
                "target_code_list": {"type": "array", "description": "目标实例ID, [10, 11, 12]！"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "model_code", "field_code", "target_code_list"]
        }
    },
    "opsany_cmdb_resource_remove_link_inst": {
        "name": "opsany_cmdb_resource_remove_link_inst",
        "description": "资源平台，资源仓库给指定数据移除关联关系字段数据，opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系， 使用该工具操作。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": "资源ID（必填）"},
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "field_code": {"type": "string", "description": "关联关系字段（必填），opsany_cmdb_get_resource_fields接口中is_relationship_field=2的字段为关联关系字段！"},
                "target_code": {"type": "array", "description": "目标实例ID, [10, 11, 12]！"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": ["code", "model_code", "field_code", "target_code"]
        }
    },
    "opsany_cmdb_create_resource": {
        "name": "opsany_cmdb_create_resource",
        "description": "资源平台，资源仓库新建数据，需要获取该模型字段后整理数据, data数据中仅支持普通字段(is_relationship_field="")和从属关系字段(is_relationship_field=1)，创建关联关系请使用opsany_cmdb_resource_add_link_inst工具。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "import_type": {"type": "string", "description": "导入来源"},
                "parent_inst": {"type": "string", "description": "从属关系资源ID，从属关系资源ID 从字段接口中is_relationship_field=1，attribute.引用模型为上级模型, 设置从属关系为空：set_null 设置从属关系：上级模型数据ID。"},
                "data": {
                    "type": "object",
                    "description": """数据对象，根据model_code拉取到的opsany_cmdb_get_resource_fields字段，创建数据;
                    案例：
                    model_code为SERVER, 获取到的字段为 SERVER_name，SERVER_VISIBLE_NAME，SERVER_HOSTNAME，SERVER_INTERNAL_IP等，
                    根据获取到的字段类型和attribute规则生成数据，key为字段标识(code)，value为数据
                    {
                        "SERVER_name": "linux-node1",
                        "SERVER_VISIBLE_NAME": "linux-node1",
                        "SERVER_HOSTNAME": "linux-node1",
                        "SERVER_INTERNAL_IP": "192.168.0.111",
                    }
                    """
                },
            },
            "required": ["model_code", "data"]
        }
    },
    "opsany_cmdb_update_resource": {
        "name": "opsany_cmdb_update_resource",
        "description": """资源平台，资源仓库新建数据，需要获取该模型字段后整理数据, 
                       data数据中仅支持普通字段(is_relationship_field="")和从属关系字段(is_relationship_field=1)，
                       修改关联关系(is_relationship_field=2)请使用opsany_cmdb_resource_add_link_inst或opsany_cmdb_resource_remove_link_inst或工具。
                       """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "code": {"type": "integer", "description": "资源ID"},
                "parent_inst": {"type": "string", "description": "从属关系资源ID，从属关系资源ID 从字段接口中is_relationship_field=1，attribute.引用模型为上级模型, 设置从属关系为空：set_null 设置从属关系：上级模型数据ID。"},
                "data": {
                    "type": "object",
                    "description": """数据对象，根据model_code拉取到的opsany_cmdb_get_resource_fields字段，创建数据，从属关系字段单独使用parent_inst传参，不在data内写该字段;
                    案例：
                    model_code为SERVER, 获取到的字段为 SERVER_name，SERVER_VISIBLE_NAME，SERVER_HOSTNAME，SERVER_INTERNAL_IP等，
                    根据获取到的字段类型和attribute规则生成数据，key为字段标识(code)，value为数据
                    {
                        "SERVER_name": "linux-node1",
                        "SERVER_VISIBLE_NAME": "linux-node1",
                        "SERVER_HOSTNAME": "linux-node1",
                        "SERVER_INTERNAL_IP": "192.168.0.111",
                    }
                    """
                },
            },
            "required": ["model_code", "code", "data"]
        }
    },
    "opsany_cmdb_delete_resource": {
        "name": "opsany_cmdb_delete_resource",
        "description": "资源平台，资源仓库删除数据，需要传入资源ID。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_code": {"type": "string", "description": "资源类型（必填）"},
                "code": {"type": "integer", "description": "资源ID"},
            },
            "required": ["model_code", "code"]
        }
    },
}

TOOL_RBAC_DICT = {
    "opsany_rbac_get_or_search_all_user": {
        "name": "opsany_rbac_get_or_search_all_user",
        "description": """统一权限平台，获取平台全部用户信息，仅支持管理员用户查看，普通用户可能会返回没有操作权限；支持用户名精准查找，中文名精准查找，
                       用户名模糊搜索，中文名称模糊搜索，中文名或用户名联合模糊搜索，支持扩展字段，包括部门用户认证来源等全部字段，使用 all。""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "用户名精准查找"
                },
                "chname": {
                    "type": "string",
                    "description": "中文名精准查找"
                },
                "search_username": {
                    "type": "string",
                    "description": "用户名模糊搜索"
                },
                "search_chname": {
                    "type": "string",
                    "description": "中文名称模糊搜索"
                },
                "search_username_or_chname": {
                    "type": "string",
                    "description": "中文名或用户名联合模糊搜索"
                },
                "extend": {
                    "type": "string",
                    "default": "all",
                    "description": "扩展字段，包括部门用户认证来源等全部字段，使用 all。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 60},
            },
            "required": []
        }
    },
    "opsany_rbac_get_my_user_info": {
        "name": "opsany_rbac_get_my_user_info",
        "description": "统一权限平台，获取自己的用户信息，当前用户信息，我是谁，支持扩展字段，包括部门用户认证来源等全部字段，使用 all。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "extend": {"type": "string", "description": "扩展字段，包括部门用户认证来源等全部字段，使用 all。"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_rbac_create_user": {
        "name": "opsany_rbac_create_user",
        "description": """
        统一权限平台，批量创建用，仅支持管理员用户操作，普通用户可能会返回没有操作权限；仅支持创建普通用户，创建管理员请前往统一权限平台操作！
        仅支持修改普通用户信息，暂时仅支持修改启用禁用
        参考案例:
            {
                "user_info_list": [
                    {
                        "username": "staff01", 
                        "chname": "用户01",
                        "password": "123456.coM",
                        "phone": "183xxxx",
                        "email": "xxx@xxx",
                    }
                ]
            }
        """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_info_list": {
                    "type": "array",
                    "description": """
                    用户信息列表, 元素为Dict类型数据字段包括
                        username, 用户名，字符串类型，必填；
                        chname, 中文名，字符串类型，必填；
                        password, 密码，字符串类型，必填；
                        phone, 手机号，字符串类型，不必填；
                        email, 邮箱，字符串类型，不必填；
                        position, 职位，字符串类型，不必填；
                        description, 描述信息，字符串类型，不必填；
                    """,
                    "items": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "用户名, 用户名只能输入数字、字母、下划线。"},
                            "chname": {"type": "string", "description": "中文名"},
                            "password": {"type": "string", "description": "密码, 密码只支持数字、字母或!@#$%^*()_-+=，长度在8-20个字符，且必须保证包含大小写字母和数字。"},
                            "phone": {"type": "string", "description": "手机号"},
                            "email": {"type": "string", "description": "邮箱"},
                            "position": {"type": "string", "description": "职位"},
                            "description": {"type": "string", "description": "描述信息"}
                        },
                        "required": ["username", "chname", "password"]
                    }
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 每增加一条建议延长5秒。", "default": 60},
            },
            "required": ["user_info_list"],
        }
    },
    "opsany_rbac_update_user": {
        "name": "opsany_rbac_update_user",
        "description": """统一权限平台，批量修改用户，仅支持管理员用户操作，普通用户可能会返回没有操作权限；
        仅支持修改普通用户信息，暂时仅支持修改启用禁用
        参考案例:
            {
                "user_info_list": [
                    {
                        "username": "staff01", "is_activate": true
                    }
                ]
            }
        """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_info_list": {
                    "type": "array",
                    "description": """用户信息列表, 元素为Dict类型数据字段包括
                        is_activate, 启用禁用，布尔值，必填；
                """,
                    "items": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "用户名"},
                            "is_activate": {"type": "boolean", "description": "启用禁用"},
                        },
                        "required": ["username", "is_activate"]
                    }
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 每增加一条建议延长5秒。", "default": 30},
            },
            "required": ["user_info_list"],

        }
    },
    "opsany_rbac_delete_user": {
        "name": "opsany_rbac_delete_user",
        "description": """
            统一权限平台，批量删除用户，仅支持管理员用户操作，普通用户可能会返回没有操作权限；仅支持删除普通用户，和被禁用的用户，
            当要删除的用户是启用状态，需要用户确认是否禁用后删除，参考案例
            {
                "user_info_list": ["staff01"]
            }
            """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_info_list": {
                    "type": "array",
                    "description": """username 用户名列表""",
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 每增加一条建议延长5秒。", "default": 60},

            },
            "required": ["user_info_list"]
        }
    },
}

TOOL_MONITOR_DICT = {
    "opsany_monitor_alert_info": {
        "name": "opsany_monitor_alert_info",
        "description": "基础监控，获取基础监控平台的实例告警，需要管控平台监控并纳管后，实例包括管控平台主机，网络设备！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {"type": "string", "description": "页码， 打开第几页"},
                "pageSize": {"type": "string", "description": "页数，每页多少条"},
                "host_name": {"type": "string", "description": "主机唯一标识和实例名称模糊搜索"},
                "name": {"type": "string", "description": "告警名称模糊搜索"},
                "severity": {"type": "string", "description": "根据告警级别搜索，0: 未分类 1: 信息 2: 警告 3: 一般严重 4: 严重 5: 灾难。"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 告警过多建议增加超时时间。", "default": 30},
            },
            "required": []
        }
    }
}

TOOL_WORKBENCH_DICT = {
    "opsany_workbench_work_order_inst": {
        "name": "opsany_workbench_work_order_inst",
        "description": "工作台，ITSM平台，获取全部工单，待办工单，我的已办工单，我提交的工单！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current": {
                    "type": "string",
                    "description": "页码， 打开第几页！"
                },
                "pageSize": {
                    "type": "string",
                    "description": "页数，每页多少条！"
                },
                "data": {
                    "type": "string",
                    "description": "工单的分类，全部工单: all 待办工单: will 我的已办工单:already 我提交的工单: self ！"
                },
                "order_by": {
                    "type": "string",
                    "description": "排序字段"
                },
                "status": {
                    "type": "string",
                    "description": "工单状态，0: 正在进行 1: 已经结束 2 ！"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_workbench_work_order_temp": {
        "name": "opsany_workbench_work_order_temp",
        "description": "工作台，ITSM平台，获取全部服务目录，包含全部服务，用来提单使用，会拉取授权的全部服务和服务相关字段！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "服务id，通过模板id获取到该服务项的详情和表单字段，获取单条需要使用form_fields字段，带上表单字段，以便提单！"
                },
                "form_fields": {
                    "type": "boolean",
                    "description": "是否包含表单字段"
                },
                "current": {
                    "type": "integer",
                    "description": "页码，打开第几页。"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "页数，每页多少条。"
                },
                "folder_id": {
                    "type": "string",
                    "description": "服务分类ID，搜索指定分类的服务, all: 全部分类 或分类id。"
                },
                "data_type": {
                    "type": "string",
                    "description": "服务类型，all： 全部类型 tags：我的收藏 request：请求管理 change：变更管理 event：事件管理 issues：问题管理 recently：最近提单。"
                },
                "name_or_describe": {
                    "type": "string",
                    "description": "模糊搜索， 主要搜索 名称(name)和描述(describe)。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_workbench_work_order_submit": {
        "name": "opsany_workbench_work_order_submit",
        "description": "工作台，ITSM平台，提单，根据opsany_workbench_work_order_temp拉取到的服务id和表单字段(field_list)提单！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "submit_from": {
                    "type": "string",
                    "description": "提交来源"
                },
                "work_order_id": {
                    "type": "integer",
                    "description": "服务ID"
                },
                "follow": {
                    "type": "boolean",
                    "description": "是否跟踪，当使用true，工单有状态变更会通知提单人。"
                },
                "field_dict": {
                    "type": "object",
                    "description": """表单内容，字段内容来服务项(opsany_workbench_work_order_temp field_list)中的字段!
                    field_type 字段描述：
                        select 下拉菜单：需要传入 field_list.other_info.selectOptions 中的选项数据，如{"key": "1"}
                        cascader 级联惨淡：需要传入 field_list.other_info.cascaderOptions 中的选项数据，如 {"key": "first_layer"}, {"key": "second_layer"}, {"key": "third_layer"}]
                        radio 单选： field_list.other_info.selectOptions 中的选项数据，如 {"key": "one"}
                        checkbox 多选： field_list.other_info.selectOptions 中的选项数据，如 [{"key": "one"},  {"key": "two"}]
                    """
                }
            },
            "required": ["submit_from", "work_order_id", "field_dict"]
        }
    },
}

TOOL_JOB_DICT = {
    "opsany_job_get_tool_market_list": {
        "name": "opsany_job_get_tool_market_list",
        "description": "作业平台 获取作业平台工具市场，包括作业列表和脚本列表！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_type": {
                    "type": "string",
                    "description": "工具市场类型：job: 作业 script: 脚本 all: 全部，作业名称字段为 name，描述字段为 describe；脚本名称字段为 script_name，描述字段为 version_remarks。"
                },
                "script_name": {
                    "type": "string",
                    "description": "模糊搜索脚本或作业名称"
                },
                "create_user": {
                    "type": "string",
                    "description": "模糊搜索创建人"
                },
                "job_id": {
                    "type": "integer",
                    "description": "查询某一条作业详情，包括 作业名称 创建人 创建时间 步骤列表，步骤内脚本信息等。"
                },
                "script_id": {
                    "type": "integer",
                    "description": "查询某一条脚本详情，包括 脚本名称 创建人 创建时间 脚本内容等。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_job_get_job_list": {
        "name": "opsany_job_get_job_list",
        "description": "作业平台 获取作业平台作业列表，只需要作业ID就可以执行的作业列表，作业名称字段为 name，描述字段为 describe！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "模糊搜索作业名称。"
                },
                "create_user": {
                    "type": "string",
                    "description": "模糊搜索创建人，支持用户名中文名联合模糊搜索。"
                },
                "job_id": {
                    "type": "integer",
                    "description": "查询某一条作业详情，包括 作业名称 创建人 创建时间 步骤列表，步骤内脚本信息等。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_job_get_script_list": {
        "name": "opsany_job_get_script_list",
        "description": "作业平台 获取作业平台脚本列表，该脚本执行需要脚本ID执行主机等参数，脚本名称字段为 script_name，描述字段为 version_remarks！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script_name": {
                    "type": "string",
                    "description": "模糊搜索脚本或作业名称"
                },
                "create_user": {
                    "type": "string",
                    "description": "模糊搜索创建人，支持用户名中文名联合模糊搜索。"
                },
                "script_id": {
                    "type": "integer",
                    "description": "查询某一条脚本详情，包括 脚本名称 创建人 创建时间 脚本信息等。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_job_run_job_by_id": {
        "name": "opsany_job_run_job_by_id",
        "description": "作业平台 根据作业ID执行作业， 返回的为任务ID, 可以根据任务ID获取执行结果, 根据返回的字段flag判断是否执行完成 True: 完成 False: 未完成。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "integer",
                    "description": "作业ID"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": ["job_id"]
        }
    },
    "opsany_job_run_script_by_id": {
        "name": "opsany_job_run_script_by_id",
        "description": "作业平台 根据脚本ID执行脚本， 返回的为任务ID, 可以根据任务ID获取执行结果！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script_id": {
                    "type": "integer",
                    "description": "作业ID"
                },
                "server": {
                    "type": "string",
                    "description": "主机唯一标识, 当有多条时用逗号隔开，该主机为管控平台纳管的主机。"
                },
                "parameter": {
                    "type": "string",
                    "description": "脚本参数",
                    "default": ""
                },
                "run_describe": {
                    "type": "string",
                    "description": "执行原因"
                },
                "time_out": {
                    "type": "integer",
                    "description": "脚本执行超时时间, 默认120s",
                    "default": 120
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": ["script_id", "server"]
        }
    },
    "opsany_job_get_run_result_by_log_id": {
        "name": "opsany_job_get_run_result_by_log_id",
        "description": "作业平台 获取执行的作业或脚本结果， 根据返回的任务ID获取！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "log_id": {
                    "type": "integer",
                    "description": "执行作业或脚本后返回的任务ID"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": ["log_id"]
        }
    },
    "opsany_job_create_script_library": {
        "name": "opsany_job_create_script_library",
        "description": "作业平台，创建脚本到脚本仓库，仅支持创建私有脚本！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script_type": {"type": "integer", "description": "脚本类型 "},
                "script_name": {"type": "integer", "description": "执行作业或脚本后返回的任务ID"},
                "version_remarks": {"type": "integer", "description": "执行作业或脚本后返回的任务ID"},
                "script": {"type": "integer", "description": "执行作业或脚本后返回的任务ID"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": ["log_id"]
        }
    },
}

TOOL_CONTROL_DICT = {
    "opsany_control_get_managed_host_list": {
        "name": "opsany_control_get_managed_host_list",
        "description": """管控平台 获取管控平台纳管的主机列表，
                       该数据来自资源平台主机组内三个模型的数据(SERVER,CLOUD_SERVER,VIRTUAL_SERVER)！""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host_name_search": {
                    "type": "string",
                    "description": "根据主机唯一标识模糊搜索纳管主机"
                },
                "show_name_search": {
                    "type": "string",
                    "description": "根据主机名称模糊搜索纳管主机"
                },
                "ip_search": {
                    "type": "string",
                    "description": "根据主机名唯一标识模糊搜索纳管主机"
                },
                "id": {
                    "type": "integer",
                    "description": "根据主机ID查询纳管主机, 精准查询。"
                },
                "host_name": {
                    "type": "string",
                    "description": "根据主机ID查询纳管主机, 精准查询。"
                },
                "show_name": {
                    "type": "string",
                    "description": "根据主机ID查询纳管主机, 精准查询。"
                },
                "ip": {
                    "type": "string",
                    "description": "根据主机IP查询纳管主机, 精准查询。"
                },
                "system_type": {
                    "type": "string",
                    "description": "根据主机系统类型查询纳管主机，查询全部忽略该字段，Linux Windows"
                },
                "host_type": {
                    "type": "string",
                    "description": "查根据主机类型查询纳管主机(对应资源平台主机组内模型SERVER,CLOUD_SERVER,VIRTUAL_SERVER，"
                                   "查询全部忽略该字段，查询多个使用逗号隔开)。"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 30},
            },
            "required": []
        }
    },
    "opsany_control_get_controller_list": {
        "name": "opsany_control_get_controller_list",
        "description": "管控平台 获取管控平台控制器(Proxy)列表，纳管主机时使用，将主机纳管在该控制器下。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "根据控制名称搜索"},
                "id": {"type": "integer", "description": "根据控制ID获取控制器详情"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 10},
            },
            "required": []
        }
    },
    "opsany_control_get_host_group_list": {
        "name": "opsany_control_get_host_group_list",
        "description": "管控平台 获取管控平台主机分组列表，纳管主机时使用，将主机添加至该分组，分组支持嵌套。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 10},
            }
        }
    },
    "opsany_control_get_zabbix_list": {
        "name": "opsany_control_get_zabbix_list",
        "description": "管控平台 获取管控平台监控插件 基础监控插件ZabbixServer列表，纳管主机添加监基础控插件时使用，将主机使用该插件监控，可在基础监控平台查看。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 10},
            }
        }
    },
    "opsany_control_get_prometheus_list": {
        "name": "opsany_control_get_prometheus_list",
        "description": "管控平台 获取管控平台监控插件 应用监控插件PrometheusServer列表，纳管主机添加应用监控插件时使用，将主机使用该插件监控，可在应用监控平台查看。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 10},
            }
        }
    },
    "opsany_control_get_dashboard_list": {
        "name": "opsany_control_get_dashboard_list",
        "description": "管控平台 获取管控平台监控大屏列表，纳管主机添加监控插件时使用，根据标签判断 将主机使用该插件监控，可在应用监控平台查看。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dashboard_type": {"type": "string", "description": "大屏类型 Prometheus 或 Zabbix，选择监控插件时使用！"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 10},
            },
            "required": ["dashboard_type"]
        }
    },
    "opsany_control_get_zabbix_temp_list": {
        "name": "opsany_control_get_zabbix_temp_list",
        "description": "管控平台 获取管控平台Zabbix监控模板列表，纳管主机添加Zabbix监控插件时使用。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "zabbix_id": {
                    "type": "string", "description": "通过opsany_control_get_zabbix_list获取Zabbix实例ID，选择监控插件时使用！"
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间", "default": 20},
            },
            "required": ["zabbix_id"]
        }
    },
    "opsany_control_create_host": {
        "name": "opsany_control_create_host",
        "description": "管控平台 添加纳管主机，需要输入主机唯一标识， 主机IP,主机端口，系统用户，需要选择控制器，选择操作系统，管控方式，分组主机类型等，也可以添加Zabbix监控插件或Prometheus监控插件，需要传入指定参数。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host_info_list": {
                    "type": "array",
                    "description": "批量纳管主机列表，主机信息在列表中。",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "主机唯一标识(执行脚本等操作需要传入该唯一标识)！"},
                            "show_name": {"type": "string", "description": "主机显示名！"},
                            "ip": {"type": "string", "description": "主机IP地址！"},
                            "system_type": {
                                "type": "string",
                                "enum": ["Linux", "Windows"],
                                "default": "password",
                                "description": "主机操作系统，仅支持Linux Windows！"
                            },
                            "controller_id": {
                                "type": "integer",
                                "description": "控制器，选择控制器ID根据工具 opsany_control_get_controller_list 获取到的ID(字段为id)！"
                            },
                            "control_type": {
                                "type": "integer", "enum": [1, 2, 3, 4],
                                "default": 1,
                                "description": "管控方式，主机纳管方式包含四种 1: SSH 2: Agent 3: SSH/Agent 4: Agent/SSH。"
                            },
                            "ssh_port": {
                                "type": "string",
                                "default": "22",
                                "description": "主机端口，当主机操作系统为Linux时需要输入SSH端口，端口范围为1-65535，默认 22！",
                            },
                            "login_port": {
                                "type": "string",
                                "description": "主机远程登录端口，当主机操作系统为Windows时需要输入RDP端口, 端口范围为1-65535，默认 3389！",
                            },
                            "username": {
                                "type": "string",
                                "default": "root",
                                "description": "主机系统用户, 登录或纳管主机使用的主机系统用户！"
                            },
                            "group_id": {
                                "type": "integer",
                                "description": "主机分组，分组id根据工具 opsany_control_get_host_group_list 获取戴的ID(字段为code)，当分组结构为 第一层/第二层/第三层 指向的是嵌套到第三层的分组！"
                            },
                            "ssh_type": {
                                "type": "string",
                                "enum": ["password"],
                                "default": "password",
                                "description": "密码类型，默认 password！",
                            },
                            "password": {
                                "type": "string",
                                "description": "密码，主机密码！"
                            },
                            "host_type": {
                                "type": "string",
                                "enum": ["SERVER", "VIRTUAL_SERVER"],
                                "description": "主机类型，创建主机成功后会将主机同步至CMDB(资源平台)主机模型内，支持两种主机类型： 物理机: SERVER 虚拟机: VIRTUAL_SERVER！",
                            },
                            "privilege": {
                                "type": "boolean",
                                "description": "特权提升(sudo)，是否开启特权提升 当system_type(操作系统)选择Linux 且 control_type(管控方式)包含SSH，true 或 false！"
                            },
                            "privilege_type": {
                                "type": "string",
                                "enum": ["sudo", "su"],
                                "description": "特权类型，两个选项 sudo 或 su, 当 privilege 为 true 时使用！"
                            },
                            "privilege_username": {
                                "type": "string",
                                "description": "特权用户名, 当 privilege 为 true 时使用！"
                            },
                            "privilege_password": {
                                "type": "string",
                                "description": "特权密码, 当 privilege 为 true 时使用！"
                            },
                            "monitor_type": {
                                "type": "string",
                                "enum": ["Zabbix", "Prometheus"],
                                "description": """
                                选择监控插件， 支持主机安装监控插件， 根据监控插件进行监控，支持 Zabbix 或 Prometheus
                                当选择Zabbix需要传入参数:
                                    1. controller_zabbix(ZabbixServer)
                                    2. template_list(Zabbix监控模板)！
                                    3. dashboard_dict(大屏需要拉取dashboard_type=Zabbix数据)
                                当选择Prometheus需要传入参数:
                                    1. controller_prom(PrometheusServer)
                                    3. dashboard_dict(大屏需要拉取dashboard_type=prometheus)
                                """,
                            },
                            "controller_zabbix": {
                                "type": "string",
                                "description": "选择监控插件实例，当monitor_type参数使用Zabbix时需要传入该参数！"
                            },
                            "controller_prom": {
                                "type": "string",
                                "description": "选择监控插件实例，当monitor_type参数使用Prometheus时需要传入该参数！"
                            },
                            "bind_port": {
                                "type": "integer",
                                "default": 9101,
                                "description": "选择监控插件实例，当monitor_type参数使用Prometheus时，且需要自定义端口时需要传入该参数！"
                            },
                            "is_bastion": {
                                "type": "boolean",
                                "default": "false",
                                "description": "是否将资源同步到堡垒机！"
                            },
                            "is_bastion_group": {
                                "type": "boolean",
                                "default": "false",
                                "description": "是否将资源同步到堡垒机，并将主机分组同步至堡垒机分组，false: 同步到堡垒机默认分组， 当is_bastion是true时使用！"
                            },
                            "reinstall_zabbix_agent": {
                                "type": "boolean",
                                "default": "true",
                                "description": "选择监控插件实例，当monitor_type参数使用Zabbix时，是否需要自动安装监控插件！"
                            },
                            "reinstall_prom_exporter": {
                                "type": "boolean",
                                "default": "true",
                                "description": "选择监控插件实例，当monitor_type参数使用Prometheus时，是否需要自动安装监控插件！"
                            },
                            "template_list": {
                                "type": "array",
                                "description": "Zabbix监控模板列表，包含模板名称和ID，当monitor_type参数使用Zabbix时需要传入该参数。",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "temp_name": {
                                            "type": "string",
                                            "description": "模板名称"
                                        },
                                        "temp_id": {
                                            "type": "string",
                                            "description": "模板ID"
                                        }
                                    },
                                    "required": ["temp_name", "temp_id"]
                                }
                            },
                            "dashboard_dict": {
                                "type": "object",
                                "description": "Grafana大屏信息，当使用monitor_type参数时需要传入大屏！",
                                "properties": {
                                    "uid": {
                                        "type": "string",
                                        "description": "大屏唯一标识符"
                                    },
                                    "title": {
                                        "type": "string",
                                        "description": "大屏标题"
                                    },
                                    "url": {
                                        "type": "string",
                                        "description": "大屏访问URL"
                                    },
                                    "tags": {
                                        "type": "array",
                                        "description": "大屏标签列表",
                                        "items": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "required": ["uid", "title", "url", "tags"]
                            }
                        },
                        "required": ["name", "show_name", "ip", "system_type", "controller_id", "control_type",
                                     "username", "group_id", "host_type"]
                    }
                },
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间，每增加一台建议延长2秒。", "default": 30},
            },
            "required": ["host_info_list"],
        }
    },
}

TOOL_PROM_DICT = {
    "opsany_prom_alert_info": {
        "name": "opsany_prom_alert_info",
        "description": "应用监控，获取应用监控平台的实例告警，包括管控平台纳管并使用Prometheus的后，在组件监控接入的实例告警和服务拨测告警！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "alert_type": {"type": "string", "description": "告警类型 node：主机或组件告警 blackbox：服务拨测告警 all: 全部告警"},
                "severity": {"type": "string", "description": "根据告警级别搜索，NotClassified: 未分类 Information: 信息 Warning: 警告 Average: 一般严重 High: 严重 Disaster: 灾难。"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 告警过多建议增加超时时间。", "default": 30},
            },
            "required": []
        }
    }
}

TOOL_EVENT_DICT = {
    "opsany_event_alert_info": {
        "name": "opsany_event_alert_info",
        "description": "事件中心，获取事件中心我的告警和全部告警，可获取到待处理，处理中，已关闭告警；包括管控平台Prometheus(应用监控)，Zabbix(基础监控)纳管和监控的实例和第三方接入的告警, 获取告警优先拉取事件中心告警，包含分派给我的告警和全部告警！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "alert_type": {"type": "string", "description": "告警类型 node：主机或组件告警 blackbox：服务拨测告警 all: 全部告警"},
                "severity": {"type": "string", "description": "根据告警级别搜索，NotClassified: 未分类 Information: 信息 Warning: 警告 Average: 一般严重 High: 严重 Disaster: 灾难。"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 告警过多建议增加超时时间。", "default": 30},
            },
            "required": []
        }
    }
}

TOOL_KBASE_DICT = {
    "opsany_kbase_read_kbase_list": {
        "name": "opsany_kbase_read_kbase_list",
        "description": "知识库，获取知识库平台全部知识库，知识库内有各类文章和文档！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_type": {"type": "string", "description": "数据类型：all:全部知识库, public:公共知识库, involved:我参与的知识库, favorite:我收藏的知识库, owner: 我拥有的知识库"},
                "search_type": {"type": "string", "description": "根据字段搜索支持：name:名称： description:描述！"},
                "search_data": {"type": "string", "description": "搜索数据，与search_type同时使用！"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 告警过多建议增加超时时间。", "default": 30},
            },
            "required": []
        }
    },
    "opsany_kbase_read_kbase_article": {
        "name": "opsany_kbase_read_kbase_article",
        "description": "知识库，获取知识库平台某一知识库内文章和文档，可获取列表和单条数据！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "unique_code": {"type": "string", "description": "文章唯一标识用获取单条文章内容"},
                "data_type": {"type": "string", "description": "数据类型：all:全部文章, self:我的文章, folder:根据目录筛选文章, favorite:我收藏的文章, single:单条"},
                "kbase": {"type": "string", "description": "知识库唯一标识：opsany_kbase_read_kbase_list中unique_code字段"},
                "current": {"type": "string", "description": "当前页码"},
                "pageSize": {"type": "string", "description": "每页条数"},
                "search_type": {"type": "string", "description": "根据字段搜索支持：title:文章标题！"},
                "search_data": {"type": "string", "description": "搜索数据，与search_type同时使用！"},
                "tool_timeout": {"type": "integer", "description": "工具请求超时时间, 告警过多建议增加超时时间。", "default": 30},
            },
            "required": []
        }
    }
}


TOOL_K8S_DICT = {}
TOOL_LLMOPS_DICT = {}
TOOL_AUTO_DICT = {}
TOOL_LOG_DICT = {}
TOOL_APM_DICT = {}
TOOL_LIST = {}


def _get_tool(licence="ce"):
    print(licence)
    TOOL_DICT = TOOL_CMDB_DICT | TOOL_RBAC_DICT | TOOL_MONITOR_DICT | TOOL_WORKBENCH_DICT | TOOL_JOB_DICT | TOOL_CONTROL_DICT
    if licence in ["se", "ee"]:
        TOOL_DICT |= TOOL_PROM_DICT | TOOL_K8S_DICT | TOOL_KBASE_DICT | TOOL_LLMOPS_DICT
    if licence in ["ee"]:
        TOOL_DICT |= TOOL_EVENT_DICT | TOOL_AUTO_DICT | TOOL_LOG_DICT | TOOL_APM_DICT

    TOOL_DICT.pop("opsany_workbench_work_order_folder", None)
    TOOL_DICT.pop("opsany_job_run_script_by_script", None)
    TOOL_LIST = list(TOOL_DICT.values())
    return TOOL_LIST


if __name__ == '__main__':
    print(_get_tool("ee"))
