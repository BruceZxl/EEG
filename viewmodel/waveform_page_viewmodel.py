import asyncio
import math
import struct
import threading
from typing import Optional
from urllib.parse import urlparse
from urllib.request import url2pathname
import mne
import numpy as np
import qasync
import torch
from PySide6 import QtCore
from PySide6.QtCore import QObject
from loguru import logger
import pyedflib
from mne.io.constants import FIFF
from datetime import date
import biosppy.signals.tools as st
from biosppy.signals.ecg import correct_rpeaks, hamilton_segmenter
from scipy.signal import medfilt

from client.eeg_client import EegClient
from connect_database.tb_sleep_stage_rec import save_sleep_data
from connect_database.tb_breathe_event_rec import save_breathe_event_data
from project.esig_project import ESigProject
from utils import qutils
from brainmap import Brain_map
from data_model.axes.time_axis import TimeAxis
from data_model.waveform import WaveformModel
from viewmodel.montage_registry import MontageRegistry
from algorithm import Algorithms
from breathe_event_detection.detect import breathe_event_detect
from algorithm.compilite.stage import stage_5
from algorithm.compilite.data_pre import stage_MMFCA
from algorithm.compilite.auto_spin_detec import auto_spin_detec

STAGE_SHORT_NAMES = ['W', 'N1', 'N2', 'N3', 'R', '?']
SIZE = 250


