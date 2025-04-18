from __future__ import annotations

import random
from typing import Any, Dict, Final, Iterable, List, Literal, NamedTuple, Optional, Self, Sequence, Set, Tuple, Type, Union

import pygame
import pygame.mixer
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
import KDS.Debug

import dataclasses

from enum import IntEnum, auto, IntFlag

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
    Lighting.Shapes.cone_hard_up = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_hard_up.png").convert_alpha())
    Lighting.Shapes.cone_small_hard = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_small_hard.png").convert_alpha())
    Lighting.Shapes.cone_narrow = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/cone_narrow.png").convert_alpha())
    Lighting.Shapes.splatter = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/splatter.png").convert_alpha())
    Lighting.Shapes.fluorecent = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/fluorecent.png").convert_alpha())

    NEIN: Final[Literal[False]] = False

    Lighting.NoteParticle.textures = (
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_0.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_1.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_2.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_3.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_4.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_5.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_6.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_7.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_8.png"),
        Lighting.NoteParticle.NoteParticleTexture.load("Assets/Textures/Particles/note_9.png", weight=0.1, allow_rotate=NEIN),
    )

def _iter_nearby_tiles(rect: pygame.Rect, Tile_list: list[list[list[KDS.Build.Tile]]]) -> Iterable[KDS.Build.Tile]:
    X_OVERSCAN: Final[int] = 1 # Molok requires overscan of 1 due to its width (the tile origin is at the far right)
    Y_OVERSCAN: Final[int] = 1 # Door requires overscan of 1 due to its height (the tile origin is at the top)

    max_x: int = len(Tile_list[0]) - 1
    max_y: int = len(Tile_list) - 1

    top: int = KDS.Math.FloorToInt(rect.top / 34)
    left: int = KDS.Math.FloorToInt(rect.left / 34)
    bottom: int = KDS.Math.CeilToInt(rect.bottom / 34)
    right: int = KDS.Math.CeilToInt(rect.right / 34)

    # KDS.Math.Clamp is somehow faster than using the appropriate min-max -functions
    xmin: int = KDS.Math.Clamp(left   - X_OVERSCAN, 0, max_x)
    xmax: int = KDS.Math.Clamp(right  + X_OVERSCAN, 0, max_x)
    ymin: int = KDS.Math.Clamp(top    - Y_OVERSCAN, 0, max_y)
    ymax: int = KDS.Math.Clamp(bottom + Y_OVERSCAN, 0, max_y)

    # Yielding seems to be a tiny bit faster
    for row in Tile_list[ymin:(ymax + 1)]:
        for unit in row[xmin:(xmax + 1)]:
            for tile in unit:
                yield tile
    # return (tile for row in Tile_list[ymin:(ymax + 1)] for unit in row[xmin:(xmax + 1)] for tile in unit)

def collision_test_single(rect: pygame.Rect, tile: KDS.Build.Tile) -> bool:
    return rect.colliderect(tile.rect) and tile.checkCollision

def collision_test(rect: pygame.Rect, Tile_list: list[list[list[KDS.Build.Tile]]]) -> list[KDS.Build.Tile]:
    """Returns all collisions that were detected."""

    hit_list = []

    for tile in _iter_nearby_tiles(rect, Tile_list):
        if collision_test_single(rect, tile):
            hit_list.append(tile)

    return hit_list

def collision_test_fast(rect: pygame.Rect, Tile_list: list[list[list[KDS.Build.Tile]]]) -> KDS.Build.Tile | None:
    """Returns the first collision that was detected."""

    for tile in _iter_nearby_tiles(rect, Tile_list):
        if collision_test_single(rect, tile):
            return tile
    return None

# def _bresenham(x1: int, y1: int, x2: int, y2: int) -> Iterable[tuple[int, int]]:
#     m_new: int = 2 * (y2 - y1)
#     slope_error_new: int = m_new - (x2 - x1)

#     y: int = y1
#     for x in range(x1, x2 + 1):
#         yield (x, y)

#         slope_error_new = slope_error_new + m_new

#         if slope_error_new >= 0:
#             y = y + 1
#             slope_error_new = slope_error_new - 2 * (x2 - x1)

