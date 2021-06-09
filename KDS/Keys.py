from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple, Any

import pygame
import KDS.Events
import KDS.Math
import KDS.UI
import KDS.ConfigManager
import KDS.Colors
import KDS.System
import KDS.Logging

from pygame.locals import *

#The amount of ticks before hold is activated.
holdTicks = 50

baseKeyList: List[BaseKey] = []
keyList: List[Key] = []

class BaseKey:
    def __init__(self) -> None:
        self.pressed: bool = False
        self.held: bool = False
        self.clicked: bool = False
        self.onUp: bool = False
        self.onDown: bool = False
        self.holdClicked: bool = False
        self.ticksHeld: int = 0
        baseKeyList.append(self)

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
    def __init__(self, name: str, defaultBinding: int, secondaryDefaultBinding: Optional[int]) -> None:
        super().__init__()
        self.name = name
        self._defaultBinding: int = defaultBinding
        self._secondaryDefaultBinding: Optional[int] = secondaryDefaultBinding
        self.binding: Optional[int] = defaultBinding
        self.secondaryBinding: Optional[int] = secondaryDefaultBinding
        keyList.append(self)

    def loadBindings(self):
        bindings: List[int] = KDS.ConfigManager.GetSetting(f"Keys/Bindings/{self.name}", (self._defaultBinding, self._secondaryDefaultBinding), writeMissingOverride=False, warnMissingOverride=False)
        if len(bindings) == 0:
            return
        if len(bindings) != 2:
            KDS.Logging.AutoError(f"Unexpected bindings count! Expected: 2, Got: {len(bindings)}. Binding loading will try to continue.")
        try:
            self.binding = bindings[0]
            self.secondaryBinding = bindings[1]
        except Exception as e:
            KDS.Logging.AutoError(f"Could not load bindings. Exception ({type(e)}): {e}")

    def saveBindings(self):
        if self.binding != self._defaultBinding or self.secondaryBinding != self._secondaryDefaultBinding:
            KDS.ConfigManager.SetSetting(f"Keys/Bindings/{self.name}", (self.binding, self.secondaryBinding))

    @property
    def Bindings(self) -> Sequence[int]:
        return tuple([b for b in (self.binding, self.secondaryBinding) if b != None])

class InventoryKey(Key):
    def __init__(self, defaultBinding: int, inventory_index: int) -> None:
        super().__init__(f"inventory{inventory_index}", defaultBinding, None)
        self.index = inventory_index

class MouseButton(BaseKey):
    def __init__(self) -> None:
        super().__init__()

moveUp = Key("moveUp", K_w, K_SPACE)
moveDown = Key("moveDown", K_s, K_LCTRL)
moveRight = Key("moveRight", K_d, None)
moveLeft = Key("moveLeft", K_a, None)
moveRun = Key("moveRun", K_LSHIFT, None)
functionKey = Key("functionKey", K_e, None)
mainKey = MouseButton()
altUp = Key("altUp", K_UP, None)
altDown = Key("altDown", K_DOWN, None)
altLeft = Key("altLeft", K_LEFT, None)
altRight = Key("altRight", K_RIGHT, None)
fart = Key("fart", K_f, None) # Binding only
dropItem = Key("dropItem", K_q, None) # Binding only
terminal = Key("terminal", K_t, None) # Binding only
hideUI = Key("hideUI", K_F1, None) # Binding only
screenshot = Key("screenshot", K_F12, None) # Binding only
toggleDebug = Key("toggleDebug", K_F3, None) # Binding only
toggleFullscreen = Key("toggleFullscreen", K_F11, None) # Binding only

Inventory1 = InventoryKey(K_1, 0)
Inventory2 = InventoryKey(K_2, 1)
Inventory3 = InventoryKey(K_3, 2)
Inventory4 = InventoryKey(K_4, 3)
Inventory5 = InventoryKey(K_5, 4)
INVENTORYKEYS = (Inventory1, Inventory2, Inventory3, Inventory4, Inventory5)

REBINDBLACKLIST: Tuple[int, ...] = (
    # State Keys                         No idea what meta or mode is
    K_NUMLOCK, K_CAPSLOCK, K_SCROLLLOCK, K_RMETA, K_LMETA, K_MODE,
    #System Keys               print screen
    K_HELP, K_SYSREQ, K_BREAK, K_PRINT, K_MENU, K_POWER, K_EURO,
    # Windows key
    K_LSUPER, K_RSUPER,
    # Important Keys
    K_ESCAPE
)
REBINDABLEKEYS = {
    "Move Up": moveUp,
    "Move Down": moveDown,
    "Move Left": moveLeft,
    "Move Right": moveRight,
    "Interact": functionKey,
    "Align Up": altUp,
    "Align Down": altDown,
    "Align Left": altLeft,
    "Align Right": altRight,
    "Fart": fart,
    "Drop Item": dropItem,
    "Open Terminal": terminal,
    "Hide UI": hideUI,
    "Take a Screenshot": screenshot,
    "Toggle Debug Mode": toggleDebug,
    "Toggle Fullscreen": toggleFullscreen
}

def LoadCustomBindings():
    for key in keyList:
        key.loadBindings()

def ResetCustomBindings():
    KDS.ConfigManager.SetSetting(f"Keys/Bindings", KDS.ConfigManager.JSON.EMPTY)
    LoadCustomBindings()

def Update():
    for key in baseKeyList:
        key.update()

