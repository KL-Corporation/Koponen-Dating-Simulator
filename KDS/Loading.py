from typing import Any, Callable, Tuple, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Debug
import KDS.Math
import KDS.Jobs

import threading

pygame.init()

#region Settings
circleSizeDivider = 10
circleOffset = (0, 550)
#endregion

class Circle:
    running = False
    handle = None

    circleMask = None
    loadingBackground: pygame.Surface = pygame.Surface((0, 0))
    loadingFill: Tuple[int, int, int, int] = (0, 0, 0, 0)
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

        is_main_thread_active = lambda : any((i.name == "MainThread") and i.is_alive() for i in threading.enumerate())

        while not stop() and is_main_thread_active(): # Fix for thread still running after game has crashed
            surface.fill(Circle.loadingFill)
            surface.blit(Circle.scaledLoadingBackground, (surface_size[0] // 2 - Circle.scaledLoadingBackground.get_width() // 2, surface_size[1] // 2 - Circle.scaledLoadingBackground.get_height() // 2))

            ##### OLD CIRCLE #####
            # crl_size = (surface_size[0] // 8, surface_size[0] // 8)
            # crl = pygame.Surface(crl_size, pygame.SRCALPHA)
            # pygame.draw.circle(crl, (0, 148, 255), (crl_size[0] // 2, crl_size[1] // 2), crl_size[0] // 2, 10, False, True, True, True)
            # crl = pygame.transform.rotate(crl, angle * speed)
            ##### OLD CIRCLE #####

            ##### NEW CIRCLE #####
            maskRotated = pygame.transform.rotate(circleMask, angle * speed)
            crl = circle.copy()
            crl.blit(maskRotated, (circle_size[0] // 2 - maskRotated.get_width() // 2, circle_size[1] // 2 - maskRotated.get_height() // 2), special_flags=pygame.BLEND_RGBA_MULT)
            ##### NEW CIRCLE #####

            surface.blit(crl, (surface_size[0] // 2 - crl.get_width() // 2 + circleOffset[0], crl.get_height() // 2 + circleOffset[1]))
            angle += 4
            while angle >= 360: angle -= 360
            if debug:
                surface.blit(KDS.Debug.RenderData({"FPS": KDS.Math.RoundCustom(clock.get_fps(), 3, KDS.Math.MidpointRounding.AwayFromZero)}), (0, 0))

            clock.tick_busy_loop(60)
            pygame.display.flip()

    @staticmethod
    def Start(surface: pygame.Surface, clock: pygame.time.Clock, debug: bool = False):
        global circleMask, debugFont
        if Circle.circleMask == None:
            circleMask = pygame.image.load("Assets/Textures/UI/loading_circle_mask.png").convert_alpha()
            Circle.loadingBackground = pygame.image.load("Assets/Textures/UI/loading_background.png").convert()
            Circle.loadingFill = Circle.loadingBackground.get_at((0, 0))
            debugFont = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10, bold=0, italic=0)
        Circle.running = True
        surface_size = surface.get_size()
        Circle.scaledLoadingBackground = KDS.Convert.AspectScale(Circle.loadingBackground, surface_size)
        surface.fill(Circle.loadingFill)
        surface.blit(Circle.scaledLoadingBackground, (surface_size[0] // 2 - Circle.scaledLoadingBackground.get_width() // 2, surface_size[1] // 2 - Circle.scaledLoadingBackground.get_height() // 2))
        pygame.display.flip()
        Circle.handle = KDS.Jobs.Schedule(Circle.rendering, surface, clock, debug, lambda: not Circle.running)

    @staticmethod
    def Stop():
        Circle.running = False
        if Circle.handle != None:
            Circle.handle.Complete()

class Story:
    handle = None

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
        Story.handle = KDS.Jobs.Schedule(Story.rendering, surface, oldSurf, map_name_str, clock, titleFont, normalFont)

    @staticmethod
    def WaitForExit():
        if Story.handle != None:
            Story.handle.Complete()
            Story.handle = None