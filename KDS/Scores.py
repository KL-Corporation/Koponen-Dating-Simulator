from os import stat
import time
import sys
import KDS.Animator
import KDS.Math
import KDS.ConfigManager

waitTicks = 30 #The amount of ticks ScoreAnimation will wait before updating the next animation

maxTimeBonus = int(KDS.ConfigManager.GetGameSetting("GameData", "Default", "Score", "timeBonus"))

class GameTime:
    class FormattedGameTime:
        minutes: str = None
        seconds: str = None
    gameTime = -1
    startTime = -1
    pauseStartTime = -1
    cumulativePauseTime = -1
    @staticmethod
    def start():
        GameTime.gameTime = -1
        GameTime.startTime = time.perf_counter()
    
    @staticmethod
    def pause():
        if GameTime.pauseStartTime == -1:
            GameTime.pauseStartTime = time.perf_counter()
        
    @staticmethod
    def unpause():
        GameTime.cumulativePauseTime += GameTime.startTime - time.perf_counter()
        GameTime.pauseStartTime = -1
    
    @staticmethod
    def stop():
        GameTime.gameTime = GameTime.startTime - GameTime.cumulativePauseTime
        GameTime.FormattedGameTime.minutes = f"{round(divmod(GameTime.gameTime, 60)[0]):02d}"
        GameTime.FormattedGameTime.seconds = f"{round(divmod(GameTime.gameTime, 60)[1]):02d}"
        return GameTime.gameTime

class ScoreCounter:
    @staticmethod
    def start():
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
    def calculateScores(score: int, koponen_happiness: int):
        tb_start = KDS.ConfigManager.GetLevelProp("TimeBonus", "start", None)
        tb_end = KDS.ConfigManager.GetLevelProp("TimeBonus", "end", None)
        gameTime = KDS.Math.Clamp(GameTime.gameTime, tb_start, tb_end)
        timeBonusIndex = KDS.Math.Remap(gameTime, tb_start, tb_end, 0, 1)
        timeBonus = round(KDS.Math.Lerp(maxTimeBonus, 0, timeBonusIndex))
        
        totalScore = score + koponen_happiness + timeBonus
        
        return score, koponen_happiness, timeBonus, totalScore
    
class ScoreAnimation:
    animationIndex = 0
    animationList = ()
    valueList = ()
    waitTime = 0
    finished = False
    
    @staticmethod
    def init(score: int, koponen_happiness: int):
        score, koponen_happiness, timeBonus, totalScore = ScoreCounter.calculateScores(score, koponen_happiness)
        
        score_animation = KDS.Animator.Float(0, score, min(score, 2000), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        koponen_happiness_animation = KDS.Animator.Float(0, koponen_happiness, min(koponen_happiness, 2000), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        timeBonus_animation = KDS.Animator.Float(0, timeBonus, min(timeBonus, 2000), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        totalScore_animation = KDS.Animator.Float(0, totalScore, min(totalScore, 2000), KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        
        ScoreAnimation.animationList = (score_animation, koponen_happiness_animation, timeBonus_animation, totalScore_animation)
        ScoreAnimation.valueList = (score, koponen_happiness, timeBonus, totalScore)
    
    @staticmethod 
    def update():
        if not ScoreAnimation.finished:
            animation = ScoreAnimation.animationList[ScoreAnimation.animationIndex]
            value = animation.update()
            if value >= animation.ticks:
                ScoreAnimation.waitTime += 1
                if ScoreAnimation.waitTime > waitTicks:
                    ScoreAnimation.animationIndex += 1
                    if ScoreAnimation.animationIndex >= len(ScoreAnimation.animationList):
                        ScoreAnimation.finished = True
                        ScoreAnimation.waitTime = 0
                        
        return tuple([anim.get_value() for anim in ScoreAnimation.animationList])
    
    @staticmethod
    def skip():
        for animation in ScoreAnimation.animationList:
            animation.tick = animation.ticks
            animation.update()