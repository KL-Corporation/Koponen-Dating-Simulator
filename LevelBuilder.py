from __future__ import annotations

#region Import Error
if __name__ != "__main__":
    raise ImportError("Level Builder cannot be imported!")
#endregion

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
from pygame.locals import *
import KDS.Colors
import KDS.Convert
import KDS.ConfigManager
import KDS.System
import KDS.Math
import KDS.UI
import KDS.Console
import KDS.Logging
import KDS.Linq
import tkinter
import sys
from tkinter import filedialog
import json
import traceback
from enum import IntEnum

from typing import Any, Dict, List, Optional, Tuple, Union

root = tkinter.Tk()
root.withdraw()
pygame.init()
pygame.scrap.init()
pygame.scrap.set_mode(SCRAP_CLIPBOARD)
display_size = (1600, 800)
scalesize = 68
gamesize = 34
scaleMultiplier = scalesize / gamesize

pygame.display.set_caption("KDS Level Builder")
pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/levelBuilderIcon.png"))
def SetDisplaySize(size: Tuple[int, int] = (0, 0)):
    global display, display_size
    display = pygame.display.set_mode(size, RESIZABLE | HWSURFACE | DOUBLEBUF)
    display_size = display.get_size()
SetDisplaySize(display_size)

APPDATA = os.path.join(str(os.getenv('APPDATA')), "KL Corporation", "KDS Level Builder")
LOGPATH = os.path.join(APPDATA, "logs")
os.makedirs(LOGPATH, exist_ok=True)
KDS.Logging.init(APPDATA, LOGPATH)

clock = pygame.time.Clock()
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
harbinger_font_large = pygame.font.Font("Assets/Fonts/harbinger.otf", 55, bold=0, italic=0)
harbinger_font_small = pygame.font.Font("Assets/Fonts/harbinger.otf", 15, bold=0, italic=0)

brushNames = {
    "imp": "2001",
    "seargeant": "2002",
    "drug_dealer": "2003",
    "turbo_shotgunner": "2004",
    "mafiaman": "2005",
    "methmaker": "2006",
    "undead_monster": "2007",
    "teleport": "3001"
}

with open("Assets/Textures/build.json") as f:
    d = f.read()
buildData = json.loads(d)

t_textures: Dict[str, pygame.Surface] = {}
for element in buildData["tile_textures"]:
    srl = f"0{element}"

    elmt = buildData["tile_textures"][element]
    t_textures[srl] = pygame.image.load("Assets/Textures/Tiles/" + elmt).convert()
    t_textures[srl].set_colorkey(KDS.Colors.White)
    brushNames[os.path.splitext(elmt)[0]] = srl

i_textures: Dict[str, pygame.Surface] = {}
for element in buildData["item_textures"]:
    srl = f"1{element}"

    elmt = buildData["item_textures"][element]
    i_textures[srl] = pygame.image.load("Assets/Textures/Items/" + elmt).convert()
    i_textures[srl].set_colorkey(KDS.Colors.White)
    brushNames[os.path.splitext(elmt)[0]] = srl

e_textures: Dict[str, pygame.Surface] = {
    "2001": pygame.image.load("Assets/Textures/Animations/imp_walking_0.png").convert(),
    "2002": pygame.image.load("Assets/Textures/Animations/seargeant_walking_0.png").convert(),
    "2003": pygame.image.load("Assets/Textures/Animations/drug_dealer_walking_0.png").convert(),
    "2004": pygame.image.load("Assets/Textures/Animations/turbo_shotgunner_walking_0.png").convert(),
    "2005": pygame.image.load("Assets/Textures/Animations/mafiaman_walking_0.png").convert(),
    "2006": pygame.image.load("Assets/Textures/Animations/methmaker_idle_0.png").convert(),
    "2007": pygame.image.load("Assets/Textures/Animations/undead_monster_walking_0.png").convert(),
    "2008": pygame.image.load("Assets/Textures/Animations/mummy_walking_0.png").convert(),
    "2009": pygame.image.load("Assets/Textures/Animations/security_guard_walking_0.png").convert()
}
for tex in e_textures.values():
    tex.set_colorkey(tex.get_at((0, 0)))

teleports: Dict[str, pygame.Surface] = {
    "3001" : pygame.image.load("Assets/Textures/Editor/telep.png").convert(),
    "3501" : pygame.image.load("Assets/Textures/Tiles/door_front.png").convert()
}

Atextures: Dict[str, Dict[str, pygame.Surface]] = {
    "0": t_textures,
    "1": i_textures,
    "2": e_textures,
    "3": teleports
}

trueScale = [f"0{e:03d}" for e in buildData["trueScale"]]
### GLOBAL VARIABLES ###

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]
scroll = [0, 0]
teleportTemp = "001"
currentSaveName = ''
grid: List[List[UnitData]] = [[]]
gridSize = (0, 0)

dragRect = None

class Undo:
    changes: List[UnitData] = []
    index = 0
    overflowCount = 0
    totalOffset = 0

    @staticmethod
    def register(unit: UnitData):
        del Undo.changes[Undo.index + 1:]
        if len(Undo.changes) > 0 and unit == Undo.changes[-1]:
            return
        Undo.changes.append(unit.Copy())
        while len(Undo.changes) > 128:
            del Undo.changes[0]
            Undo.overflowCount += 1
        Undo.index = len(Undo.changes) - 1
        """
        global grid, dragRect
        if Undo.index == len(Undo.points) - 1:
            last = Undo.points[Undo.index]
            if last["grid"] == grid and last["dragRect"] == dragRect:
                if Undo.totalOffset == 0 and Undo.index == 0 and Undo.overflowCount == 0:
                    Undo.totalOffset = 1
                return

        toSave = {
            "grid": [[t.Copy() for t in r] for r in grid], # deepcopy replacement
            "dragRect": dragRect.copy() if dragRect != None else None
        }

        Selected.SetCustomGrid(toSave["grid"], registerUndo=False)
        removedCount = len(Undo.points[Undo.index + 1:])
        del Undo.points[Undo.index + 1:]
        if Undo.index == 0 and len(Undo.points) == 1 and removedCount > 0: del Undo.points[0]
        Undo.points.append(toSave)
        while len(Undo.points) > 64:
            del Undo.points[0]
            Undo.overflowCount += 1
        Undo.index = len(Undo.points) - 1
        """

    @staticmethod
    def request(redo: bool = False):
        global grid
        redoSub = KDS.Convert.ToMultiplier(redo)
        Undo.index = KDS.Math.Clamp(Undo.index - redoSub, 0, len(Undo.changes) - 1)
        subIndex = Undo.index - redoSub
        if 0 <= subIndex < len(Undo.changes) and Undo.changes[subIndex].pos == Undo.changes[Undo.index].pos:
            Undo.index = subIndex
        change = Undo.changes[Undo.index]
        if grid[change.pos[1]][change.pos[0]].pos != change.pos: # Scrapped finding by iterating, because too slow.
            KDS.Logging.AutoError(f"Unit at position: {change.pos} not found in grid!")
            return
        grid[change.pos[1]][change.pos[0]] = change.Copy()

        """
        Undo.index = KDS.Math.Clamp(Undo.index - KDS.Convert.ToMultiplier(redo), 0, len(Undo.points) - 1)

        global grid, dragRect
        data = Undo.points[Undo.index]
        grid = data["grid"]
        dragRect = data["dragRect"]
        """

    @staticmethod
    def clear():
        Undo.changes.clear()
        Undo.index = 0
        Undo.overflowCount = 0

