from typing import Dict, List
import pygame
from pygame.locals import *
import random
from time import perf_counter
import json
import KDS.Colors
import KDS.Audio
import KDS.ConfigManager
import KDS.Convert
import KDS.System
import KDS.Math

class Timer:
    def __init__(self, start_time = 60):
        self.time = start_time
        self.start_time = 0

    def start(self):
        self.start_time = perf_counter()
    
    def get_time(self):
        self.time -= perf_counter() - self.start_time
        self.start_time = perf_counter()
        time = divmod(int(self.time), 60)
        return f"{round(time[0]):02d}:{round(time[1]):02d}", self.time


def Exam(Display: pygame.Surface, Clock: pygame.time.Clock, showtitle = True):
    _quit = False
    background = pygame.image.load("Assets/Textures/UI/exam_background.png").convert()
    exam_paper = pygame.image.load("Assets/Textures/UI/exam_paper.png").convert()
    exam_paper = pygame.transform.scale(exam_paper, (round(exam_paper.get_width() * 1.7), round(exam_paper.get_height() * 1.7)))
    exam_music = pygame.mixer.Sound("Assets/Audio/Music/exam_music.ogg")
    pencil_scribbles = (pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble1.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble2.ogg"))
    page_turning = (pygame.mixer.Sound("Assets/Audio/effects/page_turning0.ogg"), pygame.mixer.Sound("Assets/Audio/effects/page_turning1.ogg"), pygame.mixer.Sound("Assets/Audio/effects/page_turning2.ogg"))
    title = "Pistokoe"
    titleFont = pygame.font.SysFont("Arial", 100)
    timerFont = pygame.font.SysFont("Arial", 40)
    examTestFont = pygame.font.SysFont("Calibri", 20)
    gradeFont = pygame.font.Font("Assets/Fonts/schoolhandwriting.ttf", 75)
    titleSurf = titleFont.render(title, False, KDS.Colors.White)

    x_texture = examTestFont.render("X", False, KDS.Colors.Black)
    time_ended = titleFont.render("Aika loppui!", False, KDS.Colors.Red)

    question_maxwidth = exam_paper.get_width() - 18
    exam_paper_height = exam_paper.get_height()
    exam_score = 0.00
    question_indent = 20

    class Question:
        def __init__(self, question: str, options: Dict[str, bool]):

            def splitToRows(string_value, max_width):
                _t_rows = []
                words = string_value.split()
                c = 1
                while c > 0:
                    c = len(words)
                    while True:
                        if examTestFont.size(" ".join(words[ : c]))[0] < max_width:
                            _t_rows.append(examTestFont.render(" ".join(words[ : c]), False, KDS.Colors.Black))
                            words = words[c : ]
                            break
                        c -= 1
                return _t_rows
            
            t_rows = splitToRows(question, question_maxwidth)

            option_keys_shuffled = list(options.keys())
            random.shuffle(option_keys_shuffled)
            for option in option_keys_shuffled:
                o_trows = splitToRows(option, question_maxwidth - question_indent)
                s_bool = options[option]
                options[option] = {"surface": pygame.Surface((question_maxwidth, (len(o_trows) - 1) * o_trows[0].get_height())),
                                    "s_bool": s_bool,
                                    "selected": False,
                                    "rect": None}
                del s_bool
                options[option]["surface"].fill(KDS.Colors.White)
                options[option]["surface"].set_colorkey(KDS.Colors.White)
                for index, row in enumerate(o_trows):
                    options[option]["surface"].blit(row, (0, index * row.get_height()))

            self.qsurf = pygame.Surface((question_maxwidth, (len(t_rows) + 1) * t_rows[0].get_height() + len(options) * t_rows[0].get_height())).convert()
            self.qsurf.fill(KDS.Colors.White)

            b_index = 0
            for index, row in enumerate(t_rows):
                self.qsurf.blit(row, (0, index * row.get_height()))
                if index == len(t_rows) - 1: b_index = index * row.get_height() + row.get_height()

            for index, question in enumerate(option_keys_shuffled):
                surface_height = options[question]["surface"].get_height()
                options[question]["rect"] = pygame.Rect(0, b_index + index * surface_height, question_indent - question_indent / 5, surface_height)
                pygame.draw.rect(self.qsurf, KDS.Colors.Black, options[question]["rect"], 1)
                self.qsurf.blit(options[question]["surface"], (question_indent, b_index + index * surface_height))
                
            self.options = options
            self.qsurf.set_colorkey(KDS.Colors.White)

        def update(self, relative_mouse_position, clicked):
            for option in self.options.keys():
                if self.options[option]["rect"].collidepoint(relative_mouse_position) and clicked: 
                    if not self.options[option]["selected"]:
                        KDS.Audio.PlaySound(random.choice(pencil_scribbles))
                        self.options[option]["selected"] = True
                        self.qsurf.blit(pygame.transform.scale(x_texture, self.options[option]["rect"].size), self.options[option]["rect"].topleft)                 
                    else: 
                        self.options[option]["selected"] = False
                        pygame.draw.rect(self.qsurf, KDS.Colors.White, self.options[option]["rect"])
                        pygame.draw.rect(self.qsurf, KDS.Colors.Black, self.options[option]["rect"], 1)

    def showTitle(_title):
        counter = 0
        relative_position = (1200 / 2 - _title.get_width() / 2, 800 / 2 - _title.get_height() / 2)
        while counter <= 180:
            Display.fill(KDS.Colors.Black)
            _title.set_alpha(KDS.Math.Sin(counter * KDS.Math.DEG2RAD) * 255)
            Display.blit(_title, (KDS.Math.Floor(relative_position[0]), KDS.Math.Floor(relative_position[1])))
            pygame.display.flip()
            Clock.tick_busy_loop(60)
            counter += 1
    
    def checkAnswers(lstc: List[List[Question]]) -> float:
        questions_correct = 0
        questions_amount = 0
        for page in lstc:
            for question in page:
                questions_amount += 1
                totalTrueQuestions = 0
                totalTrueQuestionsRight = 0
                point = True
                for option in question.options.keys():
                    if not question.options[option]["s_bool"] and question.options[option]["selected"]:
                        point = False
                        break
                    if question.options[option]["s_bool"]:
                        totalTrueQuestions += 1
                        if question.options[option]["selected"]: totalTrueQuestionsRight += 1
                if point: questions_correct += totalTrueQuestionsRight / totalTrueQuestions
        
        return questions_correct / questions_amount


    def loadQuestions(path: str, amount = 5):
        qs = []
        loaded_questions = []
        rawData: Dict[str, Dict[str, bool]] = {}
        with open(path, "r", encoding="utf-8") as qfile:
            tmp = qfile.read()
            rawData = json.loads(tmp)

        while len(qs) < amount:
            temp_qs = random.choice(list(rawData.keys()))
            if temp_qs not in loaded_questions:
                loaded_questions.append(temp_qs)
                qs.append(Question(temp_qs, rawData[temp_qs]))
        return qs

    def exam():
        nonlocal _quit
        questions = []
        relative_position = (1200 / 2 - exam_paper.get_width() / 2, 800 / 2 - exam_paper.get_height() / 2)

        KDS.Audio.PlaySound(pygame.mixer.Sound("Assets/Audio/effects/exam_start.ogg"))
        if showtitle: showTitle(titleSurf)
        pygame.mouse.set_visible(True)
        questions = loadQuestions("Assets/Data/examQuestions.kdf", amount=random.randint(10, 13))

        page_index = 0
        pages = []
        vertical_offset = 0
        temp_page_index = 0
        for question in questions:
            if question.qsurf.get_height() < exam_paper_height - vertical_offset - 50:
                if vertical_offset == 0: pages.append([])
                pages[temp_page_index].append(question)
                vertical_offset += question.qsurf.get_height()
            else:
                vertical_offset = 0
                temp_page_index += 1
        del temp_page_index, vertical_offset, questions

        class pageButton:
            def __init__(self, position: tuple, function, texture, hover_texture):
                self.texture = texture; self.texture.set_colorkey(KDS.Colors.White)
                self.h_texture = hover_texture; self.h_texture.set_colorkey(KDS.Colors.White)
                self.rect = pygame.Rect(position[0], position[1], texture.get_width(), texture.get_height())
                self.function = function

            def update(self, mouse_pos, clicked):
                if self.rect.collidepoint(mouse_pos):
                    Display.blit(self.h_texture, self.rect.topleft)
                    if clicked: self.function()
                else:
                    Display.blit(self.texture, self.rect.topleft)

        exam_running = True
        Display.blit(background, (0, 0))
        Display.blit(exam_paper, relative_position)
        pygame.display.flip()

        def page_return():
            nonlocal page_index
            page_index -= 1
            KDS.Audio.PlaySound(random.choice(page_turning))

        def page_next():
            nonlocal page_index
            page_index += 1
            KDS.Audio.PlaySound(random.choice(page_turning))

        def return_exam():
            nonlocal exam_running, _quit, exam_score
            oldSurf = Display.copy()
            exam_music.stop()
            exam_returned = pygame.mixer.Sound("Assets/Audio/effects/exam_returned.ogg")
            KDS.Audio.PlaySound(exam_returned)

            class scoreRational(object):

                rational_spares = [0, 0.25, 0.5, 0.75, 1]
                rational_marks = {0: "", 0.25: "+", 0.5: "½", 0.75: "-"}

                @staticmethod
                def closestTo(lst: list, value):
                    return min(lst, key= lambda lst_value : abs(value - lst_value))

                def __init__(self, value: float):
                    self.value = value
                    self.raw_value = value
                    self.rational = (value - KDS.Math.Floor(value))
                    self.rational_mark = ""

                    closest_1f = scoreRational.closestTo(scoreRational.rational_spares, self.rational)
                    self.raw_value = KDS.Math.Floor(self.raw_value) + closest_1f
                    if closest_1f == 1 or closest_1f == 0.75: 
                        self.value = KDS.Math.Ceil(self.value)
                        self.rational_mark = "-" if closest_1f == 0.75 else ""
                    else:
                        self.rational_mark = scoreRational.rational_marks[closest_1f]
                
                def __str__(self):
                    return f"{self.value}{self.rational_mark}"

            score = checkAnswers(pages)
            score_formatted = 0
            passLine = KDS.ConfigManager.GetGameData("Exam/passLine")
            passed_stamp = pygame.image.load("Assets/Textures/UI/passed_stamp.png").convert(); passed_stamp.set_colorkey(KDS.Colors.White)
            failed_stamp = pygame.image.load("Assets/Textures/UI/failed_stamp.png").convert(); failed_stamp.set_colorkey(KDS.Colors.White)
            stamp = None
            scoreSurf = None
            stamp_size = (270, 125)
            passed_stamp = pygame.transform.scale(passed_stamp, stamp_size); failed_stamp = pygame.transform.scale(failed_stamp, stamp_size)
            #Ethän vielä poista noita stamp rivejä, jos satut tänne tekemään jotain
            timer2 = Timer(7.5)
            timer3 = Timer(6)
            timer2.start()
            timer_finished = False

            gradePos = None
            gradeDestination = None

            check_running = True
            while check_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        check_running = False
                        _quit = True

                if round(timer2.get_time()[1]) <= 0 and not timer_finished:
                    timer_finished = True
                    timer3.start()
                    exam_returned.stop()
                    if score < passLine: score_formatted = scoreRational(4)
                    else:
                        grade_slope = (10 - 4) / (1 - passLine)
                        f_score = 4 + grade_slope * (score - passLine)
                        score_formatted = scoreRational(f_score)
                        exam_score = score_formatted.raw_value
                    scoreSurf = gradeFont.render(f"{score_formatted}", False, KDS.Colors.Red)
                    gradePos = [relative_position[0] + exam_paper.get_width(), relative_position[1] + exam_paper.get_height()]
                    gradeDestination = (relative_position[0] + exam_paper.get_width() - scoreSurf.get_width() - random.randint(20, 40), relative_position[1] + random.randint(20, 40))
                    if score < passLine: KDS.Audio.PlayFromFile("Assets/Audio/effects/exam_failed.ogg")
                    else: KDS.Audio.PlayFromFile("Assets/Audio/effects/exam_passed.ogg")

                Display.blit(oldSurf, (0, 0))

                if timer_finished:
                    if timer3.get_time()[1] <= 0: check_running = False
                    gradePos[0] += KDS.Math.Floor((gradePos[0] - gradeDestination[1]) / 30)
                    gradePos[1] += KDS.Math.Floor((gradePos[1] - gradeDestination[1]) / 30)
                    scaling_factor = (KDS.Math.Floor(gradePos[1] - gradeDestination[1] + 1) + KDS.Math.Floor(gradePos[0] - gradeDestination[0] + 1)) / 2
                    print(scaling_factor)
                    surface = pygame.transform.scale(scoreSurf, (round(scoreSurf.get_width() * scaling_factor), round(scoreSurf.get_height() * scaling_factor)))
                    Display.blit(scoreSurf, gradeDestination)
                    
                pygame.display.flip()
            exam_running = False

        pg_button1 = pygame.image.load("Assets/textures/UI/Buttons/page_arrow_red.png").convert()
        pg_button1 = pygame.transform.scale(pg_button1, (round(pg_button1.get_width() / 2), round(pg_button1.get_height() / 2)))
        pg_button2 = pygame.image.load("Assets/textures/UI/Buttons/palauta_red.png").convert()
        pg_button2 = pygame.transform.scale(pg_button2, (round(pg_button2.get_width() / 2), round(pg_button2.get_height() / 2)))

        page_return_button = pageButton((relative_position[0] + 5, relative_position[1] + exam_paper.get_height() - 55),
                                         page_return, 
                                         pygame.transform.flip(KDS.Convert.ToGrayscale(pg_button1), True, False),
                                         pygame.transform.flip(pg_button1, True, False))

        page_next_button = pageButton((relative_position[0] + exam_paper.get_width() - 5 - pg_button1.get_width(), relative_position[1] + exam_paper.get_height() - 55),
                                         page_next, 
                                         KDS.Convert.ToGrayscale(pg_button1),
                                         pg_button1)

        exam_return_button = pageButton((relative_position[0] + exam_paper.get_width() / 2 - pg_button2.get_width() / 2, relative_position[1] + exam_paper.get_height() - 55),
                                         return_exam, 
                                         KDS.Convert.ToGrayscale(pg_button2),
                                         pg_button2)

        timer = Timer(random.randint(75, 95))
        timer.start()
        KDS.Audio.PlaySound(exam_music, loops = -1)

        c = False
        while exam_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if KDS.System.MessageBox.Show("Quit?", "Are you sure you want to quit?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
                        _quit = True
                        return
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1: c = True
                elif event.type == KEYDOWN:
                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()
                        KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.type == KEYUP:
                    if event.key == K_LEFT: 
                        last_page_index = page_index 
                        page_index = max(0, page_index -1)
                        if last_page_index != page_index: KDS.Audio.PlaySound(random.choice(page_turning))
                    elif event.key == K_RIGHT:
                        last_page_index = page_index
                        page_index = min(len(pages) - 1, page_index + 1)
                        if last_page_index != page_index: KDS.Audio.PlaySound(random.choice(page_turning))

            Display.blit(background, (0, 0))
            Display.blit(exam_paper, relative_position)
            
            lastYoffset = 0
            for question in pages[page_index]:
                rel_mpos = list(pygame.mouse.get_pos())
                rel_mpos[0] -= (relative_position[0] + 10)
                rel_mpos[1] -= (relative_position[1] + 10 + lastYoffset)
                question.update(rel_mpos, c)
                del rel_mpos
                Display.blit(question.qsurf, (relative_position[0] + 10, relative_position[1] + 10 + lastYoffset))
                lastYoffset += question.qsurf.get_height()

            mouse_position = pygame.mouse.get_pos()
            strtime, nmtime = timer.get_time()
            if page_index > 0: page_return_button.update(mouse_position, c)
            if page_index < len(pages) - 1: page_next_button.update(mouse_position, c)
            exam_return_button.update(mouse_position, c)
            if nmtime < 0:
                exam_music.stop()
                oldSurf = Display.copy()
                KDS.Audio.PlayFromFile("Assets/Audio/effects/timeup.ogg")
                for x in range(0, Display.get_width() + time_ended.get_width(), int(Display.get_width() / 100)):
                    Display.blit(oldSurf, (0, 0))
                    Display.blit(time_ended, (x - time_ended.get_width() + 10, Display.get_height() / 2 - time_ended.get_height() / 2))
                    pygame.display.flip()
                    Clock.tick_busy_loop(60)
                return_exam()
            Display.blit(timerFont.render(strtime, False, KDS.Colors.Red), (10, 10))

            pygame.display.flip()
            Clock.tick_busy_loop(60)
            c = False

        exam_music.stop()
            
    
    exam()
    return _quit, exam_score