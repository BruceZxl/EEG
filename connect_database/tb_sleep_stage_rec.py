from sqlalchemy import Column, String, Table, Column, VARCHAR, SMALLINT, DECIMAL, DateTime, CHAR
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

from connect_database.config import Config

Base = declarative_base()


# 对应数据库睡眠分期表的类
class Sleep_stage_rec(Base):
    # 以下为表名 和 对应表字段
    __tablename__ = 'tb_sleep_stage_rec'
    Patient_nm = Column('Patient_nm', VARCHAR(100))
    Patient_ID = Column('Patient_ID', VARCHAR(20), primary_key=True)
    Sleep_staging_nm = Column('Sleep_staging_nm', VARCHAR(100))
    Sleep_staging_cd = Column('Sleep_staging_cd', VARCHAR(20), primary_key=True)
    seq_no = Column('seq_no', SMALLINT, primary_key=True)
    start_tm = Column('start_tm', DateTime)
    end_tm = Column('end_tm', DateTime)
    Duration = Column('Duration', DECIMAL(10, 4))
    sleep_latency = Column('sleep_latency', DECIMAL(10, 4))
    Sleep_Duration = Column('Sleep_Duration', DECIMAL(10, 4))


# 前端传来的数据 对字典进行处理
def process_data(dic):
    sorted_dic = dict(sorted(dic.items(), key=lambda x: int(x[0])))
    time_interval = 30
    start_time = 0
    prev_stage = None
    duration = 0
    result = []
    for key, value in sorted_dic.items():
        if value == prev_stage:
            duration += time_interval
        else:
            if prev_stage is not None:
                start_time_datetime = datetime.fromtimestamp(start_time * time_interval)
                end_time_datetime = start_time_datetime + timedelta(seconds=duration)
                result.append({
                    'start_time': start_time_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': end_time_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': duration,
                    'stage': prev_stage,
                    'seq_no': start_time
                })
            start_time = int(key) - int(next(iter(sorted_dic)))
            duration = time_interval
            prev_stage = value
    if prev_stage is not None:
        start_time_datetime = datetime.fromtimestamp(start_time * time_interval)
        end_time_datetime = start_time_datetime + timedelta(seconds=duration)
        result.append({
            'start_time': start_time_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration,
            'stage': prev_stage,
            'seq_no': start_time
        })
    return result


# 保存数据到数据库
def save_sleep_data(dic):
    sleep_list = process_data(dic)
    conf = Config()
    session = conf.get_session()

    for data in sleep_list:
        sleep_stage = Sleep_stage_rec(
            Patient_ID='1222',
            Sleep_staging_cd=data['seq_no'],
            seq_no='1',
            Patient_nm='张三',
            Sleep_staging_nm=data['stage'],
            start_tm=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
            end_tm=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
            Duration=data['duration'],
            sleep_latency=4,
            Sleep_Duration=1
        )
        session.add(sleep_stage)

    # 在循环结束后提交事务，然后关闭会话
    session.commit()
    session.close()

