from pathlib import Path
from typing import Optional, Callable, List

import mne
import numpy as np
import pyedflib
from loguru import logger
from mne.io.constants import FIFF
from datetime import date
import math

from connect_database.tb_sleep_stage_rec import save_sleep_data
from data_model.axes import TimeAxis, EChannelAxis, EChannelDef
from data_model.tensor.compound_tensor import CompoundTensor
from data_model.tensor.fragmented_tensor import FragmentedTensor
from data_model.tensor.pure_tensor import PureTensor
from data_model.tensor import Tensor
from data_model.waveform import WaveformModel
from project.project_state import ProjectState
from project.saver import ProjectSaver
from utils.json_utils import json_write, json_read
from utils.mitertools import apply
_k_tensor = "data"
_k_project = "project"
_k_project_v = "esig"
_k_manifest_path = "project.json"
_k_state_path = "state.json"

_k_chunk_size = 1024 * 32


class ESigProject:
    def __init__(self, directory: Optional[Path], waveform: WaveformModel):
        self.directory = directory
        self.waveform = waveform
        self._data_clean = self._manifest_clean = False
        self.mark_sequence = {}  # 标注的内容字典
        self.state = ProjectState(save_action=lambda: self._saver.save())
        self._saver = ProjectSaver(self.save, min_interval=10)
        self._listeners = set()
        self.mark_breathe_event_record = {}  # 呼吸事件的标注记录
        self.mark_spindle_notation_record = {}

    def save_to(self, directory: Optional[Path], full=False):
        directory = directory or self.directory
        if directory is None:
            return
        directory.mkdir(exist_ok=True)
        if full or not self._data_clean:
            self.waveform.tensor.save_to(directory, _k_tensor, full=full)
            self._data_clean = True
        if full or not self._manifest_clean:
            json_write({
                _k_project: _k_project_v
            }, self.directory / _k_manifest_path)
            self._manifest_clean = True
        state = self.state.save(full=full)
        if state is not None:
            json_write(state, self.directory / _k_state_path)
        print(self.mark_sequence)
        json_write(self.mark_sequence, self.directory / "mark5.json")  # 写入标注信息  命名为路径下mark5.json
        json_write(self.mark_spindle_notation_record,self.directory/ "mark_spindle_notation.json")
        json_write(self.mark_breathe_event_record, self.directory / "mark_breathe_event.json")  # 写入标注信息  命名为路径下mark_breathe_event.json

    def save(self, full=False):
        self.save_to(None, full=full)

    @staticmethod
    def load(directory: Path):
        self = ESigProject(
            directory, WaveformModel(Tensor.load_from(directory, _k_tensor))
        )
        obj = json_read(self.directory / _k_manifest_path)
        assert obj[_k_project] == _k_project_v
        self.state.load(json_read(self.directory / _k_state_path))
        self.mark_sequence = json_read(self.directory / "mark5.json")  # 读取mark5.json
        self.mark_breathe_event_record = json_read(self.directory / "mark_breathe_event.json")  # 读取mark_breathe_event.json
        self.mark_spindle_notation_record = json_read(self.directory/ "mark_spindle_notation.json") #读取纺锤波记录文件

        self._data_clean = self._manifest_clean = True
        return self

    @staticmethod
    def import_from(path: Path, format="edf"):
        if format == "edf":
            return ESigProject._import_edf(path)
        elif format == "bdf":
            return ESigProject._import_bdf(path)
        raise RuntimeError()

    @staticmethod
    def create(path: Path, channels: List[EChannelDef], sampling_rates: List[float]):
        data = []
        time_axes = []
        for sampling_rate in sampling_rates:
            time_axis = TimeAxis(sampling_rate=sampling_rate)
            data.append(FragmentedTensor(
                data=[], shape_def=(time_axis,), fragment_size=_k_chunk_size, length=0
            ))
            time_axes.append(time_axis)
        tensor = CompoundTensor(
            data=data, shape_def=(EChannelAxis(channels=channels), time_axes)
        )
        instance = ESigProject(path, WaveformModel(tensor))
        instance.save(full=True)
        return instance

    @staticmethod
    def _import_edf(path: Path):
        path = str(path)
        try:
            tensor = _load_edf_bdf_fast(path)
        except:
            logger.warning("Cannot load with PyEDFlib, using the slower mne instead.")
            tensor = _load_edf_slow(path)
        return ESigProject(None, WaveformModel(tensor))

    @staticmethod
    def _import_bdf(path: Path):
        path = str(path)
        try:
            tensor = _load_edf_bdf_fast(path)
        except:
            logger.warning("Cannot load with PyEDFlib, using the slower mne instead.")
            tensor = _load_bdf_slow(path)
        return ESigProject(None, WaveformModel(tensor))

    @staticmethod
    def sample(duration: int = 1000, sampling_rate: int = 128):
        t = np.linspace(0, duration, sampling_rate * duration)
        data = np.concatenate([
            np.sin(t * 2 * np.pi * (i + 1), dtype=np.float32)[:, np.newaxis]
            for i in range(8)
        ], axis=1)
        data[:500] = 0
        return ESigProject(None, WaveformModel(
            PureTensor(data, (
                TimeAxis(sampling_rate=sampling_rate),
                EChannelAxis(
                    kind="e", channels=[
                        EChannelDef(f"C{i}", unit_m=FIFF.FIFF_UNITM_NONE) for i in range(8)
                    ])
            ))))

    def unload(self):
        self._saver.save(force=True)
        self._saver = None
        self.state = None

    def append_data(self, piece):
        self.waveform.tensor.append(piece)
        self._data_clean = False
        self.waveform.on_data_changed()
        for listener in self._listeners:
            listener()

    def add_listener(self, callback: Callable):
        self._listeners.add(callback)

    # 导出文件
    @staticmethod
    def export_as(file: str, waveform: WaveformModel):
        if file[-3:] == 'edf':
            export_as_edf(file, waveform)
        elif file[-3:] == 'bdf':
            export_as_bdf(file, waveform)


