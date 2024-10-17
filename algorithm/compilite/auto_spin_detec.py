import mne
import torch
import os
import numpy as np
from torch.utils.data import Dataset, DataLoader
from algorithm.models.SpinModel import BinaryClassificationModel

def read_data(data, fs):
    if fs != 256:
        return []
    window_size = int(0.5 * fs)
    slieced_data = []
    # print(data.shape[0])
    for start in range(0, data.shape[0], window_size):
        end = start + window_size
        if end <= data.shape[0]:
            data_slice = data[start:end]
            slieced_data.append(data_slice)
    slieced_data = np.array(slieced_data)
    test_data = torch.from_numpy(slieced_data)
    test_dataset = torch.utils.data.TensorDataset(test_data)
    test_loader = DataLoader(dataset=test_dataset,
                             batch_size=256,
                             shuffle=False)
    return test_loader

def auto_spin_detec(data, fs):
    pthfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_model.pth')
    test_loader = read_data(data, fs)
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
    # indices = np.random.choice(len(pred), size=20, replace=False)
    # print(len(pred))
    # pred[indices] = 1
    # print(len(pred))
    # print(np.sum(pred))
    return pred