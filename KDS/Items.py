import pygame
import sys
from pygame.locals import *
import numpy

import KDS.Math
import KDS.Animator

pygame.init()

tip_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10, bold=0, italic=0)
itemTip = tip_font.render("Nosta Esine [E]", True, KDS.Colors.GetPrimary.White)

inventoryDobulesSerialNumbers = []
inventory_items = []

def init(IDSN: list, II: list):
    global inventoryDobulesSerialNumbers, inventory_items
    inventoryDobulesSerialNumbers = IDSN
    inventory_items = II

class Item:

    def __init__(self, position: tuple, serialNumber: int, texture = None):
        if serialNumber:
            self.texture = texture
        self.rect = pygame.Rect(position[0], position[1]+(34-self.texture.get_size()[
                                1]), self.texture.get_size()[0], self.texture.get_size()[1])
        self.serialNumber = serialNumber

    @staticmethod
    # Item_list is a 2d numpy array
    def render(Item_list, Surface: pygame.Surface, scroll: list, DebugMode = False):
        for renderable in Item_list:
            if DebugMode:
                pygame.draw.rect(Surface, KDS.Colors.GetPrimary.Blue, pygame.Rect(renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
            Surface.blit(renderable.texture, (renderable.rect.x - scroll[0], renderable.rect.y-scroll[1]))

    @staticmethod
    def checkCollisions(Item_list, collidingRect: pygame.Rect, Surface: pygame.Surface, scroll, functionKey: bool, inventory):
        index = 0
        showItemTip = True
        collision = False
        shortest_index = 0
        shortest_distance = sys.maxsize
        for item in Item_list:
            if collidingRect.colliderect(item.rect):
                collision = True
                distance = KDS.Math.getDistance(item.rect.midbottom, collidingRect.midbottom)
                if distance < shortest_distance:
                    shortest_index = index
                    shortest_distance = distance
                if functionKey:
                    if item.serialNumber not in inventoryDobulesSerialNumbers:
                        if inventory.storage[inventory.SIndex] == "none":
                            temp_var = item.pickup()
                            if not temp_var:
                                inventory.storage[inventory.SIndex] = item.serialNumber
                                if item.serialNumber == 6:
                                    KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.iPuhelinPickup)
                            Item_list = numpy.delete(Item_list, index)
                            showItemTip = False
                        elif item.serialNumber not in inventory_items:
                            try:
                                item.pickup()
                                Item_list = numpy.delete(Item_list, index)
                                showItemTip = False
                            except IndexError as e:
                                KDS.Logging.Log(KDS.Logging.LogType.critical, f"A non-inventory item was tried to pick up and caused error: {e}")
                    else:
                        if inventory.SIndex < inventory.size-1 and inventory.storage[inventory.SIndex] == "none":
                            if inventory.storage[inventory.SIndex + 1] == "none":
                                item.pickup()
                                inventory.storage[inventory.SIndex] = item.serialNumber
                                inventory.storage[inventory.SIndex +
                                                  1] = "doubleItemPlaceholder"
                                Item_list = numpy.delete(Item_list, index)
                                showItemTip = False
            index += 1
        
        if collision and showItemTip:
            Surface.blit(itemTip, (Item_list[shortest_index].rect.centerx - int(itemTip.get_width() / 2) - scroll[0], Item_list[shortest_index].rect.bottom - 45 - scroll[1]))

        return Item_list, inventory

    def toString2(self):
        """Converts all textures to strings
        """
        if isinstance(self.texture, pygame.Surface):
            self.texture = (pygame.image.tostring(self.texture, "RGBA"), self.texture.get_size(), "RGBA")
            
    def fromString(self):
        """Converts all strings back to textures
        """
        if not isinstance(self.texture, pygame.Surface):
            self.texture = pygame.image.fromstring(self.texture[0], self.texture[1], self.texture[2])
            self.texture.set_colorkey(KDS.Colors.GetPrimary.White)

    def pickup(self):
        pass
    def use(self):
        pass
    def drop(self):
        pass
    def init(self):
        pass

class BlueKey(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Cell(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Coffeemug(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Gasburner(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class GreenKey(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class iPuhelin(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Knife(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class LappiSytytyspalat(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Medkit(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Pistol(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class PistolMag(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class rk62(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Shotgun(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class rk62Mag(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class ShotgunShells(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Plasmarifle(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Soulsphere(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class RedKey(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class SSBonuscard(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Turboneedle(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Ppsh41(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Awm(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class AwmMag(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class EmptyFlask(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class MethFlask(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class BloodFlask(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Grenade(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class FireExtinguisher(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class LevelEnder1(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Ppsh41Mag(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

class Lantern(Item):
    def __init__(self, position: tuple, serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

serialNumbers = {
    1: BlueKey,
    2: Cell,
    3: Coffeemug,
    4: Gasburner,
    5: GreenKey,
    6: iPuhelin,
    7: Knife,
    8: LappiSytytyspalat,
    9: Medkit,
    10:Pistol,
    11:PistolMag,
    12:Plasmarifle,
    13:RedKey,
    14:rk62Mag,
    15:rk62,
    16:Shotgun,
    17:ShotgunShells,
    18:Soulsphere,
    19:SSBonuscard,
    20:Turboneedle,
    21:Ppsh41,
    22:"",
    23:"",
    24:Awm,
    25:AwmMag,
    26:EmptyFlask,
    27:MethFlask,
    28:BloodFlask,
    29:Grenade,
    30:FireExtinguisher,
    31:LevelEnder1,
    32:Ppsh41Mag,
    33:Lantern
}