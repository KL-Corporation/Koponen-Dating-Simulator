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
import tkinter 
from tkinter import filedialog
import json
import copy

root = tkinter.Tk()
root.withdraw()
pygame.init()
display_size = (1600, 800)
scalesize = 68
gamesize = 34
scaleMultiplier = scalesize / gamesize

display: pygame.Surface = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")
pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/levelBuilderIcon.png"))

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
    "3002" : pygame.image.load("Assets/Textures/Tiles/door_front.png").convert()
}

Atextures = {
    "0": t_textures,
    "1": i_textures,
    "2": e_textures,
    "3": teleports
}

trueScale = [f"0{e}" for e in buildData["trueScale"]]
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
    points = []
    index = 0
    overflowCount = 0
    
    @staticmethod
    def register():
        global grid, dragRect, brush, tileprops
        toSave = {
            "grid": copy.deepcopy(grid),
            "dragRect": dragRect.copy() if dragRect != None else dragRect,
            "brush": brush,
            "tileprops": copy.deepcopy(tileprops)
        }
        if Undo.index == len(Undo.points) - 1 and toSave == Undo.points[Undo.index]:
            return
        Selected.SetCustomGrid(toSave["grid"], registerUndo=False)
        del Undo.points[Undo.index + 1:]
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
        brush = data["brush"]
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
        return tileInfo(self.pos, serialNumber=self.serialNumber)

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
                    if srlNumber not in t_textures or not self.hasTile():
                        self.setSerialToSlot(srlNumber, index)
                    else: print(f"Tile already in {self.pos}!")
                else: print(f"Serial {srlNumber} already in {self.pos}!")
                return
        print(f"No empty slots at {self.pos} available for serial {srlNumber}!")
        
    def removeSerial(self):
        srlist = self.getSerials()
        for index, number in reversed(list(enumerate(srlist))):
            if int(number) != 0:
                self.setSerialToSlot("0000", index)
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
        pygame.draw.rect(Surface, (80, 30, 30), pygame.Rect(0, 0, (len(renderList[0]) - scroll[0]) * scalesize, (len(renderList) - scroll[1]) * scalesize))
        for row in renderList[scroll[1] : scroll[1] + display_size[1] // scalesize + 2]:
            row: List[tileInfo]
            for unit in row[scroll[0] : scroll[0] + display_size[0] // scalesize + 2]:
                blitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                srlist = unit.getSerials()
                for index, number in enumerate(srlist):
                    if int(number) != 0:
                        unitTexture = None
                        if number[0] == '3':
                            unitTexture = Atextures["3"]["3001"]
                        else:
                            try:
                                unitTexture = Atextures[number[0]][number]
                            except KeyError:
                                    print(f"Cannot render unit because texture is not added: {srlist}")

                        if number[0] == "3":
                            if pygame.Rect(unit.pos[0] * scalesize, unit.pos[1] * scalesize, scalesize, scalesize).collidepoint(mpos_scaled):
                                t_ind = str(int(number[1:]))
                                tip_renders.append(harbinger_font_small.render(t_ind, True, KDS.Colors.AviatorRed))
                                if keys_pressed[K_p]:
                                    temp_serial = KDS.Console.Start('Set teleport index: (int[0, 999])', True, KDS.Console.CheckTypes.Int(0, 999), defVal=t_ind)
                                    if len(temp_serial) > 0:
                                        temp_serial = f"3{int(temp_serial):03d}"
                                        unit.setSerialToSlot(temp_serial, index)
                                    #keys_pressed[K_p] = False

                        if unitTexture != None:
                            if number in trueScale:
                                Surface.blit(pygame.transform.scale(unitTexture, (int(unitTexture.get_width() * scaleMultiplier), int(unitTexture.get_height() * scaleMultiplier))), (blitPos[0] - (unitTexture.get_width() * scaleMultiplier - scalesize), blitPos[1] - (unitTexture.get_height() * scaleMultiplier - scalesize)))
                            else:
                                Surface.blit(pygame.transform.scale(unitTexture, (int(unitTexture.get_width() * scaleMultiplier), int(unitTexture.get_height() * scaleMultiplier))), (blitPos[0], blitPos[1] - unitTexture.get_height() * scaleMultiplier + scalesize))
                            
                tilepropsPath = f"{unit.pos[0]}-{unit.pos[1]}"
                if tilepropsPath in tileprops and "checkCollision" in tileprops[tilepropsPath]:
                    if not tileprops[tilepropsPath]["checkCollision"]:
                        tilepropsOverlayColor = KDS.Colors.Black
                    else:
                        tilepropsOverlayColor = KDS.Colors.White
                    tilepropsOverlay = pygame.Surface((scalesize, scalesize)).convert()
                    tilepropsOverlay.fill(tilepropsOverlayColor)
                    tilepropsOverlay.set_alpha(128)
                    Surface.blit(tilepropsOverlay, (blitPos[0], blitPos[1]))

                if pygame.Rect(unit.pos[0] * scalesize, unit.pos[1] * scalesize, scalesize, scalesize).collidepoint(mpos_scaled):
                    if keys_pressed[K_p]:
                        setPropKey: str = KDS.Console.Start("Enter Property Key:")
                        if len(setPropKey) > 0:
                            tmp = KDS.Console.Start("Enter Property Value:")
                            setPropVal = KDS.Convert.AutoType(tmp)
                            if setPropVal != None:
                                if tilepropsPath not in tileprops:
                                    tileprops[tilepropsPath] = {}
                                tileprops[tilepropsPath][setPropKey] = setPropVal
                            else: print(f"Value {tmp} could not be parsed into any type.")
                    
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

def loadGrid(size):
    rlist = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(tileInfo((x, y)))
        rlist.append(row)
    global gridSize
    gridSize = size
    return rlist

def resizeGrid(size, grid: list):
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

def loadMap(path: str):
    global currentSaveName, gridSize, grid, tileprops
    if Undo.index + Undo.overflowCount > 0 and KDS.System.MessageBox.Show("Unsaved Changes.", "There are unsaved changes. Do you want to save them?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
        if not currentSaveName:
            saveMapName()
        else:
            saveMap(grid, currentSaveName)
            
    temporaryGrid = None
    if path:
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

        #for row, tRow in zip(tempGrid, contents):
        #    for unit, tUnit in zip(row, tRow.split("/")):
        #        tUnit = tUnit.strip()
        #        unit.serialNumber = tUnit + " /"
        
        #return tempGrid
        currentSaveName = path

        grid = temporaryGrid
        fpath = os.path.join(os.path.dirname(path), "tileprops.kdf")
        if os.path.isfile(fpath):
            with open(fpath, 'r') as f:
                tileprops = json.loads(f.read())
                
        Undo.clear()
    
def openMap(): #Returns a 2d array ;;;udhadah Returns Nothing
    global currentSaveName, gridSize, grid, tileprops
    fileName = filedialog.askopenfilename(filetypes=(("Data file", "*.dat"), ("All files", "*.*")))
    loadMap(fileName)

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
            if commandlist[2] in brushNames:
                brush = brushNames[commandlist[2]]
                KDS.Console.Feed.append(f"Brush set: [{brushNames[commandlist[2]]}: {commandlist[2]}]")
            else: KDS.Console.Feed.append("Invalid brush.")
        elif dragRect != None:
            if commandlist[1] in brushNames:
                Selected.Set(tileInfo.toSerialString(brushNames[commandlist[1]]))
                Selected.Update()
                KDS.Console.Feed.append(f"Filled [{dragRect.topleft}, {dragRect.bottomright}] with [{brushNames[commandlist[1]]}: {commandlist[1]}]")
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
    blocksize = 70

    class selectorRect:
        def __init__(self, rect: pygame.Rect, serialNumber: str):
            self.rect: pygame.Rect = rect
            self.serialNumber: str = serialNumber

    selectorRects: List[selectorRect] = []

    y = 0
    x = 0
    for collection in Atextures:
        for item in Atextures[collection]:
            selectorRects.append(selectorRect(pygame.Rect(x*100 + 100, y*90 + 40, blocksize, blocksize), item))
            x += 1
            if x > 6:
                x = 0
                y += 1

    while matMenRunning:
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                LB_Quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_e:
                    matMenRunning = False
                    return previousMaterial
            elif event.type == MOUSEWHEEL:
                if event.y > 0: rscroll = max(rscroll - 1, 0)
                else: rscroll = min(rscroll + 1, sys.maxsize)
        
        tip_renders = []
        
        mpos = pygame.mouse.get_pos()
        display.fill((20,20,20))
        for selection in selectorRects:
            selection: selectorRect
            sorting = selection.serialNumber[0]
            display.blit(KDS.Convert.AspectScale(Atextures[sorting][selection.serialNumber], (blocksize, blocksize)), (selection.rect.x,selection.rect.y - rscroll * 30))
            if selection.rect.collidepoint(mpos[0],mpos[1] + rscroll * 30):
                pygame.draw.rect(display, (230, 30, 40), (selection.rect.x, selection.rect.y - rscroll * 30, blocksize, blocksize), 3)
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
            openMap()
            if grid != None:
                btn_menu = False
            else: 
                btn_menu = True
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
            elif event.type == DROPFILE:
                loadMap(event.file)
                btn_menu = False
        display.fill(KDS.Colors.Gray)
        mouse_pos = pygame.mouse.get_pos()
        newMap_btn.update(display, mouse_pos, clicked)
        openMap_btn.update(display, mouse_pos, clicked, True)
        genProp_btn.update(display, mouse_pos, clicked)
        quit_btn.update(display, mouse_pos, clicked)
        
        pygame.display.flip()

class Selected:
    units: List[tileInfo] = []
    
    @staticmethod
    def Set(serialOverride: str = None, registerUndo: bool = True):
        global grid
        if registerUndo: Undo.register()
        for unit in Selected.units:
            grid[unit.pos[1]][unit.pos[0]].serialNumber = unit.serialNumber if serialOverride == None else serialOverride

    @staticmethod
    def SetCustomGrid(grid: List[List[tileInfo]], serialOverride: str = None, registerUndo: bool = True):
        if registerUndo: Undo.register()
        for unit in Selected.units:
            grid[unit.pos[1]][unit.pos[0]].serialNumber = unit.serialNumber if serialOverride == None else serialOverride
            
    @staticmethod         
    def Update():
        Selected.units = []
        if dragRect == None: return
        for row in grid[dragRect.y:dragRect.y + dragRect.height]:
            for unit in row[dragRect.x:dragRect.x + dragRect.width]:
                Selected.units.append(unit.copy())
                
    @staticmethod
    def Get():
        Selected.Update()
        Selected.Set(serialOverride=tileInfo.EMPTYSERIAL, registerUndo=False)

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
        scalesize = KDS.Math.Clamp(scalesize + add, 1, 272)
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
                elif event.key == K_DELETE:
                    Selected.Set(tileInfo.EMPTYSERIAL)
                    Selected.Update()
                elif event.key == K_d:
                    if keys_pressed[K_LCTRL]:
                        Selected.Set()
                elif event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                    xy = (0, 0)
                    if event.key == K_UP:
                        xy = (0, -1)
                    elif event.key == K_DOWN:
                        xy = (0, 1)
                    elif event.key == K_LEFT:
                        xy = (-1, 0)
                    elif event.key == K_RIGHT:
                        xy = (1, 0)
                    for unit in Selected.units:
                        unit.pos = (unit.pos[0] + xy[0], unit.pos[1] + xy[1])
                    dragRect.x += xy[0]
                    dragRect.y += xy[1]
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
            openMap()
            if grid == None:
                print("Map opening cancelled.")

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
                                print(f"Cannot render unit because texture is not added: {srlist}")
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
main()

pygame.quit()

""" KEYMAP
    [Normal]
    P: Set teleport index
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
    P: Set Property
    CTRL + S: Save Project
    CTRL + SHIFT + S: Save Project As
    CTRL + O: Open Project
    
    [Material Menu]
    Escape: Close Material Menu
    E: Close Material Menu
"""