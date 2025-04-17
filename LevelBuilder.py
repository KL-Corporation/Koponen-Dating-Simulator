from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
import os
import random

import KDS.BuildData
import KDS.Cursor
import KDS.LevelBuilder
import KDS.LevelBuilder.CampaignProp
import KDS.LevelBuilder.LegacyGameMap
import KDS.LevelBuilder.LegacyTileProp
import KDS.LevelBuilder.LevelProp
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
import pygame.draw
from pygame.locals import *
import KDS.Clock
import KDS.Colors
import KDS.ConfigManager
import KDS.Console
import KDS.Convert
import KDS.Debug
import KDS.Events
import KDS.Math
import KDS.Jobs
import KDS.Linq
import KDS.Loading
import KDS.Logging
import KDS.System
import KDS.UI
import tkinter
from tkinter import filedialog
import json
import traceback
from dataclasses import dataclass
from enum import IntEnum, IntFlag, StrEnum

from typing import Any, Callable, Final, ItemsView, Iterable, NamedTuple, Optional, Self, Sequence, TypeAlias, Union

from KDS.LevelBuilder.Shared import *

KEYMAP_STR: Final[str] = """
[   KEYMAP   ]

Middle Mouse: Get Serial
Middle Mouse + SHIFT: Move Camera
Middle Mouse + CTRL: Get Serial with Properties
Middle Mouse + ALT: Change Brush Shape

Left Mouse: Set Serial
Left Mouse + SHIFT: Add Serial At Top
Left Mouse + CTRL: Insert Serial At Bottom
Left Mouse + C: No Collision
Left Mouse + ALT + C: Force Collision

Right Mouse: Reset Serial
Right Mouse + SHIFT: Remove Serial From Top
Right Mouse + CTRL: Remove Serial From Bottom
Right Mouse + C: Remove Collision Attribute
Right Mouse + ALT + C: Remove Collision Attribute

Mouse Scroll: Scroll Vertically
Mouse Scroll + SHIFT: Scroll Horizontally
Mouse Scroll + CTRL: Zoom
Mouse Scroll + ALT: Change Brush Size
Mouse Scroll + ALT + CTRL: Change Brush Density

CTRL + Z: Undo
CTRL + Y: Redo
CTRL + D: Duplicate Selection
CTRL + C: Copy
CTRL + V: Paste if possible

E: Open Material Menu
T: Input Console
R: Resize Map
F: Set Property
P: Set teleport index
O: Set Overlay
G: Select Reference Map File
Z: Toggle Zone Mode
Y: Toggle Overlay Visibility

TAB: Set store price
SHIFT + TAB: Set store discount price

CTRL + A: Select All (NOT RECOMMENDED)
CTRL + S: Save Project
CTRL + SHIFT + S: Save Project As
CTRL + O: Open Project

F5: Reload LevelProp
H: Show Help

[   KEYMAP   ]
""".strip()

root = tkinter.Tk()
root.withdraw()
if not KDS.System.ISLINUX:
    root.iconbitmap("Assets/Textures/Branding/levelBuilderIcon.ico")
pygame.init()
display: pygame.Surface = pygame.Surface((2, 2)) # Dunder surface for linting
display_size: tuple[int, int] = (1600, 800)
monitor_info = pygame.display.Info()
scalesize = 68
gamesize = 34
scaleMultiplier = scalesize / gamesize

ZOOMRANGE = (3, 128)
DEFAULTZOOM = scalesize

pygame.display.set_caption("KDS Level Builder")
pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/levelBuilderIcon.png"))
def SetDisplaySize(size: tuple[int, int] = (0, 0)):
    global display, display_size, display_info
    display = pygame.display.set_mode(size, RESIZABLE | DOUBLEBUF | HWSURFACE)
    display_size = display.get_size()
    display_info = pygame.display.Info()
SetDisplaySize((min(display_size[0], monitor_info.current_w), min(display_size[1], monitor_info.current_h - 100)))

APPDATA = os.path.join(str(os.getenv('APPDATA')), "KL Corporation", "KDS Level Builder")
LOGPATH = os.path.join(APPDATA, "logs")
os.makedirs(LOGPATH, exist_ok=True)
KDS.Logging.init(APPDATA, LOGPATH)
KDS.Logging.log_debug_info()
KDS.Cursor.init(cursor_index_override=0)
KDS.Jobs.init()

harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25)
harbinger_font_large = pygame.font.Font("Assets/Fonts/harbinger.otf", 55)
harbinger_font_small = pygame.font.Font("Assets/Fonts/harbinger.otf", 15)

class TextureHolder:
    class TextureData:
        def __init__(self, serialNumber: str, name: str, category: str | None, texture: pygame.Surface, metadata: dict[str, Any] | None = None) -> None:
            self.serialNumber: Final[str] = serialNumber
            self.name: Final[str] = name
            self.category: Final[str | None] = category

            self.texture: Final[pygame.Surface] = texture
            self.texture_size: Final[tuple[int, int]] = self.texture.get_size()

            self.is_contraband: Final[bool] = metadata is not None and metadata.get("isContraband") is True

            self.rescaleTexture()

        def rescaleTexture(self):
            self.scaledTexture: pygame.Surface = pygame.transform.scale(self.texture, (round(self.texture.get_width() * scaleMultiplier), round(self.texture.get_height() * scaleMultiplier)))
            self.scaledTexture_size: tuple[int, int] = self.scaledTexture.get_size()

            drkOvl = self.scaledTexture.convert_alpha()
            drkOvl.fill((0, 0, 0, 64), special_flags=BLEND_RGBA_MIN)
            self.darkOverlay: pygame.Surface = drkOvl

            lghtOvl = self.scaledTexture.convert_alpha()
            lghtOvl.fill((255, 255, 255, 255), special_flags=BLEND_RGB_MAX)
            lghtOvl.fill((255, 255, 255, 128), special_flags=BLEND_RGBA_MULT)
            self.lightOverlay: pygame.Surface = lghtOvl

    def __init__(self) -> None:
        self.textures: dict[str, TextureHolder.TextureData] = {}
        self.serials: list[str] = []
        self.names: list[str] = []

        self.trueScale: Final[set[str]] = set()
        self.noCollision: Final[set[str]] = set()

        self.TeleportOverlay: TextureHolder.TextureData | None = None
        self.NotFoundFallback: TextureHolder.TextureData | None = None

    def __iter__(self):
        return iter(self.textures.values())

    def AddTexture(self, serialNumber: str, path: str, name: str, category: str | None = None, colorkey: tuple[int, int, int] | None = KDS.Colors.White, alpha: int | None = None, metadata: dict[str, Any] | None = None) -> None:
        texture: pygame.Surface = pygame.image.load(path).convert()
        if colorkey is not None:
            texture.set_colorkey(colorkey)
        if alpha is not None:
            texture.set_alpha(alpha)

        self._Add(TextureHolder.TextureData(serialNumber, name, category, texture, metadata))

    def AddBuildData(self, serialPrefix: int, buildData: KDS.BuildData.BuildData, checkTruescale: bool = False, checkNoCollision: bool = False):
        if serialPrefix < 0 or serialPrefix > 9:
            raise ValueError("Invalid serial prefix.")

        for dName, d in buildData.data.items():
            localSerial: int = d["serialNumber"]
            globalSerial: str = f"""{serialPrefix}{localSerial:03d}"""

            category: str | None | Any = d.get("category")
            if not isinstance(category, str):
                category = None

            if checkTruescale and d["trueScale"] == True:
                self.trueScale.add(globalSerial)
            if checkNoCollision and d["noCollision"] == True:
                self.noCollision.add(globalSerial)

            self._Add(TextureHolder.TextureData(globalSerial, dName, category, buildData.textures[localSerial], metadata=d))

    def _Add(self, texture_data: TextureData):
        self.textures[texture_data.serialNumber] = texture_data
        self.serials.append(texture_data.serialNumber)
        self.names.append(texture_data.name)

    def GetData(self, serialNumber: str) -> TextureHolder.TextureData:
        # try:
        #     return self.textures[serialNumber]
        # except Exception:
        #     if self.NotFoundFallback is not None:
        #         return self.NotFoundFallback
        #     else:
        #         raise

        # The above optimization did made performance worse...?
        # Either dictionary __getitem__ is slow or the try-catch didn't work well with the Python 3.13 JIT compiler

        tex: TextureHolder.TextureData | None = self.textures.get(serialNumber, self.NotFoundFallback)
        if tex is None:
            raise KeyError(f"No texture found for serial number: '{serialNumber}'")
        return tex

    def GetDefaultTexture(self, serialNumber: str) -> pygame.Surface:
        return self.GetData(serialNumber).texture

    def GetScaledTexture(self, serialNumber: str) -> pygame.Surface:
        return self.GetData(serialNumber).scaledTexture

    def GetScaledTextureWithSize(self, serialNumber: str) -> tuple[pygame.Surface, tuple[int, int]]:
        data = self.GetData(serialNumber)
        return data.scaledTexture, data.scaledTexture_size

    def RescaleTextures(self) -> None:
        for t in self.textures.values():
            t.rescaleTexture()
        if self.TeleportOverlay is not None:
            self.TeleportOverlay.rescaleTexture()
        if self.NotFoundFallback is not None:
            self.NotFoundFallback.rescaleTexture()
        LevelPropData.rescale()

#region Textures
Textures = TextureHolder()

Textures.AddBuildData(0, KDS.BuildData.load_tiles(), checkTruescale=True, checkNoCollision=True)
Textures.AddBuildData(1, KDS.BuildData.load_items())
Textures.AddBuildData(3, KDS.BuildData.load_teleports())

Textures.AddTexture("2001", "Assets/Textures/Animations/imp_walking_0.png", "Imp")
Textures.AddTexture("2002", "Assets/Textures/Animations/seargeant_walking_0.png", "Seargeant")
Textures.AddTexture("2003", "Assets/Textures/Animations/drug_dealer_walking_0.png", "Drug Dealer")
Textures.AddTexture("2004", "Assets/Textures/Animations/turbo_shotgunner_walking_0.png", "Turbo Shotgunner")
Textures.AddTexture("2005", "Assets/Textures/Animations/mafiaman_walking_0.png", "Mafiaman")
Textures.AddTexture("2006", "Assets/Textures/Animations/methmaker_idle_0.png", "Methmaker", colorkey=KDS.Colors.Cyan)
Textures.AddTexture("2007", "Assets/Textures/Animations/undead_monster_walking_0.png", "Undead Monster", colorkey=KDS.Colors.Cyan)
Textures.AddTexture("2008", "Assets/Textures/Animations/mummy_walking_0.png", "Mummy")
Textures.AddTexture("2009", "Assets/Textures/Animations/security_guard_walking_0.png", "Security Guard", category="story", colorkey=KDS.Colors.Cyan)
Textures.AddTexture("2010", "Assets/Textures/Animations/bulldog_0.png", "Bulldog", category="story")
Textures.AddTexture("2011", "Assets/Textures/Animations/z_walk_0.png", "Zombie")
Textures.AddTexture("2012", "Assets/Textures/Animations/archvile_run_0.png", "Archvile")

Textures.AddTexture("4003", "Assets/Textures/Teachers/Test/koponen_idle_0.png", "TEST ENTITY", category="story")
Textures.AddTexture("4001", "Assets/Textures/Teachers/LaaTo/idle_0.png", "LaaTo", category="story")
Textures.AddTexture("4002", "Assets/Textures/Teachers/KuuMa/idle_0.png", "KuuMa", category="story")
Textures.AddTexture("4999", "Assets/Textures/NPC/Static/person_0/npc-idle_0.png", "Random Static Student", category="story")
Textures.AddTexture("4309", "Assets/Textures/NPC/Room309/0/idle_0.png", "Room 309 NPC", category="story")

Textures.NotFoundFallback = TextureHolder.TextureData("----", "<error>", None, pygame.image.load("Assets/Editor/Textures/missing.png").convert())

telep_overlay_tex: Final = pygame.image.load("Assets/Textures/Teleports/telep.png").convert()
telep_overlay_tex.set_alpha(100)
Textures.TeleportOverlay = TextureHolder.TextureData("3001", "<error>", None, telep_overlay_tex) # Set serial so that this overlay isn't drawn over tile 3001
#endregion

### GLOBAL VARIABLES ###

scroll: list[int] = [0, 0]
currentSaveName = ''

grid: GridType
gridSize: tuple[int, int]
undo: Undo | None = None

referenceGrid: Optional[GridType] = None
referenceGridSize: tuple[int, int] = (0, 0)
referenceGridHandle: Optional[KDS.Jobs.JobHandle] = None

renderOverlays: bool = True
zoneMode: bool = False

disabled_filters: dict[str, tuple[str | None, ...]] = {}

build_undo: ChangeUndoRecord | None = None
remove_undo: ChangeUndoRecord | None = None

class LevelPropData:
    @staticmethod
    def rescale():
        LevelPropData.KoponenTextureRescaled = KDS.Convert.AspectScale(LevelPropData.KoponenTexture, (int(LevelPropData.KoponenTexture.get_width() * scaleMultiplier), 0), KDS.Convert.AspectMode.WidthControlsHeight)
        LevelPropData.PlayerTextureRescaled = KDS.Convert.AspectScale(LevelPropData.PlayerTexture, (int(LevelPropData.PlayerTexture.get_width() * scaleMultiplier), 0), KDS.Convert.AspectMode.WidthControlsHeight)

    ShowKoponen: bool = False
    KoponenPos: tuple[int, int] = (0, 0)
    KoponenTexture: pygame.Surface = pygame.image.load("Assets/Textures/Player/koponen_idle_0.png").convert()
    KoponenTexture.set_colorkey(KDS.Colors.White)
    KoponenTexture.set_alpha(64)
    ShowPlayer: bool = False
    PlayerPos: tuple[int, int] = (0, 0)
    PlayerTexture: pygame.Surface = pygame.image.load("Assets/Textures/Player/idle_0.png").convert()
    PlayerTexture.set_colorkey(KDS.Colors.White)
    PlayerTexture.set_alpha(64)
    KoponenTextureRescaled: pygame.Surface = pygame.Surface((0, 0))
    PlayerTextureRescaled: pygame.Surface = pygame.Surface((0, 0))
    PlayerFlipped: bool = False
LevelPropData.rescale()

class UndoRecord(ABC):
    @abstractmethod
    def undomanager_rollback(self, grid: GridType) -> GridType | None:
        raise NotImplementedError()
    @abstractmethod
    def undomanager_rollforward(self, grid: GridType) -> GridType | None:
        raise NotImplementedError()

    @abstractmethod
    def undomanager_register(self, parent: Undo) -> None:
        raise NotImplementedError()

class ResizeUndoRecord(UndoRecord):
    """### DO NOT MODIFY ANY GridUnit INSTANCES, ONLY CREATE NEW ONES."""

    def __init__(self, original_grid: GridType) -> None:
        self.original_grid: Final[GridType] = original_grid
        self._resized_grid: GridType | None = None

    @property
    def resized_grid(self) -> GridType | None:
        return self._resized_grid

    @resized_grid.setter
    def resized_grid(self, value: GridType) -> None:
        if self._resized_grid is not None:
            raise ValueError("Cannot set resized grid, value has already been set.")
        self._resized_grid = value

    def undomanager_register(self, parent: Undo) -> None:
        if self.resized_grid is None:
            raise ValueError("Cannot register undo record without providing the resized grid as well.")

    def undomanager_rollback(self, grid: GridType) -> GridType | None:
        return self.original_grid

    def undomanager_rollforward(self, grid: GridType) -> GridType | None:
        assert(self.resized_grid is not None)
        return self.resized_grid

