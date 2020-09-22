from inspect import currentframe
from pygame.locals import *
import KDS.Logging

moveUp = "moveUp"
moveDown = "moveDown"
moveRight = "moveRight"
moveLeft = "moveLeft"
moveRun = "moveRun"
functionKey = "functionKey"
killKey = "killKey"
inventoryKeys = [K_1, K_2, K_3, K_4, K_5]
mainKey = "mainKey"
KeyStates = {
    moveUp: False,
    moveDown: False,
    moveRight: False,
    moveLeft: False,
    moveRun: False,
    functionKey: False,
    killKey: False,
    mainKey: False
}

def SetPressed(key_indentifier, pressed: bool):
    if key_indentifier in KeyStates:
        KeyStates[key_indentifier] = pressed
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetPressed(key_indentifier):
    if key_indentifier in KeyStates:
        return KeyStates[key_indentifier]
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())