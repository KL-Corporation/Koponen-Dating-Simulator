import pygame, numpy, math

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
    def __init__(self, rect, direction: int, speed:int, environment_obstacles, texture = None, maxDistance = 2000): #Direction should be 1 or -1; Speed should be -1 if you want the bullet to be hitscanner; Environment obstacles should be 2d array or 2d list; If you don't give a texture, bullet will be invisible
        """Bullet superclass written for KDS weapons"""
        self.rect = rect
        self.direction = direction
        self.speed = speed
        self.texture = texture
        self.maxDistance = maxDistance
        self.environment_obstacles = environment_obstacles

    def update(self,Surface:pygame.Surface):
        pass

class itemTools:
    class rk62:
        def __init__(self):
            self.counter = 0