from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto
import time
from typing import Optional, Tuple

import pygame

import KDS.Animator
import KDS.Audio
import KDS.ConfigManager
import KDS.Logging
import KDS.Math
import KDS.Gamemode
import KDS.Clock

waitMilliseconds = 500 #The amount of milliseconds ScoreAnimation will wait before updating the next animation
maxAnimationLength = 120 #The maximum amount of ticks one value of ScoreAnimation can take
animationDivider = 2 #The value the default animation length will be divided

maxTimeBonus = 500

score: int = 0
levelDeaths: int = 0

def init():
    global pointSound
    pointSound = pygame.mixer.Sound("Assets/Audio/Effects/point_count.ogg")

class GameTimeTimer(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def Start(self) -> None:
        pass

    @abstractmethod
    def Pause(self) -> None:
        pass

    @abstractmethod
    def Unpause(self) -> None:
        pass

    @abstractmethod
    def Stop(self) -> None:
        pass

    @abstractmethod
    def GetGameTime(self) -> timedelta:
        pass

class GameTimeTimerPerfCounter(GameTimeTimer):
    def __init__(self) -> None:
        self.start: Optional[float] = None
        self.end: Optional[float] = None
        self.pauseStart: Optional[float] = None
        self.cumPause: float = 0.0

    def Start(self) -> None:
        self.cumPause = 0.0
        self.start = time.perf_counter()

    def Pause(self) -> None:
        if self.pauseStart != None:
            raise RuntimeError("Calling pause start while paused!")
        self.pauseStart = time.perf_counter()

    def Unpause(self) -> None:
        if self.pauseStart == None:
            # raise RuntimeError("Calling pause end when not paused!")
            return
        self.cumPause += time.perf_counter() - self.pauseStart
        self.pauseStart = None

    def Stop(self) -> None:
        self.end = time.perf_counter()

    def GetGameTime(self) -> timedelta:
        if self.start == None or self.end == None:
            raise RuntimeError("Cannot get game time before stopping the timer!")
        return timedelta(seconds=self.end - self.start - self.cumPause)

class GameTimeTimerDateTime(GameTimeTimer):
    def __init__(self) -> None:
        self.start: Optional[datetime] = None
        self.end: Optional[datetime] = None
        self.pauseStart: Optional[datetime] = None
        self.cumPause: timedelta = timedelta()

    def Start(self) -> None:
        self.cumPause = timedelta()
        self.start = datetime.utcnow()

    def Pause(self) -> None:
        if self.pauseStart != None:
            raise RuntimeError("Calling pause start while paused!")
        self.pauseStart = datetime.utcnow()

    def Unpause(self) -> None:
        if self.pauseStart == None:
            raise RuntimeError("Calling pause end when not paused!")
        self.cumPause += datetime.utcnow() - self.pauseStart
        self.pauseStart = None

    def Stop(self) -> None:
        self.end = datetime.utcnow()

    def GetGameTime(self) -> timedelta:
        if self.start == None or self.end == None:
            raise RuntimeError("Cannot get game time before stopping the timer!")
        return self.end - self.start

class GameTimerType(Enum):
    PerfCounter = GameTimeTimerPerfCounter
    DateTime = GameTimeTimerDateTime

class GameTime:
    Timer: Optional[GameTimeTimer] = None

    @staticmethod
    def Start(_type: GameTimerType) -> None:
        tmpTmr: GameTimeTimer = _type.value() # Calling timer constructor
        GameTime.Timer = tmpTmr
        GameTime.Timer.Start()

    @staticmethod
    def Pause():
        if GameTime.Timer == None:
            raise RuntimeError("Cannot pause timer before starting timer!")
        GameTime.Timer.Pause()

    @staticmethod
    def Unpause():
        if GameTime.Timer == None:
            raise RuntimeError("Cannot unpause timer before starting timer!")
        GameTime.Timer.Unpause()

    @staticmethod
    def Stop():
        if GameTime.Timer == None:
            raise RuntimeError("Cannot stop timer before starting timer!")
        GameTime.Timer.Stop()

    @staticmethod
    def GetGameTime() -> timedelta:
        if GameTime.Timer == None:
            raise RuntimeError("Cannot get game time before stopping timer!")
        return GameTime.Timer.GetGameTime()

    @staticmethod
    def GetFormattedString(secondsOverride: Optional[float] = None) -> str:
        totalSeconds = secondsOverride
        if totalSeconds == None:
            time = GameTime.GetGameTime()
            totalSeconds = time.total_seconds()
        minutes = int(totalSeconds // 60)
        seconds = round(totalSeconds % 60)
        return f"{minutes}m {seconds}s"

class ScoreCounter:
    @staticmethod
    def Start():
        global score, levelDeaths
        score = 0
        levelDeaths = 0
        storyMode = KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story
        GameTime.Start(GameTimerType.PerfCounter if not storyMode else GameTimerType.DateTime)

    @staticmethod
    def Pause():
        GameTime.Pause()

    @staticmethod
    def Unpause():
        GameTime.Unpause()

    @staticmethod
    def Stop():
        GameTime.Stop()

    @staticmethod
    def CalculateScores():
        global score, levelDeaths
        tb_start: Optional[int] = KDS.ConfigManager.LevelProp.Get("Data/TimeBonus/start", None)
        tb_end: Optional[int] = KDS.ConfigManager.LevelProp.Get("Data/TimeBonus/end", None)
        if tb_start == None or tb_end == None:
            KDS.Logging.AutoError(f"Time Bonus is not defined! Values: (start: {tb_start}, end: {tb_end})")
            tb_start = 1
            tb_end = 2
        clampedGameTime = KDS.Math.Clamp(GameTime.GetGameTime().total_seconds(), tb_start, tb_end)
        timeBonusFloat: float = KDS.Math.Remap(clampedGameTime, tb_start, tb_end, maxTimeBonus, 0)
        timeBonus = round(timeBonusFloat)
        deathlessBonus = 500 if levelDeaths < 1 else 0

        totalScore: int = score + deathlessBonus + timeBonus

        return score, deathlessBonus, timeBonus, totalScore

class ScoreAnimation:
    animationIndex = 0
    animationList: Tuple = ()
    valueList: Tuple = ()
    soundCooldown = 5
    finished = False

    @staticmethod
    def init():
        score, deathlessBonus, timeBonus, totalScore = ScoreCounter.CalculateScores()

        ScoreAnimation.animationIndex = 0
        ScoreAnimation.finished = False

        score_animation = KDS.Animator.Value(0, score, min(round(abs(score) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        deathlessBonus_animation = KDS.Animator.Value(0, deathlessBonus, min(round(abs(deathlessBonus) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        timeBonus_animation = KDS.Animator.Value(0, timeBonus, min(round(abs(timeBonus) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        totalScore_animation = KDS.Animator.Value(0, totalScore, min(round(abs(totalScore) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)

        ScoreAnimation.animationList = (score_animation, deathlessBonus_animation, timeBonus_animation, totalScore_animation)
        ScoreAnimation.valueList = (score, deathlessBonus, timeBonus, totalScore)

    @staticmethod
    def update(fadeFinished: bool = True):
        if not ScoreAnimation.finished and fadeFinished:
            animation = ScoreAnimation.animationList[ScoreAnimation.animationIndex]
            animation.update()
            if animation.Finished:
                KDS.Clock.Sleep(waitMilliseconds)
                ScoreAnimation.animationIndex += 1
                if ScoreAnimation.animationIndex >= len(ScoreAnimation.animationList):
                    ScoreAnimation.finished = True
            elif ScoreAnimation.soundCooldown > 2:
                KDS.Audio.PlaySound(pointSound)
                ScoreAnimation.soundCooldown = 0
            ScoreAnimation.soundCooldown += 1

        return tuple([round(anim.get_value()) for anim in ScoreAnimation.animationList])

    @staticmethod
    def skip():
        for animation in ScoreAnimation.animationList:
            animation: KDS.Animator.Value
            animation.tick = animation.ticks + 1
            animation.update()
