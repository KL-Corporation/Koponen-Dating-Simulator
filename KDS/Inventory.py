from __future__ import annotations
from typing import List, Union, Tuple, Optional, Sequence, Type
import pygame
import KDS.World
import KDS.Build
import KDS.Missions
import KDS.Linq

class Inventory:
    emptySlot = "none"
    doubleItem = "doubleItem"

    def __init__(self, size: int):
        self.storage: List[Union[KDS.Build.Item, str]] = [Inventory.emptySlot for _ in range(size)]
        self.size: int = size
        self.SIndex: int = 0
        self.offset: Tuple[int, int] = (10, 75)

    def __len__(self) -> int:
        return len(self.storage)

    def empty(self):
        self.storage = [Inventory.emptySlot for _ in range(self.size)]

    def render(self, Surface: pygame.Surface):
        pygame.draw.rect(Surface, (192, 192, 192), (self.offset[0], self.offset[1], self.size * 34, 34), 3)

        item = self.storage[self.SIndex]
        slotwidth = 34 if isinstance(item, str) or item.serialNumber not in KDS.Build.Item.inventoryDoubles else 68

        pygame.draw.rect(Surface, (70, 70, 70), (self.SIndex * 34 + self.offset[0], self.offset[1], slotwidth, 34), 3)

        for index, item in enumerate(self.storage):
            if not isinstance(item, str) and item.serialNumber in KDS.Build.Item._textures:
                slotwidth = 34 if isinstance(item, str) or item.serialNumber not in KDS.Build.Item.inventoryDoubles else 68
                bdRect = item.texture.get_bounding_rect()
                diff = (slotwidth - bdRect.width, 34 - bdRect.height)
                Surface.blit(item.texture, (index * 34 + self.offset[0] + diff[0] // 2 - bdRect.x, self.offset[1] + diff[1] // 2 - bdRect.y))

    def moveRight(self):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        self.SIndex += 1
        if self.SIndex >= self.size:
            self.SIndex = 0
        if self.storage[self.SIndex] == Inventory.doubleItem:
            self.SIndex += 1

    def moveLeft(self):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        self.SIndex -= 1
        if self.SIndex < 0:
            self.SIndex = self.size - 1
        if self.storage[self.SIndex] == Inventory.doubleItem:
            self.SIndex -= 1

    def pickSlot(self, index: int):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        if 0 <= index < len(self.storage):
            if self.storage[index] == Inventory.doubleItem:
                self.SIndex = index - 1
            else:
                self.SIndex = index

    def getSlot(self, itemSerial: int) -> Optional[int]:
        var = KDS.Linq.FirstOrNone(self.storage, lambda i: not isinstance(i, str) and i.serialNumber == itemSerial)
        if var != None:
            return self.storage.index(var)
        return None

    def dropItemAtIndex(self, index: int, forceDrop: bool = False) -> Optional[KDS.Build.Item]:
        toDrop = self.storage[index]
        if not isinstance(toDrop, str):
            KDS.Missions.Listeners.ItemDrop.Trigger(toDrop.serialNumber)
            if index < self.size - 1:
                if self.storage[index + 1] == Inventory.doubleItem:
                    self.storage[index + 1] = Inventory.emptySlot
            if toDrop.drop() == True or forceDrop:
                self.storage[index] = Inventory.emptySlot
                return toDrop
        return None

    def dropItem(self) -> Optional[KDS.Build.Item]:
        return self.dropItemAtIndex(self.SIndex)

    def useItemAtIndex(self, index: int, rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        item = self.storage[index]
        if not isinstance(item, str):
            dumpVals = item.use()
            if direction: renderOffset = -dumpVals.get_width()
            else: renderOffset = rect.width + 2

            surface.blit(pygame.transform.flip(dumpVals, direction, False), (rect.x - scroll[0] + renderOffset, rect.y + 10 -scroll[1]))
        return None

    def useItem(self, rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        self.useItemAtIndex(self.SIndex, rect, direction, surface, scroll)

    def useItemByClass(self, Class: Type, rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        for i, v in enumerate(self.storage):
            if isinstance(v, Class):
                self.useItemAtIndex(i, rect, direction, surface, scroll)
                return

    def useItemsByClasses(self, Classes: Sequence[Type], rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        for c in Classes:
            if not isinstance(self.getHandItem(), c) and any(isinstance(item, c) for item in self.storage):
                self.useItemByClass(c, rect, direction, surface, scroll)


    # def useSpecificItem(self, index: int, Surface: pygame.Surface, *args):
    #     dumpValues = nullLantern.use(args, Surface)
    #     if direction:
    #         renderOffset = -dumpValues.get_size()[0]
    #     else:
    #         renderOffset = Player.rect.width + 2
    #
    #     Surface.blit(pygame.transform.flip(dumpValues, direction, False), (Player.rect.x - scroll[0] + renderOffset, Player.rect.y + 10 -scroll[1]))
    #     return None

    def getHandItem(self):
        return self.storage[self.SIndex]

    def getCount(self):
        count = 0
        for i in range(self.size):
            if self.storage[i] != Inventory.emptySlot:
                count += 1
        return count