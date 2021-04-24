from __future__ import annotations
import dataclasses
from typing import Dict, Any, Sequence, List, Tuple, Set, Type, Optional, Union
import pygame
import KDS.World
import KDS.ConfigManager
import KDS.Colors
import KDS.Missions
import KDS.Math
import KDS.Logging
import KDS.Inventory
import KDS.Keys
import KDS.Build
import KDS.Scores
import KDS.Audio
import KDS.Animator

def init(tileData: Dict[str, Dict[str, Any]], itemData: Dict[str, Dict[str, Any]], t_textures: Dict[int, pygame.Surface], i_textures: Dict[int, pygame.Surface]):
    Tile.noCollision.clear()
    Tile.trueScale.clear()
    Tile.specialTiles.clear()
    for d in tileData.values():
        if d["noCollision"] == True:
            Tile.noCollision.add(d["serialNumber"])
        if d["trueScale"] == True:
            Tile.trueScale.add(d["serialNumber"])
        if d["specialTile"] == True:
            Tile.specialTiles.add(d["serialNumber"])

    Item.inventoryItems.clear()
    Item.inventoryDoubles.clear()
    Item.contraband.clear()
    for d in itemData.values():
        if d["supportsInventory"] == True:
            Item.inventoryItems.add(d["serialNumber"])
        if d["doubleSize"] == True:
            Item.inventoryDoubles.add(d["serialNumber"])
        if d["isContraband"] == True:
            Item.contraband.add(d["serialNumber"])

    Tile._renderPadding = KDS.ConfigManager.GetSetting("Renderer/Tile/renderPadding", 8)
    Tile._textures = t_textures
    Item._textures = i_textures

