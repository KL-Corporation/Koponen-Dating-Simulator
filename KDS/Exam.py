import random
import pygame
from json import loads
from math import sin, radians
from typing import Dict
from pygame.locals import *
import KDS.Colors
from KDS.System import MessageBox

def Exam(Display: pygame.Surface, Clock: pygame.time.Clock, Audio, showtitle = True):
    _quit = False
    background = pygame.image.load("Assets/Textures/UI/exam_background.png").convert()
    exam_paper = pygame.image.load("Assets/Textures/UI/exam_paper.png").convert()
    exam_paper = pygame.transform.scale(exam_paper, (round(exam_paper.get_width() * 1.7), round(exam_paper.get_height() * 1.7)))
    exam_music = pygame.mixer.Sound("Assets/Audio/Music/exam_music.ogg")
    pencil_scribbles = (pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble1.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble2.ogg"))
    title = "Pistokoe"
    titleFont = pygame.font.SysFont("Arial", 100)
    examTestFont = pygame.font.SysFont("Calibri", 20)
    titleSurf = titleFont.render(title, False, KDS.Colors.White)

    x_texture = examTestFont.render("X", False, KDS.Colors.Black)

    question_maxwidth = exam_paper.get_width() - 18
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
                        s = examTestFont.render(" ".join(words[ : c]), False, KDS.Colors.Black)
                        if s.get_width() < max_width:
                            _t_rows.append(s)
                            words = words[c : ]
                            break
                        c -= 1
                return _t_rows
            
            t_rows = splitToRows(question, question_maxwidth)

            for option in options.keys():
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
            for index, question in enumerate(options.keys()):
                options[question]["rect"] = pygame.Rect(0, b_index + index * options[question]["surface"].get_height(), question_indent - question_indent / 5, options[question]["surface"].get_height())
                pygame.draw.rect(self.qsurf, KDS.Colors.Black, options[question]["rect"], 1)
                self.qsurf.blit(options[question]["surface"], (question_indent, b_index + index * options[question]["surface"].get_height()))
            self.options = options
            self.qsurf.set_colorkey(KDS.Colors.White)

        def update(self, relative_mouse_position, clicked):
            for option in self.options.keys():
                if self.options[option]["rect"].collidepoint(relative_mouse_position) and clicked: 
                    pygame.draw.rect(self.qsurf, KDS.Colors.White, self.options[option]["rect"])
                    pygame.draw.rect(self.qsurf, KDS.Colors.Black, self.options[option]["rect"], 1)
                    if not self.options[option]["selected"]:
                        Audio.playSound(random.choice(pencil_scribbles))
                        self.options[option]["selected"] = True
                        self.qsurf.blit(pygame.transform.scale(x_texture, (self.options[option]["rect"].w, self.options[option]["rect"].h)), self.options[option]["rect"].topleft)
                    else: self.options[option]["selected"] = False

    def showTitle(_title):
        counter = 0
        relative_position = (1200 / 2 - _title.get_width() / 2, 800 / 2 - _title.get_height() / 2)
        while counter <= 180:
            Display.fill(KDS.Colors.Black)
            _title.set_alpha(sin(radians(counter)) * 255)
            Display.blit(_title, relative_position)
            pygame.display.flip()
            Clock.tick_busy_loop(60)
            counter += 1

    def loadQuestions(path: str, amount = 5):
        qs = []
        loaded_questions = []
        rawData = {}
        with open(path, 'r') as qfile:
            rawData = loads(qfile.read())

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

        if showtitle: showTitle(titleSurf)
        Audio.playSound(exam_music, loops = -1)
        pygame.mouse.set_visible(True)
        questions = loadQuestions("Assets/exam_questions.kdf", 1)

        exam_running = True
        Display.blit(background, (0, 0))
        Display.blit(exam_paper, relative_position)
        pygame.display.flip()
        c = False
        while exam_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if MessageBox.Show("Quit?", "Are you sure you want to quit?", MessageBox.Buttons.YESNO, MessageBox.Icon.WARNING) == MessageBox.Responses.YES:
                        _quit = True
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        c = True

            Display.blit(background, (0, 0))
            Display.blit(exam_paper, relative_position)
            
            lastYoffset = 0
            for question in questions:
                rel_mpos = list(pygame.mouse.get_pos())
                rel_mpos[0] -= (relative_position[0] + 10)
                rel_mpos[1] -= (relative_position[1] + 10 + lastYoffset)
                question.update(rel_mpos, c)
                del rel_mpos
                Display.blit(question.qsurf, (relative_position[0] + 10, relative_position[1] + 10 + lastYoffset))
                lastYoffset += question.qsurf.get_height()

            pygame.display.flip()
            Clock.tick_busy_loop(60)
            c = False
        
        exam_music.stop()
            
    
    exam()
    return _quit