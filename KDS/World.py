from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Type, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.AI
import KDS.NPC
import KDS.Teachers
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math
import KDS.World
import KDS.ConfigManager
import KDS.Missions
import KDS.Linq
import KDS.Build

import dataclasses

from enum import auto, IntFlag

pygame.init()
pygame.key.stop_text_input()

def init():
    Lighting.Shapes.circle_softest = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_softest.png").convert_alpha())
    Lighting.Shapes.circle_soft = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_soft.png").convert_alpha())
    Lighting.Shapes.circle_softer = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_softer.png").convert_alpha())
    Lighting.Shapes.circle = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle.png").convert_alpha())
    Lighting.Shapes.circle_harder = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_harder.png").convert_alpha())
    Lighting.Shapes.circle_hard = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_hard.png").convert_alpha())
    Lighting.Shapes.circle_hardest = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/circle_hardest.png").convert_alpha())
    Lighting.Shapes.cone_hard = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_hard.png").convert_alpha())
    Lighting.Shapes.cone_small_hard = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_small_hard.png").convert_alpha())
    Lighting.Shapes.cone_narrow = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_narrow.png").convert_alpha())
    Lighting.Shapes.splatter = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/splatter.png").convert_alpha())
    Lighting.Shapes.fluorecent = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/fluorecent.png").convert_alpha())

def collision_test(rect: pygame.Rect, Tile_list: List[List[List]]):
    hit_list = []

    max_x = len(Tile_list[0]) - 1
    max_y = len(Tile_list) - 1
    x = KDS.Math.Clamp(int(rect.x / 34 - 3), 0, max_x)
    y = KDS.Math.Clamp(int(rect.y / 34 - 3), 0, max_y)
    end_x = KDS.Math.Clamp(x + 6, 0, max_x)
    end_y = KDS.Math.Clamp(y + 6, 0, max_y)

    for row in Tile_list[y:end_y]:
        for unit in row[x:end_x]:
            for tile in unit:
                if rect.colliderect(tile.rect) and tile.checkCollision:
                    hit_list.append(tile)
    return hit_list

@dataclasses.dataclass
class Collisions: # Direction relative to rect (player / entity)
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False

class CollisionDirection(IntFlag): # Direction relative to tile
    Left = 1
    Right = 2
    Top = 4
    Bottom = 8

    Horizontal = 3
    Vertical = 12

    All = 15

class EntityMover:
    def __init__(self, w_sounds: Optional[Dict[str, Sequence[pygame.mixer.Sound]]] = None) -> None:
        self.walkSounds = w_sounds

    def move(self, rect: pygame.Rect, movement: Sequence[float], tiles: List[List[List]], playWalkSound: bool = False) -> Collisions:
        if len(movement) != 2:
            raise ValueError(f"Invalid movement size! Expected: 2, Got: {len(movement)}.")

        collisions = Collisions()

        rect.x += round(movement[0])
        hit_list = collision_test(rect, tiles)
        for tile in hit_list: # CollisionDirection is inverted, because it is relative to tile
            if movement[0] > 0 and CollisionDirection.Left in tile.collisionDirection:
                rect.right = tile.rect.left
                collisions.right = True
            elif movement[0] < 0 and CollisionDirection.Right in tile.collisionDirection:
                rect.left = tile.rect.right
                collisions.left = True

        rect.y += round(movement[1])
        # Has to be checked twice or my testing of merging these two went horribly wrong
        hit_list = collision_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0 and CollisionDirection.Top in tile.collisionDirection and tile.rect.bottom > rect.bottom:
                rect.bottom = tile.rect.top
                collisions.bottom = True
                if movement[0] != 0 and self.walkSounds != None and playWalkSound:
                    KDS.Audio.PlaySound(random.choice(self.walkSounds["default"]))
            elif movement[1] < 0 and CollisionDirection.Bottom in tile.collisionDirection:
                rect.top = tile.rect.bottom
                collisions.top = True
        return collisions

