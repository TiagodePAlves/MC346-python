"""
``mean.py``
===========

Módulo com um tipo agregador da média de valores
"""

from __future__ import annotations

from typing import Union


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
        """Representação textual"""
        return f'{type(self).__name__}({self.average})'
