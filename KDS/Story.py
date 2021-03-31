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

    waitTicks = 0

    if endingType == EndingType.Happy:
        KDS.Audio.Music.Play("Assets/Audio/Music/Prologue.ogg", 0)

    running = True
    while running:
        display.fill((20, 25, 20))
        pygame.event.get() # Because Windows thinks this app has frozen
        display.blit(mdSurf, (mdHorizontalPadding[0], display.get_height() - mdScroll.update() * mdSurf.get_height()))
        if mdScroll.Finished and not KDS.Audio.Music.GetPlaying():
            pygame.mouse.set_visible(True)
            waitTicks += 1
            if waitTicks > 60 * 3:
                KDS.School.Certificate(display, clock, BackgroundColor=(20, 25, 20))
                running = False
        pygame.display.flip()
        clock.tick_busy_loop(60)
    KDS.Audio.Music.Stop()
    return False

class WalkieTalkieEffect:
    phaseTwoIndex = 0
    phaseIndex = 0
    phaseZeroChannel = None
    phaseOneChannel = None
    phaseThreeChannel = None
    blackSurf = None
    alpha_anim = KDS.Animator.Value(255.0, 0.0, 240)

    @staticmethod
    def Start(newCall: bool, player: PlayerClass, display: pygame.Surface) -> bool:
        if newCall:
            WalkieTalkieEffect.phaseTwoIndex = 0
            WalkieTalkieEffect.phaseIndex = 0
            WalkieTalkieEffect.phaseZeroChannel = None
            WalkieTalkieEffect.phaseOneChannel = None
            WalkieTalkieEffect.blackSurf = pygame.Surface(display.get_size())

        def phaseZero() -> bool:
            if WalkieTalkieEffect.phaseZeroChannel == None:
                WalkieTalkieEffect.phaseZeroChannel = KDS.Audio.PlayFromFile("Assets/Audio/Effects/walkie_talkie.ogg", clip_volume=0.3)

            return False if WalkieTalkieEffect.phaseZeroChannel.get_busy() else True

        def phaseOne() -> bool:
            if WalkieTalkieEffect.phaseOneChannel == None:
                WalkieTalkieEffect.phaseOneChannel = KDS.Audio.PlayFromFile("Assets/Audio/Effects/spooky_cut.ogg", clip_volume=0.3)

            return False if WalkieTalkieEffect.phaseOneChannel.get_busy() else True

        def phaseTwo() -> bool:
            if WalkieTalkieEffect.phaseTwoIndex == 0:
                KDS.Audio.PlayFromFile("Assets/Audio/Effects/pistol_shoot.ogg")

                slot = player.inventory.getSlot(36)
                if slot != None:
                    player.inventory.dropItemAtIndex(slot, forceDrop=True)
                else:
                    KDS.Logging.AutoError("Walkie talkie not found!")

            display.blit(pygame.Surface(display.get_size()), (0, 0)) # display.fill didn't work for some reason

            WalkieTalkieEffect.phaseTwoIndex += 1
            return False if WalkieTalkieEffect.phaseTwoIndex < 60 * 8 else True

        def phaseThree() -> bool:
            if WalkieTalkieEffect.phaseThreeChannel == None:
                pass
            # NO SOUND CREATED   KDS.Audio.PlayFromFile("Assets/Audio/Effects/fadeout tinnitus thingy")
            if WalkieTalkieEffect.blackSurf != None:
                WalkieTalkieEffect.blackSurf.set_alpha(int(WalkieTalkieEffect.alpha_anim.update()))
                display.blit(WalkieTalkieEffect.blackSurf, (0, 0))

                return False if not WalkieTalkieEffect.alpha_anim.Finished else True
            else:
                KDS.Logging.AutoError("alpha_anim is None!")
                return False

        phases = (
            phaseZero,
            phaseOne,
            phaseTwo,
            phaseThree
        )

        if phases[WalkieTalkieEffect.phaseIndex]():
            WalkieTalkieEffect.phaseIndex += 1

        return False if WalkieTalkieEffect.phaseIndex < len(phases) else True

        # Game state will be changed in main (NOT IMPLEMENTED)