class Lighting:

    class Shapes:

        class LightShape:
            def __init__(self, texture: pygame.Surface) -> None:
                self.texture = texture
                self.rendered: Dict[int, Dict[Union[int, Tuple[float, float, float], str], pygame.Surface]] = {}

            def getRadius(self, radius: int) -> Dict[Union[int, Tuple[float, float, float], str], pygame.Surface]:
                if radius not in self.rendered:
                    self.rendered[radius] = { "default": pygame.transform.smoothscale(self.texture, (radius, radius)) }
                return self.rendered[radius]

            def get(self, radius: int, color: int):
                """Returns a light shape from memory

                Args:
                    radius (int): Light radius in pixels.
                    color (int): A Correlated Color Temperature (in Kelvin) that will determine the light's color.

                Returns:
                    Surface: The surface that contains the light texture
                """
                corRad = self.getRadius(radius)

                if color not in corRad:
                    tmp_tex: Any = corRad["default"].copy()
                    convCol = KDS.Convert.CorrelatedColorTemperatureToRGB(color)
                    tmp_tex.fill((convCol[0], convCol[1], convCol[2], 255), special_flags=BLEND_RGBA_MULT)
                    corRad[color] = tmp_tex
                return corRad[color]

            def getColor(self, radius: int, hue: float, saturation: float, value: float):
                corRad = self.getRadius(radius)
                color = (hue, saturation, value)

                if color not in corRad:
                    tmp_tex: Any = corRad["default"].copy()
                    convCol = KDS.Convert.HSVToRGB(hue, saturation, value)
                    tmp_tex.fill((int(convCol[0]), int(convCol[1]), int(convCol[2]), 255), special_flags=BLEND_RGBA_MULT)
                    corRad[color] = tmp_tex
                return corRad[color]

        @staticmethod
        def clear():
            for v in Lighting.Shapes.__dict__.values():
                if isinstance(v, Lighting.Shapes.LightShape):
                    v.rendered = {}

        circle_softest: LightShape = LightShape(pygame.Surface((0, 0)))
        circle_soft: LightShape = LightShape(pygame.Surface((0, 0)))
        circle_softer: LightShape = LightShape(pygame.Surface((0, 0)))
        circle: LightShape = LightShape(pygame.Surface((0, 0)))
        circle_harder: LightShape = LightShape(pygame.Surface((0, 0)))
        circle_hard: LightShape = LightShape(pygame.Surface((0, 0)))
        circle_hardest: LightShape = LightShape(pygame.Surface((0, 0)))
        cone_hard: LightShape = LightShape(pygame.Surface((0, 0)))
        cone_small_hard: LightShape = LightShape(pygame.Surface((0, 0)))
        cone_narrow: LightShape = LightShape(pygame.Surface((0, 0)))
        splatter: LightShape = LightShape(pygame.Surface((0, 0)))
        fluorecent: LightShape = LightShape(pygame.Surface((0, 0)))

    @staticmethod
    def circle_surface(radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    @staticmethod
    def lamp_cone(topwidth, bottomwidth, height, color):
        surf = pygame.Surface((bottomwidth, height))
        pygame.draw.polygon(surf, color, [(bottomwidth / 2 + topwidth / 2, 0), (bottomwidth / 2 - topwidth / 2, 0), (0, height), (bottomwidth, height)])
        surf.set_colorkey((0, 0, 0))
        return surf

    class Light:
        def __init__(self, position: Tuple[int, int], shape: pygame.Surface, positionFromCenter: bool = False):
            """Instantiates a new light.

            Args:
                position (Tuple[int, int]): The position where the light will be rendered.
                shape (Lighting.Shapes): The shape of the light.
                color (int): A Correlated Color Temperature (in Kelvin) which will determine the light's color. Is clamped to the range [1000, 40000].
            """
            self.surf = shape
            if not positionFromCenter: self.position = position
            else: self.position = (position[0] - shape.get_width() // 2, position[1] - shape.get_height() // 2)

    class Particle:
        def __init__(self, position, size):
            self.rect = pygame.Rect(position[0], position[1], size, size)
            self.size = size
            self.pos = position

        def update(self, Surface, scroll):

            return "null"

    class Fireparticle(Particle):
        def __init__(self, position, size, lifetime, speed, color = (220, 220, 4)):
            super().__init__(position, size)
            self.speed = speed
            self.lifetime = lifetime
            self.dying_speed = size / lifetime
            self.bsurf = Lighting.circle_surface(size, color)
            self.tsurf = Lighting.circle_surface(size*2, color)

        def update(self, Surface: pygame.Surface, scroll: List[int]):
            self.rect.y -= self.speed
            self.rect.x += random.randint(-1, 1)
            self.size -= self.dying_speed

            if self.size < 0: return None

            self.bsurf = pygame.transform.scale(self.bsurf, (round(self.size), round(self.size)))
            Surface.blit(self.bsurf, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

            self.tsurf = pygame.transform.scale(self.tsurf, (round(self.size * 2), round(self.size * 2)))

            return self.tsurf

    class Sparkparticle(Particle):
        def __init__(self, position, size, lifetime, speed, color = (200, 221, 5), direction = 1, slope = 1):
            super().__init__(position, size)
            self.speed = speed
            self.size = size
            self.lifetime =lifetime
            self.color = color
            self.direction = direction
            self.slope = slope
            self.dying_speed = size / lifetime
            self.relativeX = 0.0
            self.relativeY = 0.0
            self.bsurf = pygame.Surface((size/2, size*2))
            self.bsurf.fill(color)
            self.tsurf = Lighting.circle_surface(size*2, color)
            self.tsurf.fill(color)

        def update(self, Surface: pygame.Surface, scroll):
            self.relativeX += self.direction * self.speed
            self.relativeY = self.relativeX * self.slope
            self.rect.x = self.pos[0] + round(self.relativeX)
            self.rect.y = self.pos[1] + round(self.relativeY)
            self.size -= self.dying_speed
            if self.size < 0: return None

            self.bsurf = pygame.transform.scale(self.bsurf, (round(self.size/2), round(self.size*2)))
            Surface.blit(self.bsurf, (self.rect.centerx - self.bsurf.get_width()/2 - scroll[0], self.rect.centery - self.bsurf.get_height()/2 - scroll[1]))

            self.tsurf = pygame.transform.scale(self.tsurf, (self.bsurf.get_width()*2, self.bsurf.get_height()*2))
            return self.tsurf


class Bullet:
    GodMode = False

    def __init__(self, rect: pygame.Rect, direction: bool, speed: int, environment_obstacles: List[List[List[KDS.Build.Tile]]], damage: int, texture: Optional[pygame.Surface] = None, maxDistance = 2000, slope = 0): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
        """Bullet superclass written for KDS weapons"""
        self.rect = rect
        self.direction = direction
        self.direction_multiplier = KDS.Convert.ToMultiplier(direction)
        self.speed = speed
        self.texture = texture
        self.texture_size = self.texture.get_size() if self.texture != None else None
        self.maxDistance = maxDistance
        self.movedDistance = 0
        self.environment_obstacles = environment_obstacles
        self.damage = damage if not Bullet.GodMode else KDS.Math.MAXVALUE
        self.slope = slope
        self.slopeBuffer = float(self.rect.y)

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], targets: Sequence[Union[KDS.AI.HostileEnemy, KDS.Teachers.Teacher, KDS.NPC.NPC]], HitTargets: Dict[KDS.Build.Tile, HitTarget], Particles: List[Lighting.Particle], plr_rct: pygame.Rect, player_health: float, debugMode = False) -> Optional[Tuple[str, float]]:
        if self.texture != None:
            Surface.blit(self.texture, (self.rect.centerx - self.texture_size[0] // 2 - scroll[0], self.rect.centery - self.texture_size[1] // 2 - scroll[1]))
            #pygame.draw.rect(Surface,  (244, 200, 20), (self.rect.x-scroll[0], self.rect.y-scroll[1], 10, 10))
        if debugMode:
            pygame.draw.rect(Surface, KDS.Colors.Black, (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height))
            debugStartPos = (self.rect.centerx - (self.movedDistance * self.direction_multiplier), self.rect.centery - (self.slope * self.movedDistance))
            pygame.draw.line(Surface, KDS.Colors.White, (debugStartPos[0] - scroll[0], debugStartPos[1] - scroll[1]), (debugStartPos[0] + (self.maxDistance * self.direction_multiplier) - scroll[0], debugStartPos[1] - scroll[1] + (self.slope * self.maxDistance)))

        if self.speed == -1:
            for _ in range(round(self.maxDistance / 18)):

                self.rect.x += 18 * self.direction_multiplier
                self.movedDistance += 18

                self.slopeBuffer += self.slope
                self.rect.y = self.slopeBuffer

                collision_list = collision_test(self.rect, self.environment_obstacles)

                for hTarget in HitTargets.values():
                    if hTarget.rect.colliderect(self.rect):
                        hTarget.hitted = True
                        return "wall", player_health

                for target in targets:
                    if self.rect.colliderect(target.rect) and target.health > 0 and getattr(target, "enabled", None) != False:
                        target.health -= self.damage
                        Particles.append(Lighting.Fireparticle(target.rect.center, random.randint(2, 10), 20, -1, (180, 0, 0)))
                        return "wall", player_health

                if plr_rct.colliderect(self.rect):
                    player_health -= self.damage
                    return "wall", player_health
                if collision_list:
                    return "wall", player_health

            return "air", player_health
        else:
            self.rect.x += self.speed * self.direction_multiplier
            self.movedDistance += self.speed

            self.slopeBuffer += self.slope * self.speed
            self.rect.y = round(self.slopeBuffer)

            collision_list = collision_test(self.rect, self.environment_obstacles)

            for hTarget in HitTargets.values():
                if hTarget.rect.colliderect(self.rect):
                    hTarget.hitted = True
                    return "wall", player_health

            for target in targets:
                if target.rect.colliderect(self.rect) and target.health > 0 and getattr(target, "enabled", None) != False:
                    if isinstance(target, KDS.AI.HostileEnemy):
                        target.sleep = False
                    target.health -= self.damage
                    return "wall", player_health

            if plr_rct.colliderect(self.rect):
                player_health -= self.damage
                return "wall", player_health
            if collision_list:
                return "wall", player_health
            if self.movedDistance > self.maxDistance:
                return "air", player_health

class HitTarget:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.hitted = False

class BallisticProjectile:
    def __init__(self, rect: pygame.Rect, slope: float, force: float, direction: bool, gravitational_factor: float = 0.1, flight_time: int = 240, texture: pygame.Surface = None):
        self.rect = rect
        self.sl = slope
        self.force = force * KDS.Convert.ToMultiplier(direction)
        self.upforce = -int(force * slope)
        self.texture = texture
        self.flight_time = flight_time
        self.counter = 0
        self.direction = direction
        self.gravitational_factor = gravitational_factor

    def update(self, tiles, Surface, scroll):

        self.rect.x += round(self.force)

        c = collision_test(self.rect, tiles)
        collisions = {
            "right": False,
            "left": False,
            "bottom": False,
            "top": False
        }
        for c1 in c:
            if self.force > 0:
                self.rect.right = c1.rect.left
                collisions['left'] = True
            elif self.force < 0:
                self.rect.left = c1.rect.right
                collisions['right'] = True

        self.rect.y += self.upforce
        self.upforce += self.gravitational_factor
        if self.upforce > 6:
            self.upforce = 6
        c = collision_test(self.rect, tiles)

        for c1 in c:
            if self.upforce > 0:
                self.rect.bottom = c1.rect.top
                collisions['bottom'] = True
            elif self.upforce < 0:
                self.rect.top = c1.rect.bottom
                collisions['top'] = True


        if collisions["top"] or collisions["bottom"]:
            self.upforce *= 0.6
            self.force *= 0.7
            s = self.upforce
            self.upforce = -self.upforce
            if s:
                self.upforce *= 0.1

        if collisions["right"] or collisions["left"]:
            self.force *= 0.60
            self.force = -self.force

        self.counter += 1

        if self.texture:
            Surface.blit(self.texture, (self.rect.x-scroll[0],  self.rect.y-scroll[1]))
        return self.counter > self.flight_time

class Explosion:
    def __init__(self, animation: KDS.Animator.Animation, pos: Tuple[int, int]):
        self.animation = animation
        self.pos = pos

    def update(self, Surface: pygame.Surface, scroll: List[int]):
        Surface.blit(self.animation.update(), (self.pos[0] - scroll[0], self.pos[1] - scroll[1]))
        return self.animation.done, self.animation.tick


class Dark:
    enabled: bool = False
    darkness: Tuple[int, int, int] = (0, 0, 0)
    _defaultEnabled: bool = False
    _defaultDarknessStrength: int = -1

    @staticmethod
    def Set(enabled: bool, strength: int):
        Dark.enabled = enabled
        tmp = 255 - strength
        Dark.darkness = (tmp, tmp, tmp)

    @staticmethod
    def Reset():
        Dark.Set(Dark._defaultEnabled, Dark._defaultDarknessStrength)

    @staticmethod
    def Configure(enabled: bool, strength: int):
        Dark._defaultEnabled = enabled
        Dark._defaultDarknessStrength = strength
        Dark.Reset()

class Zone:
    StaffOnlyCollisions: int = 0

    def __init__(self, rect: pygame.Rect, properties: Dict[str, Union[str, int, float, bool]]) -> None:
        self.rect = rect
        self.playerInside: bool = False
        self.staffOnly = bool("staffOnly" in properties and properties["staffOnly"] == True)
        self.darkness: Optional[int] = None
        if "darkness" in properties:
            setDark = properties["darkness"]
            if isinstance(setDark, int):
                self.darkness = setDark

    def onEnter(self):
        if self.darkness != None:
            Dark.Set(True, self.darkness)
        if self.staffOnly:
            Zone.StaffOnlyCollisions += 1

    def onExit(self):
        if self.darkness != None:
            Dark.Reset()
        if self.staffOnly:
            Zone.StaffOnlyCollisions -= 1

    def update(self, playerRect: pygame.Rect):
        if self.rect.colliderect(playerRect):
            if not self.playerInside:
                self.playerInside = True
                self.onEnter()
        elif self.playerInside:
            self.playerInside = False
            self.onExit()