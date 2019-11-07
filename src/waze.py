"""
``waze.py``
===========
"""

from __future__ import annotations

from graph import Graph
from street import Street
from typing import Optional


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
