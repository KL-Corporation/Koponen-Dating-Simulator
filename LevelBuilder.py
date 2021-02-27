from __future__ import annotations
#region Import Error
if __name__ != "__main__":
    raise ImportError("Level Builder cannot be imported!")
#endregion

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
from typing import Any, Dict, List, Tuple, Union
import sys
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
import tkinter
from tkinter import filedialog
import json
import traceback

root = tkinter.Tk()
root.withdraw()
pygame.init()
display_size = (1600, 800)
scalesize = 68
gamesize = 34
scaleMultiplier = scalesize / gamesize

display: pygame.Surface = pygame.display.set_mode(display_size, RESIZABLE | HWSURFACE | DOUBLEBUF | SCALED)
pygame.display.set_caption("KDS Level Builder")
pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/levelBuilderIcon.png"))

APPDATA = os.path.join(str(os.getenv('APPDATA')), "KL Corporation", "KDS Level Builder")
LOGPATH = os.path.join(APPDATA, "logs")
os.makedirs(LOGPATH, exist_ok=True)
KDS.Logging.init(APPDATA, LOGPATH)

clock = pygame.time.Clock()
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
harbinger_font_large = pygame.font.Font("Assets/Fonts/harbinger.otf", 55, bold=0, italic=0)
harbinger_font_small = pygame.font.Font("Assets/Fonts/harbinger.otf", 15, bold=0, italic=0)

consoleBackground = pygame.image.load("Assets/Textures/UI/loading_background.png").convert()

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

t_textures = {}
for element in buildData["tile_textures"]:
    srl = f"0{element}"

    elmt = buildData["tile_textures"][element]
    t_textures[srl] = pygame.image.load("Assets/Textures/Tiles/" + elmt).convert()
    t_textures[srl].set_colorkey(KDS.Colors.White)
    brushNames[os.path.splitext(elmt)[0]] = srl

i_textures = {}
for element in buildData["item_textures"]:
    srl = f"1{element}"

    elmt = buildData["item_textures"][element]
    i_textures[srl] = pygame.image.load("Assets/Textures/Items/" + elmt).convert()
    i_textures[srl].set_colorkey(KDS.Colors.White)
    brushNames[os.path.splitext(elmt)[0]] = srl

e_textures = {
    "2001": pygame.image.load("Assets/Textures/Animations/imp_walking_0.png").convert(),
    "2002": pygame.image.load("Assets/Textures/Animations/seargeant_walking_0.png").convert(),
    "2003": pygame.image.load("Assets/Textures/Animations/drug_dealer_walking_0.png").convert(),
    "2004": pygame.image.load("Assets/Textures/Animations/turbo_shotgunner_walking_0.png").convert(),
    "2005": pygame.image.load("Assets/Textures/Animations/mafiaman_walking_0.png").convert(),
    "2006": pygame.image.load("Assets/Textures/Animations/methmaker_idle_0.png").convert(),
    "2007": pygame.image.load("Assets/Textures/Animations/undead_monster_walking_0.png").convert(),
    "2008": pygame.image.load("Assets/Textures/Animations/mummy_walking_0.png").convert()
}

