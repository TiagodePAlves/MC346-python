"""
``street.py``
=============

Módulo para o peso de um trecho de rua
"""

from __future__ import annotations

from protocols import Weightable

from random import choice
from functools import total_ordering
from typing import Optional, List, Any, Dict


#: Incluir velocidade máxima entre as possibilidades
#: de velocidade assumida naquele trecho de rua
INCLUDE_MAX_SPEED = False


@total_ordering
class Street(Weightable):
    """
    Classe de peso do trecho da rua

    Assim que a propriedade :attr:`~street.Street.speed` é
    lida pela primeira vez, ela assume um valor que é mantido
    com ela durante a vida do objeto.

    No entanto, quuando essa instância é copiada com ``deepcopy``,
    essa propriedade é desconfigurada e ela pode assumir um novo
    valor.

    Parameters
    ----------
    distance
        distância do trecho
    max_speed
        velocidade máxima do trecho
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
