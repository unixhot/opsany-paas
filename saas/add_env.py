"""
    mysql-connector==2.2.9
    SQLAlchemy==1.4.22
"""

import os
import sys
import datetime
import configparser
from sqlalchemy import Column, DateTime, ForeignKey, String, create_engine, Index
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT, SMALLINT, TINYINT
from sqlalchemy.orm import relationship, sessionmaker
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

MYSQL_SERVER_IP = replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP", "127.0.0.1"))
MYSQL_ROOT_PASSWORD = replace_str(config_dict.get("mysql").get("MYSQL_ROOT_PASSWORD", "OpsAny@2020"))

try:

    db = create_engine("mysql+mysqlconnector://root:{}@{}/opsany_paas".format(parse.quote_plus(MYSQL_ROOT_PASSWORD), MYSQL_SERVER_IP))
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
        "app_code": "cmdb",
        "env": [
            # CMDB count 8
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_CMDB_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_CMDB_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": read_install_config.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },{
        "app_code": "cmp",
        "env": [
            # CMP count 7
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_CMP_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_CMP_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": read_install_config.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },{
        "app_code": "job",
        "env": [
            # JOB  count 10
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_JOB_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "FILE_ROOT", "value": replace_str(config_dict.get('opsany_saas').get("FILE_ROOT")), "env_scope": "all", "intro": "Salt file root"},
            {"key": "PILLAR_ROOT", "value": replace_str(config_dict.get('opsany_saas').get("PILLAR_ROOT")), "env_scope": "all", "intro": "Salt pillar root"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_JOB_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            {"key": "REDIS_HOST", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_IP")), "env_scope": "all", "intro": "redis host"},
            {"key": "REDIS_PORT", "value": replace_str(config_dict.get("redis").get("REDIS_PORT")), "env_scope": "all", "intro": "redis port"},
            {"key": "REDIS_PASSWORD", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_PASSWORD")), "env_scope": "all", "intro": "redis password"},
            # {"key": "DEFAULT_USER_ICON", "value": read_install_config.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },{
        "app_code": "workbench",
        "env": [
            # WORKBENCH  count 7
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_WORKBENCH_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_WORKBENCH_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
        ]
    },{
        "app_code": "rbac",
        "env": [
            # RBAC  count 4
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_RBAC_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
        ]
    },{
        "app_code": "monitor",
        "env": [
            # MONITOR  count 10
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_MONITOR_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_MONITOR_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            {"key": "ELASTIC_HOST", "value": replace_str(config_dict.get('elasticsearch').get("ES_SERVER_IP")), "env_scope": "all", "intro": "es host"},
            {"key": "ELASTIC_PORT", "value": replace_str(config_dict.get('elasticsearch').get("ELASTIC_PORT")), "env_scope": "all", "intro": "es port"},
            {"key": "ELASTIC_PASSWORD", "value": replace_str(config_dict.get('elasticsearch').get("ES_PASSWORD")), "env_scope": "all", "intro": "es password"},
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
        ]
    },{
        "app_code": "control",
        "env": [
            # CONTROL  count 13
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_CONTROL_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_CONTROL_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            {"key": "REDIS_HOST", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_IP")), "env_scope": "all", "intro": "redis host"},
            {"key": "REDIS_PORT", "value": replace_str(config_dict.get("redis").get("REDIS_PORT")), "env_scope": "all", "intro": "redis port"},
            {"key": "REDIS_PASSWORD", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_PASSWORD")), "env_scope": "all", "intro": "redis password"},
            {"key": "ROSTER_FILE_URL", "value": replace_str(config_dict.get('opsany_saas').get("ROSTER_FILE_URL")), "env_scope": "all", "intro": "roster file path"},
            {"key": "SALT_SSH_FILE_URL", "value": replace_str(config_dict.get('opsany_saas').get("SALT_SSH_FILE_URL")), "env_scope": "all", "intro": "salt ssh file path"},
            {"key": "ANSIBLE_HOST_KEY_CHECKING", "value": replace_str(config_dict.get("opsany_saas").get("ANSIBLE_HOST_KEY_CHECKING")), "env_scope": "all", "intro": "ansible vs host checking"},
            # {"key": "DEFAULT_USER_ICON", "value": read_install_config.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },{
        "app_code": "devops",
        "env": [
            # devops  count 8
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_DEVOPS_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "MONGO_HOST", "value": replace_str(config_dict.get('mongodb').get("MONGO_SERVER_IP")), "env_scope": "all", "intro": "mongo host"},
            {"key": "MONGO_PORT", "value": replace_str(config_dict.get('mongodb').get("MONGO_PORT")), "env_scope": "all", "intro": "mongo port"},
            {"key": "MONGO_PASSWORD", "value": replace_str(config_dict.get('mongodb').get("MONGO_DEVOPS_PASSWORD")), "env_scope": "all", "intro": "mongo password"},
            # {"key": "DEFAULT_USER_ICON", "value": read_install_config.get("DEFAULT_USER_ICON"), "env_scope": "all", "intro": "user default icon"},
        ]
    },{
        "app_code": "bastion",
        "env": [
            # bastion  count 8
            {"key": "UPLOAD_PATH", "value": replace_str(config_dict.get('opsany_saas').get("UPLOAD_PATH")), "env_scope": "all", "intro": "uploads path"},
            {"key": "MYSQL_PASSWORD", "value": replace_str(config_dict.get('mysql').get("MYSQL_OPSANY_BASTION_PASSWORD")), "env_scope": "all", "intro": "mysql password"},
            {"key": "MYSQL_HOST", "value": replace_str(config_dict.get('mysql').get("MYSQL_SERVER_IP")), "env_scope": "all", "intro": "mysql host"},
            {"key": "MYSQL_PORT", "value": replace_str(config_dict.get('mysql').get("MYSQL_PORT")), "env_scope": "all", "intro": "mysql port"},
            {"key": "REDIS_HOST", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_IP")), "env_scope": "all", "intro": "redis host"},
            {"key": "REDIS_PORT", "value": replace_str(config_dict.get("redis").get("REDIS_PORT")), "env_scope": "all", "intro": "redis port"},
            {"key": "REDIS_PASSWORD", "value": replace_str(config_dict.get("redis").get("REDIS_SERVER_PASSWORD")), "env_scope": "all", "intro": "redis password"},
            {"key": "TERMINAL_TIMEOUT", "value": replace_str(config_dict.get("redis").get("TERMINAL_TIMEOUT")), "env_scope": "all", "intro": "terminal timeout"},
        ]
    }
]


class PaasApptag(Base):
    __tablename__ = 'paas_apptags'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    code = Column(String(30), nullable=False, unique=True)
    index = Column(INTEGER(11), nullable=False)


class PaasApp(Base):
    __tablename__ = 'paas_app'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    code = Column(String(30), nullable=False, unique=True)
    introduction = Column(LONGTEXT, nullable=False)
    creater = Column(String(20), nullable=False)
    created_date = Column(DateTime, index=True)
    state = Column(SMALLINT(6), nullable=False)
    is_already_test = Column(TINYINT(1), nullable=False)
    is_already_online = Column(TINYINT(1), nullable=False)
    first_test_time = Column(DateTime, index=True)
    first_online_time = Column(DateTime, index=True)
    language = Column(String(50))
    auth_token = Column(String(36))
    tags_id = Column(ForeignKey('paas_apptags.id'), index=True)
    deploy_token = Column(LONGTEXT)
    is_use_celery = Column(TINYINT(1), nullable=False)
    is_use_celery_beat = Column(TINYINT(1), nullable=False)
    is_saas = Column(TINYINT(1), nullable=False)
    logo = Column(String(100))

    tags = relationship('PaasApptag')


class EngineApp(Base):
    __tablename__ = 'engine_apps'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(20), nullable=False)
    logo = Column(String(100), nullable=False)
    app_code = Column(String(100), nullable=False, unique=True)
    app_lang = Column(String(100), nullable=False)
    app_type = Column(String(100), nullable=False)
    is_active = Column(TINYINT(1), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class EngineAppEnv(Base):
    __tablename__ = 'engine_app_envs'

    id = Column(INTEGER(11), primary_key=True)
    mode = Column(String(200), nullable=False)
    key = Column(String(200), nullable=False)
    value = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    bk_app_id = Column(ForeignKey('engine_apps.id'), nullable=False, index=True)

    bk_app = relationship('EngineApp')


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


class AddEnv:
    def __init__(self):
        cursor = sessionmaker(bind=db)
        self.session = cursor()
        self.envs = envs

    def add_env(self):
        for env in self.envs:
            app = self.session.query(PaasApp).filter(PaasApp.code==env.get("app_code")).first()
            if app:
                env_list = env.get("env")
                for env_dict in env_list:
                    key = env_dict.get("key")
                    value = env_dict.get("value")
                    env_scope = "prod"
                    env_query = self.session.query(EngineAppEnv).filter(
                        EngineAppEnv.bk_app_id==app.id,
                        EngineAppEnv.key==key
                    ).first()
                    if not env_query:
                        create_query = EngineAppEnv(mode=env_scope, key=key, value=value,
                                                    created_at=datetime.datetime.now(),
                                                    updated_at=datetime.datetime.now(),
                                                    bk_app_id=app.id
                                                    )
                        self.session.add(create_query)
                        self.session.commit()
                        print("For {} create env info: key={} value={}".format(env.get("app_code"), key, value))
                    else:
                        self.session.query(EngineAppEnv).filter(
                                EngineAppEnv.id==env_query.id).update({
                                                                          "mode": env_scope,
                                                                          "key": key,
                                                                          "value": value,
                                                                          "updated_at": datetime.datetime.now(),
                                                                          "bk_app_id": app.id
                                                                      })
                        self.session.commit()
                        print("For {} update env info: key={} value={}".format(env.get("app_code"), key, value))

    def add_env_v2(self):
        for env in self.envs:
            app_code = env.get("app_code")
            env_list = env.get("env")
            for env_dict in env_list:
                env_query = self.session.query(PaasAppEnvvar).filter(
                        PaasAppEnvvar.app_code==app_code,
                        PaasAppEnvvar.name==env_dict.get("key")
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
                                    PaasAppEnvvar.id==env_query.id).update({
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
    AddEnv().add_env_v2()
    print("ENV INPUT IS DONE, SUCCESS.")

