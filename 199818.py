"""MC346 - Paradigmas de Programação - Python

----------------------------------------
| João Victor Flores da Costa | 199818 |
| Tiago de Paula Alves        | 187679 |
----------------------------------------

A solução aplicada aqui foi uma classe de peso da aresta
que assume um valor diferente cada vez que é copiada.
Com isso, o grafo é copiado para vários subprocessos,
assumindo pesos diferentes, onde o algoritmo de Dijkstra
é aplicado para achar o melhor caminho. Por fim, o tempo
médio dos melhores caminhos são encontrados.

Pelo que entendemos, a velocidade máxima da rua não
era para ser incluida nas possibilidades de velocidade
atual. No entanto, se fosse assim, o exemplo do
enunciado não teria solução. De qualquer modo, assumimos
o primeiro caso, mas com uma flag, `INCLUDE_MAX_SPEED`,
de controle desse funcionamento.

Tentamos explorar o sistema de tipagem estática que está
sendo desenvolvido para Python. Por causa disso, o código
só funciona com Python 3.7, como foi dito na página da
disciplina. A checagem dos tipos pode ser feita com a
biblioteca `mypy` e o comando `mypy --strict 199818.py`.

Outro impacto da tipagem foi no tamanho e na verbosidade
do código, apesar de que aqui uma grande parte da culpa
foi na motivação de criar o código em módulos e classes
mais completas. Se quiser ver o código nesse formato
mais mpdularizado, é possível encontrar em
https://tiagodepalves.github.io/MC346-python/,
documentação gerada pelo autodoc do Spinx.

Grande parte do código pode ser trivialmente removido, com
partes até inutilizadas, especialmente se desconsiderar
as anotações de tipo. Só que o código aqui tenta explorar
exatamente esse novo sistema de tipos estáticos de Python,
mudando boa parte do que é considerado pythônico, como
https://github.com/python/mypy/issues/2420#issuecomment-259168418
em vez de https://docs.python.org/3/glossary.html#term-eafp.

O código abaixo claramente não foi feito com performance
como objetivo principal. Mesmo assim, no final tem um benchmark
de dois modos de solução implementados. Um executando os vários
cálculos de caminhos sequencialmente e outro em processos
separados (default). O modo paralelizado chegou a rodar algo
próximo de 3 vezes mais rápido com grafos pequenos, mas não
conseguimos explorar como ele se sairia para grafos maiores.
Entretanto, para grafos maiores, o número de repetições (pré-
-estabelecida como 100) provavelmente deveria ser aumentado
para continuar sendo estatisticamente significante.

Assumimos que não poderia ser utilizado nenhuma biblioteca
fora do padrão de Python, nem a versão 3.8 da linguagem.
Se fosse esperado que as bibliotecas de scipy e numpy fossem
aplicadas aqui, o código sairia bem diferente e, às vezes,
mais performáticos. De qualquer modo, não foi o caso aqui.
"""

from __future__ import annotations

import sys
from random import choice
from itertools import repeat
from multiprocessing import Pool
from functools import wraps, total_ordering
from heapq import heapify, heappop, heappush, nsmallest
from dataclasses import dataclass
from operator import attrgetter
from copy import deepcopy

from typing import (
    TypeVar, Iterator, Optional, Hashable, TextIO,
    Mapping, Dict, Tuple, Generic, Collection,
    List, Set, Any,  Callable, Union, DefaultDict,
    Iterable, TYPE_CHECKING
)

#: Incluir velocidade máxima entre as possibilidades
#: de velocidade assumida naquele trecho de rua
INCLUDE_MAX_SPEED = False


#######################################################################################

if TYPE_CHECKING:
    from typing_extensions import Protocol, Literal
else:
    class Protocol: ...
    class Literal: ...


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


#######################################################################################

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


#######################################################################################


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


#######################################################################################

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
                push(edge_weight, neighbor, node)
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


#######################################################################################


