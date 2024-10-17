INCLUDED_CHANNELS_DETAILS_ASSM = {
    "EEG": {
        "channels": ["F3-M2", "F4-M1", "C3-M2", "C4-M1", "O1-M2", "O2-M1"],
        "filter-params": [.3, 35.],
        "target-sampling-rate": 100,
        "scaling": 1e6
    }, "EOG": {
        "channels": ["E1-M2", "E2-M2"],
        "filter-params": [.5, 10.],
        "target-sampling-rate": 100,
        "scaling": 1e6
    }
}

SEGMENT_LENGTH_SECS = 30
SAMPLING_RATE = 1000
SAMPLING_RATE_ASSM = 1024

# 送入模型时，NotScored将样本权重置零（序列时，如LSTM或变形器）或丢弃（单片段，如经典ML）
# 其它类减一，以从0开始
STAGE_LABELS_NAME_TO_INT = {
    'NotScored': 0, 'Wake': 1, 'NonREM1': 2, 'NonREM2': 3, 'NonREM3': 4, 'REM': 5,
    '-': 0, 'W': 1, 'N1': 2, 'N2': 3, 'N3': 4
}

STAGE_SHORT_NAMES = ['W', 'R', 'N1', 'N2', 'N3']
