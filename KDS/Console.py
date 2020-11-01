import re
import KDS.Colors
import pygame
from pygame.locals import *
pygame.init()
#region Settings
console_font = pygame.font.SysFont("Consolas", 25, bold=0, italic=0)
text_input_rect = pygame.Rect(0, 0, 800, 100)
#endregion

class RegexPresets:
    @staticmethod
    def Tuple(length: int, min_val: int, max_val: int):
        regex = r""
        for i in range(length):
            regex += f"[{min_val}-{max_val}]"
            if i < length - 1:
                regex += r",\s?"
        return regex

def Start(surface, prompt: str = "Enter Command:") -> str:
    cmd = r""
    running = True
    pygame.key.start_text_input()
    pygame.key.set_text_input_rect(text_input_rect)
    while running:
        for event in pygame.event.get():
            if event.type == TEXTEDITING:
                cmd = event.text
                print(event.text)
            elif event.type == TEXTINPUT:
                cmd += event.text
                print(event.text)
            elif event.type == QUIT:
                running = False
        pygame.draw.rect(surface, KDS.Colors.DarkGray, text_input_rect)
        surface.blit(console_font.render(cmd, True, (255, 255, 255)), (0, 0))
        pygame.display.update()
    return ""