if __name__ != "__main__":
    raise ImportError("Level Builder cannot be imported!")
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""

from typing import List, Tuple
import sys
import pygame
from pygame.locals import *
pygame.init()
import threading
import math
import KDS.Colors
import KDS.Convert
import KDS.ConfigManager
import KDS.System
import KDS.Math
import KDS.UI
import KDS.Console
import numpy
import tkinter 
from tkinter import filedialog
import re
import json

root = tkinter.Tk()
root.withdraw()
pygame.init()
display_size = (1600, 800)
scalesize = 68
gamesize = 34
scaleMultiplier = scalesize / gamesize

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")
pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/levelBuilderIcon.png"))

clock = pygame.time.Clock()
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
harbinger_font_small = pygame.font.Font("Assets/Fonts/harbinger.otf", 15, bold=0, italic=0)

consoleBackground = pygame.image.load("Assets/Textures/UI/loadingScreen.png").convert()

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
data = json.loads(d)

t_textures = {}
for element in data["tile_textures"]:
    srl = f"0{element}"

    elmt = data["tile_textures"][element]
    t_textures[srl] = pygame.image.load("Assets/Textures/Tiles/" + elmt).convert()
    t_textures[srl].set_colorkey(KDS.Colors.White)
    brushNames[os.path.splitext(elmt)[0]] = srl

i_textures = {}
for element in data["item_textures"]:
    srl = f"1{element}"
    
    elmt = data["item_textures"][element]
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
    "2007": pygame.image.load("Assets/Textures/Animations/undead_monster_walking_0.png").convert()
}

teleports = {
    "3001" : pygame.image.load("Assets/Textures/Misc/telep.png").convert()
}

Atextures = {
    "0": t_textures,
    "1": i_textures,
    "2": e_textures,
    "3": teleports
}
### GLOBAL VARIABLES ###

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]
scroll = [0, 0]
brush = "0000"
teleportTemp = "001"
currentSaveName = ''
grid = [[]]
modifiedAfterSave = False
timesModifiedAfterSave = 0

keys_pressed = {
    K_RETURN: False,
    K_e: False,
    K_s: False,
    K_o: False,
    K_p: False,
    K_LSHIFT: False,
    K_LCTRL: False,
}

def LB_Quit():
    pygame.quit()
    quit()

KDS.Console.init(main_display, pygame.Surface((1200, 800)), clock, _Offset=(200, 0), _KDS_Quit = LB_Quit)

##################################################

