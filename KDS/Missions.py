#region Importing
import pygame
import KDS.Animator
import KDS.ConfigManager
import KDS.Convert
import KDS.Gamemode
import KDS.Logging
from inspect import currentframe
#endregion
#region Settings
HeaderColor = (128, 128, 128)
BackgroundColor = (70, 70, 70)
BackgroundFinishedColor = (0, 70, 0)
textOffset = 2
#endregion
#region init
pygame.init()

mission_font = pygame.font.Font("Assets/Fonts/courier.ttf", 15, bold=1, italic=0)
task_font = pygame.font.Font("Assets/Fonts/courier.ttf", 10, bold=0, italic=0)

Missions = list()
Active_Mission = 0
Last_Active_Mission = 0
text_height = 0
textOffsetString = ""
for i in range(textOffset):
    textOffsetString += " "
Missions_Finished = False
#endregion
#region Listeners
InventorySlotSwitching_Listeners = []
Movement_Listeners = []
KoponenTalk_Listeners = []
#endregion
#region Initialize
def InitialiseMission(Safe_Name: str, Visible_Name: str):
    """Initialises a mission.

    Args:
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
    """
    global Missions
    New_Mission = [Safe_Name, Visible_Name]
    Missions.append(New_Mission)

def InitialiseTask(Mission_Name: str, Safe_Name: str, Visible_Name: str, Listener=None, ListenerAddProgress=0.0):
    """Initialises a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission you want to add this task to.
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
        Listener (ListenerTypes, optional): A custom listener that will add a certain amount of progress when triggered. Defaults to None.
        ListenerAddProgress (float, optional): The amount of progress that will be added when the listener is triggered. Defaults to 0.0.
    """
    global Missions, InventorySlotSwitching_Listeners, Movement_Listeners, KoponenTalk_Listeners
    for j in range(len(Missions)):
        if Missions[j][0] == Mission_Name:
            Missions[j].append([Safe_Name, Visible_Name, 0.0, False, (255, 255, 255), KDS.Animator.Float(0.0, 1.0, 3, KDS.Animator.Float.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)])
            break
    if Listener != None:
        if Listener == ListenerTypes.InventorySlotSwitching:
            InventorySlotSwitching_Listeners.append([Mission_Name, Safe_Name, ListenerAddProgress])
        elif Listener == ListenerTypes.Movement:
            Movement_Listeners.append([Mission_Name, Safe_Name, ListenerAddProgress])
        elif Listener == ListenerTypes.KoponenTalk:
            KoponenTalk_Listeners.append([Mission_Name, Safe_Name, ListenerAddProgress])

def DeleteAll():
    global Missions
    Missions = list()
#endregion
#region Progress
def Progress(Mission_Name: str, Task_Name: str, Value: float, Add: bool):
    """Do not use this, please.
    """
    global Active_Mission, Missions_Finished
    for i in range(len(Missions)):
        if Missions[i][0] == Mission_Name:
            for j in range(2, len(Missions[i])):
                if Missions[i][j][0] == Task_Name:
                    if Add:
                        Missions[i][j][2] += Value
                    else:
                        Missions[i][j][2] = Value
                    if Missions[i][j][2] >= 1.0:
                        Missions[i][j][3] = True
                        #Play audio?
                        break
            break
    All_Tasks_Done = True
    while All_Tasks_Done and not Missions_Finished:
        for i in range(len(Missions[Active_Mission]) - 2):
            if All_Tasks_Done == True:
                All_Tasks_Done = KDS.Convert.ToBool(Missions[Active_Mission][i + 2][3])
            else:
                break
        if All_Tasks_Done:
            if Active_Mission + 1 < len(Missions[Active_Mission]) - 2:
                Active_Mission += 1
            else:
                Missions_Finished = True
def SetProgress(Mission_Name: str, Task_Name: str, Set_Value: float):
    """Sets a specified amount of progress to a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission your task is under.
        Task_Name (str): The Safe_Name of the task.
        Set_Value (float): The value that will be set to your task's progress.
    """
    Progress(Mission_Name, Task_Name, Set_Value, False)
def AddProgress(Mission_Name: str, Task_Name: str, Add_Value: float):
    """Adds a specified amount of progress to a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission your task is under.
        Task_Name (str): The Safe_Name of the task.
        Add_Value (float): The value that will be added to your task's progress.
    """
    Progress(Mission_Name, Task_Name, Add_Value, True)
#endregion
#region Render
def GetRenderCount():
    global Missions, Active_Mission
    return len(Missions[Active_Mission]) - 2
def GetMaxWidth():
    global task_font, mission_font
    Max_Text_Width, temp = mission_font.size(Missions[Active_Mission][1])
    for i in range(len(Missions[Active_Mission]) - 2):
        Max_Text_Width = max(Max_Text_Width, task_font.size(Missions[Active_Mission][i + 2][1] + textOffsetString + str(100))[0])
    return Max_Text_Width
