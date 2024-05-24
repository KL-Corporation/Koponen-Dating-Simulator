from enum import StrEnum
import os
from tkinter import filedialog
from typing import Callable, Final, NamedTuple

import pygame

import KDS.Logging
import KDS.System

from KDS.LevelBuilder.Shared import UnitType

class ConvertCategory(StrEnum):
    building = "building"
    decoration = "decoration"
    enemies = "enemies"
    items = "items"

class TranslatedSerial(NamedTuple):
    category: ConvertCategory | None
    """Convert category in resources_convert_rules.txt"""

    name: str
    """Tile's approximate name, will more likely match legacy KDS than the latest KDS version"""

    character: str
    """Serial character in legacy KDS"""

    color: tuple[int, int, int] | None
    """Serial color in legacy KDS"""

    serial: str | None
    """Serial in the latest KDS version. None when not convertable."""

    @property
    def non_null_serial(self) -> str:
        if self.serial is None:
            raise ValueError("serial is null.")
        return self.serial

SLOTCOUNT: Final[int] = 4

AIR: Final[TranslatedSerial] = TranslatedSerial(None, "air", "a", None, "0000")

# This data is fetched through the Legacy-Archive branch's file KoponenDatingSimulator/Assets/Maps/resources_convert_rules.txt
# https://github.com/KL-Corporation/Koponen-Dating-Simulator/blob/e77cac080e63f6c2683cdc61ec9bc2495d1c36a1/KoponenDatingSimulator/Assets/Maps/resources_convert_rules.txt

class TranslateTable:
    def __init__(self, *serials: TranslatedSerial) -> None:
        self._serials: tuple[TranslatedSerial, ...] = serials

        self._color_serials: dict[tuple[int, int, int], TranslatedSerial] = {}
        for s in self._serials:
            if s.color in self._color_serials:
                raise ValueError(f"There are too many definitions serial definitions for the color '{s.color}'")

    def get_from_color(self, category: ConvertCategory, color: tuple[int, int, int]) -> tuple[TranslatedSerial, ...]:
        """Performs a linear search, might be optimised in the future."""
        return tuple(filter(lambda s: s.category == category and s.color == color, self._serials))

    def get_from_character(self, character: str) -> tuple[TranslatedSerial, ...]:
        """Performs a linear search, might be optimised in the future."""
        return tuple(filter(lambda s: s.character == character, self._serials))

