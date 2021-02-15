#region Importing
from typing import Dict, Iterable, List, Tuple, Union
import json

import pygame

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.ConfigManager
import KDS.Convert
import KDS.Gamemode
import KDS.Koponen
import KDS.Logging
import KDS.Math

#endregion
#region Initialisation
with open ("Assets/Textures/build.json", "r") as f:
    data = f.read()
buildData = json.loads(data)
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
#endregion
#region Listeners
class Listener:
    def __init__(self) -> None:
        self.listenerList: List[Tuple[str, str, float]] = []
        
    def Add(self, MissionName: str, TaskName: str, AddValue: float):
        self.listenerList.append((MissionName, TaskName, AddValue))
        
    def Trigger(self):
        for listnr in self.listenerList:
            AddProgress(listnr[0], listnr[1], listnr[2])

class ItemListener:
    def __init__(self) -> None:
        self.listenerDict: Dict[int, List[Tuple[str, str, float]]] = {}
           
    def Add(self, itemSerial: int, MissionName: str, TaskName: str, AddValue: float):
        if itemSerial not in self.listenerDict:
            self.listenerDict[itemSerial] = []
        self.listenerDict[itemSerial].append((MissionName, TaskName, AddValue))
        
    def Trigger(self, itemSerial: int):
        if itemSerial in self.listenerDict:
            for v in self.listenerDict[itemSerial]:
                AddProgress(v[0], v[1], v[2])

class Listeners:
    InventorySlotSwitching = Listener()
    Movement = Listener()
    KoponenTalk = Listener()
    KoponenRequestMission = Listener()
    KoponenReturnMission = Listener()
    LevelEnder = Listener()
    ItemPickup = ItemListener()
    ItemDrop = ItemListener()
#endregion
#region Classes
class Task:
    def __init__(self, missionName: str, safeName: str, text: str) -> None:
        global Missions
        self.safeName = safeName
        self.missionName = missionName
        self.text = text
        self.renderedText = TaskFont.render(self.text, True, KDS.Colors.White)
        self.renderedTextSize = self.renderedText.get_size()
        self.progress = 0.0
        self.progressScaled = 0
        self.finished = False
        self.lastFinished = False
        self.color = KDS.Animator.Color(TaskColor, TaskFinishedColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        Missions.GetMission(missionName).AddTask(safeName, self)
        
    def Progress(self, Value: float, Add: bool = False):
        self.progress = (self.progress + Value if Add else Value)
        if self.progress >= 1.0:
            self.finished = True
            self.progress = 1.0
        else: 
            self.finished = False
            if self.progress < 0.0: self.progress = 0.0
        self.progressScaled = KDS.Math.Floor(self.progress * 100)
        
    def Update(self, Width: int, Height: int, PlaySound: bool = True):
        surface = pygame.Surface((Width, Height))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, (Padding.left, round((Height / 2) - (self.renderedTextSize[1] / 2))))
        surface.blit(TaskFont.render(f"{self.progressScaled}%", True, KDS.Colors.White), (Width - Padding.right - hundredSize[0], round((Height / 2) - (self.renderedTextSize[1] / 2))))
        if self.finished != self.lastFinished:
            if self.finished:
                if PlaySound:
                    KDS.Audio.PlaySound(TaskFinishSound)
                self.color.changeValues(TaskColor, TaskFinishedColor)
            else:
                if PlaySound:
                    KDS.Audio.PlaySound(TaskUnFinishSound)
                self.color.changeValues(TaskColor, TaskUnFinishedColor)
        self.lastFinished = self.finished
        return surface

class KoponenTask(Task):
    def __init__(self, missionName: str, safeName: str, text: str, itemIDs: Iterable[int], itemsCallName: str, itemsCallVariation: str) -> None:
        super().__init__(missionName, safeName, text)
        koponenTaskCount = 0
        for task in Missions.GetMission(missionName).GetTaskList():
            if isinstance(task, KoponenTask): koponenTaskCount += 1
        if koponenTaskCount > 1: KDS.Logging.AutoError("Only one Koponen Task allowed per mission!")
        self.items = itemIDs
        self.callName = itemsCallName
        self.callVariation = itemsCallVariation

