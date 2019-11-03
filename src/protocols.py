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
    def __eq__(self: C, other: C) -> bool: ...


O = TypeVar('O', bound='Orderable')

@total_ordering
class Orderable(Comparable, Protocol):
    def __lt__(self: O, other: O) -> bool: ...

    def __le__(self: O, other: O) -> bool:
        return self < other or self == other


class Keyable(Orderable, Hashable, Protocol): ...


A = TypeVar('A', bound='Additive')

class Additive(Orderable, Protocol):
    @classmethod
    def __zero__(cls) -> A: ...

    def __add__(self: A, other: A) -> A: ...

    def __sub__(self: A, other: A) -> A: ...
