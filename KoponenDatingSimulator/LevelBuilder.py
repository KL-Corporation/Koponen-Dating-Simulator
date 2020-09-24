import os
import sys
import pygame
from pygame.locals import *
import threading
import KDS.Colors
import numpy
import tkinter 
import re
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw()
pygame.init()
display_size = (1600, 800)
scalesize = 50

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")

clock = pygame.time.Clock()
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
consoleBackground = pygame.image.load("Assets/Textures/UI/loadingScreen.png").convert()

with open("Assets/Textures/tile_textures.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
t_textures = {}
for element in data:
    num = num = f"0{element.split(',')[0]}"
    res = element.split(",")[1]
    t_textures[num] = pygame.transform.scale(pygame.image.load("Assets/Textures/Map/" + res).convert(), (scalesize, scalesize))
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

Atextures = {
    "0": t_textures,
    "1": i_textures
}
""" GLOBAL VARIABLES """

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]
scroll = [0, 0]
brush = "0000"

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
    def __init__(self, position: (int, int), serialNumber = "0001 0000 0000 0000 / "):
        self.rect = pygame.Rect(position[0], position[1], scalesize, scalesize)
        self.serialNumber = serialNumber

    def setNewSerialNumber(self, srlNumber: str):
        serialIdentifier = int(srlNumber[1])
        serialIdentifier *= 4
        if serialIdentifier:
            serialIdentifier += 1
        self.serialNumber = self.serialNumber[:serialIdentifier] + srlNumber + self.serialNumber[serialIdentifier+4:]

    @staticmethod
    def renderUpdate(Surface: pygame.Surface, scroll: list, renderList, brush = "0000"):
        if scroll[0] < 0:
            scroll[0] = 0
        if scroll[1] < 0:
            scroll[1] = 0
        bpos = [0,0]
        for row in renderList[scroll[1]:int((display_size[1]/scalesize)+2)]:
            for unit in row[scroll[0]:int((display_size[0]/scalesize)+2)]:
                blitPos = (unit.rect.x-scroll[0]*scalesize, unit.rect.y-scroll[1]*scalesize)
                mpos = pygame.mouse.get_pos()
                unit.serialNumber = unit.serialNumber.replace(" / ", "")
                srlist = unit.serialNumber.split()
                for number in srlist:
                    try:
                        Surface.blit(Atextures[number[0]][number], (blitPos[0],blitPos[1]))
                    except:
                        pass
                if unit.rect.collidepoint(mpos[0]+scroll[0]*scalesize, mpos[1]+scroll[1]*scalesize):
                    pygame.draw.rect(Surface,(20,20,20),(blitPos[0], blitPos[1], scalesize, scalesize), 2)
                    bpos = [unit.rect.x/scalesize, unit.rect.y/scalesize]
                    if pygame.mouse.get_pressed()[0]:
                        if brush != "0000":
                            unit.setNewSerialNumber(brush)                     
                        else:
                            unit.serialNumber = "0000 0000 0000 0000 / "
        
        blitText(main_display, f"({bpos[0]}, {bpos[1]})", (1430, 770), KDS.Colors.Get.AviatorRed)
                #print(unit.rect.topleft)

def loadGrid(size):
    rlist = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(tileInfo((x*scalesize,y*scalesize)))
        rlist.append(row)
    return rlist

def inputConsole(daInput = ">>>  "):
    r = True
    rstring = ''
    while r:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                r = False
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    r = False
                    return None
                elif event.key == K_RETURN:
                    return rstring.strip()
                elif event.key == K_BACKSPACE:
                    rstring = rstring[:-1]
                else:
                    if event.unicode:
                        rstring += event.unicode
        main_display.fill((0,0,0))
        main_display.blit(pygame.transform.scale(consoleBackground, display_size),( (display_size[0]/2)-consoleBackground.get_size()[0]/2, (display_size[1]/2)-consoleBackground.get_size()[1]/2 )  )
        main_display.blit(harbinger_font.render(daInput + rstring, True, KDS.Colors.GetPrimary.White), (10, 10))
        pygame.display.update()

def saveMap(grd, name: str):
    outputString = ''
    for row in grd:
        for unit in row:
            outputString += unit.serialNumber
        outputString += "\n"
    with open(name, 'w') as f:
        f.write(outputString)

def openMap(): #Returns a 2d array
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
        return temporaryGrid

    else: 
        return None

def consoleHandler(inputString: str):
    global brush
    commandlist = inputString.strip().split()
    if commandlist[0] == "set":
        if commandlist[1] == "brush":
            if len(commandlist[2]) == 4 and commandlist[2].isnumeric():
                brush = commandlist[2]
            

def main():
    g = inputConsole("Grid size: (int,int) >>>  ").replace(" ", "").split(",")
    gridSize = (int(g[0]), int(g[1]))
    grid = loadGrid(gridSize)

    inputConsole_output = None

    while True:
        for event in pygame.event.get(): #Event loop
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if keys_pressed["K_SHIFT"]:
                        scroll[1] += 1
                    else:
                        scroll[0] += 1
                elif event.button == 5:
                    if keys_pressed["K_SHIFT"]:
                        scroll[1] -= 1
                    else:
                        scroll[0] -= 1
            elif event.type == KEYDOWN:
                if event.key == K_LCTRL:
                    keys_pressed["K_CTRL"] = True
                elif event.key == K_t:
                    inputConsole_output = inputConsole()
                elif event.key == K_s:
                    keys_pressed["K_s"] = True
                elif event.key == K_e:
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
            saveMap(grid, "level.dat")
            print("Map was saved succesfully")
        elif keys_pressed["K_o"] and keys_pressed["K_CTRL"]:
            tempGr = openMap()
            if tempGr:
                grid = tempGr
            else:
                print("saveMap returned None")

        consoleHandler(inputConsole_output)

        main_display.fill((30,50,60))
        tileInfo.renderUpdate(main_display, scroll, grid)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
else:
    print("This program cannot be imported!")

        
        
