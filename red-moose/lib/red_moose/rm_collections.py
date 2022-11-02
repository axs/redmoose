from typing import Mapping, overload, Iterable, Tuple, Union, Iterator, \
    Callable

from red_moose.rm_types import KT, VT, T, VT_co, T_co
from collections.abc import MutableMapping
import eventkit as ev
from functools import wraps


class ObservableDict(MutableMapping):
    """ ObservableDict implementation where subscribers are notified tuple(k,v) on setting
    """

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> Iterator[T_co]:
        return iter(self._mapping)

    def __getitem__(self, k: KT) -> VT_co:
        return self._mapping[k]

    def __setitem__(self, k: KT, v: VT) -> None:
        self.set_event.emit((k, v))
        self._mapping[k] = v

    def __delitem__(self, k: KT) -> None:
        self.del_event.emit((k, self[k]))
        del self._mapping[k]

    def clear(self) -> None:
        self._mapping.clear()

    @overload
    def pop(self, k: KT) -> VT: ...

    @overload
    def pop(self, k: KT, default: Union[VT, T] = ...) -> Union[VT, T]: ...

    def pop(self, k: KT) -> VT:
        return self._mapping.pop(k)

    def popitem(self) -> Tuple[KT, VT]:
        return self._mapping.popitem()

    def setdefault(self, k: KT, default: VT = ...) -> VT:
        return self._mapping.setdefault(k, default)

    @overload
    def update(self, __m: Mapping[KT, VT], **kwargs: VT) -> None: ...

    @overload
    def update(self, __m: Iterable[Tuple[KT, VT]], **kwargs: VT) -> None: ...

    @overload
    def update(self, **kwargs: VT) -> None: ...

    def update(self, __m: Mapping[KT, VT], **kwargs: VT) -> None:
        self._mapping.update(__m, **kwargs)

    def keys(self):
        return self._mapping.keys()

    def values(self):
        return self._mapping.values()

    def __init__(self, *args, **kwargs):
        self.set_event = ev.Event()
        self.del_event = ev.Event()
        self._mapping = {}
        self._mapping.update(*args, **kwargs)

    def subscribe_to_setitem(self, listener: Callable):
        self.set_event += listener

    def unsubscribe_from_setitem(self, listener: Callable):
        self.set_event -= listener

    def subscribe_to_del(self, listener: Callable):
        self.del_event += listener

    def unsubscribe_from_del(self, listener: Callable):
        self.del_event -= listener

    def subscribe_decorator(self, listener: Callable):
        self.subscribe_to_setitem(listener)

        @wraps(listener)
        def listener_wrapper(*args):
            return listener(*args)

        return listener_wrapper
