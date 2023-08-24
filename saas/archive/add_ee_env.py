# coding=utf-8
"""
    mysql-connector==2.2.9
    SQLAlchemy==1.4.22
"""
import argparse
import os
import sys
import configparser
from sqlalchemy import Column, String, create_engine, Index
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import parse

# change dir to install
os.chdir('../install')
# testify file if exists
if not os.path.exists('install.config'):
    sys.exit('install config is not exists.')

read_install_config = configparser.ConfigParser()
try:
    read_install_config.read('install.config')
    config_dict = dict(read_install_config)
except Exception as e:
    print(e)
    sys.exit('file context is wrong.')


def replace_str(data):
    if not data:
        return None
    return data.replace("\"", "").replace("\'", "")


MYSQL_SERVER_IP = replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP", "10.0.0.80"))
MYSQL_ROOT_PASSWORD = replace_str(config_dict.get("mysql").get("MYSQL_ROOT_PASSWORD", "OpsAny@2020"))

try:
    db = create_engine(
        "mysql+mysqlconnector://root:{}@{}/opsany_paas".format(parse.quote_plus(MYSQL_ROOT_PASSWORD), MYSQL_SERVER_IP))
    Base = declarative_base(db)


    def to_dict(self):
        return {c.name: getattr(self, c.name, None)
                for c in self.__table__.columns}


    Base.to_dict = to_dict
except Exception as e:
    print("Script error: {}".format(str(e)))
    sys.exit('connect sql is failed. Please check mysql server!')

envs = [
    {
        "app_code": "event",
        "env": [
            # EVENT  共计7个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_EVENT_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_EVENT_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": os.environ.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },
    {
        "app_code": "auto",
        "env": [
            # AUTO  共计7个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_AUTO_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_AUTO_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": os.environ.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },
    {
        "app_code": "prom",
        "env": [
            # PROM  共计12个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_PROM_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_PROM_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            {"key": "ELASTIC_SEARCH_USERNAME", "value": replace_str(config_dict.get('elasticsearch').get("ELASTIC_SEARCH_USERNAME")), "env_scope": "all", "intro": "es username"},
            {"key": "ES_PASSWORD", "value": replace_str(config_dict.get('elasticsearch').get("ES_PASSWORD")), "env_scope": "all", "intro": "es password"},
            {"key": "ES_SERVER_IP", "value": replace_str(config_dict.get('elasticsearch').get("ES_SERVER_IP")), "env_scope": "all", "intro": "es host"},
            {"key": "ELASTIC_PORT", "value": replace_str(config_dict.get('elasticsearch').get("ELASTIC_PORT")), "env_scope": "all", "intro": "es port"},
            {"key": "ELASTIC_SEARCH_INDEX", "value": replace_str(config_dict.get('elasticsearch').get("ELASTIC_SEARCH_INDEX")), "env_scope": "all", "intro": "es index"},
        ]
    },
    {
        "app_code": "k8s",
        "env": [
            # K8S  共计4个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_K8S_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
        ]
    },
    {
        "app_code": "kbase",
        "env": [
            # KABASE  共计7个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_KBASE_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_KBASE_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": os.environ.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },
    {
        "app_code": "log",
        "env": [
            # LOG  共计4个
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_LOG_PASSWORD")), "env_scope": "all","intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
        ]
    },
]


class PaasAppEnvvar(Base):
    __tablename__ = 'paas_app_envvars'
    __table_args__ = (
        Index('paas_app_envvars_app_code_36685348c7256adf_uniq', 'app_code', 'mode', 'name', unique=True),
    )

    id = Column(INTEGER(11), primary_key=True)
    app_code = Column(String(30), nullable=False)
    mode = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False)
    value = Column(String(1024), nullable=False)
    intro = Column(LONGTEXT)


class AddEEEnv:
    def __init__(self):
        cursor = sessionmaker(bind=db)
        self.session = cursor()
        self.envs = envs

    def add_ee_env(self, cover=False):
        for env in self.envs:
            app_code = env.get("app_code")
            env_list = env.get("env")
            for env_dict in env_list:
                key = env_dict.get("key")
                value = env_dict.get("value", "")
                try:
                    env_query = self.session.query(PaasAppEnvvar).filter(
                        PaasAppEnvvar.app_code == app_code,
                        PaasAppEnvvar.name == env_dict.get("key")
                    ).first()
                    if not env_query:
                        create_query = PaasAppEnvvar(app_code=app_code,
                                                     name=env_dict.get("key", ""),
                                                     value=env_dict.get("value", ""),
                                                     mode=env_dict.get("env_scope", "all"),
                                                     intro=env_dict.get("intro", ""),
                                                     )
                        self.session.add(create_query)
                        self.session.commit()
                        print("For {} create env info: key={} value={}".format(app_code, env_dict.get("key"),
                                                                               env_dict.get("value")))
                    else:
                        if cover:
                            self.session.query(PaasAppEnvvar).filter(
                                PaasAppEnvvar.id == env_query.id).update({
                                "mode": env_dict.get("env_scope", "all"),
                                "name": env_dict.get("key", ""),
                                "value": env_dict.get("value", ""),
                                "intro": env_dict.get("intro", ""),
                                "app_code": app_code,
                            })
                            self.session.commit()
                            print("For {} update env info: key={} value={}".format(app_code, env_dict.get("key"),
                                                                                   env_dict.get("value")))
                except Exception as e:
                    print("Error {} create env error: key={} value={}, {}".format(env.get("app_code"), key, value, str(e)))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--cover", help="1: 强制覆(当有该变量时，强制覆盖为新数据，适用于批量修改密码) 2: 不覆盖(当有数据时不做操作，只新建不存在数据，适用于增加新变量)", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    # cover 是否覆盖
    # True 强制覆(当有该变量时，强制覆盖为新数据，适用于批量修改密码)
    # False 不覆盖(当有数据时不做操作，只新建不存在数据，适用于增加新变量)
    parameter = add_parameter()
    options = parameter.parse_args()
    cover = options.cover
    if not cover:
        cover = False
    elif cover == "1":
        cover = True
    else:
        cover = False
    AddEEEnv().add_ee_env(cover)
    print("EE ENV INPUT IS DONE, SUCCESS.")
    
    """
    # 强制覆盖环境变量(当有该变量时，强制覆盖为新数据，适用于批量修改)
    python3 add_ee_env.py --cover 1
    # 只新增环境变量(当有变量存在时不做操作，只新建不存在数据，适用于增加新变量)
    python3 add_ee_env.py --cover 2
    """
