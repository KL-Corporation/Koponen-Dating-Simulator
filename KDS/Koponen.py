import os
import random
import pygame
from pygame.locals import *
import math
import KDS.Colors
import KDS.Convert
import KDS.Animator
import KDS.Audio
import KDS.UI
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
class text_padding:
    left = 5
    top = 5
    right = 5
    bottom = 5
#endregion

pygame.init()

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

    exit_button = KDS.UI.New.Button(pygame.Rect(940, 700, 230, 80), exit_function1, button_font1.render(
        "EXIT", True, KDS.Colors.White))
    mission_button = KDS.UI.New.Button(pygame.Rect(50, 700, 450, 80), mission_function, button_font1.render(
        "REQUEST MISSION", True, KDS.Colors.White))
    date_button = KDS.UI.New.Button(pygame.Rect(50, 610, 450, 80), date_function, button_font1.render(
        "ASK FOR A DATE", True, KDS.Colors.White))
    r_mission_button = KDS.UI.New.Button(pygame.Rect(510, 700, 420, 80), end_mission, button_font1.render(
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
talk_background = pygame.Surface((1, 1))
talk_foregrounds = [pygame.Surface((1, 1))]
talk_foreground = pygame.Surface((1, 1))

class Prefixes:
    player = text_font.render(f"ERROR: ", True, text_color)
    koponen = text_font.render("Koponen: ", True, text_color)

def init(playerName: str):
    global talk_background, talk_foregrounds, talk_foreground
    talk_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png").convert()
    for ad in os.listdir("Assets/Textures/KoponenTalk/ads"):
        talk_foregrounds.append(pygame.image.load(f"Assets/Textures/KoponenTalk/ads/{ad}").convert_alpha())
    random.shuffle(talk_foregrounds)
    talk_foreground = talk_foregrounds[0]
    Prefixes.player = text_font.render(f"{playerName}: ", True, KDS.Colors.White)

class Talk:
    running = False
    mask = pygame.mask.Mask(conversation_rect.size, True)
    surface = pygame.Surface(conversation_rect.size, pygame.SRCALPHA, masks=mask)
    surface_size = surface.get_size()
    lineCount = math.floor(surface.get_height() - text_padding.top - text_padding.bottom - text_font.size(" ")[1])
    
    class Line:
        
        def __init__(self, text, prefix: Prefixes and pygame.Surface, prefix_visible: bool = True) -> None:
            self.text = text_font.render(text, True, text_color)
            self.text_size = self.text.get_size()
            self.prefix = prefix
            self.prefix_visible = prefix_visible
            self.prefix_size = self.prefix.get_size()
            self.animationProgress = text_padding.left + self.prefix_size[0]
            self.animationFinished = False
            self.waitBeforeScroll = 0
            self.finished = False
        
        def update(self):
            tot_width = text_padding.left + self.prefix_size[0] + self.text_size[0]
            self.animationProgress += line_reveal_speed
            if self.animationProgress >= tot_width:
                self.animationProgress = tot_width
                self.animationFinished = True
                self.waitBeforeScroll += 1
                if self.waitBeforeScroll > min_time_before_scroll: self.finished = True
                
        def render(self, surface: pygame.Surface, y):
            surface.blit(self.prefix, (text_padding.left, y))
            surface.blit(self.text, (text_padding.left + self.prefix_size[0], y))
            pygame.draw.rect(surface, KDS.Colors.Red, pygame.Rect(self.animationProgress, y, self.text_size[0] - self.animationProgress, line_spacing))
        
    class Lines():
        scheduled = []
        active = []
        surface = pygame.Surface((conversation_rect.width - text_padding.left - text_padding.right, conversation_rect.height - text_padding.top - text_padding.bottom))
        surface_rect = pygame.Rect(conversation_rect.width - text_padding.left, text_padding.top, surface.get_width(), surface.get_height())
        
        @staticmethod
        def update():
            if (len(Talk.Lines.active) < 1 or Talk.Lines.active[-1].animationFinished) and len(Talk.Lines.scheduled) > 0 and len(Talk.Lines.active) < Talk.lineCount:
                Talk.Lines.active.append(Talk.Lines.scheduled.pop(0))
            return False
        
        @staticmethod
        def fromEnd(index: int, count: int = -1):
            count = count if count >= 0 else Talk.lineCount
            _from = KDS.Math.Clamp(index, 0, len(Talk.Lines.active) - 1)
            _to = KDS.Math.Clamp(_from + count, _from, len(Talk.Lines.active) - 1)
            Talk.Lines.active[_from:_to]
        
    class Conversation:
            
        @staticmethod
        def schedule(text, prefix: Prefixes and pygame.Surface):
            lineSplit = KDS.Convert.ToLines(text, text_font, Talk.Lines.surface_rect.width - prefix.get_width())
            for _text in lineSplit: 
                Talk.Lines.scheduled.append(Talk.Line(_text, prefix))
        
        @staticmethod
        def render():
            Talk.surface.fill((0, 0, 0, 0))
            pygame.draw.rect(Talk.surface, background_color, pygame.Rect(0, 0, Talk.surface_size[0], Talk.surface_size[1]), 0, conversation_border_radius)
            
            Talk.Lines.update()
            
            pygame.draw.rect(Talk.surface, background_outline_color, pygame.Rect(0, 0, Talk.surface_size[0], Talk.surface_size[1]), conversation_outline_width, conversation_border_radius)
            
            return Talk.surface

    @staticmethod
    def renderMenu(surface: pygame.Surface, mouse_pos: tuple[int, int], clicked: bool):
        surface.blit(talk_background, (0, 0))
        surface.blit(talk_foreground, (40, 474))
        surface.blit(Talk.Conversation.render(), conversation_rect.topleft)
        
            
    @staticmethod
    def start(window: pygame.Surface, surface: pygame.Surface, Fullscreen, ResizeWindow, KDS_Quit, clock: pygame.time.Clock, fps: int):
        global talk_foreground
        talk_foreground = talk_foregrounds[random.randint(0, len(talk_foregrounds) - 1)]
        surface_size = surface.get_size()
        Talk.running = True
        while Talk.running:
            mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int((pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
            c = False
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_F11:
                        Fullscreen.Set()
                    elif event.key == K_F4:
                        if pygame.key.get_pressed()[K_LALT]:
                            KDS_Quit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        pass #Up
                    elif event.button == 5:
                        pass #Down
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        c = True
                elif event.type == pygame.QUIT:
                    KDS_Quit()
                elif event.type == pygame.VIDEORESIZE:
                    ResizeWindow(event.size)
                
                
            Talk.renderMenu(surface, mouse_pos, False)
            window.blit(pygame.transform.scale(surface, (int(surface_size[0] * Fullscreen.scaling), int(surface_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
            pygame.display.update()
            window.fill(KDS.Colors.Black)
            clock.tick(fps)
    
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)
Talk.Conversation.schedule("testosteroni teksti juttu hommeli homma testi hommeli homma", Prefixes.player)