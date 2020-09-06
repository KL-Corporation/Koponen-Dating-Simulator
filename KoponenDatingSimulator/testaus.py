import os, shutil, pygame, math, concurrent.futures, time, numpy

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


ar = [[1,2,3,4],[1,2,3,4,5,6,7],[1,2,3,4,5,6,7,8,9]]
print(max(ar))

def func(**kwargs):
    for key, ans in kwargs.items():
        

func(f=1,s=2,l=3)