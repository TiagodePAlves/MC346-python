"""
``utils.py``
============

Utilidades para o código principal :mod:`__main__.py`
"""

from __future__ import annotations

from multiprocessing import Pool
from itertools import repeat
from functools import wraps
from typing import TypeVar, Callable, Tuple, Any, Iterator

__all__ = ["uncurry", "run_many"]


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
