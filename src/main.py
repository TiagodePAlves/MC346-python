"""
``main.py``
===========

Solução para o problema
"""

from __future__ import annotations

from graph import dijkstra
from waze import Waze
from mean import Mean

import sys
from heapq import nsmallest
from utils import uncurry, run_many
from operator import attrgetter
from copy import deepcopy
from typing import (
    Tuple, Union, Optional, Iterable,
    TextIO, DefaultDict
)



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
    """função principal que resolve o grafo vária vezes"""

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
    # provalvelmente é um problema no grafo
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
