from dataclasses import dataclass
from typing import Final, Literal, NamedTuple, NoReturn, Self

import pygame
import KDS.Colors
import KDS.Money

@dataclass(frozen=True, init=False, eq=False, unsafe_hash=False)
class Euro:
    """Negative values can be represented, but some methods do not work with negative numbers."""

    __slots__ = "_value"
    _value: int

    def __init__(self, *, _value: int) -> None:
        object.__setattr__(self, "_value", _value)

    @classmethod
    def zero(cls) -> Self:
        return cls(_value=0)

    @classmethod
    def from_parts(cls, euros: int = 0, cents: int = 0) -> Self:
        """Both `euros` and `cents` must have the negative sign if the value is intended to be negative."""
        return cls(_value=(euros * 100) + cents)

    @classmethod
    def from_float(cls, value: int | float):
        """
        float is rounded to the nearest cent.
        int might be a bit more accurate due to floating point rounding errors.

        This method checks if the value is of the correct type as we use it in many unsafe places in KDS.
        """
        assert(isinstance(value, (int, float)))
        return cls(_value=round(value * 100))

    @staticmethod
    def _euros(val: int) -> int:
        assert(val >= 0)

        e: int = val // 100
        assert(isinstance(e, int)) # sometimes // gives a float?
        return e

    @property
    def euros(self) -> int:
        if self._value >= 0:
            return Euro._euros(self._value)
        else:
            return -1 * Euro._euros(-1 * self._value)

    @property
    def cents(self) -> int:
        mod: int = self._value % 100
        if self._value >= 0:
            return mod
        else: # if negative value, return negative sign
            assert(mod >= 0) # mod shouldn't be negative here as we convert the value to negative
            return mod - 100

    def split_units(self):
        """
        Returns the money split into base units.

        Tuple second value is non-zero when some money wasn't accounted during splitting.
        Negative values are always not accounted during splitting.
        """

        # iterate from largest to smallest
        val: int = self._value
        out: list[Euro] = []
        for unit in reversed(_units):
            while val >= unit._value:
                out.append(unit)
                val -= unit._value

        return (out, val)

    @property
    def is_base_unit(self) -> bool:
        return self in _units

    def __round__(self):
        # this should work with negative values
        # at least it seemed to work last time I tested it in the terminal...

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
        sign: str = '-' if self._value < 0 else ''
        absval: Euro = abs(self)
        return f"{sign}{absval.euros}.{absval.cents:02d}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Euro) and self._value == value._value
    @property
    def is_zero(self) -> bool:
        """I didn't want to make the __eq__ accept any other types other than Euro, so here is a fast way to check for zero instead."""
        return self._value == 0

    def __lt__(self, other: Self | Literal[0]) -> bool:
        if other == 0:
            return self._value < 0
        else:
            return self._value < other._value

    def __le__(self, other: Self | Literal[0]) -> bool:
        if other == 0:
            return self._value <= 0
        else:
            return self._value <= other._value

    def __gt__(self, other: Self | Literal[0]) -> bool:
        if other == 0:
            return self._value > 0
        else:
            return self._value > other._value

    def __ge__(self, other: Self | Literal[0]) -> bool:
        if other == 0:
            return self._value >= 0
        else:
            return self._value >= other._value

    def __add__(self, other: Self):
        return Euro(_value=(self._value + other._value))
    def __sub__(self, other: Self):
        return Euro(_value=(self._value - other._value))

    def __abs__(self):
        return Euro(_value=abs(self._value))
    def __neg__(self):
        return Euro(_value=-self._value)

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
