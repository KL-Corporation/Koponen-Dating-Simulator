#region Importing
from typing import Dict, Iterable, List, Optional, Tuple, Union, cast
import json

import pygame

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.ConfigManager
import KDS.Convert
import KDS.Events
import KDS.Gamemode
import KDS.Koponen
import KDS.Logging
import KDS.NPC
import KDS.Math
import KDS.Linq

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
        self._listenerList: List[Tuple[str, str, float]] = []
        self.OnTrigger = KDS.Events.Event()

    def Add(self, MissionName: str, TaskName: str, AddValue: float):
        self._listenerList.append((MissionName, TaskName, AddValue))

    def ContainsActiveTask(self) -> bool:
        global Active_Mission
        return KDS.Linq.Any(self._listenerList, lambda l: l[0] == Active_Mission and (m := Missions.GetMission(Active_Mission)) != None and m.GetTask(l[1]) != None)

    def Trigger(self):
        for listnr in self._listenerList:
            AddProgress(listnr[0], listnr[1], listnr[2])
        self.OnTrigger.Invoke()

    def Clear(self):
        self._listenerList.clear()

class ItemListener:
    def __init__(self) -> None:
        self._listenerDict: Dict[int, List[Tuple[str, str, float]]] = {}
        self.OnTrigger = KDS.Events.Event()

    def Add(self, itemSerial: int, MissionName: str, TaskName: str, AddValue: float):
        if itemSerial not in self._listenerDict:
            self._listenerDict[itemSerial] = []
        self._listenerDict[itemSerial].append((MissionName, TaskName, AddValue))

    def Trigger(self, itemSerial: int):
        if itemSerial in self._listenerDict:
            for v in self._listenerDict[itemSerial]:
                AddProgress(v[0], v[1], v[2])
        self.OnTrigger.Invoke(itemSerial)

    def Clear(self):
        self._listenerDict.clear()

class Listeners:
    InventorySlotSwitching = Listener()
    Movement = Listener()
    KoponenTalk = Listener()
    KoponenRequestMission = Listener()
    KoponenReturnMission = Listener()
    KoponenTalkEnd = Listener()
    LevelEnder = Listener()
    Teleport = Listener()
    TentSleepStart = Listener()
    TentSleepEnd = Listener()
    EnemyDeath = Listener()
    TeacherAgro = Listener() # Not implemented
    TeacherDeath = Listener() # Not implemented
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
        self.color = KDS.Animator.Color(TaskColor, TaskColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        Missions.GetMission(missionName).AddTask(safeName, self)

    def Progress(self, Value: float, Add: bool = False):
        self.progress = (self.progress + Value if Add else Value)
        if self.progress >= 1.0:
            self.finished = True
            self.progress = 1.0
        else:
            self.finished = False
            if self.progress < 0.0: self.progress = 0.0
        self.progressScaled = KDS.Math.FloorToInt(self.progress * 100)

    def Update(self, Width: int, Height: int, PlaySound: bool = True):
        if self.finished != self.lastFinished:
            if self.finished:
                if PlaySound:
                    KDS.Audio.PlaySound(TaskFinishSound)
                self.color.changeValues(TaskColor, TaskFinishedColor)
            else:
                if PlaySound:
                    KDS.Audio.PlaySound(TaskUnFinishSound)
                self.color.changeValues(TaskColor, TaskUnFinishedColor)

        surface = pygame.Surface((Width, Height))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, (Padding.left, round((Height / 2) - (self.renderedTextSize[1] / 2))))
        surface.blit(TaskFont.render(f"{self.progressScaled}%", True, KDS.Colors.White), (Width - Padding.right - hundredSize[0], round((Height / 2) - (self.renderedTextSize[1] / 2))))
        self.lastFinished = self.finished
        return surface

