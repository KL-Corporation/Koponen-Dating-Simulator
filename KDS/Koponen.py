from inspect import currentframe
import os
import random
from typing import List, Tuple
import pygame
from pygame.locals import *
import math
import sys
import KDS.Colors
import KDS.Convert
import KDS.Animator
import KDS.Audio
import KDS.UI
import KDS.Logging
import KDS.Math

#region Settings
text_font = pygame.font.Font("Assets/Fonts/courier.ttf", 30, bold=0, italic=0)
text_color = KDS.Colors.MidnightBlue
background_color = KDS.Colors.CloudWhite
background_outline_color = KDS.Colors.MidnightBlue
conversation_rect = pygame.Rect(40, 40, 700, 400)
conversation_outline_width = 3
conversation_border_radius = 10
line_spacing = 25
line_reveal_speed = 5
line_scroll_speed = 1
min_time_before_scroll = 120 #ticks
auto_scroll_offset_index = 10
scroll_to_bottom_rect = pygame.Rect(640, 340, 50, 50)
scroll_arrow_padding = 5
scroll_to_bottom_colors = {
    "default": (KDS.Colors.DarkGray),
    "highlighted": (KDS.Colors.Gray),
    "pressed": (KDS.Colors.LightGray)
}
class text_padding:
    left = 5
    top = 5
    right = 5
    bottom = 5
#endregion

pygame.init()
pygame.key.stop_text_input()

Task = None

