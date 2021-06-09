from typing import Optional, Tuple
import KDS.Events
import KDS.Math

from pygame.locals import *

#The amount of ticks before hold is activated.
holdTicks = 50

keyList = []

class BaseKey:
    def __init__(self) -> None:
        self.pressed: bool = False
        self.held: bool = False
        self.clicked: bool = False
        self.onUp: bool = False
        self.onDown: bool = False
        self.holdClicked: bool = False
        self.ticksHeld: int = 0
        keyList.append(self)

    def update(self):
        self.onDown = False
        self.onUp = False
        self.clicked = False
        self.holdClicked = False
        if self.pressed:
            if self.ticksHeld < KDS.Math.MAXVALUE:
                self.ticksHeld += 1
            if self.ticksHeld > holdTicks:
                self.held = True

    def SetState(self, pressed: bool):
        if pressed:
            if not self.pressed:
                self.onDown = True
        else:
            if self.pressed:
                self.clicked = True
                self.onUp = True
            if self.held:
                self.holdClicked = True
                self.held = False
            self.ticksHeld = 0
        self.pressed = pressed

    def GetHeldCustom(self, holdTicks: int):
        return True if self.ticksHeld > holdTicks else False

class Key(BaseKey):
    def __init__(self, defaultBinding: int, secondaryDefaultBinding: Optional[int]) -> None:
        super().__init__()
        self.binding: int = defaultBinding
        self.secondaryDefaultBinding: Optional[int] = secondaryDefaultBinding

    @property
    def Bindings(self) -> Tuple[int, Optional[int]]:
        return (self.binding, self.secondaryDefaultBinding)

class InventoryKey(Key):
    def __init__(self, defaultBinding: int, inventory_index: int) -> None:
        super().__init__(defaultBinding, None)
        self.index = inventory_index

class MouseButton(BaseKey):
    def __init__(self) -> None:
        super().__init__()

moveUp = Key(K_w, K_SPACE)
moveDown = Key(K_s, K_LCTRL)
moveRight = Key(K_d, None)
moveLeft = Key(K_a, None)
moveRun = Key(K_LSHIFT, None)
functionKey = Key(K_e, None)
mainKey = MouseButton()
altUp = Key(K_UP, None)
altDown = Key(K_DOWN, None)
altLeft = Key(K_LEFT, None)
altRight = Key(K_RIGHT, None)
fart = Key(K_f, None)
dropItem = Key(K_q, None)

Inventory1 = InventoryKey(K_1, 0)
Inventory2 = InventoryKey(K_2, 1)
Inventory3 = InventoryKey(K_3, 2)
Inventory4 = InventoryKey(K_4, 3)
Inventory5 = InventoryKey(K_5, 4)
INVENTORYKEYS = (Inventory1, Inventory2, Inventory3, Inventory4, Inventory5)

REBINDBLACKLIST = (
    # State Keys                         No idea what meta or mode is
    K_NUMLOCK, K_CAPSLOCK, K_SCROLLLOCK, K_RMETA, K_LMETA, K_MODE,
    #System Keys               print screen
    K_HELP, K_SYSREQ, K_BREAK, K_PRINT, K_MENU, K_POWER, K_EURO,
    # Windows key
    K_LSUPER, K_RSUPER,
    # F-keys
    K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12
    )

def Update():
    for key in keyList:
        key.update()

def Reset():
    for key in keyList:
        key.SetState(False)