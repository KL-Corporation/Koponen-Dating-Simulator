import time
import KDS.Math

print()

class GameTime:
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
    def calculateScores():
        pass