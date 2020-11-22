import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.mixer.init()

class Testosteroni:
    def __init__(self) -> None:
        self.testi = pygame.Surface((10, 10))
        self.testi2 = pygame.mixer.Sound("testSound.ogg")
        self.var = 10
        self.str = "pygame"
        self.mhm = 1.5
        
print(Testosteroni().__dict__)
        