from __future__ import annotations

import os
import random
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pygame
from pygame.locals import *

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Console
import KDS.ConfigManager
import KDS.Convert
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.UI
import KDS.Linq
import KDS.AI
import KDS.Inventory
import KDS.World
import KDS.Debug
import KDS.Clock
import KDS.Keys
import KDS.Story
import KDS.Build

import re
import shlex

#region Settings
text_font = pygame.font.Font("Assets/Fonts/courier.ttf", 20, bold=0, italic=0)
text_color = KDS.Colors.MidnightBlue
background_color = KDS.Colors.CloudWhite
background_outline_color = KDS.Colors.MidnightBlue
conversation_rect = pygame.Rect(40, 40, 700, 400)
conversation_outline_width = 3
conversation_border_radius = 10
line_spacing = 25
line_reveal_speed = 3
line_scroll_speed = 1
min_time_before_scroll = 120 #ticks
auto_scroll_offset_index = 10
scroll_to_bottom_rect = pygame.Rect(640, 340, 50, 50)
scroll_arrow_padding = 5
scroll_to_bottom_colors = {
    "default": (KDS.Colors.DarkGray),
    "highlighted": (KDS.Colors.Gray),
    "pressed": (KDS.Colors.LightGray)
}
class text_padding:
    left = 5
    top = 5
    right = 5
    bottom = 5
#endregion

#region Koponen Variables
KOPONEN_MIN_AUT_IDLE_TIME = 150 #ticks (1 / 60 seconds)
KOPONEN_MIN_AUT_MOVE_TIME = 300
KOPONEN_IDLE_CHANCE = 120
KOPONEN_WALK_CHANCE = 120
#endregion

pygame.init()
pygame.key.stop_text_input()

talk_background = pygame.Surface((0, 0))
talk_ads = [pygame.Surface((0, 0), SRCALPHA)]
old_ads = [-69 for _ in range(5)]
talk_ad = talk_ads[0]

randChance: Callable[[int], bool] = lambda v: random.uniform(0, 1) <= 1 / v

requestReturnAlt: Optional[str] = None

class Prefixes:
    player = "p:"
    koponen = "k:"

_renderedPrefixes = {
    Prefixes.player: text_font.render("ERROR: ", True, text_color),
    Prefixes.koponen: text_font.render("Koponen: ", True, text_color)
}

def init():
    global talk_background, talk_ads, talk_ad, scrollArrow, ambientTalkAudios # , scrollToBottomButton
    talk_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png").convert()
    scrollArrow = pygame.transform.scale(pygame.transform.rotate(pygame.image.load("Assets/Textures/UI/Buttons/Arrow.png").convert_alpha(), -90), (scroll_to_bottom_rect.width - scroll_arrow_padding * 2, scroll_to_bottom_rect.height - scroll_arrow_padding * 2))
    # scrollToBottomButton = KDS.UI.Button(scroll_to_bottom_rect, Talk.Conversation.scrollToBottom, scrollArrow, scroll_to_bottom_colors["default"], scroll_to_bottom_colors["highlighted"], scroll_to_bottom_colors["pressed"])
    for ad in os.listdir("Assets/Textures/KoponenTalk/ads"): talk_ads.append(pygame.image.load(f"Assets/Textures/KoponenTalk/ads/{ad}").convert_alpha())
    random.shuffle(talk_ads)

def setPlayerPrefix(prefix: str):
    global _renderedPrefixes
    _renderedPrefixes[Prefixes.player] = text_font.render(f"{prefix}: ", True, text_color)

class Mission:
    # Will be automatically assigned by KDS.Missions
    Task: Optional[KDS.Missions.KoponenTask] = None

    @staticmethod
    def Request():
        if len(Talk.scheduled) > 0 and Talk.scheduled[0] == Talk.Conversation.WAITFORMISSIONREQUEST:
            if Mission.Task == None:
                KDS.Missions.Listeners.KoponenRequestMission.Trigger()
                Talk.scheduled.pop(0)
