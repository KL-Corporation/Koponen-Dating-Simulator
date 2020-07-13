#region
import pygame
import KDS.ConfigManager
import KDS.Convert
import KDS.Logging
from inspect import currentframe, getframeinfo
#endregion
#region init
pygame.init()

screen_size = (int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeX", str(600))), int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeY", str(400))))
mission_font = pygame.font.Font("COURIER.ttf", 10, bold=0, italic=0)

Missions = []
Active_Mission = 0
Last_Active_Mission = 0
Max_Text_Width = 0
text_height = 0
BackgroundColor = (70, 70, 70)
BackgroundFinishedColor = (0, 70, 0)

#endregion
#region Initialise
def InitialiseMission(Safe_Name: str, Visible_Name: str):
    """
    1. Safe_Name, A name that does not conflict with any other names.
    2. Visible_Name, The name that will be displayed as the task header.
    """
    global Missions
    New_Mission = [Safe_Name, Visible_Name]
    Missions.append(New_Mission)

def InitialiseTask(Mission_Name: str, Safe_Name: str, Visible_Name: str):
    """
    1. Mission_Name, The Safe_Name of the mission you want to add this task to.
    2. Safe_Name, A name that does not conflict with any other names.
    3. Visible_Name, The name that will be displayed as the task header.
    """
    global Missions
    New_Task = [Safe_Name, Visible_Name, 0.0, False]
    for i in range(len(Missions)):
        if Missions[i][0] == Mission_Name:
            Missions[i].append(New_Task)
#endregion
#region Set
def SetProgress(Mission_Name: str, Task_Name: str, Add_Value: float):
    """
    1. Mission_Name, The Safe_Name of the mission your task is under.
    2. Task_Name, The Safe_Name of the task.
    3. Add_Value, The value that will be added to your task.
    """
    global Active_Mission
    for i in range(len(Missions)):
        if Missions[i][0] == Mission_Name:
            for j in range(len(Missions[i]) - 2):
                j_var = j + 2
                if Missions[i][j_var][0] == Task_Name:
                    Missions[i][j_var][2] += Add_Value
                    if Missions[i][j_var][2] >= 1.0:
                        Missions[i][j_var][3] = True
                        #Play audio?
    All_Tasks_Done = True
    while All_Tasks_Done == True:
        for i in range(len(Missions[Active_Mission]) - 2):
            if All_Tasks_Done == True:
                All_Tasks_Done = KDS.Convert.ToBool(Missions[Active_Mission][i + 2][3])
        if All_Tasks_Done:
            if Active_Mission + 1 < len(Missions[Active_Mission]) - 2:
                Active_Mission += 1
            else:
                KDS.Logging.Log(KDS.Logging.LogType.error, "No ending for tasks done yet...", True)
#endregion
#region Render
def GetRenderCount():
    global Missions, Active_Mission
    return len(Missions[Active_Mission]) - 2

def RenderTask(index):
    global mission_font, Missions, Max_Text_Width, text_height, BackgroundColor, BackgroundFinishedColor
    index_var = index + 2
    Mission_Progress = Missions[Active_Mission][index_var][2]
    if Mission_Progress > 1.0:
        Mission_Progress = 1.0
    Mission_Progress = Mission_Progress * 100
    Mission_Progress = str(int(round(Mission_Progress)))
    for i in range(len(Missions[Active_Mission]) - 2):
        if i == 0:
            Max_Text_Width = 0
        tempVar = i + 2
        temp_width, temp_height = mission_font.size(Missions[Active_Mission][tempVar][1] + "   " + Mission_Progress)
        if Max_Text_Width < temp_width:
            Max_Text_Width = temp_width
    rendered = mission_font.render(Missions[Active_Mission][index_var][1] + "   " + Mission_Progress, True, (255, 255, 255))
    text_width, text_height = mission_font.size(Missions[Active_Mission][index_var][1] + "   " + Mission_Progress)
    if Missions[Active_Mission][index_var][2] >= 1.0:
        Color = BackgroundFinishedColor
    else:
        Color = BackgroundColor
    return rendered, screen_size[0] - text_width, 5 + ((text_height + 5) * index), Color, ((text_height + 5) * index), Max_Text_Width, text_height + 5
#endregion