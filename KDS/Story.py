import pygame
from pygame.locals import *

from KDS.PygameMarkdown.PygameMarkdown import MarkdownRenderer

from enum import IntEnum, auto

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.School
import KDS.Missions
import KDS.Logging

from typing import Any, Callable, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from KoponenDatingSimulator import PlayerClass
else:
    PlayerClass = None

class EndingType(IntEnum):
    Happy = auto()
    Sad = auto()

def EndCredits(display: pygame.Surface, clock: pygame.time.Clock, endingType: EndingType) -> bool: # Returns True if application should quit.
    md = MarkdownRenderer()
    md.set_markdown("Assets/Data/credits.md", extensions=['nl2br'])

    mdScroll = KDS.Animator.Value(0.0, 1.0, 12840) # 12840 correctly syncs to music.
    mdHorizontalPadding = (10, 10)

    mdSurf = pygame.Surface((display.get_width() - mdHorizontalPadding[0] - mdHorizontalPadding[1], 4000))
    mdSurf.fill((20, 25, 20))

    md.set_area(mdSurf, 0, 0)
    md.set_color_background(20, 25, 20) # Default background color of KDS maps.
    md.display([], 0, 0, [False for _ in range(10)])

    if endingType == EndingType.Happy:
        KDS.Audio.Music.Play("Assets/Audio/Music/Prologue.ogg", 0)

    running = True
    while running:
        display.fill((20, 25, 20))
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        display.blit(mdSurf, (mdHorizontalPadding[0], display.get_height() - mdScroll.update() * mdSurf.get_height()))
        if mdScroll.Finished and KDS.Audio.Music.GetPlaying():
            pygame.time.delay(3000)
            KDS.School.Certificate(display, clock, BackgroundColor=(20, 25, 20))
            running = False
        pygame.display.flip()
        clock.tick_busy_loop(60)
    KDS.Audio.Music.Stop()
    return False

def WalkieTalkieEffect(player: PlayerClass, walkieTalkie: Type, display: pygame.Surface, clock: pygame.time.Clock, eventHandler: Callable[[Any], Any], screenBefore: pygame.Surface):
    oldSurf = pygame.transform.scale(screenBefore, display.get_size())
    slot = player.inventory.getSlot(walkieTalkie)
    if slot != None:
        player.inventory.dropItemAtIndex(slot)
    else:
        KDS.Logging.AutoError(f"No Walkie Talkie found! Type to check: {walkieTalkie}")

    def phaseZero():
        nonlocal display
        chnl = KDS.Audio.PlayFromFile("Assets/Audio/Effects/walkie_talkie.ogg", clip_volume=0.3)

        display.blit(oldSurf, (0, 0))
        pygame.display.flip()

        while chnl.get_busy():
            for event in pygame.event.get():
                eventHandler(event)

    def phaseOne():
        nonlocal display
        chnl = KDS.Audio.PlayFromFile("Assets/Audio/Effects/spooky_cut.ogg", clip_volume=0.3)

        while chnl.get_busy():
            for event in pygame.event.get():
                eventHandler(event)

    def phaseTwo():
        nonlocal display
        KDS.Audio.PlayFromFile("Assets/Audio/Effects/pistol_shoot.ogg")
        display.blit(pygame.Surface(display.get_size()), (0, 0)) # display.fill didn't work for some reason
        pygame.display.flip()

        for _ in range(60 * 8): # Frames per second times seconds
            for event in pygame.event.get():
                eventHandler(event)
            clock.tick_busy_loop(60)

    def phaseThree():
        nonlocal display, clock
        # NO SOUND CREATED   KDS.Audio.PlayFromFile("Assets/Audio/Effects/fadeout tinnitus thingy")
        blackSurf = pygame.Surface(display.get_size())
        alpha_anim = KDS.Animator.Value(255.0, 0.0, 240)

        while not alpha_anim.Finished:
            blackSurf.set_alpha(int(alpha_anim.update()))
            display.blit(oldSurf, (0, 0))
            display.blit(blackSurf, (0, 0))
            pygame.display.flip()
            clock.tick_busy_loop(60)

    phaseZero()
    phaseOne()
    phaseTwo()
    phaseThree()

    # Game state will be changed in main (NOT IMPLEMENTED)