def LB_Quit():
    global matMenRunning, btn_menu, mainRunning
    if Undo.index + Undo.overflowCount > 0 and KDS.System.MessageBox.Show("Unsaved Changes.", "There are unsaved changes. Are you sure you want to quit?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) != KDS.System.MessageBox.Responses.YES:
        return
    matMenRunning = False
    btn_menu = False
    mainRunning = False

KDS.Console.init(display, pygame.Surface((1200, 800)), clock, _Offset=(200, 0), _KDS_Quit = LB_Quit)

##################################################

class UnitType(IntEnum):
    Tile = 0
    Item = 1
    Enemy = 2
    Teleport = 3
    Unspecified = 4

class UnitData:
    releasedButtons = { 0: True, 2: True }
    placedOnTile = None
    EMPTYSERIAL = "0000 0000 0000 0000"
    EMPTY = "0000"
    SLOTCOUNT = 4

    def __init__(self, position: Tuple[int, int], serialNumber: str = EMPTYSERIAL):
        self.pos = position
        self.serialNumber = serialNumber
        self.properties = UnitProperties(self)

    def __eq__(self, other) -> bool:
        """ == operator """
        if isinstance(other, UnitData):
            return self.pos == other.pos and self.serialNumber == other.serialNumber and self.properties == other.properties
        return False

    def __ne__(self, other) -> bool:
        """ != operator """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.serialNumber

    def Copy(self) -> UnitData:
        data = UnitData(position=self.pos, serialNumber=self.serialNumber)
        data.properties = self.properties.Copy(parentOverride=data)
        return data

    def setProperties(self, properties: Dict[UnitType, Dict[str, Union[str, int, float, bool]]]):
        self.properties.SetAll(properties)

    def addProperties(self, properties: Dict[UnitType, Dict[str, Union[str, int, float, bool]]]):
        for _type, value in properties.items():
            for k, v in value.items():
                self.properties.Set(_type, k, v)

    def setSerial(self, srlNumber: str):
        Undo.register(self)
        self.serialNumber = f"{srlNumber} 0000 0000 0000"

    def setSerialToSlot(self, srlNumber: str, slot: int):
        if slot >= UnitData.SLOTCOUNT or slot < 0:
            raise ValueError(f"Slot {slot} is an invalid index!")
        Undo.register(self)
        self.serialNumber = self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]

    def getSerial(self, slot: int):
        slot = slot + 1 if slot > 0 else slot
        return self.serialNumber[slot : slot + 4]

    def getSerials(self) -> Tuple[str]:
        return tuple(self.serialNumber.split())

    def getFilledSerials(self):
        serials = self.getSerials()
        return tuple(KDS.Linq.Where(serials, lambda s: s != UnitData.EMPTY))

    def addSerial(self, srlNumber):
        srlist = self.getSerials()
        for index, number in enumerate(srlist):
            if int(number) == 0:
                if srlNumber not in srlist:
                    self.setSerialToSlot(srlNumber, index)
                else: KDS.Logging.info(f"Serial {srlNumber} already in {self.pos}!", True)
                return
        KDS.Logging.info(f"No empty slots at {self.pos} available for serial {srlNumber}!", True)

    def insertSerial(self, srlNumber):
        srlist = self.getSerials()
        for fakeIndex, number in enumerate(reversed(srlist)):
            if fakeIndex == 0:
                if int(number) != 0:
                    KDS.Logging.info(f"No empty slots at {self.pos} available to insert serial {srlNumber}!", True)
                    return
            else:
                self.setSerialToSlot(number, len(srlist) - fakeIndex) # The second argument will be one higher than the real index.
        self.setSerialToSlot(srlNumber, 0)

    def removeSerial(self):
        srlist = self.getSerials()
        for index, number in reversed(list(enumerate(srlist))):
            if int(number) != 0:
                self.setSerialToSlot(UnitData.EMPTY, index)
                return

    def removeSerialFromStart(self):
        srlist = self.getSerials()
        for fakeIndex, number in enumerate(reversed(srlist)):
            index = len(srlist) - fakeIndex - 1
            if index <= 0: # If it's the last tile, the process is complete.
                return

            self.setSerialToSlot(number, index - 1)
            if fakeIndex == 0:
                self.setSerialToSlot(UnitData.EMPTY, index)

    def hasTile(self):
        split: Tuple[str] = self.getSerials()
        return KDS.Linq.Any(split, lambda s: len(s) > 0 and s[0] == "0" and s != UnitData.EMPTY)

    def resetSerial(self):
        Undo.register(self)
        self.serialNumber = UnitData.EMPTYSERIAL
        self.properties.RemoveUnused()

    @staticmethod
    def toSerialString(srlNumber: str):
        return f"{srlNumber} 0000 0000 0000"

    @staticmethod
    def renderUpdate(Surface: pygame.Surface, scroll: List[int], renderList: List[List[UnitData]], brush: BrushData, allowTilePlacement: bool = True, middleMouseOnDown: bool = False) -> List[List[UnitData]]:
        _TYPECOLORS = {
            UnitType.Tile: KDS.Colors.EmeraldGreen,
            UnitType.Item: KDS.Colors.RiverBlue,
            UnitType.Enemy: KDS.Colors.AviatorRed,
            UnitType.Teleport: KDS.Colors.Yellow,
            UnitType.Unspecified: KDS.Colors.Magenta
        }

        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        scroll[0] = KDS.Math.Clamp(scroll[0], 0, gridSize[0] - 1)
        scroll[1] = KDS.Math.Clamp(scroll[1], 0, gridSize[1] - 1)
        bpos = (0, 0)

        tip_renders = []
        mpos = pygame.mouse.get_pos()
        mpos_scaled = (mpos[0] + scroll[0] * scalesize, mpos[1] + scroll[1] * scalesize)
        pygame.draw.rect(Surface, (80, 30, 30), pygame.Rect(0, 0, (gridSize[0] - scroll[0]) * scalesize, (gridSize[1] - scroll[1]) * scalesize))
        doorRenders: List[Tuple[pygame.Surface, Tuple[int, int]]] = []
        overlayRenders: List[Tuple[pygame.Surface, Tuple[int, int]]] = []
        for row in renderList[scroll[1] : KDS.Math.CeilToInt(scroll[1] + display_size[1] / scalesize)]:
            row: List[UnitData]
            for unit in row[scroll[0] : KDS.Math.CeilToInt(scroll[0] + display_size[0] / scalesize)]:
                normalBlitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                unitRect = pygame.Rect(unit.pos[0] * scalesize, unit.pos[1] * scalesize, scalesize, scalesize)
                srlist = unit.getSerials()
                overlayTileprops = str(unit.properties.Get(UnitType.Unspecified, "overlay", "None"))
                if overlayTileprops != "None":
                    unscaledOverlayTex = Atextures[overlayTileprops[0]][overlayTileprops]
                    unscaledOverlayTexSize = unscaledOverlayTex.get_size()
                    overlayTex = pygame.transform.scale(unscaledOverlayTex, (int(unscaledOverlayTexSize[0] * scaleMultiplier), int(unscaledOverlayTexSize[1] * scaleMultiplier)))
                    overlayRenders.append((overlayTex, (normalBlitPos[0], normalBlitPos[1] - overlayTex.get_height() + scalesize))) # Will render some tiles incorrectly
                for index, number in enumerate(srlist):
                    intNumber = int(number)
                    if intNumber != 0:
                        unitTexture = None
                        if number[0] == "3":
                            teleportTextureCheck = int(number[1:])
                            if teleportTextureCheck < 500:
                                unitTexture = Atextures["3"]["3001"]
                            else:
                                unitTexture = Atextures["3"]["3501"]
                        else:
                            try:
                                unitTexture = Atextures[number[0]][number]
                            except KeyError:
                                    KDS.Logging.warning(f"Cannot render unit because texture is not added: {number}", True)

                        if number[0] == "3" and unitRect.collidepoint(mpos_scaled):
                            t_ind = str(int(number[1:]))
                            tip_renders.append(harbinger_font_small.render(t_ind, True, KDS.Colors.AviatorRed))
                            if keys_pressed[K_p]:
                                temp_serial: str = KDS.Console.Start('Set teleport index: (int[0, 999])', True, KDS.Console.CheckTypes.Int(0, 999), defVal=t_ind)
                                if len(temp_serial) > 0:
                                    temp_serial = f"3{int(temp_serial):03d}"
                                    unit.setSerialToSlot(temp_serial, index)

                        if unitTexture != None:
                            unitTextureSize = unitTexture.get_size()
                            scaledUnitTexture = pygame.transform.scale(unitTexture, (int(unitTextureSize[0] * scaleMultiplier), int(unitTextureSize[1] * scaleMultiplier)))
                            blitPos = (normalBlitPos[0], normalBlitPos[1] - scaledUnitTexture.get_height() + scalesize)
                            if number in trueScale:
                                Surface.blit(scaledUnitTexture, (normalBlitPos[0] - scaledUnitTexture.get_width() + scalesize, blitPos[1]))
                            elif intNumber in (23, 24, 25, 26):
                                doorRenders.append((scaledUnitTexture, normalBlitPos))
                            else:
                                checkCollision = unit.properties.Get(UnitType.Tile, "checkCollision", None)
                                if number[0] == "0" and isinstance(checkCollision, bool):
                                    tilepropsOverlay = scaledUnitTexture.convert_alpha()
                                    Surface.blit(scaledUnitTexture, blitPos) # Will render some tiles incorrectly
                                    if not checkCollision:
                                        tilepropsOverlay.fill((0, 0, 0, 64), special_flags=BLEND_RGBA_MULT)
                                        Surface.blit(tilepropsOverlay, blitPos)
                                    else:
                                        KDS.Logging.warning(f"checkCollision forced on at: {unit.pos}. This is generally not recommended.")
                                else:
                                    Surface.blit(scaledUnitTexture, blitPos) # Will render some tiles incorrectly

                            if number[0] == "3":
                                teleportOverlay = pygame.transform.scale(Atextures["3"]["3001"], (scalesize, scalesize))
                                teleportOverlay.set_alpha(100)
                                Surface.blit(teleportOverlay, normalBlitPos)

                if unitRect.collidepoint(mpos_scaled):
                    if keys_pressed[K_f]:
                        autoFill = {}
                        for t in UnitType:
                            autoFill[t.name] = "break"
                        setPropType = str(KDS.Console.Start("Enter Property Type:", True, KDS.Console.CheckTypes.Commands(), commands=autoFill)).lower()
                        propType = KDS.Linq.FirstOrNone(UnitType, lambda t: t.name.lower() == setPropType)
                        if len(setPropType) > 0 and propType != None:
                            setPropKey: str = KDS.Console.Start("Enter Property Key:")
                            if len(setPropKey) > 0:
                                setPropValUnformatted = KDS.Console.Start("Enter Property Value:")
                                if propType == UnitType.Unspecified and setPropKey == "overlay": # Force string for overlay
                                    setPropVal = setPropValUnformatted
                                else:
                                    setPropVal = KDS.Convert.AutoType(setPropValUnformatted, setPropValUnformatted) # If cannot be parsed to int, bool or float; return string
                                unit.properties.Set(propType, setPropKey, setPropVal)
                        elif len(setPropType) > 0:
                            KDS.Logging.warning(f"\"{setPropType}\" could not be parsed to any type!", True)
                    elif keys_pressed[K_o] and not keys_pressed[K_LCTRL]:
                        overlayId = materialMenu(UnitData.EMPTY)
                        if overlayId != UnitData.EMPTY and overlayId[0] in Atextures and overlayId in Atextures[overlayId[0]]:
                            unit.properties.Set(UnitType.Unspecified, "overlay", overlayId)
                        elif overlayId == UnitData.EMPTY:
                            unit.properties.Remove(UnitType.Unspecified, "overlay")
                        else:
                            print(f"Overlay identifier \"{overlayId}\" is invalid.")


                    srlist = unit.getSerials()
                    fld_srls = 0
                    for sr in srlist:
                        if int(sr) != 0: fld_srls += 1
                        else: break
                    if fld_srls > 1:
                        for i in range(fld_srls): tip_renders.append(harbinger_font_small.render(srlist[i], True, KDS.Colors.RiverBlue))

                    if middleMouseOnDown and not keys_pressed[K_LSHIFT]:
                        tempbrushtemp = KDS.Linq.FirstOrNone(unit.getFilledSerials(), lambda s: s != brush.brush)
                        if tempbrushtemp == None:
                            tempbrushtemp = unit.getSerial(0)
                        if not keys_pressed[K_LCTRL]:
                            brush.SetValues(tempbrushtemp)
                        else:
                            brush.SetValues(tempbrushtemp, unit.properties.GetAll())

                    pygame.draw.rect(Surface, (20, 20, 20), (normalBlitPos[0], normalBlitPos[1], scalesize, scalesize), 2)
                    bpos = unit.pos
                    if allowTilePlacement:
                        if mouse_pressed[0]:
                            if not brush.IsEmpty() or keys_pressed[K_c]:
                                if not keys_pressed[K_c]:
                                    if not keys_pressed[K_LSHIFT] and not keys_pressed[K_LCTRL]:
                                        brush.SetOnUnit(unit)
                                    elif UnitData.releasedButtons[0] or UnitData.placedOnTile != unit:
                                        if keys_pressed[K_LSHIFT]:
                                            brush.AddOnUnit(unit)
                                        else: # At this point only CTRL can be pressed.
                                            brush.InsertOnUnit(unit)
                                elif unit.hasTile():
                                    setVal = False
                                    if keys_pressed[K_LALT]:
                                        setVal = True
                                    unit.properties.Set(UnitType.Tile, "checkCollision", setVal)
                        elif mouse_pressed[2]:
                            if not keys_pressed[K_c]:
                                if not keys_pressed[K_LSHIFT] and not keys_pressed[K_LCTRL]:
                                    unit.resetSerial()
                                elif UnitData.releasedButtons[2] or UnitData.placedOnTile != unit:
                                    if keys_pressed[K_LSHIFT]:
                                        unit.removeSerial()
                                    else: # At this point only CTRL can be pressed.
                                        unit.removeSerialFromStart()
                            else:
                                unit.properties.Remove(UnitType.Tile, "checkCollision")
                    UnitData.placedOnTile = unit

                    tipProps = unit.properties.GetAll()
                    for _type in tipProps:
                        color = _TYPECOLORS[_type]
                        for k, v in tipProps[_type].items():
                            if k == "checkCollision":
                                continue
                            rendered_tip = harbinger_font_small.render(f"{k}: ({type(v).__name__}) {v}", True, color)
                            tip_renders.append(rendered_tip)

        for doorTex, doorPos in doorRenders:
            Surface.blit(doorTex, doorPos)

        for ovs, ovp in overlayRenders:
            Surface.blit(ovs, ovp)

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

        mousePosText = harbinger_font.render(f"({bpos[0]}, {bpos[1]})", True, KDS.Colors.AviatorRed)
        display.blit(mousePosText, (display_size[0] - mousePosText.get_width(), display_size[1] - mousePosText.get_height()))

        UnitData.releasedButtons[0] = False if mouse_pressed[0] else True
        UnitData.releasedButtons[2] = False if mouse_pressed[2] else True

        return renderList

