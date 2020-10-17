#region Importing
import math
import os
import pygame
import KDS.Animator
import KDS.ConfigManager
import KDS.Colors
import KDS.Convert
import KDS.Gamemode
import KDS.Logging
import KDS.Math
from inspect import currentframe

#endregion
#region Settings
MissionColor = (128, 128, 128)
MissionFinishedColor = (0, 128, 0)
MissionUnFinishedColor = (128, 0, 0)
TaskColor = (70, 70, 70)
TaskFinishedColor = (0, 70, 0)
TaskUnFinishedColor = (70, 0, 0)
TaskAnimationDuration = 30
MissionAnimationDuration = 60
MissionWaitTicks = 120
AnimationType = KDS.Animator.AnimationType.Linear
TextOffset = 2
HeaderHeight = 25
TaskHeight = 10
class Padding:
    left = 10
    top = 5
    right = 10
    bottom = 5
MissionFont = pygame.font.Font("Assets/Fonts/courier.ttf", 15, bold=1, italic=0)
TaskFont = pygame.font.Font("Assets/Fonts/courier.ttf", 10, bold=0, italic=0)
TaskFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_finish.ogg")
TaskUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_unfinish.ogg")
MissionFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_finish.ogg")
MissionUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_unfinish.ogg")
#endregion
#region Listeners
class Listener:
    def __init__(self) -> None:
        self.listenerList = []
        
    def Add(self, MissionName: str, TaskName: str, AddValue: float):
        self.listenerList.append((MissionName, TaskName, AddValue))
        
    def Trigger(self):
        for listnr in self.listenerList:
            AddProgress(listnr[0], listnr[1], listnr[2])

Listeners = { "InventorySlotSwitching": Listener(), 
             "Movement": Listener(), 
             "KoponenTalk": Listener(), 
             "iPuhelinPickup": Listener(), 
             "iPuhelinDrop": Listener(),
             "LevelEnder": Listener()
            }
class ListenerTypes:
    InventorySlotSwitching = "InventorySlotSwitching"
    Movement = "Movement"
    KoponenTalk = "KoponenTalk"
    iPuhelinPickup = "iPuhelinPickup"
    iPuhelinDrop = "iPuhelinDrop"
    LevelEnder = "LevelEnder"
#endregion
#region Classes
class Task:
    def __init__(self, missionName: str, safeName: str, text: str, *ListenerData: tuple[ListenerTypes or str, float]) -> None:
        global Missions
        self.safeName = safeName
        self.text = text
        self.renderedText = TaskFont.render(self.text, True, KDS.Colors.GetPrimary.White)
        self.renderedTextSize = self.renderedText.get_size()
        self.progress = 0.0
        self.progressScaled = 0
        self.finished = False
        self.lastFinished = False
        self.color = KDS.Animator.Color(TaskColor, TaskFinishedColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        Missions.GetMission(missionName).AddTask(safeName, self)
        
    def Progress(self, Value: float, Add: bool = False):
        if Add: self.progress += Value
        else: self.progress = Value
        if self.progress >= 1.0:
            self.finished = True
            self.progress = 1.0
        else: 
            self.finished = False
            if self.progress < 0.0: self.progress = 0.0
        self.progressScaled = math.floor(self.progress * 100)
        
    def Update(self, Width: int, Height: int, PlaySound: bool = True):
        surface = pygame.Surface((Width, Height))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, (Padding.left, round((Height / 2) - (self.renderedTextSize[1] / 2))))
        surface.blit(TaskFont.render(f"{self.progressScaled}%", True, KDS.Colors.GetPrimary.White), (Width - Padding.right - hundredSize[0], round((Height / 2) - (self.renderedTextSize[1] / 2))))
        if self.finished != self.lastFinished:
            if self.finished:
                if PlaySound:
                    Audio.playSound(TaskFinishSound)
                self.color.changeValues(TaskColor, TaskFinishedColor)
            else:
                if PlaySound:
                    Audio.playSound(TaskUnFinishSound)
                self.color.changeValues(TaskColor, TaskUnFinishedColor)
        self.lastFinished = self.finished
        return surface

