from __future__ import annotations

from protocols import Keyable
from . import PairDict
from typing import (
    TypeVar, Optional, Callable
)


K = TypeVar('K', bound=Keyable)
V = TypeVar('V')

Factory = Callable[[], V]

class DefaultPairDict(PairDict[K, V]):
    def __init__(self, default_factory: Optional[Factory[V]]=None):
        super().__init__()
        self.default_factory = default_factory

    def __missing__(self, first_key: K, other_key: K) -> V:
        if self.default_factory is None:
            return super().__missing__(first_key, other_key)

        value = self.default_factory()
        self[first_key][other_key] = value
        return value
