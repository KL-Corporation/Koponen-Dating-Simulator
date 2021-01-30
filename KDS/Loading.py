from typing import Any, Callable

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Math
import KDS.Threading

pygame.init()

#region Settings
circleSizeDivider = 10
circleOffset = (0, 550)
#endregion

class Circle:

    running = False

    ld_thread = None
    circleMask = None
    loadingBackground: pygame.Surface = pygame.Surface((0, 0))
    scaledLoadingBackground: pygame.Surface = pygame.Surface((0, 0))
    debugFont = None

    @staticmethod
    def rendering(surface: pygame.Surface, clock: pygame.time.Clock, debug: bool, stop: Callable[[], bool]):
        angle = 0
        speed = -1
        surface_size = surface.get_size()

        ##### NEW CIRCLE #####
        circle_size = (surface_size[0] // circleSizeDivider, surface_size[0] // circleSizeDivider)
        circle = pygame.Surface(circle_size, pygame.SRCALPHA)
        pygame.draw.circle(circle, (0, 148, 255), (circle_size[0] // 2, circle_size[1] // 2), circle_size[0] // 2, 10)
        ##### NEW CIRCLE #####
        
        while not stop():
            surface.blit(Circle.scaledLoadingBackground, (surface_size[0] // 2 - Circle.scaledLoadingBackground.get_width() // 2, surface_size[1] // 2 - Circle.scaledLoadingBackground.get_height() // 2))
            
            ##### OLD CIRCLE #####
            # crl_size = (surface_size[0] // 8, surface_size[0] // 8)
            # crl = pygame.Surface(crl_size, pygame.SRCALPHA)
            # pygame.draw.circle(crl, (0, 148, 255), (crl_size[0] // 2, crl_size[1] // 2), crl_size[0] // 2, 10, False, True, True, True)
            # crl = pygame.transform.rotate(crl, angle * speed)
            ##### OLD CIRCLE #####
            
            ##### NEW CIRCLE #####
            crl = circle.copy()
            maskRotated = pygame.transform.rotate(circleMask, angle * speed)
            crl.blit(maskRotated, (circle_size[0] // 2 - maskRotated.get_width() // 2, circle_size[1] // 2 - maskRotated.get_height() // 2), special_flags=pygame.BLEND_RGBA_MULT)
            ##### NEW CIRCLE #####
            
            surface.blit(crl, (surface_size[0] // 2 - crl.get_width() // 2 + circleOffset[0], crl.get_height() // 2 + circleOffset[1]))
            angle += 4
            while angle >= 360: angle -= 360
            if debug:
                debugSurf = pygame.Surface((200, 40))
                debugSurf.fill(KDS.Colors.DarkGray)
                debugSurf.set_alpha(128)
                surface.blit(debugSurf, (0, 0))
                
                fps_text = "FPS: " + str(round(clock.get_fps()))
                fps_text = debugFont.render(fps_text, True, KDS.Colors.White)
                surface.blit(pygame.transform.scale(fps_text, (int(
                    fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))
                
            clock.tick_busy_loop(60)
            pygame.display.flip()

    @staticmethod
    def Start(surface: pygame.Surface, clock: pygame.time.Clock, debug: bool = False):
        global circleMask, debugFont, running
        if Circle.circleMask == None:
            circleMask = pygame.image.load("Assets/Textures/UI/loading_circle_mask.png").convert_alpha()
            Circle.loadingBackground = pygame.image.load("Assets/Textures/UI/loading_background.png").convert()
            debugFont = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10, bold=0, italic=0)
        running = True
        surface_size = surface.get_size()
        Circle.scaledLoadingBackground = KDS.Convert.AspectScale(Circle.loadingBackground, surface_size)
        surface.blit(Circle.scaledLoadingBackground, (surface_size[0] // 2 - Circle.scaledLoadingBackground.get_width() // 2, surface_size[1] // 2 - Circle.scaledLoadingBackground.get_height() // 2))
        pygame.display.flip()
        Circle.ld_thread = KDS.Threading.StoppableThread(Circle.rendering, "loading-screen", True, True, surface, clock, debug)

    @staticmethod
    def Stop():
        global running
        Circle.ld_thread.Stop()