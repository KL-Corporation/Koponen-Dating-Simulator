from __future__ import annotations

from enum import IntEnum
from typing import Callable, Final, List, Literal, NamedTuple, Self, Tuple, Any

import pygame
import KDS.Events
import KDS.Math
import KDS.UI
import KDS.ConfigManager
import KDS.Colors
import KDS.System
import KDS.Clock
import KDS.Logging
import KDS.Debug

from pygame.locals import *

#The amount of ticks before hold is activated.
holdTicks = 50

keys: dict[str, Key] = {}

class BindingType(IntEnum):
    mouse = 0
    keyboard = 1

class Binding(NamedTuple):
    type: BindingType
    key: int

    @classmethod
    def deserialize(cls, value: dict[str, object]) -> Self:
        t = value["type"]
        k = value["key"]
        assert(isinstance(t, str))
        assert(isinstance(k, int))
        return cls(BindingType[t], k)

    def serialize(self) -> dict[str, str | int]:
        return {"type": self.type.name, "key": self.key}

    def get_displayname(self) -> str:
        if self.type == BindingType.keyboard:
            return pygame.key.name(self.key, use_compat=False).capitalize()
        else:
            return f"Mouse Button {self.key}"

class BaseKey:
    def __init__(self) -> None:
        self.pressed: bool = False
        self.held: bool = False
        self.clicked: bool = False
        self.onUp: bool = False
        self.onDown: bool = False
        self.holdClicked: bool = False
        self.ticksHeld: int = 0

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
            self.onDown = True
        else:
            self.onUp = True
            if self.pressed:
                self.clicked = True
            if self.held:
                self.holdClicked = True
                self.held = False
            self.ticksHeld = 0
        self.pressed = pressed

    def GetHeldCustom(self, holdTicks: int):
        return True if self.ticksHeld > holdTicks else False

