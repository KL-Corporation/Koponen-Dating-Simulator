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
import KDS.World
import KDS.Clock
import KDS.Debug
import KDS.UI

from typing import TYPE_CHECKING, Callable, Final

if TYPE_CHECKING:
    from KoponenDatingSimulator import PlayerClass
else:
    PlayerClass = None

BadEndingTrigger: bool = False

walkie_talkie_sound: Final = pygame.mixer.Sound("Assets/Audio/Effects/walkie_talkie.ogg")
walkie_talkie_sound.set_volume(0.3)
walkie_talkie_spooky_cut_sound: Final = pygame.mixer.Sound("Assets/Audio/Effects/spooky_cut.ogg")
walkie_talkie_spooky_cut_sound.set_volume(0.3)
walkie_talkie_pistol_shoot_sound: Final = pygame.mixer.Sound("Assets/Audio/Effects/pistol_shoot.ogg")
tombstones_creepy_music: Final = pygame.mixer.Sound("Assets/Audio/Music/creepy_music_box.ogg")
tombstones_creepy_music.set_volume(0.5)

def badStoryEndingFunc():
    global BadEndingTrigger
    BadEndingTrigger = True

def switchToStoryHappyTalkMusic():
    KDS.Audio.Music.Play("Assets/Audio/Koponen/happyendingtalksong.ogg")

class EndingType(IntEnum):
    Happy = auto()
    Sad = auto()

def EndCredits(display: pygame.Surface, endingType: EndingType) -> bool: # Returns True if application should quit.
    if endingType == EndingType.Sad:
        Tombstones(display)

    md = MarkdownRenderer()
    md.set_markdown("Assets/Data/credits.md", extensions=['markdown.extensions.nl2br'])
    md.font_header = pygame.font.Font("Assets/Fonts/Windows/arialbd.ttf", md.font_header_size)
    md.font_header2 = pygame.font.Font("Assets/Fonts/Windows/arialbd.ttf", md.font_header2_size)
    md.font_header3 = pygame.font.Font("Assets/Fonts/Windows/arialbd.ttf", md.font_header3_size)
    md.font_text = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", md.font_text_size)
    md.font_quote = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", md.font_quote_size)
    # md.font_code = pygame.font.Font(md.font_code_str, md.font_text_size) We dont use code blocks

    mdScroll = KDS.Animator.Value(0.0, 1.0, 12840) # 12840 correctly syncs to music.
    mdHorizontalPadding = (10, 10)

    mdSurf = pygame.Surface((display.get_width() - mdHorizontalPadding[0] - mdHorizontalPadding[1], 4000))
    mdSurf.fill(KDS.Colors.DefaultBackground)

    md.set_area(mdSurf, 0, 0)
    md.set_color_background(*KDS.Colors.DefaultBackground) # Default background color of KDS maps.
    md.display([], 0, 0, [False for _ in range(10)])

    waitTicks = 0

    KDS.Audio.Music.Play("Assets/Audio/Music/Prologue.ogg", loop=False)

    running = True
    while running:
        display.fill(KDS.Colors.DefaultBackground)
        pygame.event.get() # Because Windows thinks this app has frozen. DO NOT LET PEOPLE CLOSE THE CREDITS
        display.blit(mdSurf, (mdHorizontalPadding[0], display.get_height() - mdScroll.update() * mdSurf.get_height()))
        if mdScroll.Finished and not KDS.Audio.Music.GetPlaying():
            pygame.mouse.set_visible(True)
            waitTicks += 1
            if waitTicks > 60 * 3:
                if endingType == EndingType.Happy:
                    KDS.School.Certificate(display, BackgroundColor=KDS.Colors.DefaultBackground)
                running = False
                pygame.event.clear()
        pygame.display.flip()
        KDS.Clock.Tick()
    KDS.Audio.Music.Stop()
    return False

def Tombstones(display: pygame.Surface):
    image: pygame.Surface = pygame.image.load("Assets/Textures/UI/bad_ending.png").convert()

    animA = KDS.Animator.Value(255.0, 0.0, 7 * 60)
    blk = pygame.Surface(image.get_size())

    chnl = KDS.Audio.PlaySound(tombstones_creepy_music)
    while chnl.get_busy():
        blk.set_alpha(round(animA.update()))
        pygame.event.get()

        display.blit(image, (0, 0))
        display.blit(blk, (0, 0))

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData(None), (0, 0))

        pygame.display.flip()
        KDS.Clock.Tick()

