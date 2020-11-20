from typing import Dict, List, Sequence, Tuple
import pygame, numpy, math, random
from pygame.locals import *
import KDS.Convert, KDS.Math, KDS.Animator, KDS.Logging, KDS.Audio

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
    Lighting.Shapes.splatter = Lighting.Shapes.LightShape(pygame.image.load("Assets/Textures/Lighting/splatter.png").convert_alpha())

def collision_test(rect, Tile_list):
    hit_list = []
    x = int((rect.x/34) - 3)
    y = int((rect.y/34) - 3)
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    max_x = len(Tile_list[0]) - 1
    max_y = len(Tile_list) - 1
    end_x = x + 6
    end_y = y + 6

    if end_x > max_x:
        end_x = max_x

    if end_y > max_y:
        end_y = max_y

    for row in Tile_list[y:end_y]:
        for tile in row[x:end_x]:
            if rect.colliderect(tile.rect) and not tile.air and tile.checkCollision:
                hit_list.append(tile)
    return hit_list

class Collisions:
    def __init__(self) -> None:
        self.top = False
        self.bottom = False
        self.right = False
        self.left = False

def move_entity(rect: pygame.Rect, movement: Sequence[int], tiles, w_sounds: dict = {"default" : []}, playWalkSound = False):
    collision_types = Collisions()
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.rect.left
            collision_types.right = True
        elif movement[0] < 0:
            rect.left = tile.rect.right
            collision_types.left = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.rect.top
            collision_types.bottom = True
            if movement[0] and playWalkSound:
                KDS.Audio.playSound(random.choice(w_sounds["default"]))
        elif movement[1] < 0:
            rect.top = tile.rect.bottom
            collision_types.top = True
    return rect, collision_types

