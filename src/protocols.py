"""
``protocols.py``
================

Protocolos de funcionamento das classes para
a checagem estática de tipo com o `mypy <https://mypy.readthedocs.io/>`_
"""

from __future__ import annotations

from typing import TypeVar, Hashable, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Protocol, Literal
else:
    class Protocol: ...
    class Literal: ...

__all__ = [
    "Comparable", "Orderable",
    "Keyable", "Additive",
    "Weightable", "Literal"
]



# tipo que é comparável com seu próprio tipo
C = TypeVar('C', bound='Comparable')

class Comparable(Protocol):
    """Protocolo de classes que cujas instâncias são comparáveis"""

    def __eq__(self: C, other: C) -> bool:
        """operadores ``==`` e ``!=``"""
        ...


class Keyable(Comparable, Hashable, Protocol):
    """Classes que podem ser chaves, isto é, são comparáveis e podem
    ser geradas `hashs` a partir de suas instâncias
    """
    ...


# tipo que é ordenável em relação ao seu próprio tipo
Ord = TypeVar('Ord', bound='Orderable')

class Orderable(Comparable, Protocol):
    """Protocolo para tipos ordenáveis por ordenação total"""

    def __lt__(self: Ord, other: Ord) -> bool:
        """operador ``<``"""
        ...

    def __le__(self: Ord, other: Ord) -> bool:
        """operador ``<=``"""
        ...

    def __gt__(self: Ord, other: Ord) -> bool:
        """operador ``>``"""
        ...

    def __ge__(self: Ord, other: Ord) -> bool:
        """operador ``>=``"""
        ...


# tipo que tem adição com outros de seu tipo
A = TypeVar('A', bound='Additive')

class Additive(Orderable, Protocol):
    """Tipos com adição definida, além de serem ordenáveis"""

    def __add__(self: A, other: A) -> A:
        """operadores ``+`` e ``+=``"""
        ...


class Weightable(Additive, Protocol):
    """Tipos usados como pesos de arestas, sendo ordenáveis
    e têm adição definida
    """

    def is_inf(self) -> bool:
        """Teste se o peso representa uma aresta não acessível,
        como ``float('inf')``"""
        ...
