import datetime
import gc
import glob
from loguru import logger

import tensorflow as tf
from mne.filter import resample
from mne.io import read_raw_edf
import pandas as pd
from scipy.signal import butter, sosfilt

from .commons import *
from .data_usage_config import *
import xml.etree.ElementTree as XmlElementTree
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from sklearn.utils.multiclass import unique_labels

# 不支持中文路径
MODEL_PATH = 'final_8.tflite'       # 模型位置
SEQ_LENGTH = 20

# 带通滤波
def calc_butter_bandpass_params(lohi, fs, order=5):
    # no filtering
    if lohi is None:
        return None
    # lo pass hi pass and band pass
    if lohi[0] is None:
        lohi = lohi[1]
        btype = "lowpass"
    elif lohi[1] is None:
        lohi = lohi[0]
        btype = "highpass"
    else:
        btype = "bandpass"
    sos = butter(order, lohi, btype=btype, output='sos', fs=fs)
    # sos:IIR滤波器的二阶分段表示
    return sos

def get_label(xml_file_path):
    # 直接从xml文件中获得stage
    xml = XmlElementTree.parse(xml_file_path)
    stages = xml.find("SleepStages")
    stages_list = [stage.text for stage in stages.findall("SleepStage")]
    return stages_list

# 制混淆矩阵
def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        #print("Normalized confusion matrix")
    else:
        pass
        #print('Confusion matrix, without normalization')

    #print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    ax.set_ylim(len(classes)-0.5, -0.5)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.show()
    return ax



def stage_5(path):
    edf_file = path
    print(path)
    # 整合各模态要用的通道        只用了眼电和脑电
    included_channel_names = sum([x['channels'] for x in INCLUDED_CHANNELS_DETAILS_ASSM.values()], [])
    edf = read_raw_edf(edf_file)
    print(edf.ch_names)
    # shape: ch x t
    if all(element in edf.ch_names for element in included_channel_names):
        data = edf.get_data(picks=included_channel_names)  # 提取出特定通道的数据
    else:
        edf.close()
        return []
    
    gc.collect()
    logger.info("原始数据形状 {}", data.shape)

    # 丢弃不能被片段长度（30秒）整除的部分
    segment_length_points = SEGMENT_LENGTH_SECS * SAMPLING_RATE_ASSM        # 每一段数据的长度为30*1024
    segments_count = len(data.T) // segment_length_points                   # 获得整除值
    data = data[:, :segments_count * segment_length_points]                 # 所有通道都进行一个去掉不能被30s整除的部分
    # 分段, shape: ch x batch x t
    data = data.reshape([-1, segments_count, segment_length_points])
    # logger.warning(data.shape)      # (8,997,30720)
    # 将通道维度放到批量维度后, shape: batch x ch x t
    data = np.moveaxis(data, 1, 0)      # 调整数据维度
    logger.info("分段后形状 {}", data.shape)
    # 分别处理不同模态数据
    # 八个通道，前六个是脑电，后两个是眼电
    channel_list_offset = 0     # 记录通道数
    new_data = []    
    for modal_name, modal_spec in INCLUDED_CHANNELS_DETAILS_ASSM.items():
        channels_count_of_modal = len(modal_spec['channels'])
        data_of_modal = data[:, channel_list_offset:channel_list_offset + channels_count_of_modal]
        scaling_factor = modal_spec['scaling']                          # 比例因子
            # logger.warning(data_of_modal.shape)
        if scaling_factor is not None:
            data_of_modal *= scaling_factor     # 不明白乘上这个scaling_factor是什么作用
            # logger.warning(data_of_modal.shape)
        filter_of_modal = modal_spec['filter-params']
        if filter_of_modal is not None:
            filter_of_modal = calc_butter_bandpass_params(modal_spec['filter-params'], SAMPLING_RATE_ASSM)
            # logger.warning(filter_of_modal.shape)     (5,6)
            data_of_modal = sosfilt(filter_of_modal, data_of_modal)     #
        target_sampling_rate = modal_spec['target-sampling-rate']
        if target_sampling_rate is not None:
            data_of_modal = np.array(resample(data_of_modal, 1, SAMPLING_RATE_ASSM / target_sampling_rate),dtype=np.float32)
                #  resample在这里重采样的，执行之后将1024hz降采样到100hz
        new_data.append(data_of_modal)
        channel_list_offset += channels_count_of_modal                                                                                                                    
    logger.info("各模态形状 {}", [x.shape for x in new_data])
        # 现在，各模态采样率必须相同
    data = np.concatenate(new_data, axis=1)     # 完成多个数组的拼接  axis影响拼接的时候是列的拼接0(列不变)还是行的拼接1(行不变)
    logger.info("合并后形状 {}", data.shape)

    original_batch_length = len(data)
    padded_batch_length = (-(-original_batch_length // SEQ_LENGTH)) * SEQ_LENGTH
    if padded_batch_length != original_batch_length:
        data = np.pad(data, ((0, padded_batch_length - original_batch_length), (0, 0), (0, 0)))
        logger.info("填0后形状 {}", data.shape)

        # np.save(pjoin(BASE_PATH, "test.npy"),data)
        # input()
    data = data.reshape([-1, SEQ_LENGTH] + list(data.shape[1:])) * 2
    logger.info("分序列后形状 {}", data.shape)

        # 加载模型
    logger.info("加载TF Lite")
    relative_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_PATH)
    interpreter = tf.lite.Interpreter(model_path=relative_path)
    logger.info("模型加载成功")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

        # 逐个预测
    pred = []
    for sample in data:
        interpreter.set_tensor(input_details[0]['index'], sample.astype(np.float32)[np.newaxis, ...])
        interpreter.invoke()
            # shape: [batch=1 x seq x ch x t][0] = seq x ch x t x cls
        pred.append(interpreter.get_tensor(output_details[0]['index'])[0])
        # shape: batch=seq*N x ch x t x cls

    pred = np.concatenate(pred)
    logger.info("预测值形状 {}", pred.shape)
    pred = np.argmax(pred, axis=-1)[:original_batch_length]
    logger.info("要输出的形状 {}", pred.shape)
    pred = np.where(pred == 4, 5, pred)
    print(pred)
    print("ok")

    return pred


