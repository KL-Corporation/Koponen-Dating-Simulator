import pygame
import numpy

surf = pygame.Surface((10, 10))
pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(1, 1, 5, 5))

surf_array = pygame.surfarray.array2d(surf)
surf_array = surf_array.tolist()
print(surf_array)
print(isinstance(surf, list))
print(isinstance(surf_array, list))