"""
def koponen_talk():
    global main_running, currently_on_mission, player_score, ad_images, koponen_talking_background, koponen_talking_foreground_indexes, koponenTalking
    conversations = []

    KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.KoponenTalk)

    koponenTalking = True
    pygame.mouse.set_visible(True)

    c = False

    for i in range(len(koponen_talking_foreground_indexes), 0):
        koponen_talking_foreground_indexes[i] = koponen_talking_foreground_indexes[i - 1]
    random_foreground = int(random.uniform(0, len(ad_images)))
    while random_foreground == koponen_talking_foreground_indexes[0] or random_foreground == koponen_talking_foreground_indexes[1] or random_foreground == koponen_talking_foreground_indexes[2] or random_foreground == koponen_talking_foreground_indexes[3] or random_foreground == koponen_talking_foreground_indexes[4]:
        random_foreground = int(random.uniform(0, len(ad_images)))
    koponen_talking_foreground_indexes[4] = random_foreground
    koponen_talk_foreground = ad_images[random_foreground].copy()

    def exit_function1():
        global koponenTalking
        koponenTalking = False

    def mission_function():
        global currently_on_mission, current_mission, taskTaivutettu, task

        conversations.append(f"{player_name}: Saisinko tehtävän?")
        if currently_on_mission:
            conversations.append("Koponen: Olen pahoillani, sinulla on")
            conversations.append("         tehtävä kesken")
            conversations.append("Koponen: Tehtäväsi oli tuoda minulle")
            conversations.append(f"         {task}.")
        elif WorldData.Legacy.task_items:
            current_mission = WorldData.Legacy.task_items[0]
            WorldData.Legacy.task_items.remove(WorldData.Legacy.task_items[0])
        if current_mission == "coffeemug":
            task = "kahvikuppi"
            taskTaivutettu = "kahvikupin"
        elif current_mission == "ss_bonuscard":
            task = "SS-etukortti"
            taskTaivutettu = "SS-etukortin"
        else:
            task = "[FINISHED]"
            taskTaivutettu = "[FINISHED]"

        if task == "[FINISHED]" or taskTaivutettu == "[FINISHED]":
            conversations.append("Koponen: Olet suorittanut kaikki")
            conversations.append("         tehtävät")
        elif currently_on_mission == False:
            conversations.append(
                f"Koponen: Toisitko minulle {taskTaivutettu}")
            currently_on_mission = True

    def date_function():
        global koponen_happiness

        conversations.append(
            f"{player_name}: Tulisitko kanssani treffeille?")

        if koponen_happiness > 90:
            conversations.append("Koponen: Tulisin mielelläni kanssasi")
        elif 91 > koponen_happiness > 70:
            if int(random.uniform(0, 3)):
                conversations.append("Koponen: Kyllä ehdottomasti")
            else:
                conversations.append("Koponen: En tällä kertaa")
                koponen_happiness -= 3
        elif 71 > koponen_happiness > 50:
            if int(random.uniform(0, 2)):
                conversations.append("Koponen: Tulen kanssasi")
            else:
                conversations.append("Koponen: Ei kiitos")
                koponen_happiness -= 3
        elif 51 > koponen_happiness > 30:
            if int(random.uniform(0, 3)) == 3:
                conversations.append("Koponen: Tulen")
            else:
                conversations.append("Koponen: En tule")
                koponen_happiness -= 7
        elif 31 > koponen_happiness > 10:
            if int(random.uniform(0, 5)) == 5:
                conversations.append("Koponen: Kyllä")
            else:
                conversations.append("Koponen: Ei.")
                koponen_happiness -= 10
        else:
            conversations.append("Koponen: Ei ei ei")

    def end_mission():
        global current_mission, currently_on_mission, player_score, koponen_happiness

        try:
            taskTaivutettu
        except NameError:
            KDS.Logging.Log(KDS.Logging.LogType.warning,
                            "Task not defined. Defining task...", False)
            task = ""
            taskTaivutettu = ""

        if not currently_on_mission:
            conversations.append("Koponen: Sinulla ei ole palautettavaa")
            conversations.append("         tehtävää")
        else:
            if current_mission in player_inventory.storage:
                missionRemoveRange = range(len(player_inventory.storage))
                itemFound = False
                for i in missionRemoveRange:
                    if itemFound == False:
                        if player_inventory.storage[i] == current_mission:
                            player_inventory.storage[i] = Inventory.emptySlot
                            itemFound = True
                conversations.append("Koponen: Loistavaa työtä")
                conversations.append("Game: Player score +60")
                player_score += 60
                koponen_happiness += 10
                currently_on_mission = False
                current_mission = "none"
            else:
                conversations.append("Koponen: Housuistasi ei löydy")
                conversations.append("         pyytämääni esinettä.")
                conversations.append("Koponen: Tehtäväsi oli tuoda minulle.")
                conversations.append(f"         {task}")

    c = False

    conversations.append("Koponen: Hyvää päivää")

    exit_button = KDS.UI.Button(pygame.Rect(940, 700, 230, 80), exit_function1, button_font1.render(
        "EXIT", True, KDS.Colors.White))
    mission_button = KDS.UI.Button(pygame.Rect(50, 700, 450, 80), mission_function, button_font1.render(
        "REQUEST MISSION", True, KDS.Colors.White))
    date_button = KDS.UI.Button(pygame.Rect(50, 610, 450, 80), date_function, button_font1.render(
        "ASK FOR A DATE", True, KDS.Colors.White))
    r_mission_button = KDS.UI.Button(pygame.Rect(510, 700, 420, 80), end_mission, button_font1.render(
        "RETURN MISSION", True, KDS.Colors.White))

    while koponenTalking:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponenTalking = False
                elif event.key == K_F11:
                    Fullscreen.Set()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)
        display.blit(pygame.transform.scale(koponen_talking_background, (int(
            koponen_talking_background.get_width()), int(koponen_talking_background.get_height()))), (0, 0))
        display.blit(pygame.transform.scale(koponen_talk_foreground, (int(
            koponen_talk_foreground.get_width()), int(koponen_talk_foreground.get_height()))), (40, 474))
        pygame.draw.rect(display, (230, 230, 230),
                         pygame.Rect(40, 40, 700, 400))
        pygame.draw.rect(display, (30, 30, 30),
                         pygame.Rect(40, 40, 700, 400), 3)

        exit_button.update(display, mouse_pos, c)
        mission_button.update(display, mouse_pos, c)
        date_button.update(display, mouse_pos, c)
        r_mission_button.update(display, mouse_pos, c)

        while len(conversations) > 13:
            del conversations[0]
        for i in range(len(conversations)):
            row_text = text_font.render(conversations[i], True, (7, 8, 10))
            row_text_size = text_font.size(conversations[i])
            display.blit(pygame.transform.scale(row_text, (int(
                row_text_size[0]), int(row_text_size[1]))), (50, int(50 + (i * 30))))
        c = False
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        window.fill((0, 0, 0))
    pygame.mouse.set_visible(False)
"""
talk_background = pygame.Surface((0, 0))
talk_foregrounds = [pygame.Surface((0, 0), SRCALPHA)]
talk_foreground = talk_foregrounds[0]

class Prefixes:
    player = "p:"
    koponen = "k:"
    class Rendered:
        player = text_font.render("ERROR: ", True, text_color)
        koponen = text_font.render("Koponen: ", True, text_color)

