import pygame
import KDS.Logging
import KDS.ConfigManager
from inspect import currentframe, getframeinfo

Active_Missions = [0]
Missions_Not_Returned = [0]
Safe_Names = []
Names = []
Messages = []
Koponen_Says = []
Koponen_Repeats = []
Koponen_Completes = []
Koponen_Interactables = []
Mission_Progress = []
Mission_Finished = []

pygame.init()

screen_size = (int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeX", str(600))), int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeY", str(400))))
screen = pygame.Surface(screen_size)
mission_font = pygame.font.Font("gamefont2.ttf", 10, bold=0, italic=0)

def InitialiseMission(Safe_Name: str, Name: str, Message: str, Koponen_Interactable: bool, Koponen_Say: str = "", Koponen_Repeat: str = ""):
    """
    1. Safe Name (string): A name that does not conflict with any other mission name.
    2. Name (string): Public name of the mission.
    3. Message (string): What will be the message in the mission card.
    4. Koponen Say (string): What Koponen says when giving the mission.
    5. Koponen Repeat (string): What Koponen says when asked about the mission the second time
    6. Koponen Interactable (bool): Determines if the mission is in any way associated with Koponen.
    """

    global Safe_Names, Names, Messages, Koponen_Says, Koponen_Repeats, Koponen_Interactables, Mission_Progress, Mission_Finished

    Safe_Names.append(Safe_Name)
    Names.append(Name)
    Messages.append(Message)
    Koponen_Interactables.append(Koponen_Interactable)
    Koponen_Says.append(Koponen_Say)
    Koponen_Repeats.append(Koponen_Repeat)
    Mission_Progress.append(0.0)
    Mission_Finished.append(False)

def SetMission_Progress(identifier, progress: float):
    """
    Identifierin tyyppi tarkistetaan priorisoimalla ensin index ja sitten safeName.
    """

    global Safe_Names, Names, Messages, Koponen_Says, Koponen_Repeats, Koponen_Interactables, Mission_Progress, Mission_Finished
    if isinstance(identifier, int):
        Mission_Progress[identifier] += progress
        if Mission_Progress[identifier] >= 1.0:
            Mission_Finished[identifier] = True
    elif isinstance(identifier, str):
        if identifier in Safe_Names:
            for i in range(len(Safe_Names)):
                if Safe_Names[i] == identifier:
                    Mission_Progress[i] += progress
                    if Mission_Progress[i] >= 1.0:
                        Mission_Finished[i] = True
        else:
            frameinfo = getframeinfo(currentframe())
            KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ") Identifier could not be processed.", False)
    else:
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ") Identifier could not be processed.", False)

def Update_Missions():
    for i in range(len(Safe_Names)):
        itemTip = mission_font.render("Koponen on raiskannut kymmenen ihmistä", True, (255, 255, 255))
        screen.blit(itemTip, (50, 50))