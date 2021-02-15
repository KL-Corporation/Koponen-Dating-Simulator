import re
import sys
from typing import Any, Callable, List, Tuple, TypeVar, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math

pygame.init()
pygame.key.stop_text_input()
#region Settings
console_font = pygame.font.SysFont("Consolas", 25, bold=0, italic=0)
console_font_small = pygame.font.SysFont("Consolas", 15, bold=0, italic=0)
text_input_rect = pygame.Rect(0, 750, 1200, 50)
text_rect = pygame.Rect(10, 762, 1180, 25)
text_color = KDS.Colors.LightGray
text_invalid_color = KDS.Colors.Red
text_warn_color = KDS.Colors.Yellow
cursor_width = 3
suggestionCount = 10
suggestionSpacing = 5
suggestionColor = KDS.Colors.Yellow
suggestionPreviewColor = KDS.Colors.Gray
suggestionPreviewAlpha = 128
suggestionBackgroundColor = KDS.Colors.DarkGray
suggestionBackgroundAlpha = 128
feedRect = pygame.Rect(10, 10, 1180, 700)
feedTextColor = KDS.Colors.Gray
matchChars = r" ; , \/ \\ \" "
#endregion

def init(_window: pygame.Surface, _display: pygame.Surface, _clock: pygame.time.Clock, _Offset: Tuple[int, int] = None, _KDS_Quit: Callable[[], None] = None):
    global window, display, display_size, clock, defaultBackground, KDS_Quit, rndrOffset
    window = _window
    display = _display
    display_size = display.get_size()
    rndrOffset = _Offset if _Offset != None else (0, 0)
    clock = _clock
    defaultBackground = pygame.image.load("Assets/Textures/UI/Menus/console.png").convert()
    KDS_Quit = _KDS_Quit
    pygame.scrap.init()
    pygame.scrap.set_mode(SCRAP_CLIPBOARD)

class CheckTypes:
    @staticmethod
    def Int(_min: int = None, _max: int = None):
        """Both min and max are inclusive."""
        return {
            "type": "int",
            "min":_min,
            "max": _max }
    @staticmethod
    def Float(_min: int = None, _max: int = None):
        """Both min and max are inclusive."""
        return {
            "type": "float",
            "min":_min,
            "max": _max }
    @staticmethod
    def Tuple(size: int, _min: int = None, _max: int = None, perfWarning: int = None, requireIncrease: bool = False):
        """All min, max and perfWarning are inclusive."""
        return {
            "type": "tuple",
            "size": size,
            "min":_min,
            "max": _max,
            "perfWarning": perfWarning,
            "requireIncrease": requireIncrease
            }
    @staticmethod
    def Rect(minPos: int = None, maxPos: int = None, minSize: int = None, maxSize: int = None):
        """All mins and maxs are inclusive."""
        return {
            "type": "rect",
            "minPos": minPos,
            "maxPos": maxPos,
            "minSize": minSize,
            "maxSize": maxSize,
            "size": 4
        }
    @staticmethod
    def Bool():
        return {
            "type": "bool"
        }
    @staticmethod
    def Commands():
        return {
            "type": "commands"
        }

Escaped = False
Feed = []
OldCommands = []

