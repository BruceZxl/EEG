
import qasync
from algorithm.cwt import cwt
from algorithm.stft import stft
import numpy as np
import matplotlib.pyplot as plt
def showStft(input):
    stft_axes = stft.call(input)
    for f, t, Zxx in stft_axes:
        print(f, t, Zxx)
        plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, shading='gouraud')
        plt.title('STFT Magnitude')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.show()
def showCwt(input):
    cwt_axes = cwt.call(input)
    for cwtmatr in cwt_axes:
        # plt.imshow(cwtmatr, extent=[-1, 1, 31, 1], cmap='PRGn', aspect='auto',vmax = abs(cwtmatr).max(), vmin = -abs(cwtmatr).max())
        # plt.imshow(cwtmatr)
        plt.matshow(cwtmatr)
        plt.show()
        break
from data_model.waveform import WaveformModel
if __name__ == "__main__":
    data = []
    channels = []
    time_axes = []
    # path = './SC4001E0-PSG.edf'
    # path = 'F://WeChat//WeChat Files//wxid_b904ptiydvm512//FileStorage//File//2022-08//SC4001E0-PSG.edf'
    path = './test_generator.edf'
    # with qasync.QThreadExecutor(1) as exec:
    exec = WaveformModel.load_edf(path)
    # showStft(exec.tensor)
    showCwt(exec.tensor)

