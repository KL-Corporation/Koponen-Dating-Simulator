#region
import pygame
import KDS.Logging
import KDS.ConfigManager
from inspect import currentframe, getframeinfo
#endregion
#region init
pygame.init()

screen_size = (int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeX", str(600))), int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeY", str(400))))
screen = pygame.Surface(screen_size)
mission_font = pygame.font.Font("COURIER.ttf", 10, bold=0, italic=0)

Missions = []
Active_Mission = 0
Last_Active_Mission = 0
#endregion
#region Initialise
def InitialiseMission(Safe_Name: str, Visible_Name: str):
    """
    1. Safe_Name, A name that does not conflict with any other names.
    2. Visible_Name, The name that will be displayed as the task header.
    """
    global Missions
    New_Mission = []
    New_Mission.append(Safe_Name)
    New_Mission.append(Visible_Name)
    Missions.append(New_Mission)

def InitialiseTask(Mission_Name: str, Safe_Name: str, Visible_Name: str):
    """
    1. Mission_Name, The Safe_Name of the mission you want to add this task to.
    2. Safe_Name, A name that does not conflict with any other names.
    3. Visible_Name, The name that will be displayed as the task header.
    """
    global Missions
    New_Task = []
    New_Task.append(Safe_Name)
    New_Task.append(Visible_Name)
    New_Task.append(0.0)
    New_Task.append(False)
    for i in range(len(Missions)):
        if Missions[i][0] == Mission_Name:
            Missions[i].append(New_Task)

def SetProgress(Mission_Name: str, Task_Name: str, Add_Value: float):
    """
    1. Mission_Name, The Safe_Name of the mission your task is under.
    2. Task_Name, The Safe_Name of the task.
    3. Add_Value, The value that will be added to your task.
    """
    for i in range(len(Missions)):
        if Missions[i][0] == Mission_Name:
            for j in range(len(Missions[i])):
                if Missions[i][j][0] == Task_Name:
                    Missions[i][j][2] += Add_Value
                    if Missions[i][j][2] > 1.0:
                        Missions[i][j][3] = True

def GetRenderCount():
    len(Missions[Active_Mission])

#endregion