TRANSLATE_TABLE: Final[TranslateTable] = TranslateTable(
    AIR,

    # BUILDING
    TranslatedSerial(ConvertCategory.building, "floor0", "b", (0, 255, 0), "0002"),
    TranslatedSerial(ConvertCategory.building, "wall0", "c", (255, 0, 0), "0003"),
    TranslatedSerial(ConvertCategory.building, "table0", "d", (128, 0, 0), "0014"),
    TranslatedSerial(ConvertCategory.building, "toilet0", "e", (245, 245, 245),"0015" ),
    TranslatedSerial(ConvertCategory.building, "lamp0", "f", (255, 255, 0), "0022"),
    TranslatedSerial(ConvertCategory.building, "trashcan", "g", (64, 64, 64), "0016"),
    TranslatedSerial(ConvertCategory.building, "ground1", "h", (150, 75, 0), "0028"),
    TranslatedSerial(ConvertCategory.building, "grass", "i", (0, 128, 0), "0008"),
    TranslatedSerial(ConvertCategory.building, "concrete0", "j", (192, 192, 192), "0020"),
    TranslatedSerial(ConvertCategory.building, "door", "k", (128, 128, 128), "0023"),
    TranslatedSerial(ConvertCategory.building, "red_door", "l", (255, 128, 128), "0024"),
    TranslatedSerial(ConvertCategory.building, "green_door", "m", (128, 255, 128), "0026"),
    TranslatedSerial(ConvertCategory.building, "blue_door", "n", (128, 128, 255), "0025"),
    TranslatedSerial(ConvertCategory.building, "bricks", "o", (255, 128, 0), "0007"),
    TranslatedSerial(ConvertCategory.building, "planks", "p", (255, 64, 0), "0004"),
    TranslatedSerial(ConvertCategory.building, "ladder", "q", (255, 192, 0), "0018"),
    TranslatedSerial(ConvertCategory.building, "light_bricks", "r", (213, 0, 231), "0006"),
    TranslatedSerial(ConvertCategory.building, "iron_bar", "s", (23, 41, 22), "0010"),
    TranslatedSerial(ConvertCategory.building, "mossy_bricks", "u", (120, 120, 0), "0005"),
    TranslatedSerial(ConvertCategory.building, "soil", "t", (120, 120, 1), "0011"),
    TranslatedSerial(ConvertCategory.building, "stone", "v", (120, 120, 2), "0013"),
    TranslatedSerial(ConvertCategory.building, "hay", "w", (120, 120, 3), "0009"),
    TranslatedSerial(ConvertCategory.building, "soil1", "å", (120, 120, 4), "0012"),
    TranslatedSerial(ConvertCategory.building, "wood", "ä", (120, 120, 5), "0027"),

    # DECORATION
    TranslatedSerial(ConvertCategory.decoration, "tree", "A", (0, 255, 0), "0017"),
    TranslatedSerial(ConvertCategory.decoration, "jukebox", "B", (255, 0, 0), "0019"),

    # ENEMIES
    TranslatedSerial(ConvertCategory.enemies, "zombie", "Z", (0, 255, 0), "2011"),
    TranslatedSerial(ConvertCategory.enemies, "sergeant", "S", (255, 0, 0), "2002"),
    TranslatedSerial(ConvertCategory.enemies, "archvile", "V", (0, 0, 255), None),
    TranslatedSerial(ConvertCategory.enemies, "bulldog", "K", (255, 255, 0), "2010"),

    # there are two definitions for Imp?
    TranslatedSerial(ConvertCategory.enemies, "imp", "I" ,(0,0,90), "2001"),
    TranslatedSerial(ConvertCategory.enemies, "imp", "I", (0, 0, 142), "2001"),

    # on old KDS versions this was an "enemy"
    TranslatedSerial(ConvertCategory.enemies, "landmine", "C", (0, 255, 255), "0021"),

    # ITEMS
    TranslatedSerial(ConvertCategory.items, "gasburner", "0", (0, 0, 255), "1004"),
    TranslatedSerial(ConvertCategory.items, "knife", "1", (64, 64, 64), "1007"),
    TranslatedSerial(ConvertCategory.items, "red_key", "2", (255, 128, 128), "1013"),
    TranslatedSerial(ConvertCategory.items, "green_key", "3", (128, 255, 128), "1005"),
    TranslatedSerial(ConvertCategory.items, "blue_key", "4", (128, 128, 255), "1001"),
    TranslatedSerial(ConvertCategory.items, "coffeemug", "5", (192, 192, 192), "1003"),
    TranslatedSerial(ConvertCategory.items, "ss_bonuscard", "6", (255, 128, 0), "1019"),
    TranslatedSerial(ConvertCategory.items, "lappi_sytytyspalat", "7", (255, 255, 0), "1008"),
    TranslatedSerial(ConvertCategory.items, "plasmarifle", "8", (0, 128, 255), "1012"),
    TranslatedSerial(ConvertCategory.items, "cell", "9", (64, 128, 255), "1002"),
    TranslatedSerial(ConvertCategory.items, "pistol", "!", (64, 255, 128), "1010"),
    TranslatedSerial(ConvertCategory.items, "pistol_mag", "#", (192, 255, 128), "1011"),
    TranslatedSerial(ConvertCategory.items, "rk62", "%", (192, 0, 255), "1015"),
    TranslatedSerial(ConvertCategory.items, "rk62_mag", "&", (192, 64, 255), "1014"),
    TranslatedSerial(ConvertCategory.items, "medkit", "(", (255, 0, 0), "1009"),
    TranslatedSerial(ConvertCategory.items, "shotgun", ")", (128, 64, 0), "1016"),
    TranslatedSerial(ConvertCategory.items, "shotgun_shells", "=", (128, 128, 0), "1017"),
    TranslatedSerial(ConvertCategory.items, "soulsphere", "+", (128, 128, 1), "1018"),
    TranslatedSerial(ConvertCategory.items, "turboneedle", "'", (128, 128, 2), "1020"),
)

