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

class Tile:


    def __init__(self, position: (int, int), serialNumber: int):
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.serialNumber = serialNumber
        if serialNumber:
            self.texture = t_textures[serialNumber]
            self.air = False
        else:
            self.air = True

    @staticmethod
    # Tile_list is a 2d numpy array
    def render(Tile_list, Surface: pygame.Surface, scroll: list, position: (int, int)):
        x = int(position[0] / 34)
        y = int(position[1] / 34)
        x -= 10
        y -= 10
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        max_x = len(Tile_list[0])-1
        max_y = len(Tile_list) - 1
        end_x = x + 30
        end_y = y + 12
        if end_x > max_x:
            end_x = max_x
        if end_y > max_y:
            end_y = max_y

        for row in Tile_list[y:end_y]:
            for renderable in row[x:end_x]:
                if not renderable.air:
                    Surface.blit(renderable.texture, (renderable.rect.x -
                                                      scroll[0], renderable.rect.y - scroll[1]))

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
        if not slope:
            slope = -1
        self.slope = slope

    def update(self,Surface:pygame.Surface, scroll: list):
        if self.texture:
            Surface.blit(self.texture, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        if self.speed == -1:
            for _ in range(int(self.maxDistance/18)):
                if self.direction:
                    self.rect.x -= 18                  
                else:
                    self.rect.x += 18
                self.rect.y += self.slope
                collision_list = collision_test(self.rect, self.environment_obstacles)
                if collision_list:
                    return "wall"
            return "air"
        else:
            if self.direction:
                self.rect.x -= self.speed
                self.movedDistance += self.speed             
            else:
                self.rect.x += self.speed
                self.movedDistance += self.speed
            self.rect.y += self.slope

            collision_list = collision_test(self.rect, self.environment_obstacles)
            if collision_list:
                return "wall"
            if self.movedDistance > self.maxDistance:
                return "air"

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

class Explosion:
    def __init__(self, animation, pos: (int, int)):
        self.animation = animation
        self.xpos = pos[0]
        self.ypos = pos[1]

    def update(self, Surface: pygame.Surface, scroll: list):
        txtre, finished = self.animation.update()
        Surface.blit(txtre, (self.xpos-scroll[0],self.ypos-scroll[1]))
        return finished
    
rk62_C = itemTools.rk62(100)
plasmarifle_C = itemTools.plasmarifle(100)
pistol_C = itemTools.pistol(100)
shotgun_C = itemTools.shotgun(100)