class Mission:
    def __init__(self, safeName: str, text: str) -> None:
        global Missions
        self.safeName = safeName
        self.text = text
        self.renderedText = MissionFont.render(self.text, True, KDS.Colors.White)
        self.textSize = self.renderedText.get_size()
        self.tasks: Dict[str, Task] = {}
        self.task_keys: List[str] = []
        self.task_values: List[Task] = []
        self.finished = False
        self.lastFinished = False
        self.finishedTicks = 0
        self.trueFinished = False
        self.color = KDS.Animator.Color(MissionColor, MissionFinishedColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        self.PlaySound = True
        Missions.AddMission(self.safeName, self)
        
    def AddTask(self, safeName: str, task: Task):
        if safeName not in self.tasks:
            self.tasks[safeName] = task
            self.task_keys = safeName
            self.task_values.append(self.tasks[safeName])
        else: KDS.Logging.AutoError("SafeName is already occupied!")
        
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
        self.PlaySound = False
        notFinished = 0
        taskAssigned = False
        for task in self.task_values:
            if not task.finished:
                self.finished = False
                notFinished += 1

            if isinstance(task, KoponenTask):
                KDS.Koponen.Mission.Task = task
                taskAssigned = True

            if notFinished > 0:
                self.PlaySound = True
                if taskAssigned: break
        del notFinished, taskAssigned

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
                KDS.Audio.PlaySound(MissionFinishSound)
                self.color.changeValues(MissionColor, MissionFinishedColor)
            else:
                KDS.Audio.PlaySound(MissionUnFinishSound)
                self.color.changeValues(MissionColor, MissionUnFinishedColor)
        self.lastFinished = self.finished
    
    def Render(self) -> Tuple[pygame.Surface, int]:
        _taskHeight = TaskHeight + Padding.top + Padding.bottom
        _taskWidth = 0
        for task in self.task_values:
            _taskWidth = max(_taskWidth, task.renderedTextSize[0])
        _taskWidth += Padding.left + Padding.right + TextOffset + hundredSize[0]
        HeaderHeight + ((TaskHeight + Padding.top + Padding.bottom) * len(self.task_values))
        surface = pygame.Surface((_taskWidth, HeaderHeight + ((TaskHeight + Padding.top + Padding.bottom) * len(self.task_values))))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, ((_taskWidth // 2) - (self.textSize[0] // 2), (HeaderHeight // 2) - (self.textSize[1] // 2)))
        for i, t in enumerate(self.task_values):
            surface.blit(t.Update(_taskWidth, _taskHeight, self.PlaySound), (0, HeaderHeight + (i * _taskHeight)))
        return surface, int(_taskWidth)

class MissionHolder:
    def __init__(self) -> None:
        self.missions: Dict[str, Mission] = {}
        self.mission_keys: List[str] = []
        self.mission_values: List[Mission] = []
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
        else: KDS.Logging.AutoError("SafeName is already occupied!")

Missions = MissionHolder()     
#endregion
#region init
Active_Mission: str
def init():
    global MissionFont, TaskFont, TaskFinishSound, TaskUnFinishSound, MissionFinishSound, MissionUnFinishSound, Active_Mission, Last_Active_Mission, text_height, TextOffset, hundredSize
    MissionFont = pygame.font.Font("Assets/Fonts/courier.ttf", 15, bold=1, italic=0)
    TaskFont = pygame.font.Font("Assets/Fonts/courier.ttf", 10, bold=0, italic=0)
    TaskFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_finish.ogg")
    TaskUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_unfinish.ogg")
    MissionFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_finish.ogg")
    MissionUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_unfinish.ogg")
    Active_Mission = None
    Last_Active_Mission = 0
    text_height = 0
    TextOffset = int(TaskFont.size(" ")[0] * TextOffset)
    hundredSize = TaskFont.size("100%")
#endregion
#region Initialize
def InitialiseTask(MissionName: str, SafeName: str, Text: str, *ListenerData: Union[Tuple[Listener, float], Tuple[ItemListener, int, float]]):
    """Initialises a task.

    Args:
        MissionName (str): The Safe_Name of the mission you want to add this task to.
        SafeName (str): A name that does not conflict with any other names.
        Text (str): The name that will be displayed as the task header.
    """
    Task(MissionName, SafeName, Text)
    for data in ListenerData:
        if isinstance(data[0], Listener):
            data[0].Add(MissionName, SafeName, data[1])
        elif isinstance(data[0], ItemListener):
            data[0].Add(data[1], MissionName, SafeName, data[2])
        else: raise TypeError("Listener is not a valid type!")

def InitialiseKoponenTask(MissionName: str, SafeName: str, Text: str, ItemsCallName: str, ItemsCallNameVariation: str, *itemIDs: int):
    KoponenTask(MissionName, SafeName, Text, itemIDs, ItemsCallName, ItemsCallNameVariation)

def InitialiseMission(SafeName: str, Text: str):
    """Initialises a mission.

    Args:
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
    """
    Mission(SafeName, Text)
#endregion
#region Rendering
def Render(surface: pygame.Surface):
    global Missions, Active_Mission
    Active_Mission = None
    for mission in Missions.GetMissionList():
        mission.Update()
        if not mission.trueFinished:
            Active_Mission = mission.safeName
            break
    if Active_Mission == None: Missions.finished = True
    else: Missions.finished = False
    if not Missions.finished:
        rendered, offset = Missions.GetMission(Active_Mission).Render()
        surface.blit(rendered, (surface.get_width() - offset, 0))
#endregion
#region Progress
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
    Missions = MissionHolder()
def Finish():
    global Missions
    for _mission in Missions.GetMissionList():
        for _task in _mission.GetTaskList():
            _task.Progress(100)
#endregion
