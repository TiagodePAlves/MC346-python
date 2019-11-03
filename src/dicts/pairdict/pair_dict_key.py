from __future__ import annotations

from protocols import Keyable
from dataclasses import dataclass

from typing import (
    TYPE_CHECKING, overload, Any,
    TypeVar, Iterator, Optional,
    Union,

    Dict, Mapping, MutableMapping,
    KeysView, ValuesView, ItemsView
)
if TYPE_CHECKING:
    from . import PairDict



K = TypeVar('K', bound=Keyable)
V = TypeVar('V')


@dataclass(frozen=True)
class PairDictKey(Dict[K, V]):
    key: K
    pair_dict: PairDict[K, V]

    def __missing__(self, key: K) -> V:
        return self.pair_dict.__missing__(self.key, key)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        key = repr(self.key)
        pair_dict = repr(self.pair_dict)

        return f'{class_name}({key}, {pair_dict})'

    def as_view(self) -> PairDictKeyView[K, V]:
        return PairDictKeyView(self)


T = TypeVar('T')

@dataclass(frozen=True)
class PairDictKeyView(MutableMapping[K, V]):
    __key: PairDictKey[K, V]

    @property
    def key(self) -> K:
        return self.__key.key

    @property
    def __pair_dict(self) -> PairDict[K, V]:
        return self.__key.pair_dict

    def __len__(self) -> int:
        return len(self.__key)

    def __iter__(self) -> Iterator[K]:
        return iter(self.__key)

    def __getitem__(self, key: K) -> V:
        return self.__key[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.__pair_dict.set_pair(self.key, key, value)

    def __delitem__(self, key: K) -> None:
        self.__pair_dict.del_pair(self.key, key)

    def __contains__(self, key: Any) -> bool:
        return key in self.__key

    def keys(self) -> KeysView[K]:
        return self.__key.keys()

    def values(self) -> ValuesView[V]:
        return self.__key.values()

    def items(self) -> ItemsView[K, V]:
        return self.__key.items()

    @overload
    def get(self, key: K) -> Optional[V]: ...

    @overload
    def get(self, key: K, default: T) -> Union[V, T]: ...

    def get(self, key: K, default: Optional[T]=None) -> Union[V, Optional[T]]:
        return self.__key.get(key, default)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        key = repr(self.key)
        pair_dict = repr(self.__pair_dict)

        return f'{class_name}({key}, {pair_dict})'
