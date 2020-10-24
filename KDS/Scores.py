import time
import sys
import KDS.Math
import KDS.ConfigManager

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
        GameTime.FormattedGameTime.minutes = f"{divmod(GameTime.gameTime, 60)[0]:02d}"
        GameTime.FormattedGameTime.seconds = f"{divmod(GameTime.gameTime, 60)[1]:02d}"
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