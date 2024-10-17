"""
Commonly used utility functions and aliases
"""

import os
import io
import collections.abc
import sys
from pathlib import Path

try:
    import numpy as np
except:
    np = None

# this gonna save you a bunch of time
import importlib.util

pjoin = os.path.join


def open(file, mode='r', **kwargs):
    """ gives the "open" function the ability to automatically create any folder if necessary."""
    if 'w' in mode:
        ensure_mkdir(file)
    return io.open(file, mode, **kwargs)


def ensure_mkdir(path, parent=True):
    os.makedirs(Path(path).parent if parent else path, exist_ok=True)
    return path


def dict_get_or_create(dictionary, key, creation_function, creation_function_params=None):
    value = dictionary.get(key)
    if value is None:
        value = creation_function() if creation_function_params is None \
            else creation_function(**creation_function_params)
        dictionary[key] = value
    return value


def _split_list(the_list, cut_at):
    return [the_list[:cut_at], the_list[cut_at:]]


def split_list(the_list, cut_at):
    if isinstance(cut_at, collections.abc.Sequence):
        lists = [the_list]
        for cut_point in cut_at:
            lists += _split_list(lists.pop(), cut_point)
        return lists
    else:
        return _split_list(the_list, cut_at)


def import_file(basedir, name, as_name=None):
    path = pjoin(basedir, f"{name}.py")
    if as_name is None:
        as_name = name
    spec = importlib.util.spec_from_file_location(as_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


def _print_remaining(some_struct, recur_level, max_print_elements_of_struct):
    if len(some_struct) > max_print_elements_of_struct:
        _print(f"... (a total of {len(some_struct)} elements)", recur_level=recur_level + 1)


def _print(text, recur_level, end=None):
    print('\t' * recur_level, end='')
    print(text, end=end)


def _str(val):
    if np.array(val).dtype.kind in 'ui':
        return str(val)
    else:
        the_format = '{:.1E}' if np.abs(val) < .01 or np.abs(val) > 1e9 else "{:.2f}"
        return the_format.format(val)


def print_struct(some_struct, recur_level=0, end=None, max_print_elements_of_ndarray=16,
                 max_print_elements_of_struct=16, summarize_ndarray=False):
    """Fancy-print cascaded lists, tuples, and Numpy arrays."""
    openclose = None
    # Linear lists (list and tuple)
    if isinstance(some_struct, list):
        openclose = '[]'
    elif isinstance(some_struct, tuple):
        openclose = '()'
    # mappings
    elif isinstance(some_struct, dict):
        _print('{', recur_level)
        for key, _ in zip(some_struct, range(max_print_elements_of_struct)):
            _print(f"'{key}': ", recur_level + 1, end='')
            print_struct(some_struct[key], recur_level + 1, end='',
                         max_print_elements_of_ndarray=max_print_elements_of_ndarray,
                         max_print_elements_of_struct=max_print_elements_of_struct,
                         summarize_ndarray=summarize_ndarray)
            print(',')
        _print_remaining(some_struct, recur_level, max_print_elements_of_struct)
        _print('}', recur_level, end=end)
    elif np is not None and isinstance(some_struct, np.ndarray):
        flat_arr = some_struct.flat
        kind = some_struct.dtype.kind
        if max_print_elements_of_ndarray > 0 and len(flat_arr) > 0 and (kind in 'ifu'):
            if summarize_ndarray:
                arr_desc = f"range={_str(some_struct.mean())}±{_str(some_struct.std())}, " \
                           + f"min={_str(some_struct.min())}, max={_str(some_struct.max())}, data=["
            else:
                arr_desc = "["
            if len(flat_arr) > max_print_elements_of_ndarray:
                print_eles = max_print_elements_of_ndarray - 1
                print_dots = True
            else:
                print_eles = len(flat_arr)
                print_dots = False
            for i in range(print_eles - 1):
                arr_desc += _str(flat_arr[i]) + ", "
            arr_desc += _str(flat_arr[-1])
            if print_dots:
                arr_desc += ", ..."
            arr_desc += "]"
        else:
            arr_desc = "[...]"
        _print(
            f"Array(({some_struct.dtype}){'x'.join([str(dim) for dim in some_struct.shape])}, {arr_desc})",
            recur_level, end=end)
    else:
        _print(str(some_struct), recur_level, end=end)
    if openclose is not None:
        if len(some_struct) <= 0:
            _print(openclose, recur_level, end=end)
        else:
            _print(openclose[:1], recur_level)
            for ele, _ in zip(some_struct, range(max_print_elements_of_struct)):
                print_struct(ele, recur_level + 1, end='',
                             max_print_elements_of_ndarray=max_print_elements_of_ndarray,
                             max_print_elements_of_struct=max_print_elements_of_struct,
                             summarize_ndarray=summarize_ndarray)
                print(',')
            _print_remaining(some_struct, recur_level, max_print_elements_of_struct)
            _print(openclose[1:], recur_level, end=end)
