import torch
import numpy as np
import scipy.io as sio
from PySide6 import QtCore
from PySide6.QtCore import QObject
from tqdm import tqdm
from algorithm.MDD.model_PAC import EcaSparseAttention

# def encode_onehot(labels):
#     classes = sorted(list(set(labels)))
#     classes_dict = {c: np.identity(len(classes))[i, :] for i, c in enumerate(classes)}
#     labels_onehot = np.array(list(map(classes_dict.get, labels)), dtype=np.int32)
#     return labels_onehot
#
# def load_data3(file_path):
#     adj_sub = sio.loadmat(file_path)
#     adj_data = adj_sub['pac']
#     label_file = adj_sub['label']
#     label_all = []
#     adj_all = []
#     for j in tqdm(range(adj_data.shape[4])):
#         adj_slice = adj_data[:, :, :, :, j]
#         adj_all.append(adj_slice)
#         label_all.append(label_file[0][0])
#     adj = np.array(adj_all)
#     label = np.array(label_all)
#     label_onehot = encode_onehot(label.flatten())
#     label_onehot = torch.LongTensor(np.where(label_onehot)[1])
#     adj = torch.FloatTensor(adj)
#     return adj, label_onehot
#
# def load_and_predict(model_path, data_path, labels):
#     model = EcaSparseAttention(nclasses=2, cross_band_num=1, channel_num=128, attention_lim=0.1, dropout=0.5)
#     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
#     model.eval()
#     data, label = load_data3(data_path)
#     data = torch.tensor(data, dtype=torch.float32)
#     with torch.no_grad():
#         predictions, attention_scores = model(data)
#     predicted_indices = torch.argmax(predictions, dim=1)
#     predicted_labels = [labels[idx] for idx in predicted_indices]
#     return predicted_labels
#
# class Backend(QObject):
#     predictionChanged = pyqtSignal(list, arguments=['predictions'])
#
#     @pyqtSlot(str, str)
#     def predict(self, modelFilePath, dataFilePath):
#         labels = [0, 1]
#         predicted_labels = load_and_predict(modelFilePath, dataFilePath, labels)
#         self.predictionChanged.emit(predicted_labels)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     engine = QQmlApplicationEngine()
#
#     backend = Backend()
#     engine.rootContext().setContextProperty("backend", backend)
#
#     # 确保 QML 文件路径正确
#     engine.load(r"D:/pythonProject/EEGplatformLS/eeg-display-platformpyqt-new_combine/view/algorithm_window.qml")
#
#     if not engine.rootObjects():
#         sys.exit(-1)
#     sys.exit(app.exec_())

#-----------new-----------------
class AlgorithmViewModel(QObject):
    predictionChanged = QtCore.Signal(list)

    @QtCore.Slot(str, str)
    def predict(self, modelFilePath, dataFilePath):
        if modelFilePath.startswith("file:///"):
            modelFilePath = modelFilePath[8:]
        if dataFilePath.startswith("file:///"):
            dataFilePath = dataFilePath[8:]

        model = EcaSparseAttention(nclasses=2, cross_band_num=1, channel_num=128, attention_lim=0.1, dropout=0.5)
        model.load_state_dict(torch.load(modelFilePath, map_location=torch.device('cpu')))
        model.eval()
        data, label = self.load_data3(dataFilePath)
        data = torch.tensor(data, dtype=torch.float32)
        labels = [0, 1]
        with torch.no_grad():
            predictions, attention_scores = model(data)
        predicted_indices = torch.argmax(predictions, dim=1)
        predicted_labels = [labels[idx] for idx in predicted_indices]
        print("Predicted Labels: ", predicted_labels)
        self.predictionChanged.emit(predicted_labels)

    def load_data3(self, file_path):
        adj_sub = sio.loadmat(file_path)
        adj_data = adj_sub['pac']
        label_file = adj_sub['label']
        label_all = []
        adj_all = []
        for j in tqdm(range(adj_data.shape[4])):
            adj_slice = adj_data[:, :, :, :, j]
            adj_all.append(adj_slice)
            label_all.append(label_file[0][0])
        adj = np.array(adj_all)
        label = np.array(label_all)
        label_onehot = self.encode_onehot(label.flatten())
        label_onehot = torch.LongTensor(np.where(label_onehot)[1])
        adj = torch.FloatTensor(adj)
        return adj, label_onehot

    def encode_onehot(self, labels):
        classes = sorted(list(set(labels)))
        classes_dict = {c: np.identity(len(classes))[i, :] for i, c in enumerate(classes)}
        labels_onehot = np.array(list(map(classes_dict.get, labels)), dtype=np.int32)
        return labels_onehot