import pygame, numpy, math, random

pygame.init()

def collision_test(rect: pygame.Rect, Tile_list):
    hit_list = []
    x = int((rect.x/34)-3)
    y = int((rect.y/34)-3)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    max_x = len(Tile_list[0])-1
    max_y = len(Tile_list)-1
    end_x = x+6
    end_y = y+6

    if end_x > max_x:
        end_x = max_x

    if end_y > max_y:
        end_y = max_y

    for row in Tile_list[y:end_y]:
        for tile in row[x:end_x]:
            if rect.colliderect(tile.rect) and not tile.air:
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
        self.slopeBuffer = 0.00

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
                #print(self.slopeBuffer)
                if self.slopeBuffer > 1 or self.slopeBuffer < -1:
                    self.rect.y += self.slopeBuffer
                    self.slopeBuffer = 0
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
            
            self.slopeBuffer += self.slope
            #print(self.slopeBuffer)
            if self.slopeBuffer > 1 or self.slopeBuffer < -1:
                self.rect.y += self.slopeBuffer
                self.slopeBuffer = 0

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

class Explosion:
    def __init__(self, animation, pos: (int, int)):
        self.animation = animation
        self.xpos = pos[0]
        self.ypos = pos[1]

    def update(self, Surface: pygame.Surface, scroll: list):
        txtre, finished = self.animation.update()
        Surface.blit(txtre, (self.xpos-scroll[0],self.ypos-scroll[1]))
        return finished, self.animation.tick
    
rk62_C = itemTools.rk62(100)
plasmarifle_C = itemTools.plasmarifle(100)
pistol_C = itemTools.pistol(100)
shotgun_C = itemTools.shotgun(100)
ppsh41_C = itemTools.ppsh41(100)