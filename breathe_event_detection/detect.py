import math
import numpy as np
import biosppy.signals.tools as st
import torch
from torch.utils.data import TensorDataset, DataLoader
from biosppy.signals.ecg import correct_rpeaks, hamilton_segmenter
from scipy.signal import medfilt
from scipy.interpolate import splev, splrep

from breathe_event_detection.apnea_model import Apnea_net

Batch_size = 128
before = 2  # forward interval (min)
after = 2  # backward interval (min)
hr_min = 20
hr_max = 300
ir = 3  # interpolate interval
scaler = lambda arr: (arr - np.min(arr)) / (np.max(arr) - np.min(arr))


def preprocess(signals, fs):
    sample = fs * 60  # 1 min's sample points

    x = []
    for j in range(math.ceil(len(signals) / sample)):
        if j < before or (j + 1 + after) > len(signals) / float(sample):
            continue
        signal = signals[int((j - before) * sample):int((j + 1 + after) * sample)]
        signal, _, _ = st.filter_signal(signal, ftype='FIR', band='bandpass', order=int(0.3 * fs),
                                        frequency=[3, 45], sampling_rate=fs)
        # Find R peaks
        rpeaks, = hamilton_segmenter(signal, sampling_rate=fs)
        rpeaks, = correct_rpeaks(signal, rpeaks=rpeaks, sampling_rate=fs, tol=0.1)
        # Remove abnormal R peaks signal
        if len(rpeaks) / (1 + after + before) < 40 or len(rpeaks) / (1 + after + before) > 200:
            continue
        # Extract RRI, Ampl signal
        rri_tm, rri_signal = rpeaks[1:] / float(fs), np.diff(rpeaks) / float(fs)
        rri_signal = medfilt(rri_signal, kernel_size=3)
        ampl_tm, ampl_siganl = rpeaks / float(fs), signal[rpeaks]
        hr = 60 / rri_signal
        # Remove physiologically impossible HR signal
        tm = np.arange(0, (before + 1 + after) * 60, step=1 / float(ir))
        # Save extracted signal
        rri_interp_signal = splev(tm, splrep(rri_tm, scaler(rri_signal), k=3), ext=1)
        ampl_interp_signal = splev(tm, splrep(ampl_tm, scaler(ampl_siganl), k=3), ext=1)
        x.append([rri_interp_signal, ampl_interp_signal])

    x = np.array(x, dtype="float32").transpose((0, 2, 1))
    x = torch.tensor(x)

    return x


def predicted_to_event(predicted):
    time = [i + before for i, label in enumerate(predicted) if label == 0]
    start = []
    end = []
    j = 0
    for i, item in enumerate(time):
        if i > 0:
            if time[i] != time[i - 1] + 1:
                tmp1 = time[j:i]
                start.append(tmp1[0] * 60.0)
                end.append(tmp1[-1] * 60.0)
                j = i
    tmp2 = time[j:]
    start.append(tmp2[0] * 60.0)
    end.append(tmp2[-1] * 60.0)

    return start, end


def breathe_event_detect(signal, fs):
    x = preprocess(signal, fs)  # 预处理
    dataset = TensorDataset(x)
    dataloader = DataLoader(dataset, batch_size=Batch_size, shuffle=False, num_workers=1)

    # 加载模型
    model = Apnea_net()
    model.load_state_dict(torch.load("breathe_event_detection/transformer_encoder_params.pkl", map_location='cpu'))
    model.eval()

    # 检测
    detect_predicted = []
    with torch.no_grad():  # don't keep track of the info necessary to calculate the gradients
        for batch_idx, (data, ) in enumerate(dataloader):
            data = data.transpose(1, 2).contiguous()

            outputs, features = model(data)
            predicted = torch.where(outputs.data > 0.5, torch.from_numpy(np.asarray([1])),
                                    torch.from_numpy(np.asarray([0])))
            predicted = list(np.array(predicted[:, 0]))
            detect_predicted.extend(predicted)  # 1为无事件，0为呼吸暂停

    # 将检测结果转换为起始和结束时间
    start, end = predicted_to_event(detect_predicted)

    return start, end
