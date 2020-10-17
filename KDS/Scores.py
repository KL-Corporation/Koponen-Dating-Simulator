import time

class ScoreCounter:
    def __init__(self, score, koponen_happiness, time_bonus):
        self.mainScore = score
        self.mainScore_counter = 0
        self.mainScore_finished = False
        self.koponen_happiness = koponen_happiness
        self.khP_counter = 0
        self.khP_finished = False
        self.time_bonus = time_bonus
        self.t_counter = 0
        self.t_counter_finished = False
        self.allFinished = False

    def update(self):
        result = []
        result.append("Score:                        " + str(self.mainScore_counter))
        if not self.mainScore_finished:
            self.mainScore_counter += 5
            if self.mainScore_counter > self.mainScore:
                self.mainScore_counter = self.mainScore
                self.mainScore_finished = True
        elif not self.khP_finished:
            self.khP_counter += 1
            if self.khP_counter > self.koponen_happiness:
                self.khP_counter = self.koponen_happiness
                self.khP_finished = True
        elif not self.t_counter_finished:
            self.t_counter += 3
            if self.t_counter > self.time_bonus:
                self.t_counter = self.time_bonus
                self.t_counter_finished = True

        if self.mainScore_finished:
            result.append("Koponen happiness:  " + str(self.khP_counter))
        if self.khP_finished:
            result.append("Time Bonus:               " + str(self.t_counter))
        if self.t_counter_finished:
            self.allFinished = True

        return result

    def fastForward(self):
        self.mainScore_counter = self.mainScore
        self.khP_counter = self.koponen_happiness

class GameTime:
    def __init__(self):
        self.start_time = 0.0
        self.paused = False
        self.pause_started = 0.0
        self.pause_ended = 0.0

    def start(self):
        self.start_time = time.perf_counter()

    def pause(self):
        if not self.paused:
            self.paused = True
            self.pause_started = time.perf_counter()
    
    def resume(self):
        if self.paused:
            self.paused = False
            self.pause_ended = time.perf_counter()
            self.start_time += (self.pause_ended - self.pause_started)

    def getTime(self, formatted = True):
        if formatted:
            pTime = time.perf_counter() - self.start_time
            minutes = pTime // 60
            seconds = pTime % 60
            return minutes, seconds
        else:
            return time.perf_counter() - self.start_time