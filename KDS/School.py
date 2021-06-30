import re
from typing import Any, Dict, List, Optional, Set, SupportsFloat, Tuple
import pygame
from pygame.locals import *
import random
from time import perf_counter
import json
import KDS.Animator
import KDS.Colors
import KDS.Audio
import KDS.ConfigManager
import KDS.Convert
import KDS.System
import KDS.Math
import KDS.Logging
import KDS.Debug
import KDS.UI
import KDS.Linq
import KDS.Keys
import KDS.Clock
import datetime

class Timer:
    def __init__(self, start_time: SupportsFloat = 60) -> None:
        self.time = float(start_time)
        self.start_time = 0

    def start(self) -> None:
        self.start_time = perf_counter()

    def get_time(self) -> Tuple[str, float]:
        self.time -= perf_counter() - self.start_time
        self.start_time = perf_counter()
        time = divmod(int(self.time), 60)
        return f"{round(time[0]):02d}:{round(time[1]):02d}", self.time


def init(display: pygame.Surface):
    global Display, Surnames, SurnamesSet, GradeWeights
    Display = display

    try:
        with open("Assets/Data/surnames.txt", encoding="utf-8") as f:
            Surnames = f.read().splitlines()
            SurnamesSet = set(Surnames)
    except Exception as e:
        KDS.Logging.AutoError(f"Could not load surnames. Exception below:\n{e}")
        Surnames = None
        SurnamesSet: Set[str] = set()

    GradeWeights = tuple(KDS.ConfigManager.GetGameData("Certificate/Grading/weights").values())

def Exam(showtitle = True):
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
    gradeFont = pygame.font.SysFont("Comic Sans MS", 45)
    titleSurf = titleFont.render(title, False, KDS.Colors.White)

    x_texture = examTestFont.render("X", False, KDS.Colors.Black)
    time_ended = titleFont.render("Aika loppui!", False, KDS.Colors.Red)

    question_maxwidth = exam_paper.get_width() - 18
    exam_paper_height = exam_paper.get_height()
    exam_score = 0.00
    question_indent = 20

    class Question:
        def __init__(self, question: str, _options: Dict[str, bool]):

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

            options: Dict[str, Dict[str, Any]] = {}

            option_keys_shuffled = list(_options.keys())
            random.shuffle(option_keys_shuffled)
            for option in option_keys_shuffled:
                o_trows = splitToRows(option, question_maxwidth - question_indent)
                s_bool = _options[option]
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

    def showTitle(_title: pygame.Surface):
        counter = 0
        relative_position = (1200 / 2 - _title.get_width() / 2, 800 / 2 - _title.get_height() / 2)
        while counter <= 180:
            Display.fill(KDS.Colors.Black)
            val = KDS.Math.Sin(counter * KDS.Math.DEG2RAD)
            if val < 1.0: _title.set_alpha(int(val * 255))
            Display.blit(_title, (KDS.Math.FloorToInt(relative_position[0]), KDS.Math.FloorToInt(relative_position[1])))
            pygame.display.flip()
            KDS.Clock.Tick()
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
        question_amount = random.randint(10, 13)
        questions = loadQuestions("Assets/Data/examQuestions.kdf", amount=question_amount)

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

            class scoreRational:
                def __init__(self, value: float):
                    self.raw_value = value
                    fraction, base = KDS.Math.SplitFloat(value)
                    self.value = base + KDS.Math.Closest(fraction, [0.0, 0.25, 0.5, 0.75, 1.0])
                    self.formatted_value = KDS.Convert.ToRational(self.value)

            score = checkAnswers(pages)
            score_formatted = None
            passLine = KDS.ConfigManager.GetGameData("Exam/passLine")
            scoreSurf = pygame.Surface((0, 0))
            # Ethän vielä poista noita stamp rivejä, jos satut tänne tekemään jotain
            # Hups... T: Niko
            timer2 = Timer(7.5)
            timer3 = Timer(6)
            timer2.start()
            timer_finished = False

            gradePos = []
            gradeDestination = []

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
                    if score < passLine:
                        score_formatted = scoreRational(4)
                    else:
                        grade_slope = (10 - 4) / (1 - passLine)
                        f_score = 4 + grade_slope * (score - passLine)
                        score_formatted = scoreRational(f_score)
                        exam_score = score_formatted.value

                    scoreSurf = gradeFont.render(f"""{score_formatted.formatted_value if score_formatted != None else "<score_error>"}""", False, KDS.Colors.Red)

                    gradePos = [random.randint(0, Display.get_width()), random.randint(0, Display.get_height())]
                    gradeDestination = (relative_position[0] + exam_paper.get_width() - scoreSurf.get_width() - random.randint(20, 40), relative_position[1] + random.randint(20, 40))
                    if score < passLine: KDS.Audio.PlayFromFile("Assets/Audio/effects/exam_failed.ogg")
                    else: KDS.Audio.PlayFromFile("Assets/Audio/effects/exam_passed.ogg")

                Display.blit(oldSurf, (0, 0))

                if timer_finished:
                    if timer3.get_time()[1] <= 0: check_running = False
                    gradePos[0] += KDS.Math.FloorToInt((gradeDestination[0] - gradePos[0]) / 10)
                    gradePos[1] += KDS.Math.FloorToInt((gradeDestination[1] - gradePos[1]) / 10)
                    Display.blit(scoreSurf, gradePos)

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

        timer = Timer(10 * question_amount)
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
                    if event.key in KDS.Keys.toggleFullscreen.Bindings:
                        pygame.display.toggle_fullscreen()
                        KDS.ConfigManager.ToggleSetting("Renderer/fullscreen", ...)
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
                    KDS.Clock.Tick()
                return_exam()
            Display.blit(timerFont.render(strtime, False, KDS.Colors.Red), (10, 10))

            if KDS.Debug.Enabled:
                Display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

            pygame.display.flip()
            KDS.Clock.Tick()
            c = False

        exam_music.stop()
        pygame.mouse.set_visible(False)


    exam()
    return _quit, exam_score

