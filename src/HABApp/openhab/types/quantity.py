from __future__ import annotations

from typing_extensions import Self


class QuantityInt(int):
    """Int which additionally carries a unit"""

    unit: str   # unit as sent from openHAB

    def __new__(cls, v: int, unit: str) -> Self:
        _obj = super().__new__(cls, v)
        _obj.unit = unit
        return _obj

    def _value_str(self) -> str:
        if unit := self.unit:
            return f'{super().__repr__()} {unit}'
        return super().__repr__()


class QuantityFloat(float):
    """Float which additionally carries a unit"""

    unit: str   # unit as sent from openHAB

    def __new__(cls, v: float, unit: str) -> Self:
        _obj = super().__new__(cls, v)
        _obj.unit = unit
        return _obj

    def _value_str(self) -> str:
        if unit := self.unit:
            return f'{super().__repr__()} {unit}'
        return super().__repr__()