class WaveformPageViewModel(QObject):
    nopChanged = QtCore.Signal()
    loadingChanged = QtCore.Signal(bool)
    montageChanged = QtCore.Signal()
    seekChanged = QtCore.Signal()
    filterChanged = QtCore.Signal()
    notchFilterChanged = QtCore.Signal()  # 陷波
    selectionChanged = QtCore.Signal()
    maggotModeChanged = QtCore.Signal()
    ipportModeChanged = QtCore.Signal()
    scrollModeChanged = QtCore.Signal()
    scaleChanged = QtCore.Signal()
    canvasInvalidated = QtCore.Signal()
    markSequenceChanged = QtCore.Signal()
    waveModeChanged = QtCore.Signal()  # 创建模式信号  波模式改变信号
    markbreatheeventChanged = QtCore.Signal()  # 标注事件改变信号
    set_save_flagChanged = QtCore.Signal()  # 1
    referenceChanged = QtCore.Signal()  # 参考电极修改
    colorChanged = QtCore.Signal()

    set_save_flagChanged_spindle = QtCore.Signal()  # 纺锤波标注保存 改变信号

    channelpositionChanged = QtCore.Signal()
    positionyChanged = QtCore.Signal()

    def __init__(self, *, parent=None):
        super().__init__(parent)
        self.loading = None
        self._area_viewmodels = []
        self._montage_index = 0
        self._montage = None
        self._selection_range = [0.0] * 4
        self._maggot_mode = False
        self._project: Optional[ESigProject] = None
        self._channel_height = 80
        self._user_amplifier: Optional[np.ndarray] = None
        self._cache_block_seconds = 0
        self._lowpass = self._hipass = self._notch = 0.0

        self._reference = None

        self._wave_mode = False  # 首先设置  模式为false  一旦打开双模式  改成true
        self._mark_breathe_event_num = -1  # 先设置为False   一旦点击为true  则画图
        self.mark_breathe_event_record1 = {}  # 存 每一次  画框 位置 2
        self._set_save_flag = 0  # 设置保存  的信号 3
        self._auto_breathe_event_annotate_flag = 0  # 设置自动标注呼吸事件
        self._set_delete_flag = 0  # 设置删除呼吸事件


        # 定义纺锤波标志记录
        self._mark_spindle_notation = 0  # 纺锤波标志记录 0  点纺锤波按钮为1
        self._set_save_flag_spindle = 0  # 设置保存标志0  点击保存为1
        self.mark_spindle_notation_record = {}  #标志纺锤波记录
        self._mark_spindle_notation_num = 0
        self._auto_spindle_annotate_flag = 0 # 设置自动标注纺锤波

        self._set_delete_flag_spindle = 0  # 设置删除纺锤波事件

        self._save_mark_sequence = 0  # 设置标志  保存睡眠阶段到数据库
        self._save_mark_breathe_event_record = 0  # 设置标志  保存呼吸事件到数据库
        self._mark_sequence = {}
        self._lowpass = self._hipass = self._notch = None
        self._channelindex = 0
        self._position_mode = False
        self._mousepositony = 0
        self._ip = self._port = ""
        print(type(self._ip), type(self._port))
        self._eeg_client: Optional[EegClient] = None
        self._auto_scroll = False

        self._colour_list = []

    # def get_mark_sequence(self):
    #     return self._mark_sequence

    @QtCore.Slot(str, bool, bool, str, str)
    def reload(self, path, neo, load_sine, import_from, import_format):
        loop = asyncio.get_running_loop()
        loop.create_task(self._async_reload(loop, path, neo, load_sine, import_from, import_format))

    @QtCore.Slot()
    def unload(self):
        self._project.unload()

    async def _async_reload(self, loop, path, neo, load_sine, import_from, import_format):
        if self.loading:
            return
        self.loadingChanged.emit(True)
        if load_sine:
            with qasync.QThreadExecutor(1) as exec:
                loaded = await loop.run_in_executor(exec, ESigProject.sample)
        else:
            path = qutils.url_to_path(path)
            with qasync.QThreadExecutor(1) as exec:
                if import_from:
                    args = [
                        ESigProject.import_from, qutils.url_to_path(import_from), import_format or None
                    ]
                elif neo:
                    # TODO: These shall be provided by the data receiver,
                    #  or entered by user via dialogs!
                    #  Currently created here for demonstration.
                    num_channels = 48
                    from data_model.axes import EChannelDef
                    from mne.io.constants import FIFF
                    channels = [
                        EChannelDef(f"Ch-{i}", unit_m=FIFF.FIFF_UNITM_NONE)
                        for i in range(num_channels)
                    ]
                    srs = [SIZE] * num_channels
                    # srs = [256] * (num_channels // 2)
                    # srs += [4] * (num_channels - len(srs))
                    args = [ESigProject.create, path, channels, srs]

                else:
                    args = [ESigProject.load, path]
                loaded = await loop.run_in_executor(exec, *args)
        self._project = loaded
        self._colour_list = [[255,0,0]]*len(self._project.waveform.tensor.data)
        self._project.add_listener(lambda: self.canvasInvalidated.emit())
        self._mark_sequence = self._project.mark_sequence
        self.mark_breathe_event_record1 = self._project.mark_breathe_event_record
        self.list1 = []
        self.mark_spindle_notation_record = self._project.mark_spindle_notation_record #纺锤波 记录



        # TODO: Add a button to run the algorithm.
        if import_from:
            x_stage = stage_5(qutils.url_to_path(import_from))
            if len(x_stage) == 0:
                x_stage = stage_MMFCA(qutils.url_to_path(import_from))

            index = 0
            for i in x_stage:
                self._project.mark_sequence[str(index)] = STAGE_SHORT_NAMES[i]
                index += 1

            # # 画纺锤波
            # edf_channels = mne.io.read_raw_edf(qutils.url_to_path(import_from)).info['ch_names']
            # eeg_index = next((i for i, channel in enumerate(edf_channels) if 'EEG' in channel), None)
            # if eeg_index is None:
            #     pass
            # else:
            #     y1, y2 = eeg_index * self._channel_height, (eeg_index + 1) * self._channel_height
            #     x = [0, 1, 0, 1, 0, 1]
            #     for i in range(len(x)):
            #         if x[i] == 1:
            #             tuple = (0.5 * i, y1, 0.5 * (i + 1), y2)
            #             self.list1.append(tuple)

        self.reset()
        self.update_montage()
        self.loadingChanged.emit(False)
        if import_from:
            with qasync.QThreadExecutor(1) as exec:
                loaded.directory = path
                await loop.run_in_executor(exec, loaded.save, True)

        self._mark_sequence = self._project.mark_sequence


    @QtCore.Property(str)
    def mark_sequence(self, pos, mark):
        # print("================")
        # print(self._mark_sequence)
        return self._mark_sequence

    @mark_sequence.setter
    def mark_sequence(self, value):
        key = str(int(self.position / 30))
        self._mark_sequence[key] = value
        self.markSequenceChanged.emit()
        self.canvasInvalidated.emit()

    @QtCore.Property(int, notify=set_save_flagChanged)
    def set_save_flag(self):
        return self._set_save_flag

    # 手动标注呼吸事件
    @set_save_flag.setter
    def set_save_flag(self, value):
        self._set_save_flag = value
        if self._set_save_flag == 1:
            selection = self.get_selection1()
            mark_key = str(selection[0]) + "," + str(selection[1]) + "," + str(selection[2]) + "," + str(selection[3])
            self.mark_breathe_event_record1[mark_key] = self.mark_breathe_event_num
        self.set_save_flagChanged.emit()
        self.canvasInvalidated.emit()


    #纺锤波保存标志
    @QtCore.Property(int, notify=set_save_flagChanged)
    def set_save_flag_spindle(self):
        return self._set_save_flag_spindle

    # 手动标注纺锤波

    @set_save_flag_spindle.setter
    def set_save_flag_spindle(self, value):
        self._set_save_flag_spindle = value
        # print("****:", self._set_save_flag_spindle)
        if self._set_save_flag_spindle == 1:
            selection = self.get_selection1()
            mark_key_spindle = str(selection[0]) + "," + str(selection[1]) + "," + str(selection[2]) + "," + str(
                selection[3])
            self.mark_spindle_notation_record[mark_key_spindle] = self.mark_spindle_notation_num
            # print(self.mark_spindle_notation_record)
        self.set_save_flagChanged.emit()
        self.canvasInvalidated.emit()
        # 纺锤波保存

    # 自动标注纺锤波
    @QtCore.Property(int, notify=set_save_flagChanged)
    def auto_spindle_annotate_flag(self):
        return self._auto_spindle_annotate_flag

    @auto_spindle_annotate_flag.setter
    def auto_spindle_annotate_flag(self, value):
        self._auto_spindle_annotate_flag = value
        if self._auto_spindle_annotate_flag == 1:
            num_spin = 0
            for i in range(np.size(self._project.waveform.channels)):
                if "EEG" in self._project.waveform.channels[i].name:
                    num_spin = i
                    break
            # print(num_spin)
            d = self._project.waveform.tensor.data[num_spin]  # 取通道数据
            signal_spin = np.concatenate(d.data)[:len(d)]
            fs_spin = self._project.waveform.tensor.shape_def[1][num_spin].sampling_rate  # 取通道频率
            x_spin = auto_spin_detec(signal_spin, fs_spin)  # 检测纺锤波
            y1 = float(num_spin * self._channel_height)
            y2 = float((num_spin + 1) * self._channel_height)
            for i in range(len(x_spin)):
                if x_spin[i] == 1:
                    x1, x2 = 0.5 * i, 0.5 * (i + 1)
                    mark_key = str(x1) + "," + str(x2) + "," + str(y1) + "," + str(y2)
                    self.mark_spindle_notation_record[mark_key] = "1"
        self.canvasInvalidated.emit()

    ##删除纺锤波标志
    @QtCore.Property(int, notify=set_save_flagChanged)
    def set_delete_flag_spindle(self):
        return self._set_delete_flag_spindle
    ##删除纺锤波
    @set_delete_flag_spindle.setter
    def set_delete_flag_spindle(self, value):
        self._set_delete_flag_spindle = value
        if self._set_delete_flag_spindle == 1:
            selection = self.get_selection1()
            selection_start, selection_end = selection[0], selection[1]  # 鼠标选取的删除范围
            key_delete = []

            for key, value in self.mark_spindle_notation_record.items():
                event_range = key.split(',')
                event_start, event_end = float(event_range[0]), float(event_range[1])
                if selection_start <= event_start and selection_end >= event_end:  # 寻找范围内的呼吸事件
                    key_delete.append(key)
            for key in key_delete:
                self.mark_spindle_notation_record.pop(key)  # 删除范围内的呼吸事件
        self.canvasInvalidated.emit()


    @QtCore.Property(int, notify=set_save_flagChanged)
    def auto_breathe_event_annotate_flag(self):
        return self._auto_breathe_event_annotate_flag

    # 自动标注呼吸事件
    @auto_breathe_event_annotate_flag.setter
    def auto_breathe_event_annotate_flag(self, value):
        self._auto_breathe_event_annotate_flag = value
        if self._auto_breathe_event_annotate_flag == 1:
            num_ecg = 0
            for i in range(np.size(self._project.waveform.channels)):
                if self._project.waveform.channels[i].name == "ECG":
                    num_ecg = i
                    break
            d = self._project.waveform.tensor.data[num_ecg]  # 取ECG数据
            signal_ecg = np.concatenate(d.data)[:len(d)]
            print(signal_ecg.shape)
            fs_ecg = self._project.waveform.tensor.shape_def[1][num_ecg].sampling_rate  # 取ECG频率
            start_time, end_time = breathe_event_detect(signal_ecg, fs_ecg)  # 检测呼吸事件
            y1 = float(num_ecg * self._channel_height)
            y2 = float((num_ecg + 1) * self._channel_height)
            for i in range(len(start_time)):
                x1, x2 = start_time[i], end_time[i]
                mark_key = str(x1) + "," + str(x2) + "," + str(y1) + "," + str(y2)
                self.mark_breathe_event_record1[mark_key] = "1"
        self.canvasInvalidated.emit()

    # 删除呼吸事件标志
    @QtCore.Property(int, notify=set_save_flagChanged)
    def set_delete_flag(self):
        return self._set_delete_flag

    @set_delete_flag.setter
    def set_delete_flag(self, value):
        self._set_delete_flag = value
        if self._set_delete_flag == 1:
            selection = self.get_selection1()
            selection_start, selection_end = selection[0], selection[1]  # 鼠标选取的删除范围
            key_delete = []
            for key, value in self.mark_breathe_event_record1.items():
                event_range = key.split(',')
                event_start, event_end = float(event_range[0]), float(event_range[1])
                if selection_start <= event_start and selection_end >= event_end:  # 寻找范围内的呼吸事件
                    key_delete.append(key)
            for key in key_delete:
                self.mark_breathe_event_record1.pop(key)  # 删除范围内的呼吸事件
        self.canvasInvalidated.emit()

    # 存储睡眠阶段到数据库标志
    @QtCore.Property(int, notify=set_save_flagChanged)
    def save_mark_sequence(self):
        return self._save_mark_sequence

    # 点击按钮 存储睡眠阶段到数据库
    @set_save_flag.setter
    def save_mark_sequence(self, value):
        self._save_mark_sequence = value
        if self._save_mark_sequence == 1:
            m = self._mark_sequence
            save_sleep_data(dic=m)

    # 存储呼吸事件到数据库标志
    @QtCore.Property(int, notify=set_save_flagChanged)
    def save_mark_breathe_event_record(self):
        return self._save_mark_breathe_event_record

    # 点击按钮 存储呼吸事件到数据库
    @set_save_flag.setter
    def save_mark_breathe_event_record(self, value):
        self._save_mark_breathe_event_record = value
        if self._save_mark_breathe_event_record == 1:
            m = self._project.mark_breathe_event_record  # self._project.mark_breathe_event_record保存所有呼吸事件记录
            save_breathe_event_data(dic=m)

    # noinspection PyTypeChecker,PyCallingNonCallable
    @QtCore.Property("QVariantList", notify=montageChanged)
    def area_viewmodels(self):
        return self._area_viewmodels

    # noinspection PyTypeChecker,PyCallingNonCallable
    @QtCore.Property(int, notify=nopChanged)
    def channel_height(self):
        return self._channel_height

    # noinspection PyTypeChecker,PyCallingNonCallable
    @QtCore.Property(float, notify=seekChanged)
    def position(self):
        return 0 if self._project is None else self._project.state.position

    @position.setter
    def position(self, value):
        if self._project is not None and self._project.state.position != value:
            self._project.state.position = value
            self.seekChanged.emit()

    # noinspection PyTypeChecker,PyCallingNonCallable
    @QtCore.Property(float, notify=seekChanged)
    def seconds(self) -> float:
        return 1.0 if self._project is None else self._project.waveform.seconds

    # noinspection PyCallingNonCallable
    @QtCore.Property(float)
    def render_time(self):
        return sum([area.render_time for area in self._area_viewmodels], 0)

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(float, notify=filterChanged)
    def lowpass(self):
        return self._lowpass

    @lowpass.setter
    def lowpass(self, value: float):
        if self._lowpass != value:
            self._lowpass = value
            self.filterChanged.emit()
            self.canvasInvalidated.emit()

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(float, notify=filterChanged)
    def hipass(self):
        return self._hipass

    @hipass.setter
    def hipass(self, value: float):
        if self._hipass != value:
            self._hipass = value
            self.filterChanged.emit()
            self.canvasInvalidated.emit()

    @QtCore.Property(float, notify=notchFilterChanged)
    def notch(self):
        return self._notch

    @notch.setter
    def notch(self, value: float):
        if self._notch != value:
            self._notch = value
            self.notchFilterChanged.emit()
            self.canvasInvalidated.emit()

    @QtCore.Property(int, notify=referenceChanged)
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value: int):
        if self._reference != value:
            self._reference = value
            self.referenceChanged.emit()
            self.canvasInvalidated.emit()

    # TODO: transmission related properties shall go to separated files.
    # # noinspection PyCallingNonCallable,PyTypeChecker
    # @QtCore.Property(str, notify=ipportModeChanged)
    # def ip(self):
    #     return self._ip

    # @ip.setter
    # def ip(self, value: str):
    #     if self._ip != value:
    #         self._ip = value
    #         self.ipportModeChanged.emit()
    #         self.canvasInvalidated.emit()

    # # noinspection PyCallingNonCallable,PyTypeChecker
    # @QtCore.Property(str, notify=ipportModeChanged)
    # def port(self):
    #     return self._port

    # @port.setter
    # def port(self, value: str):
    #     if self._port != value:
    #         self._port = value
    #         self.ipportModeChanged.emit()
    #         self.canvasInvalidated.emit()

    @QtCore.Property(bool, notify=channelpositionChanged)
    def position_mode(self):
        return self._position_mode

    @position_mode.setter
    def position_mode(self, value):
        self._position_mode = value
        self.channelpositionChanged.emit()

    @QtCore.Slot(float)
    def update_position_y(self, value: float):
        if self._mousepositony != value:
            self._mousepositony = value
            self._channelindex = int(value / self._channel_height)
            self.positionyChanged.emit()

    @QtCore.Property(float, notify=positionyChanged)
    def mousey(self):
        return self._mousepositony

    @QtCore.Property(float, notify=positionyChanged)
    def channel_index(self):
        return self._channelindex

    def reset(self):
        self._lowpass = 0.0
        self._hipass = 0.0
        self._notch = 0.0
        self.reset_areas()
        self.seekChanged.emit()
        self.canvasInvalidated.emit()

    def reset_areas(self):
        for area_viewmodel in self._area_viewmodels:
            area_viewmodel.reset()

    @property
    def loaded(self) -> bool:
        return self._project is not None

    @QtCore.Slot(float)
    def seek(self, seconds: float):
        if not self.loaded:
            return
        self.position = max(min(seconds, self._project.waveform.seconds), 0)
        self.canvasInvalidated.emit()

    @QtCore.Slot()
    def append_example(self):
        if self._project is None:
            return
        data = self._project.waveform.tensor
        from data_model.tensor import CompoundTensor
        from data_model.tensor.fragmented_tensor import FragmentedTensor
        assert isinstance(data, CompoundTensor)
        for channel in data:
            assert isinstance(channel, FragmentedTensor)
        t = .5
        amps = [segment.std() if len(segment) > 0 else 1 for segment in [
            channel[:int(time_axis.sampling_rate)] for (time_axis, channel) in zip(data.shape_def[1], data)
        ]]
        piece = [
            np.sin(np.linspace(
                self.seconds, self.seconds + t, int(t * time_axis.sampling_rate), dtype=np.float32) * 10
                   ) * amp
            for (time_axis, amp) in zip(data.shape_def[1], amps)
        ]
        self._project.append_data(piece)

    def set_selection_point(self, x: float, y: float, end_point=False):
        # noinspection PyPropertyAccess
        x += self.position
        self._selection_range[2], self._selection_range[3] = x, y
        if not end_point:
            self._selection_range[0], self._selection_range[1] = x, y
        self.selectionChanged.emit()
        self.canvasInvalidated.emit()

    def get_selection(self):
        s = self._selection_range
        (x1, x2), (y1, y2) = map(
            lambda a, b: ((a, b) if a <= b else (b, a)),
            (s[0], s[1]), (s[2], s[3]))
        # noinspection PyPropertyAccess
        x1, x2 = map(lambda x: x - self.position, [x1, x2])
        return x1, x2, y1, y2

    def get_selection1(self):
        s = self._selection_range
        (x1, x2), (y1, y2) = map(
            lambda a, b: ((a, b) if a <= b else (b, a)),
            (s[0], s[1]), (s[2], s[3]))
        # noinspection PyPropertyAccess
        x1, x2 = map(lambda x: x, [x1, x2])
        return x1, x2, y1, y2

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(bool, notify=maggotModeChanged)
    def maggot_mode(self):
        return self._maggot_mode

    @maggot_mode.setter
    def maggot_mode(self, value):
        self._maggot_mode = value
        self.maggotModeChanged.emit()
        self.canvasInvalidated.emit()

    # 设置 双模式   获取模式
    @QtCore.Property(bool, notify=waveModeChanged)
    def wave_mode(self):
        return self._wave_mode

    # 设置  修改  wave_mode模式
    @wave_mode.setter
    def wave_mode(self, value):
        self._wave_mode = value
        self.waveModeChanged.emit()
        self.canvasInvalidated.emit()

    # 设置 事件标注
    @QtCore.Property(str, notify=markbreatheeventChanged)
    def mark_breathe_event_num(self):
        return self._mark_breathe_event_num

    # 设置  修改 事件标注
    @mark_breathe_event_num.setter
    def mark_breathe_event_num(self, value):
        self._mark_breathe_event_num = value
        self.markbreatheeventChanged.emit()

    @QtCore.Property(str, notify=markbreatheeventChanged)
    def mark_spindle_notation_num(self):
        return self._mark_spindle_notation_num

    # 设置  修改 纺锤波事件标注
    @mark_spindle_notation_num.setter
    def mark_spindle_notation_num(self, value):
        self._mark_spindle_notation_num = value
        self.markbreatheeventChanged.emit()


    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(bool, notify=scrollModeChanged)
    def auto_scroll(self):
        print(self._auto_scroll)
        return self._auto_scroll

    @auto_scroll.setter
    def auto_scroll(self, value):
        self._auto_scroll = value
        print(self._auto_scroll)
        self.maggotModeChanged.emit()
        self.canvasInvalidated.emit()

    # 画脑地形图
    @QtCore.Slot()
    def draw_brainmap(self):
        name_channels = list()
        for i in range(np.size(self._project.waveform.channels)):
            name_channels.append(self._project.waveform.channels[i].name)
        brainmap = Brain_map(self._project.waveform.tensor, len(name_channels), name_channels)
        brainmap.draw_map()

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(int, notify=montageChanged)
    def montage_index(self):
        return self._montage_index

    @montage_index.setter
    def montage_index(self, value: int):
        if self._montage is None or value != self._montage_index:
            self._montage_index = value
            self._montage = MontageRegistry().all[value][1]()
            self.update_montage()

    @QtCore.Property(int,notify=colorChanged)
    def colour_list(self):
        return self._colour_list
    @colour_list.setter
    def colour_list(self,value:int):
        print('11111111111111111111111')
        c = [[255, 0, 0],[0, 0, 0],[0, 0, 255],[184, 134, 11],[139,0,139]]
        self._colour_list[self.channel_index] = c[value]
        self.colorChanged.emit()


    def update_montage(self):
        from viewmodel.waveform_area_viewmodel import WaveformAreaViewModel
        if self._montage is None:
            self._montage = MontageRegistry().all[self._montage_index][1]()

        self._montage.set_waveform(self._project.waveform)
        for area in self._area_viewmodels:
            self.canvasInvalidated.disconnect(area.canvasInvalidated)
        self._area_viewmodels = [WaveformAreaViewModel(
            page_viewmodel=self, montage_block=self._montage.get_block_at(i))
            for i in range(self._montage.get_block_counts())]
        for area in self._area_viewmodels:
            self.canvasInvalidated.connect(area.canvasInvalidated)
        self.reset_areas()
        self.montageChanged.emit()

    @QtCore.Slot()
    def save_changes(self):
        if self._project is None:
            return
        self._project.mark_sequence = self._mark_sequence
        self._project.mark_breathe_event_record = self.mark_breathe_event_record1
        self._project.mark_spindle_notation_record = self.mark_spindle_notation_record

        self._project.save()
        # Currently no need to use ThreadPool Executor. Fast enough.
        # with qasync.(1) as exec:
        #     await loop.run_in_executor(exec, loaded.save, True)

    @QtCore.Slot()
    def toggle_recv_mode(self):
        if self._eeg_client is None:
            logger.info("Begin receiving mode.")
            print('Begin receiving mode.')
            self._eeg_client = EegClient(
                on_batch=lambda b: self._project.append_data(b),
                on_closed=self._on_client_closed,
                ip=self._ip, port=self._port
            )
            asyncio.get_running_loop().create_task(self._eeg_client.run())
        else:
            logger.info("End receiving mode.")
            self._eeg_client.stop()
            self._on_client_closed()

    def _on_client_closed(self):
        self._eeg_client = None

    # 导出文件
    @QtCore.Slot(str)
    def export_file(self, path):
        loop = asyncio.get_running_loop()
        loop.create_task(self._async_export(loop, path))

    async def _async_export(self, loop, path):
        url = urlparse(path)
        assert url.scheme == "file"
        file = url2pathname(url.path)
        with qasync.QThreadExecutor(1) as exec:
            args = [ESigProject.export_as, file, self._project.waveform]
            await loop.run_in_executor(exec, *args)