class UnitProperties:
    def __init__(self, parent: UnitData) -> None:
        self.parent = parent
        self.values: Dict[UnitType, Dict[str, Union[str, int, float, bool]]] = {}

    def __eq__(self, other) -> bool:
        """ == operator """
        if isinstance(other, UnitProperties):
            return self.values == other.values # Won't check parents
        return False

    def __ne__(self, other) -> bool:
        """ != operator """
        return not self.__eq__(other)

    def Set(self, _type: UnitType, key: str, value: Union[str, int, float, bool]) -> None:
        if _type not in self.values:
            self.values[_type] = {}
        Undo.register(self.parent)
        self.values[_type][key] = value

    def SetAll(self, data: Dict[UnitType, Dict[str, Union[str, int, float, bool]]]):
        Undo.register(self.parent)
        self.values = {k: {ik: iv for ik, iv in v.items()} for k, v in data.items()}

    def Remove(self, _type: UnitType, key: str) -> None:
        """Removes the specified key in type if found.

        Args:
            _type (UnitType): The type specifying what the key controls.
            key (str): The key to remove.
        """
        if _type in self.values and key in self.values[_type]:
            Undo.register(self.parent)
            self.values[_type].pop(key)
            if len(self.values[_type]) < 1:
                self.values.pop(_type)

    def Get(self, _type: UnitType, key: str, default: Optional[Union[str, int, float, bool]]) -> Optional[Union[str, int, float, bool]]:
        if _type not in self.values or key not in self.values[_type]:
            return default
        return self.values[_type][key]

    def GetAll(self) -> Dict[UnitType, Dict[str, Union[str, int, float, bool]]]:
        return {k: {ik: iv for ik, iv in v.items()} for k, v in self.values.items()}

    def RemoveUnused(self):
        splitValues = self.parent.getSerials()
        for _type in self.values.copy():
            if _type == UnitType.Unspecified:
                continue

            if not KDS.Linq.Any(splitValues, lambda v: int(v[0]) == _type.value and int(v) != 0):
                self.values.pop(_type)

    def Copy(self, parentOverride: UnitData = None) -> UnitProperties:
        new = UnitProperties(parentOverride if parentOverride != None else self.parent)
        new.values = {k: {ik: iv for ik, iv in v.items()} for k, v in self.values.items()} #deepcopy replacement. Some values are not copied, because they are single-instance variables.
        return new

    def __str__(self) -> Optional[str]:
        self.RemoveUnused()
        if KDS.Linq.All(self.values.values(), lambda v: len(v) < 1): # The dictionary should be empty if there are no values, but let's check just in case.
            return ""
        key = f"{self.parent.pos[0]}-{self.parent.pos[1]}"
        value = json.dumps(self.values, separators=(',', ':')) # Separators ensure that there are no useless spaces in the file.
        return f"\"{key}\":{value}" # Puts key in quotes so that it is valid JSON

    @staticmethod
    def Serialize(grid: List[List[UnitData]]) -> str:
        strings: List[str] = []
        for row in grid:
            for unit in row:
                pString = str(unit.properties)
                if len(pString) > 0:
                    strings.append(pString)
        if len(strings) < 1: # If there is nothing to save, return empty.
            return ""
        result = "{\n" + "".join(f"{s},\n" for s in strings).removesuffix(",\n") + "\n}"
        return result

    @staticmethod
    def Deserialize(jsonString: str, grid: List[List[UnitData]]) -> None:
        deserialized: Dict[str, Dict[str, Dict[str, Union[str, int, float, bool]]]] = json.loads(jsonString)
        for row in grid:
            for unit in row:
                key = f"{unit.pos[0]}-{unit.pos[1]}"
                if key in deserialized:
                    unitProp = UnitProperties(unit)
                    unitProp.values = {UnitType(int(k)): v for k, v in deserialized[key].items()}
                    unit.properties = unitProp