def Certificate(display: pygame.Surface, BackgroundColor: Tuple[int, int, int] = None) -> bool:
    pygame.key.set_repeat(500, 31) #temp
    displaySize = display.get_size()

    #region Settings
    GradeExtras: bool = True
    StoryExtras: bool = True
    AlignOverride: bool = False
    GlobalRefrenceOverride: Optional[int] = None
    #endregion

    class Fonts:
        INFO = pygame.font.SysFont("ArialBD", 27)
        GRADE = pygame.font.SysFont("Arial", 18, bold=0)

    surname = None
    if Surnames != None:
        username = KDS.System.GetUserNameEx(KDS.System.EXTENDED_NAME_FORMAT.NameDisplay)
        for check in reversed(username.split(" ")): # reversed because surname is usually after first name and if there are two matches, it picks the most likely one.
            if check in SurnamesSet: # Will be case sensitive, but case insensitivity would be too demanding to process.
                surname = check
                break
        if surname == None:
            surname = random.choice(Surnames[0:50])
            KDS.Logging.info(f"Username: {username} did not contain a surname.", True)
    else:
        surname = "<surname-loading-failed>"

    if AlignOverride:
        surname = "[ALIGN Surname]"

    forename = (KDS.ConfigManager.Save.Active.Story.playerName if KDS.ConfigManager.Save.Active != None else "<name-error>") if not AlignOverride else "[ALIGN Forename]"
    name = f"{surname} {forename}"

    def randomBirthday() -> str:
        start_date = datetime.date(2005, 1, 1)
        end_date = datetime.date(2005, 12, 31)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        return f"{random_date.day}.{random_date.month}.{random_date.year}" if not AlignOverride else "[ALIGN Day].[ALIGN Month].[ALIGN Year]" # Teki niin mieli laittaa 6.9.2005

    def randomGrade(refrenceOverride: float = None) -> int:
        if GlobalRefrenceOverride != None and (4 <= GlobalRefrenceOverride <= 10):
            refrenceOverride = GlobalRefrenceOverride
        elif (KDS.ConfigManager.Save.Active == None or KDS.ConfigManager.Save.Active.Story.examGrade < 0):
            return -1

        ref = KDS.Math.RoundCustomInt((KDS.ConfigManager.Save.Active.Story.examGrade if KDS.ConfigManager.Save.Active != None else -404) if refrenceOverride == None else refrenceOverride, KDS.Math.MidpointRounding.AwayFromZero)
        gradeList = random.choices(
            population=(ref - 2, ref - 1, ref, ref + 1, ref + 2),
            weights=GradeWeights,
            k=1
        )
        return KDS.Math.Clamp(gradeList[0], 4, 10)

    birthday = randomBirthday()

    grades = [randomGrade() for _ in range(12)]
    average = sum(grades) / len(grades)

    if GradeExtras:
        # PE grade lowers depending on average.
        grades[-1] = randomGrade(KDS.Math.Remap(average, 4, 10, 10, 6))

    if StoryExtras:
        # Because of KDS Story Mode,
        # this will ensure that the maths grade is always 10.
        grades[4] = 10

    certificate: pygame.Surface = pygame.image.load("Assets/Textures/UI/certificate.png").convert()
    certificateSize = certificate.get_size()
    if not AlignOverride:
        pygame.draw.rect(certificate, KDS.Colors.White, (60, 170, 500, 90))
        pygame.draw.rect(certificate, KDS.Colors.White, (700, 300, 150, certificateSize[1] - 300))
    certificate.blit(Fonts.INFO.render(name, True, KDS.Colors.Black), (67, 175))
    certificate.blit(Fonts.INFO.render(birthday, True, KDS.Colors.Black), (67, 210))

    posList = [
        305,
        353,
        401,
        450,
        479,
        508,
        537,
        566,
        595,
        624,
        653,
        682
    ]
    for i in range(len(grades)):
        gradeRender = Fonts.GRADE.render(str(grades[i]) if not AlignOverride else "[ALIGN]", True, KDS.Colors.Black)
        certificate.blit(gradeRender, (738, posList[i]))

    animY = KDS.Animator.Value(displaySize[1], displaySize[1] - certificateSize[1], 30, KDS.Animator.AnimationType.EaseOutExpo, KDS.Animator.OnAnimationEnd.Stop)
    if BackgroundColor == None: BackgroundColor = KDS.Colors.Black

    exitV = False

    def exitFunc():
        nonlocal exitV
        exitV = True

    exitButton = KDS.UI.Button(pygame.Rect(displaySize[0] // 2 - 100, 25, 200, 50), exitFunc, "EXIT")

    KDS.Audio.PlayFromFile("Assets/Audio/Effects/paper_slide.ogg")
    while True:
        display.fill(BackgroundColor)
        c = False
        mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True

        if exitV:
            return False

        display.blit(certificate, (displaySize[0] // 2 - certificateSize[0] // 2, animY.update()))
        exitButton.update(display, mousePos, c)

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

        pygame.display.flip()
        KDS.Clock.Tick()