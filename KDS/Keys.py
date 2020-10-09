from inspect import currentframe
import sys
from pygame.locals import *
import KDS.Logging

#The amount of ticks before hold is activated.
holdTicks = 50

moveUp = "moveUp"
moveDown = "moveDown"
moveRight = "moveRight"
moveLeft = "moveLeft"
moveRun = "moveRun"
functionKey = "functionKey"
killKey = "killKey"
inventoryKeys = [K_1, K_2, K_3, K_4, K_5]
mainKey = "mainKey"
arrowUp ="a_up"
arrowDown = "a_down"
arrowLeft = "a_left"
arrowRight = "a_right"

KeyStates = {
#   name: [isPressed, isHeld, isClicked, [Automatic] ticksHeld] 
    moveUp: [False, False, False],
    moveDown: [False, False, False],
    moveRight: [False, False, False],
    moveLeft: [False, False, False],
    moveRun: [False, False, False],
    functionKey: [False, False, False],
    killKey: [False, False, False],
    mainKey: [False, False, False],
    arrowUp: [False, False, False],
    arrowDown: [False, False, False],
    arrowLeft: [False, False, False],
    arrowRight: [False, False, False]

}

for keyName in KeyStates:
    if len(KeyStates[keyName]) < 4:
        KeyStates[keyName].append(0)

def SetPressed(key_indentifier, pressed: bool):
    if key_indentifier in KeyStates:
        if not pressed:
            if KeyStates[key_indentifier][0] and not KeyStates[key_indentifier][1]:
                KeyStates[key_indentifier][2] = True
            KeyStates[key_indentifier][1] = pressed
            KeyStates[key_indentifier][3] = 0
        KeyStates[key_indentifier][0] = pressed
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetPressed(key_indentifier):
    if key_indentifier in KeyStates:
        return KeyStates[key_indentifier][0]
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetHeld(key_indentifier):
    if key_indentifier in KeyStates:
        return KeyStates[key_indentifier][1]
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetHeldCustom(key_indentifier, _holdTicks):
    if key_indentifier in KeyStates:
        if KeyStates[key_indentifier][3] > _holdTicks:
            return True
        else:
            return False
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())

def GetTicksHeld(key_indentifier):
    if key_indentifier in KeyStates:
        return KeyStates[key_indentifier][3]
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetClicked(key_identifier):
    if key_identifier in KeyStates:
        return KeyStates[key_identifier][2]
    else:
        KDS.Logging.AutoError(f"Key {key_identifier} does not exist in database!", currentframe())
        
def Update():
    for keyName in KeyStates:
        keyData = KeyStates[keyName]
        keyData[2] = False
        if keyData[0]:
            keyData[3] += 1
            if keyData[3] > holdTicks:
                keyData[1] = True
                if keyData[3] == sys.maxsize:
                    keyData[3] -= 1
        
def Reset():
    for keyName in KeyStates:
        SetPressed(keyName, False)