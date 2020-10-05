import os
import sys
from numpy.core.fromnumeric import size
import pygame
from pygame.locals import *
import threading
import KDS.Colors
import KDS.Convert
import numpy
import tkinter 
import re
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw()
pygame.init()
display_size = (1600, 800)
scalesize = 55

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")

clock = pygame.time.Clock()
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
harbinger_font_small = pygame.font.Font("Assets/Fonts/harbinger.otf", 15, bold=0, italic=0)

consoleBackground = pygame.image.load("Assets/Textures/UI/loadingScreen.png").convert()

with open("Assets/Textures/tile_textures.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
t_textures = {}
for element in data:
    num = num = f"0{element.split(',')[0]}"
    res = element.split(",")[1]
    t_textures[num] = KDS.Convert.AspectScale(pygame.image.load("Assets/Textures/Map/" + res).convert(), (scalesize, scalesize), horizontalOnly=True)
    t_textures[num].set_colorkey(KDS.Colors.GetPrimary.White)

with open("Assets/Textures/item_textures.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
i_textures = {}
for element in data:
    num = f"1{element.split(',')[0]}"
    res = element.split(",")[1]
    i_textures[num] = pygame.image.load(
        "Assets/Textures/Items/" + res).convert()
    i_textures[num].set_colorkey(KDS.Colors.GetPrimary.White)

e_textures = {
    "2001": pygame.image.load("Assets/Textures/Animations/imp_walking_0.png").convert(),
    "2002": pygame.image.load("Assets/Textures/Animations/seargeant_walking_0.png").convert()
}

Atextures = {
    "0": t_textures,
    "1": i_textures,
    "2": e_textures
}
""" GLOBAL VARIABLES """

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]
scroll = [0, 0]
brush = "0000"
currentSaveName = ''
grid = [[]]

keys_pressed = {
    "RETURN": False,
    "K_e": False,
    "K_s": False,
    "K_o": False,
    "K_SHIFT": False,
    "K_CTRL": False
}
##################################################

def blitText(Surface: pygame.Surface, txt: str, position: (int, int), color = KDS.Colors.GetPrimary.White):
    Surface.blit(harbinger_font.render(txt, True, color), position)
class tileInfo:
    def __init__(self, position: (int, int), serialNumber = "0000 0000 0000 0000 / "):
        self.rect = pygame.Rect(position[0], position[1], scalesize, scalesize)
        self.serialNumber = serialNumber

    def setNewSerialNumber(self, srlNumber: str):
        serialIdentifier = int(srlNumber[1])
        serialIdentifier *= 4
        if serialIdentifier:
            serialIdentifier += 1
        self.serialNumber = self.serialNumber[:serialIdentifier] + srlNumber + self.serialNumber[serialIdentifier+4:]

    def getSerialNumber(self, index):
        if index > 0:
            index += 1
        return self.serialNumber[index: index+4]

    @staticmethod
    def renderUpdate(Surface: pygame.Surface, scroll: list, renderList, brsh = "0000", updttiles=True):
        brushtemp = brsh
        if scroll[0] < 0:
            scroll[0] = 0
        if scroll[1] < 0:
            scroll[1] = 0
        bpos = [0,0]
        for row in renderList[scroll[1]:scroll[1]+int((display_size[1]/scalesize)+2)]:
            for unit in row[scroll[0]:scroll[0]+int((display_size[0]/scalesize)+2)]:
                blitPos = (unit.rect.x-scroll[0]*scalesize, unit.rect.y-scroll[1]*scalesize)
                pygame.draw.rect(Surface, (80, 30, 30), (blitPos[0], blitPos[1], scalesize, scalesize))
                mpos = pygame.mouse.get_pos()
                tempSerial = unit.serialNumber.replace(" / ", "")
                srlist = tempSerial.split()
                for number in srlist:
                    try:
                        Surface.blit(Atextures[number[0]][number], (blitPos[0],blitPos[1]))
                    except:
                        pass
                if unit.rect.collidepoint(mpos[0]+scroll[0]*scalesize, mpos[1]+scroll[1]*scalesize):
                    if pygame.mouse.get_pressed()[1]:
                        brushtemp = unit.getSerialNumber(0)
                    pygame.draw.rect(Surface,(20,20,20),(blitPos[0], blitPos[1], scalesize, scalesize), 2)
                    bpos = [unit.rect.x/scalesize, unit.rect.y/scalesize]
                    if pygame.mouse.get_pressed()[0] and updttiles:
                        if brsh != "0000":
                            unit.setNewSerialNumber(brsh)                     
                        else:
                            unit.serialNumber = "0000 0000 0000 0000 / "
        
        blitText(main_display, f"({bpos[0]}, {bpos[1]})", (1430, 770), KDS.Colors.Get.AviatorRed)
                #print(unit.rect.topleft)
        return renderList, brushtemp

def loadGrid(size):
    rlist = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(tileInfo((x * scalesize,y * scalesize)))
        rlist.append(row)
    return rlist

def inputConsole(daInput = ">>>  ", allowEscape: bool = True, gridSizeExtras: bool = False):
    pygame.key.set_repeat(500, 31)
    r = True
    rstring = ''
    while r:
        inputValid = True
        if gridSizeExtras and len(rstring) > 0:
            gridSizeStringParced = rstring.strip().replace(" ", "").split(",")
            valuesInt = True
            try:
                int(gridSizeStringParced[0])
                int(gridSizeStringParced[1])
            except:
                valuesInt = False
            if len(gridSizeStringParced) != 2 or not valuesInt:
                inputValid = False
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
                    if inputValid:
                        return rstring.strip()
                    elif allowEscape:
                        return None
                elif event.key == K_BACKSPACE:
                    rstring = rstring[:-1]
                elif event.unicode:
                    rstring += event.unicode
        main_display.fill(consoleBackground.get_at((0, 0)))
        main_display.blit(KDS.Convert.AspectScale(consoleBackground, display_size),( (display_size[0] / 2) - consoleBackground.get_size()[0] / 2, (display_size[1] / 2)-consoleBackground.get_size()[1] / 2 )  )
        consoleText = harbinger_font.render(daInput + rstring, True, KDS.Colors.GetPrimary.White)
        main_display.blit(consoleText, (10, 10))
        if not inputValid:
            notValidSurf = pygame.Surface(harbinger_font.size(rstring))
            notValidSurf.fill(KDS.Colors.GetPrimary.Red)
            notValidSurf.set_alpha(128)
            main_display.blit(notValidSurf, (harbinger_font.size(daInput)[0] + 10, 10))
            main_display.blit(harbinger_font_small.render("[value not valid]", True, KDS.Colors.GetPrimary.White), (consoleText.get_width() + 20, 15))
        pygame.display.update()
    pygame.key.set_repeat(0, 0)

def saveMap(grd, name: str):
    outputString = ''
    for row in grd:
        for unit in row:
            outputString += unit.serialNumber
        outputString += "\n"
    with open(name, 'w') as f:
        f.write(outputString)

def openMap(): #Returns a 2d array
    global currentSaveName
    fileName = filedialog.askopenfilename(filetypes = (("KDS Data file", "*.dat"), ("All files", "*.*")))
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

def consoleHandler(inputString: str):
    global brush, grid
    commandlist = inputString.strip().split()
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if len(commandlist[2]) == 4 and commandlist[2].isnumeric():
                brush = commandlist[2]
    elif commandlist[0] == "add":
        if commandlist[1] == "rows":
            for _ in range(int(commandlist[2])):
                grid.append([tileInfo((x*scalesize, len(grid)*scalesize)) for x in range(len(grid[0]))])
        elif commandlist[1] == "cols":
            for _ in range(int(commandlist[2])):
                y = 0
                for row in grid:
                    row.append(tileInfo((len(row)*scalesize, y*scalesize)))
                    y += 1
    elif commandlist[0] == "gremv":
        if commandlist[1] == "rows":
            for _ in range(int(commandlist[2])):
                grid = grid[:-1]
        elif commandlist[1] == "cols":
            for _ in range(int(commandlist[2])):
                for row in grid:
                    row = row[:-1]

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
                r = False
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
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

def main():
    global currentSaveName, brush, grid
    g = inputConsole("Grid size: (int,int) >>>  ", allowEscape=False, gridSizeExtras=True).replace(" ", "").split(",")
    gridSize = (int(g[0]), int(g[1]))
    grid = loadGrid(gridSize)

    inputConsole_output = None
    updateTiles = True

    while True:
        for event in pygame.event.get(): #Event loop
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if keys_pressed["K_SHIFT"]:
                        scroll[1] -= 1
                    else:
                        scroll[0] -= 1
                elif event.button == 5:
                    if keys_pressed["K_SHIFT"]:
                        scroll[1] += 1
                    else:
                        scroll[0] += 1
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    updateTiles = True
            elif event.type == KEYDOWN:
                if event.key == K_LCTRL:
                    keys_pressed["K_CTRL"] = True
                elif event.key == K_t:
                    inputConsole_output = inputConsole()
                elif event.key == K_s:
                    keys_pressed["K_s"] = True
                elif event.key == K_e:
                    brush = materialMenu(brush)
                    updateTiles = False
                    keys_pressed["K_e"] = True
                elif event.key == K_o:
                    keys_pressed["K_o"] = True
                elif event.key == K_LSHIFT:
                    keys_pressed["K_SHIFT"] = True
            elif event.type == KEYUP:
                if event.key == K_LCTRL:
                    keys_pressed["K_CTRL"] = False
                elif event.key == K_e:
                    keys_pressed["K_e"] = False
                elif event.key == K_s:
                    keys_pressed["K_s"] = False
                elif event.key == K_o:
                    keys_pressed["K_o"] = False 
                elif event.key == K_LSHIFT:
                    keys_pressed["K_SHIFT"] = False

        if keys_pressed["K_s"] and keys_pressed["K_CTRL"]:
            if not currentSaveName:
                savePath = filedialog.asksaveasfilename()
                saveMap(grid, savePath)
                currentSaveName = savePath
            else:
                saveMap(grid, currentSaveName)
        if keys_pressed["K_s"] and keys_pressed["K_CTRL"] and keys_pressed["K_SHIFT"]:
                savePath = filedialog.asksaveasfilename()
                saveMap(grid, savePath)
                currentSaveName = savePath

        if keys_pressed["K_o"] and keys_pressed["K_CTRL"]:
            tempGr = openMap()
            if tempGr:
                grid = tempGr
            else:
                print("saveMap returned None")

        if inputConsole_output:
            consoleHandler(inputConsole_output)
            inputConsole_output = None

        main_display.fill((30,20,60))
        grid, brush = tileInfo.renderUpdate(main_display, scroll, grid, brush, updateTiles)
        pygame.display.update()
        clock.tick(60)
if __name__ == "__main__":
    main()
else:
    print("This program cannot be imported!")

        
