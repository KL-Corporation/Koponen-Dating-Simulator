import pygame
from pygame.locals import *

class mpgObject:

    def __init__(self, path = ""):
        self._path = path
        self.obj = pygame.movie.Movie(self._path)
        self.surf = pygame.Surface(self.obj.get_size()).convert()
        self.obj.set_display(self.surf)
    
    def play(self, loops = -1):
        self.obj.play(loops)

    def stop(self):
        self.obj.stop()

    def getFrame(self):
        return self.obj