class Mission:
    def __init__(self, safeName: str, text: str) -> None:
        global Missions
        self.safeName = safeName
        self.text = text
        self.renderedText = MissionFont.render(self.text, True, KDS.Colors.GetPrimary.White)
        self.textSize = self.renderedText.get_size()
        self.tasks: dict[str, Task] = {}
        self.task_keys: list[str] = []
        self.task_values: list[Task] = []
        self.finished = False
        self.lastFinished = False
        self.finishedTicks = 0
        self.trueFinished = False
        self.color = KDS.Animator.Color(MissionColor, MissionFinishedColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        self.playSound = True
        Missions.AddMission(self.safeName, self)
        
    def AddTask(self, safeName: str, task: Task):
        if safeName not in self.tasks:
            self.tasks[safeName] = task
            self.task_keys = safeName
            self.task_values.append(self.tasks[safeName])
        else: KDS.Logging.AutoError("SafeName is already occupied!", currentframe())
        
    def GetTask(self, safeName: str):
        if safeName in self.tasks: return self.tasks[safeName]
        else: return None
    
    def GetTaskList(self):
        return self.task_values
    
    def GetKeyList(self):
        return self.task_keys
    
    def GetTaskByValue(self, value):
        return self.tasks[self.task_keys[self.task_values.index(value)]]
    
    def Update(self):
        self.finished = True
        self.playSound = False
        notFinished = 0
        for task in self.task_values:
            if not task.finished:
                self.finished = False
                notFinished += 1
                
            if notFinished > 1:
                self.playSound = True
                del notFinished
                break

        if self.finished:
            self.finishedTicks += 1
        else:
            self.trueFinished = False
            self.finishedTicks = 0
            
        if self.finishedTicks > MissionWaitTicks:
            self.trueFinished = True
            self.finishedTicks = MissionWaitTicks
        
        if self.lastFinished != self.finished:
            if self.finished:
                Audio.playSound(MissionFinishSound)
                self.color.changeValues(MissionColor, MissionFinishedColor)
            else:
                Audio.playSound(MissionUnFinishSound)
                self.color.changeValues(MissionColor, MissionUnFinishedColor)
        self.lastFinished = self.finished
    
    def Render(self, Width: int, Height: int):
        surface = pygame.Surface((Width, Height))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, ((Width / 2) - (self.textSize[0] / 2), (HeaderHeight / 2) - (self.textSize[1] / 2)))
        _taskHeight = TaskHeight + Padding.top + Padding.bottom
        i = 0
        for task in self.task_values:
            surface.blit(task.Update(Width, _taskHeight, self.playSound), (0, HeaderHeight + (i * _taskHeight)))
            i += 1
        return surface

class MissionHolder:
    def __init__(self) -> None:
        self.missions: dict[str, Mission] = {}
        self.mission_keys: list[str] = []
        self.mission_values: list[Mission] = []
        self.finished = False
        
    def GetMission(self, safeName: str):
        if safeName in self.missions: return self.missions[safeName]
        else: return None
    
    def GetMissionList(self):
        return self.mission_values
    
    def GetKeyList(self):
        return self.mission_keys
    
    def GetMissionByValue(self, value):
        return self.missions[self.mission_keys[self.mission_values.index(value)]]
    
    def AddMission(self, safeName: str, mission: Mission):
        if safeName not in self.missions:
            self.missions[safeName] = mission
            self.mission_keys.append(safeName)
            self.mission_values.append(self.missions[safeName])
        else: KDS.Logging.AutoError("SafeName is already occupied!", currentframe())
    
    def GetMaxWidth(self):
        maxWidth = 0
        for mission in self.mission_values:
            for task in mission.task_values:
                maxWidth = max(maxWidth, task.renderedTextSize[0])
        return maxWidth

Missions = MissionHolder()     
#endregion
#region init
Audio = None
pygame.init()
def init(AudioClass):
    global Audio
    Audio = AudioClass

Active_Mission = None
Last_Active_Mission = 0
text_height = 0
TextOffset = int(TaskFont.size(" ")[0] * TextOffset)
hundredSize = TaskFont.size("100%")
#endregion
#region Initialize
def InitialiseMission(SafeName: str, Text: str):
    """Initialises a mission.

    Args:
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
    """
    Mission(SafeName, Text)
        
def InitialiseTask(MissionName: str, SafeName: str, Text: str, *ListenerData: tuple[ListenerTypes or str, float]):
    """Initialises a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission you want to add this task to.
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
        Listener (ListenerTypes, optional): A custom listener that will add a certain amount of progress when triggered. Defaults to None.
        ListenerAddProgress (float, optional): The amount of progress that will be added when the listener is triggered. Defaults to 0.0.
    """
    Task(MissionName, SafeName, Text)
    for data in ListenerData:
        Listeners[data[0]].Add(MissionName, SafeName, data[1])