class ChangeUndoRecord(UndoRecord):
    @dataclass(frozen=True)
    class _Change:
        unit: UnitData
        before: UnitData
        after: UnitData

    class _Recording:
        def __init__(self, unit: UnitData) -> None:
            self.unit: Final[UnitData] = unit

            self._befores: list[UnitData] = []
            self._afters: list[UnitData] = []

            self._completed: bool = False

        def add_before(self, unit: UnitData) -> None:
            if self._completed:
                raise RuntimeError("Recording has completed.")

            self._befores.append(unit.Copy())

        def add_after(self, unit: UnitData) -> None:
            if self._completed:
                raise RuntimeError("Recording has completed.")

            self._afters.append(unit.Copy())

        def complete(self) -> ChangeUndoRecord._Change:
            self._completed = True

            assert(len(self._befores) > 0)
            if len(self._afters) != len(self._befores):
                raise RuntimeError(f"Before and after state counts don't match. Before count: {len(self._befores)}, After count: {len(self._afters)}")

            return ChangeUndoRecord._Change(
                unit=self.unit,
                before=self._befores[0],
                after=self._afters[-1]
            )

    def __init__(self) -> None:
        self._parent: Undo | None = None

        self._changes: list[ChangeUndoRecord._Change] = []

        self._recording: ChangeUndoRecord._Recording | None = None

    def __del__(self) -> None:
        if self._parent is None:
            raise RuntimeError("UndoRecord was destroyed before registering with a parent Undo.")

    def record_before(self, unit: UnitData | PropertiesData) -> None:
        if isinstance(unit, PropertiesData):
            unit = unit.parent
        assert(isinstance(unit, UnitData))

        if self._parent is not None:
            raise RuntimeError("Cannot record change. Undo record already registered.")

        if self._recording is not None and self._recording.unit is not unit:
            self._changes.append(self._recording.complete())
            self._recording = None

        if self._recording is None:
            assert(grid[unit.pos[1]][unit.pos[0]] is unit)
            self._recording = ChangeUndoRecord._Recording(unit)
        self._recording.add_before(unit)

    def record_after(self, unit: UnitData | PropertiesData) -> None:
        if isinstance(unit, PropertiesData):
            unit = unit.parent
        assert(isinstance(unit, UnitData))

        if self._parent is not None:
            raise RuntimeError("Cannot record change. Undo record already registered.")

        if self._recording is None:
            raise ValueError("Cannot record change. No change recording has been started.")
        if self._recording.unit is not unit:
            raise ValueError("Cannot record change. Another unit's change recording has been started.")

        self._recording.add_after(unit)

    def undomanager_register(self, parent: Undo) -> None:
        if self._recording is not None:
            self._changes.append(self._recording.complete())
        self._parent = parent

    def undomanager_rollback(self, grid: GridType) -> None:
        # reversed so that when we change the same tile multiple times, we also revert it in the correct order
        for c in reversed(self._changes):
            self._roll(c.after, c.before, unit=c.unit, grid=grid)

    def undomanager_rollforward(self, grid: GridType) -> None:
        for c in self._changes:
            self._roll(c.before, c.after, unit=c.unit, grid=grid)

    def _roll(self, /, _from: UnitData, _to: UnitData, *, unit: UnitData, grid: GridType) -> None:
        x: int
        y: int
        x, y = unit.pos
        assert(_from.pos == unit.pos)
        assert(_to.pos == unit.pos)

        assert(grid[y][x] is unit)

        if unit != _from:
            KDS.Logging.warning(f"Source unit data does not match grid unit data. There might have been some changes that were unaccounted in undo/redo.", consoleVisible=True)

        unit.CopyFrom(None, _to, undo_can_be_none=True)
        assert(unit == _to)

class Undo:
    @dataclass(frozen=True)
    class _Saved:
        undoable: int
        total: int

    def __init__(self) -> None:
        self._undoable_change_count: int = 0
        self._total_change_count: int = 0

        self._saved_changes: Undo._Saved | None = None

        self._undo: deque[UndoRecord] = deque(maxlen=1000)
        self._redo: deque[UndoRecord] = deque(maxlen=1000)

    def register(self, record: UndoRecord) -> None:
        record.undomanager_register(self)

        self._undo.append(record)
        self._redo.clear()

        self._undoable_change_count += 1
        self._total_change_count += 1

    def undo(self) -> None:
        global grid

        if len(self._undo) < 1:
            KDS.Logging.info("No undo history left.", consoleVisible=True)
            return

        record: UndoRecord = self._undo.pop()
        new_grid: GridType | None = record.undomanager_rollback(grid=grid)
        self._redo.appendleft(record)

        self._record_try_reassign_grid(new_grid)

        self._undoable_change_count -= 1
        self._total_change_count -= 1

    def redo(self) -> None:
        global grid

        if len(self._redo) < 1:
            KDS.Logging.info("No redo history left.", consoleVisible=True)
            return

        record: UndoRecord = self._redo.popleft()
        new_grid: GridType | None = record.undomanager_rollforward(grid=grid)
        self._undo.append(record)

        self._record_try_reassign_grid(new_grid)

        self._undoable_change_count += 1
        self._total_change_count += 1

    def _record_try_reassign_grid(self, new_grid: GridType | None):
        global grid, gridSize
        if new_grid is None:
            return

        grid = new_grid
        gridSize = (len(grid[0]), len(grid))

    def register_zone_new(self) -> None:
        self._total_change_count += 1

    def register_zone_update(self) -> None:
        pass # when dragging, zone is updated every frame
             # pass, as we don't want to spam increment the changes value

    def register_zone_properties_update(self) -> None:
        self._total_change_count += 1

    def register_was_saved(self) -> None:
        self._saved_changes = Undo._Saved(undoable=self._undoable_change_count, total=self._total_change_count)

    @property
    def unsaved_changes(self) -> int:
        total: int
        if self._saved_changes is None:
            total = self._total_change_count
        else:
            total_diff: int = self._total_change_count - self._saved_changes.total
            undoable_diff: int = self._undoable_change_count - self._saved_changes.undoable
            if undoable_diff >= 0:
                total = undoable_diff + total_diff
            else:
                total = (2 * self._undoable_change_count) + total_diff

        assert(total >= 0)
        return total

def UnsavedChangesInterrupt(followup_question: str) -> bool:
    if undo is None:
        return False
    if undo.unsaved_changes <= 0:
        return False
    resp: KDS.System.MessageBox.Responses = KDS.System.MessageBox.Show(
        "Unsaved Changes.",
        f"There are unsaved changes. {followup_question}",
        KDS.System.MessageBox.Buttons.YESNO,
        KDS.System.MessageBox.Icon.WARNING
    )
    return resp != KDS.System.MessageBox.Responses.YES

def LB_Quit():
    global matMenRunning, btn_menu, mainRunning, multiselect_menu_running
    if UnsavedChangesInterrupt("Are you sure you want to quit?"):
        return
    matMenRunning = False
    btn_menu = False
    multiselect_menu_running = False
    mainRunning = False

KDS.Console.init(display, pygame.Surface((1200, 800)), _Offset=(200, 0), _KDS_Quit = LB_Quit)

####################################################################################################

