from dataclasses import dataclass
from typing import Final, NamedTuple, Self

import pygame
import KDS.Colors

@dataclass(frozen=True, init=False, eq=False, unsafe_hash=False)
class Euro:
    __slots__ = "_value"
    _value: int

    def __init__(self, *, _value: int) -> None:
        if _value < 0:
            raise ValueError("Value cannot be negative!")

        object.__setattr__(self, "_value", _value)

    @classmethod
    def from_parts(cls, euros: int = 0, cents: int = 0) -> Self:
        if euros < 0 or cents < 0:
            raise ValueError("Value cannot be negative.")
        return cls(_value=(euros * 100) + cents)

    @classmethod
    def from_float(cls, value: int | float):
        """
        float is rounded to the nearest cent.
        int might be a bit more accurate due to floating point rounding errors.
        """
        return cls(_value=round(value * 100))
    @property
    def euros(self) -> int:
        e: int = self._value // 100
        assert(isinstance(e, int)) # sometimes // gives a float?
        return e

    @property
    def cents(self) -> int:
        return self._value % 100

    def split_units(self):
        """
        Returns the money split into base units.
        Tuple second value is non-zero when some money wasn't accounted during splitting.
        """

        # iterate from largest to smallest
        val: int = self._value
        out: list[Euro] = []
        for unit in reversed(_units):
            while val >= unit._value:
                out.append(unit)
                val -= unit._value

        return (out, val)

    def __round__(self):
        _lastUnit: int = self._value % 10
        _base: int = self._value - _lastUnit

        if _lastUnit <= 2: # 1.00, 1.01, 1.02 => 1.00
            return Euro(_value=_base)
        elif _lastUnit <= 7: # 1.03, 1.04, 1.05, 1.06, 1.07 => 1.05
            return Euro(_value=(_base + 5))
        else: # 1.08, 1.09 => 1.10
            assert _lastUnit < 10
            return Euro(_value=(_base + 10))

    def __str__(self) -> str:
        return f"{self.euros}.{self.cents:02d}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Euro) and self._value == value._value

    def __lt__(self, other: Self) -> bool:
        return self._value < other._value
    def __le__(self, other: Self) -> bool:
        return self._value <= other._value
    def __gt__(self, other: Self) -> bool:
        return self._value > other._value
    def __ge__(self, other: Self) -> bool:
        return self._value >= other._value

    def __add__(self, other: Self):
        return Euro(_value=(self._value + other._value))
    def __sub__(self, other: Self):
        val: int = self._value - other._value
        if val < 0:
            raise ValueError("Insufficient funds.")
        return Euro(_value=val)

    def __hash__(self) -> int:
        return hash(self._value)

# must be sorted from smallest to largest
_units: Final[tuple[Euro, ...]] = (
    Euro.from_parts(cents=5),
    Euro.from_parts(cents=10),
    Euro.from_parts(cents=20),
    Euro.from_parts(cents=50),
    Euro.from_parts(euros=1),
    Euro.from_parts(euros=2),
    Euro.from_parts(euros=5),
    Euro.from_parts(euros=10),
    Euro.from_parts(euros=20),
    Euro.from_parts(euros=50)
)
assert(tuple(sorted(_units)) == _units)

_textures: dict[Euro, pygame.Surface] = {}
def init():
    global _textures

    def get_texture_path(euro: Euro) -> str:
        filename: str = ""
        if euro.euros > 0:
            filename += f"{euro.euros}euro"
        if euro.cents > 0:
            filename += f"{euro.cents}cent"
        return f"Assets/Textures/Euro/{filename}.png"

    for euro in _units:
        surf: pygame.Surface = pygame.image.load(get_texture_path(euro)).convert()
        surf.set_colorkey(KDS.Colors.White)
        _textures[euro] = surf

def get_texture(unit: Euro) -> pygame.Surface:
    return _textures[unit]
