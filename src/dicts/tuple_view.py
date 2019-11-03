from __future__ import annotations

from protocols import Keyable
from dataclasses import dataclass

from typing import (
    TypeVar, overload,

    Tuple, Hashable, Optional,
    Any, Mapping, Iterator,
    Union
)


K1 = TypeVar('K1', bound=Hashable)
K2 = TypeVar('K2', bound=Hashable)
V = TypeVar('V')

T = TypeVar('T')

class MISSING: ...


@dataclass(frozen=True)
class TupleView(Mapping[Tuple[K1, K2], V]):
    mapping: Mapping[K1, Mapping[K2, V]]

    def __len__(self) -> int:
        return sum(map(len, self.mapping.values()))

    def __contains__(self, pair: Any) -> bool:
        if not isinstance(pair, tuple) or len(pair) != 2:
            return False

        k1, k2 = pair
        return k1 in self.mapping and k2 in self.mapping[k1]

    def __iter__(self) -> Iterator[Tuple[K1, K2]]:
        for k1, map_ in self.mapping.items():
            for k2 in map_:
                yield k1, k2

    def __getitem__(self, pair: Tuple[K1, K2]) -> V:
        try:
            return self.mapping[pair[0]][pair[1]]
        except KeyError:
            raise KeyError(pair)

    @overload
    def get(self, pair: Tuple[K1, K2]) -> Optional[V]: ...

    @overload
    def get(self, pair: Tuple[K1, K2], default: T) -> Union[V, T]: ...

    def get(self, pair: Tuple[K1, K2], default: Optional[T]=None) -> Union[V, T, None]:
        k1, k2 = pair

        ans = self.mapping.get(k1, MISSING())
        if isinstance(ans, MISSING):
            return default

        return ans.get(k2, default)

    def __eq__(self, other: Any) -> bool:
        return bool(self.mapping == other)

    def __ne__(self, other: Any) -> bool:
        return bool(self.mapping != other)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}({repr(self.mapping)})'