@total_ordering
class Street(Weightable):
    """
    Classe de peso (:class:`Weightable`) do trecho da rua

    Assim que a propriedade :attr:`~street.Street.speed` é
    lida pela primeira vez, ela assume um valor que é mantido
    com ela durante a vida do objeto.

    No entanto, quuando essa instância é copiada com :func:`copy.deepcopy`,
    essa propriedade é desconfigurada e ela pode assumir um novo
    valor.

    :param distance:    distância do trecho
    :param max_speed:   velocidade máxima do trecho
    """

    def __init__(self, distance: float, max_speed: float):
        self._distance = distance
        self._max_speed = max_speed
        self._latest_speeds: List[float] = []
        self._speed: Optional[float] = None

    def register_speeds(self, *speeds: float) -> None:
        """Registra as velocidades atuais no trecho"""
        self._latest_speeds += list(speeds)

    @property
    def speed(self) -> float:
        """Velocidade assumida no trecho"""
        if self._speed is None:
            if INCLUDE_MAX_SPEED:
                self._speed = choice(self._latest_speeds + [self._max_speed])
            elif self._latest_speeds:
                self._speed = choice(self._latest_speeds)
            else:
                self._speed = self._max_speed

        return self._speed

    @property
    def distance(self) -> float:
        """distância do trecho"""
        return self._distance

    @property
    def time(self) -> float:
        """tempo no trecho, com a velocidade assumida

        Usado para a comparação entre trechos
        """
        if self.speed:
            return self.distance / self.speed
        else:
            return float('inf')

    def is_inf(self) -> bool:
        """Se a velocidade assumida representa um tempo infinito"""
        return not self.speed

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Street) and self.time == other.time

    def __lt__(self, other: Any) -> bool:
        return isinstance(other, Street) and self.time < other.time

    def __add__(self, other: Street) -> Street:
        """A soma dos trechos equivale a soma dos tempos"""
        d1, d2 = self.distance, other.distance
        s1, s2 = self.speed, other.speed

        distance = d1 + d2
        if not s1 or not s2:
            speed = 0.0
        else:
            speed = (distance * s1 * s2) / (d1 * s2 + d2 * s1)
        return Street(distance, speed)

    def __repr__(self) -> str:
        return repr(self.time)

    def __deepcopy__(self, memo: Dict[int, Any]) -> Street:
        """Cópia especial que não mantém a velocidade assumida"""
        new = Street(self.distance, self._max_speed)
        new.register_speeds(*self._latest_speeds)

        memo[id(self)] = new
        return new


#######################################################################################


class Waze(Graph[str, Street]):
    """
    Grafo específico para o problema

    :param max_speed:   velocidade máxima no grafo
    """

    def __init__(self, max_speed: float):
        self._max_speed = max_speed
        super().__init__()

    def new_street(self,
                   from_: str, to: str,
                   distance: float,
                   max_speed: Optional[float] = None
                   ) -> None:
        """Cria um novo trecho de rua (:class:`Street`) de um nó
        para outro

        :param from\_: nó inicial
        :param to: nó objetivo
        :param distance: distância do trecho
        :param max_speed: velocidade máxima do trecho,
            se for diferente da velocidade máxima geral
        """
        speed = max_speed or self._max_speed
        self.make_edge(from_, to, Street(distance, speed))

    def latest_speeds(self, from_: str, to: str, *speeds: float) -> None:
        """Marca as velocidades atuais registradas recentementes
        em um trecho

        :param from\_: nó inicial
        :param to: nó objetivo
        :param speeds: velocidades atuais
        """
        weight = self.get_weight(from_, to)
        if not weight:
            raise KeyError((from_, to))

        weight.register_speeds(*speeds)


#######################################################################################

# tipos genéricos
T = TypeVar('T')
U = TypeVar('U')


def uncurry(func: Callable[..., T]) -> Callable[[Tuple[Any, ...]], T]:
    """Decorador que transforma a função para receber uma
    tupla em vez de argumentos posicionais

    :rtype: :obj:`typing.Callable`
    """

    @wraps(func)
    def wrapped(args: Tuple[Any, ...]) -> T:
        return func(*args)
    return wrapped


def run_many(func: Callable[[T], U], arg: T, runs: int, *,
             PARALLEL: bool = True,
             POOLSIZE: int = 8, CHUNKSIZE: int = 10
             ) -> Iterator[U]:
    """
    `Generator` que repete uma função com o mesmo argumento
    ``runs`` vezes

    :param func:   função a ser executada
    :param arg:             argumento da função
    :param runs:        número de execuções
    :param PARALLEL:   se a execução deve ser feita
                            em paralelo
    :param POOLSIZE:    quantidade de processos executando
                            a função ao mesmo tempo
    :param CHUNKSIZE:   quantidade de vezes que cada
                            processo executa a função
    :return:    iterador dos resultados
    """

    if not PARALLEL:
        for value in map(func, repeat(arg, runs)):
            yield value

    with Pool(POOLSIZE) as p:
        results = p.imap_unordered(func, repeat(arg, runs), CHUNKSIZE)
        for value in results:
            yield value


#######################################################################################