class tileInfo:
    def __init__(self, position: Tuple[int, int], serialNumber = "0000 0000 0000 0000 / "):
        self.pos = position
        self.serialNumber = serialNumber

    def setNewSerialNumber(self, srlNumber: str):
        serialIdentifier = int(srlNumber[1])
        serialIdentifier *= 4
        if serialIdentifier:
            serialIdentifier += 1
        self.serialNumber = self.serialNumber[:serialIdentifier] + srlNumber + self.serialNumber[serialIdentifier+4:]

    def setNewSerialNumber_attempt2(self, srlNumber, slot):
        #self.serialNumber = self.serialNumber[slot*4] + srlNumber + self.serialNumber[:3-slot]
        #return self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]
        self.serialNumber = self.serialNumber[:slot * 4 + slot] + srlNumber + self.serialNumber[slot * 4 + 4 + slot:]

    def getSerialNumber(self, index):
        if index > 0:
            index += 1
        return self.serialNumber[index: index + 4]

    @staticmethod
    def renderUpdate(Surface: pygame.Surface, scroll: list, renderList, brsh = "0000", updttiles=True):
        brushtemp = brsh
        scroll[0] = KDS.Math.Clamp(scroll[0], 0, gridSize[0] - 1)
        scroll[1] = KDS.Math.Clamp(scroll[1], 0, gridSize[1] - 1)
        bpos = (0, 0)
        
        pygame.draw.rect(Surface, (80, 30, 30), pygame.Rect(0, 0, (len(renderList[0]) - scroll[0]) * scalesize, (len(renderList) - scroll[1]) * scalesize))
        for row in renderList[scroll[1] : scroll[1] + int((display_size[1] / scalesize) + 2)]:
            for unit in row[scroll[0] : scroll[0] + int((display_size[0] / scalesize) + 2)]:
                blitPos = (unit.pos[0] * scalesize - scroll[0] * scalesize, unit.pos[1] * scalesize - scroll[1] * scalesize)
                mpos = pygame.mouse.get_pos()
                tempSerial = unit.serialNumber.replace(" / ", "")
                srlist = tempSerial.split()
                for index, number in enumerate(srlist):
                    if int(number) != 0:
                        unitTexture = None
                        try: unitTexture = Atextures[number[0]][number]
                        except: 
                            if number[0] == '3':
                                unitTexture = Atextures["3"]["3001"]
                            else:
                                print(f"Cannot render unit because texture is not added: {srlist}")
                        if keys_pressed[K_p] and number[0] == "3":
                            temp_serial = int(KDS.Console.Start('New serial number for teleport: ', False, KDS.Console.CheckTypes.Int(0, 999)))
                            temp_serial = f"3{temp_serial:03d}"
                            unit.setNewSerialNumber_attempt2(temp_serial, index)
                            keys_pressed[K_p] = False

                        if unitTexture != None: Surface.blit(pygame.transform.scale(unitTexture, (int(unitTexture.get_width() * scaleMultiplier), int(unitTexture.get_height() * scaleMultiplier))), (blitPos[0], blitPos[1] - int(unitTexture.get_height() * scaleMultiplier )+ scalesize))

                if pygame.Rect(unit.pos[0] * scalesize, unit.pos[1] * scalesize, scalesize, scalesize).collidepoint(mpos[0] + scroll[0] * scalesize, mpos[1] + scroll[1] * scalesize):
                    if pygame.mouse.get_pressed()[1] and not keys_pressed[K_LSHIFT]:
                        brushtemp = unit.getSerialNumber(0)
                    pygame.draw.rect(Surface, (20, 20, 20), (blitPos[0], blitPos[1], scalesize, scalesize), 2)
                    bpos = unit.pos
                    if pygame.mouse.get_pressed()[0] and updttiles:
                        if brsh != "0000":
                            unit.setNewSerialNumber(brsh)
                        else:
                            unit.serialNumber = "0000 0000 0000 0000 / "
                    if pygame.mouse.get_pressed()[2]:
                        unit.serialNumber = "0000 0000 0000 0000 / "
        mousePosText = harbinger_font.render(f"({bpos[0]}, {bpos[1]})", True, KDS.Colors.AviatorRed)
        main_display.blit(mousePosText, (display_size[0] - mousePosText.get_width(), display_size[1] - mousePosText.get_height()))
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

