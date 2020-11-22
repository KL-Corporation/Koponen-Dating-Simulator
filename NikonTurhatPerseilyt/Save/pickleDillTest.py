import pygame, dill, pickle
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()

class Testi:
    def __init__(self) -> None:
        self.testinTesti = pygame.Surface((50, 10))
        self.testosteroni = pygame.mixer.Sound("testSound.ogg")

print(pickle.dumps(Testi()))