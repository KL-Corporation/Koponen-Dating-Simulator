class ScoreCounter:
    def __init__(self, score, koponen_happiness):
        self.mainScore = score
        self.mainScore_counter = 0
        self.mainScore_finished = False
        self.koponen_happiness = koponen_happiness
        self.khP_counter = 0
        self.khP_finished = False
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

        if self.mainScore_finished:
            result.append("Koponen happiness:  " + str(self.khP_counter))
            if self.khP_finished:
                self.allFinished = True

        return result
