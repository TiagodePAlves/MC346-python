from __future__ import annotations

from protocols import Keyable, Literal
from . import PairDictKey
from dicts import TupleView, DefaultWithKeyDict

from typing import (
    cast, overload, TypeVar, Tuple,
    Any, Union, Iterator, Optional,

    MutableMapping, Mapping,
    KeysView, ValuesView, ItemsView
)


K = TypeVar('K', bound=Keyable)
V = TypeVar('V')


class PairDictTupleView(TupleView[K, K, V]):
    def __init__(self, pair_dict: PairDict[K, V]):
        super().__init__(pair_dict)

    def __iter__(self) -> Iterator[Tuple[K, K]]:
        for k1, k2 in super().__iter__():
            if k1 <= k2:
                yield k1, k2

    def __len__(self) -> int:
        return len(self.mapping)


T = TypeVar('T')

class MISSING: ...


class PairDict(Mapping[K, MutableMapping[K, V]]):
    def __init__(self) -> None:
        factory = lambda key: PairDictKey(key, self)
        self.__map = DefaultWithKeyDict[K, PairDictKey[K, V]](factory)
        self.__len = 0

    def __len__(self) -> int:
        return self.__len

    def __iter__(self) -> Iterator[K]:
        return iter(self.__map)

    def __contains__(self, key: Any) -> bool:
        return key in self.__map

    def __getitem__(self, key: K) -> MutableMapping[K, V]:
        return self.__map[key].as_view()

    @overload
    def get(self, key: K) -> Optional[MutableMapping[K, V]]: ...

    @overload
    def get(self, key: K, default: T) -> Union[MutableMapping[K, V], T]: ...

    def get(self, key: K, default: Optional[T]=None) -> Union[MutableMapping[K, V], T, None]:
        ans = self.__map.get(key, MISSING())

        if isinstance(ans, MISSING):
            return default
        else:
            return ans.as_view()

    def get_pair(self, first_key: K, other_key: K) -> V:
        return self.__map[first_key][other_key]

    def set_pair(self, first_key: K, other_key: K, value: V) -> None:
        if other_key not in self.__map[first_key]:
            self.__len += 1

        self.__map[first_key][other_key] = value
        self.__map[other_key][first_key] = value

    def del_pair(self, first_key: K, other_key: K) -> None:
        del self.__map[first_key][other_key]
        del self.__map[other_key][first_key]

        self.__len -= 1

    def clear(self) -> None:
        self.__map.clear()
        self.__len = 0

    def __missing__(self, first_key: K, other_key: K) -> V:
        raise KeyError((first_key, other_key))

    def as_view(self) -> PairDictTupleView[K, V]:
        return PairDictTupleView(self)

    @overload
    def keys(self) -> KeysView[K]: ...

    @overload
    def keys(self, *, pairs: Literal[True]) -> KeysView[Tuple[K, K]]: ...

    def keys(self, *, pairs: bool=False) -> Union[KeysView[K], KeysView[Tuple[K, K]]]:
        if pairs:
            return cast(KeysView[Tuple[K, K]], self.as_view().keys())
        else:
            return cast(KeysView[K], super().keys())

    @overload
    def values(self) -> ValuesView[MutableMapping[K, V]]: ...

    @overload
    def values(self, *, pairs: Literal[True]) -> ValuesView[V]: ...

    def values(self, *, pairs: bool=False) -> Union[ValuesView[V], ValuesView[MutableMapping[K, V]]]:
        if pairs:
            return self.as_view().values()
        else:
            return super().values()

    @overload
    def items(self) -> ItemsView[K, MutableMapping[K, V]]: ...

    @overload
    def items(self, *, pairs: Literal[True]) -> ItemsView[Tuple[K, K], V]: ...

    def items(self, *, pairs: bool=False) -> Union[ItemsView[Tuple[K, K], V], ItemsView[K, MutableMapping[K, V]]]:
        if pairs:
            return cast(ItemsView[Tuple[K, K], V], self.as_view().items())
        else:
            return cast(ItemsView[K, MutableMapping[K, V]], super().items())

    def __repr__(self) -> str:
        class_name = self.__class__.__name__

        def repr_item(key1: K, key2: K, value: V) -> str:
            return f'({repr(key1)}, {repr(key2)}): {repr(value)}'

        items_repr = '{' + ', '.join(repr_item(k1, k2, v) for (k1, k2), v in self.items(pairs=True)) + '}'

        return f'{class_name}({items_repr})'