#            else:
#                Talk.Conversation.schedulePriority("Äläs nyt kiirehdi... Sinulla on vielä tehtävä kesken.", Prefixes.koponen)
#        else:
#            Talk.Conversation.schedulePriority("Nyt on kyllä ideat lopussa... Minulla ei ole hajuakaan mitä tekemistä keksisin sinulle.", Prefixes.koponen)

    @staticmethod
    def Return(player_inventory):
        if player_inventory != None and Mission.Task != None and len(Talk.scheduled) > 0 and Talk.scheduled[0] == Talk.Conversation.WAITFORMISSIONRETURN:
            for item in Mission.Task.items:
                inInv = None
                for invItem in player_inventory.storage:
                    if hasattr(invItem, "serialNumber") and invItem.serialNumber == item:
                        inInv = invItem
                        break

                if inInv != None:
                    KDS.Missions.SetProgress(Mission.Task.missionName, Mission.Task.safeName, 1.0)
                    if Mission.Task.removeItems:
                        player_inventory.dropItemAtIndex(player_inventory.storage.index(inInv))
                    Mission.Task = None
                    KDS.Missions.Listeners.KoponenReturnMission.Trigger()
                    Talk.scheduled.pop(0)
                    return
            # callVariation tarkoittaa esimerkiksi sitä, että sana "juusto" on taivutettu sanaksi "juustoa" tai sana "terotin" on taivutettu sanaksi "terotinta".
#            Talk.Conversation.schedulePriority(f"Olen pahoillani, en löydä {Mission.Task.callVariation} pöksyistäsi.")
#        else:
#            Talk.Conversation.schedulePriority("Sinulla ei ole mitään palautettavaa tehtävää.", Prefixes.koponen)

def TriggerStoryEnding(koponen: KoponenEntity):
    if Talk.scheduled[0] != Talk.Conversation.WAITFORSTORYENDING:
        return

    koponen.rect.topleft = (1700, 514)
    assert KDS.ConfigManager.Save.Active != None, "How can I trigger story ending without any save loaded?"
    KDS.Story.BadEndingTrigger = True
    Talk.lines.clear()
    Talk.scheduled.pop(0)

