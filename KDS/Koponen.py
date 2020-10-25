import pygame
from pygame.locals import *

talk_running = False

"""
def koponen_talk():
    global main_running, currently_on_mission, player_score, ad_images, koponen_talking_background, koponen_talking_foreground_indexes, koponenTalking
    conversations = []

    KDS.Missions.KoponenTalk.Trigger()

    koponenTalking = True
    pygame.mouse.set_visible(True)

    c = False

    for i in range(len(koponen_talking_foreground_indexes), 0):
        koponen_talking_foreground_indexes[i] = koponen_talking_foreground_indexes[i - 1]
    random_foreground = int(random.uniform(0, len(ad_images)))
    while random_foreground in koponen_talking_foreground_indexes
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
"""

def koponen_talk():
    