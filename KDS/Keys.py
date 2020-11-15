import sys
from pygame.locals import *

#The amount of ticks before hold is activated.
holdTicks = 50

keyList = []

class Key:
    def __init__(self) -> None:
        self.pressed = False
        self.held = False
        self.clicked = False
        self.holdClicked = False
        self.ticksHeld = 0
        keyList.append(self)
        
    def update(self):
        self.clicked = False
        self.holdClicked = False
        if self.pressed:
            self.ticksHeld += 1
            if self.ticksHeld > holdTicks:
                self.held = True
                if self.ticksHeld == sys.maxsize: self.ticksHeld -= 1
                
    def SetState(self, pressed: bool):
        if not pressed:
            if self.pressed: self.clicked = True
            if self.held:
                self.holdClicked = True
                self.held = False
            self.ticksHeld = 0
        self.pressed = pressed
        
    def GetHeldCustom(self, holdTicks: int):
        return True if self.ticksHeld > holdTicks else False

moveUp = Key()
moveDown = Key()
moveRight = Key()
moveLeft = Key()
moveRun = Key()
functionKey = Key()
killKey = Key()
inventoryKeys = [K_1, K_2, K_3, K_4, K_5]
mainKey = Key()
altUp = Key()
altDown = Key()
altLeft = Key()
altRight = Key()
        
def Update():
    for key in keyList: key.update()
        
def Reset():
    for key in keyList:
        key.SetState(False)