class Talk:
    running = False
    mask = pygame.mask.Mask(conversation_rect.size, True)
    display = pygame.Surface(conversation_rect.size, pygame.SRCALPHA, masks=mask)
    display_size = display.get_size()
    lineCount = KDS.Math.FloorToInt((display.get_height() - text_padding.top - text_padding.bottom) / line_spacing)
    soundPlaying = None
    autoExit = False
    storyTrigger = False

    lines: List[str] = []
    scheduled: List[str] = []
    scheduledTokens: List[Dict[int, str]] = []

    class Conversation:
        WAITFORMISSIONREQUEST = "<wait-for-mission-request>"
        WAITFORMISSIONRETURN = "<wait-for-mission-return>"
        WAITFORTILEFIRE = "<wait-for-tile_fire>"
        WAITFORSTORYENDING = "<wait-for-story-ending>"
        _INTERNALTILEFIREEVENT = "<wait-for-internal_tile_fire>"
        PRINCIPALNAMEINPUT = "<rehtori-name-input>"
        GIVEHOTELCARD = "<give-hotel-card>"
        TRIGGERLISTENER0 = "<trigger-listener-0>"
        TRIGGERLISTENER1 = "<trigger-listener-1>"
        TRIGGERLISTENER2 = "<trigger-listener-2>"

        @staticmethod
        def scrollToBottom():
            Talk.Conversation.scroll = max(len(Talk.lines) - Talk.lineCount, 0)
        scroll = 0
        animationProgress = -1
        animationWidth = 0
        newAnimation = False

        @staticmethod
        def _handleTileFire():
            KDS.Missions.Listeners.TileFireCreated.OnTrigger -= Talk.Conversation._handleTileFire
            Talk.scheduled.pop(0)

        @staticmethod
        def schedule(text: str, prefix: Optional[str], forcePrefix: bool = False):
            if "\n" in text:
                prefixForced: bool = False
                for newLine in text.splitlines():
                    Talk.Conversation.schedule(newLine, prefix, forcePrefix and not prefixForced)
                    prefixForced = True
                return

            if text in (Talk.Conversation.WAITFORMISSIONREQUEST, Talk.Conversation.WAITFORMISSIONRETURN, Talk.Conversation.PRINCIPALNAMEINPUT, Talk.Conversation.GIVEHOTELCARD, Talk.Conversation.WAITFORTILEFIRE, Talk.Conversation.WAITFORSTORYENDING, Talk.Conversation._INTERNALTILEFIREEVENT, Talk.Conversation.TRIGGERLISTENER0, Talk.Conversation.TRIGGERLISTENER1, Talk.Conversation.TRIGGERLISTENER2):
                Talk.scheduled.append(text)
                return
            assert prefix != None, "A prefix must be specified if text is not an event (for example: WAITFORMISSIONREQUEST)."
            prefixWidth = _renderedPrefixes[prefix].get_width()
            lineSplit = KDS.Convert.ToLines(text, text_font, Talk.display_size[0] - text_padding.left - text_padding.right - prefixWidth)
            for i in range(len(lineSplit)):
                if i == 0 and forcePrefix:
                    Talk.scheduled.append("!" + prefix + lineSplit[i])
                else:
                    Talk.scheduled.append(prefix + lineSplit[i])

        @staticmethod
        def update(surfSize: Tuple[int, int], playerInventory: KDS.Inventory.Inventory):
            if Talk.Conversation.animationProgress == -1 and len(Talk.scheduled) > 0 and Talk.scheduled[0] not in (Talk.Conversation.WAITFORMISSIONREQUEST, Talk.Conversation.WAITFORMISSIONRETURN, Talk.Conversation.PRINCIPALNAMEINPUT, Talk.Conversation.GIVEHOTELCARD, Talk.Conversation.WAITFORTILEFIRE, Talk.Conversation.WAITFORSTORYENDING, Talk.Conversation._INTERNALTILEFIREEVENT, Talk.Conversation.TRIGGERLISTENER0, Talk.Conversation.TRIGGERLISTENER1, Talk.Conversation.TRIGGERLISTENER2):
                toShow = Talk.scheduled.pop(0)
                for token in re.findall(r"\{.+?\}", toShow):
                    assert KDS.ConfigManager.Save.Active != None, "No save loaded to replace tokens!"
                    toShow = toShow.replace(token, getattr(KDS.ConfigManager.Save.Active.Story, token[1:-1], f"<story_attribute_error ({token[1:-1]})>"))
                Talk.lines.append(toShow)
                Talk.Conversation.newAnimation = True
                Talk.Conversation.scrollToBottom()
#                 if len(Talk.lines) - Talk.Conversation.scroll <= Talk.lineCount + auto_scroll_offset_index:
#                     Talk.Conversation.scrollToBottom()
#                 else:
#                     Talk.Conversation.scroll = max(Talk.Conversation.scroll - deleteCount, 0)