def _load_edf_bdf_fast(path: str) -> Tensor:
    data = []
    channels = []
    time_axes = []
    with pyedflib.EdfReader(path) as edf:
        for i in range(edf.signals_in_file):
            data.append(edf.readSignal(i))
            channels.append(EChannelDef.from_pyedflib_info(edf, i))
            time_axes.append(TimeAxis(sampling_rate=edf.getSampleFrequency(i)))
    data = _convert_to_fragmented(data, time_axes)
    return CompoundTensor(data, (EChannelAxis(kind="e", channels=channels), time_axes))


def _load_edf_slow(path: str) -> Tensor:
    with mne.io.read_raw_edf(path) as edf:
        ch_names = edf.ch_names
    data = []
    channels = []
    time_axes = []
    for ch_name in ch_names:
        excluded = ch_names[:]
        excluded.remove(ch_name)
        with mne.io.read_raw_edf(path, exclude=excluded) as edf:
            data.append(edf.get_data(picks=ch_name).ravel())
            channels.append(EChannelDef.from_mne_channel_info(edf.info["chs"][0]))
            time_axes.append(TimeAxis(sampling_rate=edf.info["sfreq"]))
    data = _convert_to_fragmented(data, time_axes)
    return CompoundTensor(data, (EChannelAxis(kind="e", channels=channels), time_axes))


def _load_bdf_slow(path: str) -> Tensor:
    with mne.io.read_raw_bdf(path) as bdf:
        ch_names = bdf.ch_names
    data = []
    channels = []
    time_axes = []
    for ch_name in ch_names:
        excluded = ch_names[:]
        excluded.remove(ch_name)
        with mne.io.read_raw_bdf(path, exclude=excluded) as bdf:
            data.append(bdf.get_data(picks=ch_name).ravel())
            channels.append(EChannelDef.from_mne_channel_info(bdf.info["chs"][0]))
            time_axes.append(TimeAxis(sampling_rate=bdf.info["sfreq"]))
    data = _convert_to_fragmented(data, time_axes)
    return CompoundTensor(data, (EChannelAxis(kind="e", channels=channels), time_axes))


