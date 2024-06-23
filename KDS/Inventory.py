from __future__ import annotations
from typing import List, Literal, Union, Tuple, Optional, Sequence, Type
import pygame
import KDS.Colors
import KDS.Debug
import KDS.World
import KDS.Build
import KDS.Missions
import KDS.Linq

EMPTYSLOT: Literal["none"] = "none"
DOUBLEITEM: Literal["DOUBLEITEM"] = "DOUBLEITEM"

class Inventory:
    """The rect passed into the functions is the parent entity's rect (player rect, teacher rect, NPC rect, ...)"""

    def __init__(self, size: int, storage: Sequence[Union[KDS.Build.Item, str]] | None = None):
        self.storage: List[Union[KDS.Build.Item, str]] = [EMPTYSLOT for _ in range(size)]
        if storage != None:
            for i in range(min(len(storage), len(self.storage))):
                self.storage[i] = storage[i]
        self.size: int = size
        self.SIndex: int = 0
        self.offset: Tuple[int, int] = (10, 75)

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, index: int) -> Union[KDS.Build.Item, None]:
        item = self.storage[index]

        if isinstance(item, str):
            if item == EMPTYSLOT:
                return None
            if item == DOUBLEITEM:
                item = self.storage[index - 1]
                if isinstance(item, KDS.Build.Item):
                    return item
                else:
                    raise RuntimeError(f"Unexpected type \"{type(item)}\" for double item!")
            else:
                raise RuntimeError(f"Unexpected value \"{item}\" for string item!")

        return item

    def __iter__(self):
        self.next = 0
        return self

    def __next__(self):
        if self.next >= self.size:
            raise StopIteration
        result = self.__getitem__(self.next)
        self.next += 1
        return result

    def clear(self):
        self.storage = [EMPTYSLOT for _ in range(self.size)]

    def render(self, Surface: pygame.Surface):
        RECT_WIDTH: int = 3
        RECT_BORDER_RADIUS: int = round(RECT_WIDTH / 2)

        pygame.draw.rect(Surface, (192, 192, 192), (self.offset[0], self.offset[1], self.size * 34, 34), RECT_WIDTH, border_radius=RECT_BORDER_RADIUS)

        item = self.storage[self.SIndex]
        slotwidth = 34 if isinstance(item, str) or item.serialNumber not in KDS.Build.Item.inventoryDoubles else 68

        pygame.draw.rect(Surface, (70, 70, 70), (self.SIndex * 34 + self.offset[0], self.offset[1], slotwidth, 34), RECT_WIDTH, border_radius=RECT_BORDER_RADIUS)

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
        if self.storage[self.SIndex] == DOUBLEITEM:
            self.SIndex += 1
        if self.SIndex >= self.size: # Has to be double checked... Or not really, but I'm too lazy to code anything smarter
            self.SIndex = 0

    def moveLeft(self):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        self.SIndex -= 1
        if self.SIndex < 0:
            self.SIndex = self.size - 1
        if self.storage[self.SIndex] == DOUBLEITEM:
            self.SIndex -= 1
        if self.SIndex < 0:
            self.SIndex = self.size - 1

    def pickSlot(self, index: int):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        if 0 <= index < len(self.storage):
            if self.storage[index] == DOUBLEITEM:
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
                if self.storage[index + 1] == DOUBLEITEM:
                    self.storage[index + 1] = EMPTYSLOT
            if toDrop.drop() == True or forceDrop:
                self.storage[index] = EMPTYSLOT
                return toDrop
        return None

    def dropItem(self, forceDrop: bool = False) -> Optional[KDS.Build.Item]:
        return self.dropItemAtIndex(self.SIndex, forceDrop)

    def pickupItemToIndex(self, index: int, item: KDS.Build.Item, *, force: bool = False, set_index: bool = False) -> bool:
        if self.storage[index] != EMPTYSLOT and not force:
            return False
        if item.serialNumber in KDS.Build.Item.inventoryDoubles:
            if index >= self.size - 1:
                index = self.size - 2
            if self.storage[index + 1] != EMPTYSLOT and index > 0:
                index -= 1
            if self.storage[index + 1] != EMPTYSLOT and not force:
                return False
            if self.storage[index] != EMPTYSLOT and not force:
                return False
            self.storage[index + 1] = DOUBLEITEM
        self.storage[index] = item
        if set_index:
            self.SIndex = index
        return True

    # Use kw only args so that when I make changes, dependant systems don't break without an exception
    def pickupItem(self, item: KDS.Build.Item, *, allow_find_empty_slot: bool = False, force: bool = False) -> bool:
        if not allow_find_empty_slot:
            # Keep the old inventory behaviour as default
            # so that I don't have to test all of the other systems that depend on this method
            # Player just overrides the allow_find_empty_slot flag
            return self.pickupItemToIndex(self.SIndex, item, force=force, set_index=True)
        else:
            # Cycle inventory slots and try to pick up until a free slot is found
            startingIndex: int = self.SIndex
            for i_offset in range(self.size + 1): # size + 1 so that if inventory is full, we have returned to the original offset index
                self.SIndex = (startingIndex + i_offset) % self.size
                if self.pickupItemToIndex(self.SIndex, item, force=force, set_index=True):
                    return True

            assert(not force) # force should always return True
            return False

    def useItemAtIndex(self, index: int, rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        item = self.storage[index]
        if not isinstance(item, str):
            dumpVals = item.use()
            Inventory.renderItemTexture(dumpVals, rect, direction, surface, scroll)
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

    @staticmethod
    def renderItemTexture(texture: pygame.Surface, rect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int]):
        if direction:
            renderOffset = -texture.get_width() - 2
        else:
            renderOffset = rect.width + 2

        dest: tuple[int, int] = (rect.x - scroll[0] + renderOffset, rect.y + 10 -scroll[1])
        if KDS.Debug.Enabled:
            pygame.draw.rect(surface, KDS.Colors.RiverBlue, (*dest, *texture.get_size()))
        surface.blit(pygame.transform.flip(texture, direction, False), dest)

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
            if self.storage[i] != EMPTYSLOT:
                count += 1
        return count
