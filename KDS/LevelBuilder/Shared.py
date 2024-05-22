from enum import IntEnum as _IntEnum


class UnitType(_IntEnum):
    Tile = 0
    Item = 1
    Enemy = 2
    Teleport = 3
    Entity = 4
    Unspecified = 9
