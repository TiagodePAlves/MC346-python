"""
``heap.py``
===========

Implementação de um `heap` de mínimo
com a biblioteca :mod:`heapq` de Python
"""

from __future__ import annotations

from protocols import Orderable
from heapq import heapify, heappop, heappush
from typing import TypeVar, List, Iterator, Collection


# qualquer tipo que seja ordenável
Ord = TypeVar('Ord', bound=Orderable)


class MinHeap(Collection[Ord]):
    """
    Heap de mínimo com as funções clássicas :func:`~heap.MinHeap.peek`,
    :func:`~heap.MinHeap.push` e :func:`~heap.MinHeap.pop`.

    :param items:   valores iniciais do heap
    """
    __slots__ = ['_list']

    def __init__(self, *items: Ord):
        self._list: List[Ord] = list(items)
        heapify(self._list)

    def push(self, *items: Ord) -> None:
        """Insere valores no `heap`"""
        for item in items:
            heappush(self._list, item)

    def pop(self) -> Ord:
        """Remove e retorna o menor valor do `heap`"""
        return heappop(self._list)

    def peek(self) -> Ord:
        """Observa o menor valor no `heap` sem removê-lo"""
        return self._list[0]

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[Ord]:
        """Itera o elementos do heap em ordem crescente"""
        # ordenar a lista mantém a invariante do heap
        self._list.sort()
        return iter(self._list)

    def __contains__(self, item: object) -> bool:
        return item in self._list

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = ', '.join(map(repr, self))
        return f"{class_name}([{items}])"
