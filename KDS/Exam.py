import random
import pygame
import numpy
import json
from math import sin, radians
from typing import Dict, List, Union
from pygame.locals import *
import KDS.Colors
from KDS.Convert import ToGrayscale
from KDS.System import MessageBox

def Exam(Display: pygame.Surface, Clock: pygame.time.Clock, Audio, CM, showtitle = True):
    _quit = False
    background = pygame.image.load("Assets/Textures/UI/exam_background.png").convert()
    exam_paper = pygame.image.load("Assets/Textures/UI/exam_paper.png").convert()
    exam_paper = pygame.transform.scale(exam_paper, (round(exam_paper.get_width() * 1.7), round(exam_paper.get_height() * 1.7)))
    exam_music = pygame.mixer.Sound("Assets/Audio/Music/exam_music.ogg")
    pencil_scribbles = (pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble1.ogg"), pygame.mixer.Sound("Assets/Audio/effects/pencil_scribble2.ogg"))
    page_turning = (pygame.mixer.Sound("Assets/Audio/effects/page_turning0.ogg"), pygame.mixer.Sound("Assets/Audio/effects/page_turning1.ogg"), pygame.mixer.Sound("Assets/Audio/effects/page_turning2.ogg"))
    title = "Pistokoe"
    titleFont = pygame.font.SysFont("Arial", 100)
    examTestFont = pygame.font.SysFont("Calibri", 20)
    titleSurf = titleFont.render(title, False, KDS.Colors.White)

    x_texture = examTestFont.render("X", False, KDS.Colors.Black)

    question_maxwidth = exam_paper.get_width() - 18
    exam_paper_height = exam_paper.get_height()
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

        if showtitle: showTitle(titleSurf)
        Audio.playSound(exam_music, loops = -1)
        pygame.mouse.set_visible(True)
        questions = loadQuestions("Assets/Data/examQuestions.kdf", amount=10)

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
            Audio.playSound(random.choice(page_turning))

        def page_next():
            nonlocal page_index
            page_index += 1
            Audio.playSound(random.choice(page_turning))

        def return_exam():
            pass

        pg_button1 = pygame.image.load("Assets/textures/UI/Buttons/page_arrow_red.png").convert()
        pg_button1 = pygame.transform.scale(pg_button1, (round(pg_button1.get_width() / 2), round(pg_button1.get_height() / 2)))
        pg_button2 = pygame.image.load("Assets/textures/UI/Buttons/palauta_red.png").convert()
        pg_button2 = pygame.transform.scale(pg_button2, (round(pg_button2.get_width() / 2), round(pg_button2.get_height() / 2)))

        page_return_button = pageButton((relative_position[0] + 5, relative_position[1] + exam_paper.get_height() - 55),
                                         page_return, 
                                         pygame.transform.flip(ToGrayscale(pg_button1), True, False),
                                         pygame.transform.flip(pg_button1, True, False))

        page_next_button = pageButton((relative_position[0] + exam_paper.get_width() - 5 - pg_button1.get_width(), relative_position[1] + exam_paper.get_height() - 55),
                                         page_next, 
                                         ToGrayscale(pg_button1),
                                         pg_button1)

        exam_return_button = pageButton((relative_position[0] + exam_paper.get_width() / 2 - pg_button2.get_width() / 2, relative_position[1] + exam_paper.get_height() - 55),
                                         page_next, 
                                         ToGrayscale(pg_button2),
                                         pg_button2)

        c = False
        while exam_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if MessageBox.Show("Quit?", "Are you sure you want to quit?", MessageBox.Buttons.YESNO, MessageBox.Icon.WARNING) == MessageBox.Responses.YES:
                        _quit = True
                        return
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1: c = True
                elif event.type == KEYDOWN:
                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()
                        CM.SetSetting("Renderer/fullscreen", not CM.GetSetting("Renderer/fullscreen", False))
                elif event.type == KEYUP:
                    if event.key == K_LEFT: 
                        last_page_index = page_index 
                        page_index = max(0, page_index -1)
                        if last_page_index != page_index: Audio.playSound(random.choice(page_turning))
                    elif event.key == K_RIGHT:
                        last_page_index = page_index
                        page_index = min(len(pages) - 1, page_index + 1)
                        if last_page_index != page_index: Audio.playSound(random.choice(page_turning))

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
            if page_index > 0: page_return_button.update(mouse_position, c)
            if page_index < len(pages) - 1: page_next_button.update(mouse_position, c)
            exam_return_button.update(mouse_position, c)

            pygame.display.flip()
            Clock.tick_busy_loop(60)
            c = False
        
        exam_music.stop()
            
    
    exam()
    return _quit