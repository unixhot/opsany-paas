"""
    mysql-connector==2.2.9
    SQLAlchemy==1.4.22
"""

import os
import sys
import configparser
from sqlalchemy import Column, String, create_engine, Index
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.orm import  sessionmaker
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
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")),
             "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD",
             "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_EVENT_PASSWORD")), "env_scope": "all",
             "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")),
             "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all",
             "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")),
             "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")),
             "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_EVENT_PASSWORD")),
             "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": os.environ.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    }, {
        "app_code": "auto",
        "env": [
            # AUTO  共计6个
            {"key": "MYSQL_PASSWORD",
             "value": replace_str(config_dict.get('enterprise').get("MYSQL_OPSANY_AUTO_PASSWORD")), "env_scope": "all",
             "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")),
             "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all",
             "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")),
             "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")),
             "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('enterprise').get("MONGO_AUTO_PASSWORD")),
             "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": os.environ.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    }
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

    def add_ee_env(self):
        for env in self.envs:
            app_code = env.get("app_code")
            env_list = env.get("env")
            for env_dict in env_list:
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


if __name__ == '__main__':
    AddEEEnv().add_ee_env()
    print("EE ENV INPUT IS DONE, SUCCESS.")
