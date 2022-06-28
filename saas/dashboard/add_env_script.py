"""
脚本说明：为Saas应用添加ENV

执行说明：
    python add_env_script.py --mysql_host [mysql_host]
                             --mysql_username [mysql_username]
                             --mysql_password [mysql_password]
                             --config_file_path [config_file_path]
    例：python add_env_script.py --mysql_host 127.0.0.1
                                --mysql_username root
                                --mysql_password 123456
                                --config_file_path /xx/xxx/xxx/config

参数说明：
    mysql_host          必填
    mysql_username      必填
    mysql_password      必填
    config_file_path    必填

Mysql账号说明：
    必须使用拥有opsany_paas数据库读写权限的账号

第三方依赖：
    mysql-connector==2.2.9
    SQLAlchemy==1.4.22
"""

import sys
import configparser
import argparse
from sqlalchemy import Column, String, create_engine, Index
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import parse


class AddEnv:
    def __init__(self, mysql_host, mysql_username, mysql_password, config_file_path):
        self.db, self.database_orm = self.get_db(mysql_host, mysql_username, mysql_password)
        cursor = sessionmaker(bind=self.db)
        self.session = cursor()
        self.envs = self.get_env(config_file_path)

    def add_env(self):
        """
        {
            "app_code": "",
            "env": [
                {"key": "key1", "value": "value1"},
                {"key": "key2", "value": "value2"}
            ]
        }
        """
        app_code = self.envs.get("app_code")
        env_list = self.envs.get("env")
        for env_dict in env_list:
            env_query = self.session.query(self.database_orm).filter(
                self.database_orm.app_code == app_code,
                self.database_orm.name == env_dict.get("key")
            ).first()
            if not env_query:
                create_query = self.database_orm(
                    app_code=app_code,
                    name=env_dict.get("key", ""),
                    value=env_dict.get("value", ""),
                    mode="all",
                    intro=self.get_intro(env_dict.get("key", "")),
                )
                self.session.add(create_query)
                self.session.commit()
                print("For {} create env info: key={} value={}".format(app_code, env_dict.get("key"),
                                                                       env_dict.get("value")))
            else:
                self.session.query(self.database_orm).filter(
                    self.database_orm.id == env_query.id).update({
                        "mode": "all",
                        "name": env_dict.get("key", ""),
                        "value": env_dict.get("value", ""),
                        "intro": self.get_intro(env_dict.get("key", "")),
                        "app_code": app_code,
                    })
                self.session.commit()
                print("For {} update env info: key={} value={}".format(app_code, env_dict.get("key"),
                                                                       env_dict.get("value")))

    def get_intro(self, key: str):
        """
        MYSQL_ROOT -> mysql root
        """
        intro = "".join(info.lower() + " " for info in key.split("_"))[:-1]
        return intro

    def get_env(self, config_file_path):
        read_install_config = configparser.ConfigParser()
        read_install_config.optionxform = lambda option: option
        try:
            read_install_config.read(config_file_path, encoding="utf-8")
            config_dict = dict(read_install_config)
            app_info = config_dict.get("APP_INFO")
            app_code = ""
            for key, value in app_info.items():
                if key == "APP_CODE":
                    app_code = self.handle_value(value)
                    break
            if not app_code:
                raise Exception("Not find app_code, Please check your config file.")
            app_env = config_dict.get("APP_ENV")
            envs = []
            for key, value in app_env.items():
                envs.append({
                    "key": key,
                    "value": self.handle_value(value)
                })
            env_info = {
                "app_code": app_code,
                "env": envs
            }
            return env_info
        except Exception as e:
            print('Read config file error, error info: {}.'.format(str(e)))
            sys.exit(1)

    def handle_value(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("'") or value.startswith('"'):
                value = value[1:]
            if value.endswith("'") or value.endswith('"'):
                value = value[:-1]
        return value

    def get_db(self, mysql_host, mysql_username, mysql_password):
        try:
            db = create_engine(
                "mysql+mysqlconnector://{}:{}@{}/opsany_paas".format(
                    mysql_username,
                    parse.quote_plus(mysql_password),
                    mysql_host
                ))
            Base = declarative_base(db)

            def to_dict(self):
                return {c.name: getattr(self, c.name, None)
                        for c in self.__table__.columns}

            Base.to_dict = to_dict
        except Exception as e:
            print("Script error: {}".format(str(e)))
            print("Connect sql is failed. Please check mysql server!")
            sys.exit(1)

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
        return db, PaasAppEnvvar


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--mysql_host", help="Mysql address.", required=True)
    parameter.add_argument("--mysql_username", help="Mysql username.", required=True)
    parameter.add_argument("--mysql_password", help="Mysql password.", required=True)
    parameter.add_argument("--config_file_path", help="Config file path.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    mysql_host = options.mysql_host
    mysql_username = options.mysql_username
    mysql_password = options.mysql_password
    config_file_path = options.config_file_path
    AddEnv(mysql_host, mysql_username, mysql_password, config_file_path).add_env()
