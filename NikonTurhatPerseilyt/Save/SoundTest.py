import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.mixer.init()
snd = pygame.mixer.Sound("testSound.ogg")
pygame.mixer.quit()
print(isinstance(snd, pygame.mixer.Sound))