class BrushData:
    def __init__(self) -> None:
        self.brush: str = UnitData.EMPTY
        self.properties: Dict[UnitType, Dict[str, Union[str, int, float, bool]]] = {}

    def SetValues(self, brush: str = UnitData.EMPTY, properties: Dict[UnitType, Dict[str, Union[str, int, float, bool]]] = {}):
        self.brush = brush
        self.properties = {}
        if not self.IsEmpty():
            correctType = KDS.Linq.FirstOrNone(properties, lambda t: t.value == int(brush[0]))
            if correctType != None:
                propValues = properties[correctType]
                self.properties = {correctType: {ik: iv for ik, iv in propValues.items()}}

    def SetOnUnit(self, unit: UnitData):
        unit.setSerial(self.brush)
        unit.setProperties(self.properties)
        unit.properties.RemoveUnused()

    def AddOnUnit(self, unit: UnitData):
        unit.addSerial(self.brush)
        unit.addProperties(self.properties)
        unit.properties.RemoveUnused()

    def InsertOnUnit(self, unit: UnitData):
        unit.insertSerial(self.brush)
        unit.addProperties(self.properties)
        unit.properties.RemoveUnused()

    def IsEmpty(self):
        return self.brush == UnitData.EMPTY
brush = BrushData()

def loadGrid(size: Tuple[int, int]):
    rlist = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(UnitData((x, y)))
        rlist.append(row)
    global gridSize
    gridSize = size
    return rlist

def resizeGrid(size: Tuple[int, int], grid: list):
    grid_size = (len(grid[0]), len(grid))
    size_difference = (size[0] - grid_size[0], size[1] - grid_size[1])
    if size_difference[1] > 0:
        for y in range(grid_size[1], size[1]):
            row = []
            for x in range(grid_size[0]):
                row.append(UnitData((x, y)))
            grid.append(row)
    else:
        for y in range(abs(size_difference[1])):
            grid.pop()
    if size_difference[0] > 0:
        for y in range(len(grid)):
            row = grid[y]
            while len(row) < size[0]:
                row.append(UnitData(((len(row)), y)))
    else:
        for row in grid:
            while len(row) > size[0]:
                row.pop()
    global gridSize
    gridSize = size
    return grid

def saveMap(grid: List[List[UnitData]], name: str):
    outputString = ''
    for row in grid:
        for unit in row:
            outputString += str(unit) + " / "
        outputString = outputString.removesuffix(" / ") + "\n"
    with open(name, 'w', encoding="utf-8") as f:
        f.write(outputString)
    #region Tile Props
    propertiesPath = os.path.join(os.path.dirname(name), "properties.kdf")
    propertiesString = UnitProperties.Serialize(grid)
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
    Undo.clear()