# TODO: Test this method... I was going to use this but decided against it so this method is currently a proof of concept
# def collision_test_line(start: tuple[int, int], end: tuple[int, int], Tile_list: list[list[list[KDS.Build.Tile]]], *, overscan: int = 3) -> KDS.Build.Tile | None:
#     """Returns the first collision that was detected."""

#     # Use Bresenham's algorithm to get a rudimentary idea of the tiles that were visited
#     # Then use overscan to include any other tiles nearby

#     for tile_pos in _bresenham(int(start[0] / 34), int(start[1] / 34), int(end[0] / 34), int(end[1] / 34)):
#         # multiply by 34 as I'm too lazy to make a tile size only function variant
#         for tile in _iter_nearby_tiles((tile_pos[0] * 34, tile_pos[1] * 34), Tile_list, overscan=overscan):
#             if len(tile.rect.clipline(start, end)) > 0: # line goes through rect
#                 return tile
#     return None

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
    def __init__(self, w_sounds: Optional[Dict[str, List[pygame.mixer.Sound]]] = None) -> None:
        self.walkSounds = w_sounds

    def move(self, rect: pygame.Rect, movement: Sequence[float], tiles: List[List[List]], *, playWalkSound: bool = False) -> Collisions:
        if len(movement) != 2:
            raise ValueError(f"Invalid movement size! Expected: 2, Got: {len(movement)}.")

        collisions = Collisions()

        rect.x += round(movement[0])
        if movement[0] > 0:
            right: int = rect.right
            for tile in collision_test(rect, tiles):
                # CollisionDirection is inverted, because it is relative to tile
                if CollisionDirection.Left in tile.collisionDirection:
                    right = min(right, tile.rect.left)
                    collisions.right = True
            rect.right = right
        elif movement[0] < 0:
            left: int = rect.left
            for tile in collision_test(rect, tiles):
                if CollisionDirection.Right in tile.collisionDirection:
                    left = max(left, tile.rect.right)
                    collisions.left = True
            rect.left = left


        rect.y += round(movement[1])
        # Collisions have to be checked for x and y separately or my testing of merging these two went horribly wrong
        if movement[1] > 0:
            bottom: int = rect.bottom
            for tile in collision_test(rect, tiles):
                # no idea what that second check is for, so I kept it when re-writing the move function...
                # it has probably something to do with jump force running out while clipping into a tile?
                if CollisionDirection.Top in tile.collisionDirection and tile.rect.bottom > rect.bottom:
                    bottom = min(bottom, tile.rect.top)
                    collisions.bottom = True
                    if movement[0] != 0 and self.walkSounds is not None and playWalkSound:
                        KDS.Audio.PlaySound(random.choice(self.walkSounds["default"]))
            rect.bottom = bottom
        elif movement[1] < 0:
            top: int = rect.top
            for tile in collision_test(rect, tiles):
                if CollisionDirection.Bottom in tile.collisionDirection:
                    top = max(top, tile.rect.bottom)
                    collisions.top = True
            rect.top = top

        return collisions

