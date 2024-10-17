# 数据库设置文件

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Config:  # 定义了配置类
    # 初始化 连接数据库配置
    def __init__(self):
        self.Host = '127.0.0.1'
        self.Port = 3306
        self.Database = 'sql_software'
        self.Username = 'root'
        self.Password = 'root'
        self.DB_URL = "mysql+pymysql://{}:{}@{}:{}/{}".format(self.Username, self.Password, self.Host, self.Port,
                                                              self.Database)

    # 创建引擎
    def get_engine(self):
        return create_engine(self.DB_URL)

    # 创建会话
    def get_session(self):
        return sessionmaker(bind=self.get_engine())()
