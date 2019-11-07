"""
``graph.py``
============

Definição de um grafo e seus nós
"""

from __future__ import annotations

from protocols import Keyable, Weightable

from dataclasses import dataclass
from typing import (
    TypeVar, Iterator, Optional,
    Mapping, Dict, Any, Tuple,
    TYPE_CHECKING, Generic
)

# tipos de chave e peso de aresta
K = TypeVar('K', bound=Keyable)
W = TypeVar('W', bound=Weightable)

if not TYPE_CHECKING:
    # pré definição para as dicas de tipo
    class Node(Generic[K, W]): ...


@dataclass(frozen=True, order=True)
class Node(Dict[Node[K, W], W]):
    """A classe de um nó de um grafo, como um mapeamento
    onde as chaves são os nós adjacentes e os valores
    são os pesos das arestas
    """

    key: K
    """chave do nó no grafo"""

    def edges(self) -> Iterator[Tuple[W, Node[K, W]]]:
        """Arestas saindo do nó

        :return:    iterador com o peso e o nó alvo de
                    cada aresta
        """
        for neighbor, weight in self.items():
            yield weight, neighbor

    def __hash__(self) -> int:  # type: ignore
        return hash(self.key)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.key)})'


class Graph(Mapping[K, Node[K, W]]):
    """A classe do grafo, como um mapeamento
    de chave para nós
    """

    def __init__(self) -> None:
        self.__nodes: Dict[K, Node[K, W]] = {}

    def __make_node(self, key: K) -> Node[K, W]:
        """Cria o nó se não existe e retorna ele"""
        node = self.__nodes.get(key)
        if node is not None:
            return node

        node = Node(key)
        self.__nodes[key] = node
        return node

    def make_edge(self, from_: K, to: K, weight: W) -> None:
        """Cria uma aresta entre dois nós

        :param from\_: nó de origem da aresta
        :param to:  nó alvo da aresta
        :param weight: peso da aresta
        """
        from_node = self.__make_node(from_)
        to_node = self.__make_node(to)

        from_node[to_node] = weight

    def get_weight(self, from_: K, to: K) -> Optional[W]:
        """Recupera o peso da aresta de um nó para o outro,
        se ela existir

        :param from\_: nó de origem da aresta
        :param to:  nó alvo da aresta
        :return: peso da aresta ou :obj:`None`
        """
        return self[from_].get(self[to])

    # abaixo são algums métodos de um Mapping
    def __len__(self) -> int:
        return len(self.__nodes)

    def __iter__(self) -> Iterator[K]:
        return iter(self.__nodes)

    def __getitem__(self, key: K) -> Node[K, W]:
        return self.__nodes[key]

    def __contains__(self, key: object) -> bool:
        return key in self.__nodes

    def __repr__(self) -> str:
        name = type(self).__name__
        items = '{' + ', '.join(map(repr, self.__nodes.keys())) + '}'
        return f'{name}({items})'