def upgradeGameMap(msgs: Callable[[str], None]):
    """tkinter required"""

    gamemap_file: str = filedialog.askopenfilename(
        filetypes=[("Game Map", "game_map.kds")],
        title="Select Game Map"
    )
    if len(gamemap_file) < 1:
        return

    itemmap_file: str = filedialog.askopenfilename(
        initialdir=os.path.dirname(gamemap_file),
        filetypes=[("Item Map", "item_map.kds")],
        title="Select Item Map"
    )
    if len(itemmap_file) < 1:
        return

    gamemap: list[str]
    with open(gamemap_file, "r", encoding="utf-8") as f:
        gamemap = f.read().splitlines()
    gamemap_size_y: int = len(gamemap)
    gamemap_size_x: int = len(gamemap[0]) if gamemap_size_y > 0 else 0

    itemmap: list[str]
    with open(itemmap_file, "r", encoding="utf-8") as f:
        itemmap = f.read().splitlines()
    itemmap_size_y: int = len(itemmap)
    itemmap_size_x: int = len(itemmap[0]) if itemmap_size_y > 0 else 0

    size_y: int = max(gamemap_size_y, itemmap_size_y)
    size_x: int = max(gamemap_size_x, itemmap_size_x)

    grid: list[list[list[TranslatedSerial]]] = [[[] for _ in range(size_x)] for _ in range(size_y)]
    for y, row in enumerate(grid):
        msgs(f"{((y + 1) / len(grid)) * 100:.2f} %")

        gamemap_row: str | None = gamemap[y] if y < gamemap_size_y else None
        itemmap_row: str | None = itemmap[y] if y < itemmap_size_y else None
        for x, tile in enumerate(row):
                if gamemap_row is not None and x < len(gamemap_row):
                    g: str = gamemap_row[x]
                    g_trans = TRANSLATE_TABLE.get_from_character(g)
                    if len(g_trans) < 1:
                        if KDS.System.MessageBox.Show("Tile not supported.", f"Tile '{g}' was not found in the translation lookup table.", KDS.System.MessageBox.Buttons.OKCANCEL, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.CANCEL:
                            return
                    elif len(g_trans) > 1:
                        KDS.System.MessageBox.Show("FATAL! Multiple definitions.", f"There are too many definitions serial definitions for the character '{g}'", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
                        return
                    else:
                        tile.append(g_trans[0])
                if itemmap_row is not None and x < len(itemmap_row):
                    i: str = itemmap_row[x]
                    if i.startswith(str(UnitType.Item)): # Some item maps include tiles for whatever reason...
                        i_trans = TRANSLATE_TABLE.get_from_character(i)
                        if len(i_trans) < 1:
                            if KDS.System.MessageBox.Show("Item not supported.", f"Item '{i}' was not found in the translation lookup table.", KDS.System.MessageBox.Buttons.OKCANCEL, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.CANCEL:
                                return
                        elif len(i_trans) > 1:
                            KDS.System.MessageBox.Show("FATAL! Multiple definitions.", f"There are too many definitions serial definitions for the character '{i}'", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
                            return
                        else:
                            tile.append(i_trans[0])

    _verify_and_write_output(grid)

def upgradeMapFiles(msgs: Callable[[str], None]):
    grid: list[list[list[TranslatedSerial]]] = []
    if _upgradeMapFile(msgs, grid, ConvertCategory.building, "Map Buildings", ("Map Buildings", "map_buildings.map")) > 0:
        return
    if _upgradeMapFile(msgs, grid, ConvertCategory.decoration, "Map Decorations", ("Map Decorations", "map_decorations.map")) > 0:
        return
    if _upgradeMapFile(msgs, grid, ConvertCategory.enemies, "Map Enemies", ("Map Enemies", "map_enemies.map")) > 0:
        return
    if _upgradeMapFile(msgs, grid, ConvertCategory.items, "Map Items", ("Map Items", "map_items.map")) > 0:
        return

    _verify_and_write_output(grid)

def _upgradeMapFile(msgs: Callable[[str], None], grid: list[list[list[TranslatedSerial]]], category: ConvertCategory, title: str, filetype: tuple[str, str]) -> int:
    file: str = filedialog.askopenfilename(
        filetypes=(filetype,),
        title=f"Select {title}"
    )
    if len(file) < 1:
        return 1

    gamemap: pygame.Surface = pygame.image.load(file, namehint=".png")

    TOTAL: int = gamemap.get_width() * gamemap.get_height()
    current: int = 0

    for y in range(gamemap.get_height()):
        while y >= len(grid):
            grid.append([])
        row: list[list[TranslatedSerial]] = grid[y]

        for x in range(gamemap.get_width()):
            current += 1
            msgs(f"Converting {title}... ({(current / TOTAL) * 100:.2f} %)")

            col: pygame.Color = gamemap.get_at((x, y))
            if col.a <= 0:
                continue

            while x >= len(row):
                row.append([])
            unit: list[TranslatedSerial] = row[x]

            ts = TRANSLATE_TABLE.get_from_color(category, (col.r, col.g, col.b))
            if len(ts) < 1:
                if KDS.System.MessageBox.Show("Unit not supported.", f"Unit '({col.r}, {col.g}, {col.b})' was not found in the translation lookup table.", KDS.System.MessageBox.Buttons.OKCANCEL, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.CANCEL:
                    return 1
            elif len(ts) > 1:
                KDS.System.MessageBox.Show("FATAL! Multiple definitions.", f"There are too many definitions serial definitions for the color '({col.r}, {col.g}, {col.b})'", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
                return 1
            else:
                unit.append(ts[0])

    return 0


def _verify_and_write_output(grid: list[list[list[TranslatedSerial]]]):
    for row in grid:
        for tile in row:
            for uindex in range(len(tile)):
                if tile[uindex].serial is None:
                    response = KDS.System.MessageBox.Show("Tile not supported.", f"Tile '{tile[uindex].name}' does not have a serial representation.", KDS.System.MessageBox.Buttons.OKCANCEL, KDS.System.MessageBox.Icon.WARNING)
                    if response == KDS.System.MessageBox.Responses.OK:
                        tile[uindex] = AIR
                    elif response == KDS.System.MessageBox.Responses.CANCEL:
                        return
                    else:
                        assert False

            while len(tile) < SLOTCOUNT:
                tile.append(AIR)
            if len(tile) > SLOTCOUNT:
                KDS.System.MessageBox.Show("FATAL! Too many tiles.", "There are too many tiles in one or more slots of the map grid.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
                return

    output: str = "\n".join(" / ".join(" ".join(u.non_null_serial for u in grid[y][x]) for x in range(len(grid[y]))) for y in range(len(grid)))
    mapfile: str = filedialog.asksaveasfilename(initialfile="level", defaultextension=".dat", filetypes=(("Data file", "*.dat"), ("All files", "*.*")), title="Save Map")
    if len(mapfile) < 1:
        return

    with open(mapfile, "w", encoding="utf-8") as f:
        f.write(output)
