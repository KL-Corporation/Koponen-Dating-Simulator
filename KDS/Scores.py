import time
from typing import Tuple

import pygame

import KDS.Animator
import KDS.Audio
import KDS.ConfigManager
import KDS.Logging
import KDS.Math

waitMilliseconds = 500 #The amount of milliseconds ScoreAnimation will wait before updating the next animation
maxAnimationLength = 120 #The maximum amount of ticks one value of ScoreAnimation can take
animationDivider = 2 #The value the default animation length will be divided

maxTimeBonus = 500

score = 0
koponen_happiness = 40

def init():
    global pointSound
    pointSound = pygame.mixer.Sound("Assets/Audio/Effects/point_count.ogg")

class GameTime:
    formattedGameTime = "null"
    gameTime = -1
    startTime = -1
    pauseStartTime = -1
    cumulativePauseTime = 0
    @staticmethod
    def start():
        GameTime.gameTime = -1
        GameTime.cumulativePauseTime = 0
        GameTime.startTime = time.perf_counter()
    
    @staticmethod
    def pause():
        if GameTime.pauseStartTime == -1:
            GameTime.pauseStartTime = time.perf_counter()
        
    @staticmethod
    def unpause():
        GameTime.cumulativePauseTime += time.perf_counter() - GameTime.pauseStartTime
        GameTime.pauseStartTime = -1
    
    @staticmethod
    def stop():
        GameTime.gameTime = time.perf_counter() - GameTime.startTime - GameTime.cumulativePauseTime
        divTime = divmod(GameTime.gameTime, 60)
        GameTime.formattedGameTime = f"{round(divTime[0]):02d}m {round(divTime[1]):02d}s"

class ScoreCounter:
    @staticmethod
    def start():
        global score, koponen_happiness
        score = 0
        koponen_happiness = 40
        GameTime.start()

    @staticmethod
    def pause():
        GameTime.pause()

    @staticmethod
    def unpause():
        GameTime.unpause()

    @staticmethod
    def stop():
        GameTime.stop()

    @staticmethod
    def calculateScores():
        global score, koponen_happiness
        tb_start: int = KDS.ConfigManager.GetLevelProp("Data/TimeBonus/start", None)
        tb_end: int = KDS.ConfigManager.GetLevelProp("Data/TimeBonus/end", None)
        if tb_start == None or tb_end == None:
            KDS.Logging.AutoError(f"Time Bonus is not defined! Values: (start: {tb_start}, end: {tb_end})")
            tb_start = 1
            tb_end = 2
        gameTime: float = KDS.Math.Clamp(GameTime.gameTime, tb_start, tb_end)
        timeBonusIndex: float = KDS.Math.Remap01(gameTime, tb_start, tb_end)
        timeBonus: int = round(KDS.Math.Lerp(maxTimeBonus, 0, timeBonusIndex))
        
        totalScore: int = score + koponen_happiness + timeBonus
        
        return score, koponen_happiness, timeBonus, totalScore

class ScoreAnimation:
    animationIndex = 0
    animationList: Tuple = ()
    valueList: Tuple = ()
    soundCooldown = 5
    finished = False
    
    @staticmethod
    def init():
        score, koponen_happiness, timeBonus, totalScore = ScoreCounter.calculateScores()
        
        ScoreAnimation.animationIndex = 0
        ScoreAnimation.finished = False
        
        score_animation = KDS.Animator.Float(0, score, min(round(abs(score) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        koponen_happiness_animation = KDS.Animator.Float(0, koponen_happiness, min(round(abs(koponen_happiness) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        timeBonus_animation = KDS.Animator.Float(0, timeBonus, min(round(abs(timeBonus) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        totalScore_animation = KDS.Animator.Float(0, totalScore, min(round(abs(totalScore) / animationDivider), maxAnimationLength), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        
        ScoreAnimation.animationList = (score_animation, koponen_happiness_animation, timeBonus_animation, totalScore_animation)
        ScoreAnimation.valueList = (score, koponen_happiness, timeBonus, totalScore)
    
    @staticmethod 
    def update(fadeFinished: bool = True):
        if not ScoreAnimation.finished and fadeFinished:
            animation = ScoreAnimation.animationList[ScoreAnimation.animationIndex]
            animation.update()
            if animation.Finished:
                pygame.time.delay(waitMilliseconds)
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
            animation.tick = animation.ticks
            animation.update()
