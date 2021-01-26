import pygame
from pygame.locals import *
import math

pygame.init()
pygame.mixer.init()

logfont = pygame.font.SysFont("Arial", 20)

class tPrint:
    def __init__(self):
        self.row = 0
    
    def tprint(self, text, surf):
        surf.blit(logfont.render(text, False, Colors.White), (0, self.row))
        self.row += logfont.size(text)[1] + 2

    def reset(self): self.row = 0

class Colors:
    Red = (255, 0, 0)
    Green = (0, 255, 0)
    Blue = (0, 0, 255)
    White = (255, 255, 255)
    Black = (0, 0, 0)

class Vector:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point
        self.length = math.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)

class VectorUnit:
    def __init__(self, start_point, end_point):
        normalizing_factor = math.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)
        self.x = (end_point[0] - start_point[0]) / normalizing_factor
        self.y = (end_point[1] - start_point[1]) / normalizing_factor

    """
    def __init__(self, vect: Vector):
        normalizing_factor = math.sqrt((vect.end_point[0] - vect.start_point[0]) ** 2 + (vect.end_point[1] - vect.start_point[1]) ** 2)
        self.x = (vect.end_point[0] - vect.start_point[0]) / normalizing_factor
        self.y = (vect.end_point[1] - vect.end_point[1]) / normalizing_factor
    """

    def getDotProduct(self, relative_vector):
        return self.x * relative_vector.x + self.y * relative_vector.y

class PygamePropgram:
    def __init__(self, window_size, audio_mixer, clock, name = "program", icon = None, framerate_limit = 60, video_flags = RESIZABLE | HWSURFACE | DOUBLEBUF):
        self.window = pygame.display.set_mode(window_size, video_flags)
        self.name = name
        self.mixer = audio_mixer
        self.loop_running = True
        self.clock = clock
        self.fps_limit = framerate_limit

        self.printer = tPrint()

        #Turhat muuttujat
        self.matrix = [[0 for _ in range(400)] for _ in range(400)]
        self.v1 = Vector((400, 400), (500, 700))

        pygame.display.set_caption(self.name)

        if icon != None:
            if isinstance(icon, str):
                icon = pygame.image.load(icon).convert()
                pygame.display.set_icon(icon)
            elif isinstance(icon, pygame.Surface):
                pygame.display.set_icon(icon)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.loop_running = False

    def update(self):
        pass

    def render(self):
        self.window.fill(Colors.Black)

        v2 = VectorUnit((400, 400), pygame.mouse.get_pos())
        pygame.draw.line(self.window, Colors.White, self.v1.start_point, self.v1.end_point, 1)

        pygame.draw.line(self.window, Colors.Red, (400, 400), (v2.x * 200 + 400, v2.y * 200 + 400), 1)
        self.printer.tprint(f"{v2.getDotProduct(VectorUnit(self.v1.start_point, self.v1.end_point))}", self.window)

        pygame.display.flip()
        self.printer.reset()
        self.clock.tick_busy_loop(self.fps_limit)

    def close(self):
        pygame.quit()

def main(*args, **kwargs):
    main_program = PygamePropgram((800, 800), pygame.mixer, pygame.time.Clock())
    while main_program.loop_running:
        main_program.handleEvents()
        main_program.update()
        main_program.render()
    main_program.close()


if __name__ == "__main__" : main()