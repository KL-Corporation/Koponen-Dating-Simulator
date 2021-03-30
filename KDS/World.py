import math
import random
import sys
from typing import Dict, List, Optional, Sequence, Tuple, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math

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

def collision_test(rect, Tile_list):
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

class Collisions:
    def __init__(self) -> None:
        self.top = False
        self.bottom = False
        self.right = False
        self.left = False

def move_entity(rect: pygame.Rect, movement: Sequence[float], tiles, w_sounds: dict = {"default" : []}, playWalkSound = False):
    collisions = Collisions()

    rect.x += int(movement[0])
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.rect.left
            collisions.right = True
        elif movement[0] < 0:
            rect.left = tile.rect.right
            collisions.left = True

    rect.y += int(movement[1])
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.rect.top
            collisions.bottom = True
            if movement[0] and playWalkSound:
                KDS.Audio.PlaySound(random.choice(w_sounds["default"]))
        elif movement[1] < 0:
            rect.top = tile.rect.bottom
            collisions.top = True
    return rect, collisions

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
                    tmp_tex: pygame.Surface = corRad["default"].copy()
                    convCol = KDS.Convert.CorrelatedColorTemperatureToRGB(color)
                    tmp_tex.fill((convCol[0], convCol[1], convCol[2], 255), special_flags=BLEND_RGBA_MULT)
                    corRad[color] = tmp_tex
                return corRad[color]

            def getColor(self, radius: int, hue: float, saturation: float, value: float):
                corRad = self.getRadius(radius)
                color = (hue, saturation, value)

                if color not in corRad:
                    tmp_tex: pygame.Surface = corRad["default"].copy()
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

    def __init__(self, rect, direction: bool, speed: int, environment_obstacles, damage, texture: Optional[pygame.Surface] = None, maxDistance = 2000, slope = 0): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
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

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], targets, HitTargets, Particles, plr_rct, plr_htlt, debugMode = False):
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

                for hTarget in HitTargets:
                    if HitTargets[hTarget].rect.colliderect(self.rect):
                        HitTargets[hTarget].hitted = True
                        return "wall", targets, plr_htlt, HitTargets, Particles

                for target in targets:
                    if self.rect.colliderect(target.rect) and target.health > 0 and getattr(target, "enabled", None) != False:
                        target.dmg(self.damage)
                        target.sleep = False
                        Particles.append(Lighting.Fireparticle(target.rect.center, random.randint(2, 10), 20, -1, (180, 0, 0)))
                        return "wall", targets, plr_htlt, HitTargets, Particles

                if plr_rct.colliderect(self.rect):
                    plr_htlt -= self.damage
                    if plr_htlt < 0:
                        plr_htlt = 0
                    return "wall", targets, plr_htlt, HitTargets, Particles
                if collision_list:
                    return "wall", targets, plr_htlt, HitTargets, Particles

            return "air", targets, plr_htlt, HitTargets, Particles
        else:
            self.rect.x += self.speed * self.direction_multiplier
            self.movedDistance += self.speed

            self.slopeBuffer += self.slope * self.speed
            self.rect.y = round(self.slopeBuffer)

            collision_list = collision_test(self.rect, self.environment_obstacles)

            for hTarget in HitTargets:
                if HitTargets[hTarget].rect.colliderect(self.rect):
                    HitTargets[hTarget].hitted = True
                    return "wall", targets, plr_htlt, HitTargets, Particles

            for target in targets:
                if target.rect.colliderect(self.rect) and target.health > 0 and getattr(target, "enabled", None) != False:
                    target.sleep = False
                    target.dmg(self.damage)
                    return "wall", targets, plr_htlt, HitTargets, Particles

            if plr_rct.colliderect(self.rect):
                plr_htlt -= self.damage
                if plr_htlt < 0:
                    plr_htlt = 0

                return "wall", targets, plr_htlt, HitTargets, Particles
            if collision_list:
                return "wall", targets, plr_htlt, HitTargets, Particles
            if self.movedDistance > self.maxDistance:
                return "air", targets, plr_htlt, HitTargets, Particles

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

class itemTools:
    class rk62:
        def __init__(self, arg = 0):
            self.counter: int = arg
    class plasmarifle:
        def __init__(self, arg = 0):
            self.counter: int = arg
    class pistol:
        def __init__(self, arg = 0):
            self.counter: int = arg
    class shotgun:
        def __init__(self, arg = 0):
            self.counter: int = arg
    class ppsh41:
        def __init__(self, arg = 0):
            self.counter: int = arg

    class awm:
        def __init__(self, arg = 0):
            self.counter: int = arg

    class Grenade:
        def __init__(self, slope, force):
            self.Slope = slope
            self.force = force

    class Knife:
        def __init__(self, arg = 0):
            self.counter: int = arg

class Explosion:
    def __init__(self, animation: KDS.Animator.Animation, pos: Tuple[int, int]):
        self.animation = animation
        self.pos = pos

    def update(self, Surface: pygame.Surface, scroll: List[int]):
        Surface.blit(self.animation.update(), (self.pos[0] - scroll[0], self.pos[1] - scroll[1]))
        return self.animation.done, self.animation.tick

rk62_C = itemTools.rk62(100)
plasmarifle_C = itemTools.plasmarifle(100)
pistol_C = itemTools.pistol(100)
shotgun_C = itemTools.shotgun(100)
ppsh41_C = itemTools.ppsh41(100)
awm_C = itemTools.awm(100)

knife_C = itemTools.Knife(100)
Grenade_O = itemTools.Grenade(0.7, 9)
