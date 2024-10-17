from sqlalchemy import Column, String, Table, Column, VARCHAR, SMALLINT, DECIMAL, DateTime, CHAR
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

from connect_database.config import Config

Base = declarative_base()

event_nm = {0: '中枢型', 1: '阻塞型', 2: '混合型'}
event_cd = {0: '03', 1: '01', 2: '02'}


# 对应数据库呼吸事件表的类
class Breathe_event_rec(Base):
    # 以下为表名 和 对应表字段
    __tablename__ = 'tb_breathe_event_rec'
    Patient_nm = Column('Patient_nm', VARCHAR(100))
    Patient_ID = Column('Patient_ID', VARCHAR(20), primary_key=True)
    seq_no = Column('seq_no', SMALLINT, primary_key=True)
    event_nm = Column('event_nm', VARCHAR(100))
    event_cd = Column('event_cd', VARCHAR(20))
    start_tm = Column('start_tm', DateTime)
    end_tm = Column('end_tm', DateTime)


# 前端传来的数据 对列表进行处理
def process_data(dic):
    sorted_dic = dict(sorted(dic.items(), key=lambda x: float(x[0].split(',')[0])))
    seq_no = 0
    result = []

    for key, value in sorted_dic.items():
        seq_no += 1
        event_class = int(value)
        selection_range = key.split(',')
        start_second = round(float(selection_range[0]))
        start_time_datetime = datetime.fromtimestamp(start_second)
        end_second = round(float(selection_range[1]))
        end_time_datetime = datetime.fromtimestamp(end_second)
        result.append({
            'seq_no': seq_no,
            'event_nm': event_nm[event_class],
            'event_cd': event_cd[event_class],
            'start_tm': start_time_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'end_tm': end_time_datetime.strftime('%Y-%m-%d %H:%M:%S')
        })

    return result


# 保存数据到数据库
def save_breathe_event_data(dic):
    breathe_event_list = process_data(dic)
    conf = Config()
    session = conf.get_session()

    for data in breathe_event_list:
        breathe_event = Breathe_event_rec(
            Patient_nm='张三',
            Patient_ID='1222',
            seq_no=data['seq_no'],
            event_nm=data['event_nm'],
            event_cd=data['event_cd'],
            start_tm=datetime.strptime(data['start_tm'], '%Y-%m-%d %H:%M:%S'),
            end_tm=datetime.strptime(data['end_tm'], '%Y-%m-%d %H:%M:%S')
        )
        session.add(breathe_event)

    # 在循环结束后提交事务，然后关闭会话
    session.commit()
    session.close()
