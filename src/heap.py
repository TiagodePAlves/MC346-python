from __future__ import annotations

from protocols import Orderable
from heapq import heapify, heappop, heappush
from typing import TypeVar, List, Iterator, Collection


Ord = TypeVar('Ord', bound=Orderable)


class MinHeap(Collection[Ord]):
    __slots__ = ['_list']

    def __init__(self, *items: Ord):
        self._list: List[Ord] = list(items)
        heapify(self._list)

    def push(self, *items: Ord) -> None:
        for item in items:
            heappush(self._list, item)

    def pop(self) -> Ord:
        return heappop(self._list)

    def peek(self) -> Ord:
        return self._list[0]

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[Ord]:
        while self:
            yield self.pop()

    def __contains__(self, item: object) -> bool:
        return item in self._list

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = ', '.join(map(repr, self))
        return f"{class_name}([{items}])"
