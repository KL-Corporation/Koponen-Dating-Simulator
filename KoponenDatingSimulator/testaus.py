import os, shutil, pygame, math, concurrent.futures, time, numpy
from pygame.locals import *
pygame.init()
main_display = pygame.display.set_mode((600,600))

angle = 45

k = 0

p1 = (0,0)
p2 = (1,2)

k = (p2[1] - p1[1])/(p2[0]- p1[0])

print(round(math.tan(math.radians(angle))))

print("ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")

class Rect:
    def __init__(self):
        self.rect = (10,10,10,10)


class Triangle:
    def __init__(self):
        self.triangle = (20, 30, 21)

array = numpy.array([])

array = numpy.append(array, Rect())
array = numpy.append(array, Triangle())

print(array)

for i in array:
    if isinstance(i, Triangle):
        print("i on kolmio")
das = pygame.image.load("Assets/Textures/Items/gasburner_off.png")
flip = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == K_a:
                flip = not flip

    main_display.blit(pygame.transform.flip(das, flip, False), (100, 100))
    pygame.display.update()

    