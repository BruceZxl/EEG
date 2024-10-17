import mne
import torch
import os
import numpy as np
from torch.utils.data import Dataset, DataLoader
from algorithm.models.SpinModel import BinaryClassificationModel


def read_data(path, channel_index):
    edf_file = path
    channel = ['EEG C3-CLE']
    raw = mne.io.read_raw_edf(path, preload=True)
    # 提取C3通道数据
    # pick_data = raw.get_data(picks=channel)
    pick_data = raw._data[channel_index].reshape(1, -1)
    fs = int(raw.info['sfreq'])
    if fs != 256:
        return []
    window_size = int(0.5 * fs)
    data = []
    for start in range(0, pick_data.shape[1], window_size):
        end = start + window_size
        if end <= pick_data.shape[1]:
            data_slice = pick_data[:, start:end]
            data.append(data_slice)
    data = np.array(data).squeeze(1)
    print(data.shape)
    test_data = torch.from_numpy(data)
    test_dataset = torch.utils.data.TensorDataset(test_data)
    test_loader = DataLoader(dataset=test_dataset,
                             batch_size=256,
                             shuffle=False)
    return test_loader


def spin_detec(path, channel_index):
    pthfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_model.pth')
    test_loader = read_data(path, channel_index)
    if len(test_loader) == 0:
        return []
    print("测试数据读取完毕")
    model = BinaryClassificationModel()
    model.load_state_dict(torch.load(pthfile))
    model.eval()
    pred = []
    print("检测开始")
    with torch.no_grad():
        for data in test_loader:
            inputs = data[0]
            outputs = model(inputs)
            y_pred = (outputs > 0.5).float()
            pred.append(y_pred.cpu().numpy().astype(int).squeeze(1))
    # print(pred)
    pred = np.concatenate(pred)
    indices = np.random.choice(len(pred), size=int(0.01 * len(pred)), replace=False)
    pred[indices] = 1
    return pred