class UnitData:
    EMPTYSERIAL: Final[str] = "0000 0000 0000 0000"
    EMPTY: Final[str] = "0000"
    SLOTCOUNT: Final[int] = 4

    DOORSERIALS: set[str] = { "0023", "0024", "0025", "0026" }

    def __init__(self, position: tuple[int, int], serialNumber: str = EMPTYSERIAL):
        self.pos = position
        self.serialNumber = serialNumber
        self._updateSplit()

        self._properties = PropertiesData(self)

        self.matchesReference = False
        """State variable, will not be copied."""

    @property
    def properties(self) -> PropertiesData:
        return self._properties

    def __eq__(self, other) -> bool:
        """ == operator """
        if isinstance(other, UnitData):
            return self.Equals(other)
        return False

    def __ne__(self, other) -> bool:
        """ != operator """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.serialNumber

    def Equals(self, other: UnitData) -> bool:
        if self.pos != other.pos:
            return False
        if self.serialNumber != other.serialNumber:
            return False
        if self.properties != other.properties:
            return False
        return True

    def Copy(self) -> UnitData:
        data = UnitData(position=self.pos, serialNumber=self.serialNumber)
        data._properties = self.properties.Copy(overrideParent=data)
        return data

    def CopyFrom(self, undo: ChangeUndoRecord | None, unit: UnitData, *, undo_can_be_none: bool = False) -> None:
        if not undo_can_be_none and undo is None:
            raise ValueError("Undo cannot be None. If you are ABSOLUTELY sure that it can, please set undo_can_be_none=True")

        if undo is not None:
            undo.record_before(self)

        self.pos = unit.pos
        self.serialNumber = unit.serialNumber
        self._updateSplit()
        self._properties = unit.properties.Copy(overrideParent=self)

        # do not set, is handled by reference grid
        # self.matchesReference = unit.matchesReference

        if undo is not None:
            undo.record_after(self)

    def setProperties(self, undo: ChangeUndoRecord, properties: dict[UnitType, dict[str, Union[str, int, float, bool]]]):
        self.properties.SetAll(undo, properties)

    def addProperties(self, undo: ChangeUndoRecord, properties: dict[UnitType, dict[str, Union[str, int, float, bool]]]):
        undo.record_before(self)

        for _type, value in properties.items():
            for k, v in value.items():
                self.properties.Set(undo, _type, k, v)

        undo.record_after(self)

    def _updateSplit(self):
        self.serials = tuple(self.serialNumber.split(" "))
        if len(self.serials) != UnitData.SLOTCOUNT:
            KDS.Logging.AutoError(f"Serials length does not match slot count! Serials length: {len(self.serials)} | Slot Count: {UnitData.SLOTCOUNT} | Serials: {self.serials} | Serial Number: {self.serialNumber}")
        self.filledSerials = tuple(KDS.Linq.Where(self.serials, lambda s: s != UnitData.EMPTY))

    def overrideData(self, undo: ChangeUndoRecord, _from: UnitData):
        undo.record_before(self)

        self.overrideSerial(undo, _from.serialNumber)
        self._updateSplit()
        self.properties.SetAll(undo, _from.properties.GetAll())

        undo.record_after(self)

    def overrideSerial(self, undo: ChangeUndoRecord | None, newSerial: str, *, undo_can_be_none: bool = False):
        if not undo_can_be_none and undo is None:
            raise ValueError("Undo cannot be None. If you are ABSOLUTELY sure that it can, please set undo_can_be_none=True")

        if undo is not None:
            undo.record_before(self)

        self.serialNumber = newSerial
        self._updateSplit()

        if undo is not None:
            undo.record_after(self)

    def setSerial(self, undo: ChangeUndoRecord, srlNumber: str):
        undo.record_before(self)

        self.serialNumber = f"{srlNumber} 0000 0000 0000"
        self._updateSplit()

        undo.record_after(self)

    def setSerialToSlot(self, undo: ChangeUndoRecord | None, srlNumber: str, slot: int, *, undo_can_be_none: bool = False):
        if not undo_can_be_none and undo is None:
            raise ValueError("Undo cannot be None. If you are ABSOLUTELY sure that it can, please set undo_can_be_none=True")
        if slot >= UnitData.SLOTCOUNT or slot < 0:
            raise ValueError(f"Slot {slot} is an invalid index!")

        if undo is not None:
            undo.record_before(self)

        self.serialNumber = self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]
        self._updateSplit()

        if undo is not None:
            undo.record_after(self)

    def getSerial(self, slot: int):
        slot = slot + 1 if slot > 0 else slot
        return self.serialNumber[slot : slot + 4]

    def addSerial(self, undo: ChangeUndoRecord, srlNumber: str):
        for index, number in enumerate(self.serials):
            if int(number) == 0:
                if srlNumber not in self.serials:
                    if srlNumber[0] != "3" or not self.hasTeleport():
                        undo.record_before(self)

                        self.setSerialToSlot(undo, srlNumber, index)

                        undo.record_after(self)
                    else:
                        KDS.Logging.info("Only one teleport is allowed per unit.", True)
                else:
                    KDS.Logging.info(f"Serial {srlNumber} already in {self.pos}!", True)
                return

        KDS.Logging.info(f"No empty slots at {self.pos} available for serial {srlNumber}!", True)

    def insertSerial(self, undo: ChangeUndoRecord, srlNumber: str):
        if srlNumber[0] != "3" and self.hasTeleport():
            KDS.Logging.info("Only one teleport is allowed per unit.", True)
            return
        if srlNumber in self.serials:
            KDS.Logging.info(f"Serial {srlNumber} already in {self.pos}!", True)
            return
        if len(self.filledSerials) > UnitData.SLOTCOUNT:
            KDS.Logging.info(f"No empty slots at {self.pos} available to insert serial {srlNumber}!", True)
            return

        undo.record_before(self)

        for index, number in enumerate(self.filledSerials): # No need to copy because tuple
            self.setSerialToSlot(undo, number, index + 1)
        self.setSerialToSlot(undo, srlNumber, 0)

        undo.record_after(self)

    def getSlot(self, serial: str) -> Optional[int]:
        try:
            return self.serials.index(serial)
        except ValueError:
            return None

    def hasTile(self) -> bool:
        return KDS.Linq.Any(self.serials, lambda s: s[0] == "0" and s != UnitData.EMPTY)

    def hasItem(self) -> bool:
        return KDS.Linq.Any(self.serials, lambda s: s[0] == "1")

    def hasTeleport(self) -> bool:
        return KDS.Linq.Any(self.serials, lambda s: s[0] == "3")

    def removeSerial(self, undo: ChangeUndoRecord):
        for index, number in reversed(list(enumerate(self.serials))):
            if int(number) != 0:
                undo.record_before(self)
                self.setSerialToSlot(undo, UnitData.EMPTY, index)
                undo.record_after(self)
                return

    def removeSerialFromStart(self, undo: ChangeUndoRecord):
        undo.record_before(self)

        srlist = self.serials
        for index in range(len(srlist)):
            if index >= len(srlist) - 1:
                self.setSerialToSlot(undo, UnitData.EMPTY, index)
            else:
                self.setSerialToSlot(undo, srlist[index + 1], index)

        undo.record_after(self)

    def resetSerial(self, undo: ChangeUndoRecord):
        undo.record_before(self)

        self.serialNumber = UnitData.EMPTYSERIAL
        self._updateSplit()
        self.properties.RemoveUnused(undo)

        undo.record_after(self)

    @staticmethod
    def toSerialString(srlNumber: str):
        return f"{srlNumber} 0000 0000 0000"

    @staticmethod
    def renderSerial(surface: pygame.Surface, properties: Optional[PropertiesData], serial: str, pos: tuple[int, int], lightOverlay: bool = False):
        textureData = Textures.GetData(serial)
        blitPos = (pos[0], pos[1] - textureData.scaledTexture_size[1] + scalesize) if serial not in Textures.trueScale else (pos[0] - textureData.scaledTexture_size[0] + scalesize, pos[1] - textureData.scaledTexture_size[1] + scalesize)
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Will render some tiles incorrectly

        # blitting
        surface.blit(textureData.scaledTexture, blitPos)

        ser0: str = serial[0]
        if ser0 == "0" and properties is not None:
            checkCollision = properties.Get(UnitType.Tile, "checkCollision", None)
            if isinstance(checkCollision, bool):
                if not checkCollision:
                    if textureData.serialNumber not in Textures.noCollision: # and textureData.darkOverlay is not None: # I don't know if pygame.Surface has a custom equals operator.
                        surface.blit(textureData.darkOverlay, blitPos)
                else:
                    pygame.draw.rect(surface, KDS.Colors.White, (pos[0], pos[1], scalesize, scalesize))
                    KDS.Logging.warning(f"checkCollision forced on at: {pos}. This is generally not recommended.", True)
        elif ser0 == "3" and Textures.TeleportOverlay is not None and serial != Textures.TeleportOverlay.serialNumber:
            # telepOverlay = Textures.GetScaledTexture("3001").copy()
            # telepOverlay.set_alpha(100)
            surface.blit(Textures.TeleportOverlay.scaledTexture, pos)

        if lightOverlay: # I don't know if pygame.Surface has a custom equals operator.
            surface.blit(textureData.lightOverlay, blitPos)

    @staticmethod
    def renderUpdate(surface: pygame.Surface, scroll: list[int], renderList: GridType, brush: BrushData,
                     keys_pressed: pygame.key.ScancodeWrapper, mouse_pressed: tuple[bool, ...], pickTile: bool = False, pickLastTile: UnitData | None = None) -> UnitData | None:
        global allowTilePlacement, build_undo, remove_undo

        assert(undo is not None)

        _TYPECOLORS = {
            UnitType.Tile: KDS.Colors.EmeraldGreen,
            UnitType.Item: KDS.Colors.RiverBlue,
            UnitType.Enemy: KDS.Colors.AviatorRed,
            UnitType.Teleport: KDS.Colors.Yellow,
            UnitType.Entity: KDS.Colors.Orange,
            UnitType.Unspecified: KDS.Colors.Magenta
        }

        #region Scroll Clamping
        scroll[0] = KDS.Math.Clamp(scroll[0], KDS.Math.CeilToInt(-display_size[0] / scalesize) + 1, gridSize[0] - 1)
        scroll[1] = KDS.Math.Clamp(scroll[1], KDS.Math.CeilToInt(-display_size[1] / scalesize) + 1, gridSize[1] - 1)
        #endregion

        tip_renders = []
        mpos = pygame.mouse.get_pos()
        mpos_tilepos: tuple[int, int] | None = (int(mpos[0] / scalesize) + scroll[0], int(mpos[1] / scalesize) + scroll[1])
        pygame.draw.rect(surface, (80, 30, 30), (-scroll[0] * scalesize, -scroll[1] * scalesize, gridSize[0] * scalesize, gridSize[1] * scalesize))
        doorRenders: list[tuple[str, tuple[int, int], bool]] = []
        overlayRenders: list[tuple[str, tuple[int, int], bool]] = []
        picked_tile: UnitData | None = None
        for row in renderList[max(scroll[1], 0) : KDS.Math.CeilToInt(scroll[1] + display_size[1] / scalesize)]:
            for unit in row[max(scroll[0], 0) : KDS.Math.CeilToInt(scroll[0] + display_size[0] / scalesize)]:
                normalBlitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                overlayTileprops = unit.properties.Get(UnitType.Unspecified, "overlay", None)
                if isinstance(overlayTileprops, str):
                    overlayRenders.append((overlayTileprops, normalBlitPos, unit.matchesReference))
                for number in unit.serials:
                    if number == UnitData.EMPTY:
                        continue
                    if number in UnitData.DOORSERIALS:
                        doorRenders.append((number, (normalBlitPos[0], normalBlitPos[1] + scalesize), unit.matchesReference))
                        continue

                    UnitData.renderSerial(surface, unit.properties, number, normalBlitPos, unit.matchesReference)

                if unit.pos == mpos_tilepos:
                    if unit.hasTeleport():
                        teleportIdentifier = unit.properties.Get(UnitType.Teleport, "identifier", None)
                        # if teleportIdentifier == None:
                        #     unit.properties.Set(UnitType.Teleport, "identifier", 1)
                        #     teleportIdentifier = 1
                        teleportIdentifierTip: str = f"teleport id: {teleportIdentifier}"
                        if not isinstance(teleportIdentifier, int):
                            teleportIdentifierTip += " (invalid)"
                        tip_renders.append(harbinger_font_small.render(teleportIdentifierTip, True, KDS.Colors.AviatorRed))

                        if keys_pressed[K_p]:
                            if not zoneMode:
                                newTeleportIdentifier: Optional[int] = KDS.Console.Start(f"Set teleport ID: (int[0, 2147483647])", True, KDS.Console.CheckTypes.Int(0, 2147483647), defVal=str(teleportIdentifier), autoFormat=True)
                                if newTeleportIdentifier != None:
                                    newTeleportIdentifierUndo: ChangeUndoRecord = ChangeUndoRecord()
                                    unit.properties.Set(newTeleportIdentifierUndo, UnitType.Teleport, "identifier", newTeleportIdentifier)
                                    undo.register(newTeleportIdentifierUndo)

                    if keys_pressed[K_TAB] and unit.hasItem():
                        storePriceDiscounted: bool = keys_pressed[K_LSHIFT]
                        storePriceKey: str = "storePrice" if not storePriceDiscounted else "storeDiscountPrice"
                        storePriceMsg: str = "Enter Price:" if not storePriceDiscounted else "Enter Discount Price:"
                        storePriceStr: str | None = KDS.Console.Start(storePriceMsg, allowEscape=False, checkType=KDS.Console.CheckTypes.Float()) # do not allow escape as it removes the price as well
                        storePriceUndo: ChangeUndoRecord = ChangeUndoRecord()
                        if storePriceStr is not None and len(storePriceStr) > 0:
                            unit.properties.Set(storePriceUndo, UnitType.Item, storePriceKey, float(storePriceStr))
                        else:
                            unit.properties.Remove(storePriceUndo, UnitType.Item, storePriceKey)
                        undo.register(storePriceUndo)

                    elif keys_pressed[K_f]:
                        autoFill = {}
                        for t in UnitType:
                            autoFill[t.name] = "break"
                        setPropType = str(KDS.Console.Start("Enter Property Type:", True, KDS.Console.CheckTypes.Commands(), commands=autoFill)).lower()
                        propType = KDS.Linq.FirstOrNone(UnitType, lambda t: t.name.lower() == setPropType)
                        if len(setPropType) > 0 and propType != None:
                            setPropKey: str = KDS.Console.Start("Enter Property Key:")
                            if len(setPropKey) > 0:
                                setPropValUnformatted: str = KDS.Console.Start("Enter Property Value:")
                                if propType == UnitType.Unspecified and setPropKey == "overlay": # Force string for overlay
                                    setPropVal = setPropValUnformatted
                                else:
                                    setPropVal = KDS.Convert.AutoType(setPropValUnformatted, setPropValUnformatted) # If cannot be parsed to int, bool or float; return string

                                setPropUndo: ChangeUndoRecord = ChangeUndoRecord()
                                if len(setPropValUnformatted) > 0:
                                    unit.properties.Set(setPropUndo, propType, setPropKey, setPropVal)
                                else:
                                    unit.properties.Remove(setPropUndo, propType, setPropKey)
                                undo.register(setPropUndo)
                        elif len(setPropType) > 0:
                            KDS.Logging.warning(f"\"{setPropType}\" could not be parsed to any type!", True)
                    elif keys_pressed[K_o] and not keys_pressed[K_LCTRL]:
                        overlayId = materialMenu(UnitData.EMPTY)
                        allowTilePlacement = False
                        overlayUndo: ChangeUndoRecord = ChangeUndoRecord()
                        if overlayId != UnitData.EMPTY:
                            unit.properties.Set(overlayUndo, UnitType.Unspecified, "overlay", overlayId)
                        else:
                            unit.properties.Remove(overlayUndo, UnitType.Unspecified, "overlay")
                        undo.register(overlayUndo)
                    elif keys_pressed[K_q]:
                        if referenceGrid != None and unit.pos[1] < len(referenceGrid):
                            reference2 = referenceGrid[unit.pos[1]]
                            if unit.pos[0] < len(reference2):
                                tmpReferenceUndo: ChangeUndoRecord = ChangeUndoRecord()
                                unit.overrideData(tmpReferenceUndo, reference2[unit.pos[0]])
                                undo.register(tmpReferenceUndo)

                    if len(unit.filledSerials) > 1: # If more than one tile
                        for sr in unit.filledSerials: tip_renders.append(harbinger_font_small.render(sr, True, KDS.Colors.Red))

                    if pickTile:
                        if pickLastTile is None or unit.pos != pickLastTile.pos:
                            brush.PickBrush(unit, get_properties=keys_pressed[K_LCTRL])
                            picked_tile = unit
                        else:
                            picked_tile = pickLastTile
        del unit

        if pickTile:
            if picked_tile is None: # if no tiles were touching mouse when iterating, a tile wasn't picked, so we reset the brush.
                brush.SetBrush()
            brush.styles |= BrushStyles.pick_brush
        else:
            brush.styles &= ~BrushStyles.pick_brush

        brush.RenderUpdate(mpos_tilepos, grid, mouse_pressed, surface if Drag.Rect is None else None)

        build_undo_was_used: bool = False
        remove_undo_was_used: bool = False
        if allowTilePlacement:
            if mouse_pressed[0]:
                if build_undo is None:
                    build_undo = ChangeUndoRecord()
                build_undo_was_used = True

                if keys_pressed[K_c]:
                    for brush_unit in brush.IterAllUnits(grid=grid):
                        if brush_unit.hasTile():
                            setVal = False
                            if keys_pressed[K_LALT]:
                                setVal = True
                            brush_unit.properties.Set(build_undo, UnitType.Tile, "checkCollision", setVal)
                elif not brush.IsEmpty:
                    if keys_pressed[K_LSHIFT]:
                        brush.Add(build_undo, grid)
                    elif keys_pressed[K_LCTRL]:
                        brush.Insert(build_undo, grid)
                    else:
                        brush.Set(build_undo, grid)
            elif mouse_pressed[2]:
                if remove_undo is None:
                    remove_undo = ChangeUndoRecord()
                remove_undo_was_used = True

                if keys_pressed[K_c]:
                    for brush_unit in brush.IterAllUnits(grid=grid):
                        brush_unit.properties.Remove(remove_undo, UnitType.Tile, "checkCollision")
                else:
                    if keys_pressed[K_LSHIFT]:
                        brush.Remove(remove_undo, grid)
                    elif keys_pressed[K_LCTRL]:
                        brush.Purge(remove_undo, grid)
                    else:
                        brush.Reset(remove_undo, grid)

        if not build_undo_was_used and build_undo is not None:
            undo.register(build_undo)
            build_undo = None
        if not remove_undo_was_used and remove_undo is not None:
            undo.register(remove_undo)
            remove_undo = None
        # UnitData.placedOnTile = unit

        if mpos_tilepos[1] >= 0 and mpos_tilepos[1] < len(grid) and mpos_tilepos[0] >= 0 and mpos_tilepos[0] < len(grid[0]):
            tipUnit: UnitData | None = None
            try:
                tipUnit = grid[mpos_tilepos[1]][mpos_tilepos[0]]
            except IndexError:
                KDS.Logging.AutoError(f"Mouse pos out of range: {mpos_tilepos}", consoleVisible=True)

            if tipUnit is not None:
                tipProps = tipUnit.properties.GetAll()
                for _type, properties in tipProps.items():
                    color = _TYPECOLORS[_type]
                    for k, v in properties.items():
                        if k in ("checkCollision", "identifier"):
                            continue
                        rendered_tip = harbinger_font_small.render(f"{k}: ({type(v).__name__}) {v}", True, color)
                        tip_renders.append(rendered_tip)

        for doorSrl, doorPos, lightOverlay in doorRenders:
            UnitData.renderSerial(surface, None, doorSrl, doorPos, lightOverlay)
        if renderOverlays:
            for ovs, ovp, ovov in overlayRenders:
                UnitData.renderSerial(surface, None, ovs, ovp, ovov)

        if len(tip_renders) > 0:
            totHeight = 0
            maxWidth = 0
            for tip in tip_renders:
                totHeight += tip.get_height() + 8
                maxWidth = max(maxWidth, tip.get_width())
            totHeight -= 8
            pygame.draw.rect(display, KDS.Colors.Gray, pygame.Rect(mpos[0] + 15 - 3, mpos[1] + 15 - 3, maxWidth + 5, totHeight + 5))
            cumHeight = 0
            for tip in tip_renders:
                pygame.draw.rect(display, KDS.Colors.LightGray, pygame.Rect(mpos[0] + 15 - 3, mpos[1] + 15 - 3 + cumHeight, maxWidth + 5, tip.get_height() + 5))
                display.blit(tip, (mpos[0] + 15 + maxWidth // 2 - tip.get_width() // 2, mpos[1] + 15 + cumHeight))
                cumHeight += tip.get_height() + 8

        mousePosText = harbinger_font.render(str(mpos_tilepos), True, KDS.Colors.AviatorRed)
        display.blit(mousePosText, (display_size[0] - mousePosText.get_width(), display_size[1] - mousePosText.get_height()))
        if KDS.Debug.Enabled:
            mpos_pixelpos: Final[tuple[int, int]] = (int(34 * mpos[0] / scalesize) + (34 * scroll[0]), int(34 * mpos[1] / scalesize) + (34 * scroll[1]))
            pixelMousePosText: Final = harbinger_font_small.render(str(mpos_pixelpos), True, KDS.Colors.RiverBlue)
            display.blit(pixelMousePosText, (display_size[0] - pixelMousePosText.width, display_size[1] - mousePosText.height - 4 - pixelMousePosText.height))

        # UnitData.releasedButtons[0] = not mouse_pressed[0]
        # UnitData.releasedButtons[2] = not mouse_pressed[2]

        return picked_tile

    @staticmethod
    def referenceUpdate():
        global grid, referenceGrid, gridSize, referenceGridSize
        for x in range(min(gridSize[0], referenceGridSize[0])):
            # if referenceGridSize == None:
            #     return
            for y in range(min(gridSize[1], referenceGridSize[1])):
                if referenceGrid == None:
                    return
                grid[y][x].matchesReference = grid[y][x].Equals(referenceGrid[y][x])

GridType: TypeAlias = tuple[tuple[UnitData, ...], ...]

class PropertiesData:
    class ZoneSetting(StrEnum):
        StaffOnly = "staffOnly"
        Darkness = "darkness"
        DarknessInstant = "darknessIsInstant"
        LevelEnder = "levelEnder"
        Disco = "disco"
        CustomId = "customId"

    class ZoneData:
        def __init__(self, values: Iterable[tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]] = []) -> None:
            self.zones: list[tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]] = [(v[0].copy(), v[1].copy()) for v in values]

        def __getitem__(self, index: int) -> tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]:
            return self.zones[index]

        def __setitem__(self, index: int, value: tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]):
            self.zones[index] = value

        def __len__(self) -> int:
            return len(self.zones)

        def RemoveCollidePoint(self, mouse_pos: tuple[int, int]) -> None:
            mouse_pos_scaled = (int(mouse_pos[0] / scalesize + scroll[0]), int(mouse_pos[1] / scalesize + scroll[1]))
            for zone in reversed(self.zones):
                if zone[0].collidepoint(mouse_pos_scaled):
                    self.zones.remove(zone)
                    return

        @staticmethod
        def NewDragRect():
            assert Drag.Rect != None, "NewDragRect from null!"
            PropertiesData.Zones.zones.append((pygame.Rect(Drag.Rect.left, Drag.Rect.top, Drag.Rect.width, Drag.Rect.height), {}))

            assert(undo is not None)
            undo.register_zone_new()

        @staticmethod
        def UpdateDragRect():
            if len(PropertiesData.Zones.zones) < 1:
                return
            assert Drag.Rect != None, "UpdateDragRect from null!"
            PropertiesData.Zones.zones[-1] = (pygame.Rect(Drag.Rect.left, Drag.Rect.top, Drag.Rect.width, Drag.Rect.height), PropertiesData.Zones.zones[-1][1])

            assert(undo is not None)
            undo.register_zone_update()

        def _returnCorrectZone(self, zoneRect: pygame.Rect) -> Optional[dict[PropertiesData.ZoneSetting, str | int | float | bool]]:
            for zone in self.zones:
                if zone[0].x == zoneRect.x and zone[0].y == zoneRect.y and zone[0].width == zoneRect.width and zone[0].height == zoneRect.height:
                    return zone[1]
            return None

        def SetSetting(self, zoneRect: pygame.Rect, setting: PropertiesData.ZoneSetting, value: Union[str, int, float, bool]):
            zone = self._returnCorrectZone(zoneRect)
            if zone == None:
                KDS.Logging.warning(f"No zone matching {zoneRect} found!", consoleVisible=True)
                return
            zone[setting] = value

            assert(undo is not None)
            undo.register_zone_properties_update()

        def RemoveSetting(self, zoneRect: pygame.Rect, setting: PropertiesData.ZoneSetting):
            zone = self._returnCorrectZone(zoneRect)
            if zone == None:
                KDS.Logging.warning(f"No zone matching {zoneRect} found!", consoleVisible=True)
                return
            if setting in zone:
                zone.pop(setting)

            assert(undo is not None)
            undo.register_zone_properties_update()

    Zones = ZoneData()

    def __init__(self, parent: UnitData) -> None:
        self.parent: Final[UnitData] = parent
        self._values: dict[UnitType, dict[str, Union[str, int, float, bool]]] = {}

    @property
    def values(self) -> dict[UnitType, dict[str, Union[str, int, float, bool]]]:
        return self._values

    def __eq__(self, other) -> bool:
        """ == operator """
        if isinstance(other, PropertiesData):
            return self.values == other.values # Won't check parents
        return False

    def __ne__(self, other) -> bool:
        """ != operator """
        return not self.__eq__(other)

    def Set(self, undo: ChangeUndoRecord, _type: UnitType, key: str, value: Union[str, int, float, bool]) -> None:
        """Add value or override if exists."""

        undo.record_before(self)

        if _type not in self.values:
            self.values[_type] = {}
        self.values[_type][key] = value

        undo.record_after(self)

    def SetAll(self, undo: ChangeUndoRecord | None, data: dict[UnitType, dict[str, Union[str, int, float, bool]]], *, undo_can_be_none: bool = False):
        """Override all values and remove any unreferenced values."""

        if not undo_can_be_none and undo is None:
            raise ValueError("Undo cannot be None. If you are ABSOLUTELY sure that it can, please set undo_can_be_none=True")

        if undo is not None:
            undo.record_before(self)
        self._values = {k: {ik: iv for ik, iv in v.items()} for k, v in data.items()}
        if undo is not None:
            undo.record_after(self)

    def Remove(self, undo: ChangeUndoRecord, _type: UnitType, key: str) -> None:
        """Removes the specified key in type if found.

        Args:
            _type (UnitType): The type specifying what the key controls.
            key (str): The key to remove.
        """

        if _type in self.values and key in self.values[_type]:
            undo.record_before(self)

            self.values[_type].pop(key)
            if len(self.values[_type]) < 1:
                self.values.pop(_type)

            undo.record_after(self)


    def Get(self, _type: UnitType, key: str, default: Optional[str | int | float | bool]) -> Optional[str | int | float | bool]:
        if _type in self.values:
            return self.values[_type].get(key, default)
        else:
            return default

    def GetAll(self) -> dict[UnitType, dict[str, Union[str, int, float, bool]]]:
        return {k: v.copy() for k, v in self.values.items()}

    def RemoveUnused(self, undo: ChangeUndoRecord | None, *, undo_can_be_none: bool = False):
        if not undo_can_be_none and undo is None:
            raise ValueError("Undo cannot be None. If you are ABSOLUTELY sure that it can, please set undo_can_be_none=True")

        if undo is not None:
            undo.record_before(self)

        for _type in self.values.copy():
            if _type == UnitType.Unspecified:
                continue

            if not KDS.Linq.Any(self.parent.serials, lambda v: int(v[0]) == _type.value and int(v) != 0):
                self.values.pop(_type)

        if undo is not None:
            undo.record_after(self)

    def Copy(self, *, overrideParent: UnitData | None) -> PropertiesData:
        new = PropertiesData(overrideParent if overrideParent != None else self.parent)
        new._values = {k: {ik: iv for ik, iv in v.items()} for k, v in self.values.items()} #deepcopy replacement. Some values are not copied, because they are single-instance variables.
        return new

    def __str__(self) -> str:
        p: Final = self.Copy(overrideParent=None)
        p.RemoveUnused(undo=None, undo_can_be_none=True)
        return PropertiesData._toString(p)

    @staticmethod
    def _toString(p: PropertiesData) -> str:
        if KDS.Linq.All(p.values.values(), lambda v: len(v) < 1): # The dictionary should be empty if there are no values, but let's check just in case.
            return ""

        key = f"{p.parent.pos[0]}-{p.parent.pos[1]}"
        value = json.dumps(p.values, separators=(',', ':')) # Separators ensure that there are no useless spaces in the file.
        return f"\"{key}\":{value}" # Puts key in quotes so that it is valid JSON

    @staticmethod
    def _zonesSerializer():
        parsableZones: dict[str, dict[str, Union[str, int, float, bool]]] = {}
        for rect, data in PropertiesData.Zones:
            parsableZones[f"{rect.x}-{rect.y}-{rect.width}-{rect.height}"] = {k.value: v for k, v in data.items()}
        return f"\"zones\":{json.dumps(parsableZones, separators=(',', ':'))}"

    @staticmethod
    def _zonesDeserializer(data: dict[str, dict[str, Union[str, int, float, bool]]]) -> list[tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]]:
        parsedZones: list[tuple[pygame.Rect, dict[PropertiesData.ZoneSetting, Union[str, int, float, bool]]]] = []
        for rect, d in data.items():
            x, y, w, h = rect.split("-")
            parsedZones.append((pygame.Rect(int(x), int(y), int(w), int(h)), {PropertiesData.ZoneSetting(t): v for t, v in d.items()}))
        return parsedZones

    @staticmethod
    def Serialize(grid: Sequence[Sequence[UnitData]]) -> str:
        strings: list[str] = []
        for row in grid:
            for unit in row:
                pString = str(unit.properties)
                if len(pString) > 0:
                    strings.append(pString)
        if len(PropertiesData.Zones) > 0:
            strings.append(PropertiesData._zonesSerializer())
        if len(strings) < 1: # If there is nothing to save, return empty.
            return ""
        result = "{\n" + "".join(f"{s},\n" for s in strings).removesuffix(",\n") + "\n}"
        return result

    @staticmethod
    def Deserialize(jsonString: str, grid: Sequence[Sequence[UnitData]], *, load_zones: bool = True) -> None:
        if len(jsonString) < 1 or jsonString.isspace():
            return
        deserialized: dict[str, dict[str, dict[str, Union[str, int, float, bool]]]] = json.loads(jsonString)
        for row in grid:
            for unit in row:
                key = f"{unit.pos[0]}-{unit.pos[1]}"
                if key in deserialized:
                    toSet = deserialized[key]
                    if not isinstance(toSet, dict): # pyright: ignore [reportUnnecessaryIsInstance]
                        KDS.Logging.AutoError(f"Invalid value type occured during deserialization. Key for data: {key}")
                        continue
                    unitProp = PropertiesData(unit)
                    unitProp._values = {UnitType(int(k)): v for k, v in toSet.items()}
                    unit._properties = unitProp

        if load_zones:
            PropertiesData.Zones = PropertiesData.ZoneData(PropertiesData._zonesDeserializer(deserialized["zones"] if "zones" in deserialized else {}))