class Key(BaseKey):
    def __init__(self, name: str, defaultBinding: Binding, secondaryDefaultBinding: Binding | None, onDownCallback: Callable[[], None] | None = None) -> None:
        super().__init__()
        self.name: Final[str] = name

        self._defaultBinding: Binding = defaultBinding
        self._secondaryDefaultBinding: Binding | None = secondaryDefaultBinding

        self._onDownCallback: Callable[[], None] | None = onDownCallback

        self.binding: Binding | None = None
        self.secondaryBinding: Binding | None = None

        if name in keys:
            raise RuntimeError(f"Name '{name}' already defined in keys.")
        keys[name] = self

    def get_primary_binding(self) -> Binding | None:
        """
        Gets the first non-null binding of this key.

        Bindings are searched in the order binding => secondaryBinding => None
        """
        if self.binding is not None:
            return self.binding
        else:
            return self.secondaryBinding

    def _loadBindings_backwardsCompat(self, bindings: list[int]):
        if len(bindings) == 0:
            return
        if len(bindings) != 2:
            KDS.Logging.AutoError(f"Unexpected bindings count! Expected: 2, Got: {len(bindings)}. Binding loading will try to continue.")
        try:
            self.binding = Binding(BindingType.keyboard, bindings[0])
            self.secondaryBinding = Binding(BindingType.keyboard, bindings[1])
        except Exception as e:
            KDS.Logging.AutoError(f"Could not load bindings. Exception ({type(e)}): {e}")

    def _loadBindings(self):
        setting_path: str = f"Keys/Bindings/{self.name}"

        primary: dict[str, object] | Literal["default"] | None = KDS.ConfigManager.GetSetting(f"{setting_path}/Primary", "default", writeMissingOverride=False, warnMissingOverride=False)
        if primary == "default":
            self.binding = self._defaultBinding
        elif primary is None:
            self.binding = None
        else:
            self.binding = Binding.deserialize(primary)

        secondary: dict[str, object] | Literal["default"] | None = KDS.ConfigManager.GetSetting(f"{setting_path}/Secondary", "default", writeMissingOverride=False, warnMissingOverride=False)
        if secondary == "default":
            self.secondaryBinding = self._secondaryDefaultBinding
        elif secondary is None:
            self.secondaryBinding = None
        else:
            self.secondaryBinding = Binding.deserialize(secondary)

    def loadBindings(self):
        bindings: list[int] | object = KDS.ConfigManager.GetSetting(f"Keys/Bindings/{self.name}", None, writeMissingOverride=False, warnMissingOverride=False)
        if isinstance(bindings, list):
            self._loadBindings_backwardsCompat(bindings)
        else:
            self._loadBindings()

    def saveBindings(self):
        setting_path: str = f"Keys/Bindings/{self.name}"

        if not isinstance(KDS.ConfigManager.GetSetting(setting_path, None, writeMissingOverride=False, warnMissingOverride=False), dict):
            KDS.ConfigManager.SetSetting(setting_path, {})

        if self.binding != self._defaultBinding:
            serialized = self.binding.serialize() if self.binding is not None else None
            KDS.ConfigManager.SetSetting(f"{setting_path}/Primary", serialized)
        else:
            KDS.ConfigManager.SetSetting(f"{setting_path}/Primary", "default")

        if self.secondaryBinding != self._secondaryDefaultBinding:
            serialized = self.secondaryBinding.serialize() if self.secondaryBinding is not None else None
            KDS.ConfigManager.SetSetting(f"{setting_path}/Secondary", serialized)
        else:
            KDS.ConfigManager.SetSetting(f"{setting_path}/Secondary", "default")

    def _register_event(self, event: pygame.event.Event) -> None:
        """Register an event for this key. The key is handled if the event matches."""
        for binding in (self.binding, self.secondaryBinding):
            if binding is None:
                continue

            setState: bool | None = None
            if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                if event.button == binding.key:
                    setState = (event.type == MOUSEBUTTONDOWN)
            elif event.type in (KEYDOWN, KEYUP):
                if event.key == binding.key:
                    setState = (event.type == KEYDOWN)

            if setState is not None:
                self.SetState(setState)
                if setState and self._onDownCallback is not None:
                    self._onDownCallback()

class InventoryKey(Key):
    def __init__(self, defaultBinding: Binding, inventory_index: int) -> None:
        super().__init__(f"inventory{inventory_index}", defaultBinding, None)
        self.index = inventory_index

def _onDownHandlerDebug():
    KDS.Debug.Enabled = not KDS.Debug.Enabled
    KDS.Logging.Profiler(KDS.Debug.Enabled)

def _onDownHandlerFullscreen():
    pygame.display.toggle_fullscreen()
    KDS.ConfigManager.ToggleSetting("Renderer/fullscreen", ...)

moveUp = Key("moveUp", Binding(BindingType.keyboard, K_w), Binding(BindingType.keyboard, K_SPACE))
moveDown = Key("moveDown", Binding(BindingType.keyboard, K_s), Binding(BindingType.keyboard, K_LCTRL))
moveRight = Key("moveRight", Binding(BindingType.keyboard, K_d), None)
moveLeft = Key("moveLeft", Binding(BindingType.keyboard, K_a), None)
moveRun = Key("moveRun", Binding(BindingType.keyboard, K_LSHIFT), None)
functionKey = Key("functionKey", Binding(BindingType.keyboard, K_e), None)
actionKey = Key("actionKey", Binding(BindingType.mouse, 1), Binding(BindingType.keyboard, K_r))
altUp = Key("altUp", Binding(BindingType.keyboard, K_UP), None)
altDown = Key("altDown", Binding(BindingType.keyboard, K_DOWN), None)
altLeft = Key("altLeft", Binding(BindingType.keyboard, K_LEFT), None)
altRight = Key("altRight", Binding(BindingType.keyboard, K_RIGHT), None)
fart = Key("fart", Binding(BindingType.keyboard, K_f), None)
dropItem = Key("dropItem", Binding(BindingType.keyboard, K_q), None)
terminal = Key("terminal", Binding(BindingType.keyboard, K_t), None)
hideUI = Key("hideUI", Binding(BindingType.keyboard, K_F1), None)
screenshot = Key("screenshot", Binding(BindingType.keyboard, K_F12), None)
toggleDebug = Key("toggleDebug", Binding(BindingType.keyboard, K_F3), None, onDownCallback=_onDownHandlerDebug)
toggleFullscreen = Key("toggleFullscreen", Binding(BindingType.keyboard, K_F11), None, onDownCallback=_onDownHandlerFullscreen)

