from typing import Optional

from typing import Optional

import mne
import numpy as np

from data_model.tensor import Tensor


class Brain_map:
    sfreq = 250
    # 电极名称表
    ch_table = ['Nz',
                'Fp1', 'Fpz', 'Fp2',
                'AF7', 'AF3', 'AFz', 'AF4', 'AF8',
                'F9', 'F7', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 'F8', 'F10',
                'FT9', 'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8', 'FT10',
                'A1', 'T9', 'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8', 'T10', 'A2',
                'TP9', 'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8', 'TP10',
                'P9', 'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8', 'P10',
                'PO7', 'PO5', 'PO3', 'POz', 'PO4', 'PO6', 'PO8',
                'CB1', 'O1', 'Oz', 'O2', 'CB2',
                'Iz']

    # , 'EEG Fpz-Cz', 'EEG Pz-Oz', 'EOG horizontal', 'Resp oro-nasal', 'EMG submental', 'Temp rectal', 'Event marker']

    def __init__(self, tensor: Tensor, num_channels, name_channels):
        # 取数据
        data_origin = []
        for i in range(num_channels):
            d = tensor.data[i]
            temp_data = np.concatenate(d.data)[:len(d)]
            data_origin.append(temp_data)
        # 重采样
        shortlen = len(data_origin[0])
        longlen = len(data_origin[0])
        for i in range(num_channels):
            if len(data_origin[i]) < shortlen:
                shortlen = len(data_origin[i])
            if len(data_origin[i]) > longlen:
                longlen = len(data_origin[i])
        data = np.zeros((num_channels, shortlen))
        for j in range(num_channels):
            if len(data_origin[j]) != shortlen:
                data[j] = mne.filter.resample(data_origin[j], up=1, down=len(data_origin[j]) / shortlen, axis=0)
        # 修改名称不符合命名规范的电极
        for m in range(num_channels):
            if name_channels[m] == 'EEG Fpz-Cz':
                name_channels[m] = 'Cz'
            if name_channels[m] == 'EEG Pz-Oz':
                name_channels[m] = 'Oz'
        # 删除非脑电的电极和相应数据
        deleted_channels = list()
        for n in range(num_channels):
            if name_channels[n] not in self.ch_table:
                deleted_channels.append(n)
        self._data = np.delete(data, deleted_channels, axis=0)
        name_channels_1 = np.delete(name_channels, deleted_channels, axis=0)
        self._name_channels = name_channels_1.tolist()
        self._num_channels = num_channels

    def draw_map(self):
        # 判断数据是否为空
        if self._num_channels == 0 | len(self._name_channels) == 0:
            print("数据为空")
            return
        # 创建info对象
        info = mne.create_info(ch_names=self._name_channels, sfreq=250., ch_types='eeg')
        # 创建raw对象
        raw = mne.io.RawArray(self._data, info)
        # 创建等距事件（events），默认id为1
        new_events = mne.make_fixed_length_events(raw, duration=2.)
        # 创建epochs
        epochs = mne.Epochs(raw, new_events)
        # 画图
        # epochs.set_montage('biosemi64', on_missing='warn')
        epochs.set_montage("standard_1020", on_missing='warn')
        epochs.plot_psd_topomap()

