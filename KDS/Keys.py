from inspect import currentframe
import sys
from typing import Dict
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

KeyStates: Dict[str, dict] = {
#   [name]: {},
    moveUp: {},
    moveDown: {},
    moveRight: {},
    moveLeft: {},
    moveRun: {},
    functionKey: {},
    killKey: {},
    mainKey: {},
    altUp: {},
    altDown: {},
    altLeft: {},
    altRight: {}
}

for keyName in KeyStates:
    KeyStates[keyName]["pressed"] = False
    KeyStates[keyName]["held"] = False
    KeyStates[keyName]["clicked"] = False
    KeyStates[keyName]["holdClicked"] = False
    KeyStates[keyName]["ticksHeld"] = 0

def SetPressed(key_indentifier, pressed: bool):
    if key_indentifier in KeyStates:
        if not pressed:
            if KeyStates[key_indentifier]["pressed"]:
                KeyStates[key_indentifier]["clicked"] = True
            if KeyStates[key_indentifier]["held"]:
                KeyStates[key_indentifier]["holdClicked"] = True
                KeyStates[key_indentifier]["held"] = False
            KeyStates[key_indentifier]["ticksHeld"] = 0
        KeyStates[key_indentifier]["pressed"] = pressed
    else:
        KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetPressed(key_indentifier):
    if key_indentifier in KeyStates: return KeyStates[key_indentifier]["pressed"]
    else: KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetHeld(key_indentifier):
    if key_indentifier in KeyStates: return KeyStates[key_indentifier]["held"]
    else: KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetHeldCustom(key_indentifier, _holdTicks):
    if key_indentifier in KeyStates: return True if KeyStates[key_indentifier]["ticksHeld"] > _holdTicks else False
    else: KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())

def GetTicksHeld(key_indentifier):
    if key_indentifier in KeyStates: return KeyStates[key_indentifier]["ticksHeld"]
    else: KDS.Logging.AutoError(f"Key {key_indentifier} does not exist in database!", currentframe())
        
def GetClicked(key_identifier):
    if key_identifier in KeyStates: return KeyStates[key_identifier]["clicked"]
    else: KDS.Logging.AutoError(f"Key {key_identifier} does not exist in database!", currentframe())
    
def GetHoldClicked(key_identifier):
    if key_identifier in KeyStates: return KeyStates[key_identifier]["holdClicked"]
    else: KDS.Logging.AutoError(f"Key {key_identifier} does not exist in database!", currentframe())
        
def Update():
    for keyName in KeyStates:
        keyData = KeyStates[keyName]
        keyData["clicked"] = False
        keyData["holdClicked"] = False
        if keyData["pressed"]:
            keyData["ticksHeld"] += 1
            if keyData["ticksHeld"] > holdTicks:
                keyData["held"] = True
                if keyData["ticksHeld"] == sys.maxsize:
                    keyData["ticksHeld"] -= 1
        
def Reset():
    for keyName in KeyStates: SetPressed(keyName, False)