def init(playerName: str):
    global talk_background, talk_foregrounds, talk_foreground, scrollArrow, scrollToBottomButton, ambientTalkAudios
    talk_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png").convert()
    scrollArrow = pygame.transform.scale(pygame.transform.rotate(pygame.image.load("Assets/Textures/UI/Buttons/Arrow.png").convert_alpha(), -90), (scroll_to_bottom_rect.width - scroll_arrow_padding * 2, scroll_to_bottom_rect.height - scroll_arrow_padding * 2))
    scrollToBottomButton = KDS.UI.Button(scroll_to_bottom_rect, Talk.Conversation.scrollToBottom, scrollArrow, scroll_to_bottom_colors["default"], scroll_to_bottom_colors["highlighted"], scroll_to_bottom_colors["pressed"])
    for ad in os.listdir("Assets/Textures/KoponenTalk/ads"): talk_foregrounds.append(pygame.image.load(f"Assets/Textures/KoponenTalk/ads/{ad}").convert_alpha())
    random.shuffle(talk_foregrounds)
    Prefixes.Rendered.player = text_font.render(f"{playerName}: ", True, text_color)
    ambientTalkAudios = [
        pygame.mixer.Sound("Assets/Audio/Koponen/talk_0.ogg"),
        pygame.mixer.Sound("Assets/Audio/Koponen/talk_1.ogg"),
        pygame.mixer.Sound("Assets/Audio/Koponen/talk_2.ogg"),
        pygame.mixer.Sound("Assets/Audio/Koponen/talk_3.ogg")
    ]
    random.shuffle(ambientTalkAudios)

class Date:
    @staticmethod
    def start(window: pygame.Surface, surface: pygame.Surface, Fullscreen, ResizeWindow, KDS_Quit, clock: pygame.time.Clock, fps: int):
        pass

