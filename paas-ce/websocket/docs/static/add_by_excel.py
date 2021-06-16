import os
import sys
import xlrd


def read_xlsx():
    file = "control.xlsx"
    book = xlrd.open_workbook(file)
    table = book.sheet_by_name("host")
    rows = table.nrows
    lt = []
    for i in range(1, rows):
        dt1 = dict(zip(table.row_values(0), table.row_values(i)))
        dt1["xlsx_id"] = i + 1
        lt.append(dt1)
    return lt


def proccess_data(dt1):
    dt1.pop("xlsx_id", "")
    dt1["control_type"] = "Agent"
    dt1["agent_state"] = "Agent未安装"
    dt1["controller_id"] = 1
    dt1["platform"] = "control"
    dt1["host_type"] = "SERVER"
    dt1["ssh_type"] = "password"
    dt1["system_type"] = "Linux"
    return dt1


def add_by_xlsx():
    lt = read_xlsx()
    for i in lt:
        name = i.get("name")
        a = AgentAdmin.fetch_one(name=name)
        if not a:
            end_data = proccess_data(i)
            AgentAdmin.create(**end_data)
        else:
            print("Excel中第{}行数据，唯一值重复，添加失败".format(i.get("xlsx_id")))


if __name__ == '__main__':
    """
    注意事项：
        1.xlsx中必须要求每列都是文本格式（左上角带绿色的角标）
        2.使用管控平台的虚拟环境，额外新增了xlrd依赖
        3.使用的配置项为项目的prod配置文件链接的数据库
    """
    parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("BK_ENV", "production")
    sys.path.append(parent_path)
    import django
    django.setup()
    from control.models import AgentAdmin
    add_by_xlsx()