class Tile:
    specialTilesClasses: Dict[int, Type[Tile]] = {}

    noCollision: Set[int] = set()
    trueScale: Set[int] = set()
    specialTiles: Set[int] = set()

    _renderPadding: int = 0
    _textures: Dict[int, pygame.Surface] = {}

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        self.serialNumber = serialNumber
        self.texture = Tile._textures[self.serialNumber] if serialNumber != -1 else None
        if serialNumber in Tile.trueScale:
            self.rect = pygame.Rect(position[0] - self.texture.get_width() + 34, position[1] - self.texture.get_height() + 34, self.texture.get_width(), self.texture.get_height())
        else:
            self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.specialTileFlag = serialNumber in Tile.specialTiles
        self.checkCollision = serialNumber not in Tile.noCollision
        self.collisionDirection = KDS.World.CollisionDirection.All
        self.lateRender = False
        self.darkOverlay: Optional[pygame.Surface] = None
        self.removeFlag: bool = False

    @staticmethod
    def renderUnit(unit: Tile, surface: pygame.Surface, scroll: Sequence[int]):
        if not unit.specialTileFlag:
            if unit.texture != None:
                surface.blit(unit.texture, (unit.rect.x - scroll[0], unit.rect.y - scroll[1]))
        else:
            texture = unit.update()
            if texture != None:
                surface.blit(texture, (unit.rect.x - scroll[0], unit.rect.y - scroll[1]))

        if unit.darkOverlay != None:
            surface.blit(unit.darkOverlay, (unit.rect.x - scroll[0], unit.rect.y - scroll[1]))

    @staticmethod
    # Tile_list is a list in a list in a list... Also known as a 3D array. Z axis is determined by index. Higher index means more towards the camera. Overlays are a different story
    def renderUpdate(Tile_list: List[List[List[Tile]]], surface: pygame.Surface, center_position: Tuple[int, int], scroll: Sequence[int], debugMode: bool):
        start_x = round((center_position[0] / 34) - ((surface.get_width() / 34) / 2)) - 1 - Tile._renderPadding
        start_y = round((center_position[1] / 34) - ((surface.get_height() / 34) / 2)) - 1 - Tile._renderPadding
        start_x = max(start_x, 0)
        start_y = max(start_y, 0)
        end_x = round((center_position[0] / 34) + ((surface.get_width() / 34) / 2)) + Tile._renderPadding
        end_y = round((center_position[1] / 34) + ((surface.get_height() / 34) / 2)) + Tile._renderPadding
        end_x = min(end_x, len(Tile_list[0]))
        end_y = min(end_y, len(Tile_list))

        lateRender = []
        for unscaled_y, row in enumerate(Tile_list[start_y:end_y]):
            for unscaled_x, unit in enumerate(row[start_x:end_x]):
                for renderable in unit:
                    if renderable.lateRender:
                        lateRender.append(renderable)
                        continue

                    if debugMode:
                        pygame.draw.rect(surface, KDS.Colors.Cyan, (renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
                    Tile.renderUnit(renderable, surface, scroll)
                    if renderable.removeFlag:
                        Tile_list[unscaled_y + start_y][unscaled_x + start_x].remove(renderable)

        for renderable in lateRender:
            if debugMode:
                pygame.draw.rect(surface, KDS.Colors.RiverBlue, (renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
            Tile.renderUnit(renderable, surface, scroll)

    def update(self) -> Optional[pygame.Surface]:
        KDS.Logging.AutoError(f"No custom update initialised for tile: \"{self.serialNumber}\"!")
        return self.texture

    def lateInit(self) -> None:
        pass

class Item:
    infiniteAmmo: bool = False

    serialNumbers: Dict[int, Type[Item]] = {}

    tipItem = None

    fall_speed: float = 1.0
    fall_max_velocity: float = 8.0

    inventoryItems: Set[int] = set()
    inventoryDoubles: Set[int] = set()
    contraband: Set[int] = set()

    _textures: Dict[int, pygame.Surface] = {}

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture: pygame.Surface = None):
        self.texture = texture if texture != None else Item._textures[serialNumber]
        self.texture_size = self.texture.get_size() if self.texture != None else (0, 0)
        self.rect = pygame.Rect(position[0], position[1] + (34 - self.texture_size[1]), self.texture_size[0], self.texture_size[1])
        self.serialNumber = serialNumber
        self.physics = False
        self.momentum = 0

    @staticmethod
    # Item_list is a list
    def renderUpdate(Item_list: Sequence[Item], Tile_list: List[List[List[Tile]]], Surface: pygame.Surface, scroll: Sequence[int], DebugMode = False):
        for renderable in Item_list:
            if DebugMode:
                pygame.draw.rect(Surface, KDS.Colors.Blue, (renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
            if renderable.texture != None:
                Surface.blit(renderable.texture, (renderable.rect.x - scroll[0], renderable.rect.y - scroll[1]))
            if renderable.physics:
                renderable.momentum = min(renderable.momentum + Item.fall_speed, Item.fall_max_velocity)
                renderable.rect.y += int(renderable.momentum)
                collisions = KDS.World.collision_test(renderable.rect, Tile_list)
                if len(collisions) > 0:
                    renderable.rect.bottom = collisions[0].rect.top
                    renderable.physics = False

    @staticmethod
    def checkCollisions(Item_list: List[Item], collidingRect: pygame.Rect, functionKey: bool, inventory):
        showItemTip = True
        collision = False
        shortest_item = None
        shortest_distance = KDS.Math.MAXVALUE

        for item in Item_list:
            if collidingRect.colliderect(item.rect):
                collision = True
                distance = KDS.Math.getDistance(item.rect.midbottom, collidingRect.midbottom)
                if distance < shortest_distance:
                    shortest_item = item
                    shortest_distance = distance

                if not functionKey:
                    continue

                if item.serialNumber not in Item.inventoryDoubles:
                    if inventory.storage[inventory.SIndex] == KDS.Inventory.EMPTYSLOT:
                        if not item.pickup():
                            inventory.storage[inventory.SIndex] = item
                            KDS.Missions.Listeners.ItemPickup.Trigger(item.serialNumber)
                        Item_list.remove(item) # Remove seems to search for instance and not equality
                        showItemTip = False
                    elif item.serialNumber not in Item.inventoryItems:
                        try:
                            item.pickup()
                            Item_list.remove(item)
                            showItemTip = False
                        except Exception as e:
                            KDS.Logging.AutoError(f"An error occured while trying to pick up a non-inventory item. Details below:\n{e}")
                else:
                    if inventory.SIndex < inventory.size - 1:
                        if inventory.storage[inventory.SIndex] == KDS.Inventory.EMPTYSLOT and inventory.storage[inventory.SIndex + 1] == KDS.Inventory.EMPTYSLOT:
                            item.pickup()
                            inventory.storage[inventory.SIndex] = item
                            inventory.storage[inventory.SIndex + 1] = KDS.Inventory.DOUBLEITEM
                            Item_list.remove(item)
                            showItemTip = False

        Item.tipItem = shortest_item if collision and showItemTip else None

    def pickup(self):
        return False # Seems to return False if we want to put in inventory

    def use(self):
        return self.texture

    def drop(self) -> bool:
        return True

    def lateInit(self):
        pass

class Weapon(Item):
    @dataclasses.dataclass
    class WeaponData:
        counter: int
        ammo: Union[int, float]

    data: Dict[Type[Weapon], Weapon.WeaponData] = {}

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture: pygame.Surface) -> None:
        super().__init__(position, serialNumber, texture=texture)

                                                # float to pass infinite through
    def internalInit(self, repeat_rate: int, defaultAmmo: Union[int, float], shootTexture: Optional[Union[pygame.Surface, KDS.Animator.Animation]], shootSound: Optional[pygame.mixer.Sound], stopSound: bool = False, allowHold: bool = False) -> None:
        self.repeat_rate = repeat_rate
        if type(self) not in Weapon.data:
            Weapon.data[type(self)] = Weapon.WeaponData(self.repeat_rate + 1, defaultAmmo)
        else:
            Weapon.data[type(self)].counter = self.repeat_rate + 1
        self.sound = shootSound
        self.stopSound = stopSound
        self.f_texture = shootTexture
        self.allowHold = allowHold

    def internalShoot(self) -> bool:
        if Weapon.data[type(self)].counter > self.repeat_rate:
            if self.stopSound and self.sound != None:
                self.sound.stop()
            if Weapon.data[type(self)].ammo > 0 or KDS.Build.Item.infiniteAmmo:
                if self.sound != None:
                    KDS.Audio.PlaySound(self.sound)
                Weapon.data[type(self)].counter = 0
                Weapon.data[type(self)].ammo -= 1 # Infinity - 1 is still infinity
                return True
        return False

    def shoot(self) -> bool:
        """
        ### OVERLOAD EXAMPLE
        super().shoot()\n
        Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))\n
        Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 30 * KDS.Convert.ToMultiplier(Player.direction), Player.rect.y + 13, 2, 2), Player.direction, -1, tiles, 100))\n
        ### OVERLOAD EXAMPLE
        """
        return self.internalShoot()

    def use(self) -> pygame.Surface:
        if KDS.Keys.mainKey.onDown or (self.allowHold and KDS.Keys.mainKey.pressed):
            if self.shoot() and self.f_texture != None:
                return self.f_texture if not isinstance(self.f_texture, KDS.Animator.Animation) else self.f_texture.update()
        elif self.stopSound and self.sound != None:
            self.sound.stop()
        Weapon.data[type(self)].counter += 1
        return self.texture

    def pickup(self) -> bool:
        Weapon.data[type(self)].counter = self.repeat_rate + 1
        if isinstance(self.f_texture, KDS.Animator.Animation):
            self.f_texture.tick = 0
        return super().pickup()

    def getAmmo(self) -> Union[int, float]:
        return Weapon.data[type(self)].ammo

    @staticmethod
    def addAmmo(_type: Type[Weapon], amount: Union[int, float]) -> None:
        Weapon.data[_type].ammo += amount

    @staticmethod
    def reset() -> None:
        Weapon.data.clear()

class Ammo(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture: pygame.Surface):
        super().__init__(position, serialNumber, texture=texture)

    def internalInit(self, _type: Type[Weapon], addAmmo: int, addScore: int, sound: pygame.mixer.Sound):
        self.sound = sound
        self.type = _type
        self.add = addAmmo
        self.score = addScore

    def use(self):
        if KDS.Keys.mainKey.onDown:
            self.pickup()
        return self.texture

    def pickup(self):
        KDS.Scores.score += self.score
        KDS.Audio.PlaySound(self.sound)
        Weapon.data[self.type].ammo += self.add
        return True