#           WTF IS THIS IF ELSE SHIT?? IT'S EASIER TO READ A FUCKING STONE AGE POEM
            elif (len(Talk.scheduled) < 1 or Talk.scheduled[0] in (Talk.Conversation.WAITFORMISSIONREQUEST, Talk.Conversation.WAITFORMISSIONRETURN, Talk.Conversation.PRINCIPALNAMEINPUT, Talk.Conversation.GIVEHOTELCARD, Talk.Conversation.WAITFORTILEFIRE, Talk.Conversation.WAITFORSTORYENDING, Talk.Conversation._INTERNALTILEFIREEVENT, Talk.Conversation.TRIGGERLISTENER0, Talk.Conversation.TRIGGERLISTENER1, Talk.Conversation.TRIGGERLISTENER2)) and Talk.Conversation.animationProgress == -1:
                if len(Talk.scheduled) > 0 and Talk.scheduled[0] == Talk.Conversation.PRINCIPALNAMEINPUT:
                    KDS.Clock.Sleep(500)
                    Talk.scheduled.pop(0)
                    tmpSurf = pygame.Surface(surfSize)
                    Talk.renderMenu(tmpSurf, (0, 0), False, playerInventory, updateConversation=False)                          # funnyStrings=["name"] removed, because the joke isn't as funny the second time
                    nameSuggestion: str = KDS.Console.Start("Enter Name:", False, KDS.Console.CheckTypes.String(20, invalidStrings=("<principal-name-error>"), noSpace=True), background=tmpSurf)
                    if len(nameSuggestion) > 1:
                        nameSuggestion = nameSuggestion[0].upper() + nameSuggestion[1:]
                    assert KDS.ConfigManager.Save.Active != None, "No save loaded to suggest principal name!"
                    KDS.ConfigManager.Save.Active.Story.principalName = nameSuggestion
                    Talk.storyTrigger = True
                elif len(Talk.scheduled) > 0 and Talk.scheduled[0] == Talk.Conversation.GIVEHOTELCARD:
                    playerInventory.pickupItem(KDS.Build.Item.serialNumbers[38]((0, 0), 38), force=True)
                    Talk.scheduled.pop(0)
                elif len(Talk.scheduled) > 0 and Talk.scheduled[0] in (Talk.Conversation.TRIGGERLISTENER0, Talk.Conversation.TRIGGERLISTENER1, Talk.Conversation.TRIGGERLISTENER2):
                    if Talk.scheduled[0] == Talk.Conversation.TRIGGERLISTENER0:
                        KDS.Missions.Listeners.KoponenTalkEmbed0.Trigger()
                    elif Talk.scheduled[0] == Talk.Conversation.TRIGGERLISTENER1:
                        KDS.Missions.Listeners.KoponenTalkEmbed1.Trigger()
                    elif Talk.scheduled[0] == Talk.Conversation.TRIGGERLISTENER2:
                        KDS.Missions.Listeners.KoponenTalkEmbed2.Trigger()
                    Talk.scheduled.pop(0)
                elif len(Talk.scheduled) > 0 and Talk.scheduled[0] == Talk.Conversation.WAITFORTILEFIRE:
                    Talk.scheduled[0] = Talk.Conversation._INTERNALTILEFIREEVENT
                    KDS.Missions.Listeners.TileFireCreated.OnTrigger += Talk.Conversation._handleTileFire
                else:
                    if Talk.autoExit:
                        Talk.stop(forceExit=True)

        @staticmethod
        def render(mouse_pos: Tuple[int, int], clicked: bool) -> pygame.Surface:
            Talk.display.fill((0, 0, 0, 0))
            pygame.draw.rect(Talk.display, background_color, pygame.Rect(0, 0, Talk.display_size[0], Talk.display_size[1]), 0, conversation_border_radius)

            lastIncluded = False
            for i in range(Talk.Conversation.scroll, min(Talk.Conversation.scroll + Talk.lineCount + 1, len(Talk.lines))):
                text = Talk.lines[i]
                forcePrefix = False
                if text[0] == "!":
                    forcePrefix = True
                    text = text[1:]
                prefix = _renderedPrefixes[text[:2]]
                offsetX = text_padding.left + prefix.get_width()
                offsetY = text_padding.top + (i - Talk.Conversation.scroll) * line_spacing
                Talk.display.blit(text_font.render(text[2:], True, KDS.Colors.MidnightBlue), (offsetX, offsetY))
                if i <= 0 or forcePrefix or text[:2] != Talk.lines[i - 1].removeprefix("!")[:2]:
                    Talk.display.blit(prefix, (text_padding.left, offsetY))

                # if len(Talk.lines) - Talk.Conversation.scroll > Talk.lineCount + auto_scroll_offset_index: scrollToBottomButton.update(Talk.display, mouse_pos, clicked)

                if i == len(Talk.lines) - 1:
                    lastIncluded = True

            if len(Talk.lines) > 0:
                lastLine = Talk.lines[-1]
                if lastLine.startswith("!"):
                    lastLine = lastLine.removeprefix("!")
                animationRectTarget = pygame.Rect(text_padding.left + _renderedPrefixes[lastLine[:2]].get_width(),
                                                text_padding.top + (len(Talk.lines) - 1 - Talk.Conversation.scroll) * line_spacing, text_font.size(lastLine[2:])[0], text_font.get_height())
            else: animationRectTarget = pygame.Rect(0, 0, 0, 0)

            if Talk.Conversation.newAnimation:
                Talk.Conversation.newAnimation = False
                Talk.Conversation.animationProgress = 0.0
                Talk.Conversation.animationWidth = animationRectTarget.width

            if Talk.Conversation.animationProgress >= 1.0:
                Talk.Conversation.animationProgress = -1
            if Talk.Conversation.animationProgress != -1:
                Talk.Conversation.animationWidth = max(Talk.Conversation.animationWidth - line_reveal_speed, 0)
                Talk.Conversation.animationProgress = KDS.Math.Remap01(Talk.Conversation.animationWidth, animationRectTarget.width, 0)
                if lastIncluded:
                    pygame.draw.rect(Talk.display, background_color, pygame.Rect(animationRectTarget.x + (animationRectTarget.width - Talk.Conversation.animationWidth), animationRectTarget.y, Talk.Conversation.animationWidth, animationRectTarget.height))

            pygame.draw.rect(Talk.display, background_outline_color, pygame.Rect(0, 0, Talk.display_size[0], Talk.display_size[1]), conversation_outline_width, conversation_border_radius)
            return Talk.display

        @staticmethod
        def clear():
            Talk.lines.clear()
            Talk.scheduled.clear()

    @staticmethod
    def renderMenu(surface: pygame.Surface, mouse_pos: Tuple[int, int], clicked: bool, playerInventory: KDS.Inventory.Inventory, updateConversation: bool = True):
        surface.blit(talk_background, (0, 0))
        surface.blit(talk_ad, (40, 474))
        if updateConversation:
            Talk.Conversation.update(surface.get_size(), playerInventory)
        surface.blit(Talk.Conversation.render(mouse_pos, clicked), conversation_rect.topleft)

    @staticmethod
    def stop(forceExit: bool = False):
        if not Talk.autoExit or forceExit:
            Talk.running = False

    @staticmethod
    def start(display: pygame.Surface, player_inventory: KDS.Inventory.Inventory, KDS_Quit: Callable, autoExit: bool = False) -> bool: # Tells the caller if the story mode event should kick in
        global requestReturnAlt
        pygame.mouse.set_visible(True)
        Talk.storyTrigger = False
        global talk_ad, old_ads
        loopStopper = 0
        ad_index = -1
        while (ad_index in old_ads or ad_index == -1) and loopStopper < 10:
            ad_index = random.randint(0, len(talk_ads) - 1)
            loopStopper += 1
        del old_ads[0]
        old_ads.append(ad_index)
        talk_ad = talk_ads[ad_index]
        display_size = display.get_size()
        Talk.running = True
        Talk.autoExit = autoExit

        exit_button = KDS.UI.Button(pygame.Rect(940, 700, 230, 80), Talk.stop, KDS.UI.ButtonFont.render("EXIT", True, (KDS.Colors.AviatorRed)))
        ReqRet = "MISSION" if requestReturnAlt == None else requestReturnAlt
        request_mission_button = KDS.UI.Button(pygame.Rect(50, 700, 450, 80), Mission.Request, f"REQUEST {ReqRet}")
        return_mission_button = KDS.UI.Button(pygame.Rect(510, 700, 420, 80), Mission.Return, f"RETURN {ReqRet}")

        KDS.Missions.Listeners.KoponenTalk.Trigger()

        while Talk.running:
            mouse_pos = pygame.mouse.get_pos()
            conversation_mouse_pos = (mouse_pos[0] - conversation_rect.left, mouse_pos[0] - conversation_rect.top)
            c = False
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key in KDS.Keys.toggleFullscreen.Bindings:
                        pygame.display.toggle_fullscreen()
                        KDS.ConfigManager.ToggleSetting("Renderer/fullscreen", ...)
                    elif event.key == K_F4:
                        if pygame.key.get_pressed()[K_LALT]:
                            KDS_Quit()
                    elif event.key == K_ESCAPE:
                        Talk.stop()
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        c = True
                elif event.type == QUIT:
                    KDS_Quit()
                elif event.type == MOUSEWHEEL:
                    Talk.Conversation.scroll = KDS.Math.Clamp(Talk.Conversation.scroll - line_scroll_speed * event.y, 0, max(len(Talk.lines) - Talk.lineCount, 0))

            Talk.renderMenu(display, mouse_pos, c, player_inventory)

            exit_button.update(display, mouse_pos, c)
            request_mission_button.update(display, mouse_pos, c)
            return_mission_button.update(display, mouse_pos, c, player_inventory)

            pygame.display.flip()
            display.fill(KDS.Colors.Black)
            KDS.Clock.Tick()

        pygame.mouse.set_visible(False)
        return Talk.storyTrigger

