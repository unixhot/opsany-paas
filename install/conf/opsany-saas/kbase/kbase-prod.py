# -*- coding: utf-8 -*-
from config import RUN_VER

if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa
import mongoengine

# 正式环境
RUN_MODE = 'PRODUCT'

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = 'ERROR'

UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/opt/opsany/")
# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# MySQL Config
DATABASES.update(
    {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': APP_CODE,  # 数据库名
            'USER': APP_CODE,  # 数据库用户
            'PASSWORD': os.getenv("MYSQL_PASSWORD", "MYSQL_OPSANY_KBASE_PASSWORD"),  # 数据库密码
            'HOST': os.getenv("MYSQL_HOST", "MYSQL_SERVER_IP"),  # 数据库主机
            'PORT': int(os.getenv("MYSQL_PORT", "MYSQL_SERVER_PORT")),  # 数据库端口
            'OPTIONS': {
                "init_command": "SET default_storage_engine=INNODB",
            }

        },
    }
)


# MongoDB Config
MONGO_CONN = mongoengine.connect(
    db=APP_CODE,  # 需要进行操作的数据库名称
    alias='default',  # 必须定义一个default数据库
    host=os.getenv("MONGO_HOST", "MONGO_SERVER_IP"),
    port=int(os.getenv("MONGO_PORT", "MONGO_SERVER_PORT")),
    username=APP_CODE,
    password=os.getenv("MONGO_PASSWORD", "MONGO_KBASE_PASSWORD"),
    connect=False,
    # authentication_source="admin",           # 进行身份认证的数据库，通常这个数据库为admin
)

FILE_UPLOAD_ENDSWITH_LIST = [
    # 图片格式
    " bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps", "ai", "raw", "wmf", "webp", "avif", "apng",
    # 文件格式
    "doc","docx", "xls", "xlsx", "ppt", "pptx", "pot", "pps", "txt", "md", "xsl", "mind", "ps", "eps", "xmind", "xmmap", "mmap",
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

CORS_ALLOW_CREDENTIALS = True