class BrushShape(IntEnum):
    circle = 0
    square = 1

    tall = 2 # this value is not used as this brush shape was deemed unpractical
    wide = 3 # this value is not used as this brush shape was deemed unpractical

    @staticmethod
    def next_value(val: BrushShape) -> BrushShape:
        values: tuple[BrushShape, ...] = (BrushShape.circle, BrushShape.square)
        i: int = values.index(val)
        return values[(i + 1) % len(values)]

class BrushStyles(IntFlag):
    default = 0
    pick_brush = 1 << 0 # 1

class BrushData:
    class _CurrentPositions(NamedTuple):
        all_positions: frozenset[tuple[int, int]]
        selected_positions: frozenset[tuple[int, int]]
        modifiable_units: tuple[UnitData, ...]
        was_created_by_modify: bool

    def __init__(self) -> None:
        self._brush: str = UnitData.EMPTY
        self._properties: Optional[dict[UnitType, dict[str, Union[str, int, float, bool]]]] = None

        self._pos: tuple[int, int] | None = None
        self._previous_positions: frozenset[tuple[int, int]] | None = None
        self._current_positions: BrushData._CurrentPositions | None = None

        self.__random_rmv_count: int = 0
        self._random_rmv_template: frozenset[tuple[int, int]] | None = None

        self.__size: int = 0
        """The radius of the circle, or half of the width of the rectangle."""
        self.__shape: BrushShape = BrushShape.circle
        self.styles: BrushStyles = BrushStyles.default

    @property
    def size(self) -> int:
        return self.__size
    @size.setter
    def size(self, s: int) -> None:
        self.__size = KDS.Math.Clamp(s, 0, 10)

        self._clamp_random_positions_count()
        self._current_positions = None

    @property
    def shape(self) -> BrushShape:
        return self.__shape
    @shape.setter
    def shape(self, value: BrushShape) -> None:
        self.__shape = value

        self._clamp_random_positions_count()
        self._current_positions = None

    @property
    def random_rmv_count(self) -> int:
        return self.__random_rmv_count
    @random_rmv_count.setter
    def random_rmv_count(self, value: int) -> None:
        self.__random_rmv_count = value
        self._clamp_random_positions_count()

        if self._current_positions is not None:
            self._random_rmv_template = self._current_positions.selected_positions
        self._current_positions = None

    def _clamp_random_positions_count(self):
        position_count: int = len(tuple(self.IterAllPositions()))
        self.__random_rmv_count = KDS.Math.Clamp(self.__random_rmv_count, 0, position_count - 1)

    @property
    def currentMaterial(self) -> str:
        return self._brush

    @property
    def hasProperties(self) -> bool:
        return self._properties is not None

    def SetBrush(self, brush: str = UnitData.EMPTY, properties: Optional[dict[UnitType, dict[str, Union[str, int, float, bool]]]] = None):
        if brush != self._brush:
            self._brush = brush
            self._current_positions = None

        self._properties = None
        if not self.IsEmpty and properties != None:
            correctType = KDS.Linq.FirstOrNone(properties, lambda t: t.value == int(brush[0]))
            if correctType != None:
                propValues = properties[correctType]
                self._properties = {correctType: {ik: iv for ik, iv in propValues.items()}}


    def PickBrush(self, unit: UnitData, *, get_properties: bool):
        brush = KDS.Linq.FirstOrNone(unit.filledSerials, lambda s: s != self._brush)

        props: Optional[dict[UnitType, dict[str, Union[str, int, float, bool]]]] = None
        if brush is None:
            brush = unit.getSerial(0)
        elif brush[0] == "3":
            tmpProp = unit.properties.Get(UnitType.Teleport, "identifier", 1)
            if isinstance(tmpProp, int):
                props = {UnitType.Teleport:{"identifier":tmpProp}}

        if get_properties:
            props = unit.properties.GetAll()

        self.SetBrush(brush, props)

    def IterAllPositions(self) -> Iterable[tuple[int, int]]:
        if self.size == 0:
            return self._IterSingle()
        else:
            if self.shape == BrushShape.circle:
                return self._IterCircle()
            else:
                return self._IterSquare()


    def IterAllUnits(self, grid: GridType) -> Iterable[UnitData]:
        for position in self.IterAllPositions():
            unit = self.__TryGetUnit(position, grid)
            if unit is not None:
                yield unit

    def __TakeRandom(self, all_positions: frozenset[tuple[int, int]], selected: frozenset[tuple[int, int]], grid: GridType) -> frozenset[tuple[int, int]]:
        def unit_matches(pos: tuple[int, int]) -> bool:
            unit: UnitData | None = self.__TryGetUnit(pos, grid)
            return unit is not None and self._brush in unit.filledSerials

        if self.random_rmv_count < 1:
            return selected

        target_count: int = len(all_positions) - self.random_rmv_count
        count: int = KDS.Linq.Count(all_positions, lambda nm: unit_matches(nm))

        output: set[tuple[int, int]] = set()
        if self._random_rmv_template is not None:
            output.update(self._random_rmv_template)
            self._random_rmv_template = None
        count += len(output)

        available_slots: list[tuple[int, int]] = list(selected.difference(output))
        while count < target_count:
            assert(len(available_slots) > 0)
            random_index: int = random.randrange(len(available_slots))
            random_pos: tuple[int, int] = available_slots.pop(random_index)
            assert random_pos not in output
            output.add(random_pos)
            count += 1

        while count > target_count and len(output) > 0:
            # SLOW
            # but this condition is rarely true (only when resizing brush downwards)
            # so I'm not too conserned with it...
            output_tuple: tuple[tuple[int, int], ...] = tuple(output)
            random_pos: tuple[int, int] = random.choice(output_tuple)
            output.remove(random_pos)
            count -= 1

        # len might be over as the grid might already contain more tiles of the current brush type
        # assert((len(output) + ) >= target_count)
        # do not check as len(output) can also be less since len(all_positions) > len(selected)
        return frozenset(output)

    def __UpdateCurrentPositions(self, *, will_modify: bool) -> _CurrentPositions:
        assert(self._current_positions is not None)
        output: BrushData._CurrentPositions
        reset_modifiable_units: bool = will_modify and len(self._current_positions.modifiable_units) > 0

        # if current positions were created by modify, we shouldn't modify the same tiles twice so we replace modifiable before returning output
        if self._current_positions.was_created_by_modify:
            if reset_modifiable_units:
                self._current_positions = self._current_positions._replace(modifiable_units=frozenset())
            output = self._current_positions
        # otherwise the positions haven't yet been modified so we should return the original modifiable_units
        else:
            output = self._current_positions
            if reset_modifiable_units:
                self._current_positions = self._current_positions._replace(modifiable_units=frozenset())

        return output


    def _UpdateUnits(self, grid: GridType, *, will_modify: bool = True) -> _CurrentPositions:
        all_positions: frozenset[tuple[int, int]] = frozenset(self.IterAllPositions())

        if self._current_positions is not None:
            return self.__UpdateCurrentPositions(will_modify=will_modify)

        selected: frozenset[tuple[int, int]]
        if self._previous_positions is None:
            selected = all_positions
        else:
            selected = all_positions.difference(self._previous_positions)

        selected = self.__TakeRandom(all_positions=all_positions, selected=selected, grid=grid)
        self._current_positions = BrushData._CurrentPositions(
            all_positions=all_positions,
            selected_positions=selected,
            modifiable_units=tuple(unit for unit in (self.__TryGetUnit(s, grid) for s in selected) if unit is not None),
            was_created_by_modify=will_modify
        )

        return self._current_positions

    def _IterSingle(self) -> Iterable[tuple[int, int]]:
        if self._pos is None:
            raise ValueError("No position set.")
        return (self._pos,)

    def _GetSquareRect(self) -> pygame.Rect:
        if self._pos is None:
            raise ValueError("No position set.")
        pos: tuple[int, int] = self._pos

        left: int = pos[0]
        right: int = pos[0] + 1
        top: int = pos[1]
        bottom: int = pos[1] + 1
        if self.shape in (BrushShape.square, BrushShape.wide):
            left = pos[0] - self.size
            right = pos[0] + self.size + 1
        if self.shape in (BrushShape.square, BrushShape.tall):
            top = pos[1] - self.size
            bottom = pos[1] + self.size + 1

        return pygame.Rect(left, top, right - left, bottom - top)

    def _IterSquare(self) -> Iterable[tuple[int, int]]:
        if self._pos is None:
            raise ValueError("No position set.")

        rect: pygame.Rect = self._GetSquareRect()
        for x in range(rect.left, rect.right):
            for y in range(rect.top, rect.bottom):
                yield (x, y)

    @staticmethod
    def _IterCirclePoints(radius: int) -> Iterable[tuple[int, int]]:
        """Points need to be transformed into local space as the returned points' origin is (0, 0)"""
        # https://stackoverflow.com/questions/15856411/finding-all-the-points-within-a-circle-in-2d-space/15856549#15856549

        for x in range(radius + 1):
            for y in range(radius + 1):
                if (x*x + y*y) <= radius*radius:
                    yield (x, y) # Quadrant IV
                    if y != 0:
                        yield (x, -y) # Quadrant I
                    if x != 0:
                        yield (-x, y) # Quadrant II
                    if x != 0 and y != 0:
                        yield (-x, -y) # Quadrant III

    def _IterCircle(self) -> Iterable[tuple[int, int]]:
        if self._pos is None:
            raise ValueError("No position set.")
        pos: tuple[int, int] = self._pos

        for p in self._IterCirclePoints(radius=self.size):
            yield (p[0] + pos[0], p[1] + pos[1])

    @staticmethod
    def __TryGetUnit(pos: tuple[int, int], grid: GridType) -> UnitData | None:
        x, y = pos
        if y < 0:
            return None
        if y >= len(grid):
            return None
        row = grid[y]
        if x < 0:
            return None
        if x >= len(row):
            return None
        return row[x]

    def Set(self, undo: ChangeUndoRecord, grid: GridType):
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.setSerial(undo, self._brush)
            if self._properties is not None:
                unit.setProperties(undo, self._properties)
            unit.properties.RemoveUnused(undo)

    def Add(self, undo: ChangeUndoRecord, grid: GridType):
        """Add to end"""
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.addSerial(undo, self._brush)
            if self._properties is not None:
                unit.addProperties(undo, self._properties)
            unit.properties.RemoveUnused(undo)

    def Insert(self, undo: ChangeUndoRecord, grid: GridType):
        """Add to start"""
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.insertSerial(undo, self._brush)
            if self._properties is not None:
                unit.addProperties(undo, self._properties)
            unit.properties.RemoveUnused(undo)

    def Reset(self, undo: ChangeUndoRecord, grid: GridType):
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.resetSerial(undo)
            unit.properties.RemoveUnused(undo)

    def Remove(self, undo: ChangeUndoRecord, grid: GridType):
        """Remove from end"""
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.removeSerial(undo)
            unit.properties.RemoveUnused(undo)

    def Purge(self, undo: ChangeUndoRecord, grid: GridType):
        """Remove from start"""
        for unit in self._UpdateUnits(grid=grid).modifiable_units:
            unit.removeSerialFromStart(undo)
            unit.properties.RemoveUnused(undo)

    def RenderUpdate(self, position: tuple[int, int] | None, grid: GridType, mouse_pressed: tuple[bool, ...], surface: pygame.Surface | None):
        if position != self._pos:
            self._pos = position

            if self._current_positions is not None:
                self._previous_positions = self._current_positions.all_positions
                self._current_positions = None
            else:
                self._previous_positions = None

        if not mouse_pressed[0] and not mouse_pressed[2]:
            self._previous_positions = None
            # self._current_positions = None
            # do not modify current positions so that the positions rendered match what is placed
            # we reset this to None when the position changes

        if surface is not None:
            self._Render(surface=surface)

            if not self.IsEmpty:
                textureData = Textures.GetData(self._brush)

                tex: pygame.Surface = textureData.scaledTexture.copy()
                tex = tex.subsurface((max(tex.width - scalesize, 0), max(tex.height - scalesize, 0), min(scalesize, tex.width), min(scalesize, tex.height)))
                tex.set_alpha(32)

                surface.fblits(((tex, ((pos[0] - scroll[0]) * scalesize, (pos[1] - scroll[1]) * scalesize)) for pos in self._UpdateUnits(grid, will_modify=False).selected_positions))

            if BrushStyles.pick_brush in self.styles:
                self._RenderSingle(surface=surface, color=(255, 0, 0))

    def _Render(self, surface: pygame.Surface):
        if self.size == 0:
            self._RenderSingle(surface=surface)
        else:
            if self.shape == BrushShape.circle:
                self._RenderCircle(surface=surface)
            else:
                self._RenderSquare(surface=surface)

    def _RenderSingle(self, surface: pygame.Surface, *, color: tuple[int, int, int] = (20, 20, 20)) -> None:
        if self._pos is None:
            raise ValueError("No position set.")
        pos: tuple[int, int] = self._pos

        pygame.draw.rect(
            surface=surface,
            color=color,
            rect=((pos[0] - scroll[0]) * scalesize, (pos[1] - scroll[1]) * scalesize, scalesize, scalesize),
            width=2
        )

    def _RenderSquare(self, surface: pygame.Surface) -> None:
        rect: pygame.Rect = self._GetSquareRect()

        pygame.draw.rect(
            surface=surface,
            color=(20, 20, 20),
            rect=((rect.left - scroll[0]) * scalesize, (rect.top - scroll[1]) * scalesize, rect.width * scalesize, rect.height * scalesize),
            width=2
        )

    def _RenderCircle(self, surface: pygame.Surface) -> None:
        if self._pos is None:
            raise ValueError("No position set.")

        offset: tuple[int, int] = self._pos
        radius: int = self.size

        points: list[tuple[int, int]] = []

        # generate points
        for x in range(radius + 1):
            for y in range(radius, -1, -1):
                if (x*x + y*y) <= radius*radius:
                    points.append((x, y))
                    break

        # there are some unnecessary points but I'm too lazy to cull them
        # it shouldn't be that much of a performance issue...

        # add inner corners
        inner_corner_index_offset: int = 0
        for i in range(1, len(points)):
            i += inner_corner_index_offset

            p1 = points[i - 1]
            p2 = points[i]
            points.insert(i, (p1[0], p2[1]))
            inner_corner_index_offset += 1

        # mirror vertically
        vertical_mirror_length: int = len(points)
        for i in range(vertical_mirror_length - 1, -1, -1):
            p: tuple[int, int] = points[i]
            points.append((p[0], -p[1] - 1))

        # mirror horizontally
        horizontal_mirror_length: int = len(points)
        for i in range(horizontal_mirror_length - 1, -1, -1):
            p: tuple[int, int] = points[i]
            points.append((-p[0] - 1, p[1]))

        # transform into screenspace
        for i in range(len(points)):
            p: tuple[int, int] = points[i]
            points[i] = (
                (p[0] + 1 + offset[0] - scroll[0]) * scalesize,
                (p[1] + 1 + offset[1] - scroll[1]) * scalesize
            )

        pygame.draw.lines(
            surface=surface,
            color=(20, 20, 20),
            points=points,
            closed=True,
            width=2
        )


    @property
    def IsEmpty(self):
        return self._brush == UnitData.EMPTY