teleports = {
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
brush = "0000"
brushTex = None
teleportTemp = "001"
currentSaveName = ''
grid: List[List[tileInfo]] = [[]]
tileprops: Dict[str, Dict[str, Any]] = {}
gridSize = (0, 0)

dragRect = None

class Undo:
    points: List[Dict[str, Any]] = []
    index = 0
    overflowCount = 0

    @staticmethod
    def register():
        global grid, dragRect, brush, tileprops
        if Undo.index == len(Undo.points) - 1 and Undo.points[Undo.index] == { "grid": grid, "dragRect": dragRect, "brush": brush, "tileprops": tileprops }:
            return

        toSave = {
            "grid": [[t.copy() for t in r] for r in grid], # deepcopy replacement
            "dragRect": dragRect.copy() if dragRect != None else dragRect,
            "tileprops": {k: {ik: iv for ik, iv in v.items()} for k, v in tileprops.items()} # deepcopy replacement. Dictionary replacement keys do not need to be deepcopied, because they are strings.
            #                     ^^ Value doesn't need to be deepcopied, because it can only be str, float, int or bool.
        }

        Selected.SetCustomGrid(toSave["grid"], toSave["tileprops"], registerUndo=False)
        removedCount = len(Undo.points[Undo.index + 1:])
        del Undo.points[Undo.index + 1:]
        if Undo.index == 0 and len(Undo.points) == 1 and removedCount > 0: del Undo.points[0]
        Undo.points.append(toSave)
        while len(Undo.points) > 64:
            del Undo.points[0]
            Undo.overflowCount += 1
        Undo.index = len(Undo.points) - 1

    @staticmethod
    def request(redo: bool = False):
        Undo.index = KDS.Math.Clamp(Undo.index - KDS.Convert.ToMultiplier(redo), 0, len(Undo.points) - 1)

        global grid, dragRect, brush, tileprops
        data = Undo.points[Undo.index]
        grid = data["grid"]
        dragRect = data["dragRect"]
        tileprops = data["tileprops"]

    @staticmethod
    def clear():
        Undo.points.clear()
        Undo.index = 0
        Undo.register()
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

class tileInfo:
    releasedButtons = { 0: True, 2: True }
    placedOnTile = None
    EMPTYSERIAL = "0000 0000 0000 0000 / "

    def __init__(self, position: Tuple[int, int], serialNumber = EMPTYSERIAL):
        self.pos = position
        self.serialNumber = serialNumber

    def __eq__(self, other) -> bool:
        """ == operator """
        if isinstance(other, tileInfo):
            return self.pos == other.pos and self.serialNumber == other.serialNumber
        else: return False

    def __ne__(self, other) -> bool:
        """ != operator """
        return not self.__eq__(other)

    def copy(self) -> tileInfo:
        return tileInfo(position=self.pos, serialNumber=self.serialNumber)

    def setSerial(self, srlNumber: str):
        self.serialNumber = f"{srlNumber} 0000 0000 0000 / "

    def setSerialToSlot(self, srlNumber: str, slot: int):
        #self.serialNumber = self.serialNumber[slot*4] + srlNumber + self.serialNumber[:3-slot]
        #return self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]
        self.serialNumber = self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]

    def getSerial(self, slot: int):
        slot = slot + 1 if slot > 0 else slot
        return self.serialNumber[slot : slot + 4]

    def getSerials(self):
        return tuple(self.serialNumber.replace(" / ", "").split())

    def addSerial(self, srlNumber):
        srlist = self.getSerials()
        for index, number in enumerate(srlist):
            if int(number) == 0:
                if srlNumber not in srlist:
                    if srlNumber not in t_textures:
                        KDS.Logging.warning(f"Cannot add unit because texture is not added: {srlNumber}")
                        return
                    self.setSerialToSlot(srlNumber, index)
                else: KDS.Logging.info(f"Serial {srlNumber} already in {self.pos}!", True)
                return
        KDS.Logging.info(f"No empty slots at {self.pos} available for serial {srlNumber}!", True)

    def removeSerial(self):
        global tileprops
        srlist = self.getSerials()
        for index, number in reversed(list(enumerate(srlist))):
            if int(number) != 0:
                self.setSerialToSlot("0000", index)

                tpp = f"{self.pos[0]}-{self.pos[1]}"
                if tpp in tileprops and "overlay" in tileprops[tpp] and tileprops[tpp]["overlay"] == number:
                    tileprops[tpp].pop("overlay")
                return

    def hasTile(self):
        split: List[str] = self.serialNumber.split(" ")
        for s in split:
            if len(s) > 0 and s[0] == "0" and s != "0000":
                return True
        return False

    def resetSerial(self):
        self.serialNumber = tileInfo.EMPTYSERIAL

    @staticmethod
    def toSerialString(srlNumber: str):
        return f"{srlNumber} 0000 0000 0000 / "

    @staticmethod
    def renderUpdate(Surface: pygame.Surface, scroll: list, renderList: List, brsh: str = "0000", updttiles: bool = True):
        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        brushtemp = brsh
        scroll[0] = KDS.Math.Clamp(scroll[0], 0, gridSize[0] - 1)
        scroll[1] = KDS.Math.Clamp(scroll[1], 0, gridSize[1] - 1)
        bpos = (0, 0)

        tip_renders = []
        mpos = pygame.mouse.get_pos()
        mpos_scaled = (mpos[0] + scroll[0] * scalesize, mpos[1] + scroll[1] * scalesize)
        pygame.draw.rect(Surface, (80, 30, 30), pygame.Rect(0, 0, (gridSize[0] - scroll[0]) * scalesize, (gridSize[1] - scroll[1]) * scalesize))
        for row in renderList[scroll[1] : scroll[1] + display_size[1] // scalesize + 2]:
            row: List[tileInfo]
            for unit in row[scroll[0] : scroll[0] + display_size[0] // scalesize + 2]:
                blitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                unitRect = pygame.Rect(unit.pos[0] * scalesize, unit.pos[1] * scalesize, scalesize, scalesize)
                srlist = unit.getSerials()
                tilepropsPath = f"{unit.pos[0]}-{unit.pos[1]}"
                overlay = Atextures[tileprops[tilepropsPath]["overlay"][0]][tileprops[tilepropsPath]["overlay"]] if tilepropsPath in tileprops and "overlay" in tileprops[tilepropsPath] else None
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
                            if number in trueScale:
                                Surface.blit(scaledUnitTexture, (blitPos[0] - scaledUnitTexture.get_width() + scalesize, blitPos[1] - scaledUnitTexture.get_height() + scalesize))
                            elif intNumber in (23, 24, 25, 26):
                                Surface.blit(scaledUnitTexture, (blitPos[0], blitPos[1]))
                            else:
                                if number[0] == "0" and tilepropsPath in tileprops:
                                    tilepropsOverlay = scaledUnitTexture.convert_alpha()
                                    Surface.blit(scaledUnitTexture, (blitPos[0], blitPos[1] - scaledUnitTexture.get_height() + scalesize))
                                    if "checkCollision" in tileprops[tilepropsPath]:
                                        if not tileprops[tilepropsPath]["checkCollision"]:
                                            tilepropsOverlay.fill((0, 0, 0, 64), special_flags=BLEND_RGBA_MULT)
                                            Surface.blit(tilepropsOverlay, (blitPos[0], blitPos[1] - scaledUnitTexture.get_height() + scalesize))
                                        else:
                                            KDS.Logging.warning(f"checkCollision forced on at: {unit.pos}. This is generally not recommended.")
                                else:
                                    Surface.blit(scaledUnitTexture, (blitPos[0], blitPos[1] - scaledUnitTexture.get_height() + scalesize))

                            if number[0] == "3":
                                teleportOverlay = pygame.transform.scale(Atextures["3"]["3001"], (scalesize, scalesize))
                                teleportOverlay.set_alpha(100)
                                Surface.blit(teleportOverlay, (blitPos[0], blitPos[1] - teleportOverlay.get_height() + scalesize))

                if overlay != None:
                    overlay = pygame.transform.scale(overlay, (int(overlay.get_width() * scaleMultiplier), int(overlay.get_height() * scaleMultiplier)))
                    Surface.blit(overlay, (blitPos[0], blitPos[1] - overlay.get_height() + scalesize))

                if unitRect.collidepoint(mpos_scaled):
                    if keys_pressed[K_f]:
                        setPropKey: str = KDS.Console.Start("Enter Property Key:")
                        if len(setPropKey) > 0:
                            setPropValUnformatted = KDS.Console.Start("Enter Property Value:")
                            setPropVal = KDS.Convert.AutoType(setPropValUnformatted)
                            if setPropVal != None:
                                if tilepropsPath not in tileprops:
                                    tileprops[tilepropsPath] = {}
                                if setPropKey == "overlay":
                                    # It will be possible to break the system by changing the overlay without
                                    # removing the old overlay, but hopefully our users aren't that stupid...
                                    tileprops[tilepropsPath][setPropKey] = setPropValUnformatted
                                else:
                                    tileprops[tilepropsPath][setPropKey] = setPropVal
                            else: KDS.Logging.warning(f"Value {setPropValUnformatted} could not be parsed into any type.", True)

                    srlist = unit.getSerials()
                    fld_srls = 0
                    for sr in srlist:
                        if int(sr) != 0: fld_srls += 1
                        else: break
                    if fld_srls > 1:
                        for i in range(fld_srls): tip_renders.append(harbinger_font_small.render(srlist[i], True, KDS.Colors.RiverBlue))

                    if mouse_pressed[1] and not keys_pressed[K_LSHIFT]:
                        brushtemp = unit.getSerial(0)
                    pygame.draw.rect(Surface, (20, 20, 20), (blitPos[0], blitPos[1], scalesize, scalesize), 2)
                    bpos = unit.pos
                    if mouse_pressed[0] and updttiles:
                        if brsh != "0000":
                            if not keys_pressed[K_c]:
                                if not keys_pressed[K_LSHIFT]:
                                    unit.setSerial(brsh)
                                elif tileInfo.releasedButtons[0] or tileInfo.placedOnTile != unit: unit.addSerial(brsh)
                            elif unit.hasTile():
                                if not keys_pressed[K_LALT]:
                                    tileprops[f"{unit.pos[0]}-{unit.pos[1]}"] = {"checkCollision" : False}
                                else:
                                    tileprops[f"{unit.pos[0]}-{unit.pos[1]}"] = {"checkCollision" : True}
                        elif keys_pressed[K_c]:
                            if not keys_pressed[K_LALT]:
                                tileprops[f"{unit.pos[0]}-{unit.pos[1]}"] = {"checkCollision" : False}
                            else:
                                tileprops[f"{unit.pos[0]}-{unit.pos[1]}"] = {"checkCollision" : True}
                    elif mouse_pressed[2]:
                        tpP = f"{unit.pos[0]}-{unit.pos[1]}"
                        if not keys_pressed[K_c]:
                            if not keys_pressed[K_LSHIFT]:
                                unit.resetSerial()
                                if tpP in tileprops:
                                    del tileprops[tpP]
                            elif tileInfo.releasedButtons[2] or tileInfo.placedOnTile != unit: unit.removeSerial()
                        elif tpP in tileprops and "checkCollision" in tileprops[tpP]:
                            del tileprops[tpP]["checkCollision"]
                            if len(tileprops[tpP]) < 1: del tileprops[tpP]
                    tileInfo.placedOnTile = unit

                    if tilepropsPath in tileprops:
                        for k, v in tileprops[tilepropsPath].items():
                            if k != "checkCollision":
                                tip_renders.append(harbinger_font_small.render(f"{k}: {v}", True, KDS.Colors.EmeraldGreen))

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

        tileInfo.releasedButtons[0] = False if mouse_pressed[0] else True
        tileInfo.releasedButtons[2] = False if mouse_pressed[2] else True

        return renderList, brushtemp

def loadGrid(size: Tuple[int, int]):
    rlist = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(tileInfo((x, y)))
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
                row.append(tileInfo((x, y)))
            grid.append(row)
    else:
        for y in range(abs(size_difference[1])):
            grid.pop()
    if size_difference[0] > 0:
        for y in range(len(grid)):
            row = grid[y]
            while len(row) < size[0]:
                row.append(tileInfo(((len(row)), y)))
    else:
        for row in grid:
            while len(row) > size[0]:
                row.pop()
    global gridSize
    gridSize = size
    return grid

def saveMap(grd, name: str):
    outputString = ''
    for row in grd:
        for unit in row:
            outputString += unit.serialNumber
        outputString += "\n"
    with open(name, 'w') as f:
        f.write(outputString)
    #region Tile Props
    global tileprops
    tilepropsPath = os.path.join(os.path.dirname(name), "tileprops.kdf")
    if len(tileprops) > 0:
        if os.path.isfile(tilepropsPath) or KDS.System.MessageBox.Show("No Tileprops!", "Your project does not have a tileprops file even though it is required. Do you want to add one?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
            with open(tilepropsPath, "w") as f:
                f.write(json.dumps(tileprops))
        else:
            KDS.System.MessageBox.Show("Tileprops Ignored", "Tileprops generation ignored. You might lose level data.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.INFORMATION)
    elif os.path.isfile(tilepropsPath):
        if KDS.System.MessageBox.Show("Useless Tileprops!", "We have detected a tileprops file in your project, but this file is no longer needed. Do you want to remove it?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
            os.remove(tilepropsPath)
        else:
            with open(tilepropsPath, "w") as f:
                f.write(json.dumps(tileprops))
    #endregion
    Undo.clear()

def saveMapName():
    global currentSaveName, grid
    savePath = filedialog.asksaveasfilename(initialfile="level", defaultextension=".dat", filetypes=(("Data file", "*.dat"), ("All files", "*.*")))
    if len(savePath) > 0:
        saveMap(grid, savePath)
        currentSaveName = savePath

def loadMap(path: str) -> bool: # bool indicates if the map loading was succesful
    global currentSaveName, gridSize, grid, tileprops
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
        contents = f.read().split("\n")
        while len(contents[-1]) < 1: contents = contents[:-1]

    maxW = 0
    for i in range(len(contents)):
        maxW = max(maxW, len(contents[i][:-2].split("/")))
    temporaryGrid = loadGrid((maxW, len(contents)))

    for row, rRow in zip(contents, temporaryGrid):
        for unit, rUnit in zip(row[:-2].split("/"), rRow):
            unit = unit.strip() + " / "
            rUnit.serialNumber = unit

    currentSaveName = path

    grid = temporaryGrid
    fpath = os.path.join(os.path.dirname(path), "tileprops.kdf")
    if os.path.isfile(fpath):
        with open(fpath, 'r') as f:
            tileprops = json.loads(f.read())

    Undo.clear()
    return True

def openMap() -> bool: #Returns True if the operation was succesful
    global currentSaveName, gridSize, grid, tileprops
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
    Undo.register()
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if len(commandlist) < 3:
                KDS.Console.Feed.append("Invalid set command.")
                return
            if commandlist[2] in brushNames:
                brush = brushNames[commandlist[2]]
                KDS.Console.Feed.append(f"Brush set: [{brushNames[commandlist[2]]}: {commandlist[2]}]")
            elif commandlist[2] in brushNames.values():
                brush = commandlist[2]
                KDS.Console.Feed.append(f"Brush set: [{commandlist[2]}: {list(brushNames.keys())[list(brushNames.values()).index(commandlist[2])]}]")
            else: KDS.Console.Feed.append("Invalid brush.")
        elif dragRect != None:
            if commandlist[1] in brushNames:
                Selected.Set(tileInfo.toSerialString(brushNames[commandlist[1]]))
                Selected.Update()
                KDS.Console.Feed.append(f"Filled [{dragRect.topleft}, {dragRect.bottomright}] with [{brushNames[commandlist[1]]}: {commandlist[1]}]")
            elif commandlist[1] in brushNames.values():
                Selected.Set(tileInfo.toSerialString(commandlist[2]))
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
                    unit: tileInfo
                    srlist = unit.getSerials()
                    for i in range(1, len(srlist)):
                        unit.setSerialToSlot("0000", i)
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
    for collection in Atextures:
        for key in Atextures[collection]:
            selectorRects.append(selectorRect((x, y), key))
            x += 1
            if x > COLUMNS:
                x = 0
                y += 1

        y += 1
        if x > 0:
            x = 0
            y += 1

    selectorSize = (COLUMNS, y)

    while matMenRunning:
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                LB_Quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_e:
                    matMenRunning = False
                    return previousMaterial
                elif event.key == K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == MOUSEWHEEL:
                if event.y > 0: rscroll = max(rscroll - 1, 0)
                else: rscroll = min(rscroll + 1, sys.maxsize)

        tip_renders = []

        mpos = pygame.mouse.get_pos()
        display.fill((20,20,20))
        for selection in selectorRects:
            selection: selectorRect
            sorting = selection.serialNumber[0]
            display.blit(KDS.Convert.AspectScale(Atextures[sorting][selection.serialNumber], (BLOCKSIZE, BLOCKSIZE)), (selection.rect.x, selection.rect.y - rscroll * 30))
            if selection.rect.collidepoint(mpos[0], mpos[1] + rscroll * 30):
                pygame.draw.rect(display, (230, 30, 40), (selection.rect.x, selection.rect.y - rscroll * 30, BLOCKSIZE, BLOCKSIZE), 3)
                tip_renders.append(harbinger_font_small.render(selection.serialNumber, True, KDS.Colors.RiverBlue))
                if mouse_pressed[0]:
                    return selection.serialNumber

        if mouse_pressed[0]:
            return "0000"

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

def menu():
    global currentSaveName, brush, grid, gridSize, btn_menu, gamesize, scaleMultiplier, scalesize, mainRunning
    btn_menu = True
    grid = None
    def button_handler(_openMap: bool = False):
        global btn_menu
        if _openMap:
            # Button menu is turned off if openMap was succesful
            btn_menu = not openMap()
        else: btn_menu = False
    newMap_btn = KDS.UI.Button(pygame.Rect(650, 150, 300, 100), button_handler, harbinger_font.render("New Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    openMap_btn = KDS.UI.Button(pygame.Rect(650, 300, 300, 100), button_handler, harbinger_font.render("Open Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    genProp_btn = KDS.UI.Button(pygame.Rect(650, 450, 300, 100), generateLevelProp, harbinger_font.render("Generate levelProp.kdf", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    quit_btn = KDS.UI.Button(pygame.Rect(650, 600, 300, 100), LB_Quit, harbinger_font.render("Quit", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))

    while btn_menu:
        clicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                LB_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    clicked = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == DROPFILE:
                # Button menu is turned off if loadMap was succesful
                btn_menu = not loadMap(event.file)
        display.fill(KDS.Colors.Gray)
        mouse_pos = pygame.mouse.get_pos()
        newMap_btn.update(display, mouse_pos, clicked)
        openMap_btn.update(display, mouse_pos, clicked, True)
        genProp_btn.update(display, mouse_pos, clicked)
        quit_btn.update(display, mouse_pos, clicked)

        pygame.display.flip()

class Selected:
    units: List[tileInfo] = []
    tilepropunits: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def Set(serialOverride: str = None, tilepropsOverride: Dict[str, Any] = None, registerUndo: bool = True):
        global grid, tileprops
        Selected.SetCustomGrid(grid=grid, tileprops=tileprops, serialOverride=serialOverride, tilepropsOverride=tilepropsOverride, registerUndo=registerUndo)

    @staticmethod
    def SetCustomGrid(grid: List[List[tileInfo]], tileprops: Dict[str, Dict[str, Any]], serialOverride: str = None, tilepropsOverride: Dict[str, Any] = None, registerUndo: bool = True):
        if registerUndo: Undo.register()
        for unit in Selected.units:
            try:
                grid[unit.pos[1]][unit.pos[0]].serialNumber = unit.serialNumber if serialOverride == None else serialOverride
            except IndexError:
                warnSize = f"({len(grid[0])}, {len(grid)})" if len(grid) > 0 else "(0, 0)"
                KDS.Logging.warning(f"Index error while setting unit at position: \"{unit.pos}\". Grid size: {warnSize}")
        for k in Selected.tilepropunits:
            if tilepropsOverride != None:
                if len(tilepropsOverride) > 0:
                    tileprops[k] = tilepropsOverride
                else:
                    tileprops.pop(k)
            else:
                tileprops[k] = Selected.tilepropunits[k]

    @staticmethod
    def Move(x: int, y: int):
        global dragRect
        for u in Selected.units:
            u.pos = (u.pos[0] + x, u.pos[1] + y)
        movedTileprops: Dict[str, Dict[str, Any]] = {}
        for k in Selected.tilepropunits:
            tmp = k.split("-")
            new_tpp = f"{int(tmp[0]) + x}-{int(tmp[1]) + y}"
            movedTileprops[new_tpp] = Selected.tilepropunits[k]
        Selected.tilepropunits = movedTileprops
        dragRect.x += x
        dragRect.y += y

    @staticmethod
    def Update():
        Selected.units = []
        Selected.tilepropunits = {}
        if dragRect == None: return
        for row in grid[dragRect.y:dragRect.y + dragRect.height]:
            for unit in row[dragRect.x:dragRect.x + dragRect.width]:
                Selected.units.append(unit.copy())
        for y in range(dragRect.y, dragRect.height + 1):
            for x in range(dragRect.x, dragRect.width + 1):
                tpp = f"{x}-{y}"
                if tpp in tileprops:
                    Selected.tilepropunits[tpp] = tileprops[tpp]

    @staticmethod
    def Get():
        Selected.Update()
        Selected.Set(serialOverride=tileInfo.EMPTYSERIAL, tilepropsOverride={}, registerUndo=False)

def main():
    global currentSaveName, brush, grid, gridSize, btn_menu, gamesize, scaleMultiplier, scalesize, mainRunning, brushTex, dragRect

    menu()
    if not mainRunning: return

    display.fill(KDS.Colors.Black)

    def zoom(add: int, scroll: List[int], grid: List[List[tileInfo]]):
        global scalesize, scaleMultiplier
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_scaled = (KDS.Math.Floor(mouse_pos[0] / scalesize + scroll[0]), KDS.Math.Floor(mouse_pos[1] / scalesize + scroll[1]))
        hitPos = grid[int(KDS.Math.Clamp(mouse_pos_scaled[1], 0, gridSize[1] - 1))][int(KDS.Math.Clamp(mouse_pos_scaled[0], 0, gridSize[0] - 1))].pos
        scalesize = KDS.Math.Clamp(scalesize + add, 1, 256)
        scaleMultiplier = scalesize / gamesize
        mouse_pos_scaled = (KDS.Math.Floor(mouse_pos[0] / scalesize + scroll[0]), KDS.Math.Floor(mouse_pos[1] / scalesize + scroll[1]))
        scroll[0] += hitPos[0] - mouse_pos_scaled[0]
        scroll[1] += hitPos[1] - mouse_pos_scaled[1]

    if grid == None:
        g = KDS.Console.Start("Grid Size: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000)).replace(" ", "").split(",")

        gridSize = (int(g[0]), int(g[1]))
        grid = loadGrid(gridSize)

    inputConsole_output = None
    updateTiles = True

    DebugMode = False

    dragStartPos = None
    dragPos = None
    selectTrigger = False
    brushTrigger = True

    mouse_pos_beforeMove = pygame.mouse.get_pos()
    scroll_beforeMove = scroll
    while mainRunning:
        pygame.key.set_repeat(500, 31)
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get(): #Event loop
            if event.type == QUIT:
                LB_Quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if brush != "0000":
                        Undo.register()
                    selectTrigger = True
                elif event.button == 3:
                    Undo.register()
                elif event.button == 2:
                    mouse_pos_beforeMove = mouse_pos
                    scroll_beforeMove = scroll.copy()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    updateTiles = True
            elif event.type == KEYDOWN:
                if event.key == K_z or event.key == K_y:
                    if keys_pressed[K_LCTRL]:
                        redo = False
                        if event.key == K_y: redo = True
                        Undo.request(redo)
                        Selected.Update()
                elif event.key == K_t:
                    inputConsole_output = KDS.Console.Start("Enter Command:", True, KDS.Console.CheckTypes.Commands(), commands=commandTree, showFeed=True, autoFormat=True, enableOld=True)
                elif event.key == K_r:
                    Undo.register()
                    resize_output = KDS.Console.Start("New Grid Size: (int, int)", True, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000), defVal=f"{gridSize[0]}, {gridSize[1]}", autoFormat=True)
                    if resize_output != None: grid = resizeGrid((int(resize_output[0]), int(resize_output[1])), grid)
                elif event.key == K_e:
                    brush = materialMenu(brush)
                    updateTiles = False
                elif event.key == K_F3:
                    DebugMode = not DebugMode
                    KDS.Logging.Profiler(DebugMode)
                elif event.key == K_DELETE:
                    Selected.Set(tileInfo.EMPTYSERIAL)
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
                elif event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == K_a:
                    if keys_pressed[K_LCTRL]:
                        dragRect = pygame.Rect(0, 0, gridSize[0], gridSize[1])
                        Selected.Get()
            elif event.type == MOUSEWHEEL:
                if keys_pressed[K_LSHIFT]:
                    scroll[0] -= event.y
                elif keys_pressed[K_LCTRL]:
                    zoom(event.y * 5, scroll, grid)
                else:
                    scroll[1] -= event.y
                scroll[0] += event.x
            elif event.type == DROPFILE:
                loadMap(event.file)

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
        grid, brush = tileInfo.renderUpdate(display, scroll, grid, brush, updateTiles)

        undoTotal = Undo.index + Undo.overflowCount
        if undoTotal > 0:
            if undoTotal < 50:
                _color = KDS.Colors.Yellow
            elif 100 >= undoTotal >= 50: _color = KDS.Colors.Orange
            else: _color = KDS.Colors.Red
            pygame.draw.circle(display, _color, (10, 10), 5)
        if brush != "0000":
            tmpScaled = KDS.Convert.AspectScale(Atextures[brush[0]][brush], (68, 68))
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
        if brush == "0000": brushTrigger = True
        if mouse_pressed[2] and dragRect != None and not keys_pressed[K_c]:
            selectTrigger = False
            dragStartPos = None
            dragRect = None
            Selected.Set()
            Selected.Update()

        if len(Selected.units) > 0:
            for unit in Selected.units:
                blitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                srlist = unit.getSerials()
                for number in srlist:
                    blitTex = None
                    if number[0] == '3':
                        blitTex = Atextures["3"]["3001"]
                    elif number != "0000":
                        try:
                            blitTex = Atextures[number[0]][number]
                        except KeyError:
                                KDS.Logging.warning(f"Cannot render unit because texture is not added: {srlist}", True)
                    if blitTex != None:
                        if number in trueScale:
                            display.blit(pygame.transform.scale(blitTex, (int(blitTex.get_width() * scaleMultiplier), int(blitTex.get_height() * scaleMultiplier))), (blitPos[0] - (blitTex.get_width() * scaleMultiplier - scalesize), blitPos[1] - (blitTex.get_height() * scaleMultiplier - scalesize)))
                        else:
                            display.blit(pygame.transform.scale(blitTex, (int(blitTex.get_width() * scaleMultiplier), int(blitTex.get_height() * scaleMultiplier))), (blitPos[0], blitPos[1] - blitTex.get_height() * scaleMultiplier + scalesize))

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
    Left Mouse: Set Serial
    Left Mouse + SHIFT: Add Serial
    Left Mouse + C: No Collision
    Left Mouse + ALT + C: Force Collision
    Right Mouse + C: Remove Collision Attribute
    Right Mouse + ALT + C: Remove Collision Attribute
    E: Open Material Menu
    CTRL + Z: Undo
    CTRL + Y: Redo
    CTRL + D: Duplicate Selection
    T: Input Console
    R: Resize Map
    F: Set Property
    P: Set teleport index
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