"""
def inputConsole(daInput = ">>>  ", allowEscape: bool = True, gridSizeExtras: bool = False, defVal: str = ""):
    pygame.key.set_repeat(500, 31)
    r = True
    rstring = defVal
    while r:
        inputError = False
        inputWarning = False
        if gridSizeExtras and len(rstring) > 0:
            gridSizeStringParced = rstring.strip().replace(" ", "").split(",")
            if len(gridSizeStringParced) != 2:
                inputError = True
            if not inputError:
                try:
                    int(gridSizeStringParced[0])
                    int(gridSizeStringParced[1])
                except:
                    inputError = True
                if not inputError:
                    if len(gridSizeStringParced[0]) >= len(str(sys.maxsize)) or len(gridSizeStringParced[1]) >= len(str(sys.maxsize)):
                        inputError = True
                    elif int(gridSizeStringParced[0]) > 1000 or int(gridSizeStringParced[1]) > 1000:
                        inputWarning = True
                    elif int(gridSizeStringParced[0]) < 1 or int(gridSizeStringParced[1]) < 1:
                        inputError = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                r = False
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    if allowEscape:
                        r = False
                        return None
                elif event.key == K_RETURN:
                    if not inputError:
                        return rstring.strip()
                    elif allowEscape:
                        return None
                elif event.key == K_BACKSPACE:
                    rstring = rstring[:-1]
                elif event.unicode:
                    rstring += event.unicode
        main_display.fill(consoleBackground.get_at((0, 0)))
        main_display.blit(KDS.Convert.AspectScale(consoleBackground, display_size),( (display_size[0] / 2) - consoleBackground.get_size()[0] / 2, (display_size[1] / 2)-consoleBackground.get_size()[1] / 2 )  )
        consoleText = harbinger_font.render(daInput + rstring, True, KDS.Colors.White)
        main_display.blit(consoleText, (10, 10))
        if inputError:
            warningText = "[invalid value]"
            warningColor = KDS.Colors.Red
        elif inputWarning:
            warningText = "[performance warning]"
            warningColor = KDS.Colors.Yellow
        else:
            #Pylance ei tykkää, jos tän poistaa
            warningText = ""
            warningColor = (0, 0, 0)
        if inputWarning or inputError:
            notValidSurf = pygame.Surface(harbinger_font.size(rstring))
            notValidSurf.fill(warningColor)
            notValidSurf.set_alpha(128)
            main_display.blit(notValidSurf, (harbinger_font.size(daInput)[0] + 10, 10))
            main_display.blit(harbinger_font_small.render(warningText, True, KDS.Colors.White), (consoleText.get_width() + 20, 15))
        pygame.display.update()
    pygame.key.set_repeat(0, 0)
"""

def saveMap(grd, name: str):
    outputString = ''
    for row in grd:
        for unit in row:
            outputString += unit.serialNumber
        outputString += "\n"
    with open(name, 'w') as f:
        f.write(outputString)
    global modifiedAfterSave, timesModifiedAfterSave
    modifiedAfterSave = False
    timesModifiedAfterSave = 0
        
def saveMapName():
    global currentSaveName, grid
    savePath = filedialog.asksaveasfilename(initialfile="level", defaultextension=".dat", filetypes=(("Data file", "*.dat"), ("All files", "*.*")))
    if len(savePath) > 0:
        saveMap(grid, savePath)
        currentSaveName = savePath

def openMap(): #Returns a 2d array
    global currentSaveName, gridSize
    fileName = filedialog.askopenfilename(filetypes = (("Data file", "*.dat"), ("All files", "*.*")))
    if fileName:
        with open(fileName, 'r') as f:
            contents = f.read().split("\n")
            contents = contents[:-1]
        temporaryGrid = loadGrid((len(contents[0][:-2].split("/")), len(contents)))

        for row, rRow in zip(contents, temporaryGrid):
            for unit, rUnit in zip(row[:-2].split("/"), rRow):
                unit = unit.strip() + " / "
                rUnit.serialNumber = unit

        #for row, tRow in zip(tempGrid, contents):
        #    for unit, tUnit in zip(row, tRow.split("/")):
        #        tUnit = tUnit.strip()
        #        unit.serialNumber = tUnit + " /"
        
        #return tempGrid
        currentSaveName = fileName
        return temporaryGrid

    else: 
        return None

commandTree = {
    "set": {
        "brush": brushNames
    },
    "add": {
        "rows": "break",
        "cols": "break"
    },
    "rmv": {
        "rows": "break",
        "cols": "break"
    }
}
def consoleHandler(inputString: str):
    global brush, grid
    commandlist = inputString.lower().strip().split()
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if commandlist[2] in brushNames:
                brush = brushNames[commandlist[2]]
                KDS.Console.Feed.append(f"Brush set: [{brushNames[commandlist[2]]}: {commandlist[2]}]")
            else: KDS.Console.Feed.append("Invalid brush.")
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
        else: KDS.Console.Feed.append("Invalid remove command.")
    else: KDS.Console.Feed.append("Invalid command.")