class WalkieTalkieEffect:
    phaseTwoIndex: int
    phaseIndex: int
    phaseZeroChannel: pygame.mixer.Channel | None
    phaseOneChannel: pygame.mixer.Channel | None
    phaseThreeStarted: bool
    blackSurf: pygame.Surface
    alpha_anim: KDS.Animator.Value


    @staticmethod
    def Start(newCall: bool, player: PlayerClass, display: pygame.Surface) -> tuple[bool, bool]:
        if newCall:
            WalkieTalkieEffect.phaseTwoIndex = 0
            WalkieTalkieEffect.phaseIndex = 0
            WalkieTalkieEffect.phaseZeroChannel = None
            WalkieTalkieEffect.phaseOneChannel = None
            WalkieTalkieEffect.phaseThreeStarted = False
            WalkieTalkieEffect.blackSurf = pygame.Surface(display.get_size())
            WalkieTalkieEffect.alpha_anim = KDS.Animator.Value(255.0, 0.0, 240)

            player.lockMovement = True
            KDS.Audio.Music.Fadeout(1.0)

        def phaseZero() -> bool:
            if WalkieTalkieEffect.phaseZeroChannel is None:
                WalkieTalkieEffect.phaseZeroChannel = KDS.Audio.PlaySound(walkie_talkie_sound)

            return False if WalkieTalkieEffect.phaseZeroChannel.get_busy() else True

        def phaseOne() -> bool:
            if WalkieTalkieEffect.phaseOneChannel is None:
                WalkieTalkieEffect.phaseOneChannel = KDS.Audio.PlaySound(walkie_talkie_spooky_cut_sound)

            return False if WalkieTalkieEffect.phaseOneChannel.get_busy() else True

        def phaseTwo() -> bool:
            if WalkieTalkieEffect.phaseTwoIndex == 0:
                KDS.Audio.PlaySound(walkie_talkie_pistol_shoot_sound)

                slot = player.inventory.getSlot(36)
                if slot != None:
                    player.inventory.dropItemAtIndex(slot, forceDrop=True)
                else:
                    KDS.Logging.AutoError("Walkie talkie not found!")

                KDS.World.Dark.Configure(True, 224)
                player.health = 15.0
                player.direction = True

            display.fill((0, 0, 0))

            WalkieTalkieEffect.phaseTwoIndex += 1
            return False if WalkieTalkieEffect.phaseTwoIndex < 60 * 8 else True

        def phaseThree() -> tuple[bool, bool]:
            run_glitch: bool = False
            if not WalkieTalkieEffect.phaseThreeStarted:
                KDS.Audio.Music.Play("Assets/Audio/Effects/glitch.ogg")
                run_glitch = True
                WalkieTalkieEffect.phaseThreeStarted = True

            WalkieTalkieEffect.blackSurf.set_alpha(int(WalkieTalkieEffect.alpha_anim.update()))
            display.blit(WalkieTalkieEffect.blackSurf, (0, 0))
            return (WalkieTalkieEffect.alpha_anim.Finished, run_glitch)

        phases: tuple[Callable[[], bool | tuple[bool, bool]], ...] = (
            phaseZero,
            phaseOne,
            phaseTwo,
            phaseThree
        )

        run_glitch: bool = False
        phase_output: bool | tuple[bool, bool] = phases[WalkieTalkieEffect.phaseIndex]()
        if isinstance(phase_output, bool):
            if phase_output:
                WalkieTalkieEffect.phaseIndex += 1
        else:
            if phase_output[0]:
                WalkieTalkieEffect.phaseIndex += 1
            if phase_output[1]:
                run_glitch = True

        if WalkieTalkieEffect.phaseIndex >= len(phases):
            player.lockMovement = False
            return (True, run_glitch)

        return (False, run_glitch)

        # Game state will be changed in main (NOT IMPLEMENTED) (or is it? I can't remember)
