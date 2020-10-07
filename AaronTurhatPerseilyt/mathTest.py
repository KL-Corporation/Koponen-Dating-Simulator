import pygame
import math
from pygame.locals import *

pygame.init()

window_size = (500, 500)


window = pygame.display.set_mode(window_size)
c = pygame.time.Clock()
r = True

def getAngle(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]


    return math.degrees(math.atan2(dy,dx))


def getSlope(p1, p2):
    return (p2[1] - p1[1]) /  (p2[0] - p1[0])

gameRect = pygame.Rect(150, 200, 30, 30)

fs = 0.00000000
while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
            pygame.quit()
            quit()

    window.fill((255,255,255))
    a = getAngle(gameRect.center, pygame.mouse.get_pos())
    s = getSlope(gameRect.center, pygame.mouse.get_pos())
    pygame.draw.rect(window, (0, 0, 0), gameRect)
    x=0
    pygame.draw.line(window, (0, 255, 0), gameRect.center, pygame.mouse.get_pos())
    while x < 500:
        try:
            pygame.draw.rect(window, (255, 0, 0), (x+gameRect.centerx, x*s+gameRect.centery, 5, 5))
        except:
            pass
        x+= 1

    fs+=0.01
    c.tick(60)
    pygame.display.update()