import os
import random
import pygame
from pygame.draw import lines
from pygame.locals import *
import KDS.Colors
import KDS.Animator
import KDS.Audio
import KDS.UI

#region Settings
text_font = pygame.font.Font("Assets/Fonts/courier.ttf", 30, bold=0, italic=0)
text_color = KDS.Colors.Get.MidnightBlue
background_color = KDS.Colors.Get.CloudWhite
background_outline_color = KDS.Colors.Get.MidnightBlue
conversation_rect = pygame.Rect(40, 40, 700, 400)
conversation_outline_width = 3
conversation_border_radius = 10
line_reveal_duration = 30 #ticks
min_time_before_scroll = 120 #ticks
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
        "EXIT", True, KDS.Colors.GetPrimary.White))
    mission_button = KDS.UI.New.Button(pygame.Rect(50, 700, 450, 80), mission_function, button_font1.render(
        "REQUEST MISSION", True, KDS.Colors.GetPrimary.White))
    date_button = KDS.UI.New.Button(pygame.Rect(50, 610, 450, 80), date_function, button_font1.render(
        "ASK FOR A DATE", True, KDS.Colors.GetPrimary.White))
    r_mission_button = KDS.UI.New.Button(pygame.Rect(510, 700, 420, 80), end_mission, button_font1.render(
        "RETURN MISSION", True, KDS.Colors.GetPrimary.White))

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

def init():
    global talk_background, talk_foregrounds, talk_foreground
    talk_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png").convert()
    for ad in os.listdir("Assets/Textures/KoponenTalk/ads"):
        talk_foregrounds.append(pygame.image.load(f"Assets/Textures/KoponenTalk/ads/{ad}").convert_alpha())
    random.shuffle(talk_foregrounds)
    talk_foreground = talk_foregrounds[0]

class Talk:
    running = False
    class Conversation:
        surface = pygame.Surface(conversation_rect.size, pygame.SRCALPHA)
        surface_size = surface.get_size()
        
        class ConversationLine:
            def __init__(self, text) -> None:
                self.text = text_font.render(text, True, text_color)
                self.text_size = self.text.get_size()
                self.animationProgress = KDS.Animator.Float(0, Talk.Conversation.surface_size[0], line_reveal_duration, KDS.Animator.AnimationType.EaseIn, KDS.Animator.OnAnimationEnd.Stop)
                self.animationFinished = False
                self.waitBeforeScroll = 0
                self.finished = False
                
            def update(self):
                self.animationProgress.update()
                
            def render(self, surface: pygame.Surface):
                surface.blit(self.text, (0, 0))
        
        lines: list[ConversationLine] = []
        
        @staticmethod
        def schedule(text):
            lines.append(Talk.Conversation.ConversationLine(text))
        
        @staticmethod
        def render():
            surface = Talk.Conversation.surface
            surface.fill((0, 0, 0, 0))
            surface_size = surface.get_size()
            pygame.draw.rect(surface, background_color, pygame.Rect(0, 0, surface_size[0], surface_size[1]), 0, conversation_border_radius)
            pygame.draw.rect(surface, background_outline_color, pygame.Rect(0, 0, surface_size[0], surface_size[1]), conversation_outline_width, conversation_border_radius)
            return surface

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
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        c = True
                elif event.type == pygame.QUIT:
                    KDS_Quit()
                elif event.type == pygame.VIDEORESIZE:
                    ResizeWindow(event.size)
                
                
            Talk.renderMenu(surface, (0, 0), False)
            window.blit(pygame.transform.scale(surface, (int(surface_size[0] * Fullscreen.scaling), int(surface_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
            pygame.display.update()
            window.fill(KDS.Colors.GetPrimary.Black)
            clock.tick(fps)