from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
import time
from typing import Final, Optional, Tuple

from uuid import UUID
import weakref

import pygame

import KDS.Animator
import KDS.Audio
import KDS.ConfigManager
import KDS.Logging
import KDS.MapProp
import KDS.Math
import KDS.Gamemode
import KDS.Clock
import KDS.Convert

waitMilliseconds = 500 #The amount of milliseconds ScoreAnimation will wait before updating the next animation
maxAnimationLength = 120 #The maximum amount of ticks one value of ScoreAnimation can take
animationDivider = 2 #The value the default animation length will be divided

maxTimeBonus = 500

score: int = 0
levelDeaths: int = 0

class ItemScoreHandler:
    _items: dict[int, weakref.ref[object]] | None = None

    @staticmethod
    def internalStart():
        ItemScoreHandler._items = dict()

    @staticmethod
    def registerItemPickupScore(item: object, addScore: int):
        """
        Item should be the item instance that triggers the pickup.
        This should be instance of `KDS.Build.Item`, but we cannot verify it due to Python being stupid. (cannot import item)
        """
        # NOTE: This isn't a foolproof system
        # as some items are destroyed/created in the lifecycle of the game
        # i.e. meth flask => empty flask (drinking)
        # In these cases the new item can be reregistered for item score
        # but this is still vastly better than getting score for every single pickup possible

        # TODO: Save the score inside every item instance and set it as 0 when used.

        if ItemScoreHandler._items is None:
            raise RuntimeError("Item Score Handler has not been started!")

        itemMemoryAddr: int = id(item)

        # Check if memory address is used first
        # We check memory address instead of set contains in case any items have overridden the __eq__ method
        # After that the item needs to be verified because GC can free the memory for new items to be allocated in the same spot
        existingObject: weakref.ref[object] | None = ItemScoreHandler._items.get(itemMemoryAddr, None)
        if existingObject is not None:
            # We keep a weak reference to this object in the dictionary so that the garbage collector can clear unused items
            # so that we don't have a memory leak

            # We check 'is item' to verify that the memory address belongs to the same object
            # if a new object was allocated on its space, we replate the item at that memory location reference.
            if existingObject() is item:
                KDS.Logging.info(f"Ignoring item score for item, item has already been picked up.")
                return
            else:
                KDS.Logging.info(f"Item at address {hex(itemMemoryAddr)} has been replaced by a new item instance, score will be added.", consoleVisible=True)

        ItemScoreHandler._items[itemMemoryAddr] = weakref.ref(item)

        global score
        score += addScore

    @staticmethod
    def internalStop():
        ItemScoreHandler._items = None

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
        self.start = datetime.now(UTC)

    def Pause(self) -> None:
        if self.pauseStart != None:
            raise RuntimeError("Calling pause start while paused!")
        self.pauseStart = datetime.now(UTC)

    def Unpause(self) -> None:
        if self.pauseStart == None:
            raise RuntimeError("Calling pause end when not paused!")
        self.cumPause += datetime.now(UTC) - self.pauseStart
        self.pauseStart = None

    def Stop(self) -> None:
        self.end = datetime.now(UTC)

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

@dataclass(frozen=True)
class TimeBonusScore:
    bonus_start: float
    bonus_end: float
    gametime: timedelta

    @property
    def score(self) -> int:
        clampedGameTime = KDS.Math.Clamp(self.gametime.total_seconds(), self.bonus_start, self.bonus_end)
        timeBonusFloat: float = KDS.Math.Remap(clampedGameTime, self.bonus_start, self.bonus_end, maxTimeBonus, 0)
        return round(timeBonusFloat)

@dataclass(frozen=True)
class DeathlessBonusScore:
    deathCount: int

    @property
    def score(self) -> int:
        return 500 if self.deathCount < 1 else 0

@dataclass(frozen=True)
class RunScores:
    score: int
    deathless_bonus: DeathlessBonusScore
    time_bonus: TimeBonusScore

    @property
    def total_score(self) -> int:
        return self.score + self.deathless_bonus.score + self.time_bonus.score

class ScoreCounter:
    @staticmethod
    def Start():
        global score, levelDeaths
        score = 0
        levelDeaths = 0

        ItemScoreHandler.internalStart()
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
        ItemScoreHandler.internalStop()
        GameTime.Stop()

    @staticmethod
    def GetScores() -> RunScores:
        global score, levelDeaths
        tb_start: Optional[int] = KDS.MapProp.LevelProp.Get("Data/TimeBonus/start", None)
        tb_end: Optional[int] = KDS.MapProp.LevelProp.Get("Data/TimeBonus/end", None)
        if tb_start == None or tb_end == None:
            KDS.Logging.AutoError(f"Time Bonus is not defined! Values: (start: {tb_start}, end: {tb_end})")
            tb_start = 1
            tb_end = 2

        gametime: timedelta = GameTime.GetGameTime()
        return RunScores(
            score=score,
            deathless_bonus=DeathlessBonusScore(levelDeaths),
            time_bonus=TimeBonusScore(bonus_start=tb_start, bonus_end=tb_end, gametime=gametime)
        )

class ScoreAnimation:
    animationIndex = 0
    animationList: Tuple = ()
    valueList: Tuple = ()
    soundCooldown = 5
    finished = False

    @staticmethod
    def init(calcscores: RunScores):
        score: Final[int] = calcscores.score
        deathlessBonus: Final[int] = calcscores.deathless_bonus.score
        timeBonus: Final[int] = calcscores.time_bonus.score
        totalScore: Final[int] = calcscores.total_score

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

def render_campaign_scores(save_uuid: UUID, font: pygame.Font, size: tuple[int, int], padding: int, background_color: tuple[int, int, int]) -> pygame.Surface | None:
    save: Final = KDS.ConfigManager.CampaignSave.load(save_uuid)
    if not save.can_be_scored:
        return None

    datas: list[list[tuple[str, str]]] = [
        [
            ("Highest Score", str(save.get_max_score())),
            ("Fastest Run", KDS.Convert.FormatDuration(save.get_min_duration())),
        ],
        [
            ("Total Deaths", str(save.get_total_deaths())),
            ("Total Runs", str(save.get_run_count()))
        ]
    ]

    logical_size: Final = (size[0] - 2 * padding, size[1] - 2 * padding)

    data_surfs: list[pygame.Surface] = [
        _render_campaign_data(font=font, width=logical_size[0], data=data, background_color=background_color)
        for data in datas
    ]
    data_surf_total_height: int = sum(ds.height for ds in data_surfs)
    space_between: float = (logical_size[1] - data_surf_total_height) / (len(data_surfs) - 1)

    surf: Final = pygame.Surface(size)
    surf.fill(background_color)

    blitted_height: int = 0
    for i, ds in enumerate(data_surfs):
        y: int = padding + blitted_height + round(i * space_between)
        surf.blit(ds, (padding, round(y)))
        blitted_height += ds.height
    return surf

def _render_campaign_data(*, font: pygame.Font, width: int, data: list[tuple[str, str]], background_color: tuple[int, int, int]) -> pygame.Surface:
    lineheight: int = font.get_linesize()
    height: int = len(data) * lineheight

    surf: Final = pygame.Surface((width, height))
    surf.fill(background_color)
    for i, (title, value) in enumerate(data):
        tsurf = font.render(title, True, (255, 255, 255))
        vsurf = font.render(value, True, (255, 255, 255))

        y: int = i * lineheight
        surf.blit(tsurf, (0, y))
        surf.blit(vsurf, (width - vsurf.width, y))

    return surf