def Start(prompt: str = "Enter Command:", allowEscape: bool = True, checkType: CheckTypes and dict = None, background: pygame.Surface = None, commands: dict = None, autoFormat: bool = False, showFeed: bool = False, enableOld: bool = False, defVal: str = None) -> Any:
    global Escaped, Feed, OldCommands
    if commands != None:
        commandsFound = commands
        previousCommandsFound = commandsFound
        commandsFoundLowerKeys = dict((k.lower(), k) for k in commandsFound)
    cmd = "" if defVal == None else defVal
    lastCmd = cmd
    tabbedCmd = ""
    suggestionPathIndex = 0
    suggestionIndex = 0
    suggestionsRendered = False
    suggestionsOverride = False
    renderedCmd = None
    running = True
    pygame.key.set_text_input_rect(text_input_rect)
    pygame.key.start_text_input()
    textInput = True
    cursor_index = len(cmd)
    cursor_animation = KDS.Animator.Value(2.0, 0.0, 64, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
    invalid = False
    warning = False
    warnText = console_font_small.render("[PERFORMANCE WARNING]", True, text_color)
    pygame.key.set_repeat(500, 31)
    promptRender = console_font.render(prompt, True, text_color)
    text_y = text_rect.y + text_rect.height / 2 - console_font.get_height() / 2
    tabAdd = False
    match: List[str] = []
    oldIndex = -1
    
    if checkType != None and (checkType["type"] == "commands") != (commands != None): KDS.Logging.AutoError("Check Type and Commands defined incorrectly!")
    
    def addText(text: str):
        nonlocal cursor_index, cmd
        cmd = cmd[:cursor_index] + text + cmd[cursor_index:]
        cursor_index += 1
        cursor_animation.tick = 0

    while running:
        showSuggestions = True
        tabbed = False
        Key_Up = False
        Key_Down = False
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
                    Escaped = True
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
                elif event.key == K_TAB:
                    tabbed = True
                    if tabAdd: suggestionIndex += 1
                    tabAdd = True
                elif event.key == K_UP:
                    tabAdd = False
                    suggestionIndex -= 1
                    Key_Up = True
                elif event.key == K_DOWN:
                    tabAdd = False
                    suggestionIndex += 1
                    Key_Down = True
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
            elif event.type == QUIT:
                if allowEscape:
                    cmd = ""
                    textInput = False
                    running = False
                if KDS_Quit != None: KDS_Quit()
        
        while console_font.size(cmd)[0] + cursor_width >= text_rect.width: cmd = cmd[:-1]

        if lastCmd != cmd:
            suggestionIndex = 0
            suggestionsOverride = False
            tabAdd = False
            if tabbedCmd != cmd:
                tabbedCmd = ""
        
        display.blit(defaultBackground if background == None else background, (0, 0))
        pygame.draw.rect(display, KDS.Colors.Black, text_input_rect)

        #region Feed Rendering
        if showFeed:
            newFeed: List[str] = []
            for line in Feed:
                 splitFeed = KDS.Convert.ToLines(line, console_font, feedRect.width)
                 for newLine in splitFeed: newFeed.append(newLine)
            while len(newFeed) > feedRect.height / console_font.get_height(): del newFeed[0]
            Feed = newFeed
            renderFeed = Feed.copy()
            renderFeed.reverse()
            for y_i in range(len(renderFeed)): display.blit(console_font.render(renderFeed[y_i], True, feedTextColor), (feedRect.left, feedRect.bottom - console_font.get_height() - y_i * console_font.get_height()))
                
        #endregion

        #region Type Checking
        invalid = False
        warning = False
        if checkType != None:
            _type = checkType["type"]
            if _type == "int":
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
            
            elif _type == "float":
                
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
            
            elif _type == "bool":
                if KDS.Convert.ToBool(cmd, None, True) == None: invalid = True
                   
            elif _type in ("tuple", "rect"):
                cmdSplit = re.sub(r"\)$", "", re.sub(r"^\(", "", cmd)).split(",")
                for i in range(1, len(cmdSplit)): cmdSplit[i] = re.sub(r"^\s", "", cmdSplit[i])
                for i, s in enumerate(cmdSplit): 
                    if len(s) > 0:
                        if re.fullmatch(r"^[+-]?\d+$", s) == None: 
                            invalid = True
                            break
                        elif int(s) > sys.maxsize:
                            invalid = True
                            break
                        elif len(cmdSplit) != checkType["size"]:
                            invalid = True
                            break
                        elif checkType["requireIncrease"] and i > 0 and int(cmdSplit[i - 1]) >= int(s):
                            invalid = True
                            break
                    else:
                        invalid = True
                        break
                        
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
            elif _type != "commands": KDS.Logging.AutoError("Check Type invalid!")
        #endregion
        
        #region Commands and Suggestions
        if commands != None:
            if not tabbed and len(cmd) < 1: showSuggestions = False
            
            previousCommandsFound = {}
            commandsFound = {}
            
            cmdSplit = cmd.split(" ")
            if not suggestionsOverride:
                commandsFound = commands
                commandsFoundLowerKeys = dict((k.lower(), k) for k in commandsFound)
                suggestionPathIndex = 0
                while suggestionPathIndex < len(cmdSplit):
                    if isinstance(commandsFound, dict) and cmdSplit[suggestionPathIndex].lower() in commandsFoundLowerKeys:
                        previousCommandsFound = commandsFound
                        commandsFound = commandsFound[commandsFoundLowerKeys[cmdSplit[suggestionPathIndex].lower()]]
                        if isinstance(commandsFound, dict):
                            commandsFoundLowerKeys = dict((k.lower(), k) for k in commandsFound)
                        else:
                            showSuggestions = False
                            break
                        suggestionPathIndex += 1
                    else:
                        break
              
                if isinstance(commandsFound, dict):
                    match: List[str] = []
                    if len(cmdSplit) - 1 == suggestionPathIndex:
                        for k in commandsFound:
                            found = k.lower().find(cmdSplit[suggestionPathIndex].lower())
                            if found == 0: match.append(k)
                    else:
                        for k in commandsFound: match.append(k)
                
            if suggestionIndex < 0: suggestionIndex = len(match) - 1
            elif suggestionIndex >= len(match): suggestionIndex = 0
            
            if showSuggestions and (len(cmdSplit) > 0 or len(cmdSplit) - 1 == suggestionPathIndex) and (tabbedCmd == cmd or cmdSplit[-1] not in previousCommandsFound):
                renderIndex = max(suggestionCount, suggestionIndex + 1)
                y = (suggestionSpacing + console_font.get_height()) * min(len(match), suggestionCount)
                w = 0
                suggestions = []
                for r in match[renderIndex - suggestionCount:renderIndex]:
                    rndrCol = text_color
                    if match.index(r) == suggestionIndex:
                        rndrCol = suggestionColor
                        if tabbed:
                            if len(cmd) > 0:
                                if cmd[-1] != " " or cmd[-1] in commandsFound:
                                    tmpCmd = [cmdTxt + " " for cmdTxt in cmd.split(" ")]
                                    tmpCmd[-1].rstrip()
                                else: tmpCmd = [cmdTxt + " " for cmdTxt in cmd.split(" ")]
                                cmd = "".join(tmpCmd[:-1])
                            cmd += r
                            tabbedCmd = cmd
                            cursor_index = len(cmd)
                            suggestionsOverride = True
                        else:
                            if len(cmdSplit) > 0:
                                previewOffsetX = text_rect.left
                                for i in range(len(cmdSplit) - 1): previewOffsetX += console_font.size(f"{cmdSplit[i]} ")[0]
                            else: previewOffsetX = text_rect.left
                            tempSplit = cmdSplit[-1]
                            if len(cmdSplit) < 1 or cmdSplit[-1] in r:
                                previewTxt = r
                                for l in range(min(len(tempSplit), len(previewTxt))):
                                    if previewTxt[l].isupper() and not tempSplit[l].isupper(): previewTxt = previewTxt[:l] + tempSplit[l] + previewTxt[l + 1:]
                                previewTxt = console_font.render(previewTxt, True, suggestionPreviewColor)
                                previewSurf = pygame.Surface(previewTxt.get_size())
                                previewSurf.blit(previewTxt, (0, 0))
                                previewSurf.set_alpha(suggestionPreviewAlpha)
                                display.blit(previewSurf, (previewOffsetX, text_y))
                    rndrd = console_font.render(r, True, rndrCol)
                    suggestions.append(rndrd)
                    w = max(w, rndrd.get_width())
                
                suggestionsRendered = True
                suggestionSurf = pygame.Surface((w, y))
                suggestionSurf.fill(suggestionBackgroundColor)
                suggestionSurf.set_alpha(suggestionBackgroundAlpha)
                display.blit(suggestionSurf, (0, text_input_rect.top - y))
                for r in suggestions:
                    display.blit(r, (0, text_input_rect.top - y))
                    y -= suggestionSpacing + console_font.get_height()
                    
            if enableOld and (len(cmd) <= 0 or cmd in OldCommands) and ((len(OldCommands) > oldIndex and oldIndex != -1 or len(OldCommands) > oldIndex + 1 and oldIndex == -1)) and (Key_Up or Key_Down):
                if Key_Up:
                    oldIndex += 1
                    if oldIndex >= len(OldCommands): oldIndex = len(OldCommands) - 1
                    cmd = OldCommands[len(OldCommands) - 1 - oldIndex]
                else:
                    oldIndex -= 1
                    if oldIndex < -1: oldIndex = -1
                    cmd = OldCommands[len(OldCommands) - 1 - oldIndex] if oldIndex > -1 else ""
                cursor_index = len(cmd)
  
        if not suggestionsRendered: display.blit(promptRender, (text_input_rect.left, text_input_rect.top - promptRender.get_height()))
        #endregion
        
        #region Text Rendering
        text_render_color = text_color
        if warning and not invalid:
            text_render_color = text_warn_color
            display.blit(warnText, (text_rect.left + console_font.size(cmd)[0] + 5, text_y + (console_font.get_height() - console_font_small.get_height())))
        if invalid: text_render_color = text_invalid_color
        renderedCmd = console_font.render(cmd, True, text_render_color)
        display.blit(renderedCmd, (text_rect.left, text_y))
        if textInput and cursor_animation.update() >= 1.0:
            pygame.draw.rect(display, (192, 192, 192), pygame.Rect(text_rect.left + console_font.size(cmd[:cursor_index])[0] - round(cursor_width / 2), text_y, cursor_width, console_font.get_height()))
        
        """
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
        """
        #endregion
        
        suggestionsRendered = False 
        lastCmd = cmd
        window.blit(pygame.transform.scale(display, (display_size[0], display_size[1])), (0, 0))
        pygame.display.flip()
        display.fill(KDS.Colors.Black)
        window.fill(KDS.Colors.Black)
        clock.tick_busy_loop(60)

    pygame.key.stop_text_input()
    pygame.key.set_repeat(0, 0)
    if enableOld and len(cmd) > 0: OldCommands.append(cmd)
    
    #region Formatting
    if autoFormat:
        if len(cmd) > 0:
            _type = checkType["type"]
            if _type == "int":
                return int(cmd)
            elif _type == "float":
                return float(cmd)
            elif _type == "bool":
                return KDS.Convert.ToBool(cmd)
            elif _type in ("tuple", "rect"):
                tmpSplit = cmd.split(",")
                tmpVals = [int(re.sub(r"\D", "", val)) for val in tmpSplit]
                if _type == "rect": return pygame.Rect(*tmpVals)
                else: return tuple(tmpVals)
            elif _type == "commands": return cmd.lower().split()
            else: KDS.Logging.AutoError("Invalid type for automatic formatting!")
        return None
    #endregion
    
    return cmd
