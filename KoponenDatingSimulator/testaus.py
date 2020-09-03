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

objectTypes = {0: "tile", 1: "item", 2: "entity", 3: "decoration"}
with open("Assets/Maps/map06/level.map", "r") as level:
    levelData = level.read().split("\n")
    for row in levelData:
        for block in row.split("/"):
            blockData = block.split()
            print(blockData)
            #Tänne jokaisen blockin käsittelyyn liittyvä koodi
            blockType = objectTypes[int(blockData[0])]

d2_array = [
    [1,1,1],
    [1,1,1],
    [1,1,1],
    [1,1,1],
    [1,1,1],
    [1,1,1],
]
#array = numpy.empty((4,4))
array = numpy.array([Rect(), Rect(), Rect()])
#array[1][1] = Rect()
print(array)