def saveMapName():
    global currentSaveName, grid
    savePath = filedialog.asksaveasfilename(initialfile="level", defaultextension=".dat", filetypes=(("Data file", "*.dat"), ("All files", "*.*")))
    if len(savePath) > 0:
        saveMap(grid, savePath)
        currentSaveName = savePath

def loadMap(path: str) -> bool: # bool indicates if the map loading was succesful
    global currentSaveName, gridSize, grid
    if path == None or len(path) < 1:
        KDS.Logging.info(f"Path \"{path}\" of map file is not valid.", True)
        return False
    if not path.endswith(".dat"):
        KDS.Logging.info(f"Map file at path \"{path}\" is not a valid type.", True)
        return False
    if Undo.index + Undo.overflowCount > 0 and KDS.System.MessageBox.Show("Unsaved Changes.", "There are unsaved changes. Do you want to save them?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
        if not currentSaveName:
            saveMapName()
        else:
            saveMap(grid, currentSaveName)

    temporaryGrid = None
    with open(path, 'r') as f:
        contents = f.read().splitlines()
        while len(contents[-1]) < 1: contents = contents[:-1]

    maxW = 0
    for c in contents:
        maxW = max(maxW, len(c.split("/")))
    temporaryGrid = loadGrid((maxW, len(contents)))

    for row, rRow in zip(contents, temporaryGrid):
        for unit, rUnit in zip(row.split("/"), rRow):
            unit = unit.strip(" ")
            #region Fixing Broken Serials
            while len(unit) < len(UnitData.EMPTYSERIAL):
                if not unit.endswith("0000"):
                    unit += "0"
                else:
                    unit += " "
            if len(unit) > len(UnitData.EMPTYSERIAL):
                unit = unit[:len(UnitData.EMPTYSERIAL) - 1]
            #endregion
            rUnit.serialNumber = unit

    currentSaveName = path

    grid = temporaryGrid
    fpath = os.path.join(os.path.dirname(path), "properties.kdf")
    if os.path.isfile(fpath):
        with open(fpath, 'r', encoding="utf-8") as f:
            UnitProperties.Deserialize(f.read(), grid)

    Undo.clear()
    return True

def openMap() -> bool: #Returns True if the operation was succesful
    global currentSaveName, gridSize, grid
    fileName = filedialog.askopenfilename(filetypes=(("Data file", "*.dat"), ("All files", "*.*")))
    if fileName == None or len(fileName) < 1:
        return False
    return loadMap(fileName)

commandTree = {
    "set": {
        "brush": brushNames,
        **brushNames
    },
    "add": {
        "rows": "break",
        "cols": "break"
    },
    "rmv": {
        "rows": "break",
        "cols": "break",
        "stacks": "break"
    }
}
def consoleHandler(commandlist):
    global brush, grid, dragRect
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if len(commandlist) < 3:
                KDS.Console.Feed.append("Invalid set command.")
                return
            if commandlist[2] in brushNames:
                brush.SetValues(brushNames[commandlist[2]])
                KDS.Console.Feed.append(f"Brush set: [{brushNames[commandlist[2]]}: {commandlist[2]}]")
            elif commandlist[2] in brushNames.values():
                brush.SetValues(commandlist[2])
                KDS.Console.Feed.append(f"Brush set: [{commandlist[2]}: {list(brushNames.keys())[list(brushNames.values()).index(commandlist[2])]}]")
            else: KDS.Console.Feed.append("Invalid brush.")
        elif dragRect != None:
            if commandlist[1] in brushNames:
                Selected.Set(UnitData.toSerialString(brushNames[commandlist[1]]))
                Selected.Update()
                KDS.Console.Feed.append(f"Filled [{dragRect.topleft}, {dragRect.bottomright}] with [{brushNames[commandlist[1]]}: {commandlist[1]}]")
            elif commandlist[1] in brushNames.values():
                Selected.Set(UnitData.toSerialString(commandlist[2]))
                Selected.Update()
                KDS.Console.Feed.append(f"Filled [{dragRect.topleft}, {dragRect.bottomright}] with [{commandlist[2]}: {list(brushNames.keys())[list(brushNames.values()).index(commandlist[2])]}]")
        else: KDS.Console.Feed.append("Invalid set command.")
    elif commandlist[0] == "add":
        if commandlist[1] == "rows":
            if commandlist[2].isnumeric:
                resizeGrid((gridSize[0], gridSize[1] + int(commandlist[2])), grid)
                KDS.Console.Feed.append(f"Added {int(commandlist[2])} rows.")
            else: KDS.Console.Feed.append("Row add count is not a valid value.")
        elif commandlist[1] == "cols":
            if commandlist[2].isnumeric:
                resizeGrid((gridSize[0] + int(commandlist[2]), gridSize[1]), grid)
                KDS.Console.Feed.append(f"Added {int(commandlist[2])} columns.")
            else: KDS.Console.Feed.append("Column add count is not a valid value.")
        else: KDS.Console.Feed.append("Invalid add command.")
    elif commandlist[0] == "rmv":
        if commandlist[1] == "rows":
            if commandlist[2].isnumeric:
                resizeGrid((gridSize[0], gridSize[1] - int(commandlist[2])), grid)
                KDS.Console.Feed.append(f"Removed {int(commandlist[2])} rows.")
            else: KDS.Console.Feed.append("Row add count is not a valid value.")
        elif commandlist[1] == "cols":
            if commandlist[2].isnumeric:
                resizeGrid((gridSize[0] - int(commandlist[2]), gridSize[1]), grid)
                KDS.Console.Feed.append(f"Removed {int(commandlist[2])} columns.")
            else: KDS.Console.Feed.append("Column add count is not a valid value.")
        elif commandlist[1] == "stacks":
            for row in grid:
                for unit in row:
                    unit: UnitData
                    srlist = unit.getSerials()
                    for i in range(1, len(srlist)):
                        unit.setSerialToSlot(UnitData.EMPTY, i)
        else: KDS.Console.Feed.append("Invalid remove command.")
    else: KDS.Console.Feed.append("Invalid command.")

def materialMenu(previousMaterial: str) -> str:
    global matMenRunning
    matMenRunning = True
    rscroll = 0
    BLOCKSIZE = 70
    SPACING = (100, 90)
    COLUMNS = 12
    OFFSET = (display_size[0] // 2 - SPACING[0] * COLUMNS // 2 - BLOCKSIZE // 2, 40)

    class selectorRect:
        def __init__(self, pos: Tuple[int, int], serialNumber: str):
            self.pos = pos
            self.rect: pygame.Rect = pygame.Rect(pos[0] * SPACING[0] + OFFSET[0], pos[1] * SPACING[1] + OFFSET[1], BLOCKSIZE, BLOCKSIZE)
            self.serialNumber: str = serialNumber

    selectorRects: List[selectorRect] = []

    y = 0
    x = 0
    for i, collection in enumerate(Atextures):
        for key in Atextures[collection]:
            selectorRects.append(selectorRect((x, y), key))
            x += 1
            if x > COLUMNS:
                x = 0
                y += 1

        if i < len(Atextures) - 1: # Skips the line adding for the last collection
            y += 1
            if x > 0:
                x = 0
                y += 1

    ROWS = y

    while matMenRunning:
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if defaultEventHandler(event):
                continue
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_e:
                    matMenRunning = False
                    return previousMaterial
            elif event.type == MOUSEWHEEL:
                if event.y > 0: rscroll = max(rscroll - 1, 0)
                else: rscroll = int(min((rscroll + 1) * 30, ROWS * SPACING[1] + OFFSET[1]) / 30) # Not floor divided, because (whatever nimittäjä is in english) is a multiple digit value.
        yCalc = rscroll * 30

        tip_renders = []

        mpos = pygame.mouse.get_pos()
        display.fill((20, 20, 20))
        for selection in selectorRects:
            selection: selectorRect
            sorting = selection.serialNumber[0]
            rndY = selection.rect.y - yCalc
            display.blit(KDS.Convert.AspectScale(Atextures[sorting][selection.serialNumber], (BLOCKSIZE, BLOCKSIZE)), (selection.rect.x, rndY))
            if selection.rect.collidepoint(mpos[0], mpos[1] + yCalc):
                pygame.draw.rect(display, (230, 30, 40), (selection.rect.x, rndY, BLOCKSIZE, BLOCKSIZE), 3)
                tip_renders.append(harbinger_font_small.render(selection.serialNumber, True, KDS.Colors.RiverBlue))
                if mouse_pressed[0]:
                    return selection.serialNumber

        if mouse_pressed[0]:
            return UnitData.EMPTY

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
        pygame.display.flip()

    return previousMaterial

def generateLevelProp():
    """
    Generate a levelProp.kdf using this tool.
    """
    dark = KDS.Console.Start("Darkness Enabled: (bool)", False, KDS.Console.CheckTypes.Bool(), autoFormat=True)
    if dark:
        darkness = KDS.Console.Start("Darkness Strength: (int[0, 255])", False, KDS.Console.CheckTypes.Int(0, 255), autoFormat=True)
        player_light = KDS.Console.Start("Player Light: (bool)", False, KDS.Console.CheckTypes.Bool(), defVal="true", autoFormat=True)
    else:
        darkness = 0
        player_light = False

    ambient_light = KDS.Console.Start("Ambient Light Enabled: (bool)", False, KDS.Console.CheckTypes.Bool(), autoFormat=True)
    if ambient_light: ambient_light_tint = KDS.Console.Start("Ambient Light Tint: (int, int, int)", False, KDS.Console.CheckTypes.Tuple(3, 0, 255), autoFormat=True)
    else: ambient_light_tint = (0, 0, 0)

    p_start_pos = KDS.Console.Start("Player Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="100, 100", autoFormat=True)

    k_start_pos = KDS.Console.Start("Koponen Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="200, 200", autoFormat=True)

    tb_start, tb_end = KDS.Console.Start("Time Bonus Range in seconds: (full points: int, no points: int)", False, KDS.Console.CheckTypes.Tuple(2, 0, requireIncrease=True), autoFormat=True)

    savePath = filedialog.asksaveasfilename(initialfile="levelprop", defaultextension=".kdf", filetypes=(("Koponen Data Format", "*.kdf"), ("All files", "*.*")))
    if len(savePath) > 0:
        if os.path.isfile(savePath): os.remove(savePath)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/enabled", dark)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/strength", darkness)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/playerLight", player_light)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/AmbientLight/enabled", ambient_light)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/AmbientLight/tint", ambient_light_tint)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Player/startPos", p_start_pos)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/startPos", k_start_pos)
        KDS.ConfigManager.JSON.Set(savePath, "Data/TimeBonus/start", tb_start)
        KDS.ConfigManager.JSON.Set(savePath, "Data/TimeBonus/end", tb_end)

def upgradeTileProp():
    filename = filedialog.askopenfilename(filetypes=(("Tileprops file", "tileprops.kdf"), ("Koponen Data Format file", "*.kdf"), ("All files", "*.*")))
    if filename == None or len(filename) < 1:
        return
    try:
        with open(filename, "r") as f:
            data: Dict[str, Dict[str, Any]] = json.loads(f.read())
        newData: Dict[str, Dict[int, Dict[str, Any]]] = {}

        for k, v in data.items():
            newData[k] = {}
            for k2, v2 in v.items():
                if k2 != "overlay":
                    if UnitType.Tile.value not in newData[k]: # Adding it if needed, because due to overlays being a different type, this might be empty.
                        newData[k][UnitType.Tile.value] = {}
                    newData[k][UnitType.Tile.value][k2] = v2
                else:
                    if UnitType.Unspecified.value not in newData[k]:
                        newData[k][UnitType.Unspecified.value] = {}
                    newData[k][UnitType.Unspecified.value][k2] = v2

        with open(os.path.join(os.path.dirname(filename), "properties.kdf"), "w", encoding="utf-8") as f:
            f.write(json.dumps(newData, separators=(',', ':'))) # Separators specified to remove useless spaces.

        if KDS.System.MessageBox.Show("Success!", "Tileprops was converted to properties succesfully. Do you want to delete the old tileprops file?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
            os.remove(filename)
    except Exception as e:
        KDS.System.MessageBox.Show("Failure!", "Tileprops conversion failed.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
        KDS.Logging.AutoError(str(e)) # Number probably means a key error

def menu():
    global currentSaveName, brush, grid, gridSize, btn_menu, gamesize, scaleMultiplier, scalesize, mainRunning
    btn_menu = True
    grid = [[]]
    def button_handler(_openMap: bool = False):
        global btn_menu
        if _openMap:
            # Button menu is turned off if openMap was succesful
            btn_menu = not openMap()
        else: btn_menu = False

    newMap_btn = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 450,       125, 400, 200), button_handler, harbinger_font.render("New Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    openMap_btn = KDS.UI.Button(pygame.Rect(display_size[0] // 2 + 50,       125, 400, 200), button_handler, harbinger_font.render("Open Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    upgradeProps_btn = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 450, 425, 400, 100), upgradeTileProp, harbinger_font.render("Upgrade Legacy tileprops", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    genProp_btn = KDS.UI.Button(pygame.Rect(display_size[0] // 2 + 50,       425, 400, 100), generateLevelProp, harbinger_font.render("Generate levelProp.kdf", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    quit_btn = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 150, 650, 300, 100), LB_Quit, harbinger_font.render("Quit", True, KDS.Colors.AviatorRed), (255, 255, 255), (235, 235, 235), (200, 200, 200))

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
        display.fill(KDS.Colors.Gray)
        mouse_pos = pygame.mouse.get_pos()
        newMap_btn.update(display, mouse_pos, clicked)
        openMap_btn.update(display, mouse_pos, clicked, True)
        upgradeProps_btn.update(display, mouse_pos, clicked)
        genProp_btn.update(display, mouse_pos, clicked)
        quit_btn.update(display, mouse_pos, clicked)

        pygame.display.flip()

class Selected:
    units: List[UnitData] = []

    @staticmethod
    def Set(serialOverride: str = None, propertiesOverride: Dict[UnitType, Dict[str, Union[str, int, float, bool]]] = None):
        global grid #                                                                                                        ^^ Undo is now registered each time mouse button 1 (left click) is pressed. Change this if something breaks.
        Selected.SetCustomGrid(grid=grid, serialOverride=serialOverride, propertiesOverride=propertiesOverride)

    @staticmethod
    def SetCustomGrid(grid: List[List[UnitData]], serialOverride: str = None, propertiesOverride: Dict[UnitType, Dict[str, Union[str, int, float, bool]]] = None):
        for unit in Selected.units:
            unitCopy = unit.Copy()
            if serialOverride != None:
                unitCopy.serialNumber = serialOverride
            if propertiesOverride != None:
                unitCopy.properties.values = propertiesOverride
            try:
                grid[unit.pos[1]][unit.pos[0]] = unitCopy
            except IndexError:
                warnSize = f"({len(grid[0])}, {len(grid)})" if len(grid) > 0 else "(<invalid-grid-size>, <invalid-grid-size>)"
                KDS.Logging.warning(f"Index error while setting unit at position: \"{unit.pos}\". Grid size: {warnSize}")

    @staticmethod
    def Move(x: int, y: int):
        global dragRect
        for u in Selected.units:
            u.pos = (u.pos[0] + x, u.pos[1] + y)
        dragRect.x += x
        dragRect.y += y

    @staticmethod
    def Update():
        Selected.units = []
        if dragRect == None: return
        for row in grid[dragRect.y:dragRect.y + dragRect.height]:
            for unit in row[dragRect.x:dragRect.x + dragRect.width]:
                Selected.units.append(unit.Copy())

    @staticmethod
    def Get():
        Selected.Update()
        Selected.Set(serialOverride=UnitData.EMPTYSERIAL, propertiesOverride={})

    @staticmethod
    def ToString(serializeProperties: bool = False) -> Union[str, Tuple[str, str]]:
        global dragRect

        units2d: Dict[int, Dict[int, UnitData]] = {} # Dictionaries are ordered
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
            return output, UnitProperties.Serialize(unitsNormalizedPositions)

    @staticmethod
    def FromString(string: str, properties: str = None):
        global dragRect
        Selected.units: List[UnitData] = []
        contents = string.splitlines()
        while len(contents[-1]) < 1: contents = contents[:-1]

        offset = dragRect.topleft if dragRect != None else (0, 0)
        maxX = 0
        for y, row in enumerate(contents):
            for x, unit in enumerate(row.split("/")):
                maxX = max(maxX, x)
                Selected.units.append(UnitData((x, y), unit.strip(" ")))
        if properties != None:
            UnitProperties.Deserialize(properties, [Selected.units]) # Should be fine since deserialize doesn't actually use the indexes of units in list
        for u in Selected.units:
            u.pos = (u.pos[0] + offset[0], u.pos[1] + offset[1])
        dragRect = pygame.Rect(offset[0], offset[1], maxX + 1, len(contents)) if maxX > 0 and len(contents) > 0 else None
                                                    # ^^ Need to add one... I don't know why.

def defaultEventHandler(event, ignoreEventOfType: int = None) -> bool:
    if event.type == ignoreEventOfType:
        return False
    if event.type == QUIT:
        LB_Quit()
        return True # Return True if you event handling can be stopped
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

def main():
    global currentSaveName, brush, grid, gridSize, btn_menu, gamesize, scaleMultiplier, scalesize, mainRunning, dragRect

    menu()
    if not mainRunning: return

    display.fill(KDS.Colors.Black)

    def zoom(add: int, scroll: List[int], grid: List[List[UnitData]]):
        global scalesize, scaleMultiplier
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_scaled = (KDS.Math.FloorToInt(mouse_pos[0] / scalesize + scroll[0]), KDS.Math.FloorToInt(mouse_pos[1] / scalesize + scroll[1]))
        hitPos = grid[int(KDS.Math.Clamp(mouse_pos_scaled[1], 0, gridSize[1] - 1))][int(KDS.Math.Clamp(mouse_pos_scaled[0], 0, gridSize[0] - 1))].pos
        scalesize = KDS.Math.Clamp(scalesize + add, 1, 256)
        scaleMultiplier = scalesize / gamesize
        mouse_pos_scaled = (KDS.Math.FloorToInt(mouse_pos[0] / scalesize + scroll[0]), KDS.Math.FloorToInt(mouse_pos[1] / scalesize + scroll[1]))
        scroll[0] += hitPos[0] - mouse_pos_scaled[0]
        scroll[1] += hitPos[1] - mouse_pos_scaled[1]

    if grid == None:
        g = KDS.Console.Start("Grid Size: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000)).replace(" ", "").split(",")

        gridSize = (int(g[0]), int(g[1]))
        grid = loadGrid(gridSize)

    inputConsole_output = None
    allowTilePlacement = True

    DebugMode = False

    dragStartPos = None
    dragPos = None
    selectTrigger = False
    brushTrigger = True

    mouse_pos_beforeMove = pygame.mouse.get_pos()
    scroll_beforeMove = scroll
    while mainRunning:
        middleMouseOnDown = False
        pygame.key.set_repeat(500, 31)
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get(): #Event loop
            if defaultEventHandler(event):
                continue
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    selectTrigger = True
                elif event.button == 2:
                    mouse_pos_beforeMove = mouse_pos
                    scroll_beforeMove = scroll.copy()
                    middleMouseOnDown = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    allowTilePlacement = True
            elif event.type == KEYDOWN:
                if event.key == K_z or event.key == K_y:
                    if keys_pressed[K_LCTRL]:
                        Undo.request(event.key == K_y)
                        Selected.Update()
                elif event.key == K_t:
                    inputConsole_output = KDS.Console.Start("Enter Command:", True, KDS.Console.CheckTypes.Commands(), commands=commandTree, showFeed=True, autoFormat=True, enableOld=True)
                elif event.key == K_r:
                    resize_output = KDS.Console.Start("New Grid Size: (int, int)", True, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000), defVal=f"{gridSize[0]}, {gridSize[1]}", autoFormat=True)
                    if resize_output != None: grid = resizeGrid((int(resize_output[0]), int(resize_output[1])), grid)
                elif event.key == K_e:
                    brush.SetValues(materialMenu(brush.brush))
                    allowTilePlacement = False
                elif event.key == K_F3:
                    DebugMode = not DebugMode
                    KDS.Logging.Profiler(DebugMode)
                elif event.key == K_DELETE:
                    Selected.Set(UnitData.EMPTYSERIAL)
                    Selected.Update()
                elif event.key == K_d:
                    if keys_pressed[K_LCTRL]:
                        Selected.Set()
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
                        dragRect = pygame.Rect(0, 0, gridSize[0], gridSize[1])
                        Selected.Get()
                elif event.key == K_c:
                    if keys_pressed[K_LCTRL]:
                        try:
                            toClipboard = Selected.ToString(serializeProperties=True)
                            if not isinstance(toClipboard, tuple) or len(toClipboard) != 2:
                                raise ValueError(f"Clipboard data (type: from) is an incorrect type. Tuple of length 2 expected; got: \"{toClipboard}\".")
                            pygame.scrap.put("text/plain;charset=utf-8", bytes(f"KDS_LevelBuilder_Clipboard_Copy_{toClipboard[0]}??{toClipboard[1]}", "utf-8"))
                        except Exception:
                            KDS.Logging.AutoError(f"Copy to clipboard failed. Exception: {traceback.format_exc()}")
                elif event.key == K_v:
                    if keys_pressed[K_LCTRL]:
                        try:
                            fromClipboard = pygame.scrap.get("text/plain;charset=utf-8")
                            if fromClipboard:
                                if isinstance(fromClipboard, bytes):
                                    fromClipboard = fromClipboard.decode("utf-8")
                                else:
                                    fromClipboard = str(fromClipboard)
                                if fromClipboard.startswith("KDS_LevelBuilder_Clipboard_Copy_"):
                                    fromClipboard = fromClipboard.removeprefix("KDS_LevelBuilder_Clipboard_Copy_").split("??", 1)
                                    if len(fromClipboard) != 2:
                                        raise ValueError(f"Clipboard data (type: to) is an incorrect type. Tuple of length 2 expected; got: \"{fromClipboard}\".")
                                    if len(fromClipboard[1]) > 0 and not fromClipboard[1].isspace():
                                        Selected.FromString(fromClipboard[0], fromClipboard[1])
                                    else:
                                        KDS.Logging.info("Skipped properties for pasting from clipboard, because it is either empty or whitespace.")
                        except Exception:
                            KDS.Logging.AutoError(f"Paste from clipboard failed. Exception: {traceback.format_exc()}")
            elif event.type == MOUSEWHEEL:
                if keys_pressed[K_LSHIFT]:
                    scroll[0] -= event.y
                elif keys_pressed[K_LCTRL]:
                    zoom(event.y * 5, scroll, grid)
                else:
                    scroll[1] -= event.y
                scroll[0] += event.x

        if mouse_pressed[1] and keys_pressed[K_LSHIFT]:
            mid_scroll_x = (mouse_pos_beforeMove[0] - mouse_pos[0]) // scalesize
            mid_scroll_y = (mouse_pos_beforeMove[1] - mouse_pos[1]) // scalesize
            if mid_scroll_x > 0 or mid_scroll_y > 0 or mid_scroll_x < 0 or mid_scroll_y < 0:
                scroll[0] = scroll_beforeMove[0] + mid_scroll_x
                scroll[1] = scroll_beforeMove[1] + mid_scroll_y

        if keys_pressed[K_s] and keys_pressed[K_LCTRL]:
            if not currentSaveName:
                saveMapName()
            else:
                saveMap(grid, currentSaveName)
        if keys_pressed[K_s] and keys_pressed[K_LCTRL] and keys_pressed[K_LSHIFT]:
            saveMapName()

        if keys_pressed[K_o] and keys_pressed[K_LCTRL]:
            openMapSuccess = openMap()
            if not openMapSuccess:
                KDS.Logging.info("Map opening cancelled.", True)

        if inputConsole_output != None:
            consoleHandler(inputConsole_output)
            inputConsole_output = None

        display.fill((30,20,60))
        grid = UnitData.renderUpdate(display, scroll, grid, brush, allowTilePlacement, middleMouseOnDown)

        undoTotal = Undo.index + Undo.overflowCount
        if undoTotal > 0:
            if undoTotal < 50:
                _color = KDS.Colors.Yellow
            elif 100 >= undoTotal >= 50: _color = KDS.Colors.Orange
            else: _color = KDS.Colors.Red
            pygame.draw.circle(display, _color, (10, 10), 5)
        if not brush.IsEmpty():
            tmpScaled = KDS.Convert.AspectScale(Atextures[brush.brush[0]][brush.brush], (68, 68))
            display.blit(tmpScaled, (display_size[0] - 10 - tmpScaled.get_width(), 10))
            if brushTrigger:
                selectTrigger = False
                dragStartPos = None
                dragRect = None
                Selected.Set()
                brushTrigger = False
        elif selectTrigger and mouse_pressed[0] and not keys_pressed[K_c]:
            if dragStartPos == None:
                Selected.Set()
                dragStartPos = (int((mouse_pos[0] + scroll[0] * scalesize) / scalesize), int((mouse_pos[1] + scroll[1] * scalesize) / scalesize))
            dragPos = (int(mouse_pos[0] / scalesize + scroll[0]), int(mouse_pos[1] / scalesize + scroll[1]))
            dragRect = pygame.Rect(min(dragPos[0], dragStartPos[0]), min(dragPos[1], dragStartPos[1]), abs(dragStartPos[0] - dragPos[0]) + 1, abs(dragStartPos[1] - dragPos[1]) + 1)
            Selected.Update()
        elif dragStartPos != None:
            selectTrigger = False
            dragStartPos = None
            Selected.Get()
        if brush.IsEmpty(): brushTrigger = True
        if mouse_pressed[2] and dragRect != None and not keys_pressed[K_c]:
            selectTrigger = False
            dragStartPos = None
            dragRect = None
            Selected.Set()
            Selected.Update()

        if len(Selected.units) > 0:
            for unit in Selected.units:
                srlist = unit.getSerials()
                normalBlitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                for number in srlist:
                    blitTex = None
                    if number[0] == '3':
                        blitTex = Atextures["3"]["3001"]
                    elif number != UnitData.EMPTY:
                        try:
                            blitTex = Atextures[number[0]][number]
                        except KeyError:
                                KDS.Logging.warning(f"Cannot render unit because texture is not added: {srlist}", True)
                    if blitTex != None:
                        scaledBlitTex = pygame.transform.scale(blitTex, (int(blitTex.get_width() * scaleMultiplier), int(blitTex.get_height() * scaleMultiplier)))
                        blitPos = (normalBlitPos[0], normalBlitPos[1] - scaledBlitTex.get_height() + scalesize)
                        if number in trueScale:
                            display.blit(scaledBlitTex, (normalBlitPos[0] - scaledBlitTex.get_width() + scalesize, blitPos[1]))
                        else:
                            display.blit(scaledBlitTex, blitPos)

        if dragRect != None and dragRect.width > 0 and dragRect.height > 0:
            selectDrawRect = pygame.Rect((dragRect.x - scroll[0]) * scalesize, (dragRect.y - scroll[1]) * scalesize, dragRect.width * scalesize, dragRect.height * scalesize)
            selectDraw = pygame.Surface(selectDrawRect.size)
            selectDraw.fill(KDS.Colors.White)
            pygame.draw.rect(selectDraw, KDS.Colors.Black, (0, 0, *selectDraw.get_size()), scalesize // 8)
            selectDraw.set_alpha(64)
            display.blit(selectDraw, (selectDrawRect.x, selectDrawRect.y))

        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))

            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = harbinger_font.render(fps_text, True, KDS.Colors.White)
            display.blit(fps_text, (10, 10))

        pygame.display.flip()
        clock.tick_busy_loop()

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

pygame.quit()

""" KEYMAP
    [Normal]
    Middle Mouse: Get Serial
    Middle Mouse + SHIFT: Move Camera
    Middle Mouse + CTRL: Get Serial with Properties
    Left Mouse: Set Serial
    Left Mouse + SHIFT: Add Serial At Top
    Left Mouse + CTRL: Insert Serial At Bottom
    Right Mouse: Reset Serial
    Right Mouse + SHIFT: Remove Serial From Top
    Right Mouse + CTRL: Remove Serial From Bottom
    Left Mouse + C: No Collision
    Left Mouse + ALT + C: Force Collision
    Right Mouse + C: Remove Collision Attribute
    Right Mouse + ALT + C: Remove Collision Attribute
    E: Open Material Menu
    CTRL + Z: Undo
    CTRL + Y: Redo
    CTRL + D: Duplicate Selection
    CTRL + C: Copy
    CTRL + Z: Paste if possible
    T: Input Console
    R: Resize Map
    F: Set Property
    P: Set teleport index
    O: Set Overlay
    CTRL + A: Select All
    CTRL + S: Save Project
    CTRL + SHIFT + S: Save Project As
    CTRL + O: Open Project

    [Material Menu]
    Escape: Close Material Menu
    E: Close Material Menu
"""

""" Reserved indexes for teleports:
        [0 - 499]: Invisible teleports
        [500 - 999] Teleport-doors
"""