def materialMenu(previousMaterial):
    r = True
    rscroll = 0
    blocksize = 70

    class selectorRect:
        def __init__(self, rect: pygame.Rect, serialNumber):
            self.rect = rect
            self.serialNumber = serialNumber

    selectorRects = []

    y = 0
    x = 0
    for collection in Atextures:
        for item in Atextures[collection]:
            selectorRects.append(selectorRect(pygame.Rect(x*100+100, y*90+40, blocksize, blocksize), item))
            x+=1
            if x > 6:
                x = 0
                y += 1

    while r:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                LB_Quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_e:
                    r = False
                    return previousMaterial
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 5:
                    rscroll += 1
                elif event.button == 4:
                    rscroll -= 1
                    if rscroll < 0:
                        rscroll = 0
        mpos = pygame.mouse.get_pos()
        main_display.fill((20,20,20))
        for selection in selectorRects:
            sorting = selection.serialNumber[0]
            main_display.blit(KDS.Convert.AspectScale(Atextures[sorting][selection.serialNumber],(blocksize,blocksize)), (selection.rect.x,selection.rect.y-rscroll*30))
            if selection.rect.collidepoint(mpos[0],mpos[1]+rscroll*30):
                pygame.draw.rect(main_display, (230, 30, 40), (selection.rect.x, selection.rect.y-rscroll*30, blocksize, blocksize), 3)
                if pygame.mouse.get_pressed()[0]:
                    return selection.serialNumber
        pygame.display.update()

