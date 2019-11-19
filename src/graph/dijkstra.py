"""
``dijkstra.py``
===============

Implementação do algorítmo de Dijkstra
para encontrar um caminho ótimo
"""

from __future__ import annotations

from . import Graph, Node
from protocols import Keyable, Weightable
from heap import MinHeap

from typing import (
    TypeVar, Optional, Dict, Set,
    Mapping, Tuple, List
)

__all__ = ["dijkstra"]


# tipos genéricos de chave e pesos
K = TypeVar('K', bound=Keyable)
W = TypeVar('W', bound=Weightable)

# tipos genéricos agregados, para facilitar
# as anotações de tipo
PathHeap = MinHeap[Tuple[W, Node[K, W]]]
ParentDict = Dict[Node[K, W], Node[K, W]]
WeightPath = Tuple[W, Tuple[Node[K, W], ...]]


def dijkstra(graph: Graph[K, W], source: K, destination: K) -> Optional[WeightPath[W, K]]:
    """Encontra o caminho ótimo entre dois nós

    :param graph: o grafo
    :param source: nó inicial do caminho
    :param destination: nó final
    :return: o melhor caminho entre os nós e o peso total
            do caminho ou :obj:`None`, se não for possível
            encontrar um caminho
    """

    source_node = graph[source]

    # o heap com o nó e peso total até lá
    paths = PathHeap[W, K]()
    # conjunto de nós visitados
    visited: Set[Node[K, W]] = set()
    # mapeamento de nós-pais no caminho
    parent: ParentDict[K, W] = {}
    # peso total até o nó
    weights: Dict[Node[K, W], W] = {}

    def push(weight: W, node: Node[K, W], parent_node: Node[K, W]) -> None:
        """função auxiliar que adiciona o nó no heap se ele tem uma chance
        de aparecer no melhor caminho
        """
        if not weight.is_inf() and (node not in weights or weight < weights[node]):
            weights[node] = weight
            parent[node] = parent_node
            paths.push((weight, node))

    # adiciona todos os vizinhos do nó inicial
    for weight, node in source_node.edges():
        push(weight, node, source_node)
    visited.add(source_node)

    # vai puxando até acabar o heap
    while paths:
        weight, node = paths.pop()

        # pula se o nó já foi visitado
        if node in visited:
            continue
        # se for o nó destino, não precisa procurar mais
        # já é o melhor caminho até lá
        elif node.key == destination:
            return weight, hiearachy_path(parent, node)

        # senão, tenta adicionar a vizinhaça do nó
        for edge_weight, neighbor in node.edges():
            if neighbor not in visited:
                push(weight + edge_weight, neighbor, node)
        # e marca como visitado
        visited.add(node)

    # se o heap acabar, é que não tem caminho
    # até o nó ou não existe esse nó
    return None


def hiearachy_path(mapping: Mapping[K, K], start: K) -> Tuple[K, ...]:
    """monta o caminho por mapeamento hieráquico a partir de uma chave"""

    path: List[K] = []
    key: Optional[K] = start

    while key is not None:
        path.append(key)
        key = mapping.get(key)

    # e inverte o caminho para começar da raiz
    return tuple(reversed(path))