class Talk:
    running = False
    mask = pygame.mask.Mask(conversation_rect.size, True)
    surface = pygame.Surface(conversation_rect.size, pygame.SRCALPHA, masks=mask)
    surface_size = surface.get_size()
    lineCount = math.floor((surface.get_height() - text_padding.top - text_padding.bottom) / text_font.size(" ")[1])
    audioChannel = None
    soundPlaying = None
    
    lines: List[str] = []
    scheduled: List[str] = []
        
    class Conversation:
        @staticmethod
        def scrollToBottom():
            Talk.Conversation.scroll = max(len(Talk.lines) - Talk.lineCount, 0)
        scroll = 0
        animationProgress = -1
        animationWidth = 0
        newAnimation = False
        
        @staticmethod
        def schedule(text, prefix: Prefixes and str):
            prefixWidth = Prefixes.Rendered.player.get_width() if prefix == Prefixes.player else Prefixes.Rendered.koponen.get_width()
            lineSplit = KDS.Convert.ToLines(text, text_font, Talk.surface_size[0] - text_padding.left - text_padding.right - prefixWidth)
            for _text in lineSplit: Talk.scheduled.append(prefix + _text)
        
        @staticmethod
        def update():
            if Talk.Conversation.animationProgress == -1 and len(Talk.scheduled) > 0:
                if Talk.audioChannel == None or Talk.audioChannel.get_sound() != Talk.soundPlaying:
                    Talk.soundPlaying = random.choice(ambientTalkAudios)
                    Talk.audioChannel = KDS.Audio.playSound(Talk.soundPlaying)
                Talk.lines.append(Talk.scheduled.pop(0))
                Talk.Conversation.newAnimation = True
                deleteCount = 0
                while len(Talk.lines) > 1000:
                    del Talk.lines[0]
                    deleteCount += 1
                if len(Talk.lines) - Talk.Conversation.scroll <= Talk.lineCount + auto_scroll_offset_index: Talk.Conversation.scrollToBottom()
                else: Talk.Conversation.scroll = max(Talk.Conversation.scroll - deleteCount, 0)
            elif len(Talk.scheduled) <= 0:
                for audio in ambientTalkAudios: audio.stop()
                Talk.audioChannel = None
        
        @staticmethod
        def render(mouse_pos: Tuple[int, int], clicked: bool):
            Talk.surface.fill((0, 0, 0, 0))
            pygame.draw.rect(Talk.surface, background_color, pygame.Rect(0, 0, Talk.surface_size[0], Talk.surface_size[1]), 0, conversation_border_radius)
            
            lastIncluded = False
            for i in range(Talk.Conversation.scroll, min(Talk.Conversation.scroll + Talk.lineCount + 1, len(Talk.lines))):
                text = Talk.lines[i]
                if text[:2] == Prefixes.player: prefix = Prefixes.Rendered.player
                else: prefix = Prefixes.Rendered.koponen
                offsetX = text_padding.left + prefix.get_width()
                offsetY = text_padding.top + (i - Talk.Conversation.scroll) * line_spacing
                Talk.surface.blit(text_font.render(text[2:], True, KDS.Colors.MidnightBlue), (offsetX, offsetY))
                if i - 1 < 0 or text[:2] != Talk.lines[i - 1][:2]: 
                    Talk.surface.blit(prefix, (text_padding.left, offsetY))
                
                if len(Talk.lines) - Talk.Conversation.scroll > Talk.lineCount + auto_scroll_offset_index: scrollToBottomButton.update(Talk.surface, mouse_pos, clicked)
                
                if i == len(Talk.lines) - 1: lastIncluded = True

            if len(Talk.lines) > 0:
                animationRectTarget = pygame.Rect(text_padding.left + (Prefixes.Rendered.player if Talk.lines[-1][:2] == Prefixes.player else Prefixes.Rendered.koponen).get_width(),
                                                text_padding.top + (len(Talk.lines) - 1 - Talk.Conversation.scroll) * line_spacing, text_font.size(Talk.lines[-1][2:])[0], text_font.get_height())
            else: animationRectTarget = pygame.Rect(0, 0, 0, 0)
                
            if Talk.Conversation.newAnimation:
                Talk.Conversation.newAnimation = False
                Talk.Conversation.animationProgress = 0.0
                Talk.Conversation.animationWidth = animationRectTarget.width
                
            if Talk.Conversation.animationProgress >= 1.0:
                Talk.Conversation.animationProgress = -1
            if Talk.Conversation.animationProgress != -1:
                Talk.Conversation.animationWidth = max(Talk.Conversation.animationWidth - line_reveal_speed, 0)
                Talk.Conversation.animationProgress = KDS.Math.Remap(Talk.Conversation.animationWidth, animationRectTarget.width, 0, 0, 1)
                if lastIncluded:
                    pygame.draw.rect(Talk.surface, background_color, pygame.Rect(animationRectTarget.x + (animationRectTarget.width - Talk.Conversation.animationWidth), animationRectTarget.y, Talk.Conversation.animationWidth, animationRectTarget.height))
            
            pygame.draw.rect(Talk.surface, background_outline_color, pygame.Rect(0, 0, Talk.surface_size[0], Talk.surface_size[1]), conversation_outline_width, conversation_border_radius)
            return Talk.surface

    @staticmethod
    def renderMenu(surface: pygame.Surface, mouse_pos: Tuple[int, int], clicked: bool):
        surface.blit(talk_background, (0, 0))
        surface.blit(talk_foreground, (40, 474))
        Talk.Conversation.update()
        surface.blit(Talk.Conversation.render(mouse_pos, clicked), conversation_rect.topleft)

    @staticmethod
    def start(window: pygame.Surface, surface: pygame.Surface, player_inventory, Fullscreen, ResizeWindow, KDS_Quit, clock: pygame.time.Clock, fps: int):
        global talk_foreground
        talk_foreground = talk_foregrounds[random.randint(0, len(talk_foregrounds) - 1)]
        surface_size = surface.get_size()
        Talk.running = True
        
        exit_button = KDS.UI.Button(pygame.Rect(940, 700, 230, 80))
        request_mission_button = KDS.UI.Button(pygame.Rect(50, 700, 450, 80))
        return_mission_button = KDS.UI.Button(pygame.Rect(510, 700, 420, 80), )
        date_button = KDS.UI.Button(pygame.Rect(50, 610, 450, 80), Date.start, "ASK FOR A DATE")
        
        while Talk.running:
            mouse_pos = (int((pygame.mouse.get_pos()[0] - conversation_rect.left - Fullscreen.offset[0]) / Fullscreen.scaling), int((pygame.mouse.get_pos()[1] - conversation_rect.top - Fullscreen.offset[1]) / Fullscreen.scaling))
            c = False
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_F11:
                        Fullscreen.Set()
                    elif event.key == K_F4:
                        if pygame.key.get_pressed()[K_LALT]:
                            KDS_Quit()
                    elif event.key == K_ESCAPE:
                        Talk.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        Talk.Conversation.scroll = max(Talk.Conversation.scroll - line_scroll_speed, 0)
                    elif event.button == 5:
                        Talk.Conversation.scroll = min(Talk.Conversation.scroll + line_scroll_speed, max(len(Talk.lines) - Talk.lineCount, 0))
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        c = True
                elif event.type == pygame.QUIT:
                    KDS_Quit()
                elif event.type == pygame.VIDEORESIZE:
                    ResizeWindow(event.size)

            Talk.renderMenu(surface, mouse_pos, c)
            window.blit(pygame.transform.scale(surface, (int(surface_size[0] * Fullscreen.scaling), int(surface_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
            pygame.display.update()
            window.fill(KDS.Colors.Black)
            clock.tick(fps)