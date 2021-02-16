from typing import Any, Callable, Union

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
        if Circle.ld_thread != None:
            Circle.ld_thread.Stop()
        
class Story:
    thread = None
    
    @staticmethod
    def rendering(surface: pygame.Surface, oldSurf: Union[pygame.Surface, None], map_name_str: str, clock: pygame.time.Clock, titleFont: pygame.font.Font, normalFont: pygame.font.Font):
        anim_lerp_x = KDS.Animator.Value(0.0, 1.0, 120, KDS.Animator.AnimationType.EaseOutSine, KDS.Animator.OnAnimationEnd.Stop)
        
        savingText: pygame.Surface = normalFont.render("Saving...", True, KDS.Colors.White)
        map_name: pygame.Surface = titleFont.render(map_name_str, True, KDS.Colors.White)
        
        story_surf = pygame.Surface(surface.get_size(), SRCALPHA)
        story_surf.blit(map_name, (story_surf.get_width() // 2 - map_name.get_width() // 2, story_surf.get_height() // 2 - map_name.get_height() // 2))
        story_surf.blit(savingText, (story_surf.get_width() - savingText.get_width() - 10, story_surf.get_height() - savingText.get_height() - 10))
        
        def doAnimation(reverse: bool):
            _break = False
            
            while not _break:
                surface.fill(KDS.Colors.Black)
                if oldSurf != None and not reverse: surface.blit(pygame.transform.scale(oldSurf, story_surf.get_size()), (0, 0))
                story_surf.set_alpha(round(KDS.Math.Lerp(0, 255, anim_lerp_x.update(reverse))))
                surface.blit(story_surf, (0, 0))

                pygame.display.flip()
                if not reverse:
                    if anim_lerp_x.get_value() >= 1.0:
                        _break = True
                else:
                    if anim_lerp_x.get_value() <= 0.0:
                        _break = True
                clock.tick_busy_loop(60)
        
        story_surf.fill(KDS.Colors.Black)
        story_surf.blit(map_name, (story_surf.get_width() // 2 - map_name.get_width() // 2, story_surf.get_height() // 2 - map_name.get_height() // 2))
        story_surf.blit(savingText, (story_surf.get_width() - savingText.get_width() - 10, story_surf.get_height() - savingText.get_height() - 10))
        
        KDS.Audio.Music.Pause()
        KDS.Audio.PlayFromFile("Assets/Audio/Effects/storystart_MAIN.wav")
        doAnimation(False)
        pygame.time.wait(3600)
        doAnimation(True)
        KDS.Audio.Music.Unpause()
    
    @staticmethod
    def Start(surface: pygame.Surface, oldSurf: Union[pygame.Surface, None], map_name_str: str, clock: pygame.time.Clock, titleFont: pygame.font.Font, normalFont: pygame.font.Font):
        Story.thread = KDS.Threading.Thread(Story.rendering, "story-loading-screen", True, True, surface, oldSurf, map_name_str, clock, titleFont, normalFont)
        
    @staticmethod
    def WaitForExit():
        if Story.thread != None:
            Story.thread.WaitForExit()
            Story.thread = None