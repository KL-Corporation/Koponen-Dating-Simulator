import pygame, numpy, math

pygame.init()

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