def Reset():
    for key in baseKeyList:
        key.SetState(False)

def StartBindingMenu(display: pygame.Surface, clock: pygame.time.Clock, eventHandler: Callable[[Any], bool]):
    def bindKey(key: Key, isAlt: bool):
        def setBindingValue(value: Optional[int]):
            if isAlt:
                key.secondaryBinding = value
            else:
                key.binding = value
            key.saveBindings()
            loadKeyDatas()

        nonlocal running
        running2 = True
        while running2:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running2 = False
                    running = False
                if eventHandler(event):
                    continue
                if event.type == KEYDOWN:
                    if event.mod & KMOD_CTRL:
                        if event.key == K_F4: # Delete Binding
                            setBindingValue(None)
                            running2 = False
                        elif event.key == K_x: # Restore Default
                            setBindingValue(key._defaultBinding if not isAlt else key._secondaryDefaultBinding)
                            running2 = False
                    elif event.key == K_ESCAPE: # Cancel
                        running2 = False
                    else: # Rebind
                        if event.key not in REBINDBLACKLIST:
                            setBindingValue(event.key)
                            running2 = False
                        else:
                            KDS.System.MessageBox.Show("Not Allowed", "This key cannot be bound because it is integral to the applications operation.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.WARNING)

            display.fill(KDS.Colors.Gray)
            dest1 = (display_size[0] // 2 - BindText.get_width() // 2, display_size[1] // 2 - BindText.get_height() // 2)
            display.blit(BindText, dest1)
            dest2 = (display_size[0] // 2 - BindHelperText.get_width() // 2, dest1[1] + BindText.get_height() // 2 + 20)
            display.blit(BindHelperText, dest2)

            pygame.display.flip()

    running = True
    buttonPadding = 10
    textMarginLeft = 10
    buttonWidth = 400
    buttonHeight = 50
    display_size = display.get_size()
    ArialFont = pygame.font.SysFont("Arial", 28, bold=0, italic=0)
    BindText: pygame.Surface = ArialFont.render("Press a key to bind it.", True, KDS.Colors.White)
    BindHelperText: pygame.Surface = ArialFont.render("CTRL + F4: Delete Binding | CTRL + X: Restore Default Binding | Escape: Cancel Binding", True, KDS.Colors.White)

    scroll = 0

    keyDatas: List[Tuple[str, Key, KDS.UI.Button, KDS.UI.Button]] = []
    keyMaxY = 0
    def loadKeyDatas():
        nonlocal keyDatas, keyMaxY

        def renderBindingText(binding: Optional[int]) -> pygame.Surface:
            return ArialFont.render(pygame.key.name(binding) if binding != None else "Unassigned", True, KDS.Colors.White if binding != None else KDS.Colors.LightGray)
        keyDatas.clear()

        for index, (keyName, key) in enumerate(REBINDABLEKEYS.items()):
            b2Rect = pygame.Rect(display_size[0] - buttonWidth - buttonPadding, buttonPadding + index * (buttonHeight + buttonPadding), buttonWidth, buttonHeight)
            b2Text = renderBindingText(key.secondaryBinding)
            button2 = KDS.UI.Button(b2Rect, bindKey, b2Text)

            b1Rect = pygame.Rect(b2Rect.left - buttonWidth - buttonPadding, b2Rect.top, b2Rect.width, b2Rect.height)
            b1Text = renderBindingText(key.binding)
            button1 = KDS.UI.Button(b1Rect, bindKey, b1Text)

            keyDatas.append((keyName, key, button1, button2))

            keyMaxY = b2Rect.bottom

    def return_def():
        nonlocal running
        running = False

    def reset_def():
        if KDS.System.MessageBox.Show("Reset Controls", "Are you sure you want to reset all controls to their defaults? This cannot be undone.", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
            ResetCustomBindings()
        loadKeyDatas()

    loadKeyDatas()

    reset_button = KDS.UI.Button(pygame.Rect(480, keyMaxY + 4 * buttonPadding, 240, 40), reset_def, KDS.UI.ButtonFontSmall.render("Reset Bindings", True, KDS.Colors.AviatorRed))
    return_button = KDS.UI.Button(pygame.Rect(465, reset_button.rect.bottom + 4 * buttonPadding, 270, 60), return_def, "RETURN")
    while running:
        c = False

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if eventHandler(event):
                continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == MOUSEWHEEL:
                scroll = KDS.Math.Clamp(scroll + event.y * 5, -(keyMaxY - buttonHeight), 0)

        display.fill(KDS.Colors.DefaultBackground)

        for data in keyDatas:
            data[2].rect.centery += scroll
            data[3].rect.centery += scroll
            nameRnd: pygame.Surface = ArialFont.render(data[0], True, KDS.Colors.White)
            display.blit(nameRnd, (textMarginLeft, data[2].rect.centery - nameRnd.get_height() // 2))
            data[2].update(display, mouse_pos, c, data[1], False)
            data[3].update(display, mouse_pos, c, data[1], True)
            data[2].rect.centery -= scroll
            data[3].rect.centery -= scroll

        reset_button.rect.centery += scroll
        reset_button.update(display, mouse_pos, c)
        reset_button.rect.centery -= scroll

        return_button.rect.centery += scroll
        return_button.update(display, mouse_pos, c)
        return_button.rect.centery -= scroll

        pygame.display.flip()
        clock.tick_busy_loop(60)
