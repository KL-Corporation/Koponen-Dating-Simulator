import pygame
from pygame.locals import *

from pygame_markdown import MarkdownRenderer
# pip install Markdown

from enum import IntEnum, auto

import KDS.Animator
import KDS.Audio
import KDS.Colors

class EndingType(IntEnum):
    Happy = auto()
    Sad = auto()

def EndCredits(display: pygame.Surface, clock: pygame.time.Clock, endingType: EndingType) -> bool: # Returns True if application should quit.
    md = MarkdownRenderer()
    md.set_markdown("Assets/Data/credits.md")

    mdScroll = KDS.Animator.Value(0.0, 1.0, 5000)
    mdHorizontalPadding = (10, 10)

    mdSurf = pygame.Surface((display.get_width() - mdHorizontalPadding[0] - mdHorizontalPadding[1], 1000))
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
                if event.key == K_F6:
                    running = False
        display.blit(mdSurf, (mdHorizontalPadding[0], display.get_height() - mdScroll.update() * mdSurf.get_height()))
        pygame.display.flip()
        clock.tick_busy_loop(60)
    return False