Inventory1 = InventoryKey(Binding(BindingType.keyboard, K_1), 0)
Inventory2 = InventoryKey(Binding(BindingType.keyboard, K_2), 1)
Inventory3 = InventoryKey(Binding(BindingType.keyboard, K_3), 2)
Inventory4 = InventoryKey(Binding(BindingType.keyboard, K_4), 3)
Inventory5 = InventoryKey(Binding(BindingType.keyboard, K_5), 4)
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

class RebindLabel(NamedTuple):
    title: str
    description: str | None = None

REBINDABLEKEYS: tuple[tuple[RebindLabel, Key], ...] = (
    (RebindLabel("Move Up"), moveUp),
    (RebindLabel("Move Down"), moveDown),
    (RebindLabel("Move Left"), moveLeft),
    (RebindLabel("Move Right"), moveRight),
    (RebindLabel("Interact", "open door, pickup item, ..."), functionKey),
    (RebindLabel("Action", "shoot, throw, ..."), actionKey),
    (RebindLabel("Aim Up", "aim grenade"), altUp),
    (RebindLabel("Aim Down", "aim grenade"), altDown),
    (RebindLabel("Aim Left", "switch exam page"), altLeft),
    (RebindLabel("Aim Right", "switch exam page"), altRight),
    (RebindLabel("Fart"), fart),
    (RebindLabel("Drop Item"), dropItem),
    (RebindLabel("Open Terminal"), terminal),
    (RebindLabel("Hide UI"), hideUI),
    (RebindLabel("Take a Screenshot"), screenshot),
    (RebindLabel("Toggle Debug Mode"), toggleDebug),
    (RebindLabel("Toggle Fullscreen"), toggleFullscreen),

    (RebindLabel("Inventory Slot 1"), Inventory1),
    (RebindLabel("Inventory Slot 2"), Inventory2),
    (RebindLabel("Inventory Slot 3"), Inventory3),
    (RebindLabel("Inventory Slot 4"), Inventory4),
    (RebindLabel("Inventory Slot 5"), Inventory5)
)

def MoveIsUsingWASD() -> bool:
    def _internalHelper(key: int, b1: Binding | None, b2: Binding | None):
        if b1 is not None and b1.type == BindingType.keyboard and b1.key == key:
            return True
        if b2 is not None and b2.type == BindingType.keyboard and b2.key == key:
            return True
        return False

    return all((
        _internalHelper(K_w, moveUp.binding, moveUp.secondaryBinding),
        _internalHelper(K_s, moveDown.binding, moveDown.secondaryBinding),
        _internalHelper(K_a, moveLeft.binding, moveLeft.secondaryBinding),
        _internalHelper(K_d, moveRight.binding, moveRight.secondaryBinding),
    ))

def LoadCustomBindings():
    for key in keys.values():
        key.loadBindings()

def ResetCustomBindings():
    KDS.ConfigManager.SetSetting(f"Keys/Bindings", KDS.ConfigManager.JSON.EMPTY)
    LoadCustomBindings()

def RegisterEvent(event: pygame.event.Event):
    for key in keys.values():
        key._register_event(event)

def Update():
    """Call before event handling!"""
    for key in keys.values():
        key.update()