class Lighting:

    class Shapes:
        class LightShape:
            def __init__(self, texture: pygame.Surface) -> None:
                self.texture = texture
                self.rendered: Dict[dict] = {}
                
            def get(self, radius: int, color: int, conv_a = False):
                """Returns a light shape from memory

                Args:
                    radius (int): Light radius in pixels.
                    color (int): A Correlated Color Temperature (in Kelvin) that will determine the light's color.

                Returns:
                    Surface: The surface that contains the light texture
                """
                if radius not in self.rendered: self.rendered[radius] = { "default": pygame.transform.scale(self.texture, (radius, radius)).convert_alpha() }

                corRad = self.rendered[radius]
                if color not in corRad:
                    tmp_tex: pygame.Surface = corRad["default"].copy().convert_alpha()
                    convCol = KDS.Convert.CorrelatedColorTemperatureToRGB(color)
                    tmp_tex.fill((convCol[0], convCol[1], convCol[2], 255), special_flags=BLEND_RGBA_MULT)
                    corRad[color] = tmp_tex
                return corRad[color]
        
        circle_softest: LightShape = None
        circle_soft: LightShape = None
        circle_softer: LightShape = None
        circle: LightShape = None
        circle_harder: LightShape = None
        circle_hard: LightShape = None
        circle_hardest: LightShape = None
        cone_hard: LightShape = None
        cone_small_hard: LightShape = None
        splatter: LightShape = None

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
            else: self.position = (position[0] - shape.get_width() / 2, position[1] - shape.get_height() / 2)

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
        
        def update(particle, Surface: pygame.Surface, scroll: List[int]):
            particle.rect.y -= particle.speed
            particle.rect.x += random.randint(-1, 1)
            particle.size -= particle.dying_speed

            if particle.size < 0: return None
            
            particle.bsurf = pygame.transform.scale(particle.bsurf, (round(particle.size), round(particle.size)))
            Surface.blit(particle.bsurf, (particle.rect.x - scroll[0], particle.rect.y - scroll[1]))

            particle.tsurf = pygame.transform.scale(particle.tsurf, (round(particle.size * 2), round(particle.size * 2)))

            return particle.tsurf

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
    def __init__(self, rect, direction: bool, speed:int, environment_obstacles, damage, texture = None, maxDistance = 2000, slope =0): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
        """Bullet superclass written for KDS weapons"""
        self.rect = rect
        self.direction = direction
        self.speed = speed
        self.texture = texture
        self.maxDistance = maxDistance
        self.movedDistance = 0
        self.environment_obstacles = environment_obstacles
        self.damage = damage
        self.slope = slope
        self.slopeBuffer = float(self.rect.y)

    def update(self,Surface:pygame.Surface, scroll: List[int], targets, HitTargets, Particles, plr_rct, plr_htlt, debugMode = False):
        if self.texture:
            Surface.blit(self.texture, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
            #pygame.draw.rect(Surface,  (244, 200, 20), (self.rect.x-scroll[0], self.rect.y-scroll[1], 10, 10))
        if self.speed == -1:
            for _ in range(int(self.maxDistance/18)):
                if debugMode:
                    pygame.draw.rect(Surface, (255, 255, 255), (self.rect.x-scroll[0], self.rect.y-scroll[1], self.rect.width, self.rect.height))
                if self.direction:
                    self.rect.x -= 18                  
                else:
                    self.rect.x += 18

                self.slopeBuffer += self.slope
                self.rect.y = self.slopeBuffer

                collision_list = collision_test(self.rect, self.environment_obstacles)

                for hTarget in HitTargets:
                    if HitTargets[hTarget].rect.colliderect(self.rect):
                        HitTargets[hTarget].hitted = True
                        return "wall", targets, plr_htlt, HitTargets, Particles

                for target in targets:
                    if self.rect.colliderect(target.rect) and target.health > 0:
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
            if self.direction:
                self.rect.x -= self.speed
                self.movedDistance += self.speed             
            else:
                self.rect.x += self.speed
                self.movedDistance += self.speed
            
            self.slopeBuffer += self.slope*self.speed
            self.rect.y = self.slopeBuffer

            collision_list = collision_test(self.rect, self.environment_obstacles)

            for hTarget in HitTargets:
                if HitTargets[hTarget].rect.colliderect(self.rect):
                    HitTargets[hTarget].hitted = True
                    return "wall", targets, plr_htlt, HitTargets, Particles

            for target in targets:
                if target.rect.colliderect(self.rect) and target.health > 0:
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
    def __init__(self, position, width, height, slope, force, direction, gravitational_factor = 0.1, flight_time = 240, texture=None):
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.sl = slope
        self.force = force*KDS.Convert.ToMultiplier(direction)
        self.upforce = -int(force*slope)
        self.texture = texture
        self.flight_time = flight_time
        self.counter = 0
        self.direction = direction
        self.gravitational_factor = gravitational_factor

    def update(self, tiles, Surface, scroll):

        self.rect.x += round(self.force)

        c = collision_test(self.rect, tiles)
        c_types = {
            "right":False,
            "left":False,
            "bottom":False,
            "top":False
        }
        for c1 in c:
            if self.force > 0:
                self.rect.right = c1.rect.left
                c_types['left'] = True
            elif self.force < 0:
                self.rect.left = c1.rect.right
                c_types['right'] = True

        self.rect.y += self.upforce
        self.upforce += self.gravitational_factor
        if self.upforce > 6:
            self.upforce = 6
        c = collision_test(self.rect, tiles)

        for c1 in c:
            if self.upforce > 0:
                self.rect.bottom = c1.rect.top
                c_types['bottom'] = True
            elif self.upforce < 0:
                self.rect.top = c1.bottom
                c_types['top'] = True


        #print(c_types)
        if c_types["top"] or c_types["bottom"]:
            self.upforce *= 0.6
            self.force *= 0.7
            s = self.upforce
            self.upforce = -self.upforce
            if s:
                self.upforce *= 0.1
                
        if c_types["right"] or c_types["left"]:
            self.force *= 0.60
            self.force = -self.force

        self.counter += 1

        if self.texture:
            Surface.blit(self.texture, (self.rect.x-scroll[0],  self.rect.y-scroll[1]))
        return self.counter > self.flight_time
    
    def toString(self):
        """Converts all textures to strings
        """
        if isinstance(self.texture, pygame.Surface):
            self.texture = (pygame.image.tostring(self.texture, "RGBA"), self.texture.get_size(), "RGBA")
        
    def fromString(self):
        """Converts all strings back to textures
        """
        if isinstance(self.texture, pygame.Surface):
            self.texture = pygame.image.fromstring(self.texture[0], self.texture[1], self.texture[2])

class itemTools:
    class rk62:
        def __init__(self, arg = 0):
            self.counter = arg
    class plasmarifle:
        def __init__(self, arg = 0):
            self.counter = arg
    class pistol:
        def __init__(self, arg = 0):
            self.counter = arg
    class shotgun:
        def __init__(self, arg = 0):
            self.counter = arg
    class ppsh41:
        def __init__(self, arg = 0):
            self.counter = arg

    class awm:
        def __init__(self, arg = 0):
            self.counter = arg

    class Grenade:
        def __init__(self, slope, force):
            self.Slope = slope
            self.force = force

    class Knife:
        def __init__(self, arg = 0):
            self.counter = arg

class Explosion:
    def __init__(self, animation: KDS.Animator.Animation, pos: Tuple[int, int]):
        self.animation = animation
        self.xpos = pos[0]
        self.ypos = pos[1]

    def update(self, Surface: pygame.Surface, scroll: List[int]):
        txtre = self.animation.update()
        Surface.blit(txtre, (self.xpos-scroll[0],self.ypos-scroll[1]))
        return self.animation.done, self.animation.tick
    
    def toString(self):
        """Converts all textures to strings
        """
        self.animation.toString()
        
    def fromString(self):
        """Converts all strings back to textures
        """
        self.animation.fromString()
    
rk62_C = itemTools.rk62(100)
plasmarifle_C = itemTools.plasmarifle(100)
pistol_C = itemTools.pistol(100)
shotgun_C = itemTools.shotgun(100)
ppsh41_C = itemTools.ppsh41(100)
awm_C = itemTools.awm(100)

knife_C = itemTools.Knife(100)
Grenade_O = itemTools.Grenade(0.7, 9)