class Mean:
    """
    Classe que agrega valores em uma médida de média

    Quando adicionada com um :class:`float`, agrega ele
    na medida. Quando adicionada a outro :class:`Mean`,
    a nova média é tratada como a média da junção dos
    valores que compõe as duas médias.

    :param nums:    valores iniciais na medida
    """

    def __init__(self, *nums: float):
        self._count = len(nums)
        self._sum = sum(nums)

    @property
    def average(self) -> float:
        """A média propriamente"""
        if not self._count:
            raise ValueError("no number aggregated")
        return self._sum / self._count

    def insert(self, *nums: float) -> None:
        """Insere novos valores na média

        :param nums:
        """
        self._sum += sum(nums)
        self._count += len(nums)

    def __iadd__(self, num: Union[float, Mean]) -> Mean:
        """Expansão da média com um :class:`float` ou um
        :class:`Mean`

        :param num:
        """
        if isinstance(num, float):
            self.insert(num)
        else:
            self._sum += num._sum
            self._count += num._count

        return self

    def __add__(self, num: Union[float, Mean]) -> Mean:
        """Nova média expandida com um :class:`float` ou um
        :class:`Mean`

        :param num:
        """
        if isinstance(num, float):
            new = Mean(num)
        else:
            new = Mean(num._sum)
            new._count = num._count
        new += self
        return new

    def __radd__(self, num: float) -> Mean:
        """Ordem invertida da expansão para um número"""
        return self + Mean(num)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.average})'


#######################################################################################


def read_waze(*, file: TextIO = sys.stdin) -> Waze:
    """leitura do mapa do Waze"""
    max_speed = float(file.readline().strip())
    waze = Waze(max_speed)

    try:
        while True:
            from_, to, *vals = file.readline().split()
            waze.new_street(from_, to, *map(float, vals))
    # quando a linha em branco aparecer, vai dar erro
    # no _unpacking_
    except ValueError:
        pass

    return waze


def read_latest_speeds(waze: Waze, *,
                       file: TextIO = sys.stdin
                       ) -> Tuple[str, str]:
    """leitura das velocidades recentes e dos extremos do caminho"""
    try:
        while True:
            # a linha tem que se guardada em uma linha
            # para quando der erro
            line = file.readline().strip()
            from_, to, *vals = line.split()

            waze.latest_speeds(from_, to, *map(float, vals))
    # erro quando a linha tiver um só elemento
    except ValueError:
        source = line
        destination = file.readline().strip()

    return source, destination


# tipos agregados
Path = Tuple[str, ...]
Result = Optional[Tuple[Path, float]]


@uncurry
def run(waze: Waze, source: str, dest: str) -> Result:
    """função de resolução do grafo Waze e tratamento do resultado"""

    # deepcopy pra esquecer as velocidades assumidas
    graph = deepcopy(waze)

    path = dijkstra(graph, source, dest)
    if not path:
        # caminho não encontrado
        return None

    # montagem do resultado
    keys = map(attrgetter('key'), path[1])
    return tuple(keys), path[0].time


def aggregate(items: Iterable[Result]) -> Tuple[DefaultDict[Path, Mean], int]:
    """função de agregação dos resultados"""

    # média dos resultados
    results = DefaultDict[Path, Mean](Mean)
    # grafos sem solução
    errors = 0

    for result in items:
        if not result:
            errors += 1
        else:
            path, time = result
            results[path] += time

    return results, errors


def main(RUNS: int = 100, PARALLEL: bool = True, *,
         infile: Union[TextIO, str] = sys.stdin,
         outfile: TextIO = sys.stdout
         ) -> None:
    """função principal que resolve o grafo várias vezes"""

    # abre o arquivo de leitura, se necessário
    if isinstance(infile, str):
        file = open(infile, 'r')
    else:
        file = infile
    # lê o grafo
    waze_graph = read_waze(file=file)
    source, dest = read_latest_speeds(waze_graph, file=file)
    # e fecha o arquivo
    if isinstance(infile, str):
        file.close()

    # prepara o generator com a execução
    items = run_many(run, (waze_graph, source, dest),
                     runs=RUNS, PARALLEL=PARALLEL)
    # analisa os resultados
    results, errors = aggregate(items)
    # se não teve nenhum resultado válido
    # provavelmente é um problema no grafo
    if errors == RUNS:
        raise ValueError(f"no path between {source} and {dest}")

    # retira e mostra os melhores resultados
    best = nsmallest(2, results.items(), key=lambda x: x[1].average)
    for path, time in best:
        print(f'{time.average * 60.0:.1f}', file=outfile)
        print(*path, file=outfile)


# preparação e código para benchmark
SETUP = """
from __main__ import main
import os

devnull = open(os.devnull, 'w')
"""

CODE = "main(file_or_name='{file}', out=devnull, PARALLEL={arg})"


def time(RUNS: int = 100, *, input_file: str) -> None:
    """benchmark dos modos paralelo e sequencial, para comparação"""
    from timeit import timeit

    for arg in (True, False):
        code = CODE.format(file=input_file, arg=arg)
        timing = timeit(code, setup=SETUP, number=RUNS)
        print(f'PARALLEL={arg}', f'TIMING={timing}')


#######################################################################################

# seletor de modo de execução
TIMING = False

if __name__ == "__main__":
    if TIMING:
        # dependendo do grafo
        time(input_file='test.txt')
    else:
        main()
