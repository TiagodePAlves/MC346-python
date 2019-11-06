from __future__ import annotations

from protocols import Orderable
from heapq import heapify, heappop, heappush
from typing import TypeVar, List, Iterator, Generic


Ord = TypeVar('Ord', bound=Orderable)


class MinHeap(Generic[Ord]):
    def __init__(self, *items: Ord):
        self.__list: List[Ord] = list(items)
        heapify(self.__list)

    def push(self, *items: Ord) -> None:
        for item in items:
            heappush(self.__list, item)

    def pop(self) -> Ord:
        return heappop(self.__list)

    def peek(self) -> Ord:
        return self.__list[0]

    def __len__(self) -> int:
        return len(self.__list)

    def __iter__(self) -> Iterator[Ord]:
        self.__list.sort()
        return iter(self.__list)

    def __contains__(self, item: Ord) -> bool:
        return item in self.__list

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = ', '.join(map(repr, self))
        return f"{class_name}([{items}])"
