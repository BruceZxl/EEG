from typing import Callable, TypeVar, Iterable, Iterator, MutableMapping

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def bfs_tree(root: T, extend_fn: Callable[[T], Iterable[T]]):
    q, i = [root], 0
    while i < len(q):
        e, i = q[i], i + 1
        yield e
        q.extend(extend_fn(e))


class LazyList:

    def __init__(self, iterator: Iterator):
        self._cache = []
        self._iterator = iterator

    def __iter__(self):
        return _LazyListIterator(self)

    def __len__(self):
        return len(self._cache)

    def __getitem__(self, item):
        if len(self._cache) > item:
            return self._cache[item]
        if len(self._cache) < item:
            raise RuntimeError()
        e = next(self._iterator)
        self._cache.append(e)
        return e


class _LazyListIterator:

    def __init__(self, lazy_list: LazyList):
        self._index = 0
        self._lazy_list = lazy_list

    def __next__(self):
        e = self._lazy_list[self._index]
        self._index += 1
        return e


def expr(_):
    return _ExprWrapper()


class _ExprWrapper:

    def expr(self, _):
        return self


def apply(self, *fns: Callable):
    for fn in fns:
        fn(self)
    return self


def transform_for_key(dick: MutableMapping[K, V], key: K, transform: Callable[[V], V]):
    dick[key] = transform(dick[key])
    return dick


def rename_dict_value(dick: MutableMapping[K, V], key: K, new_key: K):
    dick[new_key] = dick.pop(key)
    return dick


def do_assert(cond, message=None):
    if message is None:
        assert cond
    else:
        assert cond, message


def do_raise(error):
    raise error
