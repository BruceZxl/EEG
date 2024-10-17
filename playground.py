import shutil
from pathlib import Path

import numpy as np
from mne.io.constants import FIFF

from data_model.axes import EChannelAxis, EChannelDef, TimeAxis
from data_model.tensor import CompoundTensor, PureTensor, Tensor
from data_model.tensor.fragmented_tensor import FragmentedTensor


def try_saveload():
    debug_path = Path(r"C:\temp\1")
    debug_path_second = Path(r"C:\temp\2")
    shutil.rmtree(debug_path, ignore_errors=True)
    shutil.rmtree(debug_path_second, ignore_errors=True)
    debug_path.mkdir(exist_ok=True)
    debug_path_second.mkdir(exist_ok=True)
    num_channels = 4
    shape = (
        EChannelAxis(channels=[
            EChannelDef(f"C{i}", unit_m=FIFF.FIFF_UNITM_NONE) for i in range(num_channels)
        ]),
        [TimeAxis(sampling_rate=128) for i in range(num_channels)]
    )
    t = CompoundTensor(
        data=[
            FragmentedTensor(
                data=[np.zeros((32,), dtype=np.float32) + i for _ in range(8)],
                shape_def=tuple([shape[1][i]] + list(shape[2:])),
                fragment_size=32,
                length=32 * 7 + 10
            )
            for i in range(num_channels)
        ],
        shape_def=shape
    )
    # t = CompoundTensor(
    #     data=[
    #         PureTensor(
    #             data=np.zeros((256,), dtype=np.float32) + i,
    #             shape_def=tuple([shape[1][i]] + list(shape[2:]))
    #         )
    #         for i in range(num_channels)
    #     ],
    #     shape_def=shape
    # )
    t.save_to(debug_path, "data", full=True)
    s = Tensor.load_from(debug_path, "data")
    s.save_to(debug_path, "data2", full=True)
    s.append([np.zeros((50,), dtype=np.int32) + i for i in range(num_channels)])
    s.save_to(debug_path_second, "qwq")


def try_slice():
    num_channels = 4
    shape = (
        EChannelAxis(channels=[
            EChannelDef(f"C{i}", unit_m=FIFF.FIFF_UNITM_NONE) for i in range(num_channels)
        ]),
        [TimeAxis(sampling_rate=128) for i in range(num_channels)]
    )
    t = CompoundTensor(
        data=[
            PureTensor(
                data=np.zeros((256,), dtype=np.float32) + i,
                shape_def=tuple([shape[1][i]] + list(shape[2:]))
            )
            for i in range(num_channels)
        ],
        shape_def=shape
    )
    print(t[0])
    print("====")
    print(t[0:, 1])
    print("====")
    t = CompoundTensor(
        data=[
            FragmentedTensor(
                data=[np.zeros((32,), dtype=np.float32) + i for _ in range(8)],
                shape_def=tuple([shape[1][i]] + list(shape[2:])),
                fragment_size=32,
                length=32 * 7 + 10
            )
            for i in range(num_channels)
        ],
        shape_def=shape
    )
    print(t[0])
    print("====")
    print(t[2:, 1])
    print("====")
    x = t[2:, 2:77]
    print(x, [xx.shape for xx in x])
    print("====")


if __name__ == "__main__":
    # try_saveload()
    try_slice()
