import re
import sys
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
text_rect = pygame.Rect(10, 762, 1180, 25)
text_color = KDS.Colors.LightGray
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
    pygame.scrap.init()
    pygame.scrap.set_mode(SCRAP_CLIPBOARD)

class CheckTypes:
    @staticmethod
    def Int(_min: int = None, _max: int = None):
        #min and max are both inclusive
        return {
            "type": "int",
            "min":_min,
            "max": _max }
    @staticmethod
    def Float(_min: int = None, _max: int = None):
        return {
            "type": "float",
            "min":_min,
            "max": _max }
    @staticmethod
    def Tuple(size: int, _min: int = None, _max: int = None, perfWarning: int = None):
        return {
            "type": "tuple",
            "size": size,
            "min":_min,
            "max": _max,
            "perfWarning": perfWarning #inclusive
            }
    @staticmethod
    def Rect(minPos: int = None, maxPos: int = None, minSize: int = None, maxSize: int = None):
        return {
            "type": "rect",
            "minPos": minPos,
            "maxPos": maxPos,
            "minSize": minSize,
            "maxSize": maxSize,
            "size": 4
        }

def Start(prompt: str = "Enter Command:", allowEscape: bool = True, checkType: CheckTypes and dict = None, background: pygame.Surface = None, commands: tuple[str] = None, showFeed: bool = False) -> str:
    cmd = ""
    renderedCmd = None
    running = True
    pygame.key.set_text_input_rect(text_input_rect)
    pygame.key.start_text_input()
    textInput = True
    cursor_index = 0
    cursor_animation = KDS.Animator.Float(2.0, 0.0, 64, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
    invalid = False
    warning = False
    warnText = console_font_small.render("[PERFORMANCE WARNING]", True, text_color)
    pygame.key.set_repeat(500, 31)
    ovrColor = KDS.Colors.White
    
    def addText(text: str):
        nonlocal cursor_index, cmd
        cmd = cmd[:cursor_index] + text + cmd[cursor_index:]
        cursor_index += 1
        cursor_animation.tick = 0

    while running:
        for event in pygame.event.get():
            if event.type == TEXTINPUT:
                addText(event.text)
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]:
                        if len(cmd[:cursor_index]) > 0:
                            cmd = cmd[:cursor_index][:-1] + cmd[cursor_index:]
                            cursor_index -= 1
                    else:
                        rmv = cmd[:cursor_index].rstrip(matchChars)
                        found = [i.end() for i in re.finditer(f"[{matchChars}][{matchChars}]*", rmv)]
                        if len(found) > 0:
                            cmd = cmd[:found[-1]] + cmd[cursor_index:]
                            cursor_index = found[-1]
                        else:
                            cmd = cmd[cursor_index:]
                            cursor_index = 0
                elif event.key == K_DELETE:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]:
                        if len(cmd[cursor_index:]) > 0: cmd = cmd[:cursor_index] + cmd[cursor_index:][1:]
                    else:
                        rmv = cmd[cursor_index:].lstrip(matchChars)
                        found = [i.start() for i in re.finditer(f"[{matchChars}][{matchChars}]*", rmv)]
                        if len(found) > 0: cmd = cmd[:cursor_index] + cmd[cursor_index + found[0] + (len(cmd[cursor_index:]) - len(rmv)):]
                        else: cmd = cmd[:cursor_index]     
                elif event.key == K_RETURN:
                    if not invalid:
                        pygame.key.stop_text_input()
                        textInput = False
                        running = False
                    elif allowEscape:
                        cmd = ""
                        running = False
                elif event.key == K_ESCAPE and allowEscape:
                    cmd = ""                 
                    running = False
                elif event.key == K_LEFT:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]: cursor_index = max(cursor_index - 1, 0)
                    elif cursor_index > 0:
                        found = [i.end() for i in re.finditer(f"[{matchChars}][{matchChars}]*", f"{cmd[:cursor_index]} ")]
                        if len(found) > 1: cursor_index = found[-2]
                        else: cursor_index = 0
                elif event.key == K_RIGHT:
                    cursor_animation.tick = 0
                    if not pygame.key.get_pressed()[K_LCTRL]: cursor_index = min(cursor_index + 1, len(cmd))
                    elif cursor_index < len(cmd):
                        found = [i.end() for i in re.finditer(f"[{matchChars}][{matchChars}]*", cmd[cursor_index:])]
                        if len(found) > 1: cursor_index = len(cmd[:cursor_index]) + found[0]
                        else: cursor_index = len(cmd)
                elif event.key == K_v and pygame.key.get_pressed()[K_LCTRL]:
                    clipboardText = pygame.scrap.get(SCRAP_TEXT)
                    if clipboardText: addText(clipboardText)
                    #CTRL + V doesn't work because pygame always loses rights to the clipboard...
            elif event.type == MOUSEBUTTONDOWN:
                cursor_animation.tick = 0
                if text_input_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.key.start_text_input()
                    textInput = True
                else:
                    pygame.key.stop_text_input()
                    textInput = False
            elif event.type == QUIT and allowEscape:
                cmd = ""
                pygame.key.stop_text_input()
                textInput = False
                running = False

        while console_font.size(cmd)[0] + cursor_width >= text_rect.width: cmd = cmd[:-1]

        pygame.draw.rect(display, KDS.Colors.DarkGray, text_input_rect)
        renderedCmd = console_font.render(cmd, True, text_color)
        text_y = text_rect.y + text_rect.height / 2 - console_font.get_height() / 2
        display.blit(renderedCmd, (text_rect.left, text_y))
        if textInput and cursor_animation.update() >= 1.0:
            pygame.draw.rect(display, (192, 192, 192), pygame.Rect(text_rect.left + console_font.size(cmd[:cursor_index])[0] - round(cursor_width / 2), text_y, cursor_width, console_font.get_height()))

        invalid = False
        warning = False
        if checkType != None:
            if checkType["type"] == "int":
                if re.fullmatch(r"^[+-]?\d+$", cmd) != None:
                        cmdInt = int(cmd)
                        if cmdInt > sys.maxsize: invalid = True
                        _min = checkType["min"]
                        if _min != None:
                            if min(_min, cmdInt) != _min: invalid = True
                        _max = checkType["max"]
                        if _max != None:
                            if max(_max, cmdInt) != _max: invalid = True
                else: invalid = True
            elif checkType["type"] == "float":
                
                if re.fullmatch(r"^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$", cmd) != None:
                    cmdFloat = float(cmd)
                    if cmdFloat > sys.maxsize: invalid = True
                    _min = checkType["min"]
                    if _min != None:
                        if min(_min, cmdFloat) != _min: invalid = True
                    _max = checkType["max"]
                    if _max != None:
                        if max(_max, cmdFloat) != _max: invalid = True
                else: invalid = True
                
            elif checkType["type"] in ("tuple", "rect"):
                cmdSplit = re.sub(r"\)$", "", re.sub(r"^\(", "", cmd)).split(",")
                for i in range(1, len(cmdSplit)): cmdSplit[i] = re.sub(r"^\s", "", cmdSplit[i])
                for s in cmdSplit: 
                    if len(s) > 0:
                        if re.fullmatch(r"^[+-]?\d+$", s) == None: 
                            invalid = True
                        elif int(s) > sys.maxsize: invalid = True
                        elif len(cmdSplit) != checkType["size"]: invalid = True
                    else: invalid = True
                        
                if not invalid:
                    cmdIntSplit = [int(v) for v in cmdSplit]
                    if checkType["type"] == "tuple":
                        _min = checkType["min"]
                        if _min != None:
                            if min(_min, min(cmdIntSplit)) != _min: invalid = True
                        if not invalid:
                            _max = checkType["max"]
                            if _max != None:
                                if max(_max, max(cmdIntSplit)) != _max: invalid = True
                            if not invalid:
                                _warn = checkType["perfWarning"]
                                if _warn != None:
                                    if max(_warn, max(cmdIntSplit)) != _warn: warning = True
                        
                    if checkType["type"] == "rect":
                        _range = (checkType["minPos"], checkType["maxPos"])
                        if _range[0] != None:
                            if min(_range[0], min(cmdIntSplit[:2])) != _range[0]: invalid = True
                        if _range[1] != None:
                            if max(_range[1], max(cmdIntSplit[:2])) != _range[1]: invalid = True
                        _size = (checkType["minSize"], checkType["maxSize"])
                        if _size[0] != None:
                            if min(_size[0], min(cmdIntSplit[2:])) != _size[0]: invalid = True
                        if _size[1] != None:
                            if max(_size[1], max(cmdIntSplit[2:])) != _size[1]: invalid = True
        
        overlayColor = KDS.Colors.White
        if invalid:
            overlayColor = KDS.Colors.Red
        elif warning:
            overlayColor = KDS.Colors.Yellow
            display.blit(warnText, (text_rect.left + renderedCmd.get_width() + 5, text_y + (console_font.get_height() - console_font_small.get_height())))
        if invalid or warning:
            overlaySurf = pygame.Surface(renderedCmd.get_size())
            overlaySurf.fill(overlayColor)
            overlaySurf.set_alpha(128)
            display.blit(overlaySurf, (text_rect.left, text_y))
            
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        display.fill(KDS.Colors.Black)
        window.fill(KDS.Colors.Black)
        clock.tick(60)

    pygame.key.set_repeat(0, 0)
    return cmd