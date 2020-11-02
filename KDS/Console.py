import re
import KDS.Colors
import KDS.Animator
import pygame
from pygame.locals import *
pygame.init()
pygame.key.stop_text_input()
#region Settings
console_font = pygame.font.SysFont("Consolas", 25, bold=0, italic=0)
console_font_small = pygame.font.SysFont("Consolas", 15, bold=0, italic=0)
text_input_rect = pygame.Rect(0, 750, 1200, 50)
text_rect = pygame.Rect(10, 750, 1180, 50)
cursor_width = 3
matchChars = r" ; , \/ \\ \" "
#endregion

def init(_window, _display, _display_size, _Fullscreen, _clock):
    global window, display, display_size, Fullscreen, clock
    window = _window
    display = _display
    display_size = _display_size
    Fullscreen = _Fullscreen
    clock = _clock

class RegexPresets:
    @staticmethod
    def Tuple(length: int, min_val: int, max_val: int):
        regex = r""
        for i in range(length):
            regex += f"[{min_val}-{max_val}]"
            if i < length - 1:
                regex += r",\s?"
        return regex

def Start(prompt: str = "Enter Command:", allowEscape: bool = True, regex: str = None, background: pygame.Surface = None, *commands) -> str:
    cmd = r""
    running = True
    pygame.key.set_text_input_rect(text_input_rect)
    pygame.key.start_text_input()
    textInput = True
    cursor_index = 0
    cursor_animation = KDS.Animator.Float(2.0, 0.0, 64, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
    pygame.key.set_repeat(500, 31)
    while running:
        for event in pygame.event.get():
            if event.type == TEXTINPUT:
                cmd = cmd[:cursor_index] + event.text + cmd[cursor_index:]
                cursor_index += 1
                cursor_animation.tick = 0
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]:
                        if len(cmd[:cursor_index]) > 0:
                            cmd = cmd[:cursor_index][:-1] + cmd[cursor_index:]
                            cursor_index -= 1
                    else:
                        rmv = cmd[:cursor_index].rstrip(matchChars)
                        split1 = re.findall(f"[{matchChars}]", rmv)
                        split2 = re.split(f"[{matchChars}]", rmv)
                        rmv_split = [split2[i] + split1[i] for i in range(len(split1))]
                        cmd = "".join(rmv_split) + cmd[cursor_index:]
                        cursor_index = len("".join(rmv_split))
                elif event.key == K_DELETE:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]:
                        if len(cmd[cursor_index:]) > 0:
                            cmd = cmd[:cursor_index] + cmd[cursor_index:][1:]
                    else:
                        pass
                elif event.key == K_RETURN and allowEscape:
                    pygame.key.stop_text_input()
                    textInput = False
                    running = False
                elif event.key == K_ESCAPE and allowEscape:
                    cmd = r""
                    running = False
                elif event.key == K_LEFT:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]: cursor_index = max(cursor_index - 1, 0)
                    elif cursor_index > 0:
                        tst = cmd[:cursor_index - 1].strip(matchChars)
                        found = re.findall(f"[{matchChars}]", tst)
                        if len(found) > 0: cursor_index = cmd[:cursor_index - 1].rfind(found[0]) + 1
                        else: cursor_index = 0
                    else: cursor_index = 0
                elif event.key == K_RIGHT:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]: cursor_index = min(cursor_index + 1, len(cmd))
                    elif cursor_index < len(cmd):
                        tst = cmd[cursor_index:].strip(matchChars)
                        found = re.findall(f"[{matchChars}]", tst)
                        if len(found) > 0: cursor_index = tst.find(found[-1]) + (len(cmd) - len(cmd[cursor_index:])) + 1
                        else: cursor_index = len(cmd)
                    else: cursor_index = len(cmd)
            elif event.type == MOUSEBUTTONDOWN:
                cursor_animation.tick = 0
                if text_input_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.key.start_text_input()
                    textInput = True
                else:
                    pygame.key.stop_text_input()
                    textInput = False
            elif event.type == QUIT and allowEscape:
                cmd = r""
                pygame.key.stop_text_input()
                textInput = False
                running = False

        while console_font.size(cmd)[0] + cursor_width >= text_rect.width: cmd = cmd[:-1]

        pygame.draw.rect(display, KDS.Colors.DarkGray, text_input_rect)
        text = console_font.render(cmd, True, (192, 192, 192))
        text_y = text_rect.y + text_rect.height / 2 - console_font.get_height() / 2
        display.blit(text, (text_rect.left, text_y))
        if textInput and cursor_animation.update() >= 1.0:
            pygame.draw.rect(display, (192, 192, 192), pygame.Rect(text_rect.left + console_font.size(cmd[:cursor_index])[0], text_y, cursor_width, console_font.get_height()))

        if regex != None:
            if len(re.findall(regex, cmd)) != 1:
                pygame.draw.rect(display, (255, 255, 255, 128), pygame.Rect(text_rect.left, text_rect.top, text.get_width(), text_rect.height))
        
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        display.fill(KDS.Colors.Black)
        window.fill(KDS.Colors.Black)
        clock.tick(60)
        
    pygame.key.set_repeat(0, 0)
    return cmd