class Lighting:

    class Shapes:

        class LightShape:
            def __init__(self, texture: pygame.Surface) -> None:
                self.texture = texture
                self.rendered: Dict[int, Dict[Union[int, Tuple[float, float, float], str], pygame.Surface]] = {}

            def getDiameter(self, diameter: int) -> Dict[Union[int, Tuple[float, float, float], str], pygame.Surface]:
                if diameter not in self.rendered:
                    self.rendered[diameter] = { "default": pygame.transform.smoothscale(self.texture, (diameter, diameter)) }
                return self.rendered[diameter]

            def get(self, diameter: int, color: int):
                """Returns a light shape from memory

                Args:
                    radius (int): Light radius in pixels.
                    color (int): A Correlated Color Temperature (in Kelvin) that will determine the light's color.

                Returns:
                    Surface: The surface that contains the light texture
                """
                corRad = self.getDiameter(diameter)

                if color not in corRad:
                    tmp_tex: Any = corRad["default"].copy()
                    convCol = KDS.Convert.CorrelatedColorTemperatureToRGB(color)
                    tmp_tex.fill((convCol[0], convCol[1], convCol[2], 255), special_flags=BLEND_RGBA_MULT)
                    corRad[color] = tmp_tex
                return corRad[color]

            def getColor(self, diameter: int, hue: float, saturation: float, value: float):
                corRad = self.getDiameter(diameter)
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

        circle_softest: LightShape
        circle_soft: LightShape
        circle_softer: LightShape
        circle: LightShape
        circle_harder: LightShape
        circle_hard: LightShape
        circle_hardest: LightShape
        cone_hard: LightShape
        cone_hard_up: LightShape
        cone_small_hard: LightShape
        cone_narrow: LightShape
        splatter: LightShape
        fluorecent: LightShape

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
            if not positionFromCenter:
                self.position = position
            else:
                self.position = (position[0] - shape.get_width() // 2, position[1] - shape.get_height() // 2)

    class Particle:
        class UpdateAction(IntEnum):
            KillParticle = auto()
            NoLight = auto()
            Error = auto()

        def __init__(self, position, size):
            self.rect = pygame.Rect(position[0], position[1], size, size)
            self.size = size
            self.pos = position

        def update(self, Surface, scroll) -> Union[pygame.Surface, Lighting.Particle.UpdateAction]:
            """
            Returns a light surface if this particle emits light.
            Returns Lighting.Particle.UpdateAction.NoLight otherwise.

            Returns a Lighting.Particle.UpdateAction.KillParticle when particle is ready to be destroyed by Koponen Engine™
            """

            return Lighting.Particle.UpdateAction.Error

    class WaterParticle(Particle):
        def __init__(self, position: Tuple[int, int], size: int, speed: int, waitTicks: int, tileListInstance: List[List[List[KDS.Build.Tile]]], color: Tuple[float, float, float] = (0, 180, 0)):
            super().__init__(position, size)
            self.speed = speed
            self.mover = EntityMover()
            self.startY = self.rect.y
            self.wait = waitTicks
            self.tilesInstance = tileListInstance
            self.bsurf = Lighting.circle_surface(size, color)

        def update(self, Surface, scroll) -> Union[pygame.Surface, Lighting.Particle.UpdateAction]:
            self.wait = max(self.wait - 1, 0)
            if self.wait == 0:
                collisions = self.mover.move(self.rect, (0, self.speed), self.tilesInstance)
                if collisions.bottom:
                    return Lighting.Particle.UpdateAction.KillParticle
                if self.startY + 1000 < self.rect.y:
                    return Lighting.Particle.UpdateAction.KillParticle

            self.bsurf = pygame.transform.scale(self.bsurf, (round(self.size), round(self.size)))
            Surface.blit(self.bsurf, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

            return Lighting.Particle.UpdateAction.NoLight

    class Fireparticle(Particle):
        def __init__(self, position, size, lifetime, speed, color = (220, 220, 4)):
            super().__init__(position, size)
            self.speed = speed
            self.lifetime = lifetime
            self.dying_speed = size / lifetime
            self.bsurf = Lighting.circle_surface(size, color)
            self.tsurf = Lighting.circle_surface(size*2, color)

        def update(self, Surface: pygame.Surface, scroll: List[int]) -> Union[pygame.Surface, Lighting.Particle.UpdateAction]:
            self.rect.y -= self.speed
            self.rect.x += random.randint(-1, 1)
            self.size -= self.dying_speed

            if self.size < 0:
                return Lighting.Particle.UpdateAction.KillParticle

            self.bsurf = pygame.transform.scale(self.bsurf, (round(self.size), round(self.size)))
            Surface.blit(self.bsurf, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

            self.tsurf = pygame.transform.scale(self.tsurf, (round(self.size * 2), round(self.size * 2)))

            return self.tsurf

    class Sparkparticle(Particle):
        def __init__(self, position, size, lifetime, speed, color = (200, 221, 5), direction = 1, slope = 1):
            super().__init__(position, size)
            self.speed = speed
            self.size = size
            self.lifetime = lifetime
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

        def update(self, Surface: pygame.Surface, scroll) -> Union[pygame.Surface, Lighting.Particle.UpdateAction]:
            self.relativeX += self.direction * self.speed
            self.relativeY = self.relativeX * self.slope
            self.rect.x = self.pos[0] + round(self.relativeX)
            self.rect.y = self.pos[1] + round(self.relativeY)
            self.size -= self.dying_speed
            if self.size < 0:
                return Lighting.Particle.UpdateAction.KillParticle

            self.bsurf = pygame.transform.scale(self.bsurf, (round(self.size/2), round(self.size*2)))
            Surface.blit(self.bsurf, (self.rect.centerx - self.bsurf.get_width()/2 - scroll[0], self.rect.centery - self.bsurf.get_height()/2 - scroll[1]))

            self.tsurf = pygame.transform.scale(self.tsurf, (self.bsurf.get_width()*2, self.bsurf.get_height()*2))
            return self.tsurf

    class NoteParticle(Particle):
        class NoteParticleTexture(NamedTuple):
            texture: pygame.Surface
            weight: float = 1.0
            allow_rotate: bool = True

            @classmethod
            def load(cls, path: str, weight: float = 1.0, allow_rotate: bool = True) -> Self:
                tex: pygame.Surface = pygame.image.load(path).convert()
                tex.set_colorkey(KDS.Colors.White)

                # This was in the original code but it did nothing as it was accidentally assigned to an unreferenced value
                # tex = pygame.transform.scale(tex, (tex.get_width() / 4, tex.get_height() / 4))

                return cls(tex, weight=weight, allow_rotate=allow_rotate)

        SIZE: int = 20
        HALF_SIZE: int = round(SIZE / 2)

        textures: tuple[NoteParticleTexture, ...]

        def __init__(self, position: tuple[int, int], angleDeg: float):
            """angleDeg is ignored on particles where rotation is forbidden."""

            super().__init__(position, Lighting.NoteParticle.SIZE)
            self.lifetime = 40
            self.life = 0
            self.speed = 0.1
            self.dying_speed = 5
            self.opacity = 255

            self.float_y: float = position[1]

            tex = random.choices(Lighting.NoteParticle.textures, weights=[n.weight for n in Lighting.NoteParticle.textures], k=1)[0]
            if tex.allow_rotate:
                self.texture = pygame.transform.rotate(tex.texture, angle=angleDeg)
            else:
                self.texture = tex.texture

        def update(self, Surface: pygame.Surface, scroll: List[int]) -> pygame.Surface | KDS.World.Lighting.Particle.UpdateAction:
            self.float_y -= self.speed
            self.rect.y = KDS.Math.FloorToInt(self.float_y)

            self.life += 5
            if self.life >= self.lifetime:
                self.life = self.lifetime
                self.opacity -= self.dying_speed

            if self.opacity <= 0:
                return Lighting.Particle.UpdateAction.KillParticle

            self.texture.set_alpha(self.opacity)

            Surface.blit(self.texture, (self.rect.centerx - (self.texture.get_width() / 2) - scroll[0], self.rect.centery - (self.texture.get_height() / 2) - scroll[1]))

            return Lighting.Particle.UpdateAction.NoLight

class Bullet:
    GodMode = False

    RESOLUTION: Final[int] = 16 # The maximum amount of pixels to move between collision checks => lower is better.
    # the smallest entity (by width) I could find was KuuMa which was 17 pixels width, so I set the resolution at 16

    def __init__(self, player_rect: pygame.Rect | None, rect: pygame.Rect, direction: bool, speed: int, environment_obstacles: List[List[List[KDS.Build.Tile]]], damage: int, texture: Optional[pygame.Surface] = None, maxDistance: int = 2000, slope: float = 0): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
        """Bullet superclass written for KDS weapons."""
        self.player_rect: pygame.Rect | None = player_rect
        self.player_rect_handled: bool = False

        self.start_center: tuple[int, int] = rect.center
        self.rect = rect

        # tile_res is a tile specific resolution that adjusts itself based on the width of nearby tiles
        self.tile_res: int = 1  # Start with 1 and initialise value properly after first collision check
                                # This is done so that the bullet doesn't go through any doors if the barrel is close enough.

        self.direction = direction
        self.direction_multiplier = KDS.Convert.ToMultiplier(direction)

        self.speed = speed
        self.slope = slope
        self.slopeBuffer = float(self.rect.y)
        self.movedDistance = 0
        self.maxDistance = maxDistance

        self.damage = damage if not Bullet.GodMode else KDS.Math.MAXVALUE
        self.texture = texture
        self.texture_size = self.texture.get_size() if self.texture != None else None

        self.environment_obstacles = environment_obstacles

    def _tile_collision_check(self, target_mv: int) -> bool:
        current_mv: int = 0

        while current_mv < target_mv:
            mv: int = min(self.tile_res, target_mv - current_mv)

            # Increment moved amount
            current_mv += mv

            # Move bullet
            self.rect.x += mv * self.direction_multiplier
            self.movedDistance += mv

            self.slopeBuffer += self.slope * mv
            self.rect.y = self.slopeBuffer

            # Check tile collisions and adjust tile resolution
            self.tile_res = Bullet.RESOLUTION
            for tile in _iter_nearby_tiles(self.rect, self.environment_obstacles):
                # If tile rect is smaller and we might jump over it during the next collision update
                if tile.rect.width < self.tile_res and abs(tile.rect.x - self.rect.x) < self.tile_res:
                    self.tile_res = tile.rect.width
                if collision_test_single(self.rect, tile):
                    return True

        return False

    def _collision_check(self, *, targets: Sequence[Union[KDS.AI.HostileEnemy, KDS.Teachers.Teacher, KDS.NPC.NPC]], HitTargets: Dict[KDS.Build.Tile, HitTarget], Particles: List[Lighting.Particle], plr_rct: pygame.Rect, player_health: float) -> Optional[Tuple[str, float]]:
        target_mv: Final[int] = self.speed if self.speed > -1 else self.maxDistance
        current_mv: int = 0

        while current_mv < target_mv:
            mv: int = min(Bullet.RESOLUTION, target_mv - current_mv)
            # move amount

            if self._tile_collision_check(mv):
                return "wall", player_health

            # assert(tile_moved_amount == mv) # Removed assert to squeeze out every ounce of performance
            current_mv += mv

            for hTarget in HitTargets.values():
                if hTarget.rect.colliderect(self.rect):
                    hTarget.hitted = True
                    return "wall", player_health

            for target in targets: # We really are in need of a chunk system so that all entities aren't checked each bullet physics frame
                if self.rect.colliderect(target.rect) and target.health > 0 and target.enabled:
                    target.health -= self.damage
                    Particles.append(Lighting.Fireparticle(target.rect.center, random.randint(2, 10), 20, -1, (180, 0, 0)))
                    return "wall", player_health

            if plr_rct.colliderect(self.rect):
                player_health -= self.damage
                return "wall", player_health

        if self.movedDistance >= self.maxDistance:
            return "air", player_health

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], targets: Sequence[Union[KDS.AI.HostileEnemy, KDS.Teachers.Teacher, KDS.NPC.NPC]], HitTargets: Dict[KDS.Build.Tile, HitTarget], Particles: List[Lighting.Particle], plr_rct: pygame.Rect, player_health: float) -> Optional[Tuple[str, float]]:
        # Early return so that the bullet has no chance of dealing damage (or rendering) if the gun is embedded into a wall
        if not self.player_rect_handled:
            if self.player_rect is not None:
                test_leftright: tuple[int, int]
                if self.rect.centerx > self.player_rect.centerx:
                    test_leftright = (self.player_rect.centerx, self.rect.right)
                else:
                    test_leftright = (self.rect.left, self.player_rect.centerx)

                pr_test = pygame.Rect(test_leftright[0], self.rect.top, test_leftright[1] - test_leftright[0], self.rect.height)
                pr_had_col: bool = collision_test_fast(pr_test, self.environment_obstacles) is not None # increase overscan if necessary
                if KDS.Debug.Enabled:
                    pygame.draw.rect(Surface, KDS.Colors.AviatorRed if pr_had_col else KDS.Colors.Gray, (pr_test.x - scroll[0], pr_test.y - scroll[1], *pr_test.size))
                if pr_had_col:
                    return "wall", player_health

            self.player_rect_handled = True

        x_before_move: int = self.rect.x
        collision = self._collision_check(targets=targets, HitTargets=HitTargets, Particles=Particles, plr_rct=plr_rct, player_health=player_health)

        if KDS.Debug.Enabled:
            pygame.draw.line(
                Surface,
                KDS.Colors.White,
                (self.start_center[0] - scroll[0], self.start_center[1] - scroll[1]),
                (self.start_center[0] + (self.maxDistance * self.direction_multiplier) - scroll[0], self.start_center[1] - scroll[1] + (self.slope * self.maxDistance))
            )
            pygame.draw.line(
                Surface,
                KDS.Colors.EmeraldGreen if collision is None or collision[0] == "air" else KDS.Colors.SunYellow,
                (self.start_center[0] - scroll[0], self.start_center[1] - scroll[1]),
                (self.rect.centerx - scroll[0], self.rect.centery - scroll[1])
            )

        # fast weapons like plasmarifle look like two floating bullets layered on top of each other
        # this attempts to fix that issue.
        # render if collision didn't happen, bullet hasn't travelled to the first renderpoint or bullets are sufficiently apart from each other
        if collision is None or abs(self.start_center[0] - self.rect.centerx) < self.speed or abs(x_before_move - self.rect.x) > (self.speed / 2):
            if self.texture != None:
                assert self.texture_size != None
                Surface.blit(self.texture, (self.rect.centerx - self.texture_size[0] // 2 - scroll[0], self.rect.centery - self.texture_size[1] // 2 - scroll[1]))
                #pygame.draw.rect(Surface,  (244, 200, 20), (self.rect.x-scroll[0], self.rect.y-scroll[1], 10, 10))

        return collision



class HitTarget:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.hitted = False

class BallisticProjectile:
    def __init__(self, rect: pygame.Rect, slope: float, force: float, direction: bool, gravitational_factor: float = 0.1, flight_time: int = 240, texture: Optional[pygame.Surface] = None):
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
    _SPEED: Final[int] = 5

    _current_enabled: bool
    _target_enabled: bool
    _current_strength: int
    _target_strength: int

    _defaultEnabled: bool
    _defaultDarknessStrength: int

    class Disco:
        enabled: bool = False
        colors: Tuple[Tuple[int, int, int], ...] = ((255, 192, 192), (192, 255, 192), (192, 192, 255), (255, 224, 192), (192, 255, 255))
        colorAnimation: KDS.Animator.Color = KDS.Animator.Color(KDS.Colors.Black, KDS.Colors.Black, 30, KDS.Animator.AnimationType.EaseInOutQuad)
        colorAnimation.tick = colorAnimation.ticks
        colorIndex: int = 0
        circleX: int = 0

    @staticmethod
    def GetEnabled() -> bool:
        """
        Whether any lights should be rendered.

        NOTE: Even though this method might return False, it does not guarantee that the darkness strength will be 0.
        """

        # If we are targeting enabled, we will wait until the animation is finished
        # if we are targeting disabled, disable lights immediately
        #
        # this is done like this because on small darkness values, lights were rendered as black
        # which I couldn't seem to fix using any other methods
        # so now I just wait until the animation is finished before rendering any lights
        # if darkness is always enabled during the animation, lights should keep rendering
        if Dark._target_enabled:
            return Dark._current_enabled
        else:
            return Dark._target_enabled

    @staticmethod
    def Set(enabled: bool, strength: int, *, instant: bool):
        assert(strength >= 0 and strength <= 255)

        Dark._target_enabled = enabled
        Dark._target_strength = strength
        if instant or strength == Dark._current_strength:
            Dark._current_enabled = Dark._target_enabled
            Dark._current_strength = Dark._target_strength

    @staticmethod
    def Update() -> tuple[int, int, int] | None:
        dist: int = abs(Dark._current_strength - Dark._target_strength)
        sign: int = -1 if Dark._current_strength > Dark._target_strength else 1

        if dist <= Dark._SPEED:
            Dark._current_strength += dist * sign

            # 0 <= dist <= Dark._Speed so...
            # end was reached, so update currently enabled
            Dark._current_enabled = Dark._target_enabled
        else:
            Dark._current_strength += Dark._SPEED * sign

        if Dark._current_enabled or Dark._target_enabled:
            assert(Dark._current_strength >= 0 and Dark._current_strength <= 255)
            darkVal: int = 255 - Dark._current_strength
            return (darkVal, darkVal, darkVal)
        else:
            return None

    @staticmethod
    def Reset(*, instant: bool):
        Dark.Set(Dark._defaultEnabled, Dark._defaultDarknessStrength, instant=instant)
        Dark.Disco.enabled = False

    @staticmethod
    def Configure(enabled: bool, strength: int):
        Dark._defaultEnabled = enabled
        Dark._defaultDarknessStrength = strength
        Dark.Reset(instant=True)

class Zone:
    StaffOnlyCollisions: int = 0
    CollidingZones: list[Zone] = []

    def __init__(self, rect: pygame.Rect, properties: Dict[str, Union[str, int, float, bool]]) -> None:
        self.rect = rect
        self.playerInside: bool = False

        self.staffOnly: Final[bool] = bool("staffOnly" in properties and properties["staffOnly"] == True)
        self.levelEnder: Final[bool] = bool("levelEnder" in properties and properties["levelEnder"] == True)
        self.disco: Final[bool] = bool("disco" in properties and properties["disco"] == True)
        self.darknessIsInstant: Final[bool] = bool("darknessIsInstant" in properties and properties["darknessIsInstant"] == True)

        setId: str | None = None
        if "customId" in properties:
            id = properties["customId"]
            if isinstance(id, str):
                setId = id
            else:
                KDS.Logging.AutoError(f"The zone custom id property type is invalid: '{type(id).__name__}'")
        self.customId: Final[str | None] = setId

        setDark: int | None = None
        if "darkness" in properties:
            dark = properties["darkness"]
            if isinstance(dark, int):
                setDark = dark
            else:
                KDS.Logging.AutoError(f"The zone darkness property type is invalid: '{type(dark).__name__}'")
        self.darkness: Final[int | None] = setDark

    @staticmethod
    def _getDarknessZoneFromCollisions() -> Zone | None:
        for zone in reversed(Zone.CollidingZones):
            if zone.darkness is not None:
                return zone

    @staticmethod
    def _addDarkness(zone: Zone) -> None:
        assert zone.darkness is not None
        assert zone is Zone.CollidingZones[-1]
        Dark.Set(True, zone.darkness, instant=zone.darknessIsInstant)

    @staticmethod
    def _removeDarkness(zone: Zone) -> None:
        darkness_zone: Zone | None = None
        for z in reversed(Zone.CollidingZones):
            if z.darkness is not None:
                darkness_zone = z
                break

        if darkness_zone is not None:
            assert darkness_zone.darkness is not None
            assert darkness_zone is not zone
            # use darknessIsInstant of the removed zone, not the last one in the list
            Dark.Set(True, darkness_zone.darkness, instant=zone.darknessIsInstant)
        else:
            Dark.Reset(instant=zone.darknessIsInstant)

    @staticmethod
    def _addCollision(zone: Zone):
        if zone in Zone.CollidingZones:
            KDS.Logging.AutoError("Zone collision already registered. Add request ignored.")
            return

        Zone.CollidingZones.append(zone)
        if zone.darkness is not None:
            Zone._addDarkness(zone)
        if zone.staffOnly:
            Zone.StaffOnlyCollisions += 1
        if zone.levelEnder:
            KDS.Missions.Listeners.LevelEnder.Trigger()
        if zone.disco:
            Dark.Disco.enabled = True

    @staticmethod
    def _removeCollision(zone: Zone):
        if zone not in Zone.CollidingZones:
            KDS.Logging.AutoError("Zone collision not registered. Remove request ignored.")
            return

        Zone.CollidingZones.remove(zone)
        if zone.darkness is not None:
            Zone._removeDarkness(zone)
        if zone.staffOnly:
            Zone.StaffOnlyCollisions -= 1
        if zone.disco:
            Dark.Disco.enabled = False

    @staticmethod
    def reset() -> None:
        Zone.StaffOnlyCollisions = 0
        Zone.CollidingZones.clear()

    def update(self, playerRect: pygame.Rect):
        if self.rect.colliderect(playerRect):
            if not self.playerInside:
                self.playerInside = True
                Zone._addCollision(self)
        elif self.playerInside:
            self.playerInside = False
            Zone._removeCollision(self)