def Reset():
    for key in keys.values():
        key.SetState(False)

class _KeyData(NamedTuple):
    title: str
    description: str | None
    key: Key
    rebindButton1: KDS.UI.Button
    rebindButton2: KDS.UI.Button

def StartBindingMenu(display: pygame.Surface, eventHandler: Callable[[Any], bool]):
    def bindKey(key: Key, isAlt: bool):
        def setBindingValue(binding: Binding | None):
            if isAlt:
                # Do not allow multiple same bindings to the same key instance
                if key.binding == binding:
                    key.binding = None
                key.secondaryBinding = binding
            else:
                if key.secondaryBinding == binding:
                    key.secondaryBinding = None
                key.binding = binding
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
                        if event.key == K_x: # Delete Binding
                            setBindingValue(None)
                            running2 = False
                        elif event.key == K_d: # Restore Default
                            setBindingValue(key._defaultBinding if not isAlt else key._secondaryDefaultBinding)
                            running2 = False
                    elif event.key == K_ESCAPE: # Cancel
                        running2 = False
                    else: # Rebind
                        if event.key not in REBINDBLACKLIST:
                            setBindingValue(Binding(BindingType.keyboard, event.key))
                            running2 = False
                        else:
                            KDS.System.MessageBox.Show("Not Allowed", "This key cannot be bound because it is integral to the applications operation.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.WARNING)
                elif event.type == MOUSEBUTTONDOWN:
                    setBindingValue(Binding(BindingType.mouse, event.button))
                    running2 = False

            display.fill(KDS.Colors.Gray)
            dest1 = (display_size[0] // 2 - BindText.get_width() // 2, display_size[1] // 2 - BindText.get_height() // 2)
            display.blit(BindText, dest1)
            dest2 = (display_size[0] // 2 - BindHelperText.get_width() // 2, dest1[1] + BindText.get_height() // 2 + 20)
            display.blit(BindHelperText, dest2)

            pygame.display.flip()

    running = True
    buttonPadding = 10
    textMarginLeft = 10
    textMarginBetween = 20
    buttonWidth = 400
    buttonHeight = 50
    display_size = display.get_size()
    ArialFont = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", 28)
    ArialFontShrinkedItalic = pygame.font.Font("Assets/Fonts/Windows/ariali.ttf", 18)
    BindText: pygame.Surface = ArialFont.render("Press a key to bind it.", True, KDS.Colors.White)
    BindHelperText: pygame.Surface = ArialFont.render("CTRL + X: Delete Binding | CTRL + D: Restore Default Binding | Escape: Cancel Binding", True, KDS.Colors.White)

    raw_scroll: float = 0
    headerSize: int = ArialFont.get_height() + 20

    keyDatas: List[_KeyData] = []
    keyMaxY = 0
    def loadKeyDatas():
        nonlocal keyDatas, keyMaxY

        def renderBindingText(key: Key, isSecondary: bool) -> pygame.Surface:
            defaultBinding: Binding | None = key._defaultBinding if not isSecondary else key._secondaryDefaultBinding
            binding: Binding | None = key.binding if not isSecondary else key.secondaryBinding

            if binding is None:
                return ArialFont.render("Unassigned", True, KDS.Colors.LightGray)
            # XXX: Naive approach using any (making this O(n²)), but this still runs 60 fps, so I don't really care...
            elif any((binding == k.binding or binding == k.secondaryBinding) and (k is not key or (k.binding == k.secondaryBinding)) for k in keys.values()):
                # k.binding == binding and k.secondaryBinding == binding => k.binding == k.secondaryBinding
                # ^^ check for multiple identical bindings for the same key...
                # We don't allow these kinds of bindings, but I left it here so that in case this behaviour changes later, we already have code that handles it.
                return ArialFont.render(binding.get_displayname(), True, KDS.Colors.Yellow)
            elif binding != defaultBinding:
                return ArialFont.render(binding.get_displayname(), True, (128, 255, 255))
            else:
                return ArialFont.render(binding.get_displayname(), True, KDS.Colors.White)

        keyDatas.clear()

        for index, (label, key) in enumerate(REBINDABLEKEYS):
            b2Rect = pygame.Rect(display_size[0] - buttonWidth - buttonPadding, buttonPadding + index * (buttonHeight + buttonPadding), buttonWidth, buttonHeight)
            b2Text = renderBindingText(key, isSecondary=True)
            button2 = KDS.UI.Button(b2Rect, bindKey, b2Text)

            b1Rect = pygame.Rect(b2Rect.left - buttonWidth - buttonPadding, b2Rect.top, b2Rect.width, b2Rect.height)
            b1Text = renderBindingText(key, isSecondary=False)
            button1 = KDS.UI.Button(b1Rect, bindKey, b1Text)

            keyDatas.append(_KeyData(label.title, label.description, key, button1, button2))

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
    # restart_tip: pygame.Surface = ArialFont.render("We recommend restarting the game if any changes were made.", True, KDS.Colors.White)
    primary_tip: pygame.Surface = ArialFont.render("Primary", True, KDS.Colors.White)
    secondary_tip: pygame.Surface = ArialFont.render("Secondary", True, KDS.Colors.White)

    left_pressed: bool = False
    while running:
        left_clicked: bool = False

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if eventHandler(event):
                continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    left_pressed = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if left_pressed:
                        left_clicked = True
                    left_pressed = False
            elif event.type == MOUSEWHEEL:
                raw_scroll = KDS.Math.Clamp(raw_scroll + event.precise_y * 20, -(keyMaxY - buttonHeight), 0)

        scroll: int = round(raw_scroll)

        display.fill(KDS.Colors.DefaultBackground)
        display.blit(primary_tip, (keyDatas[0].rebindButton1.rect.centerx - primary_tip.get_width() // 2, scroll + headerSize // 2 - primary_tip.get_height() // 2))
        display.blit(secondary_tip, (keyDatas[0].rebindButton2.rect.centerx - secondary_tip.get_width() // 2, scroll + headerSize // 2 - secondary_tip.get_height() // 2))

        for data in keyDatas:
            data.rebindButton1.rect.centery += scroll + headerSize
            data.rebindButton2.rect.centery += scroll + headerSize

            nameRnd: pygame.Surface = ArialFont.render(data.title, True, KDS.Colors.White)
            nameRndPos: tuple[int, int] = (textMarginLeft, data.rebindButton1.rect.centery - nameRnd.get_height() // 2)
            display.blit(nameRnd, nameRndPos)

            if data.description is not None:
                descRnd: pygame.Surface = ArialFontShrinkedItalic.render(data.description, True, KDS.Colors.LightGray)
                display.blit(descRnd, (nameRndPos[0] + nameRnd.get_width() + textMarginBetween, nameRndPos[1] + nameRnd.get_height() - descRnd.get_height()))

            data.rebindButton1.update(display, mouse_pos, left_clicked, data.key, False)
            data.rebindButton2.update(display, mouse_pos, left_clicked, data.key, True)

            data.rebindButton1.rect.centery -= scroll + headerSize
            data.rebindButton2.rect.centery -= scroll + headerSize

        reset_button.rect.centery += scroll + headerSize
        reset_button.update(display, mouse_pos, left_clicked)
        reset_button.rect.centery -= scroll + headerSize

        return_button.rect.centery += scroll + headerSize
        return_button.update(display, mouse_pos, left_clicked)
        return_button.rect.centery -= scroll + headerSize
        # display.blit(restart_tip, (return_button.rect.centerx - restart_tip.get_width() // 2, return_button.rect.bottom + scroll + headerSize + 10))

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))
        pygame.display.flip()
        KDS.Clock.Tick()