class KoponenEntity:

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.animations = KDS.Animator.MultiAnimation(
            idle = KDS.Animator.Animation("koponen_idle", 2, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop),
            walk = KDS.Animator.Animation("koponen_walk", 2, 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        )
        self.speed = KDS.ConfigManager.GetGameData("Physics/Koponen/speed")
        self.movement = [self.speed, 4]
        self.collisions = KDS.World.Collisions()

        self.listeners = []
        self.listenerInstances: Dict[str,  KDS.Missions.Listener] = {}

        self.ls_instructions: List[str] = []
        self.current_instruction: int = 0
        self.last_instruction: str = ""

        self.air_time = 0
        self.y_velocity = 0

        self._move = True
        self.forceIdle = False
        self.enabled = True
        self.task_counter = 0

        self._aut_moving = True
        self._aut_moving_time = 0
        self._aut_idle = True
        self._aut_idle_time = 0
        self._path_finder_on = False

        self.allow_talk = False
        self.force_talk = False
        self.start_with_talk = False

        self.mover = KDS.World.EntityMover()

    def update(self, tiles, display, quitHandler):
        if self._move and not self.forceIdle:
            #region Handling randomisation
            if self._path_finder_on:
                raise NotImplementedError("Path finding will most likely not be implemented for Koponen") #The pathfinding thing
            elif self._aut_moving: #Handling AI movements
                if self._aut_idle_time >= KOPONEN_MIN_AUT_IDLE_TIME:
                    self._aut_idle_time = 0
                    self.movement[0] = abs(self.speed) * random.choice([-1, 1])
                self._aut_moving_time += 1
                if self._aut_moving_time >= KOPONEN_MIN_AUT_MOVE_TIME: # This comment has no usage
                    if randChance(KOPONEN_IDLE_CHANCE):
                        self._aut_moving = False
                        self._aut_idle = True
            elif self._aut_idle:
                if self._aut_moving_time >= KOPONEN_MIN_AUT_MOVE_TIME:
                    self._aut_moving_time = 0
                    self.movement[0] = 0
                self._aut_idle_time += 1
                if self._aut_idle_time >= KOPONEN_MIN_AUT_IDLE_TIME:
                    if randChance(KOPONEN_WALK_CHANCE):
                        self._aut_idle = False
                        self._aut_moving = True
            #endregion
            self.collisions = self.mover.move(self.rect, self.movement, tiles)
        else:
            if not self.forceIdle:
                self.collisions = self.mover.move(self.rect, self.movement, tiles)

        self.handleInstructions(tiles)
        if self.collisions.left or self.collisions.right:
            self.movement[0] *= -1
            self.AI_jump(tiles, "left" if self.collisions.left else "right")

        if self.collisions.bottom:
            self.air_time = 0
            self.y_velocity = 0
        else:
            self.air_time += 1

        self.y_velocity += 0.5
        self.y_velocity = min(8.0, self.y_velocity)
        self.movement[1] = self.y_velocity

        if self.movement[0] != 0 and self._move and not self.forceIdle:
            self.animations.trigger("walk")
        else:
            self.animations.trigger("idle")

    def handleInstructions(self, tiles: List[List[List]]):
        class execFuncs:
            allowedFuncs: Dict[str, Callable] = {}
            @staticmethod
            def SetTileProperty(x: int, y: int, index: int, propertyName: str, value: Any):
                nonlocal tiles
                setattr(tiles[y][x][index], propertyName, value)
            @staticmethod
            def SetSelfProperty(propertyName: str, value: Any):
                nonlocal self
                setattr(self, propertyName, value)
            @staticmethod
            def PlaySoundFromFile(filepath: str):
                KDS.Audio.PlayFromFile(filepath)
            @staticmethod
            def SetMissionProgress(missionName: str, taskName: str, progress: float):
                KDS.Missions.SetProgress(missionName, taskName, progress)

        execFuncs.allowedFuncs = {
            "SetTileProperty": execFuncs.SetTileProperty,
            "SetSelfProperty": execFuncs.SetSelfProperty,
            "PlaySoundFromFile": execFuncs.PlaySoundFromFile,
            "SetMissionProgress": execFuncs.SetMissionProgress
        }

        if self.current_instruction < len(self.ls_instructions):
            instruction = self.ls_instructions[self.current_instruction]
            new_instruction = instruction != self.last_instruction
            self.last_instruction = instruction

            args = instruction.split(":", 1)
            if len(args):
                if args[0] == "move":
                    if new_instruction: self.stopAutoMove()
                    if len(args) > 1:
                        coordinates: List[int] = []
                        for c in args[1].split(","):
                            coordinates.append(int(c))
                        if self.rect.collidepoint((coordinates[0], coordinates[1])):
                            self.current_instruction += 1
                            self.continueAutoMove()
                        else:
                            self.movement[0] = self.speed if coordinates[0] > self.rect.x else -self.speed
                    else:
                        self.continueAutoMove()
                        self.current_instruction += 1
                elif args[0] == "exec":
                    if re.fullmatch(r"[a-zA-Z]+\(.*\)", args[1]) != None:
                        execFuncName, execArgs = args[1].split("(", 1)
                        execArgs = [a.removesuffix(",") for a in shlex.split(execArgs.removesuffix(")"))]
                        execFunc = execFuncs.allowedFuncs[execFuncName] if execFuncName in execFuncs.allowedFuncs else None
                        if execFunc != None:
                            execCArgs = [KDS.Convert.AutoType3(a) for a in execArgs]
                            try:
                                execFunc(*execCArgs) #type: ignore (tää disabloi ton tyhmän errorin)
                            except Exception as e:
                                KDS.Logging.AutoError(f"Exec function {execFuncName} failed on instruction {self.current_instruction} with message: {e}")
                        else:
                            KDS.Logging.AutoError(f"Exec function not found on instruction {self.current_instruction}")
                    else:
                        KDS.Logging.AutoError(f"Exec syntax error on instruction {self.current_instruction}")
                    self.current_instruction += 1
            else:
                self.current_instruction += 1

    def render(self, Surface: pygame.Surface, scroll: list):
        if KDS.Debug.Enabled:
            pygame.draw.rect(Surface, KDS.Colors.Cyan, (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h))
        self.animations.update()
        Surface.blit(self.animations.get_frame(), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def reset(self) -> None:
        pass

    def stopAutoMove(self) -> None:
        self._move = False
        #Mä tuun vielä ihan varmasti lisäämään näihin kahteen jotain, että jumalauta jos joku koskee näihin funktioihin ja muuttaa koodia niin että näitä funktioita ei ole

    def continueAutoMove(self) -> None:
        self._move = True

    def AI_jump(self, obstacles, collision_type : str):
        x_coor = 0
        if collision_type == "right":
            x_coor = (self.rect.x + self.rect.w) // 34
        else:
            x_coor = (self.rect.x) // 34 - 1
        y_coor = (self.rect.y + self.rect.h) // 34 - 1
        try:
            jump = True
            for y in range(math.ceil(self.rect.h / 34)):
                for obst in obstacles[y_coor - 1 - y][x_coor]:
                    if obst.checkCollision:
                        jump = False
                        break
            if jump:
                self.movement[0] = -self.movement[0]
                self.rect.y -= 35
        except Exception as e:
            KDS.Logging.AutoError(e)

    def setEnabled(self, state: bool = True) -> None:
        self.enabled = state

    def listenerTrigger_0(self):
        if self.task_counter == 1:
            self.listenerInstances["TileSleepEnd"].OnTrigger -= self.listenerTrigger_0
            self.enabled = True
        else:
            self.task_counter += 1

    def setListeners(self, listener_names: List[str] = []):
        for listener in listener_names:
            if listener == "TileSleepEnd":
                self.enabled = False
                tempListener = getattr(KDS.Missions.Listeners, listener, None)
                if tempListener != None:
                    self.listenerInstances[listener] = tempListener
                    self.listenerInstances[listener].OnTrigger += self.listenerTrigger_0
            else:
                KDS.Logging.AutoError("This has not been implemented yet!")

    def loadScript(self, script: list = []) -> None:
        self.ls_instructions = script
