from __future__ import annotations

from typing import (
    TypeVar, Hashable,
    Dict, Callable
)


K = TypeVar('K', bound=Hashable)
V = TypeVar('V')


class DefaultWithKeyDict(Dict[K, V]):
    def __init__(self, factory: Callable[[K], V]):
        self.factory = factory

    def __missing__(self, key: K) -> V:
        value = self.factory(key)
        self[key] = value
        return value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        dict_repr = super().__repr__()
        factory_repr = repr(self.factory)

        return f'{class_name}({factory_repr}, {dict_repr})'
