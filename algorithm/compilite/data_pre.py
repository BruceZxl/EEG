import mne
import numpy as np
import os
import torch
import sys
from algorithm.models import newModel


def read_data(raw):
    channels = ['EEG Fpz-Cz', 'EOG horizontal', 'EMG submental']
    fs = int(raw.info['sfreq'])
    data = raw.get_data(picks=channels)
    seg = fs * 30
    seg_num = len(data[0]) // seg
    data = data[:, :seg_num * seg].reshape([-1, seg_num, seg])
    data = np.moveaxis(data, 0, 1)
    # data = np.array()
    test_data = torch.from_numpy(data)
    dataset = torch.utils.data.TensorDataset(test_data)
    test_loader = torch.utils.data.DataLoader(dataset=dataset,
                                              batch_size=1000,
                                              shuffle=False)
    return test_loader


def stage_MMFCA(path):
    pthfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_best.pt')
    raw = mne.io.read_raw_edf(path)
    present_channels = raw.info['ch_names']
    channels = ['EEG Fpz-Cz', 'EOG horizontal', 'EMG submental']
    missing = [ch for ch in channels if ch not in present_channels]
    if len(missing) != 0:
        return []
    test_loader = read_data(raw)
    print("数据读取完毕")
    model = newModel.SleepClass()
    model.load_state_dict(torch.load(pthfile, map_location=torch.device('cpu')))
    model.eval()
    pred = []
    print("分期开始")
    with torch.no_grad():
        for data in test_loader:
            inputs = data[0]
            y_pred, _ = model(inputs)
            y_pred = y_pred.argmax(axis=-1)
            pred.append(y_pred)
    pred = torch.cat(pred, dim=0)
    pred = pred.cpu().numpy()
    print("分期完成")
    return pred