class KoponenTask(Task):
    def __init__(self, missionName: str, safeName: str, text: str, itemIDs: Iterable[int]) -> None:
        super().__init__(missionName, safeName, text)
        koponenTaskCount = 0
        for task in Missions.GetMission(missionName).GetTaskList():
            if isinstance(task, KoponenTask):
                koponenTaskCount += 1
        if koponenTaskCount > 1:
            KDS.Logging.AutoError("Only one Koponen Task allowed per mission!")
        self.items = itemIDs

class StudentTask(Task):
    def __init__(self, missionName: str, safeName: str, text: str, interactCount: int, interactPrompt: str) -> None:
        super().__init__(missionName, safeName, text)
        studentTaskCount = 0
        for task in Missions.GetMission(missionName).GetTaskList():
            if isinstance(task, StudentTask):
                studentTaskCount += 1
        if studentTaskCount:
            KDS.Logging.AutoError("Only one Student Task allowed per mission!")
        self.interacted = 0
        self.interactCount = interactCount
        self.interactedStudents: List[KDS.NPC.StudentNPC] = []
        self.prompt = TipFont.render(interactPrompt, True, KDS.Colors.White)

    def HasInteracted(self, student: KDS.NPC.StudentNPC) -> bool:
        return student in self.interactedStudents

    def Interact(self, student: KDS.NPC.StudentNPC):
        self.interactedStudents.append(student)
        self.interacted += 1
        self.Progress(self.interacted / self.interactCount)


