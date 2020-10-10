import pygame, numpy, math, random
import KDS.Convert, KDS.Math, KDS.Animator

pygame.init()

def collision_test(rect: pygame.Rect, Tile_list):
    hit_list = []
    x = int((rect.x/34)-2)
    y = int((rect.y/34)-2)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    max_x = len(Tile_list[0])-1
    max_y = len(Tile_list)-1
    end_x = x+4
    end_y = y+4

    if end_x > max_x:
        end_x = max_x

    if end_y > max_y:
        end_y = max_y

    for row in Tile_list[y:end_y]:
        for tile in row[x:end_x]:
            if rect.colliderect(tile.rect) and not tile.air and tile.checkCollision:
                hit_list.append(tile.rect)
    return hit_list

class Bullet:
    def __init__(self, rect, direction: int, speed:int, environment_obstacles, damage, texture = None, maxDistance = 2000, slope =0): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
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

    def update(self,Surface:pygame.Surface, scroll: list, targets, plr_rct, plr_htlt, debugMode = False):
        if self.texture:
            Surface.blit(self.texture, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
            #pygame.draw.rect(Surface,  (244, 200, 20), (self.rect.x-scroll[0], self.rect.y-scroll[1], 10, 10))
        if self.speed == -1:
            for _ in range(int(self.maxDistance/18)):
                if debugMode:
                    pygame.draw.rect(Surface, (255,255,255), (self.rect.x-scroll[0], self.rect.y-scroll[1], self.rect.width, self.rect.height))
                if self.direction:
                    self.rect.x -= 18                  
                else:
                    self.rect.x += 18

                self.slopeBuffer += self.slope
                self.rect.y = self.slopeBuffer

                collision_list = collision_test(self.rect, self.environment_obstacles)
                for target in targets:
                    if self.rect.colliderect(target.rect) and target.health > 0:
                        target.dmg(self.damage)
                        target.sleep = False
                        return "wall", targets, plr_htlt
                
                if plr_rct.colliderect(self.rect):
                    plr_htlt -= self.damage
                    if plr_htlt < 0:
                        plr_htlt = 0
                    return "wall", targets, plr_htlt
                if collision_list:
                    return "wall", targets, plr_htlt

            return "air", targets, plr_htlt
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
            for target in targets:
                if target.rect.colliderect(self.rect) and target.health > 0:
                    target.sleep = False
                    target.dmg(self.damage)
                    return "wall", targets, plr_htlt
            if plr_rct.colliderect(self.rect):
                plr_htlt -= self.damage
                if plr_htlt < 0:
                    plr_htlt = 0
                return "wall", targets, plr_htlt
            if collision_list:
                return "wall", targets, plr_htlt
            if self.movedDistance > self.maxDistance:
                return "air", targets, plr_htlt

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
                self.rect.right = c1.left
                c_types['left'] = True
            elif self.force < 0:
                self.rect.left = c1.right
                c_types['right'] = True

        self.rect.y += self.upforce
        self.upforce += self.gravitational_factor
        if self.upforce > 6:
            self.upforce = 6
        c = collision_test(self.rect, tiles)

        for c1 in c:
            if self.upforce > 0:
                self.rect.bottom = c1.top
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
        

class Lighting:

    @staticmethod
    def circle_surface(radius, color):
        surf = pygame.Surface((radius*2, radius*2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0,0,0))
        return surf

    @staticmethod
    def lamp_cone(topwidth, bottomwidth, height, color):
        surf = pygame.Surface((bottomwidth, height))
        pygame.draw.polygon(surf, color, [(bottomwidth/2+topwidth/2,0),(bottomwidth/2 - topwidth/2,0),(0, height),(bottomwidth, height)])
        surf.set_colorkey((0,0,0))
        return surf
    
    class Light:
        def __init__(self, position, surf):
            self.surf = surf
            self.position = position

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

class Explosion:
    def __init__(self, animation: KDS.Animator.Animation, pos: (int, int)):
        self.animation = animation
        self.xpos = pos[0]
        self.ypos = pos[1]

    def update(self, Surface: pygame.Surface, scroll: list):
        txtre, finished = self.animation.update()
        Surface.blit(txtre, (self.xpos-scroll[0],self.ypos-scroll[1]))
        return finished, self.animation.tick
    
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

Grenade_O = itemTools.Grenade(0.7, 9)