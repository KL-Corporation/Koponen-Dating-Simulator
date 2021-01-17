import random
import pygame
from json import load, loads
from math import sin, radians
from typing import List
from pygame.locals import *
import KDS.Colors
from KDS.System import MessageBox

def Exam(Display: pygame.Surface, Clock: pygame.time.Clock, Audio, showtitle = True):
    _quit = False
    background = pygame.image.load("Assets/Textures/UI/exam_background.png").convert()
    exam_paper = pygame.image.load("Assets/Textures/UI/exam_paper.png").convert()
    exam_paper = pygame.transform.scale(exam_paper, (round(exam_paper.get_width() * 1.7), round(exam_paper.get_height() * 1.7)))
    exam_music = pygame.mixer.Sound("Assets/Audio/Music/exam_music.ogg")
    title = "Pistokoe"
    titleFont = pygame.font.SysFont("Arial", 100)
    examTestFont = pygame.font.SysFont("Calibri", 20)
    titleSurf = titleFont.render(title, False, KDS.Colors.White)

    question_maxwidth = exam_paper.get_width() - 18

    class Question:
        def __init__(self, question: str, options: List[str]):
            t_rows = []
            words = question.split()
            c = 1
            while c > 0:
                c = len(words)
                while True:
                    s = examTestFont.render(" ".join(words[ : c]), False, KDS.Colors.Black)
                    if s.get_width() < question_maxwidth:
                        t_rows.append(s)
                        words = words[c : ]
                        break
                    c -= 1

            self.qsurf = pygame.Surface((question_maxwidth, len(t_rows) * t_rows[0].get_height()))
            self.qsurf.fill(KDS.Colors.White)
            for index, row in enumerate(t_rows):
                self.qsurf.blit(row, (0, index * row.get_height()))
            self.qsurf.set_colorkey(KDS.Colors.White)

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
            print(len(qs), amount)
            temp_qs = rawData[random.choice(list(rawData.keys()))]
            if temp_qs["question"] not in loaded_questions:
                print("Added question")
                loaded_questions.append(temp_qs["question"])
                qs.append(Question(temp_qs["question"], temp_qs["choices"]))
        
        #qs.append(Question("Homopippelipeenis kakka himmeli kakka saatanan pippeli himmeli suututewhds ass", ["Oikea", "Vaara", "Hehehe V"]))
        return qs

    def exam():
        nonlocal _quit
        questions = []
        relative_position = (1200 / 2 - exam_paper.get_width() / 2, 800 / 2 - exam_paper.get_height() / 2)

        if showtitle: showTitle(titleSurf)
        Audio.playSound(exam_music, loops = -1)
        pygame.mouse.set_visible(True)
        questions = loadQuestions("Assets/exam_questions.kdf", 4)

        exam_running = True
        Display.blit(background, (0, 0))
        Display.blit(exam_paper, relative_position)
        pygame.display.flip()
        while exam_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if MessageBox.Show("Quit?", "Are you sure you want to quit?", MessageBox.Buttons.YESNO, MessageBox.Icon.WARNING) == MessageBox.Responses.YES:
                        _quit = True
                        return

            Display.blit(background, (0, 0))
            Display.blit(exam_paper, relative_position)
            
            lastYoffset = 0
            for question in questions:
                Display.blit(question.qsurf, (relative_position[0] + 10, relative_position[1] + 10 + lastYoffset))
                lastYoffset += question.qsurf.get_height()

            pygame.display.flip()
            Clock.tick_busy_loop(60)
        
        exam_music.stop()
            
    
    exam()
    return _quit