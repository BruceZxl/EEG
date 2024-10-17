# create by zikers
# 创建数据库代码   mysql  user:root   password:123456   database:sql_software
# 运行此代码 可以创建相应的表
from sqlalchemy import create_engine, MetaData, Table, Column, VARCHAR, SMALLINT, DECIMAL, Date, CHAR

# 创建一个MySQL连接引擎
engine = create_engine('mysql://root:123456@127.0.0.1:3306/sql_software')

# 创建一个metadata实例
metadata = MetaData()

# 自动分析参数设置表
auto_analysis_para_table = Table('tb_auto_anlysis_para', metadata,
                                 Column('type_nm', VARCHAR(100)),
                                 Column('type_cd', VARCHAR(20), primary_key=True),
                                 Column('sub_type_nm', VARCHAR(100)),
                                 Column('sub_type_cd', VARCHAR(20), primary_key=True),
                                 Column('para_nm', VARCHAR(100)),
                                 Column('para_cd', VARCHAR(20), primary_key=True),
                                 Column('unit', VARCHAR(20)),
                                 Column('default_value', DECIMAL(8, 4))
                                 )
# 睡眠分期记录表
sleep_stage_rec_table = Table('tb_sleep_stage_rec', metadata,
                              Column('Patient_nm', VARCHAR(100)),
                              Column('Patient_ID', VARCHAR(20), primary_key=True),
                              Column('Sleep_staging_nm', VARCHAR(100)),
                              Column('Sleep_staging_cd', VARCHAR(20), primary_key=True),
                              Column('seq_no', SMALLINT, primary_key=True),
                              Column('start_tm', Date),
                              Column('end_tm', Date),
                              Column('Duration', DECIMAL(10, 4)),
                              Column('sleep_latency', DECIMAL(10, 4)),
                              Column('Sleep_Duration', DECIMAL(10, 4))
                              )
# 血氧饱和记录表
SpO2_rec_table = Table('tb_SpO2_rec', metadata,
                       Column('Patient_nm', VARCHAR(100)),
                       Column('Patient_ID', VARCHAR(20), primary_key=True),
                       Column('seq_no', SMALLINT, primary_key=True),
                       Column('event_nm', VARCHAR(100)),
                       Column('event_cd', VARCHAR(20)),
                       Column('start_tm', Date),
                       Column('end_tm', Date),
                       Column('Max_value', DECIMAL(10, 4)),
                       Column('Min_value', DECIMAL(10, 4)),
                       Column('Mean_value', DECIMAL(10, 4))
                       )
# 呼吸事件记录表
breathe_event_rec_table = Table('tb_breathe_event_rec', metadata,
                                Column('Patient_nm', VARCHAR(100)),
                                Column('Patient_ID', VARCHAR(20), primary_key=True),
                                Column('seq_no', SMALLINT, primary_key=True),
                                Column('event_nm', VARCHAR(100)),
                                Column('event_cd', VARCHAR(20)),
                                Column('start_tm', Date),
                                Column('end_tm', Date)
                                )
# 心率事件记录表
heart_rate_rec_table = Table('tb_heart_rate_rec', metadata,
                             Column('Patient_nm', VARCHAR(100)),
                             Column('Patient_ID', VARCHAR(20), primary_key=True),
                             Column('seq_no', SMALLINT, primary_key=True),
                             Column('event_nm', VARCHAR(100)),
                             Column('event_cd', VARCHAR(20)),
                             Column('start_tm', Date),
                             Column('end_tm', Date),
                             Column('Max_value', DECIMAL(10, 4)),
                             Column('Min_value', DECIMAL(10, 4)),
                             Column('Mean_value', DECIMAL(10, 4))
                             )
# 鼾声事件记录表
snore_rec_table = Table('tb_snore_rec', metadata,
                        Column('Patient_nm', VARCHAR(100)),
                        Column('Patient_ID', VARCHAR(20), primary_key=True),
                        Column('seq_no', SMALLINT, primary_key=True),
                        Column('event_nm', VARCHAR(100)),
                        Column('event_cd', VARCHAR(20)),
                        Column('start_tm', Date),
                        Column('end_tm', Date),
                        Column('Mean_value', DECIMAL(10, 4))
                        )
# 觉醒事件记录表
awake_rec_table = Table('tb_awake_rec', metadata,
                        Column('Patient_nm', VARCHAR(100)),
                        Column('Patient_ID', VARCHAR(20), primary_key=True),
                        Column('seq_no', SMALLINT, primary_key=True),
                        Column('event_nm', VARCHAR(100)),
                        Column('event_cd', VARCHAR(20)),
                        Column('start_tm', Date),
                        Column('end_tm', Date),
                        Column('Mean_value', DECIMAL(10, 4))
                        )
# 体动事件记录表
body_movement_rec_table = Table('tb_body_movement_rec', metadata,
                                Column('Patient_nm', VARCHAR(100)),
                                Column('Patient_ID', VARCHAR(20), primary_key=True),
                                Column('seq_no', SMALLINT, primary_key=True),
                                Column('event_nm', VARCHAR(100)),
                                Column('event_cd', VARCHAR(20)),
                                Column('start_tm', Date),
                                Column('end_tm', Date),
                                Column('Mean_value', DECIMAL(10, 4))
                                )
# 通道参数设置
chan_para_table = Table('tb_chan_para', metadata,
                        Column('Patient_nm', VARCHAR(100)),
                        Column('Patient_ID', VARCHAR(20), primary_key=True),
                        Column('Electrode_nm', VARCHAR(100)),
                        Column('Polarity', VARCHAR(20)),
                        Column('Ref', VARCHAR(100)),
                        Column('Grid_spacing', DECIMAL(6, 4)),
                        Column('size', DECIMAL(6, 4)),
                        Column('colour', VARCHAR(20)),
                        Column('Frequency_reduction', CHAR(4)),
                        Column('zoom', DECIMAL(8, 4)),
                        Column('Bipolar_polarity', CHAR(4)),
                        Column('High_filtering', DECIMAL(8, 4)),
                        Column('Low_filtering', DECIMAL(8, 4)),
                        Column('power_frequency', CHAR(4)),
                        Column('Auto_ruler', CHAR(4)),
                        Column('Signal_offset_corr', CHAR(4)),
                        Column('Waveform_conversion', CHAR(4))
                        )

metadata.create_all(engine)