def _convert_to_fragmented(data, time_axes):
    result = []
    for channel, time_axis in zip(data, time_axes):
        length = len(channel)
        channel = np.split(channel, np.arange(_k_chunk_size, len(channel), _k_chunk_size))
        channel[-1] = np.pad(channel[-1], ((0, _k_chunk_size - len(channel[-1]),),))
        # print([len(x) for x in channel])
        result.append(FragmentedTensor(
            data=channel, shape_def=(time_axis,), fragment_size=_k_chunk_size, length=length
        ))
    return result


# 导出edf文件
def export_as_edf(file, waveform):
    data = []
    time_axis: list[TimeAxis] = waveform.tensor.shape_def[waveform.index_time_axis]
    f = pyedflib.EdfWriter(file, waveform.num_channels, file_type=pyedflib.FILETYPE_EDFPLUS)
    f.setBirthdate(date(2000, 1, 1))  # 设置开始日期
    for i in range(waveform.num_channels):
        d = waveform.tensor.data[i]
        temp_data = np.concatenate(d.data)[:len(d)]
        data.append(temp_data)
        f.setLabel(i, waveform.channels[i].name)  # 设置通道标签
        if waveform.channels[i].unit_m == FIFF.FIFF_UNITM_MU:  # 设置通道单位
            f.setPhysicalDimension(i, "uV")
        elif waveform.channels[i].unit_m == FIFF.FIFF_UNITM_M:
            f.setPhysicalDimension(i, "mV")
        elif waveform.channels[i].unit_m == FIFF.FIFF_UNITM_NONE:
            f.setPhysicalDimension(i, "V")
        f.setSamplefrequency(i, time_axis[i].sampling_rate)  # 设置采样频率
        f.setPhysicalMaximum(i, max(temp_data))  # 设置物理最大值和最小值
        if max(temp_data) == min(temp_data):
            f.setPhysicalMinimum(i, min(temp_data)-1.0)
        else:
            f.setPhysicalMinimum(i, min(temp_data))
    f.writeSamples(data)  # 存储数据
    f.close()


# 导出bdf文件
def export_as_bdf(file, waveform):
    data = []
    time_axis: list[TimeAxis] = waveform.tensor.shape_def[waveform.index_time_axis]
    f = pyedflib.EdfWriter(file, waveform.num_channels, file_type=pyedflib.FILETYPE_BDFPLUS)
    f.setBirthdate(date(2000, 1, 1))  # 设置开始日期
    for i in range(waveform.num_channels):
        d = waveform.tensor.data[i]
        temp_data = np.concatenate(d.data)[:len(d)]
        data.append(temp_data)
        f.setLabel(i, waveform.channels[i].name)  # 设置通道标签
        if waveform.channels[i].unit_m == FIFF.FIFF_UNITM_MU:  # 设置通道单位
            f.setPhysicalDimension(i, "uV")
        elif waveform.channels[i].unit_m == FIFF.FIFF_UNITM_M:
            f.setPhysicalDimension(i, "mV")
        elif waveform.channels[i].unit_m == FIFF.FIFF_UNITM_NONE:
            f.setPhysicalDimension(i, "V")
        f.setSamplefrequency(i, time_axis[i].sampling_rate)  # 设置采样频率
        f.setPhysicalMaximum(i, max(temp_data))  # 设置物理最大值和最小值
        if max(temp_data) == min(temp_data):
            f.setPhysicalMinimum(i, min(temp_data) - 1.0)
        else:
            f.setPhysicalMinimum(i, min(temp_data))
    f.writeSamples(data)  # 存储数据
    f.close()