#endregion
#region Progress
def Render(surface: pygame.Surface):
    global Missions, Active_Mission
    maxWidth = Missions.GetMaxWidth()
    maxWidth += Padding.left + Padding.right + TextOffset + hundredSize[0]
    Active_Mission = None
    for mission in Missions.GetMissionList():
        mission.Update()
        if not mission.trueFinished:
            Active_Mission = mission.safeName
            break
    if Active_Mission == None: Missions.finished = True
    else: Missions.finished = False
    if not Missions.finished:
        surface.blit(Missions.GetMission(Active_Mission).Render(maxWidth, HeaderHeight + ((TaskHeight + Padding.top + Padding.bottom) * len(Missions.GetMission(Active_Mission).GetTaskList()))), (surface.get_width() - maxWidth, 0))

def SetProgress(MissionName: str, TaskName: str, SetValue: float):
    """Sets a specified amount of progress to a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission your task is under.
        Task_Name (str): The Safe_Name of the task.
        Set_Value (float): The value that will be set to your task's progress.
    """
    var = Missions.GetMission(MissionName)
    if var != None: 
        var = var.GetTask(TaskName)
        if var != None: var.Progress(SetValue)
    
def AddProgress(MissionName: str, TaskName: str, AddValue: float):
    """Adds a specified amount of progress to a task.

    Args:
        Mission_Name (str): The Safe_Name of the mission your task is under.
        Task_Name (str): The Safe_Name of the task.
        Add_Value (float): The value that will be added to your task's progress.
    """
    var = Missions.GetMission(MissionName)
    if var != None: 
        var = var.GetTask(TaskName)
        if var != None: var.Progress(AddValue, True)
#endregion
#region MissionHolder Functions
def GetFinished():
    return Missions.finished
def SetFinished(MissionName: str):
    global Missions
    for task in Missions.GetMission(MissionName).GetTaskList():
        task.Progress(100)
def Clear():
    global Missions
    del Missions
    Missions = MissionHolder()
def Finish():
    global Missions
    for _mission in Missions.GetMissionList():
        for _task in _mission.GetTaskList():
            _task.Progress(100)
#endregion
#region Missions
def InitialiseMissions(LevelIndex):
    Clear()
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
        InitialiseMission("tutorial", "Tutoriaali")
        InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", (ListenerTypes.Movement, 0.005))
        InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (ListenerTypes.InventorySlotSwitching, 0.2))
        InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
        InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q", (ListenerTypes.iPuhelinDrop, 1.0), (ListenerTypes.iPuhelinPickup, -1.0))

        InitialiseMission("koponen_introduction", "Tutustu Koposeen")
        InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", (ListenerTypes.KoponenTalk, 1.0))
    else:
        if LevelIndex < 2:
            InitialiseMission("tutorial", "Tutoriaali")
            InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", (ListenerTypes.Movement, 0.005))
            InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (ListenerTypes.InventorySlotSwitching, 0.2))
            InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
            InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q", (ListenerTypes.iPuhelinDrop, 1.0), (ListenerTypes.iPuhelinPickup, -1.0))

            InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", (ListenerTypes.KoponenTalk, 1.0))
        elif LevelIndex == 2:
            InitialiseMission("koponen_talk", "Puhu Koposelle")
            InitialiseTask("koponen_talk", "talk", "Puhu Koposelle", (ListenerTypes.KoponenTalk, 1.0))
        elif LevelIndex == 6:
            InitialiseMission("tutorial", "Tutoriaali")
            InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", (ListenerTypes.Movement, 0.005))
            InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (ListenerTypes.InventorySlotSwitching, 0.2))
            InitialiseTask("tutorial", "fart", "Piere painamalla: F, kun staminasi on 100")
            InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q", (ListenerTypes.iPuhelinDrop, 1.0), (ListenerTypes.iPuhelinPickup, -1.0))

            InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", (ListenerTypes.KoponenTalk, 1.0))
        else:
            InitialiseMission("reach_level_exit", "Exit")
            InitialiseTask("reach_level_exit", "exit", "Reach Level Exit", (ListenerTypes.LevelEnder, 1.0))
#endregion
#region Listeners
def TriggerListener(Type: ListenerTypes or str):
    global Listeners
    if Type in Listeners:
        Listeners[Type].Trigger()
    else: KDS.Logging.AutoError("Listener Type not valid!", currentframe())
#endregion