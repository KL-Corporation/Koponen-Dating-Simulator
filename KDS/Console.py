import re
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math

pygame.init()
pygame.key.stop_text_input()
pygame.scrap.init()
pygame.scrap.set_mode(SCRAP_CLIPBOARD)
#region Settings
console_font = pygame.font.SysFont("Consolas", 25, bold=False, italic=False)
console_font_small = pygame.font.SysFont("Consolas", 15, bold=False, italic=False)
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
    @staticmethod
    def String(maxLength: int = None, invalidChars: str = None, invalidStrings: Sequence[str] = None, funnyStrings: Sequence[str] = None, noSpace: bool = False):
        return {
            "type": "string",
            "maxLength": maxLength,
            "invalidChars": list(invalidChars) if invalidChars != None else invalidChars,
            "invalidStrings": invalidStrings,
            "funnyStrings": funnyStrings,
            "noSpace": noSpace
        }

Escaped = False
Feed = []
OldCommands = []

def Start(prompt: str = "Enter Command:", allowEscape: bool = True, checkType: dict = None, background: pygame.Surface = None, commands: dict = None, autoFormat: bool = False, showFeed: bool = False, enableOld: bool = False, defVal: str = None) -> Any:
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
    caret_index: int = len(cmd)
    caret_length: int = 0
    caret_animation = KDS.Animator.Value(2.0, 0.0, 64, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
    invalid = False
    warning = False
    warnText = console_font_small.render("[PERFORMANCE WARNING]" if checkType == None or checkType["type"] != "string" else "Haha, funny. Fuck you.", True, text_color)
    pygame.key.set_repeat(500, 31)
    promptRender = console_font.render(prompt, True, text_color)
    text_y = text_rect.y + text_rect.height / 2 - console_font.get_height() / 2
    tabAdd = False
    match: List[str] = []
    oldIndex = -1

    if checkType != None and (checkType["type"] == "commands") != (commands != None): KDS.Logging.AutoError("Check Type and Commands defined incorrectly!")

    def addText(text: str):
        nonlocal caret_index, cmd, caret_length
        tmp_crt_pos = caret_index + caret_length
        cmd = cmd[:min(caret_index, tmp_crt_pos)] + text + cmd[max(caret_index, tmp_crt_pos):]
        caret_index = KDS.Math.Clamp(caret_index + len(text) + min(caret_length, 0), 0, len(cmd))
        caret_length = 0
        caret_animation.tick = 0

    def addCaretLength(add: int):
        nonlocal caret_index, caret_length, cmd
        old_index = caret_index
        caret_index = KDS.Math.Clamp(caret_index + add, 0, len(cmd))
        caret_length += old_index - caret_index

    def resetCaretLength(left: bool, right: bool) -> bool:
        nonlocal caret_length, caret_index
        if caret_length == 0:
            return False

        if left and caret_length < 0:
            caret_index += caret_length
        if right and caret_length > 0:
            caret_index += caret_length
        caret_length = 0
        return True

    def nextWordIndexes(text: str) -> List[Tuple[int, int]]:
        found = [(i.start(), i.end()) for i in re.finditer(f"[{matchChars}][{matchChars}]*", text)]
        return found

    def previousWordIndexes(text: str) -> List[Tuple[int, int]]:
        found = nextWordIndexes(text)
        found.reverse()
        return found

    while running:
        showSuggestions = True
        tabbed = False
        Key_Up = False
        Key_Down = False
        tmp_events = pygame.event.get()
        keys_pressed: Dict[int, bool] = pygame.key.get_pressed()
        for event in tmp_events:
            if event.type == TEXTINPUT:
                addText(event.text)
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    caret_animation.tick = 0
                    if caret_length != 0:
                        addText("")
                        continue
                    if not keys_pressed[K_LCTRL]:
                        if len(cmd[:caret_index]) > 0:
                            cmd = cmd[:caret_index][:-1] + cmd[caret_index:]
                            caret_index -= 1
                    else:
                        found = previousWordIndexes(cmd[:caret_index].rstrip(matchChars))
                        if len(found) >= 1:
                            cmd = cmd[:found[0][1]] + cmd[caret_index:]
                            caret_index = found[0][1]
                        else:
                            cmd = cmd[caret_index:]
                            caret_index = 0
                elif event.key == K_DELETE:
                    caret_animation.tick = 0
                    if caret_length != 0:
                        addText("")
                        continue
                    if not keys_pressed[K_LCTRL]:
                        if len(cmd[caret_index:]) > 0:
                            cmd = cmd[:caret_index] + cmd[caret_index:][1:]
                    else:
                        rmv = cmd[caret_index:].lstrip(matchChars)
                        found = nextWordIndexes(rmv)
                        if len(found) >= 1:
                            cmd = cmd[:caret_index] + cmd[caret_index + found[0][0] + (len(cmd[caret_index:]) - len(rmv)):]
                        else:
                            cmd = cmd[:caret_index]
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
                    caret_animation.tick = 0
                    if not keys_pressed[K_LSHIFT]:
                        if resetCaretLength(True, False):
                            continue
                        if not keys_pressed[K_LCTRL]:
                            caret_index = max(caret_index - 1, 0)
                        elif caret_index > 0:
                            found = previousWordIndexes(cmd[:caret_index])
                            if len(found) >= 2:
                                if caret_index != found[0][1]:
                                    caret_index = found[0][1] # Fixes caret moving twice if no space before caret
                                else:
                                    caret_index = found[1][1]
                            else:
                                caret_index = 0
                        else:
                            caret_index = 0
                    else:
                        if not keys_pressed[K_LCTRL]:
                            addCaretLength(-1)
                        else:
                            found = previousWordIndexes(cmd[:caret_index])
                            if len(found) >= 2:
                                if caret_index != found[0][1]:
                                    addCaretLength(found[0][1] - caret_index) # Fixes caret moving twice if no space before caret
                                else:
                                    addCaretLength(found[1][1] - caret_index)
                            else:
                                addCaretLength(-caret_index)
                elif event.key == K_RIGHT:
                    caret_animation.tick = 0
                    if not keys_pressed[K_LSHIFT]:
                        if resetCaretLength(False, True):
                            continue
                        if not keys_pressed[K_LCTRL]:
                            caret_index = min(caret_index + 1, len(cmd))
                        elif caret_index < len(cmd):
                            found = nextWordIndexes(cmd[caret_index:])
                            if len(found) >= 1:
                                caret_index = len(cmd[:caret_index]) + found[0][1]
                            else:
                                caret_index = len(cmd)
                        else:
                            caret_index = len(cmd)
                    else:
                        if not keys_pressed[K_LCTRL]:
                            addCaretLength(1)
                        else:
                            found = nextWordIndexes(cmd[caret_index:])
                            if len(found) >= 1:
                                addCaretLength(found[0][1])
                            else:
                                addCaretLength(len(cmd) - caret_index)
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
                elif event.key == K_a:
                    if keys_pressed[K_LCTRL]:
                        caret_index = 0
                        addCaretLength(len(cmd))
                elif event.key == K_v and keys_pressed[K_LCTRL]:
                    clipboardText: Union[str, bytes, None] = pygame.scrap.get("text/plain;charset=utf-8")
                    if clipboardText != None:
                        if isinstance(clipboardText, bytes):
                            clipboardText = clipboardText.decode("utf-8")
                        addText(clipboardText)
            elif event.type == MOUSEBUTTONDOWN:
                caret_animation.tick = 0
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
                if KDS_Quit != None:
                    KDS_Quit()

        while console_font.size(cmd)[0] + cursor_width >= text_rect.width:
            cmd = cmd[:-1]

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
                 for newLine in splitFeed:
                     newFeed.append(newLine)
            while len(newFeed) > feedRect.height / console_font.get_height():
                del newFeed[0]
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
                        if cmdInt > KDS.Math.MAXVALUE: invalid = True
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
                    if cmdFloat > KDS.Math.MAXVALUE: invalid = True
                    _min = checkType["min"]
                    if _min != None:
                        if min(_min, cmdFloat) != _min: invalid = True
                    _max = checkType["max"]
                    if _max != None:
                        if max(_max, cmdFloat) != _max: invalid = True
                else: invalid = True

            elif _type == "bool":
                if KDS.Convert.ToBool2(cmd, None, True) == None: invalid = True

            elif _type in ("tuple", "rect"):
                cmdSplit = re.sub(r"\)$", "", re.sub(r"^\(", "", cmd)).split(",")
                for i in range(1, len(cmdSplit)): cmdSplit[i] = re.sub(r"^\s", "", cmdSplit[i])
                for i, s in enumerate(cmdSplit):
                    if len(s) > 0:
                        if re.fullmatch(r"^[+-]?\d+$", s) == None:
                            invalid = True
                            break
                        elif int(s) > KDS.Math.MAXVALUE:
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
            elif _type == "string":
                if checkType["invalidChars"] != None:
                    for char in checkType["invalidChars"]:
                        if char in cmd:
                            invalid = True
                            break
                if checkType["invalidStrings"] != None:
                    for word in checkType["invalidStrings"]:
                        if word == cmd:
                            invalid = True
                            break
                if checkType["funnyStrings"] != None:
                    for word in checkType["funnyStrings"]:
                        if word == cmd:
                            warning = True
                            break
                if checkType["maxLength"] != None:
                    if checkType["maxLength"] < len(cmd):
                        invalid = True
                if checkType["noSpace"] == True:
                    if " " in cmd:
                        invalid = True
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
                            caret_index = len(cmd)
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
                caret_index = len(cmd)

        if not suggestionsRendered: display.blit(promptRender, (text_input_rect.left, text_input_rect.top - promptRender.get_height()))
        #endregion

        #region Text Rendering
        text_render_color = text_color
        if warning or invalid:
            if not invalid:
                text_render_color = text_warn_color
                display.blit(warnText, (text_rect.left + console_font.size(cmd)[0] + 5, text_y + (console_font.get_height() - console_font_small.get_height())))
            else:
                text_render_color = text_invalid_color

        renderedCmd = console_font.render(cmd, True, text_render_color)
        display.blit(renderedCmd, (text_rect.left, text_y))
        if caret_length != 0:
            tmp_crt_pos = caret_index + caret_length
            blueTint = pygame.Surface((console_font.size(cmd[min(caret_index, tmp_crt_pos):max(caret_index, tmp_crt_pos)])[0], console_font.get_height()))
            blueTint.fill((168, 206, 255))
            blueTint.set_alpha(192)
            display.blit(blueTint, (text_rect.left + console_font.size(cmd[:min(caret_index, caret_index + caret_length)])[0], text_y))
        if textInput and caret_animation.update() >= 1.0:
            pygame.draw.rect(display, (192, 192, 192), pygame.Rect(text_rect.left + console_font.size(cmd[:caret_index])[0] - round(cursor_width / 2), text_y, cursor_width, console_font.get_height()))

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
                return KDS.Convert.ToBool2(cmd)
            elif _type in ("tuple", "rect"):
                tmpSplit = cmd.split(",")
                tmpVals = [int(re.sub(r"\D", "", val)) for val in tmpSplit]
                if _type == "rect": return pygame.Rect(*tmpVals)
                else: return tuple(tmpVals)
            elif _type == "commands": return cmd.lower().split()
            elif _type == "string": return cmd
            else: KDS.Logging.AutoError("Invalid type for automatic formatting!")
        return None
    #endregion

    return cmd