def generateLevelProp():
    """
    Generate a levelProp.kdf using this tool.
    """
    ic = KDS.Convert.ToBool(KDS.Console.Start("Darkness Enabled: (bool)", False, KDS.Console.CheckTypes.Bool()))
    if isinstance(ic, bool):
        dark = ic
    else:
        dark = False
    if dark:
        ic = int(KDS.Console.Start("Darkness Strength: (int[0, 255])", False, KDS.Console.CheckTypes.Int()))
    else:
        ic = 0
    darkness = KDS.Math.Clamp(ic, 0, 255)
    
    ic = KDS.Convert.ToBool(KDS.Console.Start("Ambient Light Enabled: (bool)", False, KDS.Console.CheckTypes.Bool()))
    if isinstance(ic, bool):
        ambient_light = ic
    else:
        ambient_light = False
    if ambient_light:
        ic = KDS.Console.Start("Ambient Light Tint: (int, int, int)", False, KDS.Console.CheckTypes.Tuple(3, 0, 255)).replace(" ", "").split(",")
    else:
        ic = (0, 0, 0)
    ambient_light_tint = (int(ic[0]), int(ic[1]), int(ic[2]))
    
    ic = KDS.Console.Start("Player Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="100, 100").replace(" ", "").split(",")
    p_start_pos = (int(ic[0]), int(ic[1]))
    
    ic = KDS.Console.Start("Koponen Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="200, 200").replace(" ", "").split(",")
    k_start_pos = (int(ic[0]), int(ic[1]))
    
    ic = KDS.Console.Start("Time Bonus Range in seconds: (full points: int, no points: int)", False, KDS.Console.CheckTypes.Tuple(2, 0)).replace(" ", "").split(",")
    tb_start = int(ic[0])
    tb_end = int(ic[1])
    
    savePath = filedialog.asksaveasfilename(initialfile="levelprop", defaultextension=".kdf", filetypes=(("Koponen Data Format", "*.kdf"), ("All files", "*.*")))
    if len(savePath) > 0:
        KDS.ConfigManager.SetJSON(savePath, "Darkness", "enabled", dark)
        KDS.ConfigManager.SetJSON(savePath, "Darkness", "strength", darkness)
        KDS.ConfigManager.SetJSON(savePath, "AmbientLight", "enabled", ambient_light)
        KDS.ConfigManager.SetJSON(savePath, "AmbientLight", "tint", ambient_light_tint)
        KDS.ConfigManager.SetJSON(savePath, "StartPos", "player", p_start_pos)
        KDS.ConfigManager.SetJSON(savePath, "StartPos", "koponen", k_start_pos)
        KDS.ConfigManager.SetJSON(savePath, "TimeBonus", "start", tb_start)
        KDS.ConfigManager.SetJSON(savePath, "TimeBonus", "end", tb_end)

def main():
    global currentSaveName, brush, grid, gridSize, modifiedAfterSave, timesModifiedAfterSave, btn_menu, gamesize, scaleMultiplier, scalesize
    btn_menu = True
    grid = None
    def button_handler(_openMap: bool = False, _generateLevelProp: bool = False, _quit: bool = False):
        global btn_menu, grid
        if _generateLevelProp:
            generateLevelProp()
        elif _quit:
            LB_Quit
        elif _openMap:
            o_m = openMap()
            if o_m != None: 
                grid = o_m
                btn_menu = False
            else: 
                btn_menu = True
        else: btn_menu = False
    newMap_btn = KDS.UI.Button(pygame.Rect(650, 150, 300, 100), button_handler, harbinger_font.render("New Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    openMap_btn = KDS.UI.Button(pygame.Rect(650, 300, 300, 100), button_handler, harbinger_font.render("Open Map", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    genProp_btn = KDS.UI.Button(pygame.Rect(650, 450, 300, 100), button_handler, harbinger_font.render("Generate levelProp.kdf", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    quit_btn = KDS.UI.Button(pygame.Rect(650, 600, 300, 100), button_handler, harbinger_font.render("Quit", True, KDS.Colors.Black), (255, 255, 255), (235, 235, 235), (200, 200, 200))
    while btn_menu:
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                LB_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    clicked = True
        main_display.fill(KDS.Colors.Gray)
        mouse_pos = pygame.mouse.get_pos()
        newMap_btn.update(main_display, mouse_pos, clicked)
        openMap_btn.update(main_display, mouse_pos, clicked, True)
        genProp_btn.update(main_display, mouse_pos, clicked, False, True)
        quit_btn.update(main_display, mouse_pos, clicked, False, False, True)
        pygame.display.update()
    
    main_display.fill(KDS.Colors.Black)
    
    def zoom(add: int, scroll: List[int], grid: List[List[tileInfo]]):
        global scalesize, scaleMultiplier
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_scaled = (math.floor(mouse_pos[0] / scalesize + scroll[0]), math.floor(mouse_pos[1] / scalesize + scroll[1]))
        hitPos = grid[int(KDS.Math.Clamp(mouse_pos_scaled[1], 0, gridSize[1] - 1))][int(KDS.Math.Clamp(mouse_pos_scaled[0], 0, gridSize[0] - 1))].pos
        scalesize = KDS.Math.Clamp(scalesize + add, 1, 272)
        scaleMultiplier = scalesize / gamesize
        mouse_pos_scaled = (math.floor(mouse_pos[0] / scalesize + scroll[0]), math.floor(mouse_pos[1] / scalesize + scroll[1]))
        scroll[0] += hitPos[0] - mouse_pos_scaled[0]
        scroll[1] += hitPos[1] - mouse_pos_scaled[1]
        

    if grid == None:
        g = KDS.Console.Start("Grid Size: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000)).replace(" ", "").split(",")
            
        gridSize = (int(g[0]), int(g[1]))
        grid = loadGrid(gridSize)

    inputConsole_output = None
    updateTiles = True

    mouse_pos_beforeMove = pygame.mouse.get_pos()
    scroll_beforeMove = scroll
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get(): #Event loop
            if event.type == pygame.QUIT:
                if modifiedAfterSave:
                    if KDS.System.MessageBox.Show("Unsaved Changes.", "There are unsaved changes. Are you sure you want to quit?", KDS.System.MessageBox.Styles.Yes_No) == 6:
                        LB_Quit()
                else:
                    LB_Quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if keys_pressed[K_LSHIFT]:
                        scroll[0] -= 1
                    elif keys_pressed[K_LCTRL]:
                        zoom(5, scroll, grid)
                    else:
                        scroll[1] -= 1
                elif event.button == 5:
                    if keys_pressed[K_LSHIFT]:
                        scroll[0] += 1
                    elif keys_pressed[K_LCTRL]:
                        zoom(-5, scroll, grid)
                    else:
                        scroll[1] += 1
                elif event.button == 2:
                    mouse_pos_beforeMove = mouse_pos
                    scroll_beforeMove = scroll.copy()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    updateTiles = True
            elif event.type == KEYDOWN:
                if event.key == K_LCTRL:
                    keys_pressed[K_LCTRL] = True
                elif event.key == K_t:
                    inputConsole_output = KDS.Console.Start("Enter Command:", True, KDS.Console.CheckTypes.Commands(), commands=commandTree, showFeed=True)
                elif event.key == K_r:
                    resize_output = KDS.Console.Start("New Grid Size: (int, int)", True, KDS.Console.CheckTypes.Tuple(2, 1, sys.maxsize, 1000), defVal=f"{gridSize[0]}, {gridSize[1]}")
                    if len(resize_output) > 0:
                        resize_output = resize_output.replace(" ", "").split(",")
                        grid = resizeGrid((int(resize_output[0]), int(resize_output[1])), grid)
                elif event.key == K_s:
                    keys_pressed[K_s] = True
                elif event.key == K_e:
                    brush = materialMenu(brush)
                    updateTiles = False
                    keys_pressed[K_e] = True
                elif event.key == K_o:
                    keys_pressed[K_o] = True
                elif event.key == K_LSHIFT:
                    keys_pressed[K_LSHIFT] = True
                elif event.key == K_p:
                    keys_pressed[K_p] = True
            elif event.type == KEYUP:
                if event.key == K_LCTRL:
                    keys_pressed[K_LCTRL] = False
                elif event.key == K_e:
                    keys_pressed[K_e] = False
                elif event.key == K_s:
                    keys_pressed[K_s] = False
                elif event.key == K_o:
                    keys_pressed[K_o] = False 
                elif event.key == K_p:
                    keys_pressed[K_p] = False
                elif event.key == K_LSHIFT:
                    keys_pressed[K_LSHIFT] = False
        
        if pygame.mouse.get_pressed()[1] and keys_pressed[K_LSHIFT]:
            mid_scroll_x = int(round((mouse_pos_beforeMove[0] - mouse_pos[0]) / scalesize))
            mid_scroll_y = int(round((mouse_pos_beforeMove[1] - mouse_pos[1]) / scalesize))
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
            tempGr = openMap()
            if tempGr:
                grid = tempGr
            else:
                print("saveMap returned None")

        if inputConsole_output != None:
            consoleHandler(inputConsole_output)
            inputConsole_output = None

        main_display.fill((30,20,60))
        
        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
            modifiedAfterSave = True
            timesModifiedAfterSave += 1
            
        grid, brush = tileInfo.renderUpdate(main_display, scroll, grid, brush, updateTiles)

        if modifiedAfterSave:
            _color = KDS.Colors.Yellow
            if 200 > timesModifiedAfterSave > 100:
                _color = KDS.Colors.Orange
            elif timesModifiedAfterSave > 200:
                _color = KDS.Colors.Red
            pygame.draw.circle(main_display, _color, (display_size[0] - 10, 10), 5)

        pygame.display.update()
        clock.tick(60)
        
main()