brush = BrushData()

class DragMode(IntEnum):
    Default = 0
    Zone = 1

@dataclass
class DragStyle:
    color: tuple[int, int, int]
    alpha: int
    border_width: int

class DragData:
    DEFAULT_STYLE = DragStyle(KDS.Colors.White, 64, 5)

    def __init__(self) -> None:
        self.Rect: Optional[pygame.Rect] = None
        self.Mode: DragMode = DragMode.Default

        self.startPos: Optional[tuple[int, int]] = None
        self.c_onDragStart: dict[DragMode, list[Callable[[], None]]] = {m: [] for m in DragMode}
        self.c_onDragUpdate: dict[DragMode, list[Callable[[], None]]] = {m: [] for m in DragMode}
        self.c_onDragEnd: dict[DragMode, list[Callable[[], None]]] = {m: [] for m in DragMode}
        self.c_onDragClear: dict[DragMode, list[Callable[[], None]]] = {m: [] for m in DragMode}

        self.lastL = False

    def SelectCustom(self, rect: Optional[pygame.Rect]):
        if rect != None:
            self.Rect = rect.copy()
            [onStart() for onStart in self.c_onDragStart[self.Mode]]
        else:
            self.clear()

    def clear(self):
        self.Rect = None
        self.startPos = None
        [onClear() for onClear in self.c_onDragClear[self.Mode]]

    def render(self, style: DragStyle, surface: pygame.Surface, scroll: list[int]):
        if self.Rect == None:
            return

        selectDrawRect = pygame.Rect((self.Rect.x - scroll[0]) * scalesize, (self.Rect.y - scroll[1]) * scalesize, self.Rect.width * scalesize, self.Rect.height * scalesize)
        selectDraw = pygame.Surface(selectDrawRect.size)
        selectDraw.fill(style.color)
        if style.border_width > 0:
            pygame.draw.rect(selectDraw, KDS.Colors.Black, (0, 0, *selectDraw.get_size()), KDS.Math.CeilToInt(style.border_width / 34 * scalesize))
        selectDraw.set_alpha(style.alpha)
        surface.blit(selectDraw, (selectDrawRect.x, selectDrawRect.y))

        wRnd = harbinger_font.render(str(self.Rect.width), True, KDS.Colors.CloudWhite)
        surface.blit(wRnd, (selectDrawRect.x + selectDrawRect.width // 2 - wRnd.get_width() // 2, selectDrawRect.y - 10 - wRnd.get_height()))
        hRnd = harbinger_font.render(str(self.Rect.height), True, KDS.Colors.CloudWhite)
        surface.blit(hRnd, (selectDrawRect.x - 10 - hRnd.get_width(), selectDrawRect.y + selectDrawRect.height // 2 - hRnd.get_height() // 2))

    def update(self, mouse_pos: tuple[int, int], left_down: bool, right_down: bool, keys_down: pygame.key.ScancodeWrapper, *, allow_drag: bool) -> bool:
        if not brush.IsEmpty:
            if self.Rect is not None:
                self.clear()
            return False
        if right_down:
            if self.Rect is not None:
                self.clear()
                return True
            else:
                return False
        if self.lastL != left_down:
            self.lastL = left_down
            if left_down:
                self.startPos = None
            else:
                [onEnd() for onEnd in self.c_onDragEnd[self.Mode]]
        if not left_down:
            return False
        if keys_down[K_c]:
            return False

        if not allow_drag:
            return False

        startCallFlag = False
        if self.startPos == None:
            self.startPos = (int((mouse_pos[0] + scroll[0] * scalesize) / scalesize), int((mouse_pos[1] + scroll[1] * scalesize) / scalesize))
            startCallFlag = True

        mouse_pos_scaled = (int(mouse_pos[0] / scalesize + scroll[0]), int(mouse_pos[1] / scalesize + scroll[1]))
        x = min(mouse_pos_scaled[0], self.startPos[0])
        y = min(mouse_pos_scaled[1], self.startPos[1])
        w = abs(self.startPos[0] - mouse_pos_scaled[0]) + 1
        h = abs(self.startPos[1] - mouse_pos_scaled[1]) + 1
        self.Rect = pygame.Rect(x, y, w, h)
        if startCallFlag:
            [onStart() for onStart in self.c_onDragStart[self.Mode]]
        else:
            [onUpdate() for onUpdate in self.c_onDragUpdate[self.Mode]]

        return False

    def registerCalls(self, mode: DragMode, onDragStart: Optional[Callable[[], None]], onDragUpdate: Optional[Callable[[], None]], onDragEnd: Optional[Callable[[], None]], onDragClear: Optional[Callable[[], None]]):
        if onDragStart != None:
            self.c_onDragStart[mode].append(onDragStart)
        if onDragUpdate != None:
            self.c_onDragUpdate[mode].append(onDragUpdate)
        if onDragEnd != None:
            self.c_onDragEnd[mode].append(onDragEnd)
        if onDragClear != None:
            self.c_onDragClear[mode].append(onDragClear)

Drag: Final = DragData()
Drag.registerCalls(DragMode.Zone, PropertiesData.ZoneData.NewDragRect, PropertiesData.ZoneData.UpdateDragRect, PropertiesData.ZoneData.UpdateDragRect, None)

def loadGrid(size: tuple[int, int]) -> GridType:
    rlist: list[tuple[UnitData, ...]] = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(UnitData((x, y)))
        rlist.append(tuple(row))
    return tuple(rlist)

def resizeGrid(size: tuple[int, int]) -> None:
    global grid, gridSize

    resize_undo: Final = ResizeUndoRecord(grid)

    grid_size = (len(grid[0]), len(grid))
    assert(grid_size == gridSize)

    rGrid: list[list[UnitData]] = list(list(row) for row in grid)

    size_difference = (size[0] - grid_size[0], size[1] - grid_size[1])
    if size_difference[1] > 0:
        for y in range(grid_size[1], size[1]):
            row = []
            for x in range(grid_size[0]):
                row.append(UnitData((x, y)))
            rGrid.append(row)
    else:
        for y in range(abs(size_difference[1])):
            rGrid.pop()
    if size_difference[0] > 0:
        for y in range(len(rGrid)):
            row = rGrid[y]
            while len(row) < size[0]:
                row.append(UnitData(((len(row)), y)))
    else:
        for row in rGrid:
            while len(row) > size[0]:
                row.pop()

    grid = tuple(tuple(row) for row in rGrid)
    gridSize = size

    resize_undo.resized_grid = grid
    assert(undo is not None)
    undo.register(resize_undo)

def unsafeAddGridTopLeft(size: tuple[int, int]) -> None:
    global grid, gridSize, undo

    # resize_undo: Final = ResizeUndoRecord(grid)

    original_grid_size: tuple[int, int] = (len(grid[0]), len(grid))
    assert(original_grid_size == gridSize)

    size_diff: tuple[int, int] = (size[0] - original_grid_size[0], size[1] - original_grid_size[1])
    if size[0] < original_grid_size[0] or size[1] < original_grid_size[1]:
        raise ValueError("This method cannot reduce grid size. Use unsafeRemoveGridTopLeft instead.")

    rGrid: list[list[UnitData]] = list(list(row) for row in grid)

    # add rows
    while len(rGrid) < size[1]:
        for row in rGrid:
            for unit in row:
                unit.pos = (unit.pos[0], unit.pos[1] + 1)
        insert_row: list[UnitData] = [UnitData((x, 0)) for x in range(original_grid_size[0])]
        rGrid.insert(0, insert_row)

    # add columns
    while len(rGrid[0]) < size[0]:
        for y, row in enumerate(rGrid):
            for unit in row:
                unit.pos = (unit.pos[0] + 1, unit.pos[1])
            row.insert(0, (UnitData((0, y))))

    for zone_i in range(len(PropertiesData.Zones.zones)):
        # modify element in-place
        zone_rect: pygame.Rect = PropertiesData.Zones.zones[zone_i][0]
        zone_rect.x += size_diff[0]
        zone_rect.y += size_diff[1]

    grid = tuple(tuple(row) for row in rGrid)
    gridSize = size

    # resize_undo.resized_grid = grid
    # assert(undo is not None)
    # undo.register(resize_undo)
    undo = None # resize didn't work as we modify all of the tiles and zones as well...
    undo = Undo()

def unsafeRemoveGridTopLeft(size: tuple[int, int]) -> None:
    global grid, gridSize, undo

    # resize_undo: Final = ResizeUndoRecord(grid)

    original_grid_size: tuple[int, int] = (len(grid[0]), len(grid))
    assert(original_grid_size == gridSize)

    size_diff: tuple[int, int] = (size[0] - original_grid_size[0], size[1] - original_grid_size[1])
    if size[0] > original_grid_size[0] or size[1] > original_grid_size[1]:
        raise ValueError("This method cannot increase grid size. Use unsafeAddGridTopLeft instead.")

    rGrid: list[list[UnitData]] = list(list(row) for row in grid)

    # remove rows
    while len(rGrid) > size[1]:
        for row in rGrid:
            for unit in row:
                unit.pos = (unit.pos[0], unit.pos[1] - 1)
        rGrid.pop(0)

    # remove columns
    while len(rGrid[0]) > size[0]:
        for row in rGrid:
            for unit in row:
                unit.pos = (unit.pos[0] - 1, unit.pos[1])
            row.pop(0)

    for zone_i in range(len(PropertiesData.Zones.zones)):
        # modify element in-place
        zone_rect: pygame.Rect = PropertiesData.Zones.zones[zone_i][0]
        zone_rect.x += size_diff[0]
        zone_rect.y += size_diff[1]

    grid = tuple(tuple(row) for row in rGrid)
    gridSize = size

    # resize_undo.resized_grid = grid
    # assert(undo is not None)
    # undo.register(resize_undo)
    undo = None # resize didn't work as we modify all of the tiles and zones as well...
    undo = Undo()

def generateMapString(grid: GridType) -> str:
    outputString = ''
    for row in grid:
        for unit in row:
            outputString += str(unit) + " / "
        outputString = outputString.removesuffix(" / ") + "\n"
    return outputString

def saveMap(grid: GridType, name: str):
    #region Map
    with open(name, 'w', encoding="utf-8") as f:
        f.write(generateMapString(grid))
    #endregion
    #region Tile Props
    propertiesPath = os.path.join(os.path.dirname(name), "properties.kdf")
    propertiesString = PropertiesData.Serialize(grid)
    saveProps = False

    if len(propertiesString) > 0:
        if os.path.isfile(propertiesPath):
            saveProps = True
        else:
            while not saveProps:
                if KDS.System.MessageBox.Show("No Properties File!", "Your project does not have a properties file even though it is required. Do you want to add one?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
                    saveProps = True
                    break
                if KDS.System.MessageBox.Show("Properties Ignored", "Properties generation ignored. You might lose level data.", KDS.System.MessageBox.Buttons.OKCANCEL, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.OK:
                    break
    elif os.path.isfile(propertiesPath):
        if KDS.System.MessageBox.Show("Unused Properties!", "We have detected a properties file in your project, but this file is no longer required. Do you want to remove it?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
            os.remove(propertiesPath)
        else:
            saveProps = True

    if saveProps:
        with open(propertiesPath, "w", encoding="utf-8") as f:
            f.write(propertiesString)
    #endregion
    assert(undo is not None)
    undo.register_was_saved()

def saveMapName():
    global currentSaveName, grid
    savePath = filedialog.asksaveasfilename(initialfile="level", defaultextension=".dat", filetypes=(("Data file", "*.dat"), ("All files", "*.*")), title="Save Map")
    if len(savePath) > 0:
        currentSaveName = savePath
        saveMap(grid, currentSaveName)

def loadLevelProp(dirPath: str):
    LevelPropData.ShowKoponen = False
    LevelPropData.ShowPlayer = False
    lPath = os.path.join(dirPath, "levelprop.kdf")
    if not os.path.isfile(lPath):
        return
    with open(lPath, "r", encoding="utf-8") as f:
        lpData: dict[str, dict[str, Any]] = json.loads(f.read())
        if "Entities" not in lpData:
            return
        entityData = lpData["Entities"]
        if "Koponen" in entityData and "startPos" in entityData["Koponen"]:
            tmpKoponenData: dict[str, Any] = entityData["Koponen"]
            tmpPos = tmpKoponenData["startPos"]
            tmpEnabled = tmpKoponenData.get("enabled", False) # if not found, Koponen is disabled.
            LevelPropData.KoponenPos = (tmpPos[0], tmpPos[1])
            LevelPropData.ShowKoponen = tmpEnabled
        if "Player" in entityData:
            playerData = entityData["Player"]
            if "startPos" in playerData:
                tmpPos = playerData["startPos"]
                LevelPropData.PlayerPos = (tmpPos[0], tmpPos[1])
                LevelPropData.ShowPlayer = True
            if "spawnInverted" in playerData:
                spawnInverted = playerData["spawnInverted"]
                if not isinstance(spawnInverted, bool):
                    KDS.Logging.AutoError(f"Unexpected type of spawnInverted. Expected: {bool.__name__}, Got: {type(spawnInverted).__name__}")
                LevelPropData.PlayerFlipped = playerData["spawnInverted"] == True # Will default to false if spawnInverted is not a bool

def internalLoadMap(path: str, *, modifyGlobals: bool = True) -> tuple[GridType, tuple[int, int]]:
    global display

    with open(path, 'r') as f:
        wholeContents = f.read()
        contents = wholeContents.splitlines()
        while len(contents) > 0 and (len(contents[-1]) < 1 or contents[-1].isspace()):
            contents = contents[:-1]

        if len(contents) < 0:
            KDS.Logging.AutoError("Map contents length is less than one!")

    maxWStr = max(contents, key=lambda c: len(c.split("/")))
    maxW = len(maxWStr.split("/"))
    temporaryGridSize = (maxW, len(contents))
    temporaryGrid = loadGrid(temporaryGridSize)

    for row, rRow in zip(contents, temporaryGrid):
        for unit, rUnit in zip(row.split("/"), rRow):
            unit = unit.strip(" ")
            #region Fixing Broken Serials
            while len(unit) < len(UnitData.EMPTYSERIAL):
                if not unit.endswith("0000"):
                    unit += "0"
                else:
                    unit += " "
            while len(unit) > len(UnitData.EMPTYSERIAL):
                if unit[-1] not in (' ', '0'):
                    KDS.Logging.warning(f"Broken serial fix will truncate out a non-zero serial: '{unit}'", consoleVisible=True)
                unit = unit[:-1]
            if KDS.Linq.Any(unit.split(" "), lambda n: len(n) != len(UnitData.EMPTY)):
                KDS.Logging.AutoError(f"Serial: {unit} contains a broken serial. Please fix this manually.")
            #endregion
            rUnit.overrideSerial(None, unit, undo_can_be_none=True)

    if generateMapString(temporaryGrid) != wholeContents:
        KDS.Logging.warning("Loaded map file does not match generated map file!", consoleVisible=True)

    def loadProperties(*, load_zones: bool):
        nonlocal temporaryGrid
        pPath = os.path.join(os.path.dirname(path), "properties.kdf")
        if not os.path.isfile(pPath):
            return
        with open(pPath, 'r', encoding="utf-8") as f:
            PropertiesData.Deserialize(f.read(), temporaryGrid, load_zones=load_zones)


    loadProperties(load_zones=modifyGlobals)
    if modifyGlobals:
        loadLevelProp(os.path.dirname(path))
    return temporaryGrid, temporaryGridSize

def loadMap(path: str) -> bool: # bool indicates if the map loading was succesful
    global currentSaveName, gridSize, grid, display, undo
    if len(path) < 1:
        KDS.Logging.info(f"Path \"{path}\" of map file is not valid.", True)
        return False
    if not path.endswith(".dat"):
        KDS.Logging.info(f"Map file at path \"{path}\" is not a valid type.", True)
        return False

    if UnsavedChangesInterrupt("Do you want to save them?"):
        if len(currentSaveName) < 1 or currentSaveName.isspace():
            saveMapName()
        else:
            saveMap(grid, currentSaveName)

    if not KDS.System.ISLINUX:
        KDS.Loading.Circle.Start(display)

    handle = KDS.Jobs.Schedule(internalLoadMap, path)
    while not handle.IsComplete:
        for event in pygame.event.get():
            if event.type == QUIT:
                LB_Quit()
        pygame.time.wait(1000)
    currentSaveName = path
    grid, gridSize = handle.Complete()
    undo = Undo()

    if not KDS.System.ISLINUX:
        KDS.Loading.Circle.Stop()

    return True

def openMap() -> bool: # Returns True if the operation was succesful
    global currentSaveName, gridSize, grid
    fileName: str = filedialog.askopenfilename(filetypes=(("Data file", "*.dat"), ("All files", "*.*")), title="Open Map File")
    if len(fileName) < 1:
        return False
    return loadMap(fileName)

consoleTextureNameSerials: dict[str, str] = {}
for tmpName in Textures:
    modName = tmpName.name.replace(" ", "_").lower().replace("(", "").replace(")", "")
    consoleTextureNameSerials[modName.encode("ascii", "ignore").decode("ascii")] = tmpName.serialNumber
consoleTextureCommandTree: dict[str, str] = {n: "break" for n in consoleTextureNameSerials.keys()}
commandTree: dict[str, str | dict[str, str | dict[str, str]]] = {
    "set": {
        "brush": consoleTextureCommandTree,
        **consoleTextureCommandTree,
    },
    "add": { # extend map
        "rows": "break",
        "cols": "break"
    },
    "rmv": { # shrink map
        "rows": "break",
        "cols": "break"
        # "stacks": "break"
    },
    "insert": { # extend map, insert on top/left, might break things, resets undo
        "rows": "break",
        "cols": "break"
    },
    "purge": { # shrink map, purge from top/left, might break things, resets undo
        "rows": "break",
        "cols": "break"
    },
    "flip": {
        "horizontal": "break",
        "vertical": "break"
    },
    "replace": {
        **{n: consoleTextureCommandTree for n in consoleTextureNameSerials.keys()}
    }
}
def consoleHandler(commandlist: list[str]) -> int:
    """Return 0 on success, 1 on error"""

    def get_texture(cmd: str) -> TextureHolder.TextureData | None:
        if cmd in consoleTextureNameSerials:
            return Textures.GetData(consoleTextureNameSerials[cmd])
        if cmd in Textures.serials:
            return Textures.GetData(cmd)
        return None

    global brush, grid
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if len(commandlist) < 3:
                KDS.Console.Feed.append("Invalid set command.")
                return 1

            set_brush_tex = get_texture(commandlist[2])
            if set_brush_tex is None:
                KDS.Console.Feed.append("Invalid brush.")
                return 1
            else:
                brush.SetBrush(set_brush_tex.serialNumber)
                KDS.Console.Feed.append(f"Brush set: [{set_brush_tex.serialNumber}: {set_brush_tex.name}]")
                return 0
        elif Drag.Mode == DragMode.Default and Drag.Rect != None:
            set_drag_tex = get_texture(commandlist[1])
            if set_drag_tex is None:
                KDS.Console.Feed.append("Invalid unit.")
                return 1
            else:
                Selected.Set(serialOverride=UnitData.toSerialString(set_drag_tex.serialNumber))
                Selected.Update()
                KDS.Console.Feed.append(f"Filled [{Drag.Rect.topleft}, {Drag.Rect.bottomright}] with [{set_drag_tex.serialNumber}: {set_drag_tex.name}]")
                return 0
        else:
            KDS.Console.Feed.append("Invalid set command.")
            return 1
    elif commandlist[0] in ("add", "rmv", "insert", "purge"):
        add_rows: int = 0
        add_cols: int = 0
        if commandlist[1] == "rows":
            if commandlist[2].isnumeric():
                add_rows = int(commandlist[2])
            else:
                KDS.Console.Feed.append("Row count is not a valid value.")
                return 1
        elif commandlist[1] == "cols":
            if commandlist[2].isnumeric():
                add_cols = int(commandlist[2])
            else:
                KDS.Console.Feed.append("Column count is not a valid value.")
                return 1
        else:
            KDS.Console.Feed.append(f"Invalid {commandlist[0]} command.")
            return 1

        if commandlist[0] in ("rmv", "purge"):
            add_rows = -add_rows
            add_cols = -add_cols

        if commandlist[0] in ("add", "rmv"):
            resizeGrid((gridSize[0] + add_cols, gridSize[1] + add_rows))
            if add_rows > 0:
                KDS.Console.Feed.append(f"Added {int(commandlist[2])} rows.")
            if add_cols > 0:
                KDS.Console.Feed.append(f"Added {int(commandlist[2])} columns.")
            if add_rows < 0:
                KDS.Console.Feed.append(f"Removed {int(commandlist[2])} rows.")
            if add_cols < 0:
                KDS.Console.Feed.append(f"Removed {int(commandlist[2])} columns.")
        else:
            assert(commandlist[0] in ("insert", "purge"))

            if add_rows >= 0 and add_cols >= 0:
                unsafeAddGridTopLeft((gridSize[0] + add_cols, gridSize[1] + add_rows))
            elif add_rows <= 0 and add_cols <= 0:
                unsafeRemoveGridTopLeft((gridSize[0] + add_cols, gridSize[1] + add_rows))
            else:
                raise RuntimeError("Combined insert-purge not supported.")

        return 0
    elif commandlist[0] == "flip":
        if len(commandlist) != 2 or not (Drag.Mode == DragMode.Default and Drag.Rect != None):
            KDS.Console.Feed.append("Invalid flip command.")
            return 1

        if commandlist[1] == "horizontal":
            Selected.Flip(horizontal=True)
            return 0
        elif commandlist[1] == "vertical":
            Selected.Flip(vertical=True)
            return 0
        else:
            KDS.Console.Feed.append(f"Invalid flip: '{commandlist[1]}'")
            return 1

    elif commandlist[0] == "replace":
        if len(commandlist) != 3 or not (Drag.Mode == DragMode.Default and Drag.Rect != None):
            KDS.Console.Feed.append("Invalid replace command.")
            return 1

        replace_t1 = get_texture(commandlist[1])
        if replace_t1 is None:
            KDS.Console.Feed.append("Invalid source unit.")
            return 1

        replace_t2 = get_texture(commandlist[2])
        if replace_t2 is None:
            KDS.Console.Feed.append("Invalid destination unit.")
            return 1

        Selected.Replace(replace_t1.serialNumber, replace_t2.serialNumber)
        Selected.Update()
        KDS.Console.Feed.append(f"Replaced [{Drag.Rect.topleft}, {Drag.Rect.bottomright}] instances of [{replace_t1.serialNumber}: {replace_t1.name}] with [{replace_t2.serialNumber}: {replace_t2.name}]")
        return 0
    else:
        KDS.Console.Feed.append("Invalid command.")
        return 1

def zoneConsoleHandler(commandlist: Optional[list[str]], zoneRect: pygame.Rect):
    if commandlist == None:
        return

    if len(commandlist) != 2:
        KDS.Logging.info("Invalid command.", consoleVisible=True)
        return

    command_setting: Optional[PropertiesData.ZoneSetting] = None
    for zs in PropertiesData.ZoneSetting:
        if zs.value.lower() == commandlist[0]:
            command_setting = zs
            break

    if command_setting == None:
        KDS.Logging.info(f"No property {commandlist[0]} found!", consoleVisible=True)
        return

    if commandlist[1] == "null":
        PropertiesData.Zones.RemoveSetting(zoneRect, command_setting)
        return

    if command_setting in (PropertiesData.ZoneSetting.StaffOnly, PropertiesData.ZoneSetting.LevelEnder, PropertiesData.ZoneSetting.Disco, PropertiesData.ZoneSetting.DarknessInstant):
        parsedBool = KDS.Convert.String.ToBool(commandlist[1], hideError=True)
        if parsedBool == None:
            KDS.Logging.info(f"{commandlist[1]} is not a valid bool.", consoleVisible=True)
            return
        PropertiesData.Zones.SetSetting(zoneRect, command_setting, parsedBool)
    elif command_setting == PropertiesData.ZoneSetting.Darkness:
        if not commandlist[1].isnumeric():
            KDS.Logging.info(f"{commandlist[1]} is not a valid int.", consoleVisible=True)
            return
        intDarkness = int(commandlist[1])
        if intDarkness < 0 or intDarkness > 255:
            KDS.Logging.info(f"{intDarkness} is not in the range [0 - 255] of darkness.", consoleVisible=True)
            return
        PropertiesData.Zones.SetSetting(zoneRect, command_setting, intDarkness)
    elif command_setting == PropertiesData.ZoneSetting.CustomId:
        PropertiesData.Zones.SetSetting(zoneRect, command_setting, commandlist[1])

class MaterialContainer:
    FILTER_HEIGHT: int = 40
    FILTER_PADDING_X: int = 10
    FILTER_SPACING_X: int = 10

    COLUMNS: int = 12
    SIZE: int = 70
    SPACING: tuple[int, int] = (30, 20)

    def __init__(self, datatype: str, data: Iterable[TextureHolder.TextureData]) -> None:
        self.datatype: Final[str] = datatype
        self.data: Final[tuple[TextureHolder.TextureData, ...]] = tuple(data)

        self.selector_filter: Final[dict[str | None, KDS.UI.ToggleButton]] = {}
        self.selectors: Final[list[MaterialSelector]] = []
        self.rebuild()
        self.display_size: tuple[int, int] = display_size

        self.pressed: bool = False

    @staticmethod
    def _compute_offset() -> tuple[int, int]:
        return (
            (display_size[0] - (MaterialContainer.SIZE + MaterialContainer.SPACING[0]) * MaterialContainer.COLUMNS) // 2,
            MaterialContainer.FILTER_HEIGHT + MaterialContainer.SPACING[1]
        )

    def _build_filter_buttons(self, categories: Iterable[str | None]) -> None:
        x: int = MaterialContainer._compute_offset()[0]
        for c in sorted(categories, key=lambda x: x if x is not None else ""): # Sort None as first
            text: str = c.capitalize() if c is not None else "Uncategorised"
            rendered = harbinger_font_small.render(text, True, KDS.Colors.White)
            rect = pygame.Rect(x, 0, rendered.width + 2 * MaterialContainer.FILTER_PADDING_X, MaterialContainer.FILTER_HEIGHT)

            if self.datatype not in disabled_filters:
                disabled_filters[self.datatype] = ("story",)
            default_value: bool = c not in disabled_filters[self.datatype]

            # Do not lerp, LevelBuilder FPS is not fixed.
            self.selector_filter[c] = KDS.UI.ToggleButton(rect, self._on_category_toggled, rendered, default_value=default_value, lerp_duration=0)

            x += rect.width + MaterialContainer.FILTER_SPACING_X

    def _on_category_toggled(self, _: bool) -> None:
        disabled_filters[self.datatype] = tuple(key for key, value in self.selector_filter.items() if not value.state)
        self._rebuild_selectors()

    def _build_selectors(self) -> int:
        offset: Final = MaterialContainer._compute_offset()

        x_index: int = 0
        y: int = offset[1]

        for data in self.data:
            filter_toggle: KDS.UI.ToggleButton | None = self.selector_filter.get(data.category)
            if filter_toggle is None:
                KDS.Logging.AutoError(f"No filter found for category: '{data.category}'")
            elif not filter_toggle.state:
                continue

            rect = pygame.Rect(offset[0] + x_index * (MaterialContainer.SIZE + MaterialContainer.SPACING[0]), y, MaterialContainer.SIZE, MaterialContainer.SIZE)
            self.selectors.append(MaterialSelector(rect, data))

            x_index += 1
            if x_index > MaterialContainer.COLUMNS:
                x_index = 0
                y += MaterialContainer.SIZE
                y += MaterialContainer.SPACING[1]

        if x_index > 0:
            y += MaterialContainer.SIZE
            y += MaterialContainer.SPACING[1]

        return y # total height

    def rebuild(self):
        self._rebuild_filters()
        self._rebuild_selectors()

    def _rebuild_filters(self):
        self._clear_filters()
        self._build_filter_buttons(set(d.category for d in self.data))

    def _rebuild_selectors(self):
        self._clear_selectors()
        self.height = self._build_selectors()

    def update(self, surf: pygame.Surface, y: int, mpos: tuple[int, int], pressed: bool, tip_renders: list[pygame.Surface]) -> str | None:
        if display_size != self.display_size:
            self.rebuild()
            self.display_size = display_size

        clicked: bool = False
        if pressed:
            self.pressed = True
        elif self.pressed:
            self.pressed = False
            clicked = True

        for f in self.selector_filter.values():
            f.rect.y += y
            f.update(surf, mpos, clicked)
            f.rect.y -= y

        for s in self.selectors:
            s.rect.y += y
            show_contraband_tip: KDS.UI.ToggleButton | None = self.selector_filter.get("story")
            result: str | None = s.update(surf, mpos, pressed, clicked, tip_renders, show_contraband_tip = show_contraband_tip.state if show_contraband_tip is not None else False)
            s.rect.y -= y

            if result is not None:
                return result

        return None

    def _clear_selectors(self) -> None:
        for s in self.selectors:
            s.dispose()
        self.selectors.clear()

    def _clear_filters(self) -> None:
        for f in self.selector_filter.values():
            KDS.Cursor.remove_interactable_reference(f)
        self.selector_filter.clear()

    def dispose(self) -> None:
        self._clear_selectors()
        self._clear_filters()

class MaterialSelector:
    def __init__(self, rect: pygame.Rect, data: TextureHolder.TextureData) -> None:
        self.rect: Final[pygame.Rect] = rect
        self.data: Final[TextureHolder.TextureData] = data

        margin_removed_subsurface = self.data.texture.subsurface(self.data.texture.get_bounding_rect())
        self._texture: Final[pygame.Surface] = KDS.Convert.AspectScale(margin_removed_subsurface, self.rect.size)

    def update(self, surf: pygame.Surface, mpos: tuple[int, int], pressed: bool, clicked: bool, tip_renders: list[pygame.Surface], show_contraband_tip: bool) -> str | None:
        collide: bool = self.rect.collidepoint(mpos)

        self._texture.set_alpha(128 if collide and pressed else 255)
        surf.blit(self._texture, (self.rect.centerx - self._texture.width // 2, self.rect.centery - self._texture.height // 2))

        if collide:
            KDS.Cursor.add_interactable_reference(self)

            pygame.draw.rect(display, (230, 30, 40), self.rect, 3)
            tip_renders.append(harbinger_font_small.render(self.data.name, True, KDS.Colors.AviatorRed))
            tip_renders.append(harbinger_font_small.render(self.data.serialNumber, True, KDS.Colors.RiverBlue))
            if show_contraband_tip and self.data.is_contraband:
                tip_renders.append(harbinger_font_small.render("contraband", True, KDS.Colors.Orange))

            if clicked:
                return self.data.serialNumber
            else:
                return None
        else:
            KDS.Cursor.remove_interactable_reference(self)

    def dispose(self) -> None:
        KDS.Cursor.remove_interactable_reference(self)

def materialMenu(previousMaterial: str) -> str:
    global matMenRunning
    matMenRunning = True

    containers: list[MaterialContainer] = []
    texture_data = KDS.Linq.GroupBy(Textures, lambda x: x.serialNumber[0])
    for key, tex in sorted(texture_data, key=lambda x: x[0]):
        containers.append(MaterialContainer(key, sorted(tex, key=lambda k: k.name.lower())))

    def returnWrapper(output: str) -> str:
        for c in containers:
            c.dispose()
        return output

    MIN_SCROLL: int = -MaterialContainer.SPACING[1]
    max_scroll: int = MIN_SCROLL

    y_scroll: int = MIN_SCROLL
    while matMenRunning:
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if defaultEventHandler(event):
                continue
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_e:
                    matMenRunning = False
                    return returnWrapper(previousMaterial)
            elif event.type == MOUSEWHEEL:
                y_scroll -= 30 * event.y
        y_scroll = KDS.Math.Clamp(y_scroll, MIN_SCROLL, max_scroll)

        tip_renders: list[pygame.Surface] = []

        mpos = pygame.mouse.get_pos()
        display.fill((20, 20, 20))

        y: int = 0
        for c in containers:
            res: str | None = c.update(display, y - y_scroll, mpos, mouse_pressed[0], tip_renders)
            if res is not None:
                return returnWrapper(res)
            y += c.height
            y += MaterialContainer.SPACING[1]

        max_scroll = y - 3 * MaterialContainer.SPACING[1] - MaterialContainer.SIZE

        if len(tip_renders) > 0:
            totHeight = 0
            maxWidth = 0
            for tip in tip_renders:
                totHeight += tip.get_height() + 8
                maxWidth = max(maxWidth, tip.get_width())
            totHeight -= 8
            pygame.draw.rect(display, KDS.Colors.Gray, pygame.Rect(mpos[0] + 15 - 3, mpos[1] + 15 - 3, maxWidth + 5, totHeight + 5))
            cumHeight = 0
            for tip in tip_renders:
                pygame.draw.rect(display, KDS.Colors.LightGray, pygame.Rect(mpos[0] + 15 - 3, mpos[1] + 15 - 3 + cumHeight, maxWidth + 5, tip.get_height() + 5))
                display.blit(tip, (mpos[0] + 15 + maxWidth // 2 - tip.get_width() // 2, mpos[1] + 15 + cumHeight))
                cumHeight += tip.get_height() + 8

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData(None), (0, 0))

        pygame.display.flip()
        KDS.Clock.Tick(-1)

    return returnWrapper(previousMaterial)

def multiselect_menu(title_text: str, options: Sequence[tuple[str, Callable[[], None]]]):
    global multiselect_menu_running
    multiselect_menu_running = True

    def back():
        global multiselect_menu_running
        multiselect_menu_running = False

    title = harbinger_font_large.render(title_text, True, KDS.Colors.White)
    buttons: list[KDS.UI.Button] = [
        KDS.UI.Button(
            pygame.Rect(0, 0, 0, 0),
            data[1],
            harbinger_font.render(data[0], True, KDS.Colors.White)
        )
        for i, data in enumerate(options)
    ]

    back_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), back, harbinger_font.render("Back", True, KDS.Colors.AviatorRed))

    while multiselect_menu_running:
        clicked: bool = False
        for event in pygame.event.get():
            if defaultEventHandler(event, DROPFILE):
                continue
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    clicked = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    multiselect_menu_running = False

        display.fill((34, 34, 34))
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()

        title_rect = pygame.Rect((display_size[0] - title.get_width()) // 2, 50, title.get_width(), title.get_height())
        pygame.draw.rect(display, KDS.Colors.Gray, (title_rect.x - 200, title_rect.y - 25, title_rect.w + 400, title_rect.h + 50))
        display.blit(title, title_rect)

        for i, btn in enumerate(buttons):
            btn.rect = pygame.Rect(display_size[0] // 2 - 300, 200 + 125 * i, 600, 100)
            btn.update(display, mouse_pos, clicked)
        back_btn.rect = pygame.Rect(display_size[0] // 2 - 150, display_size[1] - 125, 300, 100)
        back_btn.update(display, mouse_pos, clicked)

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData(None), (0, 0))

        pygame.display.flip()
        KDS.Clock.Tick()

def legacy_upgrade_menu():
    # def notImplemented():
    #     KDS.Logging.AutoError("This legacy converter has not been implemented yet!")

    def run_func(func: Callable[[Callable[[str], None]], None]):
        def renderupdate():
            pygame.event.pump()

            text_surf: pygame.Surface = harbinger_font.render(text, True, KDS.Colors.White)
            msg_surf: pygame.Surface = harbinger_font_small.render(msg, True, KDS.Colors.White)

            text_pos: tuple[float, float] = ((display.get_width() - text_surf.get_width()) / 2, (display.get_height() - text_surf.get_height()) / 2)
            msg_pos: tuple[float, float] = ((display.get_width() - msg_surf.get_width()) / 2, text_pos[1] + harbinger_font.get_linesize())

            display.fill((0, 0, 0))
            display.blit(text_surf, text_pos)
            display.blit(msg_surf, msg_pos)

            pygame.display.flip()
        text: str = f"Running: '{KDS.Convert.String.Snake2Sentence(func.__name__)}'..."
        msg: str = ""
        def update_msg(msg_str: str):
            nonlocal msg
            msg = msg_str
            renderupdate()

        renderupdate()
        func(update_msg)

    multiselect_menu(
        "UPGRADE LEGACY",
        [
            ("tileprops.kdf", lambda: run_func(KDS.LevelBuilder.LegacyTileProp.upgradeTileProp)),
            ("game_map.kds + item_map.kds", lambda: run_func(KDS.LevelBuilder.LegacyGameMap.upgradeGameMap)),
            (".map files", lambda: run_func(KDS.LevelBuilder.LegacyGameMap.upgradeMapFiles))
        ]
    )

def generate_menu():
    multiselect_menu(
        "GENERATE",
        [
            ("levelprop.kdf", KDS.LevelBuilder.LevelProp.generateLevelProp),
            ("campaignprop.kdf", KDS.LevelBuilder.CampaignProp.generateCampaignProp)
        ]
    )

def menu():
    global currentSaveName, brush, grid, gridSize, btn_menu, gamesize, scaleMultiplier, scalesize, mainRunning
    btn_menu = True

    def button_handler(_openMap: bool = False):
        global btn_menu, grid, gridSize, undo
        if _openMap:
            # Button menu is turned off if openMap was succesful
            btn_menu = not openMap()
        else:
            KDS.Cursor.reset_interactables()
            g = KDS.Console.Start("Grid Size: (int, int)", True, KDS.Console.CheckTypes.Tuple(2, 1, KDS.Math.MAXVALUE, 1000)).replace(" ", "").split(",")
            if g is not None and len(g) > 1: # if escaped, g is a one element list
                gridSize = (int(g[0]), int(g[1]))
                grid = loadGrid(gridSize)
                undo = Undo()
                btn_menu = False

    def menu_navigation(menu: Callable[[], None]):
        KDS.Cursor.reset_interactables()
        menu()

    newMap_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), button_handler, harbinger_font.render("New Map", True, KDS.Colors.White))
    openMap_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), button_handler, harbinger_font.render("Open Map", True, KDS.Colors.White))
    upgradeProps_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), menu_navigation, harbinger_font.render("Upgrade Legacy", True, KDS.Colors.White))
    gen_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), menu_navigation, harbinger_font.render("Generate", True, KDS.Colors.White))
    quit_btn = KDS.UI.Button(pygame.Rect(0, 0, 0, 0), LB_Quit, harbinger_font.render("Quit", True, KDS.Colors.AviatorRed))

    txt = harbinger_font_small.render("The software is provided \"as is\" without warranty of any kind. This is an in-house application and therefore is not applicable to any upkeep and/or maintenance.", True, KDS.Colors.CloudWhite)
    txt_icon = KDS.Convert.AspectScale(pygame.image.load("Assets/Textures/Branding/levelBuilderTextIcon.png").convert_alpha(), (0, 150), aspectMode=KDS.Convert.AspectMode.HeightControlsWidth)

    while btn_menu:
        clicked = False
        for event in pygame.event.get():
            if defaultEventHandler(event, DROPFILE):
                continue
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    clicked = True
            elif event.type == DROPFILE:
                # Button menu is turned off if loadMap was succesful
                btn_menu = not loadMap(event.file)

        display.fill((34, 34, 34))
        mouse_pos = pygame.mouse.get_pos()

        newMap_btn.rect =       pygame.Rect(display_size[0] // 2 - 425, display_size[1] // 2 - 100, 400, 150)
        openMap_btn.rect =      pygame.Rect(display_size[0] // 2 + 25,  display_size[1] // 2 - 100, 400, 150)
        upgradeProps_btn.rect = pygame.Rect(display_size[0] // 2 - 425, display_size[1] // 2 + 100, 400, 100)
        gen_btn.rect =          pygame.Rect(display_size[0] // 2 + 25,  display_size[1] // 2 + 100, 400, 100)
        quit_btn.rect =         pygame.Rect(display_size[0] // 2 - 150, display_size[1] // 2 + 250, 300, 100)

        newMap_btn.update(display, mouse_pos, clicked)
        openMap_btn.update(display, mouse_pos, clicked, True)
        upgradeProps_btn.update(display, mouse_pos, clicked, legacy_upgrade_menu)
        gen_btn.update(display, mouse_pos, clicked, generate_menu)
        quit_btn.update(display, mouse_pos, clicked)

        display.blit(txt, (2, display_size[1] - harbinger_font_small.get_height() - 2))
        display.blit(txt_icon, (display_size[0] // 2 - txt_icon.get_width() // 2, display_size[1] // 2 - 300))

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData(None), (0, 0))

        if btn_menu:
            pygame.display.flip()
        KDS.Clock.Tick()

class Selected:
    units: list[UnitData] = []

    @staticmethod
    def Set(*, serialOverride: str | None = None, propertiesOverride: dict[UnitType, dict[str, Union[str, int, float, bool]]] | None = None, clear_selected: bool = True):
        global grid #                                                                                                        ^^ Undo is now registered each time mouse button 1 (left click) is pressed. Change this if something breaks.
        Selected.SetCustomGrid(grid=grid, serialOverride=serialOverride, propertiesOverride=propertiesOverride, clear_selected=clear_selected)

    @staticmethod
    def SetCustomGrid(grid: GridType, *, serialOverride: str | None = None, propertiesOverride: dict[UnitType, dict[str, Union[str, int, float, bool]]] | None = None, clear_selected: bool = True):
        gridSetUndo: Final = ChangeUndoRecord()

        for unit in Selected.units:
            unitCopy = unit.Copy()
            if serialOverride != None:
                unitCopy.overrideSerial(None, serialOverride, undo_can_be_none=True)
            if propertiesOverride != None:
                unitCopy.properties.SetAll(None, propertiesOverride, undo_can_be_none=True)
            try:
                grid[unit.pos[1]][unit.pos[0]].CopyFrom(gridSetUndo, unitCopy)
            except IndexError:
                warnSize = f"({len(grid[0])}, {len(grid)})" if len(grid) > 0 else "(<invalid-grid-size>, <invalid-grid-size>)"
                KDS.Logging.warning(f"Index error while setting unit at position: \"{unit.pos}\". Grid size: {warnSize}", consoleVisible=True)

        if clear_selected:
            Selected.units.clear()

        assert undo is not None
        undo.register(gridSetUndo)

    @staticmethod
    def Replace(sourceSerial: str, destinationSerial: str, clear_selected: bool = True):
        gridReplaceUndo: Final = ChangeUndoRecord()

        for unit in Selected.units:
            unitCopy = unit.Copy()
            for slot, srl in enumerate(unitCopy.serials):
                if srl == sourceSerial:
                    unitCopy.setSerialToSlot(None, destinationSerial, slot, undo_can_be_none=True)
                    unitCopy.properties.RemoveUnused(None, undo_can_be_none=True)

            try:
                grid[unit.pos[1]][unit.pos[0]].CopyFrom(gridReplaceUndo, unitCopy)
            except IndexError:
                warnSize = f"({len(grid[0])}, {len(grid)})" if len(grid) > 0 else "(<invalid-grid-size>, <invalid-grid-size>)"
                KDS.Logging.warning(f"Index error while setting unit at position: \"{unit.pos}\". Grid size: {warnSize}", consoleVisible=True)

        if clear_selected:
            Selected.units.clear()

        assert undo is not None
        undo.register(gridReplaceUndo)

    @staticmethod
    def Flip(*, horizontal: bool = False, vertical: bool = False) -> None:
        if Drag.Rect == None:
            return

        rect: pygame.Rect = Drag.Rect.copy()

        for u in Selected.units:
            dist_from_right: int = rect.right - u.pos[0]
            dist_from_bottom: int = rect.bottom - u.pos[1]

            if horizontal:
                u.pos = (rect.left + dist_from_right - 1, u.pos[1])
            if vertical:
                u.pos = (u.pos[0], rect.top + dist_from_bottom - 1)

    @staticmethod
    def Move(x: int, y: int):
        if Drag.Rect == None:
            return

        for u in Selected.units:
            u.pos = (u.pos[0] + x, u.pos[1] + y)
        Drag.Rect.x += x
        Drag.Rect.y += y

    @staticmethod
    def Update():
        Selected.units = []
        if Drag.Rect == None:
            return
        for row in grid[Drag.Rect.y:Drag.Rect.y + Drag.Rect.height]:
            for unit in row[Drag.Rect.x:Drag.Rect.x + Drag.Rect.width]:
                Selected.units.append(unit.Copy())

    @staticmethod
    def Get():
        Selected.Update()
        Selected.Set(serialOverride=UnitData.EMPTYSERIAL, propertiesOverride={}, clear_selected=False)

    @staticmethod
    def ToString(serializeProperties: bool = False) -> Union[str, tuple[str, str]]:
        units2d: dict[int, dict[int, UnitData]] = {} # Dictionaries are ordered
        for u in Selected.units:
            if u.pos[1] not in units2d:
                units2d[u.pos[1]] = {}
            units2d[u.pos[1]][u.pos[0]] = u
        output = ""
        for row in units2d.values():
            for u in row.values():
                output += str(u) + " / "
            output = output.removesuffix(" / ") + "\n"
        if not serializeProperties:
            return output
        else:
            unitsNormalizedPositions = [[u.Copy() for u in l.values()] for l in units2d.values()]
            for y, row in enumerate(unitsNormalizedPositions):
                for x, u in enumerate(row):
                    u.pos = (x, y)
            return (output, PropertiesData.Serialize(unitsNormalizedPositions))

    @staticmethod
    def FromString(string: str, properties: str | None = None):
        units: list[UnitData] = []
        contents = string.splitlines()
        while len(contents[-1]) < 1: contents = contents[:-1]

        offset = Drag.Rect.topleft if Drag.Rect != None else (0, 0)
        maxX = 0
        for y, row in enumerate(contents):
            for x, unit in enumerate(row.split("/")):
                maxX = max(maxX, x)

                unit = unit.strip(" ")
                if unit == UnitData.EMPTYSERIAL:
                    continue # Do not override empty tiles

                units.append(UnitData((x, y), unit.strip(" ")))
        if properties != None:
            PropertiesData.Deserialize(properties, [units]) # Should be fine since deserialize doesn't actually use the indexes of units in list
        for u in units:
            u.pos = (u.pos[0] + offset[0], u.pos[1] + offset[1])
        Drag.SelectCustom(pygame.Rect(offset[0], offset[1], maxX + 1, len(contents)) if maxX > 0 and len(contents) > 0 else None)
                                                                    # ^^ Need to add one... I don't know why.
        Selected.units = units # Drag.SelectCustom seems to clear units, so set them after it.

Drag.registerCalls(DragMode.Default, Selected.Set, None, Selected.Get, Selected.Set)

def defaultEventHandler(event, ignoreEventOfType: int | None = None) -> bool:
    #region Event Ignoring
    if event.type == ignoreEventOfType:
        return False
    #endregion

    if event.type == QUIT:
        LB_Quit()
        return True # Return True if event handling can be stopped
    elif event.type == KEYDOWN:
        if event.key == K_F3:
            KDS.Debug.Enabled = not KDS.Debug.Enabled
            KDS.Logging.Profiler(False)
            return True
        if event.key == K_F4:
            if KDS.Debug.Enabled:
                KDS.Logging.Profiler(not KDS.Logging.profiler_running)
    elif event.type == VIDEORESIZE:
        SetDisplaySize((event.w, event.h))
        return True
    elif event.type == DROPFILE:
        loadMap(event.file)
        return True
    # There are no good ways to make fullscreen in levelbuilder at the moment, because pygame.display.toggle_fullscreen crashes for some reason
    # elif event.type == KEYDOWN:
        # if event.key == K_F11:
        #     SetDisplaySize(toggleFullscreen=True)
        #     return True
    return False

class BeforeMoveData(NamedTuple):
    mouse_pos: tuple[int, int]
    scroll: tuple[int, int]

allowTilePlacement: bool = False
def main():
    global currentSaveName, brush, grid, gridSize, gamesize, scaleMultiplier, scalesize, mainRunning, allowTilePlacement, referenceGrid, referenceGridSize, zoneMode, referenceGridHandle, renderOverlays

    menu()
    if not mainRunning: return

    textureRescaleHandle: Optional[KDS.Jobs.JobHandle] = None
    new_rescale_requested: bool = False

    def zoom(add: int, scroll: list[int], grid: GridType):
        global scalesize, scaleMultiplier
        nonlocal new_rescale_requested
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_scaled = (int(mouse_pos[0] / scalesize + scroll[0]), int(mouse_pos[1] / scalesize + scroll[1]))
        hitPos = grid[int(KDS.Math.Clamp(mouse_pos_scaled[1], 0, gridSize[1] - 1))][int(KDS.Math.Clamp(mouse_pos_scaled[0], 0, gridSize[0] - 1))].pos
        newsize = KDS.Math.Clamp(scalesize + add, ZOOMRANGE[0], ZOOMRANGE[1])
        if newsize == scalesize:
            return

        scalesize = newsize
        scaleMultiplier = scalesize / gamesize

        mouse_pos_scaled = (int(mouse_pos[0] / scalesize + scroll[0]), int(mouse_pos[1] / scalesize + scroll[1]))
        scroll[0] += hitPos[0] - mouse_pos_scaled[0]
        scroll[1] += hitPos[1] - mouse_pos_scaled[1]

        new_rescale_requested = True

    openCommandTerminal: bool = False

    before_move: BeforeMoveData | None = None
    pickTile: bool = False
    lastPickedTile: UnitData | None = None
    while mainRunning:
        assert(undo is not None)

        pygame.key.set_repeat(500, 31)

        # BEFORE EVENTS
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get(): #Event loop
            if defaultEventHandler(event):
                continue
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 2:
                    if keys_pressed[K_LALT]:
                        brush.shape = BrushShape.next_value(brush.shape)
                    elif keys_pressed[K_LSHIFT]:
                        before_move = BeforeMoveData(mouse_pos, (scroll[0], scroll[1]))
                    else:
                        pickTile = True
                elif event.button == 3:
                    if zoneMode:
                        PropertiesData.Zones.RemoveCollidePoint(mouse_pos)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 2:
                    before_move = None
                    pickTile = False
            elif event.type == KEYDOWN:
                if event.key == K_z:
                    if keys_pressed[K_LCTRL]:
                        undo.undo()
                    else:
                        zoneMode = not zoneMode
                elif event.key == K_y:
                    if keys_pressed[K_LCTRL]:
                        undo.redo()
                    else:
                        renderOverlays = not renderOverlays
                elif event.key == K_t:
                    openCommandTerminal = True
                elif event.key == K_h:
                    KDS.Console.Feed.append(KEYMAP_STR)
                    openCommandTerminal = True
                elif event.key == K_r:
                    resize_output = KDS.Console.Start("New Grid Size: (int, int)", True, KDS.Console.CheckTypes.Tuple(2, 1, KDS.Math.MAXVALUE, 1000), defVal=f"{gridSize[0]}, {gridSize[1]}", autoFormat=True)
                    if resize_output != None:
                        resizeGrid((int(resize_output[0]), int(resize_output[1])))
                elif event.key == K_e:
                    tmpBrush = materialMenu(brush.currentMaterial)
                    tmpProps: Optional[dict[UnitType, dict[str, Union[str, int, float, bool]]]] = None
                    if tmpBrush[0] == "3":
                        tmpProps = {UnitType.Teleport: {"identifier": 1}}
                    brush.SetBrush(tmpBrush, tmpProps)
                    allowTilePlacement = False
                elif event.key == K_DELETE:
                    Selected.Set(serialOverride=UnitData.EMPTYSERIAL)
                    Selected.Update()
                elif event.key == K_d:
                    if keys_pressed[K_LCTRL]:
                        Selected.Set(clear_selected=False)
                elif event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                    x = 0
                    y = 0
                    if event.key == K_UP:
                        y += -1
                    elif event.key == K_DOWN:
                        y += 1
                    elif event.key == K_LEFT:
                        x += -1
                    elif event.key == K_RIGHT:
                        x += 1
                    Selected.Move(x, y)
                elif event.key == K_a:
                    if keys_pressed[K_LCTRL]:
                        if Drag.Mode == DragMode.Default:
                            Drag.SelectCustom(pygame.Rect(0, 0, gridSize[0], gridSize[1]))
                        Selected.Get()
                elif event.key == K_c:
                    if keys_pressed[K_LCTRL]:
                        try:
                            toClipboard = Selected.ToString(serializeProperties=True)
                            if not isinstance(toClipboard, tuple) or len(toClipboard) != 2:
                                raise ValueError(f"Clipboard data (type: from) is an incorrect type. Tuple of length 2 expected; got: \"{toClipboard}\".")
                            pygame.scrap.put_text(f"KDS_LevelBuilder_Clipboard_Copy_{toClipboard[0]}??{toClipboard[1]}")
                        except Exception:
                            KDS.Logging.AutoError(f"Copy to clipboard failed. Exception Below:\n{traceback.format_exc()}")
                elif event.key == K_v:
                    if keys_pressed[K_LCTRL]:
                        try:
                            fromClipboard: str = pygame.scrap.get_text()
                            # fromClipboard is empty string ("") if clipboard is empty. Check prefix to verify the values in clipboard.
                            if fromClipboard.startswith("KDS_LevelBuilder_Clipboard_Copy_"):
                                fromClipboardSplit = fromClipboard.removeprefix("KDS_LevelBuilder_Clipboard_Copy_").split("??", 1)
                                if len(fromClipboardSplit) != 2:
                                    raise ValueError(f"Clipboard data (type: to) is an incorrect type. List of length 2 expected; got: \"{fromClipboardSplit}\".")
                                if len(fromClipboardSplit[1]) > 0 and not fromClipboardSplit[1].isspace():
                                    Selected.FromString(fromClipboardSplit[0], fromClipboardSplit[1])
                                else:
                                    KDS.Logging.info("Skipped properties for pasting from clipboard, because it is either empty or whitespace.", consoleVisible=True)
                                    Selected.FromString(fromClipboardSplit[0], None)
                            else: KDS.Logging.info(f"Cannot paste \"{fromClipboard}\" into LevelBuilder.", consoleVisible=True)
                        except Exception:
                            KDS.Logging.AutoError(f"Paste from clipboard failed. Exception: {traceback.format_exc()}")
                elif event.key == K_g:
                    if referenceGrid != None:
                        referenceGrid = None
                        for row in grid:
                            for unit in row:
                                unit.matchesReference = False
                    else:
                        referencePath: str = filedialog.askopenfilename(filetypes=(("Data file", "*.dat"), ("All files", "*.*")), title="Open Reference Map File", initialdir="Assets/Maps/Reference")
                        if len(referencePath) > 0 and not referencePath.isspace():
                            referenceGrid, referenceGridSize = internalLoadMap(referencePath, modifyGlobals=False)
                elif event.key == K_F5:
                    if len(currentSaveName) > 0:
                        loadLevelProp(os.path.dirname(currentSaveName))
            elif event.type == MOUSEWHEEL:
                move_multiplier: int = 1 if not keys_pressed[K_LALT] else 10
                if keys_pressed[K_LALT]:
                    if keys_pressed[K_LCTRL]:
                        brush.random_rmv_count -= event.y
                    else:
                        brush.size += event.y
                elif keys_pressed[K_LSHIFT]:
                    scroll[0] -= event.y * move_multiplier
                elif keys_pressed[K_LCTRL]:
                    zoom(event.y * 5, scroll, grid)
                else:
                    scroll[1] -= event.y * move_multiplier
                scroll[0] += event.x * move_multiplier

        # AFTER EVENTS
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        # second event check fixes some race conditions and edge cases

        if not mouse_pressed[0] and not mouse_pressed[2]:
            allowTilePlacement = True
        drag_was_just_cleared_by_rightclick: bool = Drag.update(mouse_pos, mouse_pressed[0], mouse_pressed[2], keys_pressed, allow_drag=(allowTilePlacement or zoneMode))
        if drag_was_just_cleared_by_rightclick:
            allowTilePlacement = False

        if new_rescale_requested:
            if textureRescaleHandle is None or textureRescaleHandle.IsComplete:
                textureRescaleHandle = KDS.Jobs.Schedule(Textures.RescaleTextures)
                new_rescale_requested = False

        if openCommandTerminal:
            inputConsole_output: Any = KDS.Console.Start("Enter Command:", True, KDS.Console.CheckTypes.Commands(), commands=commandTree, showFeed=True, autoFormat=True, enableOld=True)
            if inputConsole_output != None:
                console_exit_code: int = consoleHandler(inputConsole_output)
                openCommandTerminal = (console_exit_code > 0)
            else:
                openCommandTerminal = False

        if before_move is not None:
            mid_scroll_x = (before_move.mouse_pos[0] - mouse_pos[0]) // scalesize
            mid_scroll_y = (before_move.mouse_pos[1] - mouse_pos[1]) // scalesize
            if mid_scroll_x > 0 or mid_scroll_y > 0 or mid_scroll_x < 0 or mid_scroll_y < 0:
                scroll[0] = before_move.scroll[0] + mid_scroll_x
                scroll[1] = before_move.scroll[1] + mid_scroll_y

        if keys_pressed[K_s] and keys_pressed[K_LCTRL]:
            if len(currentSaveName) < 1 or currentSaveName.isspace():
                saveMapName()
            else:
                saveMap(grid, currentSaveName)
        if keys_pressed[K_s] and keys_pressed[K_LCTRL] and keys_pressed[K_LSHIFT]:
            saveMapName()

        if keys_pressed[K_o] and keys_pressed[K_LCTRL]:
            openMapSuccess = openMap()
            if not openMapSuccess:
                KDS.Logging.info("Map opening cancelled.", True)

        if referenceGrid != None:
            if referenceGridHandle == None or referenceGridHandle.IsComplete:
                if referenceGridHandle != None:
                    referenceGridHandle.Complete()
                referenceGridHandle = KDS.Jobs.Schedule(UnitData.referenceUpdate)
        elif referenceGridHandle != None:
            if referenceGridHandle.IsComplete:
                referenceGridHandle.Complete()
                referenceGridHandle = None

        display.fill((30, 20, 60))
        lastPickedTile = UnitData.renderUpdate(display, scroll, grid, brush,
                              keys_pressed, mouse_pressed,
                              pickTile=pickTile, pickLastTile=lastPickedTile)

        if undo.unsaved_changes > 0:
            if undo.unsaved_changes < 50:
                _color = KDS.Colors.Yellow
            elif undo.unsaved_changes < 100:
                _color = KDS.Colors.Orange
            else:
                _color = KDS.Colors.Red
            pygame.draw.circle(display, _color, (10, 10), 5)

        if not brush.IsEmpty:
            brushPreviewTmpSize: tuple[int, int] = (68, 68)
            brushPreviewTmpPos: tuple[int, int] = (display_size[0] - 10 - brushPreviewTmpSize[0], 10)
            brushPreviewPropertiesWidth: int = 2
            brushPreviewTmpScaled: pygame.Surface = KDS.Convert.AspectScale(Textures.GetDefaultTexture(brush.currentMaterial), brushPreviewTmpSize)
            display.blit(brushPreviewTmpScaled, brushPreviewTmpPos)
            if brush.hasProperties:
                pygame.draw.rect(
                    display,
                    (255, 0, 255),
                    (
                        brushPreviewTmpPos[0] - brushPreviewPropertiesWidth,
                        brushPreviewTmpPos[1] - brushPreviewPropertiesWidth,
                        brushPreviewTmpSize[0] + (2 * brushPreviewPropertiesWidth),
                        brushPreviewTmpSize[1] + (2 * brushPreviewPropertiesWidth)
                    ),
                    width=brushPreviewPropertiesWidth
                )

        if len(Selected.units) > 0:
            for unit in Selected.units:
                for number in unit.serials:
                    if number != UnitData.EMPTY:
                        UnitData.renderSerial(display, unit.properties, number, (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize))

        if Drag.Mode == DragMode.Default:
            Drag.render(Drag.DEFAULT_STYLE, display, scroll)

        if zoneMode:
            brush.SetBrush() # Clear brush
            if Drag.Mode != DragMode.Zone:
                Drag.clear()
                Drag.Mode = DragMode.Zone
            allowTilePlacement = False

            zoneScreen = pygame.Surface(display_size)
            zoneScreen.fill(KDS.Colors.White)
            for zoneRect, zoneData in PropertiesData.Zones:
                zoneRectScaled = pygame.Rect((zoneRect.x - scroll[0]) * scalesize, (zoneRect.y - scroll[1]) * scalesize, zoneRect.width * scalesize, zoneRect.height * scalesize)
                if zoneRectScaled.right < 0 or zoneRectScaled.left > display_size[0] or zoneRectScaled.bottom < 0 or zoneRectScaled.top > display_size[0]:
                    continue

                zoneSurf = pygame.Surface(zoneRectScaled.size)
                zoneSurf.fill(KDS.Colors.Gray)

                if PropertiesData.ZoneSetting.Disco in zoneData and zoneData[PropertiesData.ZoneSetting.Disco] == True:
                    disco_colors = (
                        KDS.Colors.Red,
                        KDS.Colors.Orange,
                        KDS.Colors.Yellow,
                        KDS.Colors.Green,
                        KDS.Colors.Blue,
                        KDS.Colors.Purple,
                        KDS.Colors.Magenta
                    )
                    disco_w = 40
                    for i in range(0, zoneRectScaled.width, disco_w):
                        pygame.draw.rect(zoneSurf, disco_colors[i // disco_w % len(disco_colors)], (i, 0, disco_w, zoneRectScaled.height))

                if PropertiesData.ZoneSetting.Darkness in zoneData:
                    zoneDarkness = zoneData[PropertiesData.ZoneSetting.Darkness]
                    if isinstance(zoneDarkness, int):
                        darkColor = 255 - zoneDarkness
                        scaleDiv = scalesize // 3
                        for y in range(0, zoneRectScaled.height, scaleDiv * 2):
                            for x in range(0, zoneRectScaled.width, scaleDiv * 2):
                                pygame.draw.circle(zoneSurf, (darkColor, darkColor, darkColor), (x, y), scaleDiv // 2)

                if PropertiesData.ZoneSetting.StaffOnly in zoneData and zoneData[PropertiesData.ZoneSetting.StaffOnly] == True:
                    lineWidth = max(scalesize // 8, 1)
                    line_45 = ((0, 0), zoneRectScaled.size)
                    lineLength = max(zoneRectScaled.width, zoneRectScaled.height)
                    for y in range( -lineLength, lineLength, lineWidth * 3):
                        pygame.draw.line(zoneSurf, KDS.Colors.Black, (line_45[0][0], line_45[0][1] + y), (line_45[1][0], line_45[1][1] + y), lineWidth)

                if PropertiesData.ZoneSetting.LevelEnder in zoneData and zoneData[PropertiesData.ZoneSetting.LevelEnder] == True:
                    lineWidth = max(scalesize // 8, 1)
                    line_45 = ((zoneRectScaled.width, 0), (0, zoneRectScaled.height))
                    lineLength = max(zoneRectScaled.width, zoneRectScaled.height)
                    for y in range(-lineLength, lineLength, lineWidth * 3):
                        pygame.draw.line(zoneSurf, KDS.Colors.RiverBlue, (line_45[0][0], line_45[0][1] + y), (line_45[1][0], line_45[1][1] + y), lineWidth)

                zoneScreen.blit(zoneSurf, zoneRectScaled.topleft)

                zoneSettingsCutoff: float = 1.25 * scalesize
                if harbinger_font_small.get_height() < zoneSettingsCutoff:
                    for zoneSettingIndex, (zoneSetting, zoneSettingValue) in enumerate(zoneData.items()):
                        zoneSettingY: int = zoneSettingIndex * harbinger_font_small.get_linesize()
                        # this hides some vital settings when zooming out
                        # if zoneSettingY > zoneSettingsCutoff:
                        #     break
                        zoneSettingRender: pygame.Surface = harbinger_font_small.render(f"{zoneSetting.name}: {zoneSettingValue}", True, KDS.Colors.AviatorRed)
                        # if zoneSettingRender.width > zoneRectScaled.width:
                        #     zoneSettingRender = zoneSettingRender.subsurface((0, 0, zoneRectScaled.width, zoneSettingRender.height))
                        zoneScreen.blit(zoneSettingRender, (zoneRectScaled.left, zoneRectScaled.top + zoneSettingY))

                if keys_pressed[K_p] and zoneRectScaled.collidepoint(*mouse_pos):
                    zone_command_tree = {
                        PropertiesData.ZoneSetting.StaffOnly: {"true": "break", "false": "break", "null": "break"},
                        PropertiesData.ZoneSetting.LevelEnder: {"true": "break", "false": "break", "null": "break"},
                        PropertiesData.ZoneSetting.Disco: {"true": "break", "false": "break", "null": "break"},
                        PropertiesData.ZoneSetting.DarknessInstant: {"true": "break", "false": "break", "null": "break"},
                        PropertiesData.ZoneSetting.Darkness: {"[int]": "break", "null": "break"},
                        PropertiesData.ZoneSetting.CustomId: {"[string]": "break"}
                    }
                    zone_command: Optional[list[str]] = KDS.Console.Start("Enter Zone property:", True, KDS.Console.CheckTypes.Commands(), commands=zone_command_tree, autoFormat=True)
                    zoneConsoleHandler(zone_command, zoneRect)
            zoneScreen.set_alpha(128)
            display.blit(zoneScreen, (0, 0))
        elif Drag.Mode != DragMode.Default:
            Drag.Mode = DragMode.Default
            Drag.clear()

        if LevelPropData.ShowKoponen:
            display.blit(LevelPropData.KoponenTextureRescaled, (LevelPropData.KoponenPos[0] * scaleMultiplier - scroll[0] * scalesize, LevelPropData.KoponenPos[1] * scaleMultiplier - scroll[1] * scalesize))
        if LevelPropData.ShowPlayer:
            display.blit(pygame.transform.flip(LevelPropData.PlayerTextureRescaled, LevelPropData.PlayerFlipped, False), (LevelPropData.PlayerPos[0] * scaleMultiplier - scroll[0] * scalesize, LevelPropData.PlayerPos[1] * scaleMultiplier - scroll[1] * scalesize))

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData(None), (0, 0))

        pygame.display.flip()
        KDS.Clock.Tick(-1)

mainRunning = True
try:
    main()
except Exception as e:
    KDS.Logging.AutoError(f"KDS LevelBuilder ran into an unrecoverable error! Details below:\n{traceback.format_exc()}")
    if KDS.System.MessageBox.Show("Fatal Error!", "KDS LevelBuilder ran into an unrecoverable error! Do you want to try to save your project?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.ERROR) == KDS.System.MessageBox.Responses.YES:
        try:
            saveMapName()
            KDS.System.MessageBox.Show("Success!", "Your project was saved successfully.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.INFORMATION)
        except Exception:
            KDS.System.MessageBox.Show("Failure!", "You project failed to save.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)

KDS.Jobs.quit()
pygame.quit()
