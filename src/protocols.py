from __future__ import annotations

from functools import total_ordering
from typing import TypeVar, Hashable
try:
    from typing_extensions import Protocol, Literal
except ModuleNotFoundError:
    class Protocol: ...  # type: ignore
    class Literal: ...   # type: ignore

__all__ = ["Comparable", "Orderable", "Additive", "Literal"]



C = TypeVar('C', bound='Comparable')

class Comparable(Protocol):
    def __eq__(self: C, other: C) -> bool:
        ...


class Keyable(Comparable, Hashable, Protocol):
    ...


Ord = TypeVar('Ord', bound='Orderable')

@total_ordering
class Orderable(Comparable, Protocol):
    def __lt__(self: Ord, other: Ord) -> bool:
        ...

    def __le__(self: Ord, other: Ord) -> bool:
        return self < other or self == other


A = TypeVar('A', bound='Additive')

class Additive(Orderable, Protocol):
    def __add__(self: A, other: A) -> A:
        ...


class Weightable(Additive, Protocol):
    def is_inf(self) -> bool:
        ...