class Mission:
    def __init__(self, safeName: str, text: str, playSound: bool) -> None:
        global Missions
        self.safeName = safeName
        self.text = text
        self.renderedText = MissionFont.render(self.text, True, KDS.Colors.White)
        self.textSize = self.renderedText.get_size()
        self.tasks: Dict[str, Task] = {}
        self.finished = False
        self.lastFinished = False
        self.finishedTicks = 0
        self.trueFinished = False
        self.color = KDS.Animator.Color(MissionColor, MissionFinishedColor, TaskAnimationDuration, AnimationType, KDS.Animator.OnAnimationEnd.Stop)
        self._playTaskSound: bool = False
        self.playSound = playSound
        Missions.AddMission(self.safeName, self)

    def AddTask(self, safeName: str, task: Task):
        if safeName not in self.tasks:
            self.tasks[safeName] = task
        else: KDS.Logging.AutoError("SafeName is already occupied!")

    def GetTask(self, safeName: str):
        if safeName in self.tasks: return self.tasks[safeName]
        else: return None

    def GetTaskList(self) -> List[Task]:
        return list(self.tasks.values())

    def GetKeyList(self) -> List[str]:
        return list(self.tasks.keys())

    def GetTaskByValue(self, value):
        return self.tasks[tuple(self.tasks.keys())[tuple(self.tasks.values()).index(value)]]

    def Update(self):
        self.finished = True
        self._playTaskSound = False
        notFinished = 0
        taskAssigned = False
        for task in self.tasks.values():
            if not task.finished:
                self.finished = False
                notFinished += 1

            if isinstance(task, KoponenTask):
                KDS.Koponen.Mission.Task = task
                taskAssigned = True

            if notFinished > 0:
                self._playTaskSound = True
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
                if self.playSound: KDS.Audio.PlaySound(MissionFinishSound)
                self.color.changeValues(MissionColor, MissionFinishedColor)
            else:
                if self.playSound: KDS.Audio.PlaySound(MissionUnFinishSound)
                self.color.changeValues(MissionColor, MissionUnFinishedColor)
        self.lastFinished = self.finished

    def Render(self) -> Tuple[pygame.Surface, int]:
        _taskHeight = TaskHeight + Padding.top + Padding.bottom
        _taskWidth = 0
        for task in self.tasks.values():
            _taskWidth = max(_taskWidth, task.renderedTextSize[0])
        _taskWidth += Padding.left + Padding.right + TextOffset + hundredSize[0]
        surface = pygame.Surface((_taskWidth, HeaderHeight + ((TaskHeight + Padding.top + Padding.bottom) * len(self.tasks))))
        surface.fill(self.color.update(not self.finished))
        surface.blit(self.renderedText, ((_taskWidth // 2) - (self.textSize[0] // 2), (HeaderHeight // 2) - (self.textSize[1] // 2)))
        for i, t in enumerate(self.tasks.values()):
            surface.blit(t.Update(_taskWidth, _taskHeight, self._playTaskSound if self.playSound else False), (0, HeaderHeight + (i * _taskHeight)))
        return surface, int(_taskWidth)

class MissionHolder:
    def __init__(self) -> None:
        self.missions: Dict[str, Mission] = {}
        self.finished: bool = False

    def GetMission(self, safeName: str) -> Union[Mission, None]:
        if safeName in self.missions: return self.missions[safeName]
        else: return None

    def GetMissionList(self) -> List[Mission]:
        return list(self.missions.values())

    def GetKeyList(self) -> List[str]:
        return list(self.missions.keys())

    def GetMissionByValue(self, value) -> Mission:
        return self.missions[tuple(self.missions.keys())[tuple(self.missions.values()).index(value)]]

    def AddMission(self, safeName: str, mission: Mission):
        if safeName not in self.missions:
            self.missions[safeName] = mission
        else: KDS.Logging.AutoError("SafeName is already occupied!")

Missions = MissionHolder()
#endregion
#region init
Active_Mission: str
def init():
    global MissionFont, TaskFont, TipFont, TaskFinishSound, TaskUnFinishSound, MissionFinishSound, MissionUnFinishSound, Active_Mission, Last_Active_Mission, text_height, TextOffset, hundredSize
    TipFont = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10, bold=0, italic=0)
    MissionFont = pygame.font.Font("Assets/Fonts/courier.ttf", 15, bold=1, italic=0)
    TaskFont = pygame.font.Font("Assets/Fonts/courier.ttf", 10, bold=0, italic=0)
    TaskFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_finish.ogg")
    TaskUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/task_unfinish.ogg")
    MissionFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_finish.ogg")
    MissionUnFinishSound = pygame.mixer.Sound("Assets/Audio/effects/mission_unfinish.ogg")
    Active_Mission = ""
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
            data[0].Add(cast(int, data[1]), MissionName, SafeName, cast(float, data[2]))
        else: raise ValueError("Invalid arguments were given.")

def InitialiseKoponenTask(MissionName: str, SafeName: str, Text: str, *itemIDs: int):
    KoponenTask(MissionName, SafeName, Text, itemIDs)

def InitialiseMission(SafeName: str, Text: str, NoSound: bool = False):
    """Initialises a mission.

    Args:
        Safe_Name (str): A name that does not conflict with any other names.
        Visible_Name (str): The name that will be displayed as the task header.
    """
    Mission(SafeName, Text, not NoSound)
#endregion
#region Rendering
def Render(surface: pygame.Surface):
    global Missions, Active_Mission
    Active_Mission = ""
    for mission in Missions.GetMissionList():
        mission.Update()
        if not mission.trueFinished:
            Active_Mission = mission.safeName
            break
    if len(Active_Mission) < 1:
        Missions.finished = True
        return

    Missions.finished = False
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
    for l in Listeners.__dict__.values():
        if isinstance(l, Listener) or isinstance(l, ItemListener):
            l.Clear()
    Missions = MissionHolder()
def Finish():
    global Missions
    for _mission in Missions.GetMissionList():
        for _task in _mission.GetTaskList():
            _task.Progress(100)
def ForceFinish():
    global Missions
    for _mission in Missions.GetMissionList():
        for _task in _mission.GetTaskList():
            _task.Progress(100)
            _task.lastFinished = True
        _mission.finished = True
        _mission.trueFinished = True
        _mission.lastFinished = True
#endregion
