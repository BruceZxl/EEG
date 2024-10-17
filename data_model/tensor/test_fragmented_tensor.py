from unittest import TestCase

import numpy as np
from mne.io.constants import FIFF

from data_model.axes import TimeAxis, EChannelAxis, EChannelDef
from data_model.tensor.fragmented_tensor import FragmentedTensor


class TestFragmentedTensor(TestCase):
    def test_append(self):
        seq = [1, 2, 3, 7, 222, 3, 2, 1, 7]
        num_chs = 7
        for block_size in [4, 17, 32]:
            tensor = _prepare_tensor(num_chs, block_size)
            segs = []
            for i, seg_size in enumerate(seq):
                seg = np.zeros((seg_size, num_chs), dtype=np.float32) + i * 100 + [list(range(num_chs))]
                tensor.append(seg)
                segs.append(seg)
            assert tensor.length == sum(seq)
            for block in tensor.data:
                assert len(block) == block_size
            data = np.concatenate(tensor.data, axis=0)
            assert (tensor.length + block_size) > len(data) >= tensor.length
            offset = 0
            for expected_seg, seg_size in zip(segs, seq):
                new_offset = offset + seg_size
                assert np.allclose(data[offset:new_offset], expected_seg)
                offset = new_offset

    def test_slice(self):
        num_chs = 3
        num_samples = 1027
        for block_size in [4, 17, 32, 251, 2048]:
            tensor = _prepare_tensor(num_chs, block_size)
            tensor.append(np.repeat(
                np.arange(num_samples, dtype=np.float32)[:, np.newaxis] * 1000,
                num_chs, axis=1) + [list(range(num_chs))])
            for l, r in [(0, 9), (123, 244), (333, num_samples), (244, 777)]:
                seg = tensor[l:r]
                assert r - l == len(seg)
                assert np.allclose(
                    np.repeat(
                        np.arange(l, r, dtype=np.float32)[:, np.newaxis] * 1000,
                        num_chs, axis=1) + [list(range(num_chs))], seg
                )


def _prepare_tensor(num_chs, block_size):
    return FragmentedTensor(data=[], shape_def=(TimeAxis(), EChannelAxis(channels=[
        EChannelDef(f"C{i}", unit_m=FIFF.FIFF_UNITM_NONE) for i in range(num_chs)
    ])), fragment_size=block_size, length=0)