def RenderMission(surface: pygame.Surface):
    global Missions, mission_font, BackgroundColor, Active_Mission, HeaderColor
    rendered = mission_font.render(Missions[Active_Mission][1], True, (255, 255, 255))
    text_width = mission_font.size(Missions[Active_Mission][1])[0]
    MaxWidth = GetMaxWidth()
    screen_width = surface.get_width()
    pygame.draw.rect(surface, HeaderColor, (screen_width - MaxWidth, 0, MaxWidth, 20))
    surface.blit(rendered, (screen_width - MaxWidth + ((MaxWidth / 2) - (text_width / 2)), 3.75))
class ValueType:
    Background = 0
    Text = 1
    Progress = 2
def RenderTask(surface: pygame.Surface, index: int):
    global task_font, Missions, text_height, BackgroundColor, BackgroundFinishedColor
    index_var = index + 2
    Mission_Progress = Missions[Active_Mission][index_var][2]
    if Mission_Progress > 1.0:
        Mission_Progress = 1.0
    Mission_Progress = Mission_Progress * 100
    Mission_Progress = str(int(round(Mission_Progress)))
    task_rendered = task_font.render(Missions[Active_Mission][index_var][1], True, (255, 255, 255))
    progress_rendered = task_font.render(Mission_Progress, True, (255, 255, 255))
    text_height = task_font.size(Missions[Active_Mission][index_var][1])[1]
    progress_width = task_font.size(Mission_Progress)[0]
    if Missions[Active_Mission][index_var][2] >= 1.0:
        task_color = BackgroundFinishedColor
    else:
        task_color = BackgroundColor
    if task_color != Missions[Active_Mission][index_var][4]:
        fade = Missions[Active_Mission][index_var][5].update()
        if fade == 1.0:
            draw_color = task_color
            Missions[Active_Mission][index_var][4] = task_color
        else:
            draw_color = (task_color[0] + ((Missions[Active_Mission][index_var][4][0] - task_color[0]) * fade), task_color[1] + ((Missions[Active_Mission][index_var][4][1] - task_color[1]) * fade), task_color[2] + ((Missions[Active_Mission][index_var][4][2] - task_color[2]) * fade))
    else:
        draw_color = task_color
    Max_Text_Width = GetMaxWidth()
    surface_size = surface.get_size()
    backgroundRect = (surface_size[0] - Max_Text_Width, 20 + ((text_height + 5) * index), Max_Text_Width, text_height + 5)
    taskpos = (surface_size[0] - Max_Text_Width, 22.5 + ((text_height + 5) * index))
    progresspos = (surface_size[0] - progress_width, 22.5 + ((text_height + 5) * index))

    pygame.draw.rect(surface, draw_color, backgroundRect)
    surface.blit(task_rendered, taskpos)
    surface.blit(progress_rendered, progresspos)
#endregion
#region Missions
def InitialiseMissions(LevelIndex):
    DeleteAll()
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
        InitialiseMission("tutorial", "Tutoriaali")
        InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", ListenerTypes.Movement, 0.005)
        InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", ListenerTypes.InventorySlotSwitching, 0.2)
        InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
        InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q")

        InitialiseMission("koponen_introduction", "Tutustu Koposeen")
        InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", ListenerTypes.KoponenTalk, 1.0)
    elif KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
        if LevelIndex < 2:
            InitialiseMission("tutorial", "Tutoriaali")
            InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", ListenerTypes.Movement, 0.005)
            InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", ListenerTypes.InventorySlotSwitching, 0.2)
            InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
            InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q")

            InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", ListenerTypes.KoponenTalk, 1.0)
        elif LevelIndex == 2:
            InitialiseMission("koponen_talk", "Puhu Koposelle")
            InitialiseTask("koponen_talk", "talk", "Puhu Koposelle", ListenerTypes.KoponenTalk, 1.0)
        elif LevelIndex == 6:
            InitialiseMission("tutorial", "Tutoriaali")
            InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", ListenerTypes.Movement, 0.005)
            InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", ListenerTypes.InventorySlotSwitching, 0.2)
            InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
            InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q")

            InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", ListenerTypes.KoponenTalk, 1.0)
        else:
            InitialiseMission("mission_error", "ERROR! Mission loaded incorrectly.")
            InitialiseTask("mission_error", "task_error", "ERROR! Task loaded incorrectly.")
#endregion
#region Data
def GetFinished():
    return Missions_Finished
#endregion
#region Listeners
class ListenerTypes:
    InventorySlotSwitching = "InventorySlotSwitching"
    Movement = "Movement"
    KoponenTalk = "KoponenTalk"

def TriggerListener(Type):
    global InventorySlotSwitching_Listeners, Movement_Listeners, KoponenTalk_Listeners
    ListenerList = None
    if Type == ListenerTypes.InventorySlotSwitching:
        ListenerList = InventorySlotSwitching_Listeners
    elif Type == ListenerTypes.Movement:
        ListenerList = Movement_Listeners
    elif Type == ListenerTypes.KoponenTalk:
        ListenerList = KoponenTalk_Listeners
    if ListenerList != None:
        for listener in ListenerList:
            AddProgress(listener[0], listener[1], listener[2])
    else:
        KDS.Logging.AutoError("Listener Type not valid!", currentframe())
#endregion