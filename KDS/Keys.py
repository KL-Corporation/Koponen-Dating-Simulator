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
altUp ="altUp"
altDown = "altDown"
altLeft = "altLeft"
altRight = "altRight"

KeyStates = {
#   name: [isPressed, isHeld, isClicked, ticksHeld] 
    moveUp: [],
    moveDown: [],
    moveRight: [],
    moveLeft: [],
    moveRun: [],
    functionKey: [],
    killKey: [],
    mainKey: [],
    altUp: [],
    altDown: [],
    altLeft: [],
    altRight: []
}

for keyName in KeyStates:
    KeyStates[keyName].append(False)
    KeyStates[keyName].append(False)
    KeyStates[keyName].append(False)
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