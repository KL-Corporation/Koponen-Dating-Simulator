import os
import sys
import pygame
from pygame.locals import *
import threading
import KDS.Colors
import numpy

pygame.init()
display_size = (1600, 800)

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
    t_textures[num] = pygame.image.load(
        "Assets/Textures/Map/" + res).convert()
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


""" GLOBAL VARIABLES """

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]
scroll = [0, 0]

keys_pressed = {
    "RETURN": False,
    "K_e": False,
    "K_CTRL": False
}
##################################################
class tileInfo:
    def __init__(self, position: (int, int), serialNumber = "/ 0000 0000 0000 0000 / "):
        self.rect = pygame.Rect(position[0], position[1], 50, 50)
        self.serialNumber = serialNumber


    def setNewSerialNumber(self, serialNumber: str, index: int):
        pass

def loadGrid(size):
    rlist = []
    row = []
    for y in range(size[1]):
        for x in range(size[0]):
            row.append(tileInfo((x*50,y*50)))
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

def main():
    g = inputConsole("Grid size: (int,int) >>>  ").replace(" ", "").split(",")
    gridSize = (int(g[0]), int(g[1]))
    grid = loadGrid(gridSize)

    while True:
        for event in pygame.event.get(): #Event loop
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll[0] += 6
                elif event.button == 5:
                    scroll[0] -= 6
            elif event.type == KEYDOWN:
                if event.key == K_LCTRL:
                    keys_pressed["K_CTRL"] = True
                elif event.key == K_e:
                    keys_pressed["K_e"] = True
            elif event.type == KEYUP:
                if event.key == K_LCTRL:
                    keys_pressed["K_CTRL"] = False
                elif event.key == K_e:
                    keys_pressed["K_e"] = False

        main_display.fill((30,50,60))
        pygame.display.update()

if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        print("Something in main()-method went wrong and program was closed!")
        quit()
else:
    print("This program cannot be imported!")

        
        
