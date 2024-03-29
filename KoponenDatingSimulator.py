﻿#region Importing
from __future__ import annotations

import os
#region Startup Config
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
#endregion
from datetime import datetime

import json
import random
import shutil
import traceback
from enum import IntEnum, IntFlag, auto
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

import pygame
import pygame.mixer
from pygame.locals import *

import KDS.AI
import KDS.Animator
import KDS.Application
import KDS.Audio
import KDS.Build
import KDS.Clock
import KDS.Colors
import KDS.ConfigManager
import KDS.Console
import KDS.Convert
import KDS.Debug
import KDS.Events
import KDS.Gamemode
import KDS.Inventory
import KDS.Jobs
import KDS.Keys
import KDS.Koponen
import KDS.Linq
import KDS.Loading
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.NPC
import KDS.School
import KDS.Scores
import KDS.Story
import KDS.System
import KDS.Teachers
import KDS.UI
import KDS.World
#endregion
#region Priority Initialisation
pygame.init()

# No longer required as pygame doesn't force its ugly cursor on you anymore.
# pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)

CompanyLogo = pygame.image.load("Assets/Textures/Branding/kl_corporation-logo.png")

pygame.display.set_icon(pygame.image.load("Assets/Textures/Branding/gameIcon.png"))
pygame.display.set_caption("Koponen Dating Simulator")
display_size = (1200, 800)
display: pygame.Surface = pygame.display.set_mode(display_size, RESIZABLE | DOUBLEBUF | HWSURFACE | SCALED)

# LOGO (here to make the blink from starting the window much shorter)
display.fill(CompanyLogo.get_at((0, 0)))
display.blit(pygame.transform.smoothscale(CompanyLogo, (500, 500)), (display_size[0] // 2 - 250, display_size[1] // 2 - 250))
pygame.display.flip()
# LOGO

screen_size = (600, 400)
screen = pygame.Surface(screen_size)

pygame.event.set_allowed((
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYDOWN,
    KEYUP,
    MOUSEWHEEL,
    QUIT,
    WINDOWFOCUSLOST
))
#endregion
#region Quit Handling
def KDS_Quit(confirm: bool = False, remove_data_s: bool = False):
    global main_running, main_menu_running, tcagr_running, esc_menu, settings_running, selectedSave, tick, remove_data_on_quit, level_finished_running
    if not confirm or KDS.System.MessageBox.Show("Quit?", "Are you sure you want to quit?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
        main_menu_running = False
        main_running = False
        tcagr_running = False
        esc_menu = False
        KDS.Koponen.Talk.running = False
        settings_running = False
        remove_data_on_quit = remove_data_s
        level_finished_running = False
#endregion
#region Initialisation
class PersistentPaths:
    AppData = os.path.join(str(os.getenv('APPDATA')), "KL Corporation", "Koponen Dating Simulator")
    Cache = os.path.join(AppData, "cache")
    Saves = os.path.join(AppData, "saves")
    Logs = os.path.join(AppData, "logs")
    Screenshots = os.path.join(AppData, "screenshots")
    CustomMaps = os.path.join(AppData, "custom_maps")
os.makedirs(PersistentPaths.AppData, exist_ok=True)
os.makedirs(PersistentPaths.Cache, exist_ok=True)
KDS.System.emptdir(PersistentPaths.Cache)
KDS.System.hide(PersistentPaths.Cache)
os.makedirs(PersistentPaths.Saves, exist_ok=True)
os.makedirs(PersistentPaths.Logs, exist_ok=True)
os.makedirs(PersistentPaths.Screenshots, exist_ok=True)
os.makedirs(PersistentPaths.CustomMaps, exist_ok=True)

KDS.Logging.init(PersistentPaths.AppData, PersistentPaths.Logs)
KDS.ConfigManager.init(PersistentPaths.AppData, PersistentPaths.Cache, PersistentPaths.Saves)
KDS.Logging.debug("Initialising Game...")
KDS.Logging.debug("Initialising Display Driver...")

if KDS.ConfigManager.GetSetting("Renderer/fullscreen", ...):
    pygame.display.toggle_fullscreen()

KDS.Logging.debug("Initialising KDS modules...")
KDS.Audio.init()
KDS.Jobs.init()
KDS.AI.init()
KDS.World.init()
KDS.Missions.init()
KDS.Scores.init()
KDS.Koponen.init()
KDS.Logging.debug("KDS modules initialised.")
KDS.Console.init(display, display, _KDS_Quit = KDS_Quit)
KDS.School.init(display)
KDS.Keys.LoadCustomBindings()

cursorIndex: int = KDS.ConfigManager.GetSetting("UI/cursor", ...)
cursorData = {
    1: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor1.xbm", "Assets/Textures/UI/Cursors/cursor1.xbm"),
    2: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor2.xbm", "Assets/Textures/UI/Cursors/cursor2.xbm"),
    3: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor3.xbm", "Assets/Textures/UI/Cursors/cursor3.xbm"),
    4: pygame.cursors.arrow,
    5: pygame.cursors.tri_left
}
if cursorIndex in cursorData: pygame.mouse.set_cursor(*cursorData[cursorIndex])
del cursorData

surfarrayLagFix = pygame.surfarray.pixels2d(screen)
# Creating a surfarray for the first time is not noticeable on faster hardware like my desktop,
# but lags the shit out of the game on my laptop with an amazing two-core processor.
del surfarrayLagFix
#endregion
#region Loading
#region Settings
KDS.Logging.debug("Loading Settings...")
tcagr: bool = KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)
current_map: str = KDS.ConfigManager.GetSetting("Player/currentMap", ...)
current_map_name: str = ""
maxParticles: int = KDS.ConfigManager.GetSetting("Renderer/Particle/maxCount", ...)
play_walk_sound: bool = KDS.ConfigManager.GetSetting("Mixer/walkSound", ...)
KDS.Logging.debug("Settings Loaded.")
#endregion
KDS.Logging.debug("Loading Assets...")
pygame.event.pump()
#region Fonts
KDS.Logging.debug("Loading Fonts...")
score_font = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10)
tip_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10)
teleport_message_font = pygame.font.Font("Assets/Fonts/gamefont2_extended.ttf", 10)
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25)
ArialFont = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", 28)
ArialTitleFont = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", 72)
KDS.Logging.debug("Font Loading Complete.")
#endregion
pygame.event.pump()
#region UI Textures
text_icon = pygame.image.load("Assets/Textures/Branding/textIcon.png").convert()
text_icon.set_colorkey(KDS.Colors.White)
level_cleared_icon = pygame.image.load("Assets/Textures/UI/LevelCleared.png").convert()
level_cleared_icon.set_colorkey(KDS.Colors.White)
#endregion
pygame.event.pump()
#region Building Textures
KDS.Logging.debug("Loading Building Textures...")
door_open: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/door_front.png").convert()
exit_door_open: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/door_open.png").convert_alpha()
KDS.Logging.debug("Building Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Item Textures
KDS.Logging.debug("Loading Item Textures...")
red_key = pygame.image.load("Assets/Textures/Items/red_key.png").convert()
green_key = pygame.image.load("Assets/Textures/Items/green_key2.png").convert()
blue_key = pygame.image.load("Assets/Textures/Items/blue_key.png").convert()
plasma_ammo = pygame.image.load("Assets/Textures/Items/plasma_ammo.png").convert()
pistol_f_texture = pygame.image.load("Assets/Textures/Items/pistol_firing.png").convert()
rk62_f_texture = pygame.image.load("Assets/Textures/Items/rk62_firing.png").convert()
shotgun_f = pygame.image.load("Assets/Textures/Items/shotgun_firing.png").convert()
ppsh41_f_texture = pygame.image.load("Assets/Textures/Items/ppsh41_f.png").convert()
awm_f_texture = pygame.image.load("Assets/Textures/Items/awm_f.png").convert()

red_key.set_colorkey(KDS.Colors.White)
green_key.set_colorkey(KDS.Colors.White)
blue_key.set_colorkey(KDS.Colors.White)
plasma_ammo.set_colorkey(KDS.Colors.White)
pistol_f_texture.set_colorkey(KDS.Colors.White)
rk62_f_texture.set_colorkey(KDS.Colors.White)
shotgun_f.set_colorkey(KDS.Colors.White)
ppsh41_f_texture.set_colorkey(KDS.Colors.White)
awm_f_texture.set_colorkey(KDS.Colors.White)
KDS.Logging.debug("Item Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Menu Textures
KDS.Logging.debug("Loading Menu Textures...")
gamemode_bc_1_1 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode/Gamemode_bc_1_1.png").convert()
gamemode_bc_1_2 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode/Gamemode_bc_1_2.png").convert()
gamemode_bc_2_1 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode/Gamemode_bc_2_1.png").convert()
gamemode_bc_2_2 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode/Gamemode_bc_2_2.png").convert()
main_menu_background_2 = pygame.image.load("Assets/Textures/UI/Menus/Main/main_menu_bc2.png").convert()
main_menu_background_3 = pygame.image.load("Assets/Textures/UI/Menus/Main/main_menu_bc3.png").convert()
main_menu_background_4 = pygame.image.load("Assets/Textures/UI/Menus/Main/main_menu_bc4.png").convert()
main_menu_background = pygame.image.load("Assets/Textures/UI/Menus/Main/main_menu_bc.png").convert()
settings_background = pygame.image.load("Assets/Textures/UI/Menus/settings_bc.png").convert()
agr_background = pygame.image.load("Assets/Textures/UI/Menus/tcagr_bc.png").convert()
arrow_button = pygame.image.load("Assets/Textures/UI/Buttons/Arrow.png").convert_alpha()
main_menu_title = pygame.image.load("Assets/Textures/UI/Menus/Main/main_menu_title.png").convert()
main_menu_title.set_colorkey(KDS.Colors.White)
KDS.Logging.debug("Menu Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Audio
KDS.Logging.debug("Loading Audio Files...")
gasburner_clip = pygame.mixer.Sound("Assets/Audio/Items/gasburner_pickup.ogg")
gasburner_fire = pygame.mixer.Sound("Assets/Audio/Items/gasburner_use.ogg")
door_opening = pygame.mixer.Sound("Assets/Audio/Tiles/door.ogg")
door_locked = pygame.mixer.Sound("Assets/Audio/Tiles/door_locked.ogg")
coffeemug_sound = pygame.mixer.Sound("Assets/Audio/Items/coffeemug.ogg")
knife_pickup = pygame.mixer.Sound("Assets/Audio/Items/knife_pickup.ogg")
key_pickup = pygame.mixer.Sound("Assets/Audio/Items/key_pickup.ogg")
ss_sound = pygame.mixer.Sound("Assets/Audio/Items/ssbonuscard_pickup.ogg")
lappi_sytytyspalat_sound = pygame.mixer.Sound("Assets/Audio/Items/lappisytytyspalat_pickup.ogg")
ppsh41_shot = pygame.mixer.Sound("Assets/Audio/Items/ppsh41_shoot.ogg")
landmine_explosion = pygame.mixer.Sound("Assets/Audio/Tiles/landmine_explosion.ogg")
hurt_sound = pygame.mixer.Sound("Assets/Audio/Effects/player_hurt.ogg")
plasmarifle_f_sound = pygame.mixer.Sound("Assets/Audio/Items/plasmarifle_shoot.ogg")
weapon_pickup = pygame.mixer.Sound("Assets/Audio/Items/weapon_pickup.ogg")
item_pickup = pygame.mixer.Sound("Assets/Audio/Items/default_pickup.ogg")
plasma_hitting = pygame.mixer.Sound("Assets/Audio/Effects/plasma_hit.ogg")
pistol_shot = pygame.mixer.Sound("Assets/Audio/Effects/pistol_shoot.ogg")
rk62_shot = pygame.mixer.Sound("Assets/Audio/Items/rk62_shoot.ogg")
glug_sound = pygame.mixer.Sound("Assets/Audio/Effects/glug.ogg")
shotgun_shot = pygame.mixer.Sound("Assets/Audio/Effects/shotgun_shoot.ogg")
archvile_attack = pygame.mixer.Sound("Assets/Audio/Effects/flame.ogg")
archvile_death = pygame.mixer.Sound("Assets/Audio/Entities/archvile_death.ogg")
fart = pygame.mixer.Sound("Assets/Audio/Effects/player_fart.ogg")
soulsphere_pickup = pygame.mixer.Sound("Assets/Audio/Items/soulsphere_pick.ogg")
pray_sound = pygame.mixer.Sound("Assets/Audio/Tiles/decorative_head_pray.ogg")
decorative_head_wakeup_sound = pygame.mixer.Sound("Assets/Audio/Tiles/decorative_head_wakeup.ogg")
awm_shot = pygame.mixer.Sound("Assets/Audio/Items/awm_shot.ogg")
smg_shot = pygame.mixer.Sound("Assets/Audio/Items/smg_shoot.ogg")
grenade_throw = pygame.mixer.Sound("Assets/Audio/Items/grenade_throw.ogg")
lantern_pickup = pygame.mixer.Sound("Assets/Audio/Items/lantern_pickup.ogg")
camera_shutter = pygame.mixer.Sound("Assets/Audio/Effects/camera_shutter.ogg")
flicker_trigger_sound = pygame.mixer.Sound("Assets/Audio/Tiles/flicker_trigger.ogg")
patja_kaatuminen = pygame.mixer.Sound("Assets/Audio/Tiles/patja_kaatuminen.ogg")
respawn_anchor_sounds = [
    pygame.mixer.Sound("Assets/Audio/Tiles/respawn_anchor_0.ogg"),
    pygame.mixer.Sound("Assets/Audio/Tiles/respawn_anchor_1.ogg"),
    pygame.mixer.Sound("Assets/Audio/Tiles/respawn_anchor_2.ogg")
]
decorative_head_wakeup_sound.set_volume(0.5)
plasmarifle_f_sound.set_volume(0.05)
hurt_sound.set_volume(0.6)
plasma_hitting.set_volume(0.03)
rk62_shot.set_volume(0.9)
shotgun_shot.set_volume(0.8)
KDS.Logging.debug("Audio File Loading Complete.")
#endregion
pygame.event.pump()
KDS.Logging.debug("Asset Loading Complete.")
#endregion
#region Variable Initialisation
ambient_tint = pygame.Surface(screen_size)
black_tint = pygame.Surface(screen_size, SRCALPHA)
black_tint.fill((20, 20, 20))
black_tint.set_alpha(170)

pauseOnFocusLoss: bool = KDS.ConfigManager.GetSetting("Game/pauseOnFocusLoss", ...)

remove_data_on_quit = False

main_running = True
currently_on_mission = False
current_mission = "none"
shoot = False

KDS.Logging.debug("Defining Variables...")
selectedSave = 0

esc_menu = False

gamemode_bc_1_alpha = KDS.Animator.Value(0.0, 255.0, 8, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
gamemode_bc_2_alpha = KDS.Animator.Value(0.0, 255.0, 8, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)

go_to_main_menu = False
go_to_console = False

main_menu_running = False
level_finished_running = False
tcagr_running = False
mode_selection_running = False
settings_running = False

renderPlayer = True

Tiles: List[List[List[KDS.Build.Tile]]] = []
Items: List[KDS.Build.Item] = []
Zones: List[KDS.World.Zone] = []

Entities: List[Union[KDS.Teachers.Teacher, KDS.NPC.NPC, KDS.AI.HostileEnemy]] = []

Projectiles: List[KDS.World.Bullet] = []
BallisticObjects: List[KDS.World.BallisticProjectile] = []
Explosions: List[KDS.World.Explosion] = []

Lights: List[KDS.World.Lighting.Light] = []
Particles: List[KDS.World.Lighting.Particle] = []

level_finished = False
HitTargets: Dict[KDS.Build.Tile, KDS.World.HitTarget] = {}
enemy_difficulty = 1
overlays: List[KDS.Build.Tile] = []
LightScroll = [0, 0]
renderUI = True
walk_sound_delay = 0
level_background_img: Optional[pygame.Surface] = None

true_scroll = [0.0, 0.0]
SCROLL_OFFSET = (301, 221)

stand_size = (28, 63)
crouch_size = (28, 34)
jump_velocity = 2.0

Koponen: KDS.Koponen.KoponenEntity = KDS.Koponen.KoponenEntity((0, 0), (0, 0))

koponen_talk_tip = tip_font.render(f"Puhu Koposelle [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

KDS.Logging.debug("Variable Defining Complete.")
#endregion
#region Game Settings
fall_speed: float = 0.4
fall_multiplier: float = 2.5
fall_max_velocity: float = 8.0
def LoadGameSettings():
    global fall_speed, fall_multiplier, fall_max_velocity, item_fall_speed, item_fall_max_velocity
    fall_speed = KDS.ConfigManager.GetGameData("Physics/Player/fallSpeed")
    fall_multiplier = KDS.ConfigManager.GetGameData("Physics/Player/fallMultiplier")
    fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Player/fallMaxVelocity")
    item_fall_speed = KDS.ConfigManager.GetGameData("Physics/Items/fallSpeed")
    item_fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Items/fallMaxVelocity")
try:
    LoadGameSettings()
except:
    KDS.Logging.AutoError("Game Settings could not be loaded!")

debug_gamesetting_allow_subprog_debug: bool = KDS.ConfigManager.GetGameData("Debug/allowSubprogramTesting")
debug_gamesetting_allow_console_in_storymode: bool = KDS.ConfigManager.GetGameData("Debug/allowConsoleInStoryMode")
#endregion
#region World Data
class WorldData:
    MapSize = (0, 0)
    PlayerStartPos = (-1, -1)

    @staticmethod
    def LoadMap(MapPath: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        global Items, Tiles, Enemies, Projectiles, overlays, Player, Zones
        if not (os.path.isdir(MapPath) and os.path.isfile(os.path.join(MapPath, "level.dat")) and os.path.isfile(os.path.join(MapPath, "levelprop.kdf")) ):
            #region Error String
            KDS.Logging.AutoError(f"""##### MAP FILE ERROR #####
    Map Directory: {os.path.isdir(MapPath)}
        Level File: {os.path.isfile(os.path.join(MapPath, "level.dat"))}
        LevelProp File: {os.path.isfile(os.path.join(MapPath, "levelprop.kdf"))}
        Level Music File (optional): {os.path.isfile(os.path.join(MapPath, "music.ogg"))}
        Properties File (optional): {os.path.isfile(os.path.join(MapPath, "properties.kdf"))}
        Level Background File (optional): {os.path.isfile(os.path.join(MapPath, "background.png"))}
    ##### MAP FILE ERROR #####""")
            #endregion
            KDS.System.MessageBox.Show("Map Error", "This map is currently unplayable. You can find more details in the log file.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.EXCLAMATION)
            KDS.Loading.Circle.Stop()
            return None
                        #pos,     type,      key,  value
        properties: Dict[str, Dict[str, Dict[str, Union[str, int, float, bool]]]] = {}
        if os.path.isfile(os.path.join(MapPath, "properties.kdf")):
            properties = KDS.ConfigManager.JSON.Get(os.path.join(MapPath, "properties.kdf"), KDS.ConfigManager.JSON.NULLPATH, {}, encoding="utf-8")
        global level_background_img
        if os.path.isfile(os.path.join(MapPath, "background.png")):
            level_background_img = pygame.image.load(os.path.join(MapPath, "background.png")).convert()
        else:
            level_background_img = None

        with open(os.path.join(MapPath, "level.dat"), "r", encoding="utf-8") as map_file:
            map_data = map_file.read().split("\n")

        max_map_width = len(max(map_data))
        WorldData.MapSize = (max_map_width, len(map_data))

        for _r in Tiles:
            for _t in _r:
                for _u in _t:
                    _u.onDestroy()
        Tiles = [[[] for x in range(WorldData.MapSize[0] + 1)] for y in range(WorldData.MapSize[1] + 1)]
        overlays = []

        KDS.ConfigManager.LevelProp.init(MapPath)
        KDS.World.Dark.Configure(KDS.ConfigManager.LevelProp.Get("Rendering/Darkness/enabled", False), KDS.ConfigManager.LevelProp.Get("Rendering/Darkness/strength", 0))
        Player.light = KDS.ConfigManager.LevelProp.Get("Rendering/Darkness/playerLight", True)
        Player.disableSprint = KDS.ConfigManager.LevelProp.Get("Entities/Player/disableSprint", False)
        Player.direction = KDS.ConfigManager.LevelProp.Get("Entities/Player/spawnInverted", False)

        tmpInventory: Dict[str, int] = KDS.ConfigManager.LevelProp.Get("Entities/Player/Inventory", {})
        for k, v in tmpInventory.items():
            if k.isnumeric() and int(k) < len(Player.inventory) and v in KDS.Build.Item.serialNumbers:
                Player.inventory.pickupItemToIndex(int(k), KDS.Build.Item.serialNumbers[v]((0, 0), v), force=True)
            else:
                KDS.Logging.AutoError(f"Value: {v} cannot be assigned to index: {k} of Player Inventory.")
        KDS.Build.Item.infiniteAmmo = KDS.ConfigManager.LevelProp.Get("Data/infiniteAmmo", False)

        WorldData.PlayerStartPos: Tuple[int, int] = KDS.ConfigManager.LevelProp.Get("Entities/Player/startPos", (100, 100))
        k_start_pos: Tuple[int, int] = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/startPos", (200, 200))
        global Koponen
        Koponen = KDS.Koponen.KoponenEntity(k_start_pos, (24, 64))
        Koponen.setEnabled(KDS.ConfigManager.LevelProp.Get("Entities/Koponen/enabled", False))
        Koponen.forceIdle = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/forceIdle", False)
        Koponen.allow_talk = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/talk", False)
        Koponen.force_talk = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/forceTalk", False)
        Koponen.start_with_talk = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/startWithTalk", False)
        Koponen.setListeners(KDS.ConfigManager.LevelProp.Get("Entities/Koponen/listeners", []))
        koponen_script = KDS.ConfigManager.LevelProp.Get("Entities/Koponen/lscript", [])
        if len(koponen_script) > 0:
            Koponen.loadScript(koponen_script)

        KDS.UI.Indicator.Enabled = KDS.ConfigManager.LevelProp.Get("Rendering/Indicator/enabled", True)

        Enemy.total = 0
        Enemy.death_count = 0
        Entity.total = 0
        Entity.death_count = 0
        Entity.agro_count = 0

        y = 0
        #region Main Map
        for row in map_data:
            x = 0
            for datapoint in row.split(" "):
                # Tänne jokaisen blockin käsittelyyn liittyvä koodi
                if len(datapoint) < 1 or datapoint.isspace():
                    continue

                if "/" in datapoint:
                    x += 1
                    continue

                identifier = f"{x}-{y}"
                if identifier in properties:
                    idProp = properties[identifier]
                    if "9" in idProp: # 9 is an unspecified type.
                        tlProp = idProp["9"]
                        if "overlay" in tlProp:
                            ovSerial = int(tlProp["overlay"])
                            if ovSerial not in KDS.Build.Tile.specialTiles: # Currently only tiles are supported
                                tmpOV = KDS.Build.Tile((x * 34, y * 34), ovSerial)
                            else:
                                tmpOV = KDS.Build.Tile.specialTilesClasses[ovSerial]((x * 34, y * 34), serialNumber=ovSerial)
                            for k, v in tlProp.items():
                                setattr(tmpOV, k, v)
                                # Does not set darkOverlay, but probably not needed.
                            overlays.append(tmpOV)

                if len(datapoint) == 4 and int(datapoint) != 0:
                    serialNumber = int(datapoint[1:])
                    pointer = int(datapoint[0])
                    value = None
                    if pointer == 0:
                        if serialNumber not in KDS.Build.Tile.specialTiles:
                            value = KDS.Build.Tile((x * 34, y * 34), serialNumber=serialNumber)
                            Tiles[y][x].append(value)
                        else:
                            value = KDS.Build.Tile.specialTilesClasses[serialNumber]((x * 34, y * 34), serialNumber=serialNumber)
                            Tiles[y][x].append(value)
                    elif pointer == 1:
                        value = KDS.Build.Item.serialNumbers[serialNumber]((x * 34, y * 34), serialNumber=serialNumber)
                        Items.append(value)
                    elif pointer == 2:
                        value = Enemy.serialNumbers[serialNumber]((x * 34,y * 34))
                        Entities.append(value)
                        Enemy.total += 1
                    elif pointer == 3:
                        value = BaseTeleport.serialNumbers[serialNumber]((x * 34, y * 34), serialNumber)
                        Tiles[y][x].append(value)
                    elif pointer == 4:
                        value = Entity.serialNumbers[serialNumber]((x * 34, y * 34))
                        Entities.append(value)
                        Entity.total += 1
                    else:
                        KDS.Logging.AutoError(f"Invalid pointer at ({x}, {y})")

                    if identifier in properties:
                        idProp = properties[identifier]
                        idPropCheck = str(pointer)
                        if idPropCheck in idProp:
                            for k, v in idProp[idPropCheck].items():
                                if k == "checkCollision" and isinstance(value, KDS.Build.Tile): # Checking instance instead of pointer so that Pylance is happy.
                                    value.checkCollision = bool(v)
                                    if not v and value.texture != None and isinstance(value.texture, pygame.Surface): # Some tiles have animations as texture
                                        tex: Any = value.texture.convert_alpha()
                                        tex.fill((0, 0, 0, 64), special_flags=BLEND_RGBA_MULT)
                                        value.darkOverlay = tex
                                elif k == "collisionDirection" and isinstance(value, KDS.Build.Tile):
                                    if isinstance(v, str):
                                        value.collisionDirection = KDS.World.CollisionDirection[v]
                                    elif isinstance(v, int):
                                        value.collisionDirection = KDS.World.CollisionDirection(v)
                                    else:
                                        KDS.Logging.AutoError("Invalid collision direction in properties!")
                                else:
                                    setattr(value, k, v)
            y += 1
        #endregion

        #region Zones
        if "zones" in properties:
            for k, v in properties["zones"].items():
                zoneKSplit = k.split("-")
                zoneKRect = pygame.Rect(int(zoneKSplit[0]) * 34, int(zoneKSplit[1]) * 34, int(zoneKSplit[2]) * 34, int(zoneKSplit[3]) * 34)
                Zones.append(KDS.World.Zone(zoneKRect, v))
        #endregion

        #region LateInit
        # lateInit order is the reverse of pointers
        for entity in Entities:
            entity.lateInit()
        for item in Items:
            item.lateInit()
        for overlay in overlays:
            overlay.lateInit()
        for row in Tiles:
            for unit in row:
                for tile in unit:
                    tile.lateInit()
        #endregion

        for teleportData in BaseTeleport.teleportDatas.values():
            teleportData.Order()

        if os.path.isfile(os.path.join(MapPath, "music.ogg")):
            KDS.Audio.Music.Load(os.path.join(MapPath, "music.ogg"))
        else:
            KDS.Audio.Music.Unload()
        return WorldData.PlayerStartPos, k_start_pos
#endregion
#region Data
KDS.Logging.debug("Loading Data...")

with open("Assets/Data/Build/tiles.kdf", "r", encoding="utf-8") as f:
    tileData: Dict[str, Dict[str, Any]] = json.loads(f.read())
t_textures: Dict[int, pygame.Surface] = {}
for d in tileData.values():
    d_srl = d["serialNumber"]
    t_textures[d_srl] = pygame.image.load(f"""Assets/Textures/Tiles/{d["path"]}""").convert()
    t_textures[d_srl].set_colorkey(KDS.Colors.White)

with open("Assets/Data/Build/teleports.kdf", "r", encoding="utf-8") as f:
    teleportData: Dict[str, Dict[str, Any]] = json.loads(f.read())
telep_textures: Dict[int, Optional[pygame.Surface]] = {}
for d in teleportData.values():
    telep_textures[d["serialNumber"]] = pygame.image.load(f"""Assets/Textures/Teleports/{d["path"]}""").convert()

with open("Assets/Data/Build/items.kdf", "r", encoding="utf-8") as f:
    itemData: Dict[str, Dict[str, Any]] = json.loads(f.read())
i_textures: Dict[int, pygame.Surface] = {}
for d in itemData.values():
    d_srl = d["serialNumber"]
    i_textures[d_srl] = pygame.image.load(f"""Assets/Textures/Items/{d["path"]}""").convert()
    i_textures[d_srl].set_colorkey(KDS.Colors.White)

path_sounds: Dict[str, List[pygame.mixer.Sound]] = {}
default_paths = os.listdir("Assets/Audio/Tiles/path_sounds/default")
sounds = []
for p in default_paths:
    sounds.append(pygame.mixer.Sound(os.path.join("Assets/Audio/Tiles/path_sounds/default", p)))
path_sounds["default"] = sounds
#for p in path_sounds_temp:
#    path_sounds[int(p)] = pygame.mixer.Sound(path_sounds_temp[p])
del default_paths, sounds

KDS.Build.init(tileData, itemData, t_textures, i_textures)

def defaultEventHandler(event: pygame.event.Event, *ignore: int) -> bool:
    if event.type in ignore:
        return False

    if event.type == KDS.Audio.MUSICENDEVENT:
        KDS.Audio.Music.OnEnd.Invoke()
        return True
    elif event.type == KEYDOWN:
        if event.key in KDS.Keys.toggleDebug.Bindings:
            KDS.Debug.Enabled = not KDS.Debug.Enabled
            KDS.Logging.Profiler(KDS.Debug.Enabled)
            return True
        elif event.key in KDS.Keys.toggleFullscreen.Bindings:
            pygame.display.toggle_fullscreen()
            KDS.ConfigManager.ToggleSetting("Renderer/fullscreen", ...)
            return True
    elif event.type == QUIT:
        KDS_Quit(confirm=True)
        return True
    return False

class ScreenEffects:
    class Effects(IntFlag):
        Flicker = 1
        FadeInOut = 2
        Glitch = 4

    triggered: Effects
    OnEffectFinish = KDS.Events.Event()

    class EffectData:
        Flicker = {
            "repeat_rate": 2,
            "repeat_length": 12,
            "repeat_index": 0
        }
        FadeInOut = {
            "animation": KDS.Animator.Value(0.0, 255.0, 120),
            "reversed": False,
            "wait_index": 0,
            "wait_length": 240,
            "surface": pygame.Surface(screen_size).convert()
        }
        Glitch = {
            "repeat_rate": 2,
            "repeat_index": 0,
            "current_glitch": ((0, 0, 0, 0), (0, 0))
        }

    @staticmethod
    def Queued() -> bool:
        return ScreenEffects.triggered != 0

    @staticmethod
    def Trigger(effect: ScreenEffects.Effects):
        ScreenEffects.triggered |= effect

    @staticmethod
    def Get(effect: ScreenEffects.Effects) -> bool:
        return effect in ScreenEffects.triggered

    @staticmethod
    def Finish(effect: ScreenEffects.Effects):
        ScreenEffects.triggered &= ~effect
        ScreenEffects.OnEffectFinish.Invoke(effect)

    @staticmethod
    def Clear():
        ScreenEffects.triggered = ScreenEffects.Effects(0)
ScreenEffects.Clear()

#region Animations
koponen_animations = KDS.Animator.MultiAnimation(
    idle = KDS.Animator.Animation("koponen_idle", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
    walk = KDS.Animator.Animation("koponen_walk", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player")
)
menu_gasburner_animation = KDS.Animator.Animation(
    "main_menu_bc_gasburner", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
gasburner_animation_object = KDS.Animator.Animation("gasburner_on", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
menu_toilet_animation = KDS.Animator.Animation(
    "menu_toilet_anim", 3, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
menu_trashcan_animation = KDS.Animator.Animation(
    "menu_trashcan", 3, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
burning_tree = KDS.Animator.Animation("tree_burning", 4, 5, (0, 0, 0), KDS.Animator.OnAnimationEnd.Loop)
explosion_animation = KDS.Animator.Animation(
    "explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
plasmarifle_animation = KDS.Animator.Animation(
    "plasmarifle_firing", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
zombie_death_animation = KDS.Animator.Animation(
    "z_death", 5, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
zombie_walk_animation = KDS.Animator.Animation(
    "z_walk", 3, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
zombie_attack_animation = KDS.Animator.Animation(
    "z_attack", 4, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
sergeant_walk_animation = KDS.Animator.Animation(
    "seargeant_walking", 4, 8, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
sergeant_shoot_animation = KDS.Animator.Animation(
    "seargeant_shooting", 2, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)

archvile_run_animation = KDS.Animator.Animation(
    "archvile_run", 3, 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
arhcvile_attack_animation = KDS.Animator.Animation(
    "archvile_attack", 6, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
archvile_death_animation = KDS.Animator.Animation(
    "archvile_death", 7, 12, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
flames_animation = KDS.Animator.Animation(
    "flames", 5, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
bulldog_run_animation = KDS.Animator.Animation(
    "bulldog", 5, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

imp_walking = KDS.Animator.Animation(
    "imp_walking", 4, 19, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
imp_attacking = KDS.Animator.Animation(
    "imp_attacking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
imp_dying = KDS.Animator.Animation(
    "imp_dying", 5, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)

knife_animation_object = KDS.Animator.Animation(
    "knife", 2, 20, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

KDS.Logging.debug("Animation Loading Complete.")
#endregion
KDS.Logging.debug("Data Loading Complete.")
#endregion
#region Tiles
KDS.Logging.debug("Loading Tiles...")
class Toilet(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int, _burning=False):
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = t_textures[serialNumber]
        self.animation = KDS.Animator.Animation("toilet_anim", 3, 5, (KDS.Colors.White), KDS.Animator.OnAnimationEnd.Loop)
        self.checkCollision = True
        self.light_scale = 150

    def update(self):
        global renderPlayer
        if KDS.Math.getDistance((Player.rect.centerx, Player.rect.centery), self.rect.center) < 50 and Gasburner.burning and not self.burning:
            self.burning = True
            KDS.Scores.score += 30
            renderPlayer = True
        if self.burning:
            if 130 < self.light_scale < 170:
                self.light_scale += random.randint(-3, 6)
            elif self.light_scale > 160:
                self.light_scale -= 4
            else:
                self.light_scale += 4
            if random.randint(0, 2) == 0:
                Particles.append(KDS.World.Lighting.Fireparticle((random.randint(self.rect.x + 7, self.rect.x + self.rect.width - 13), self.rect.y + 8), random.randint(3, 6), 30, 1, color=(240, 200, 0)))
            Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(self.light_scale, 1700), True))
            return self.animation.update()
        else:
            return self.texture

class Trashcan(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int, _burning=False):
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = t_textures[serialNumber]
        self.animation = KDS.Animator.Animation("trashcan", 3, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.checkCollision = True
        self.light_scale = 150

    def update(self):

        if KDS.Math.getDistance((Player.rect.centerx, Player.rect.centery), self.rect.center) < 48 and Gasburner.burning and not self.burning:
            self.burning = True
            KDS.Scores.score += 20
        if self.burning:
            if 130 < self.light_scale < 170:
                self.light_scale += random.randint(-3, 6)
            elif self.light_scale > 160:
                self.light_scale -= 4
            else:
                self.light_scale += 4
            if random.randint(0, 2) == 0:
                Particles.append(KDS.World.Lighting.Fireparticle((random.randint(self.rect.x, self.rect.x + self.rect.width - 16), self.rect.y + 8), random.randint(3, 6), 30, 1, color=(240, 200, 0)))
            Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(self.light_scale, 1700), True))
            return self.animation.update()
        else:
            return self.texture

def _load_jukebox_songs() -> list[pygame.mixer.Sound]:
    musikerna = os.listdir("Assets/Audio/JukeboxMusic/")
    songs = []
    for musiken in musikerna:
        songs.append(pygame.mixer.Sound("Assets/Audio/JukeboxMusic/" + musiken))
    # random.shuffle(songs)
    # This feels useless as we access songs randomly anyways...

    return songs

class Jukebox(KDS.Build.Tile):
    songs: list[pygame.mixer.Sound] = _load_jukebox_songs()

    tmp_jukebox_data = tip_font.render(f"Use Jukebox [Click: {KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    tmp_jukebox_data2 = tip_font.render(f"Stop Jukebox [Hold: {KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    jukebox_tip: pygame.Surface = pygame.Surface((max(tmp_jukebox_data.get_width(), tmp_jukebox_data2.get_width()), tmp_jukebox_data.get_height() + tmp_jukebox_data2.get_height()), SRCALPHA)
    jukebox_tip.blit(tmp_jukebox_data, ((tmp_jukebox_data2.get_width() - tmp_jukebox_data.get_width()) / 2, 0))
    jukebox_tip.blit(tmp_jukebox_data2, ((tmp_jukebox_data.get_width() - tmp_jukebox_data2.get_width()) / 2, tmp_jukebox_data.get_height()))
    del tmp_jukebox_data, tmp_jukebox_data2

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.checkCollision = False
        self.playing = -1
        self.lastPlayed = [-69 for _ in range(5)]
        self.channel = None

    def stopPlayingTrack(self):
        for music in Jukebox.songs:
            music.stop()
        self.playing = -1
        self.channel = None
        KDS.Audio.Music.Unpause()

    def playRandomTrack(self):
        KDS.Audio.Music.Pause()
        loopStopper = 0
        while (self.playing in self.lastPlayed or self.playing == -1) and loopStopper < 10:
            self.playing = random.randint(0, len(Jukebox.songs) - 1)
            loopStopper += 1
        self.lastPlayed.pop(0)
        self.lastPlayed.append(self.playing)
        self.channel = KDS.Audio.PlaySound(Jukebox.songs[self.playing], KDS.Audio.MusicVolume)

    def update(self):
        if self.rect.colliderect(Player.rect):
            screen.blit(Jukebox.jukebox_tip, (self.rect.centerx - scroll[0] - Jukebox.jukebox_tip.get_width() / 2, self.rect.y - scroll[1] - 30))
            if KDS.Keys.functionKey.clicked and not KDS.Keys.functionKey.holdClicked:
                self.stopPlayingTrack()
                self.playRandomTrack()
            elif KDS.Keys.functionKey.held: self.stopPlayingTrack()
        if self.channel != None and not self.channel.get_busy():
            for music in Jukebox.songs: # Fix freeze on Python 3.11
                music.stop()            # Fix freeze on Python 3.11
            self.playRandomTrack()
        if self.playing != -1:
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 600 # Bigger value means volume gets smaller at a smaller rate
            jukebox_volume = KDS.Math.Clamp01(KDS.Math.Lerp(1.5, 0, lerp_multiplier))
            Jukebox.songs[self.playing].set_volume(jukebox_volume)
            Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(100, 1000), True))

        return self.texture

class Door(KDS.Build.Tile):
    keys = {
        24: "red",
        25: "blue",
        26: "green"
    }

    def __init__(self, position: Tuple[int, int], serialNumber: int, closingCounter = -1):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = door_open
        self.rect = pygame.Rect(position[0], position[1], 5, 68)
        self.open = False
        self.maxClosingCounter = closingCounter
        self.closingCounter = 0
        self.lateRender = True

    def lateInit(self):
        self.darkOverlay = None
        self.checkCollision = not self.open

    def update(self):
        self.checkCollision = not self.open
        if self.open:
            if self.maxClosingCounter > 0:
                self.closingCounter += 1
            else:
                self.closingCounter = self.maxClosingCounter
            if self.closingCounter > self.maxClosingCounter:
                KDS.Audio.PlaySound(door_opening)
                self.open = False
                self.closingCounter = 0
        if KDS.Math.getDistance(Player.rect.midbottom, self.rect.midbottom) < 20 and KDS.Keys.functionKey.clicked:
            if self.serialNumber == 23 or Player.keys[Door.keys[self.serialNumber]]:
                KDS.Audio.PlaySound(door_opening)
                self.closingCounter = 0
                self.open = not self.open
                if not self.open:
                    if self.rect.centerx - Player.rect.centerx > 0:
                        Player.rect.right = self.rect.left
                    else:
                        Player.rect.left = self.rect.right
            else:
                KDS.Audio.PlaySound(door_locked)
        return self.texture if not self.open else self.opentexture

class Landmine(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1] + 26, 22, 11)
        self.checkCollision = False

    def update(self):
        if Player.rect.colliderect(self.rect) or any([r.rect.colliderect(self.rect) for r in Entities]):
            if KDS.Math.getDistance(Player.rect.center, self.rect.center) < 100:
                Player.health -= 100 - KDS.Math.getDistance(Player.rect.center, self.rect.center)
            for entity in Entities:
                if KDS.Math.getDistance(entity.rect.center, self.rect.center) < 100:
                    entity.health -= 120 - round(KDS.Math.getDistance(entity.rect.center, self.rect.center))
            KDS.Audio.PlaySound(landmine_explosion)
            Explosions.append(KDS.World.Explosion(KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop), (self.rect.x - 60, self.rect.y - 60)))
            self.removeFlag = True
        return self.texture

class Ladder(KDS.Build.Tile):
    sounds = [pygame.mixer.Sound("Assets/Audio/Tiles/ladder_0.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/ladder_1.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/ladder_2.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/ladder_3.ogg")]
    ct = 0
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] + round(17 - self.texture.get_width() / 2), position[1] + round(17 - self.texture.get_height() / 2), self.texture.get_width(), self.texture.get_height())
        self.checkCollision = False

    def update(self):
        if self.rect.colliderect(Player.rect):
            Player.onLadder = True
        return self.texture

    def lateInit(self):
        self.darkOverlay = None

class Lamp(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1], 14, 21)
        self.checkCollision = True
        self.coneheight = 90

    def lateInit(self):
        global Tiles
        y = 0
        r = True
        while r:
            y += 33
            for row in Tiles:
                for unit in row:
                    for tile in unit:
                        if tile.rect.collidepoint((self.rect.centerx, self.rect.y + self.rect.height + y)) and tile.serialNumber != 22 and tile.checkCollision:
                            y = y - (self.rect.y + self.rect.height + y - tile.rect.y) + 8
                            r = False
            if y > 154:
                r = False
        self.coneheight = y

    def update(self):
        if random.randint(0, 10) != 10:
            btmidth = int(self.coneheight * 80 / 90)
            Lights.append(KDS.World.Lighting.Light((self.rect.x - btmidth // 2 + 7, self.rect.y + 16), KDS.World.Lighting.lamp_cone(10, btmidth, self.coneheight, (200, 200, 200))))
        return self.texture

class LampChain(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] + 6, position[1], 1, 34)
        self.checkCollision = True

    def update(self):
        return self.texture

class DecorativeHead(KDS.Build.Tile):
    decorative_head_tip: pygame.Surface = tip_font.render(f"Activate Head [Hold: {KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]-26, 28, 60)
        self.checkCollision = False
        self.praying = False
        self.prayed = False

    def update(self):
        if self.rect.colliderect(Player.rect):
            if not self.prayed:
                screen.blit(DecorativeHead.decorative_head_tip, (self.rect.centerx - scroll[0] - DecorativeHead.decorative_head_tip.get_width() // 2, self.rect.top - scroll[1] - 20))
                if KDS.Keys.functionKey.pressed and not self.praying:
                    KDS.Audio.PlaySound(pray_sound)
                    self.praying = True
                elif not KDS.Keys.functionKey.pressed and self.praying:
                    pray_sound.stop()
                    self.praying = False
                if KDS.Keys.functionKey.held:
                    self.prayed = True
                    KDS.Audio.PlaySound(decorative_head_wakeup_sound)
            else:
                if not KDS.Keys.functionKey.pressed:
                    pray_sound.stop()
                    self.praying = False
                if Player.health > 0:
                    Player.health = min(Player.health + 0.01, 100)
        else:
            pray_sound.stop()
            self.praying = False

        if self.prayed:
            if KDS.World.Dark.enabled:
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 1900), True))
            else:
                day_light = KDS.World.Lighting.Shapes.circle.get(150, 1900).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - day_light.get_width() // 2, self.rect.centery - scroll[1] - day_light.get_height() // 2))
        return self.texture

class Tree(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]-50, 47, 84)
        self.checkCollision = False

    def update(self):
        return self.texture

class Rock0(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]+19, 32, 15)
        self.checkCollision = True

    def update(self):
        return self.texture

class Torch(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = KDS.Animator.Animation("tall_torch_burning", 4, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0], position[1] - 16, 20, 50)
        self.checkCollision = False
        self.light_scale = 150

    def update(self):
        if 130 < self.light_scale < 170:
            self.light_scale += random.randint(-3, 6)
        elif self.light_scale > 160:
            self.light_scale -= 4
        else:
            self.light_scale += 4
        if random.randint(0, 4) == 0:
            Particles.append(KDS.World.Lighting.Fireparticle((self.rect.centerx - 3, self.rect.y + 8), random.randint(3, 6), 30, 1))
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(self.light_scale, 1900), True))
        return self.texture.update()

class GoryHead(KDS.Build.Tile):
    blh: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/bloody_h.png").convert()
    blh.set_colorkey(KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1] - 28, 34, 62)
        self.checkCollision = False
        self.gibbed = False
        HitTargets[self] = KDS.World.HitTarget(self.rect)

    def update(self):
        if not self.gibbed and HitTargets[self].hitted:
            self.gibbed = True
            self.texture = GoryHead.blh
            HitTargets.pop(self)
        return self.texture

class LevelEnder(KDS.Build.Tile):
    level_ender_tip: pygame.Surface = tip_font.render(f"Finish level [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1] - 16, 34, 50)
        self.checkCollision = False

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.top + 10), KDS.World.Lighting.Shapes.circle.get(40, 40000), True))
        if self.rect.colliderect(Player.rect):
            screen.blit(LevelEnder.level_ender_tip, (self.rect.centerx - LevelEnder.level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                KDS.Missions.Listeners.LevelEnder.Trigger()
        return t_textures[self.serialNumber]

class LevelEnderDoor(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = exit_door_open
        self.rect = pygame.Rect(position[0], position[1] - 34, 34, 68)
        self.checkCollision = False
        self.opened = False
        self.propOpen = False
        self.interactable: bool = True
        self.showTip = False

    def update(self):
        if self.rect.colliderect(Player.rect) or self.propOpen:
            if self.showTip: screen.blit(LevelEnder.level_ender_tip, (self.rect.centerx - LevelEnder.level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked or self.propOpen:
                if self.interactable:
                    if not self.propOpen:
                        KDS.Missions.Listeners.LevelEnder.Trigger()
                        Player.visible = False
                    KDS.Audio.PlaySound(door_opening)
                    self.opened = True
                else:
                    KDS.Audio.PlaySound(door_locked)
                self.propOpen = False
        return self.texture if not self.opened else self.opentexture

class LevelEnderTransparent(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = None
        self.triggered: bool = False

        self.listener = None
        self.listenerItem = None
        self.readyToTrigger: bool = True
        self.listenerInstance: Optional[Union[KDS.Missions.Listener, KDS.Missions.ItemListener]] = None

    def eventHandler(self, *args: Any):
        if len(args) < 1 or (isinstance(self.listenerInstance, KDS.Missions.ItemListener) and args[0] != self.listenerItem):
            return
        assert self.listenerInstance != None
        self.listenerInstance.OnTrigger -= self.eventHandler
        self.listenerInstance = None
        self.readyToTrigger = True

    def lateInit(self):
        if self.listener != None:
            tmpListener: Optional[KDS.Missions.Listener] = getattr(KDS.Missions.Listeners, self.listener, None)
            if tmpListener != None and (not isinstance(tmpListener, KDS.Missions.ItemListener) or self.listenerItem != None):
                self.listenerInstance = tmpListener
                self.listenerInstance.OnTrigger += self.eventHandler
                self.readyToTrigger = False

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect) and self.readyToTrigger and not self.triggered:
            KDS.Missions.Listeners.LevelEnder.Trigger()
            self.triggered = True
        return None

class Candle(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = KDS.Animator.Animation("candle_burning", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0], position[1]+14, 20, 20)
        self.checkCollision = False
        self.light_scale = 40

    def update(self):
        if random.randint(0, 5) == 5:
            self.light_scale = random.randint(20, 60)
        if random.randint(0, 50) == 0:
            Particles.append(KDS.World.Lighting.Fireparticle((self.rect.centerx - 3, self.rect.y), random.randint(3, 6), 20, 0.01))
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - self.light_scale // 2, self.rect.y - self.light_scale // 2), KDS.World.Lighting.Shapes.circle.get(self.light_scale, 2000)))
        return self.texture.update()

class LampPoleLamp(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0]-6, position[1]-6, 40, 40)
        self.checkCollision = False

    def update(self):
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5000), True))
        return self.texture

class Chair(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0]-6, position[1]-8, 40, 42)
        self.checkCollision = False

    def update(self):
        return self.texture

class SkullTile(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0]+7, position[1]+7, 27, 27)
        self.checkCollision = False

    def update(self):
        return self.texture

class WallLight(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.checkCollision = False
        self.direction = serialNumber == 72
        self.light_t = pygame.transform.flip(KDS.World.Lighting.Shapes.cone_hard.get(100, 6200), self.direction, False)

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - (17 * KDS.Convert.ToMultiplier(self.direction)), self.rect.centery), self.light_t, True))
        return self.texture

class RespawnAnchor(KDS.Build.Tile):
    respawn_anchor_on: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/respawn_anchor_on.png").convert()

    active: Optional[RespawnAnchor] = None
    rspP_list = []
    respawn_anchor_tip: pygame.Surface = tip_font.render(f"Set Respawn Point [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.ontexture = RespawnAnchor.respawn_anchor_on
        self.checkCollision = False
        RespawnAnchor.rspP_list.append(self)

    def update(self):
        if RespawnAnchor.active is self:
            if KDS.World.Dark.enabled:
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 2400), True))
            else:
                day_light = KDS.World.Lighting.Shapes.circle.get(150, 2400).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - day_light.get_width() // 2, self.rect.centery - scroll[1] - day_light.get_height() // 2))
            return self.ontexture

        if self.rect.colliderect(Player.rect):
            screen.blit(RespawnAnchor.respawn_anchor_tip, (self.rect.centerx - scroll[0] - RespawnAnchor.respawn_anchor_tip.get_width() // 2, self.rect.top - scroll[1] - 50))
            if KDS.Keys.functionKey.clicked:
                RespawnAnchor.active = self
                KDS.Audio.PlaySound(random.choice(respawn_anchor_sounds))
        return self.texture

class Spruce(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] - 10, position[1] - 40, 63, 75)
        self.checkCollision = False

    def update(self):
        return self.texture

class AllahmasSpruce(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] - 10, position[1] - 40, 63, 75)
        self.checkCollision = False
        self.spruce_colors = (0.0, 60.0, 120.0, 240.0)
        self.colorIndex = 0
        self.colorTicks = 60
        self.colorTick = 0

    def update(self):
        self.colorTick += 1
        if self.colorTick > self.colorTicks:
            self.colorTick = 0
            self.colorIndex += 1
            self.colorIndex = 0 if self.colorIndex >= len(self.spruce_colors) else self.colorIndex
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.splatter.getColor(150, self.spruce_colors[self.colorIndex], 1.0, 1.0), True))
        return self.texture

class Methtable(KDS.Build.Tile):
    o_sounds = [pygame.mixer.Sound("Assets/Audio/Tiles/methtable_0.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/methtable_1.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/methtable_2.ogg")]
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("methtable_rescaled", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        # for index, im in enumerate(self.animation.images):
        #     self.animation.images[index] = pygame.transform.scale(im, (round(im.get_width() / 2.5), round(im.get_height() / 2.5))) # WTF????
        # self.rect = pygame.Rect(position[0] - (self.animation.images[0].get_width() - 34), position[1] - (self.animation.images[0].get_height() - 34), self.animation.images[0].get_width(), self.animation.images[0].get_height())
        # self.checkCollision = False

    def update(self):
        if random.randint(0, 105) == 50:
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 200 # Bigger value means volume gets smaller at a smaller rate
            sound_volume = KDS.Math.Clamp01(KDS.Math.Lerp(1, 0, lerp_multiplier))
            sound = random.choice(Methtable.o_sounds)
            sound.set_volume(sound_volume)
            KDS.Audio.PlaySound(sound)
        return self.animation.update()

class FlickerTrigger(KDS.Build.Tile):
    def __init__(self, position, serialNumber, repeating: bool = False) -> None:
        super().__init__(position, serialNumber)
        self.checkCollision = False
        self.exited: bool = True
        self.readyToTrigger: bool = True
        self.animation: bool = False
        self.repeating: bool = repeating
        self.texture = None
        self.listener = None
        self.listenerItem = None
        self.listenerInstance: Optional[Union[KDS.Missions.Listener, KDS.Missions.ItemListener]] = None

    def flickerEnd(self, effect: ScreenEffects.Effects):
        if effect == ScreenEffects.Effects.Flicker and self.animation:
            ScreenEffects.OnEffectFinish -= self.flickerEnd
            self.animation = False
            self.readyToTrigger = self.repeating # ready to trigger if repeats
            flicker_trigger_sound.stop()
            KDS.Audio.UnpauseAllSounds()

    def eventHandler(self, *args: Any):
        if len(args) < 1 or (isinstance(self.listenerInstance, KDS.Missions.ItemListener) and args[0] != self.listenerItem):
            return
        assert self.listenerInstance != None
        self.listenerInstance.OnTrigger -= self.eventHandler
        self.listenerInstance = None
        self.readyToTrigger = True

    def lateInit(self):
        if self.listener != None:
            tmpListener: Optional[KDS.Missions.Listener] = getattr(KDS.Missions.Listeners, self.listener, None)
            if tmpListener != None and (not isinstance(tmpListener, KDS.Missions.ItemListener) or self.listenerItem != None):
                self.listenerInstance = tmpListener
                self.listenerInstance.OnTrigger += self.eventHandler
                self.readyToTrigger = False
        self.darkOverlay = None

    def update(self):
        if self.rect.colliderect(Player.rect):
            if self.exited and self.readyToTrigger:
                self.animation = True
                self.readyToTrigger = False
                self.exited = False
                KDS.Audio.PauseAllSounds()
                KDS.Audio.PlaySound(flicker_trigger_sound)
                ScreenEffects.Trigger(ScreenEffects.Effects.Flicker)
                ScreenEffects.OnEffectFinish += self.flickerEnd
        else:
            self.exited = True

        return self.texture

class ImpaledBody(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.animation = KDS.Animator.Animation("impaled_corpse", 2, 50, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0] - (self.animation.images[0].get_width() - 34), position[1] - (self.animation.images[0].get_height() - 34), self.animation.images[0].get_width(), self.animation.images[0].get_height())
        self.checkCollision = False

    def update(self):
        return self.animation.update()

class Barrier(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)

    def lateInit(self) -> None:
        self.checkCollision = True
        self.darkOverlay = None

    def update(self):
        return None

class GroundFire(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("ground_fire", 3, 4, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.checkCollision = False

    def update(self):
        if self.rect.colliderect(Player.rect) and random.randint(0, 55) == 20:
            Player.health -= random.randint(5, 10)
        if random.randint(0, 2) == 0: Particles.append(KDS.World.Lighting.Fireparticle((self.rect.x + random.randint(0, 34), self.rect.y + 15 + random.randint(0, 12)), random.randint(3, 10), random.randint(1, 20), random.randint(2, 5)))
        return self.animation.update()

class TileFire(KDS.Build.Tile):
    # Has to be cached... Otherwise it will use way too much RAM
    cachedAnimation = KDS.Animator.Animation("tileFire", 32, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Tiles")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.gridPos = (position[0] // 34, position[1] // 34)
        self.animationOffset = random.randint(0, TileFire.cachedAnimation.ticks - 1)
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.checkCollision = False
        self.randomSoundWait()
        self.randomSpreadWait()

    def randomSpreadWait(self):
        self.spreadWait: int = random.randint(5 * 60, 15 * 60)

    def randomSoundWait(self):
        self.soundWait = random.randint(3 * 60, 5 * 60)

    def update(self):
        global Tiles
        oldTick = TileFire.cachedAnimation.tick
        TileFire.cachedAnimation.tick = (TileFire.cachedAnimation.tick + self.animationOffset) % TileFire.cachedAnimation.ticks
        frame = TileFire.cachedAnimation.update()
        TileFire.cachedAnimation.tick = oldTick

        if self.rect.colliderect(Player.rect) and random.randint(0, 55) == 20:
            Player.health -= random.randint(5, 10)

        self.soundWait -= 1
        if self.soundWait < 0:
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 600 # Bigger value means volume gets smaller at a smaller rate
            volume_modifier = KDS.Math.Clamp01(KDS.Math.Lerp(1.5, 0, lerp_multiplier))
            volume = (random.random() / 4) * volume_modifier
            if volume > 0:
                KDS.Audio.PlayFromFile("Assets/Audio/Effects/fire.ogg", clip_volume=volume)
            self.randomSoundWait()

        self.spreadWait -= 1
        if self.spreadWait < 0:
            randomPos = (random.randint(self.gridPos[0] - 1, self.gridPos[0] + 1), random.randint(self.gridPos[1] - 1, self.gridPos[1] + 1))
            if TileFire.createInstanceAtPosition(randomPos):
                self.randomSpreadWait()

        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle_harder.get(34 * 5, 1850), True))

        return frame

    @staticmethod
    def isUnitFreeOfFire(gridPos: Tuple[int, int]) -> Tuple[bool, Tuple[int, int], List[KDS.Build.Tile]]:
        clampPos = KDS.Math.Clamp(gridPos[0], 0, WorldData.MapSize[0]), KDS.Math.Clamp(gridPos[1], 0, WorldData.MapSize[1])
        unit = Tiles[clampPos[1]][clampPos[0]]
        for t in unit:
            if isinstance(t, TileFire):
                return False, clampPos, unit
        return True, clampPos, unit

    @staticmethod
    def createInstanceAtPosition(gridPos: Tuple[int, int]) -> bool:
        global Tiles
        isFree, clampPos, unit = TileFire.isUnitFreeOfFire(gridPos)
        if not isFree:
            return False
        unit.append(TileFire((clampPos[0] * 34, clampPos[1] * 34), 151))
        KDS.Missions.Listeners.TileFireCreated.Trigger()
        return True

class GlassPane(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int) -> None:
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.texture = t_textures[serialNumber]
        self.texture.set_alpha(30)

    def lateInit(self):
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        return self.texture

class RoofPlanks(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        w, h = self.texture.get_size()
        w34 = 34 - w
        h34 = 34 - h
        self.rect = pygame.Rect(position[0] + w34, position[1] + h34, w, h)
        self.checkCollision = True

    def update(self):
        return self.texture

class Patja(KDS.Build.Tile):
    kaatunut_texture: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/patja_kaatunut.png").convert()
    kaatunut_texture.set_colorkey(KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int) -> None:
        super().__init__(position, serialNumber)
        # Rect is handled by trueScale
        self.texture = t_textures[serialNumber]
        self.kaatunutTexture = Patja.kaatunut_texture
        self.checkCollision = False
        self.kaatunut = False
        self.kaatumisTrigger = False
        self.kaatumisCounter = 0
        self.kaatumisDelay = 180

    def lateInit(self):
        self.darkOverlay = None

    def update(self):
        if self.rect.colliderect(Player.rect):
            self.kaatumisTrigger = True
        if self.kaatumisTrigger and not self.kaatunut:
            self.kaatumisCounter += 1
            if self.kaatumisCounter > self.kaatumisDelay:
                self.kaatunut = True
                KDS.Audio.PlaySound(patja_kaatuminen)
                if self.rect.colliderect(Player.rect):
                    Player.health -= random.randint(20, 60)
        return self.texture if not self.kaatunut else self.kaatunutTexture

class Crackhead(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("crackhead_smoking", 3, 14, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.checkCollision = False

    def update(self):
        return self.animation.update()

class DoorFront(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = exit_door_open
        self.rect = pygame.Rect(position[0], position[1] - 34, 34, 68)
        self.checkCollision = False
        self.opened = False
        self.locked = False
        self.showTip = False

    def lateInit(self):
        self.darkOverlay = None

    def update(self):
        if self.rect.colliderect(Player.rect):
            if self.showTip:
                screen.blit(LevelEnder.level_ender_tip, (self.rect.centerx - LevelEnder.level_ender_tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                if not self.locked:
                    KDS.Audio.PlaySound(door_opening)
                    self.opened = not self.opened
                else:
                    KDS.Audio.PlaySound(door_locked)
        return self.texture if not self.opened else self.opentexture

class DoorFrontMirrored(DoorFront):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.opentexture = pygame.image.load("Assets/Textures/Tiles/door_open_mirrored.png").convert_alpha()

    def update(self):
        return super().update()

class Sleepable(KDS.Build.Tile):
    tip = tip_font.render(f"Toggle Sleep [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.sleeping: bool = False
        self.fadeAnimation: bool = False
        self.sleepAutoEnd: bool = False # Works only with fadeAnimation
        self.requireTileSleepTask: bool = False
        self.audiofile: str = "Assets/Audio/Effects/zipper.ogg"
        self.disableSleep: bool = False

    def toggleSleep(self, effect: Optional[ScreenEffects.Effects] = None):
        global Player
        if effect != None:
            if effect == ScreenEffects.Effects.FadeInOut:
                ScreenEffects.OnEffectFinish -= self.toggleSleep
            else:
                return

        self.sleeping = not self.sleeping
        if self.sleeping:
            KDS.Missions.Listeners.TileSleepStart.Trigger()
            KDS.Audio.PlayFromFile(self.audiofile)
            if self.fadeAnimation:
                ScreenEffects.Trigger(ScreenEffects.Effects.FadeInOut)
        else:
            KDS.Missions.Listeners.TileSleepEnd.Trigger()
        #region Position Player Correctly
        Player.rect.bottomright = (self.rect.right - (34 - Player.rect.width) // 2, self.rect.bottom) # The camera will follow the player, but whatever... This is done so that Story enemy makes it's sound correctly
        Player.direction = False
        #endregion
        Player.visible = not Player.visible
        Player.lockMovement = not Player.lockMovement

    def update(self):
        if self.disableSleep:
            return self.texture

        if self.rect.colliderect(Player.rect):
            screen.blit(Sleepable.tip, (self.rect.centerx - Sleepable.tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked and (not self.requireTileSleepTask or KDS.Missions.Listeners.TileSleepStart.ContainsActiveTask()):
                if self.sleepAutoEnd:
                    ScreenEffects.OnEffectFinish += self.toggleSleep
                    if not self.sleeping:
                        self.toggleSleep()
                else:
                    self.toggleSleep()

        return self.texture

class Tent(Sleepable):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        #Rect will be set automatically with trueScale.
        self.checkCollision = False
        self.inTent: bool = False
        self.fadeAnimation: bool = False # Redundant
        self.autoOut: bool = False # Works only with fadeAnimation
        self.forceTentTask: bool = False
        self.audiofile: str = "Assets/Audio/Effects/zipper.ogg"

    def lateInit(self) -> None:
        self.sleeping = self.inTent
        self.sleepAutoEnd = self.autoOut
        self.requireTileSleepTask = self.forceTentTask
        super().lateInit()

class HotelBed(Sleepable):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.audiofile = "Assets/Audio/Tiles/hotel_bed.ogg"

class AvarnCar(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        assert self.texture != None
        self.texture.set_colorkey(KDS.Colors.Cyan)
        l_shape = pygame.transform.flip(KDS.World.Lighting.Shapes.cone_narrow.texture, True, True)
        l_shape = pygame.transform.scale(l_shape, (int(l_shape.get_width() * 0.3), int(l_shape.get_height() * 0.3))) # WTF???
        self.light = KDS.World.Lighting.Light((self.rect.x - l_shape.get_width() + 20, self.rect.y - 7), l_shape)
        self.hidden = False
        self.listener = None
        self.listenerInstance: Optional[KDS.Missions.Listener] = None
        self.cachedDarkOverlay = None

    def eventHandler(self):
        assert self.listenerInstance != None
        self.listenerInstance.OnTrigger -= self.eventHandler
        self.listenerInstance = None
        self.hidden = False
        if self.cachedDarkOverlay != None:
            self.darkOverlay = self.cachedDarkOverlay

    def lateInit(self):
        if self.listener != None:
            tmpListener: Optional[KDS.Missions.Listener] = getattr(KDS.Missions.Listeners, self.listener, None)
            if tmpListener != None:
                self.listenerInstance = tmpListener
                self.listenerInstance.OnTrigger += self.eventHandler
                self.hidden = True
        if self.hidden:
            self.cachedDarkOverlay = self.darkOverlay
            self.darkOverlay = None

    def update(self):
        #pygame.draw.circle(screen, KDS.Colors.Red, (self.rect.x - scroll[0], self.rect.y - scroll[1]), 5)
        if not self.hidden:
            Lights.append(self.light)
            return self.texture
        return None

class Sound(KDS.Build.Tile):
    def __init__(self, position, serialNumber, repeating: bool = False) -> None:
        super().__init__(position, serialNumber)
        self.checkCollision = False
        self.exited: bool = True
        self.readyToTrigger: bool = True
        self.texture = None
        self.repeating: bool = repeating
        self.filepath: Optional[str] = None
        self.volume: float = -1.0
        self.clip_volume: float = 1.0

    def lateInit(self):
        if self.filepath == None:
            KDS.Logging.AutoError("No filepath specified for Sound tile!")

    def update(self):
        if self.rect.colliderect(Player.rect):
            if self.exited and self.readyToTrigger:
                self.readyToTrigger = False
                self.exited = False
                if self.filepath != None:
                    KDS.Audio.PlayFromFile(self.filepath, volume=self.volume, clip_volume=self.clip_volume)
        elif not self.exited:
            self.readyToTrigger = self.repeating
            self.exited = True

        return self.texture

class FluorescentTube(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 5)

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.y + 170 // 2 + 5), KDS.World.Lighting.Shapes.fluorecent.get(170, 9500), True))
        return self.texture

class Kiuas(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1] - 31, 38, 65)
        self.animation = KDS.Animator.Animation("kiuas", 3, 3, KDS.Colors.White)
        self.light_scale = 150

    def update(self):
        if 130 < self.light_scale < 170:
            self.light_scale += random.randint(-3, 6)
        elif self.light_scale > 160:
            self.light_scale -= 4
        else:
            self.light_scale += 4
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(self.light_scale, 1900), True))
        return self.animation.update()

class Nysse(KDS.Build.Tile):
    tip: pygame.Surface = tip_font.render(f"Matkusta bussilla [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        # TrueScale flag
        self.blinker: bool = True
        self.headlights: bool = True
        self.blinkerIndex = 0
        self.blinkerRepeatRate = 180 # beats per minute
        self.blinkerLight: bool = False
        self.levelEnder: bool = False

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        if self.headlights:
            Lights.append(KDS.World.Lighting.Light((self.rect.x + 23, self.rect.y + 71), KDS.World.Lighting.Shapes.circle_harder.get(50, 5000), True))
            Lights.append(KDS.World.Lighting.Light((self.rect.x + 99, self.rect.y + 71), KDS.World.Lighting.Shapes.circle_harder.get(50, 5000), True))
        if self.blinker:
            if self.blinkerIndex == 0:
                self.blinkerLight = not self.blinkerLight
            if self.blinkerLight:
                Lights.append(KDS.World.Lighting.Light((self.rect.x + 18, self.rect.y + 68), KDS.World.Lighting.Shapes.circle_hard.get(10, 2550), True))
            self.blinkerIndex += self.blinkerRepeatRate
            if self.blinkerIndex > 3600:
                self.blinkerIndex = 0
        if self.levelEnder and self.rect.colliderect(Player.rect):
            screen.blit(Nysse.tip, (self.rect.centerx - Nysse.tip.get_width() // 2 - scroll[0], self.rect.y - 5 - Nysse.tip.get_height() - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                KDS.Missions.Listeners.LevelEnder.Trigger()
                Player.visible = False
                Player.lockMovement = True
        return self.texture

class Fucking(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("fucking", 11, 4, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        return self.animation.update()

class Shower(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.particleTick = 0
        self.particleWait = 60

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        self.particleTick = (self.particleTick + 1) % self.particleWait
        if self.particleTick == 0:
            Particles.append(KDS.World.Lighting.WaterParticle((self.rect.right - 3 - random.randint(0, 10), self.rect.top + 6), random.randint(1, 3), 3, random.randint(60, 120), Tiles, (0, 0, 255)))
        return self.texture

class PistokoeDoor(KDS.Build.Tile):
    tip: pygame.Surface = tip_font.render(f"Vaita peseneesi kadet [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.message: Optional[str] = None
        self.renderedMessage: Optional[pygame.Surface] = None
        self.used: bool = False
        self.allowMultipleUses: bool = False
        self.animation = KDS.Animator.Animation("kuuma_door", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

    def lateInit(self) -> None:
        self.darkOverlay = None
        if self.message != None:
            self.renderedMessage = teleport_message_font.render(self.message, True, KDS.Colors.White)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            if self.renderedMessage != None:
                screen.blit(self.renderedMessage, (self.rect.centerx - self.renderedMessage.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1] - (PistokoeDoor.tip.get_height() + 5 if not self.used else 0)))
            if not self.used:
                screen.blit(PistokoeDoor.tip, (self.rect.centerx - PistokoeDoor.tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
                if KDS.Keys.functionKey.clicked:
                    KDS.Missions.SetProgress("story_exam", "go_to_class", 1.0)
                    KDS.Audio.MusicMixer.pause()
                    quit_temp, exam_grade = KDS.School.Exam()
                    KDS.Audio.MusicMixer.unpause()
                    self.used = not self.allowMultipleUses
                    if quit_temp:
                        KDS_Quit()
                    elif KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
                        if KDS.ConfigManager.Save.Active != None:
                            KDS.ConfigManager.Save.Active.Story.examGrade = exam_grade
                        else:
                            KDS.Logging.AutoError("Could not save exam grade. No save active when gamemode is story.")
        return self.animation.update()

class CashRegister(KDS.Build.Tile):
    dropItemTip: pygame.Surface = tip_font.render(f"Aseta ostos [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    payTip: pygame.Surface = tip_font.render(f"Maksa euro [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    ssCardTip: pygame.Surface = tip_font.render(f"Nayta SS-Etukortti [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    sound: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Tiles/cashregister.ogg")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.items: List[KDS.Build.Item] = []
        self.itemIndexes: Dict[KDS.Build.Item, int] = {}
        self.items_cost: int = 0
        self.discount_items_cost: int = 0
        self.ssBonuscardShown: bool = False
        self.dropItemsRect: pygame.Rect = pygame.Rect(124 + self.rect.x, 0 + self.rect.y, 80, 102)
        self.payRect: pygame.Rect = pygame.Rect(57 + self.rect.x, 0 + self.rect.y, 41, 102)
        self.itemsBottomTarget: int = 72 + self.rect.y
        self.itemsLeftMoveRange: Tuple[int, int] = (45 + self.rect.x, 4 + self.rect.x)
        self.itemsMoveSpeed: int = -1

    @property
    def Cost(self) -> int:
        if not self.ssBonuscardShown:
            return max(self.items_cost, 0)
        else:
            return max(self.discount_items_cost, 0)

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        toRm: List[KDS.Build.Item] = []
        for item in self.items:
            if item not in self.itemIndexes or self.itemIndexes[item] >= len(Items) or Items[self.itemIndexes[item]] is not item:
                if item in Items:
                    self.itemIndexes[item] = Items.index(item) # Index saved, because checking if Item exists would rape the FPS so hard that Python would commit suicide
                else:
                    KDS.Missions.Listeners.Shoplifting.Trigger()
                    toRm.append(item)

        for item in toRm:
            self.items.remove(item)

        for item in self.items: # Maybe don't need this one, but I still put it just in case
            if item.rect.left > self.itemsLeftMoveRange[1]:
                item.rect.left += self.itemsMoveSpeed

        if self.payRect.colliderect(Player.rect):
            hndItm = Player.inventory.getHandItem()
            if isinstance(hndItm, Euro):
                screen.blit(CashRegister.payTip, (self.payRect.centerx - CashRegister.payTip.get_width() // 2 - scroll[0], self.payRect.y - 10 - scroll[1]))
                if KDS.Keys.functionKey.clicked and self.payEuro():
                    drpd = Player.inventory.dropItem()
                    if drpd == None:
                        KDS.Logging.AutoError("Could not drop Euro coin!")
            elif isinstance(hndItm, SSBonuscard):
                screen.blit(CashRegister.ssCardTip, (self.payRect.centerx - CashRegister.ssCardTip.get_width() // 2 - scroll[0], self.payRect.y - 10 - scroll[1]))
                if KDS.Keys.functionKey.clicked:
                    self.ssBonuscardShown = True
        elif self.dropItemsRect.colliderect(Player.rect):
            hndItm = Player.inventory.getHandItem()
            if isinstance(hndItm, KDS.Build.Item) and hndItm.storePrice != None:
                screen.blit(CashRegister.dropItemTip, (self.dropItemsRect.centerx - CashRegister.dropItemTip.get_width() // 2 - scroll[0], self.dropItemsRect.y + 20 - scroll[1]))
                if KDS.Keys.functionKey.clicked:
                    drpd = Player.inventory.dropItem()
                    if drpd != None:
                        if self.addItem(drpd):
                            KDS.Audio.PlaySound(CashRegister.sound)
                        else:
                            Player.inventory.pickupItem(drpd)

        assert self.texture != None, "Cash register texture should not be None!"
        screen.blit(self.texture, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        screen.blit(tip_font.render(f"{self.Cost}.00", True, KDS.Colors.Green), (self.rect.x - scroll[0] + 67, self.rect.y - scroll[1] + 51))

        return None

    def payEuro(self) -> bool:
        if self.Cost - 1 < 0:
            return False
        self.items_cost -= 1
        self.discount_items_cost -= 1
        self.moneyUpdate()
        return True

    def moneyUpdate(self):
        if self.Cost <= 0:
            for item in self.items:
                item.storePrice = None
                item.storeDiscountPrice = None
                KDS.Missions.Listeners.ItemPurchase.Trigger(item.serialNumber)
            self.items.clear()
        else:
            for item in self.items:
                item.storePrice = 0

    def addItem(self, item: KDS.Build.Item) -> bool:
        global Items
        if item.storePrice == None:
            return False
        self.items.append(item)
        Items.append(item)
        self.items_cost += item.storePrice
        self.discount_items_cost += item.storeDiscountPrice if item.storeDiscountPrice != None else item.storePrice
        item.rect.bottomleft = (self.itemsLeftMoveRange[0], self.itemsBottomTarget)
        self.moneyUpdate()
        return True

class TheftDetector(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("theft_detector", 2, 15, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.sound = pygame.mixer.Sound("Assets/Audio/Tiles/theft_detector.ogg")
        self.sound.set_volume(0.5)
        self.alarmTicks: int = 0
        self.alarmWaitTicks: int = 180

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        if self.alarmTicks <= 0:
            self.sound.stop()
            self.animation.tick = 0

            if self.rect.colliderect(Player.rect):
                for item in Player.inventory:
                    if item != None and item.storePrice != None:
                        self.alarmTicks = self.alarmWaitTicks
                        KDS.Audio.PlaySound(self.sound, loops=-1)
                        KDS.Missions.Listeners.Shoplifting.Trigger()
                        break
            return self.texture

        self.alarmTicks -= 1

        if abs(self.rect.centerx - Player.rect.centerx) > screen_size[0] / 2: # To stop sound playing infinitely
            self.alarmTicks = 0

        return self.animation.update()


class BaseTeleport(KDS.Build.Tile):
    class TeleportData:
        def __init__(self) -> None:
            self.index: int = 0
            self.teleports: List[BaseTeleport] = []
            self.allowNext: bool = True

        def Next(self, caller: BaseTeleport) -> Optional[BaseTeleport]:
            if not self.allowNext:
                return None

            self.index = self.teleports.index(caller) + 1
            if self.index >= len(self.teleports):
                self.index = 0

            self.allowNext = False
            return self.teleports[self.index]

        def Update(self):
            self.allowNext = True

        def Order(self) -> None:
            self.teleports.sort(key=lambda t: t.order)

    serialNumbers: Dict[int, Type[BaseTeleport]] = {}
    teleportDatas: Dict[int, BaseTeleport.TeleportData] = {}

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        self.message: Optional[str] = None
        self.renderedMessage: Optional[pygame.Surface] = None
        self.identifier: Optional[int] = None
        self.order: int = KDS.Math.MAXVALUE
        self.interactable: bool = True
        self.setDark: Optional[int] = None

        super().__init__(position, -1)
        self.serialNumber: int = serialNumber
        self.texture: Optional[pygame.Surface] = telep_textures[self.serialNumber]
        if self.texture != None:
            self.texture.set_colorkey(KDS.Colors.White)
        self.checkCollision: bool = False
        self.specialTileFlag: bool = True
        self.resetScroll: bool = True

        self.teleportSound: Optional[pygame.mixer.Sound] = None
        self.nonInteractableSound: Optional[pygame.mixer.Sound] = None
        self.messageOffset: Tuple[int, int] = (0, 0)
        self.teleportOffset: Tuple[int, int] = (0, 0)

        self.usetop: bool = False

        self.triggerStoryEnding: bool = False

    def lateInit(self):
        if self.message != None:
            self.renderedMessage = teleport_message_font.render(self.message, True, KDS.Colors.White)
        if self.identifier != None:
            if self.identifier not in BaseTeleport.teleportDatas:
                BaseTeleport.teleportDatas[self.identifier] = BaseTeleport.TeleportData()
            BaseTeleport.teleportDatas[self.identifier].teleports.append(self)
        else:
            KDS.Logging.AutoError(f"No identifier set for teleport at {self.rect.topleft}!")

    def renderMessage(self):
        if self.renderedMessage != None:
            screen.blit(self.renderedMessage, (self.rect.centerx - self.renderedMessage.get_width() // 2 - scroll[0] + self.messageOffset[0], self.rect.centery - self.renderedMessage.get_height() // 2 - scroll[1] + self.messageOffset[1]))

    def teleport(self):
        global trueScroll
        if self.identifier == None:
            KDS.Logging.AutoError("Teleport has no identifier!")
            return
        if not self.interactable:
            if self.nonInteractableSound != None:
                KDS.Audio.PlaySound(self.nonInteractableSound)
            return

        # Getting next teleport if available
        t = BaseTeleport.teleportDatas[self.identifier].Next(self)
        if t == None:
            return

        if self.triggerStoryEnding:
            KDS.Koponen.TriggerStoryEnding(Koponen)

        if self.teleportSound != None:
            KDS.Audio.PlaySound(self.teleportSound)
        # Executing teleporting process
        t.onTeleport()
        Player.rect.centerx = t.rect.centerx + t.teleportOffset[0]
        if not self.usetop:
            Player.rect.bottom = t.rect.bottom + t.teleportOffset[1]
        else:
            Player.rect.top = t.rect.top + t.teleportOffset[1]
        # Reseting scroll
        if self.resetScroll:
            true_scroll[0] += Player.rect.x - true_scroll[0] - SCROLL_OFFSET[0]
            true_scroll[1] += Player.rect.y - true_scroll[1] - SCROLL_OFFSET[1]
        # Setting Dark
        if self.setDark != None:
            KDS.World.Dark.Set(True, self.setDark)
        else:
            KDS.World.Dark.Reset()
        # Triggering Listener
        KDS.Missions.Listeners.Teleport.Trigger()

    def onTeleport(self):
        pass

class InvisibleTeleport(BaseTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.lastCollision: bool = False
        self.texture = None

    def update(self):
        collision = bool(self.rect.colliderect(Player.rect))
        if collision != self.lastCollision and collision:
            self.teleport()
        self.lastCollision = collision
        return None

    def onTeleport(self):
        self.lastCollision = True

class DoorTeleport(BaseTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(self.rect.x, self.rect.y - 34, 34, 68)
        self.teleportSound = None
        self.messageOffset = (0, -50)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            self.renderMessage()
            if KDS.Keys.functionKey.clicked:
                self.teleport()
        return self.texture

class WoodDoorTeleport(DoorTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.teleportSound = door_opening
        self.nonInteractableSound = door_locked

class LargeDoorTeleport(DoorTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(self.rect.x, self.rect.y, 68, 68)
        self.messageOffset = (0, -55)

class Elevator(DoorTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(self.rect.x, self.rect.y - 34, 102, 102)
        self.resetScroll = False

class HotelDoor(DoorTeleport):
    class DoorState(IntEnum):
        Default = auto()
        Accept = auto()
        Decline = auto()

    tip_render: pygame.Surface = tip_font.render(f"Use Keycard [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    acceptSound = pygame.mixer.Sound("Assets/Audio/Tiles/hotel_door_accept.ogg")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.resetStateTimer = 0
        self.state = HotelDoor.DoorState.Default
        self.lightPos = (self.rect.x + 26, self.rect.y + 25)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            self.messageOffset = (0, -50)
            if isinstance(Player.inventory.getHandItem(), HotelKeycard):
                self.messageOffset = (0, -50 - teleport_message_font.get_height() - 5)
                messageSize = self.renderedMessage.get_size() if self.renderedMessage != None else (0, 0)
                normalMessagePos = (self.rect.centerx - messageSize[0] // 2 - scroll[0] + self.messageOffset[0], self.rect.centery - messageSize[1] // 2 - scroll[1] + self.messageOffset[1])
                screen.blit(HotelDoor.tip_render, (self.rect.centerx - HotelDoor.tip_render.get_width() // 2 - scroll[0], normalMessagePos[1] + messageSize[1] + 5))

                if KDS.Keys.functionKey.clicked:
                    if self.interactable:
                        self.state = HotelDoor.DoorState.Accept
                        KDS.Audio.PlaySound(HotelDoor.acceptSound)
                    else:
                        self.state = HotelDoor.DoorState.Decline
            self.renderMessage()

        if self.state != HotelDoor.DoorState.Default:
            Lights.append(KDS.World.Lighting.Light(self.lightPos, KDS.World.Lighting.Shapes.circle_hard.getColor(10, 120 if self.state == HotelDoor.DoorState.Accept else 0, 1.0, 1.0), True))

            self.resetStateTimer += 1
            if self.resetStateTimer > 120:
                self.resetStateTimer = 0
                if self.state == HotelDoor.DoorState.Accept:
                    self.teleport()
                self.state = HotelDoor.DoorState.Default

        return self.texture

class HotelDoorMirrored(HotelDoor):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.lightPos = (self.rect.x + 9, self.rect.y + 25)

class HotelGuardDoor(DoorTeleport):
    tip_render: pygame.Surface = tip_font.render(f"Knock [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    alt_tip_render: pygame.Surface = tip_font.render(f"Enter [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.currentOpenTicks: int = 0
        self.targetOpenTicks: int = 10 * 60
        self.open: bool = False
        self.waitOpenTicks: int = -1
        self.opentexture = exit_door_open
        self.playerInsideRoom: bool = False
        self.deathListenerTriggered: bool = False
        self.song: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Effects/jumputus.ogg")
        self.song.set_volume(0.0)
        self.song_muffled: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Effects/jumputus_lowpass.ogg")
        self.song_muffled.set_volume(0.15)
        e = KDS.NPC.DoorGuardNPC((self.rect.right, self.rect.top + 34))
        e.enabled = False
        self.entity = e
        global Entities
        Entities.append(e)

        self.messageOffset = (0, -50 - teleport_message_font.get_height() - 5)

    def lateInit(self):
        super().lateInit()
        KDS.Audio.PlaySound(self.song, loops=-1)
        KDS.Audio.PlaySound(self.song_muffled, loops=-1)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            self.renderMessage()

            messageSize = self.renderedMessage.get_size() if self.renderedMessage != None else (0, 0)
            normalMessagePos = (self.rect.centerx - messageSize[0] // 2 - scroll[0] + self.messageOffset[0], self.rect.centery - messageSize[1] // 2 - scroll[1] + self.messageOffset[1])
            if not self.open:
                screen.blit(HotelGuardDoor.tip_render, (self.rect.centerx - HotelGuardDoor.tip_render.get_width() // 2 - scroll[0], normalMessagePos[1] + messageSize[1] + 5))
            elif self.entity.health <= 0:
                screen.blit(HotelGuardDoor.alt_tip_render, (self.rect.centerx - HotelGuardDoor.alt_tip_render.get_width() // 2 - scroll[0], normalMessagePos[1] + messageSize[1] + 5))

            if KDS.Keys.functionKey.clicked and self.interactable:
                if not self.open:
                    KDS.Audio.PlayFromFile("Assets/Audio/Tiles/guard_door_knock.ogg")
                    if self.waitOpenTicks == -1:
                        # Knock mission progress
                        self.waitOpenTicks = 3 * 60
                    else:
                        self.waitOpenTicks -= 30
                elif self.entity.health <= 0:
                    self.teleport()

        if self.waitOpenTicks != -1:
            self.waitOpenTicks -= 1
            if self.waitOpenTicks <= 0:
                KDS.Audio.PlaySound(door_opening)
                self.waitOpenTicks = -1
                self.open = True
                self.entity.enabled = True
                KDS.Missions.Listeners.DoorGuardNPCEnable.Trigger()

        if self.playerInsideRoom:
            self.song.set_volume(1.0)
            self.song_muffled.set_volume(0.0)
        else:
            self.song.set_volume(0.0)
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 600 # Bigger value means volume gets smaller at a smaller rate
            muffled_volume = KDS.Math.Lerp(0.75, 0.15, lerp_multiplier)
            if self.open:
                muffled_volume *= 2
            self.song_muffled.set_volume(muffled_volume)

        if self.open:
            if self.entity.health > 0:
                self.currentOpenTicks += 1
                if self.currentOpenTicks > self.targetOpenTicks:
                    KDS.Audio.PlaySound(door_opening)
                    self.currentOpenTicks = 0
                    self.entity.enabled = False
                    self.open = False
                    KDS.Missions.Listeners.DoorGuardNPCDisable.Trigger()
            elif not self.deathListenerTriggered:
                KDS.Missions.Listeners.DoorGuardNPCDeath.Trigger()
                self.deathListenerTriggered = True

            return self.opentexture
        return self.texture

    def teleport(self):
        self.playerInsideRoom = True
        KDS.Missions.SetProgress("story_index_11_mission_door_blockage", "story_index_11_mission_task_goin", 1.0)
        return super().teleport()

    def onTeleport(self):
        self.playerInsideRoom = False

    def onDestroy(self):
        self.song.stop()
        self.song_muffled.stop()

class WoodDoorSideTeleport(WoodDoorTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0] + 27, position[1] - 34, 7, 68)
        self.teleportOffset = (-KDS.Math.CeilToInt(stand_size[0] / 2 + self.rect.width / 2), 0)

    def onTeleport(self):
        Player.direction = True

class NysseTeleport(BaseTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        assert self.texture != None, "Nysse teleport should have a texture!"
        self.rect = pygame.Rect(position[0], position[1] - self.texture.get_height() + 34, self.texture.get_width(), self.texture.get_height())
        self.blinker: bool = True
        self.headlights: bool = True
        self.blinkerIndex = 0
        self.blinkerRepeatRate = 180 # beats per minute
        self.blinkerLight: bool = False

    def lateInit(self) -> None:
        super().lateInit()
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        if self.headlights:
            Lights.append(KDS.World.Lighting.Light((self.rect.x + 23, self.rect.y + 71), KDS.World.Lighting.Shapes.circle_harder.get(50, 5000), True))
            Lights.append(KDS.World.Lighting.Light((self.rect.x + 99, self.rect.y + 71), KDS.World.Lighting.Shapes.circle_harder.get(50, 5000), True))
        if self.blinker:
            if self.blinkerIndex == 0:
                self.blinkerLight = not self.blinkerLight
            if self.blinkerLight:
                Lights.append(KDS.World.Lighting.Light((self.rect.x + 18, self.rect.y + 68), KDS.World.Lighting.Shapes.circle_hard.get(10, 2550), True))
            self.blinkerIndex += self.blinkerRepeatRate
            if self.blinkerIndex > 3600:
                self.blinkerIndex = 0
        if self.rect.colliderect(Player.rect):
            screen.blit(Nysse.tip, (self.rect.centerx - Nysse.tip.get_width() // 2 - scroll[0], self.rect.y - 5 - Nysse.tip.get_height() - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                self.teleport()
        return self.texture

class HologramTeleport(BaseTeleport):
    tip: pygame.Surface = tip_font.render(f"Teleport [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)
    sound = pygame.mixer.Sound("Assets/Audio/Tiles/platform_teleport_sound.ogg")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.teleportSound = HologramTeleport.sound

    def update(self) -> Optional[pygame.Surface]:
        shape: pygame.Surface = KDS.World.Lighting.Shapes.cone_narrow.getColor(102, 196.164, 0.7773, 0.8980)
        shape = pygame.transform.rotate(shape, 90)
        shape = shape.subsurface((0, 0, shape.get_width(), 68))
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.bottom - 34), shape, True))

        if self.rect.colliderect(Player.rect):
            screen.blit(HologramTeleport.tip, (self.rect.centerx - HologramTeleport.tip.get_width() // 2 - scroll[0], self.rect.y - 45 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                self.teleport()

        return self.texture

KDS.Build.Tile.specialTilesClasses = {
    15: Toilet,
    16: Trashcan,
    17: Tree,
    18: Ladder,
    19: Jukebox,
    21: Landmine,
    23: Door,
    22: Lamp,
    24: Door,
    25: Door,
    26: Door,
    43: DecorativeHead,
    47: Rock0,
    48: Rock0,
    52: Torch,
    53: GoryHead,
    54: LevelEnder,
    55: Candle,
    58: LampPoleLamp,
    59: Chair,
    66: SkullTile,
    71: WallLight,
    72: WallLight,
    73: LevelEnderDoor,
    74: RespawnAnchor,
    76: Spruce,
    77: AllahmasSpruce,
    78: Methtable,
    82: Ladder,
    84: FlickerTrigger,
    85: ImpaledBody,
    87: Barrier,
    93: GroundFire,
    94: LampChain,
    101: Tent,
    102: GlassPane,
    108: RoofPlanks,
    109: RoofPlanks,
    110: RoofPlanks,
    111: RoofPlanks,
    113: Patja,
    118: LevelEnderTransparent,
    123: Crackhead,
    126: DoorFront,
    128: AvarnCar,
    130: Nysse,
    131: Sound,
    132: DoorFrontMirrored,
    134: FluorescentTube,
    145: Kiuas,
    151: TileFire,
    155: Fucking,
    157: Shower,
    160: LevelEnderDoor,
    161: PistokoeDoor,
    164: HotelBed,
    168: CashRegister,
    169: TheftDetector
}
BaseTeleport.serialNumbers = {
    1: InvisibleTeleport,
    2: WoodDoorTeleport,
    3: WoodDoorTeleport,
    4: WoodDoorTeleport,
    5: LargeDoorTeleport,
    6: Elevator,
    7: HotelDoor,
    8: HotelDoorMirrored,
    9: WoodDoorSideTeleport,
    10: HotelGuardDoor,
    11: NysseTeleport,
    12: HologramTeleport
}

KDS.Logging.debug("Tile Loading Complete.")
#endregion
#region Items
KDS.Logging.debug("Loading Items...")
itemTip: pygame.Surface = tip_font.render(f"Nosta Esine [{KDS.Keys.functionKey.BindingDisplayName}]", True, KDS.Colors.White)

class BlueKey(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(key_pickup)
        Player.keys["blue"] = True

class Cell(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Plasmarifle, 30, 5, item_pickup)

class Coffeemug(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 6
        KDS.Audio.PlaySound(coffeemug_sound)

class Gasburner(KDS.Build.Item):
    burning = False
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.sound = False

    def use(self):
        if KDS.Keys.mainKey.pressed:
            Gasburner.burning = True
            if not self.sound:
                KDS.Audio.PlaySound(gasburner_fire, loops=-1)
                self.sound = True
            return gasburner_animation_object.update()
        else:
            gasburner_fire.stop()
            self.sound = False
            Gasburner.burning = False
            return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 12
        KDS.Audio.PlaySound(gasburner_clip)

class GreenKey(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(key_pickup)
        Player.keys["green"] = True

class iPuhelin(KDS.Build.Item):
    #pickup_sound = pygame.mixer.Sound("Assets/Audio/Legacy/apple_o_paskaa.ogg")
    realistic_texture = pygame.image.load("Assets/Textures/Items/iPuhelin_realistic.png").convert()
    realistic_texture.set_colorkey(KDS.Colors.White)
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.useCount = 0

    def use(self):
        if KDS.Keys.functionKey.clicked:
            self.useCount += 1
        if self.useCount > 7:
            self.useCount = 7
            self.texture = iPuhelin.realistic_texture
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score -= 6
        KDS.Audio.PlaySound(item_pickup)

class Knife(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(40, KDS.Math.INFINITY, knife_animation_object, None, allowHold=True)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 13 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 1, 1), holderData.direction, -1, Tiles, 5, maxDistance=40))
        return output

    def use(self) -> pygame.Surface:
        self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))
        if KDS.Keys.mainKey.pressed:
            return knife_animation_object.update()
        else:
            knife_animation_object.tick = 0
            return self.texture

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 5
        KDS.Audio.PlaySound(knife_pickup)

class LappiSytytyspalat(KDS.Build.Item):
    sytytys_tip: pygame.Surface = tip_font.render(f"Ignite Tile [Hold: LMB]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.requireTaskWithName: Optional[str] = None

    def use(self):
        global Tiles
        allowSytytys: bool
        if self.requireTaskWithName != None:
            tmp_miss = KDS.Missions.Missions.GetMission(KDS.Missions.Active_Mission)
            if tmp_miss != None:
                allowSytytys = tmp_miss.GetTask(self.requireTaskWithName) != None
            else:
                allowSytytys = False
        else:
            allowSytytys = True
        if allowSytytys:
            tmpdirctn = KDS.Convert.ToMultiplier(Player.direction)
            pos = (int(Player.rect.centerx / 34) + tmpdirctn + tmpdirctn, int(Player.rect.centery / 34))
            if TileFire.isUnitFreeOfFire(pos)[0]:
                screen.blit(LappiSytytyspalat.sytytys_tip, (pos[0] * 34 + 17 - scroll[0] - LappiSytytyspalat.sytytys_tip.get_width() // 2, pos[1] * 34 - scroll[1]))
            if KDS.Keys.mainKey.held:
                TileFire.createInstanceAtPosition(pos)
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 14
        KDS.Audio.PlaySound(lappi_sytytyspalat_sound)

class Medkit(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(item_pickup)
        Player.health = min(Player.health + 25, 100)

class Pistol(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(30, 8, pistol_f_texture, pistol_shot)

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 18
        KDS.Audio.PlaySound(weapon_pickup)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 30 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 25))
        return output

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

class PistolMag(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Pistol, 7, 7, item_pickup)

class rk62(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(4, 30, rk62_f_texture, rk62_shot, True, True)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 50 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 6))
        return output


    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 29
        KDS.Audio.PlaySound(weapon_pickup)

class Shotgun(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(50, 8, shotgun_f, shotgun_shot)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            for x in range(10):
                Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 60 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 6, maxDistance=1400, slope=3 - x / 1.5))
        return output

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 23
        KDS.Audio.PlaySound(weapon_pickup)

class rk62Mag(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(rk62, 30, 8, item_pickup)

class ShotgunShells(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Shotgun, 4, 5, item_pickup)

class Plasmarifle(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(3, 36, plasmarifle_animation, plasmarifle_f_sound, allowHold=True)

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            asset_offset = 70 * -KDS.Convert.ToMultiplier(holderData.direction)
            Lights.append(KDS.World.Lighting.Light((int(holderData.rect.centerx - asset_offset / 1.4), holderData.rect.centery - 30), KDS.World.Lighting.Shapes.circle.get(40, 40000)))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx - asset_offset, holderData.rect.y + 13, 2, 2), holderData.direction, 27, Tiles, 5, plasma_ammo, 2000, random.randint(-1, 1) / 27))
        return output

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 35
        KDS.Audio.PlaySound(weapon_pickup)

class Soulsphere(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Scores.score += 20
        Player.health += 100
        KDS.Audio.PlaySound(item_pickup)

class RedKey(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(key_pickup)
        Player.keys["red"] = True

class SSBonuscard(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 30
        KDS.Audio.PlaySound(ss_sound)

class Turboneedle(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

    def pickup(self) -> None:
        KDS.Audio.PlaySound(item_pickup)
        Player.stamina = 250

class Ppsh41(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(2, 72, ppsh41_f_texture, smg_shot, True, True)

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 60 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 3, slope=random.uniform(-0.5, 0.5)))
        return output

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 15

class Awm(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(130, 5, awm_f_texture, awm_shot)

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(holderData.rect.centerx + 90 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, random.randint(75, 150), slope=0))
        return output

    def pickup(self) -> None:
        super().pickup()
        KDS.Scores.score += 25

class AwmMag(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Awm, 5, 10, item_pickup)

class EmptyFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 1
        KDS.Audio.PlaySound(coffeemug_sound)

class MethFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.mainKey.pressed:
            KDS.Scores.score += 1
            Player.health += random.choice([random.randint(10, 30), random.randint(-30, 30)])
            Player.inventory.pickupItem(KDS.Build.Item.serialNumbers[26]((0, 0), 26), force=True)
            KDS.Audio.PlaySound(glug_sound)
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 10
        KDS.Audio.PlaySound(coffeemug_sound)

class BloodFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
    def use(self):
        if KDS.Keys.mainKey.pressed:
            KDS.Scores.score += 1
            Player.health += random.randint(0, 10)
            Player.inventory.pickupItem(KDS.Build.Item.serialNumbers[26]((0, 0), 26), force=True)
            KDS.Audio.PlaySound(glug_sound)
        return self.texture

    def pickup(self) -> None:
        KDS.Audio.PlaySound(coffeemug_sound)
        KDS.Scores.score += 7

class Grenade(KDS.Build.Item):
    Slope = 0.7
    Force = 9

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.altUp.pressed:
            Grenade.Slope += 0.03
        elif KDS.Keys.altDown.pressed:
            Grenade.Slope -= 0.03

        pygame.draw.line(screen, (255, 10, 10), (Player.rect.centerx - scroll[0], Player.rect.y + 10 - scroll[1]), (Player.rect.centerx + (Grenade.Force + 15) * KDS.Convert.ToMultiplier(Player.direction) - scroll[0], Player.rect.y + 10 + Grenade.Slope * (Grenade.Force + 15) * -1 - scroll[1]) )
        if KDS.Keys.mainKey.pressed:
            KDS.Audio.PlaySound(grenade_throw)
            Player.inventory.dropItem(forceDrop=True)
            BallisticObjects.append(KDS.World.BallisticProjectile(pygame.Rect(Player.rect.centerx, Player.rect.centery - 25, 10, 10), Grenade.Slope, Grenade.Force, Player.direction, gravitational_factor=0.4, flight_time=140, texture = i_textures[29]))
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score += 7

class FireExtinguisher(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

class LevelEnderItem(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.mainKey.pressed:
            KDS.Missions.Listeners.LevelEnder.Trigger()

        return self.texture

    def pickup(self) -> None:
        KDS.Audio.PlaySound(weapon_pickup)

class Ppsh41Mag(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Ppsh41, 69, 5, item_pickup)

class Lantern(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("lantern_burning", 2, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

    def use(self):
        Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hardest.get(random.randint(180, 220), 5000), True))
        return self.animation.update()

    def pickup(self) -> None:
        KDS.Audio.PlaySound(lantern_pickup)

class Chainsaw(KDS.Build.Item):
    pickup_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_start.ogg")
    freespin_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_freespin.ogg")
    throttle_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_throttle.ogg")
    soundCounter = 70
    soundCounter1 = 122
    ammunition = -1.0
    defaultAmmunition = 100.0
    a_a = False
    Ianimation = KDS.Animator.Animation("chainsaw_animation", 2, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.pickupFinished = False
        self.pickupCounter = 0

    def use(self):
        if self.pickupFinished and (Chainsaw.ammunition > 0 or KDS.Build.Item.infiniteAmmo):
            if KDS.Keys.mainKey.pressed:
                Chainsaw.ammunition = max(0, Chainsaw.ammunition - 0.05)
                Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 18 * KDS.Convert.ToMultiplier(Player.direction), Player.rect.y + 28, 1, 1), Player.direction, -1, Tiles, damage=1, maxDistance=80))
                if Chainsaw.soundCounter > 70:
                    Chainsaw.freespin_sound.stop()
                    KDS.Audio.PlaySound(Chainsaw.throttle_sound)
                    Chainsaw.soundCounter = 0
                Chainsaw.a_a = True
            else:
                Chainsaw.a_a = False
                if Chainsaw.soundCounter1 > 103:
                    Chainsaw.soundCounter1 = 0
                    Chainsaw.throttle_sound.stop()
                    Chainsaw.ammunition = round(max(0, Chainsaw.ammunition - 0.1), 1)
                    KDS.Audio.PlaySound(Chainsaw.freespin_sound)
        else:
            self.pickupCounter += 1
            if self.pickupCounter > 180:
                self.pickupFinished = True
        Chainsaw.soundCounter += 1
        Chainsaw.soundCounter1 += 1
        if Chainsaw.a_a:
            return Chainsaw.Ianimation.update()
        return self.texture

    def pickup(self) -> None:
        KDS.Audio.PlaySound(Chainsaw.pickup_sound)
        KDS.Missions.Listeners.AnyWeaponPickup.Trigger()

class GasCanister(KDS.Build.Item):
    pickup_sound = pygame.mixer.Sound("assets/Audio/Items/gascanister_shake.ogg")
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(GasCanister.pickup_sound)
        Chainsaw.ammunition = min(100, Chainsaw.ammunition + 50)

class WalkieTalkie(KDS.Build.Item):
    storyTrigger: bool = False
    storyRunning: bool = False

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.allowDrop: bool = True
        self.playTime = -1
        self.clip = None
        self.clipVolume = 1.0
        self.clipSound = None
        self.audioChannel = None

    def lateInit(self):
        if self.clip != None:
            self.clipSound = pygame.mixer.Sound(self.clip)
        if self.clipVolume != 1.0 and self.clipSound != None:
            self.clipSound.set_volume(self.clipVolume)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(weapon_pickup)
        if self.clipSound != None:
            self.audioChannel = KDS.Audio.PlaySound(self.clipSound)
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            WalkieTalkie.storyTrigger = True

    def drop(self):
        return self.allowDrop

class BucketOfBlood(KDS.Build.Item):
    pickup_sound = pygame.mixer.Sound("Assets/Audio/Items/bucket_of_blood_pickup.ogg")
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        KDS.Audio.PlaySound(BucketOfBlood.pickup_sound)

class HotelKeycard(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

class SurveyAnswers(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

class Euro(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

KDS.Build.Item.serialNumbers = {
    1: BlueKey,
    2: Cell,
    3: Coffeemug,
    4: Gasburner,
    5: GreenKey,
    6: iPuhelin,
    7: Knife,
    8: LappiSytytyspalat,
    9: Medkit,
    10: Pistol,
    11: PistolMag,
    12: Plasmarifle,
    13: RedKey,
    14: rk62Mag,
    15: rk62,
    16: Shotgun,
    17: ShotgunShells,
    18: Soulsphere,
    19: SSBonuscard,
    20: Turboneedle,
    21: Ppsh41,
    # 22: "", # 55 S 55???
    # 23: "", # 55 S 55???
    24: Awm,
    25: AwmMag,
    26: EmptyFlask,
    27: MethFlask,
    28: BloodFlask,
    29: Grenade,
    30: FireExtinguisher,
    31: LevelEnderItem,
    32: Ppsh41Mag,
    33: Lantern,
    34: Chainsaw,
    35: GasCanister,
    36: WalkieTalkie,
    37: BucketOfBlood,
    38: HotelKeycard,
    39: SurveyAnswers,
    40: Euro
}
KDS.Logging.debug("Item Loading Complete.")
#endregion
#region Enemies
class Enemy:
    serialNumbers: Dict[int, Type[KDS.AI.HostileEnemy]] = {
        1: KDS.AI.Imp,
        2: KDS.AI.SergeantZombie,
        3: KDS.AI.DrugDealer,
        4: KDS.AI.TurboShotgunner,
        5: KDS.AI.MafiaMan,
        6: KDS.AI.MethMaker,
        7: KDS.AI.CaveMonster,
        8: KDS.AI.Mummy,
        9: KDS.AI.SecurityGuard,
        10: KDS.AI.Bulldog,
        11: KDS.AI.Zombie
    }

    death_count = 0
    total = 0

    @staticmethod
    def _addDeath():
        Enemy.death_count += 1

    @staticmethod
    def _internalEnemyHandler(enemy: KDS.AI.HostileEnemy):
        global Items
        projectiles, itms = enemy.update(screen, scroll, Tiles, Player.rect)
        if enemy.health > 0 and not KDS.Math.IsPositiveInfinity(enemy.health):
            healthTxt = score_font.render(str(enemy.health), True, KDS.Colors.AviatorRed)
            screen.blit(healthTxt, (enemy.rect.centerx - healthTxt.get_width() // 2 - scroll[0], enemy.rect.top - 20 - scroll[1]))
        for r in projectiles:
            Projectiles.append(r)
        for serialNumber in itms:
            tempItem = KDS.Build.Item.serialNumbers[serialNumber](enemy.rect.center, serialNumber)
            tempItem.physics = True
            Items.append(tempItem)
KDS.Missions.Listeners.EnemyDeath.OnTrigger += Enemy._addDeath
#endregion
#region Entity
class Entity:
    serialNumbers: Dict[int, Type[Union[KDS.Teachers.Teacher, KDS.NPC.NPC]]] = {}

    agro_count = 0
    death_count = 0
    total = 0

    @staticmethod
    def _addDeath():
        Enemy.death_count += 1

    @staticmethod
    def _addAgro():
        Entity.agro_count += 1

    @staticmethod
    def _internalEntityHandler(entity: Union[KDS.Teachers.Teacher, KDS.NPC.NPC]):
        global Items
        projectiles, itms = entity.update(screen, scroll, Tiles, Items, Player)
        if ((isinstance(entity, KDS.Teachers.Teacher) and KDS.Teachers.TeacherState.Combat in entity.state) or (isinstance(entity, KDS.NPC.NPC) and entity.panicked)) and entity.health > 0 and not KDS.Math.IsPositiveInfinity(entity.health):
            healthTxt = score_font.render(str(entity.health), True, KDS.Colors.AviatorRed)
            screen.blit(healthTxt, (entity.rect.centerx - healthTxt.get_width() // 2 - scroll[0], entity.rect.top - 20 - scroll[1]))
        for r in projectiles:
            Projectiles.append(r)
        for serialNumber in itms:
            tempItem = KDS.Build.Item.serialNumbers[serialNumber](entity.rect.center, serialNumber)
            tempItem.physics = True
            Items.append(tempItem)

    @staticmethod
    def update(Entity_List: Sequence[Union[KDS.Teachers.Teacher, KDS.NPC.NPC, KDS.AI.HostileEnemy]]):
        for entity in Entity_List:
            if not entity.enabled:
                continue
            if KDS.Math.getDistance(Player.rect.center, entity.rect.center) < 1200:
                if isinstance(entity, KDS.AI.HostileEnemy):
                    Enemy._internalEnemyHandler(entity)
                else:
                    Entity._internalEntityHandler(entity)

Entity.serialNumbers = {
    1: KDS.Teachers.LaaTo,
    2: KDS.Teachers.KuuMa,
    3: KDS.Teachers.Test,
    309: KDS.NPC.Room309NPC,
    999: KDS.NPC.StudentNPC
}
KDS.Missions.Listeners.TeacherAgro.OnTrigger += Entity._addAgro
KDS.Missions.Listeners.TeacherDeath.OnTrigger += Entity._addDeath
#endregion
#region Player
KDS.Logging.debug("Loading Player...")
class PlayerClass:
    def __init__(self) -> None:
        self.inventory = KDS.Inventory.Inventory(5)
        self.animations: KDS.Animator.MultiAnimation = KDS.Animator.MultiAnimation(
            idle = KDS.Animator.Animation("idle", 2, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            walk = KDS.Animator.Animation("walk", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            run = KDS.Animator.Animation("walk", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            idle_short = KDS.Animator.Animation("idle_short", 2, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            walk_short = KDS.Animator.Animation("walk_short", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            death = KDS.Animator.Animation("death", 6, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop, animation_dir="Player")
        )
        self.deathSound: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Effects/player_death.ogg")
        self.mover = KDS.World.EntityMover(w_sounds=path_sounds)

        self.reset()

    def reset(self, clear_inventory: bool = True, clear_keys: bool = True):
        self.rect: pygame.Rect = pygame.Rect(100, 100, stand_size[0], stand_size[1])
        self._health: float = 100.0
        self.stamina: float = 100.0
        if clear_inventory:
            self.inventory = KDS.Inventory.Inventory(5)
        if clear_keys:
            self.keys: Dict[str, bool] = { "red": False, "green": False, "blue": False }
        self.farting: bool = False
        self.fart_counter: int = 0
        self.light: bool = False
        self.infiniteHealth: bool = False
        self.infiniteStamina: bool = False
        self.fly: bool = False
        self.dead: bool = False
        self.deathAnimFinished: bool = False
        self.deathWait: int = 0
        self.direction: bool = False
        self.walking: bool = False
        self.air_timer: int = 0
        self.movement: List[float] = [0, 0]
        self.walk_sound_delay: float = 9999
        self.vertical_momentum: float = 0
        self.onLadder: bool = False
        self.disableSprint: bool = False
        self.wasOnLadder: bool = False
        self.crouching: bool = False
        self.running: bool = False
        self.visible: bool = True
        self.lockMovement: bool = False
        self.animations.reset()
        self.deathSound.stop()

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float):
        if value < self._health and value > 0 and not KDS.Math.IsPositiveInfinity(self._health):
            KDS.Audio.PlaySound(hurt_sound)
        self._health = max(value, 0)

    def update(self):
        if self.infiniteHealth:
            self.health = KDS.Math.INFINITY
        elif KDS.Math.IsInfinity(self.health):
            self._health = 100.0 # Skip hurt sound using _health instead of health
        if self.infiniteStamina:
            self.stamina = KDS.Math.INFINITY
        elif KDS.Math.IsInfinity(self.stamina):
            self.stamina = 100.0

        #region Movement
        #region Functions
        def crouch(state: bool):
            if state:
                if not self.crouching:
                    self.rect = pygame.Rect(self.rect.x, self.rect.y + (stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
                    self.crouching = True
            elif self.crouching:
                # If more than zero collisions; do not release crouch
                if len(KDS.World.collision_test(pygame.Rect(Player.rect.x, Player.rect.y - crouch_size[1], Player.rect.width, Player.rect.height), Tiles)) > 0:
                    return
                self.rect = pygame.Rect(self.rect.x, self.rect.y + (crouch_size[1] - stand_size[1]), stand_size[0], stand_size[1])
                self.crouching = False

        def jump(ladderOverride: bool = False):
            if KDS.Keys.moveUp.pressed and not KDS.Keys.moveDown.pressed:
                if ladderOverride or (self.air_timer < 6 and KDS.Keys.moveUp.onDown and not self.onLadder):
                    self.vertical_momentum = -10
        #endregion
        #region Normal
        if self.health > 0 and not self.fly:
            self.movement = [0, 0]
            jump()
            _fall_speed = fall_speed
            if self.vertical_momentum > 0 or not KDS.Keys.moveUp.pressed or KDS.Keys.moveDown.pressed:
                _fall_speed *= fall_multiplier

            if KDS.Keys.moveRight.pressed:
                if not self.crouching: self.movement[0] += 4
                else: self.movement[0] += 2
                if KDS.Keys.moveRun.pressed and self.stamina > 0 and not self.crouching and not self.disableSprint:
                    self.movement[0] += 4
                elif self.stamina <= 0: KDS.Keys.moveRun.SetState(False)

            if KDS.Keys.moveLeft.pressed:
                if not self.crouching: self.movement[0] -= 4
                else: self.movement[0] -= 2
                if KDS.Keys.moveRun.pressed and self.stamina > 0 and not self.crouching and not self.disableSprint:
                    self.movement[0] -= 4
                elif self.stamina <= 0: KDS.Keys.moveRun.SetState(False)

            self.running = abs(self.movement[0]) > 4

            if self.running: self.stamina -= 0.75
            elif self.stamina < 100.0: self.stamina += 0.25

            if not self.movement[0] or self.air_timer > 1:
                self.walk_sound_delay = KDS.Math.MAXVALUE
            self.walk_sound_delay += abs(self.movement[0])
            playWalkSound = (self.walk_sound_delay > 60) if play_walk_sound else False
            if playWalkSound: self.walk_sound_delay = 0

            if self.onLadder:
                self.wasOnLadder = True
                self.vertical_momentum = 0
                if KDS.Keys.moveUp.pressed or KDS.Keys.moveDown.pressed:
                    if Ladder.ct > 20:
                        Ladder.ct = 0
                    if Ladder.ct == 0: # Separate if to make the sound play immediately.
                        KDS.Audio.PlaySound(random.choice(Ladder.sounds))
                    Ladder.ct += 1

                    if KDS.Keys.moveUp.pressed:
                        self.vertical_momentum += -1
                    else:
                        self.vertical_momentum += 1
            elif self.wasOnLadder:
                self.wasOnLadder = False
                jump(True)

            self.movement[1] += self.vertical_momentum
            self.vertical_momentum = min(self.vertical_momentum + _fall_speed, fall_max_velocity)

            if KDS.Keys.moveDown.pressed and not self.onLadder:
                crouch(True)
            else:
                crouch(False)

            collisions = self.mover.move(self.rect, self.movement if not self.lockMovement else (0.0, 0.0), Tiles, playWalkSound=playWalkSound)

            if collisions.bottom:
                self.air_timer = 0
                self.vertical_momentum = 0
            else:
                if collisions.top:
                    self.vertical_momentum = 0
                self.air_timer += 1

            if self.movement[0] != 0:
                self.direction = self.movement[0] < 0
                self.walking = True
                KDS.Missions.Listeners.Movement.Trigger()
            else:
                self.walking = False

            if self.walking:
                if not self.running:
                    if not self.crouching:
                        self.animations.trigger("walk")
                    else:
                        self.animations.trigger("walk_short")
                else:
                    self.animations.trigger("run")
            else:
                if not self.crouching:
                    self.animations.trigger("idle")
                else:
                    self.animations.trigger("idle_short")

            self.onLadder = False
        #endregion
        #region Flying
        elif self.fly:
            self.movement = [0, 0]
            if KDS.Keys.moveUp.pressed:
                self.movement[1] -= 3
            if KDS.Keys.moveDown.pressed:
                self.movement[1] += 3
            if KDS.Keys.moveLeft.pressed:
                self.movement[0] -= 3
            if KDS.Keys.moveRight.pressed:
                self.movement[0] += 3
            if pygame.key.get_pressed()[K_LSHIFT]:
                self.movement[0] *= 5
                self.movement[1] *= 5
            if self.movement[0] > 0:
                self.direction = False
            elif self.movement[0] < 0:
                self.direction = True
            self.rect.y += round(self.movement[1])
            self.rect.x += round(self.movement[0])
        #endregion
        #endregion
        #region Dead
        else:
            crouch(False)
            self.animations.trigger("death")

            if self.dead and self.animations.active.tick >= self.animations.active.ticks:
                self.dead = False
                self.deathAnimFinished = True

            if not self.deathAnimFinished:
                self.dead = True
                KDS.Audio.Music.Stop()
                KDS.Audio.PlaySound(self.deathSound)
                self.deathSound.set_volume(0.5)
                self.deathAnimFinished = True
            else:
                self.deathWait += 1
        #endregion

Player = PlayerClass()
KDS.Logging.debug("Player Loading Complete.")
#endregion
#region Console
KDS.Logging.debug("Loading Console...")
def console(oldSurf: pygame.Surface):
    global level_finished, go_to_console, Player, Enemies
    go_to_console = False

    itemDict: Dict[str, Union[str, Dict[str, str]]] = {}
    for itemName, _data in itemData.items():
        if _data["supportsInventory"] != True:
            continue
        modName = itemName.replace(" ", "_").lower().replace("(", "").replace(")", "")
        itemDict[modName.encode("ascii", "ignore").decode("ascii")] = f"""{_data["serialNumber"]:03d}"""
    keyDict = {}
    for key in Player.keys:
        keyDict[key] = "break"
    itemDict["key"] = keyDict

    trueFalseTree = {"true": "break", "false": "break"}

    commandTree = {
        "give": itemDict,
        "remove": {
            "item": "break",
            "key": "break"
        },
        "kill": "break",
        "stop": "break",
        "killme": "break",
        "killall": "break",
        "terms": trueFalseTree,
        "woof": trueFalseTree,
        "infinite": {
            "health": trueFalseTree,
            "ammo": trueFalseTree,
            "damage": trueFalseTree,
            "stamina": trueFalseTree
        },
        "finish": {
            "missions": "break",
            "active_mission": "break"
            },
        "teleport": {
         "~": { "~": "break" },
        },
        "summon": {
            "imp": "break",
            "sergeantzombie": "break",
            "drugdealer": "break",
            "turboshotgunner": "break",
            "methmaker": "break",
            "cavemonster": "break"
        },
        "fly": trueFalseTree,
        "godmode": trueFalseTree
    }

    consoleRunning = True

    blurred_background = KDS.Convert.ToBlur(pygame.transform.scale(oldSurf.copy(), display_size), 6)

    while consoleRunning:
        command_list: list = KDS.Console.Start(prompt="Enter Command:", allowEscape=True, checkType=KDS.Console.CheckTypes.Commands(), background=blurred_background, commands=commandTree, autoFormat=True, enableOld=True, showFeed=True)
        if command_list == None:
            consoleRunning = False
            break
        try:
            if command_list[0] == "give":
                if command_list[1] != "key":
                    if command_list[1] in itemDict:
                        consoleItemSerial = itemDict[command_list[1]]
                        if not isinstance(consoleItemSerial, str):
                            KDS.Logging.AutoError(f"Unexpected data type. Expected: {str.__name__}, Got: {type(consoleItemSerial)}")
                            return
                        consoleItemSerialInt = int(consoleItemSerial)
                        Player.inventory.pickupItem(KDS.Build.Item.serialNumbers[consoleItemSerialInt]((0, 0), consoleItemSerialInt), force=True)
                        KDS.Console.Feed.append(f"Item was given: [{consoleItemSerial}: {command_list[1]}]")
                    else: KDS.Console.Feed.append(f"Item not found.")
                else:
                    if len(command_list) > 2:
                        if command_list[2] in Player.keys:
                            Player.keys[command_list[2]] = True
                            KDS.Console.Feed.append(f"Item was given: {command_list[1]} {command_list[2]}")
                        else: KDS.Console.Feed.append(f"Item [{command_list[1]} {command_list[2]}] does not exist!")
                    else: KDS.Console.Feed.append("No key specified!")
            elif command_list[0] == "remove":
                if command_list[1] == "item":
                    Player.inventory.dropItem(forceDrop=True)
                elif command_list[1] == "key":
                    if command_list[2] in Player.keys:
                        if Player.keys[command_list[2]] == True:
                            Player.keys[command_list[2]] = False
                            KDS.Console.Feed.append(f"Item was removed: {command_list[1]} {command_list[2]}")
                        else: KDS.Console.Feed.append("You don't have that item!")
                    else: KDS.Console.Feed.append(f"Item [{command_list[1]} {command_list[2]}] does not exist!")
                else: KDS.Console.Feed.append("Not a valid remove command.")
            elif command_list[0] == "kill" or command_list[0] == "stop":
                KDS.Console.Feed.append("Stopping Game...")
                KDS.Logging.info("Stop command issued through console.", True)
                KDS_Quit()
            elif command_list[0] == "killme":
                KDS.Console.Feed.append("Player Killed.")
                KDS.Logging.info("Player kill command issued through console.", True)
                Player.health = 0
            elif command_list[0] == "killall":
                KDS.Console.Feed.append("All entities killed.")
                KDS.Logging.info("Entity kill command issued through console.", True)
                for entity in Entities:
                    entity.health = 0
            elif command_list[0] == "terms":
                setTerms = False
                if len(command_list) == 2:
                    setTerms = KDS.Convert.String.ToBool(command_list[1], None)
                    if setTerms != None:
                        KDS.ConfigManager.SetSetting("Data/Terms/accepted", setTerms)
                        KDS.Console.Feed.append(f"Terms status set to: {setTerms}")
                    else:
                        KDS.Console.Feed.append("Please provide a proper state for terms & conditions")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for terms & conditions")
            elif command_list[0] == "infinite":
                if len(command_list) == 3:
                    if command_list[1] == "health":
                        h_state = KDS.Convert.String.ToBool(command_list[2], None)
                        if h_state != None:
                            Player.infiniteHealth = h_state
                            KDS.Console.Feed.append(f"infinite health state has been set to: {Player.infiniteHealth}")
                        else:
                            KDS.Console.Feed.append("Please provide a proper state for infinite health.")
                    elif command_list[1] == "ammo":
                        a_state = KDS.Convert.String.ToBool(command_list[2], None)
                        if a_state != None:
                            KDS.Build.Item.infiniteAmmo = a_state
                            KDS.Console.Feed.append(f"infinite ammo state has been set to: {KDS.Build.Item.infiniteAmmo}")
                        else:
                            KDS.Console.Feed.append("Please provide a proper state for infinite ammo.")
                    elif command_list[1] == "damage":
                        a_state = KDS.Convert.String.ToBool(command_list[2], None)
                        if a_state != None:
                            KDS.World.Bullet.GodMode = a_state
                            KDS.Console.Feed.append(f"infinite damage state has been set to: {KDS.World.Bullet.GodMode}")
                        else:
                            KDS.Console.Feed.append("Please provide a proper state for infinite damage.")
                    elif command_list[1] == "stamina":
                        h_state = KDS.Convert.String.ToBool(command_list[2], None)
                        if h_state != None:
                            Player.infiniteStamina = h_state
                            KDS.Console.Feed.append(f"infinite stamina state has been set to: {Player.infiniteStamina}")
                        else:
                            KDS.Console.Feed.append("Please provide a proper state for infinite health.")
                    else:
                        KDS.Console.Feed.append("Not a valid infinite command.")
                else:
                    KDS.Console.Feed.append("Not a valid infinite command.")
            elif command_list[0] == "finish":
                if len(command_list) > 1 and command_list[1] == "missions":
                    KDS.Console.Feed.append("Missions Finished.")
                    KDS.Logging.info("Mission finish issued through console.", True)
                    KDS.Missions.Finish()
                elif len(command_list) > 1 and command_list[1] == "active_mission":
                    tmpFinishMission = KDS.Missions.Missions.GetMission(KDS.Missions.Active_Mission)
                    if tmpFinishMission != None:
                        KDS.Console.Feed.append(f"Active mission \"{tmpFinishMission.text}\" finished.")
                        KDS.Logging.info("Current mission finish issued through console.", True)
                        for tmpFinishMissionTask in tmpFinishMission.GetTaskList():
                            tmpFinishMissionTask.Progress(100)
                    else:
                        KDS.Console.Feed.append("Could not finish active mission. No mission found.")
                elif len(command_list) == 1:
                    KDS.Console.Feed.append("Level Finished.")
                    KDS.Logging.info("Level finish issued through console.", True)
                    level_finished = True
                else:
                    KDS.Console.Feed.append("Please provide a proper finish type.")
            elif command_list[0] == "teleport":
                if len(command_list) == 3:
                    if command_list[1][0] == "~":
                        if len(command_list[1]) < 2: command_list[1] += "0"
                        xt = command_list[1][1:]
                        try: xt = Player.rect.x + int(xt)
                        except ValueError: KDS.Console.Feed.append("X-coordinate invalid.")
                    else:
                        xt = command_list[1]
                        try: xt = int(xt)
                        except ValueError: KDS.Console.Feed.append("X-coordinate invalid.")

                    if command_list[2][0] == "~":
                        if len(command_list[2]) < 2: command_list[2] += "0"
                        yt = command_list[2][1:]
                        try: yt = Player.rect.y + int(yt)
                        except ValueError:
                            if not isinstance(xt, int): KDS.Console.Feed[-1] = "X and Y-coordinates invalid."
                            else: KDS.Console.Feed.append("Y-coordinate invalid.")
                    else:
                        yt = command_list[2]
                        try: yt = int(yt)
                        except ValueError:
                            if not isinstance(xt, int): KDS.Console.Feed[-1] = "X and Y-coordinates invalid."
                            else: KDS.Console.Feed.append("Y-coordinate invalid.")

                    if isinstance(xt, int) and isinstance(yt, int):
                        Player.rect.topleft = (xt, yt)
                        KDS.Console.Feed.append(f"Teleported player to {xt}, {yt}")
                else: KDS.Console.Feed.append("Please provide proper coordinates for teleporting.")
            elif command_list[0] == "summon":
                if len(command_list) > 1:
                    summonEntity: Dict[str, Type[KDS.AI.HostileEnemy]] = {
                        "imp": KDS.AI.Imp,
                        "sergeantzombie": KDS.AI.SergeantZombie,
                        "drugdealer": KDS.AI.DrugDealer,
                        "turboshotgunner": KDS.AI.TurboShotgunner,
                        "methmaker": KDS.AI.MethMaker,
                        "cavemonster": KDS.AI.CaveMonster
                    }
                    try:
                        ent = summonEntity[command_list[1]]
                        Entities.append(ent(Player.rect.topright))
                        KDS.Console.Feed.append(f"Summoned Entity: \"{ent.__name__}\".")
                    except KeyError:
                        KDS.Console.Feed.append(f"Entity name {command_list[1]} is not valid.")
            elif command_list[0] == "fly":
                if len(command_list) == 2:
                    flyState = KDS.Convert.String.ToBool(command_list[1], None)
                    if flyState != None:
                        Player.fly = flyState
                        KDS.Console.Feed.append(f"Fly state has been set to: {Player.fly}")
                    else:
                        KDS.Console.Feed.append("Please provide a proper state for fly")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for fly")
            elif command_list[0] == "godmode":
                if len(command_list) == 2:
                    godmodeState = KDS.Convert.String.ToBool(command_list[1], None)
                    if godmodeState != None:
                        KDS.World.Bullet.GodMode = godmodeState
                        Player.infiniteHealth = godmodeState
                        Player.infiniteStamina = godmodeState
                        KDS.Build.Item.infiniteAmmo = godmodeState
                        KDS.Console.Feed.append(f"Godmode state has been set to: {KDS.World.Bullet.GodMode}")
                    else:
                        KDS.Console.Feed.append("Please provide a proper state for godmode")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for godmode")
            elif command_list[0] == "help":
                KDS.Console.Feed.append("""
        Console Help:
            - give => Adds the specified item to your inventory.
            - remove => Removes the specified item from your inventory.
            - kill | stop => Stops the game.
            - killme => Kills the player.
            - killall => Kills all entities.
            - terms => Sets Terms and Conditions accepted to the specified value.
            - woof => Sets all bulldogs anger to the specified value.
            - finish => Forces level finish, finishes missions or finishes active mission.
            - infinite => Sets the specified infinite type to the specified value.
            - teleport => Teleports player either to static coordinates or relative coordinates.
            - summon => Summons enemy to the coordinates of player's rectangle's top left corner.
            - fly => Sets fly mode to the specified value.
            - godmode => Gives the player some buffs like infinite health
            - help => Shows the list of commands.
        """)
            else:
                KDS.Console.Feed.append("Invalid Command.")
        except Exception as e:
            KDS.Logging.AutoError(f"An exception occured while running console. Exception below:\n{traceback.format_exc()}")
            KDS.Console.Feed.append("An exception occured!")
#endregion
#region Terms and Conditions
def agr():
    global tcagr_running
    tcagr_running = True

    global main_running
    c = False

    def tcagr_agree_function():
        global tcagr_running, main_menu_running
        KDS.Logging.info("Terms and Conditions have been accepted.")
        KDS.Logging.info("You said you will not get offended... Dick!")
        updatedValue = KDS.ConfigManager.SetSetting("Data/Terms/accepted", True)
        KDS.Logging.debug(f"Terms Agreed. Updated Value: {updatedValue}", False)
        tcagr_running = False


    agree_button = KDS.UI.Button(pygame.Rect(465, 500, 270, 135), tcagr_agree_function, KDS.UI.ButtonFont.render(
        "I Agree", True, KDS.Colors.White))

    while tcagr_running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if defaultEventHandler(event, QUIT):
                continue
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == QUIT:
                KDS_Quit()
        display.blit(agr_background, (0, 0))
        agree_button.update(display, mouse_pos, c)
        pygame.display.flip()
        c = False
    return True
KDS.Logging.debug("Console Loading Complete.")
KDS.Logging.debug("Game Initialisation Complete.")
#endregion
#region Game Functions
def play_function(gamemode: KDS.Gamemode.Modes, reset_scroll: bool, show_loading: bool = True, auto_play_music: bool = True):
    KDS.Logging.debug("Loading Game...")
    global main_menu_running, current_map, true_scroll, selectedSave

    pygame.mouse.set_visible(False)
    KDS.Audio.Music.Stop()

    if show_loading:
        KDS.Loading.Circle.Start(display)

    level_index: int
    if gamemode == KDS.Gamemode.Modes.CustomCampaign:
        mapPath = os.path.join(PersistentPaths.CustomMaps, current_map_name)
        gamemode = KDS.Gamemode.Modes.Campaign
        level_index = int(current_map)
    elif gamemode == KDS.Gamemode.Modes.Story:
        assert KDS.ConfigManager.Save.Active != None, "Could not load story mode map! No save active."
        mapPath = os.path.join("Assets/Maps/Story", f"map{KDS.ConfigManager.Save.Active.Story.index:02d}")
        level_index = KDS.ConfigManager.Save.Active.Story.index
    else:
        mapPath = os.path.join("Assets/Maps/Campaign", f"map{current_map}")
        level_index = int(current_map)

    KDS.Gamemode.SetGamemode(gamemode, level_index)
    KDS.World.Lighting.Shapes.clear()

    global Player
    Player = PlayerClass()

    #region World Data
    global Items, Explosions, BallisticObjects, Projectiles, Entities, Zones
    Items.clear()
    Explosions.clear()
    BallisticObjects.clear()
    Projectiles.clear()
    Entities.clear()
    Zones.clear()
    #endregion
    #region Class Data
    KDS.NPC.NPC.InstanceList.clear()
    KDS.Teachers.Teacher.InstanceList.clear()
    KDS.World.Zone.StaffOnlyCollisions = 0
    RespawnAnchor.active = None
    BaseTeleport.teleportDatas = {}
    ScreenEffects.Clear()
    #endregion

    #region Ammo Resetting
    for c in KDS.Build.Item.serialNumbers.values():
        defaultAmmo = getattr(c, "defaultAmmunition", None)
        if defaultAmmo != None:
            setattr(c, "ammunition", defaultAmmo)
    #endregion

    LoadGameSettings()


    loadMapHandle = KDS.Jobs.Schedule(WorldData.LoadMap, mapPath)
    while not loadMapHandle.IsComplete:
        for event in pygame.event.get(): # No default event handler in loading screen
            if event.type == QUIT:
                KDS_Quit()
        pygame.time.wait(100)
    wdata = loadMapHandle.Complete()
    # Stupid idea
    # KDS.System.gc.collect() # Collecting here since player has already waited for long and this application uses a shit ton of RAM
    if not wdata:
        pygame.mouse.set_visible(True)
        return
    Player.rect.topleft, _ = wdata

    #region Set Game Data
    global level_finished
    level_finished = False
    #endregion

    main_menu_running = False
    KDS.Scores.ScoreCounter.Start()
    if reset_scroll:
        true_scroll = [float(Player.rect.x - SCROLL_OFFSET[0]), float(Player.rect.y - SCROLL_OFFSET[1])]
    pygame.event.clear()
    KDS.Keys.Reset()
    KDS.Logging.debug("Game Loaded.")
    if show_loading:
        KDS.Loading.Circle.Stop()
    #LoadMap will assign Loaded if it finds a song for the level. If not found LoadMap will call Unload to set Loaded as None.
    if auto_play_music and KDS.Audio.Music.Loaded != None:
        KDS.Audio.Music.Play()

def play_story(saveIndex: int, newSave: bool = True, show_loading: bool = True, oldSurf: Optional[pygame.Surface] = None):
    pygame.mouse.set_visible(False)

    map_names: Dict[int, str] = {}
    def load_map_names():
        nonlocal map_names
        map_names = {}
        try:
            with open("Assets/Maps/Story/names.dat", "r", encoding="utf-8") as file:
                tmp = file.read().split("\n")
                for t in tmp:
                    tmp_split = t.split(":")
                    for i in range(len(tmp_split)):
                        tmp_split[i] = tmp_split[i].strip()
                    if len(tmp_split) == 2:
                        map_names[int(tmp_split[0])] = tmp_split[1]
                    else:
                        KDS.Logging.AutoError(f"Map name \"{t}\" is broken!")
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")
    load_map_names()

    if newSave:
        KDS.ConfigManager.Save(saveIndex)
    else:
        assert KDS.ConfigManager.Save.Active != None, "Could not save story. No save loaded."
        KDS.ConfigManager.Save.Active.save()

    assert KDS.ConfigManager.Save.Active != None, "play_story function failed. No save loaded."

    if KDS.ConfigManager.Save.Active.Story.index > KDS.ConfigManager.GetGameData("Story/levelCount"):
        KDS.Story.EndCredits(display, KDS.Story.EndingType.Happy)
        main_menu()
        return

    if KDS.ConfigManager.Save.Active.Story.playerName == "<name-error>":
        playerName = KDS.Console.Start("Enter name:", True, KDS.Console.CheckTypes.String(20, invalidStrings=("<name-error>"), funnyStrings=["name"], noSpace=True), background=pygame.image.load("Assets/Textures/UI/tutorial.png").convert()) #Name is invalid because fuck the player. They took "Enter Name" literally.
        if len(playerName) < 1:
            KDS.ConfigManager.Save.Active.delete()
            pygame.mouse.set_visible(True)
            return

        newName = ""
        for name in playerName.split('-'):
            if len(name) > 0:
                newName += name[0].upper()
                if len(name) > 1:
                    newName += name[1:]
            newName += '-'
        playerName = newName[:-1]

        KDS.ConfigManager.Save.Active.Story.playerName = playerName
        KDS.ConfigManager.Save.Active.save(updateStats=False)

    KDS.Audio.Music.Stop()

    animationOverride = map_names[KDS.ConfigManager.Save.Active.Story.index] != "<no-animation>"
    if animationOverride and show_loading:
        KDS.Loading.Story.Start(display, oldSurf, map_names[KDS.ConfigManager.Save.Active.Story.index], ArialTitleFont, ArialFont)
    KDS.Koponen.setPlayerPrefix(KDS.ConfigManager.Save.Active.Story.playerName)
    play_function(KDS.Gamemode.Modes.Story, True, show_loading=not animationOverride, auto_play_music=False)
    KDS.Loading.Story.WaitForExit()
    if KDS.Audio.Music.Loaded != None:
        KDS.Audio.Music.Play()

def respawn_function():
    global level_finished
    KDS.Scores.levelDeaths += 1
    Player.reset(clear_inventory=False, clear_keys=False)
    level_finished = False
    if WorldData.PlayerStartPos[0] == -1 and WorldData.PlayerStartPos[1] == -1:
        KDS.Logging.AutoError("PlayerStartPos is (-1, -1)!")
    if RespawnAnchor.active == None:
        Player.rect.topleft = WorldData.PlayerStartPos
    else:
        Player.rect.midbottom = RespawnAnchor.active.rect.midbottom
    if KDS.Audio.Music.Loaded != None:
        KDS.Audio.Music.Play()
#endregion
#region Menus
def esc_menu_f(oldSurf: pygame.Surface):
    global esc_menu, go_to_main_menu, clock, c
    c = False

    esc_surface = pygame.Surface(display_size, SRCALPHA)

    normal_background = pygame.transform.scale(oldSurf.copy(), display_size)
    blurred_background = KDS.Convert.ToBlur(pygame.transform.scale(oldSurf.copy(), display_size), 6)

    def resume():
        global esc_menu
        esc_menu = False

    def goto_main_menu():
        global esc_menu, go_to_main_menu
        pygame.mixer.unpause()
        esc_menu = False
        go_to_main_menu = True

    aligner = (display_size[0] // 2, display_size[1] // 2 - 200, display_size[1] // 2 + 200)

    resume_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 100, aligner[2] - 160, 200, 30), resume, KDS.UI.ButtonFontSmall.render("RESUME", True, KDS.Colors.White))
    settings_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 100, aligner[2] - 120, 200, 30), settings_menu, KDS.UI.ButtonFontSmall.render("SETTINGS", True, KDS.Colors.White))
    main_menu_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 100, aligner[2] - 80, 200, 30), goto_main_menu, KDS.UI.ButtonFontSmall.render("MAIN MENU", True, KDS.Colors.White))

    anim_lerp_x = KDS.Animator.Value(0.0, 1.0, 15, KDS.Animator.AnimationType.EaseOutSine, KDS.Animator.OnAnimationEnd.Stop)

    while esc_menu:
        display.blit(pygame.transform.scale(normal_background, display_size), (0, 0))
        anim_x = anim_lerp_x.update(False)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if defaultEventHandler(event):
                continue
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    esc_menu = False
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True

        esc_surface.blit(pygame.transform.scale(
            blurred_background, display_size), (0, 0))
        pygame.draw.rect(esc_surface, (123, 134, 111), (aligner[0] - 250, aligner[1], 500, 400))
        esc_surface.blit(pygame.transform.scale(
            text_icon, (250, 139)), (aligner[0] - 125, aligner[1] + 50))

        resume_button.update(esc_surface, mouse_pos, c)
        settings_button.update(esc_surface, mouse_pos, c)
        main_menu_button.update(esc_surface, mouse_pos, c)

        esc_surface.set_alpha(int(KDS.Math.Lerp(0, 255, anim_x)))
        display.blit(esc_surface, (0, 0))
        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

        display.blit(pygame.transform.scale(display, display_size), (0, 0))
        pygame.display.flip()
        display.fill(KDS.Colors.Black)
        c = False
        KDS.Clock.Tick()

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, pauseOnFocusLoss, play_walk_sound
    c = False
    settings_running = True

    def return_def():
        global settings_running
        settings_running = False

    def reset_settings():
        return_def()
        oldTerms = KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)
        KDS.ConfigManager.OverrideDefaultSettings()
        KDS.ConfigManager.SetSetting("Data/Terms/accepted", oldTerms)

    def remove_data():
        if KDS.System.MessageBox.Show("Remove Data", "Are you sure you want to remove all Koponen Dating Simulator data? This cannot be undone.", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.WARNING) == KDS.System.MessageBox.Responses.YES:
            KDS_Quit(remove_data_s=True)

    return_button = KDS.UI.Button(pygame.Rect(465, 700, 270, 60), return_def, "RETURN")
    music_volume_slider = KDS.UI.Slider("musicVolume", pygame.Rect(450, 135, 340, 20), (20, 30), ..., custom_path="Mixer/Volume/music")
    effect_volume_slider = KDS.UI.Slider("effectVolume", pygame.Rect(450, 185, 340, 20), (20, 30), ..., custom_path="Mixer/Volume/effect")
    walk_sound_switch = KDS.UI.Switch("playWalkSound", pygame.Rect(450, 235, 100, 30), (30, 50), ..., custom_path="Mixer/walkSound")
    legacy_lobbymusic_switch = KDS.UI.Switch("legacyLobbyMusic", pygame.Rect(450, 305, 100, 30), (30, 50), ..., custom_path="Mixer/legacyLobbyMusic")
    lastLobbymusicState = legacy_lobbymusic_switch.state
    pause_loss_switch = KDS.UI.Switch("pauseOnFocusLoss", pygame.Rect(450, 375, 100, 30), (30, 50), ..., custom_path="Game/pauseOnFocusLoss")
    controls_settings_button = KDS.UI.Button(pygame.Rect(480, 485, 260, 50), lambda: KDS.Keys.StartBindingMenu(display, defaultEventHandler), KDS.UI.ButtonFontSmall.render("Controls", True, KDS.Colors.White))
    reset_settings_button = KDS.UI.Button(pygame.Rect(220, 595, 240, 40), reset_settings, KDS.UI.ButtonFontSmall.render("Reset Settings", True, KDS.Colors.White))
    give_feedback_button = KDS.UI.Button(pygame.Rect(480, 595, 240, 40), lambda: KDS.System.OpenURL("https://github.com/KL-Corporation/Koponen-Dating-Simulator/issues"), KDS.UI.ButtonFontSmall.render("Give Feedback", True, KDS.Colors.EmeraldGreen))
    remove_data_button = KDS.UI.Button(pygame.Rect(740, 595, 240, 40), remove_data, KDS.UI.ButtonFontSmall.render("Remove Data", True, KDS.Colors.White))
    music_volume_text = KDS.UI.ButtonFontSmall.render("Music Volume", True, KDS.Colors.White)
    effect_volume_text = KDS.UI.ButtonFontSmall.render("Sound Effect Volume", True, KDS.Colors.White)
    walk_sound_text = KDS.UI.ButtonFontSmall.render("Play footstep sounds", True, KDS.Colors.White)
    legacy_lobbymusic_text = KDS.UI.ButtonFontSmall.render("Play Legacy Menu Music", True, KDS.Colors.White)
    pause_loss_text = KDS.UI.ButtonFontSmall.render("Pause On Focus Loss", True, KDS.Colors.White)

    while settings_running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if defaultEventHandler(event):
                continue
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    settings_running = False

        display.blit(settings_background, (0, 0))

        display.blit(pygame.transform.flip(
            menu_trashcan_animation.update(), False, False), (279, 515))

        display.blit(music_volume_text, (50, 135))
        display.blit(effect_volume_text, (50, 185))
        display.blit(walk_sound_text, (50, 235))
        display.blit(legacy_lobbymusic_text, (50, 305))
        display.blit(pause_loss_text, (50, 375))
        KDS.Audio.Music.SetVolume(music_volume_slider.update(display, mouse_pos))
        KDS.Audio.SetVolume(effect_volume_slider.update(display, mouse_pos))
        play_walk_sound = walk_sound_switch.update(display, mouse_pos, c)
        tmp = legacy_lobbymusic_switch.update(display, mouse_pos, c)
        if tmp != lastLobbymusicState:
            lastLobbymusicState = tmp
            KDS.Audio.Music.Play("Assets/Audio/Music/lobbymusic.ogg" if lastLobbymusicState == False else "Assets/Audio/Music/Legacy/lobbymusic.ogg")
        pauseOnFocusLoss = pause_loss_switch.update(display, mouse_pos, c)

        return_button.update(display, mouse_pos, c)
        controls_settings_button.update(display, mouse_pos, c)
        reset_settings_button.update(display, mouse_pos, c)
        remove_data_button.update(display, mouse_pos, c)
        give_feedback_button.update(display, mouse_pos, c)
        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

        pygame.display.flip()
        display.fill(KDS.Colors.Black)
        c = False
        KDS.Clock.Tick()

def main_menu():
    global current_map, current_map_name

    pygame.mouse.set_visible(True)

    class Mode(IntEnum):
        MainMenu = 0
        ModeSelectionMenu = 1
        StoryMenu = 2
        CampaignMenu = 3
    MenuMode: Mode = Mode.MainMenu

    current_map_int = int(current_map)

    global main_menu_running, main_running, go_to_main_menu
    go_to_main_menu = False

    main_menu_running = True
    c = False
    skip_render_this_frame = False

    KDS.Audio.Music.Play("Assets/Audio/Music/lobbymusic.ogg" if KDS.ConfigManager.GetSetting("Mixer/legacyLobbyMusic", False) == False else "Assets/Audio/Music/Legacy/lobbymusic.ogg")

    map_names: Dict[int, str] = {}
    custom_maps_names = {}
    def load_map_names():
        nonlocal map_names, custom_maps_names
        map_names = {}
        custom_maps_names = {}
        try:
            with open("Assets/Maps/Campaign/names.dat", "r") as file:
                tmp = file.read().split("\n")
                for t in tmp:
                    tmp_split = t.split(":")
                    for i in range(len(tmp_split)):
                        tmp_split[i] = tmp_split[i].strip()
                    if len(tmp_split) == 2:
                        map_names[int(tmp_split[0])] = tmp_split[1]
                    else:
                        KDS.Logging.AutoError(f"Map name \"{t}\" is broken!")
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")
        try:
            for i, p in enumerate(os.listdir(PersistentPaths.CustomMaps)):
                custom_maps_names[i + 1] = p
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")
    if len(map_names) < 1:
        load_map_names()

    class level_pick:
        class direction:
            left = -1
            right = 1
            none = 0

        @staticmethod
        def right():
            level_pick.pick(level_pick.direction.right)

        @staticmethod
        def left():
            level_pick.pick(level_pick.direction.left)

        @staticmethod
        def pick(direction: int):
            global current_map
            current_map_int = int(current_map)
            if direction == level_pick.direction.left:
                current_map_int -= 1
            elif direction == level_pick.direction.right:
                current_map_int += 1
            current_map_int = KDS.Math.Clamp(current_map_int, -len(custom_maps_names), len(map_names))
            current_map = f"{current_map_int:02d}"
            KDS.ConfigManager.SetSetting("Player/currentMap", current_map)
    level_pick.pick(level_pick.direction.none)

    def menu_mode_selector(mode: Mode):
        nonlocal MenuMode
        MenuMode = mode

    #region Main Menu

    #Main menu variables:
    framecounter = 0
    current_frame = 0
    framechange_lerp = KDS.Animator.Value(0.0, 255.0, 100, KDS.Animator.AnimationType.EaseInOutSine, KDS.Animator.OnAnimationEnd.Stop)
    framechange_lerp.tick = framechange_lerp.ticks

    main_menu_play_button = KDS.UI.Button(pygame.Rect(450, 180, 300, 60), menu_mode_selector, "PLAY")
    main_menu_settings_button = KDS.UI.Button(pygame.Rect(450, 250, 300, 60), settings_menu, "SETTINGS")
    main_menu_quit_button = KDS.UI.Button(pygame.Rect(450, 320, 300, 60), KDS_Quit, "QUIT")
    #Frame 2
    Frame2 = pygame.Surface(display_size)
    Frame2.fill(KDS.Colors.DefaultBackground)
    Frame2.blit(main_menu_background_2, (0, 0))
    #Frame 3
    Frame3 = pygame.Surface(display_size)
    Frame3.fill(KDS.Colors.DefaultBackground)
    Frame3.blit(main_menu_background_3, (0, 0))
    #Frame 4
    Frame4 = pygame.Surface(display_size)
    Frame4.fill(KDS.Colors.DefaultBackground)
    Frame4.blit(main_menu_background_4, (0, 0))
    #endregion
    #region Mode Selection Menu
    mode_selection_modes = []
    mode_selection_modes.append(KDS.Gamemode.Modes.Story)
    mode_selection_modes.append(KDS.Gamemode.Modes.Campaign)
    mode_selection_buttons = []
    story_mode_button = pygame.Rect(0, 0, display_size[0], display_size[1] // 2)
    campaign_mode_button = pygame.Rect(0, display_size[1] // 2, display_size[0], display_size[1] // 2)
    mode_selection_buttons.append(story_mode_button)
    mode_selection_buttons.append(campaign_mode_button)
    #endregion
    return_text = KDS.UI.ButtonFont.render("RETURN", True, (KDS.Colors.AviatorRed))
    return_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 150, display_size[1] - 150, 300, 100), menu_mode_selector, return_text)
    #region Story Menu
    story_new_save_override = False
    def newSave():
        nonlocal story_new_save_override
        story_new_save_override = not story_new_save_override

    def storyStartMiddleman(index: int):
        nonlocal story_new_save_override, skip_render_this_frame
        if story_new_save_override:
            KDS.ConfigManager.Save(index).delete()
        play_story(index)
        skip_render_this_frame = True

    story_save_button_0_rect = pygame.Rect(14, 14, 378, 400)
    story_save_button_1_rect = pygame.Rect(410, 14, 378, 400)
    story_save_button_2_rect = pygame.Rect(806, 14, 378, 400)
    story_save_button_0 = KDS.UI.Button(story_save_button_0_rect, storyStartMiddleman)
    story_save_button_1 = KDS.UI.Button(story_save_button_1_rect, storyStartMiddleman)
    story_save_button_2 = KDS.UI.Button(story_save_button_2_rect, storyStartMiddleman)
    story_new_save_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 175, display_size[1] - 325, 350, 125), newSave, "<error>")
    story_menu_data = None
    story_background: pygame.Surface = pygame.image.load("Assets/Textures/UI/Menus/story_menu.png").convert()
    #endregion
    #region Campaign Menu
    campaign_right_button_rect = pygame.Rect(1084, 200, 66, 66)
    campaign_left_button_rect = pygame.Rect(50, 200, 66, 66)
    campaign_play_button_rect = pygame.Rect(display_size[0] // 2 - 150, display_size[1] - 300, 300, 100)
    campaign_play_text = KDS.UI.ButtonFont.render("START", True, KDS.Colors.EmeraldGreen)
    campaign_backgrounds: Dict[int, pygame.Surface] = {
        1: pygame.image.load("Assets/Textures/UI/Menus/Campaign/1.png").convert(),
        2: pygame.image.load("Assets/Textures/UI/Menus/Campaign/2.png").convert(),
        3: pygame.image.load("Assets/Textures/UI/Menus/Campaign/3.png").convert(),
        4: pygame.image.load("Assets/Textures/UI/Menus/Campaign/4.png").convert(),
        5: pygame.image.load("Assets/Textures/UI/Menus/Campaign/5.png").convert(),
        6: pygame.image.load("Assets/Textures/UI/Menus/Campaign/6.png").convert(),
        7: pygame.image.load("Assets/Textures/UI/Menus/Campaign/7.png").convert(),
        8: pygame.image.load("Assets/Textures/UI/Menus/Campaign/8.png").convert(),
        9: pygame.image.load("Assets/Textures/UI/Menus/Campaign/9.png").convert(),
        10: pygame.image.load("Assets/Textures/UI/Menus/Campaign/10.png").convert()
    }
    campaignNoBackgroundSurf: pygame.Surface = pygame.Surface(display_size)

    campaignCurrentBackground: Optional[pygame.Surface] = None
    campaignLastBackground: Optional[pygame.Surface] = None
    campaignBackgroundAnim = KDS.Animator.Value(0, 255, 30)

    def campaign_play_handler():
        if current_map_int != 0:
            play_function(KDS.Gamemode.Modes.Campaign if current_map_int > 0 else KDS.Gamemode.Modes.CustomCampaign, True)

    campaign_play_button = KDS.UI.Button(campaign_play_button_rect, campaign_play_handler, campaign_play_text)
    campaign_left_button = KDS.UI.Button(campaign_left_button_rect, level_pick.left, pygame.transform.flip(arrow_button, True, False))
    campaign_right_button = KDS.UI.Button(campaign_right_button_rect, level_pick.right, arrow_button)

    Frame1 = pygame.Surface(display_size)
    Frame1.fill(KDS.Colors.DefaultBackground)
    frames = [Frame1, Frame2, Frame3, Frame4]
    #endregion
    while main_menu_running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if defaultEventHandler(event, QUIT):
                continue
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if MenuMode == Mode.ModeSelectionMenu or MenuMode == Mode.MainMenu:
                        MenuMode = Mode.MainMenu
                    else:
                        menu_mode_selector(Mode.ModeSelectionMenu)
                elif event.key == K_F5:
                    if debug_gamesetting_allow_subprog_debug:
                        KDS.Audio.Music.Pause()
                        KDS.School.Certificate(display, KDS.Colors.DefaultBackground)
                        KDS.Audio.Music.Unpause()
                elif event.key == K_F6:
                    if debug_gamesetting_allow_subprog_debug:
                        KDS.Audio.Music.Pause()
                        KDS.Story.Tombstones(display)
                        KDS.Audio.Music.Unpause()
            elif event.type == QUIT:
                KDS_Quit()

        if MenuMode == Mode.MainMenu:
            Frame1.blit(main_menu_background, (0, 0))

            Frame1.blit(pygame.transform.flip(
                menu_gasburner_animation.update(), False, False), (625, 445))
            Frame1.blit(pygame.transform.flip(
                menu_toilet_animation.update(), False, False), (823, 507))
            Frame1.blit(pygame.transform.flip(
                menu_trashcan_animation.update(), False, False), (283, 585))

            frames[current_frame].set_alpha(int(framechange_lerp.update()))

            display.blit(frames[current_frame - 1].convert_alpha(), (0, 0))
            display.blit(frames[current_frame].convert_alpha(), (0,0))

            main_menu_play_button.update(display, mouse_pos, c, Mode.ModeSelectionMenu)
            main_menu_settings_button.update(display, mouse_pos, c)
            main_menu_quit_button.update(display, mouse_pos, c)

            display.blit(main_menu_title, (391, 43))
            framecounter += 1

            if framecounter > 550:
                current_frame += 1
                framecounter = 0
                if current_frame > len(frames)-1:
                    current_frame = 0
                framechange_lerp.tick = 0
                frames[current_frame].set_alpha(0)
                frames[current_frame - 1].set_alpha(255)

        elif MenuMode == Mode.ModeSelectionMenu:

            display.blit(gamemode_bc_1_1, (0, 0))
            display.blit(gamemode_bc_2_1, (0, display_size[1] // 2))
            for y in range(len(mode_selection_buttons)):
                if mode_selection_buttons[y].collidepoint(mouse_pos):
                    if y == 0:
                        gamemode_bc_1_2.set_alpha(int(gamemode_bc_1_alpha.update(True)))
                        display.blit(gamemode_bc_1_2, (story_mode_button.x, story_mode_button.y))
                    elif y == 1:
                        gamemode_bc_2_2.set_alpha(int(gamemode_bc_2_alpha.update(True)))
                        display.blit(gamemode_bc_2_2, (campaign_mode_button.x, campaign_mode_button.y))
                    if c:
                        if mode_selection_modes[y] == KDS.Gamemode.Modes.Story:
                            MenuMode = Mode.StoryMenu
                        elif mode_selection_modes[y] == KDS.Gamemode.Modes.Campaign:
                            MenuMode = Mode.CampaignMenu
                            campaignBackgroundAnim.tick = 0
                            campaignLastBackground = None
                            c = False
                        else:
                            KDS.Logging.AutoError(f"Invalid mode_selection_mode! Value: {mode_selection_modes[y]}")
                else:
                    if y == 0:
                        gamemode_bc_1_2.set_alpha(int(gamemode_bc_1_alpha.update(False)))
                        display.blit(gamemode_bc_1_2, (story_mode_button.x, story_mode_button.y))
                    elif y == 1:
                        gamemode_bc_2_2.set_alpha(int(gamemode_bc_2_alpha.update(False)))
                        display.blit(gamemode_bc_2_2, (campaign_mode_button.x, campaign_mode_button.y))

        elif MenuMode == Mode.StoryMenu:
            display.blit(story_background, (0, 0))

            font = harbinger_font
            fontHeight = font.get_height()

            text_offset = (10, 10)
            line_offset = 25

            if story_menu_data == None:
                story_menu_data = KDS.ConfigManager.Save.GetMenuData()

            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_0_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_1_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_2_rect, 10)

            story_save_button_0.update(display, mouse_pos, c, 0)
            story_save_button_1.update(display, mouse_pos, c, 1)
            story_save_button_2.update(display, mouse_pos, c, 2)

            story_new_save_button.overlay = KDS.UI.ButtonFont.render("NEW SAVE", True, KDS.Colors.EmeraldGreen if not story_new_save_override else KDS.Colors.AviatorRed)
            story_new_save_button.update(display, mouse_pos, c)
            return_button.update(display, mouse_pos, c, Mode.MainMenu)

            for index, data in enumerate(story_menu_data):
                rect = (story_save_button_0_rect, story_save_button_1_rect, story_save_button_2_rect)[index]
                if not story_new_save_override:
                    if data != None:
                        lines = [
                            data["name"],
                            f"""Progress: {KDS.Math.RoundCustomInt(data["progress"] * 100, KDS.Math.MidpointRounding.AwayFromZero)}%""",
                            None,
                            None,
                            f"""Exam Grade: {KDS.Convert.ToRational(data["grade"])}""" if data["grade"] != -1 else None,
                            f"""Score: {data["score"]}""",
                            f"""Playtime: {KDS.Scores.GameTime.GetFormattedString(data["playtime"])}""",
                            f"""Last Played: {KDS.Convert.DateTime.Humanize(datetime.fromtimestamp(data["lastPlayedTimestamp"]))}"""
                        ]
                        for i, line in enumerate(lines):
                            rendered = font.render(line, True, KDS.Colors.White)
                            display.blit(rendered, (text_offset[0] + rect.x, (i * (fontHeight + line_offset)) + text_offset[1] + rect.y))
                    else:
                        rendered = font.render("EMPTY SLOT", True, KDS.Colors.White)
                        display.blit(rendered, ((rect.width // 2 - rendered.get_width() // 2) + rect.x, (rect.height // 3 - rendered.get_height() // 2) + rect.y))
                else:
                    rendered = font.render("PICK SLOT", True, KDS.Colors.White)
                    display.blit(rendered, ((rect.width // 2 - rendered.get_width() // 2) + rect.x, (rect.height // 3 - rendered.get_height() // 2) + rect.y))

        elif MenuMode == Mode.CampaignMenu:
            campaign_comp = campaign_backgrounds[current_map_int] if current_map_int in campaign_backgrounds else None
            if campaign_comp is not campaignCurrentBackground:
                campaignLastBackground = campaignCurrentBackground
                campaignCurrentBackground = campaign_comp
                campaignBackgroundAnim.tick = 0
            campaignToBlit = (campaignCurrentBackground if campaignCurrentBackground != None else campaignNoBackgroundSurf).copy()
            campaignToBlit.set_alpha(int(campaignBackgroundAnim.update()))
            display.blit(campaignLastBackground if campaignLastBackground != None else campaignNoBackgroundSurf, (0, 0))
            display.blit(campaignToBlit, (0, 0))

            if len(os.listdir(PersistentPaths.CustomMaps)) != len(custom_maps_names):
                KDS.Logging.debug("New custom maps detected.", True)
                load_map_names()
                level_pick.pick(level_pick.direction.none)

            pygame.draw.rect(display, KDS.Colors.LightGray, (50, 200, int(display_size[0] - 100), 66))

            current_map_int = int(current_map)

            if current_map_int in map_names:
                current_map_name = map_names[current_map_int]
            elif current_map_int < 0 and abs(current_map_int) in custom_maps_names:
                current_map_name = custom_maps_names[abs(current_map_int)]
            else:
                current_map_name = "[ ERROR ]"

            if current_map_int > 0:
                render_map_name = f"{current_map} - {current_map_name}"
            elif current_map_int == 0:
                render_map_name = "<= Custom                Campaign =>"
            else:
                render_map_name = f"CUSTOM - {current_map_name}"
            level_text = KDS.UI.ButtonFont.render(render_map_name, True, (0, 0, 0))
            display.blit(level_text, (125, 209))

            skip_render_this_frame = campaign_play_button.update(display, mouse_pos, c)
            return_button.update(display, mouse_pos, c, Mode.MainMenu)
            campaign_left_button.update(display, mouse_pos, c)
            campaign_right_button.update(display, mouse_pos, c)

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

        c = False
        if not skip_render_this_frame:
            pygame.display.flip()
        else:
            skip_render_this_frame = False
        display.fill(KDS.Colors.DefaultBackground)
        KDS.Clock.Tick()

def level_finished_menu(oldSurf: pygame.Surface):
    global level_finished_running

    score_color = KDS.Colors.Cyan
    padding = 50
    textVertOffset = 40
    textStartVertOffset = 300
    totalVertOffset = 25
    timeTakenVertOffset = 100
    scoreTexts = (
        ArialFont.render("Score:", True, score_color),
        ArialFont.render("Deathless Bonus:", True, score_color),
        ArialFont.render("Time Bonus:", True, score_color),
        ArialFont.render("Total:", True, score_color)
    )

    KDS.Audio.Music.Play("Assets/Audio/Music/level_cleared.ogg")

    KDS.Scores.ScoreAnimation.init()
    anim_lerp_x = KDS.Animator.Value(0.0, 1.0, 15, KDS.Animator.AnimationType.EaseOutSine, KDS.Animator.OnAnimationEnd.Stop)
    level_f_surf = pygame.Surface(display_size, SRCALPHA)
    normal_background = pygame.transform.scale(oldSurf.copy(), display_size)
    blurred_background = KDS.Convert.ToBlur(pygame.transform.scale(oldSurf.copy(), display_size), 6)
    menu_rect = pygame.Rect(display_size[0] // 2 - 250, display_size[1] // 2 - 300, 500, 600)

    def goto_main_menu():
        global level_finished_running, go_to_main_menu
        level_finished_running = False
        go_to_main_menu = True
        KDS.Audio.Music.Unpause()

    render_level_finished: bool = True
    def next_level():
        global level_finished_running, current_map
        nonlocal render_level_finished
        level_finished_running = False
        current_map = f"{int(current_map) + 1:02}"
        play_function(KDS.Gamemode.Modes.Campaign, True)
        render_level_finished = False

    next_level_bool = int(current_map) < int(KDS.ConfigManager.GetGameData("Campaign/officialLevelCount"))

    main_menu_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 - 220, menu_rect.bottom - padding, 200, 30), goto_main_menu, KDS.UI.ButtonFontSmall.render("Main Menu", True, KDS.Colors.White))
    next_level_button = KDS.UI.Button(pygame.Rect(display_size[0] // 2 + 20, menu_rect.bottom - padding, 200, 30), next_level, KDS.UI.ButtonFontSmall.render("Next Level", True, KDS.Colors.White), enabled=next_level_bool)

    pre_rendered_scores = {}


    level_finished_running = True
    while level_finished_running:
        display.blit(normal_background, (0, 0))
        anim_x = anim_lerp_x.update(False)
        mouse_pos = pygame.mouse.get_pos()

        c = False
        for event in pygame.event.get():
            if defaultEventHandler(event):
                continue
            elif event.type == KEYUP:
                if event.key in (K_SPACE, K_RETURN, K_ESCAPE):
                    KDS.Scores.ScoreAnimation.skip()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    KDS.Scores.ScoreAnimation.skip()
                    c = True

        level_f_surf.blit(pygame.transform.scale(blurred_background, display_size), (0, 0))
        pygame.draw.rect(level_f_surf, (123, 134, 111), menu_rect)
        level_f_surf.blit(pygame.transform.scale(level_cleared_icon, (250, 139)), (display_size[0] // 2 - 125, display_size[1] // 2 - 275))

        values = KDS.Scores.ScoreAnimation.update(anim_lerp_x.tick >= anim_lerp_x.ticks)
        comparisonValue = KDS.Math.Clamp(KDS.Scores.ScoreAnimation.animationIndex + 1, 0, len(values))
        lineY = textStartVertOffset + (len(values) - 1) * textVertOffset + round(totalVertOffset / 2)
        pygame.draw.line(level_f_surf, KDS.Colors.Cyan, (menu_rect.left + padding, lineY), (menu_rect.right - padding, lineY), 3)
        for i in range(len(scoreTexts)):
            totalOffset = i == len(values) - 1
            textY = textStartVertOffset + i * textVertOffset + (0 if not totalOffset else totalVertOffset)
            if i < comparisonValue:
                value = str(values[i])
                if value not in pre_rendered_scores:
                    rend_txt = ArialFont.render(value, True, score_color)
                    if KDS.Scores.ScoreAnimation.animationList[i].Finished:
                        pre_rendered_scores[value] = rend_txt
                else:
                    rend_txt = pre_rendered_scores[value]
                level_f_surf.blit(rend_txt, (menu_rect.right - rend_txt.get_width() - padding, textY))
            level_f_surf.blit(scoreTexts[i], (menu_rect.left + padding, textY))

        if KDS.Scores.ScoreAnimation.finished:
            timeTakenText = ArialFont.render(f"Time Taken: {KDS.Scores.GameTime.GetFormattedString()}", True, score_color)
            textY = textStartVertOffset + (len(values) - 1) * textVertOffset + totalVertOffset
            level_f_surf.blit(timeTakenText, (menu_rect.left + padding, textY + timeTakenVertOffset))

            main_menu_button.update(level_f_surf, mouse_pos, c)
            next_level_button.update(level_f_surf, mouse_pos, c)

        level_f_surf.set_alpha(round(KDS.Math.Lerp(0, 255, anim_x)))
        display.blit(level_f_surf, (0, 0))
        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))
        if render_level_finished:
            pygame.display.flip()
        KDS.Clock.Tick()
#endregion
#region Check Terms
pygame.event.clear()
if not tcagr:
    agr()
    tcagr: bool = KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)
if tcagr:
    main_menu()
#endregion
#region Main Running
while main_running:
#region Events
    KDS.Keys.Update()
    for event in pygame.event.get():
        if defaultEventHandler(event):
            continue
        elif event.type == KEYDOWN:
            if event.key in KDS.Keys.moveRight.Bindings:
                KDS.Keys.moveRight.SetState(True)
            elif event.key in KDS.Keys.moveLeft.Bindings:
                KDS.Keys.moveLeft.SetState(True)
            elif event.key in KDS.Keys.moveUp.Bindings:
                KDS.Keys.moveUp.SetState(True)
            elif event.key in KDS.Keys.moveDown.Bindings:
                KDS.Keys.moveDown.SetState(True)
            elif event.key in KDS.Keys.moveRun.Bindings:
                if not KDS.Keys.moveDown.pressed:
                    KDS.Keys.moveRun.SetState(True)
            elif event.key in KDS.Keys.functionKey.Bindings:
                KDS.Keys.functionKey.SetState(True)
            elif event.key == K_ESCAPE:
                esc_menu = True
            elif (matchingInventoryKey := KDS.Linq.FirstOrNone(KDS.Keys.INVENTORYKEYS, lambda ik: event.key in ik.Bindings)) != None:
                Player.inventory.pickSlot(matchingInventoryKey.index)
            elif event.key in KDS.Keys.dropItem.Bindings:
                if Player.inventory.getHandItem() != KDS.Inventory.EMPTYSLOT and Player.inventory.getHandItem() != KDS.Inventory.DOUBLEITEM:
                    droppedItem: Optional[KDS.Build.Item] = Player.inventory.dropItem()
                    if droppedItem != None:
                        KDS.Build.Item.modDroppedPropertiesAndAddToList(Items, droppedItem, Player)
            elif event.key in KDS.Keys.fart.Bindings:
                if Player.stamina == 100:
                    Player.stamina = -1000.0
                    Player.farting = True
                    KDS.Audio.PlaySound(fart)
            elif event.key in KDS.Keys.altDown.Bindings:
                KDS.Keys.altDown.SetState(True)
            elif event.key in KDS.Keys.altUp.Bindings:
                KDS.Keys.altUp.SetState(True)
            elif event.key in KDS.Keys.altLeft.Bindings:
                KDS.Keys.altLeft.SetState(True)
            elif event.key in KDS.Keys.altRight.Bindings:
                KDS.Keys.altRight.SetState(True)
            elif event.key in KDS.Keys.hideUI.Bindings:
                renderUI = not renderUI
            elif event.key in KDS.Keys.terminal.Bindings:
                if KDS.Gamemode.gamemode != KDS.Gamemode.Modes.Story or debug_gamesetting_allow_console_in_storymode: # Console is disabled in story mode if debug setting not overridden in GameData.
                    go_to_console = True
            elif event.key in KDS.Keys.screenshot.Bindings:
                pygame.image.save(screen, os.path.join(PersistentPaths.Screenshots, datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"))
                KDS.Audio.PlaySound(camera_shutter)
            elif event.key == K_F5 and debug_gamesetting_allow_subprog_debug:
                KDS.Audio.MusicMixer.pause()
                quit_temp, exam_score = KDS.School.Exam()
                KDS.Audio.MusicMixer.unpause()
                if quit_temp:
                    KDS_Quit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                KDS.Keys.mainKey.SetState(True)
                rk62_sound_cooldown = 11
        elif event.type == KEYUP:
            if event.key in KDS.Keys.moveRight.Bindings:
                KDS.Keys.moveRight.SetState(False)
            elif event.key in KDS.Keys.moveLeft.Bindings:
                KDS.Keys.moveLeft.SetState(False)
            elif event.key in KDS.Keys.moveUp.Bindings:
                KDS.Keys.moveUp.SetState(False)
            elif event.key in KDS.Keys.moveDown.Bindings:
                KDS.Keys.moveDown.SetState(False)
            elif event.key in KDS.Keys.moveRun.Bindings:
                KDS.Keys.moveRun.SetState(False)
            elif event.key in KDS.Keys.functionKey.Bindings:
                KDS.Keys.functionKey.SetState(False)
            elif event.key in KDS.Keys.altDown.Bindings:
                KDS.Keys.altDown.SetState(False)
            elif event.key in KDS.Keys.altUp.Bindings:
                KDS.Keys.altUp.SetState(False)
            elif event.key in KDS.Keys.altLeft.Bindings:
                KDS.Keys.altLeft.SetState(False)
            elif event.key in KDS.Keys.altRight.Bindings:
                KDS.Keys.altRight.SetState(False)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                KDS.Keys.mainKey.SetState(False)
        elif event.type == MOUSEWHEEL:
            tmpAmount = event.x - event.y
            if tmpAmount > 0:
                for _ in range(abs(tmpAmount)): Player.inventory.moveRight()
            else:
                for _ in range(abs(tmpAmount)): Player.inventory.moveLeft()
        elif event.type == WINDOWFOCUSLOST:
            if pauseOnFocusLoss: esc_menu = True
#endregion
#region Data
    display.fill(KDS.Colors.DefaultBackground)
    screen_overlay = None

    Lights.clear()

    true_scroll[0] += (Player.rect.centerx - true_scroll[0] - (screen_size[0] / 2)) / 12
    true_scroll[1] += (Player.rect.y - true_scroll[1] - 220) / 12

    scroll = [round(true_scroll[0]), round(true_scroll[1])]
    if level_background_img != None:
        screen.blit(level_background_img, (scroll[0] * 0.12 * -1 - 68, scroll[1] * 0.12 * -1 - 68))
    else:
        screen.fill(KDS.Colors.DefaultBackground)
    mouse_pos = pygame.mouse.get_pos()

    if Player.farting:
        scroll[0] += random.randint(-10, 10)
        scroll[1] += random.randint(-10, 10)
        Player.fart_counter += 1
        if Player.fart_counter > 256:
            Player.farting = False
            Player.fart_counter = 0
            for entity in Entities:
                if KDS.Math.getDistance(entity.rect.center, Player.rect.center) <= 800:
                    entity.health -= random.randint(500, 1000)
#endregion
#region Rendering
    ###### TÄNNE UUSI ASIOIDEN KÄSITTELY ######
    KDS.Build.Item.checkCollisions(Items, Player.rect, Player.inventory)
    KDS.Build.Tile.renderUpdate(Tiles, screen, (Player.rect.centerx - (Player.rect.x - scroll[0] - SCROLL_OFFSET[0]), Player.rect.centery - (Player.rect.y - scroll[1] - SCROLL_OFFSET[1])), scroll)
    TileFire.cachedAnimation.update()

    Entity.update(Entities)

    Player.update()

    #region Koponen
    if Koponen.enabled:
        talk = Koponen.force_talk or Koponen.start_with_talk
        if Koponen.rect.colliderect(Player.rect):
            Koponen.stopAutoMove()
            if Koponen.allow_talk:
                screen.blit(koponen_talk_tip, (Koponen.rect.centerx - scroll[0] - koponen_talk_tip.get_width() // 2, Koponen.rect.top - scroll[1] - 20))
                if KDS.Keys.functionKey.pressed:
                    KDS.Keys.Reset()
                    talk = True
        if talk:
            Koponen.start_with_talk = False
            result = KDS.Koponen.Talk.start(display, Player.inventory, KDS_Quit, autoExit=Koponen.force_talk)
            if result:
                KDS.Missions.ForceFinish()
                tmp = pygame.Surface(display_size)
                KDS.Koponen.Talk.renderMenu(tmp, (0, 0), False, Player.inventory, updateConversation=False)
                screen_overlay = pygame.transform.scale(tmp, screen_size)
        else:
            Koponen.continueAutoMove()

        Koponen.update(Tiles, display, KDS_Quit)
    #endregion
    KDS.Build.Item.renderUpdate(Items, Tiles, screen, scroll)
    if Player.health > 0 and Player.visible:
        Player.inventory.useItemsByClasses((Lantern, WalkieTalkie), Player.rect, Player.direction, screen, scroll)
        Player.inventory.useItem(Player.rect, Player.direction, screen, scroll)

    for Zone in Zones:
        Zone.update(Player.rect)

    for Projectile in Projectiles:
        result = Projectile.update(screen, scroll, Entities, HitTargets, Particles, Player.rect, Player.health)
        if result != None:
            v = result[0]
            Player.health = result[1]
        else:
            v = None

        if v == "wall" or v == "air":
            Projectiles.remove(Projectile)

    for B_Object in BallisticObjects:
        r2 = B_Object.update(Tiles, screen, scroll)
        if r2:
            for x in range(8):
                x /= -8
                Projectiles.append(KDS.World.Bullet(pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), True, -1, Tiles, 25, maxDistance=82, slope=x))
                Projectiles.append(KDS.World.Bullet(pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), False, -1, Tiles, 25, maxDistance=82, slope=x))

            KDS.Audio.PlaySound(landmine_explosion)
            Explosions.append(KDS.World.Explosion(KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop), (B_Object.rect.x - 60, B_Object.rect.y - 55)))

            BallisticObjects.remove(B_Object)

    #Räjähdykset
    for unit in Explosions:
        finished, etick = unit.update(screen, scroll)
        if finished:
            Explosions.remove(unit)
        elif etick < 10:
            Lights.append(KDS.World.Lighting.Light((unit.pos[0] - 80, unit.pos[1] - 80), KDS.World.Lighting.Shapes.circle_hard.get(300, 5500)))

    #Partikkelit
    #Particles.append(KDS.World.Lighting.Sparkparticle((Player.rect.x, Player.rect.y - 20), random.randint(1, 20), random.randint(1, 20), random.randint(1, 9)))
    if len(Particles) > maxParticles:
        Particles = Particles[maxParticles:]
    renderedParticleCount = len(Particles)
    for particle in Particles:
        result = particle.update(screen, scroll)
        if isinstance(result, pygame.Surface):
            Lights.append(KDS.World.Lighting.Light((particle.rect.x, particle.rect.y), result))
        elif result == KDS.World.Lighting.Particle.UpdateAction.KillParticle:
            Particles.remove(particle)
        elif result != KDS.World.Lighting.Particle.UpdateAction.NoLight:
            KDS.Logging.AutoError("Invalid particle update return value!")

    if KDS.Debug.Enabled:
        pygame.draw.rect(screen, KDS.Colors.Green, (Player.rect.x - scroll[0], Player.rect.y - scroll[1], Player.rect.width, Player.rect.height))
    if Player.visible:
        screen.blit(pygame.transform.flip(Player.animations.update(), Player.direction, False), (Player.rect.topleft[0] - scroll[0] + (Player.rect.width - Player.animations.active.size[0]) // 2, int(Player.rect.bottomleft[1] - scroll[1] - Player.animations.active.size[1])))
    if Koponen.enabled:
        Koponen.render(screen, scroll)

    #Overlayt
    for ov in overlays:
        if KDS.Debug.Enabled:
            pygame.draw.rect(screen, KDS.Colors.Blue, (ov.rect.x - scroll[0], ov.rect.y - scroll[1], 34, 34))
        KDS.Build.Tile.renderUnit(ov, screen, scroll)

    #Item Tip
    if KDS.Build.Item.tipItem != None:
        tip_rnd_pos = (KDS.Build.Item.tipItem.rect.centerx - itemTip.get_width() // 2, KDS.Build.Item.tipItem.rect.bottom - 45)
        screen.blit(itemTip, (tip_rnd_pos[0] - scroll[0], tip_rnd_pos[1] - scroll[1]))
        if KDS.Build.Item.tipItem.storePrice != None:
            price_tip = tip_font.render(f"{KDS.Build.Item.tipItem.storePrice}.00 euroa " + (f"""[SS-Etukortilla: {KDS.Build.Item.tipItem.storeDiscountPrice}.00{" ostoksen ohessa" if KDS.Build.Item.tipItem.storeDiscountPrice == 0 else ""}]""" if KDS.Build.Item.tipItem.storeDiscountPrice != None else ""), True, KDS.Colors.White)
            #                           if storePrice == 0, bulldogs will be angry if nothing else of value was bought
            screen.blit(price_tip, (KDS.Build.Item.tipItem.rect.centerx - price_tip.get_width() // 2 - scroll[0], tip_rnd_pos[1] + itemTip.get_height() - scroll[1]))

    #Valojen käsittely
    if KDS.World.Dark.enabled:
        if not KDS.World.Dark.Disco.enabled:
            black_tint.fill(KDS.World.Dark.darkness)
        else:
            black_tint.fill(KDS.World.Dark.Disco.colorAnimation.update())
            if KDS.World.Dark.Disco.colorAnimation.Finished:
                KDS.World.Dark.Disco.colorIndex = (KDS.World.Dark.Disco.colorIndex + 1) % len(KDS.World.Dark.Disco.colors)
                KDS.World.Dark.Disco.colorAnimation.From = KDS.World.Dark.Disco.colors[KDS.World.Dark.Disco.colorIndex]
                KDS.World.Dark.Disco.colorAnimation.To = KDS.World.Dark.Disco.colors[(KDS.World.Dark.Disco.colorIndex + 1) % len(KDS.World.Dark.Disco.colors)]
                KDS.World.Dark.Disco.colorAnimation.tick = 0
            circleSize: int = 20
            circleSpacing: int = 10
            circleSpeed: int = 1
            KDS.World.Dark.Disco.circleX = (KDS.World.Dark.Disco.circleX + circleSpeed) % (circleSize + circleSpacing)
            for x in range(KDS.World.Dark.Disco.circleX - (circleSize + circleSpeed), black_tint.get_width(), (circleSize + circleSpeed)):
                for y in range(circleSpacing, black_tint.get_height() - circleSpacing - circleSize, (circleSpacing + circleSize)):
                    black_tint.blit(KDS.World.Lighting.Shapes.circle_hard.get(circleSize // 2, 6000), (x, y))

        if Player.light and Player.visible:
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_soft.get(300, 5500), True))
        for light in Lights:
            black_tint.blit(light.surf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
            if KDS.Debug.Enabled:
                rectSurf = pygame.Surface(light.surf.get_size())
                rectSurf.fill(KDS.Colors.Yellow)
                rectSurf.set_alpha(128)
                screen.blit(rectSurf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
            #black_tint.blit(KDS.World.Lighting.Shapes.circle.get(40, 40000), (20, 20))
        screen.blit(black_tint, (0, 0), special_flags=BLEND_MULT)
    #UI
    if renderUI:
        yellow_indicator_states: Dict[str, bool] = {
            "visible_contraband": False
        }

        Player.health = max(Player.health, 0)
        ui_hand_item = Player.inventory.getHandItem()

        screen.blit(score_font.render(f"SCORE: {KDS.Scores.score}", True, KDS.Colors.White), (10, 45))
        screen.blit(score_font.render(f"""HEALTH: {KDS.Math.CeilToInt(Player.health) if not KDS.Math.IsInfinity(Player.health) else "INFINITE"}""", True, KDS.Colors.White), (10, 55))
        screen.blit(score_font.render(f"""STAMINA: {KDS.Math.CeilToInt(Player.stamina) if not KDS.Math.IsInfinity(Player.stamina) else "INFINITE"}""", True, KDS.Colors.White), (10, 120))
        if KDS.Gamemode.gamemode != KDS.Gamemode.Modes.Story:
            screen.blit(score_font.render(f"DEATHS: {KDS.Scores.levelDeaths}", True, KDS.Colors.White), (10, 130))

        KDS.UI.Indicator.visible_contraband = False
        if isinstance(ui_hand_item, KDS.Build.Item):
            if ui_hand_item.serialNumber in KDS.Build.Item.contraband:
                KDS.UI.Indicator.visible_contraband = True

            if isinstance(ui_hand_item, KDS.Build.Weapon):
                tmpAmmo = ui_hand_item.getAmmo()
                if not KDS.Math.IsInfinity(tmpAmmo):
                    ammoOffset = 10
                    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
                        ammoOffset = KDS.UI.Indicator.TEXTURESIZE[1] + (KDS.UI.Indicator.red_y_anim.get_value() if KDS.UI.Indicator.red_visible else 0) + 10
                    ammoRender: pygame.Surface = harbinger_font.render(f"""AMMO: {tmpAmmo if not KDS.Build.Item.infiniteAmmo else "INFINITE"}""", True, KDS.Colors.White)
                    screen.blit(ammoRender, (10, screen_size[1] - ammoRender.get_height() - ammoOffset))

        if Player.keys["red"]:
            screen.blit(red_key, (10, 20))
        if Player.keys["green"]:
            screen.blit(green_key, (24, 20))
        if Player.keys["blue"]:
            screen.blit(blue_key, (38, 20))

        KDS.UI.Indicator.combat = any([KDS.Teachers.TeacherState.Combat in t.state and t.health > 0 for t in KDS.Teachers.Teacher.InstanceList]) # Doing it by iterating whole list to have more consistent performance.
        KDS.UI.Indicator.searching = any([KDS.Teachers.TeacherState.Searching in t.state and t.health > 0 for t in KDS.Teachers.Teacher.InstanceList])
        KDS.UI.Indicator.trespassing = bool(KDS.World.Zone.StaffOnlyCollisions > 0)
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            KDS.UI.Indicator.render(screen)

        KDS.Missions.Render(screen)

        Player.inventory.render(screen)

    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################

#endregion
#region Screen Rendering
    if ScreenEffects.Queued():
        if ScreenEffects.Get(ScreenEffects.Effects.Flicker):
            data = ScreenEffects.EffectData.Flicker # Should be the same instance...

            if int(data["repeat_index"]) % int(data["repeat_rate"]) == 0:
                invPix = pygame.surfarray.pixels2d(screen)
                invPix ^= 2 ** 32 - 1
                del invPix

            data["repeat_index"] += 1
            if data["repeat_index"] > data["repeat_length"]:
                data["repeat_index"] = 0
                ScreenEffects.Finish(ScreenEffects.Effects.Flicker)
        if ScreenEffects.Get(ScreenEffects.Effects.FadeInOut):
            data = ScreenEffects.EffectData.FadeInOut # Should be the same instance...
            anim: KDS.Animator.Value = data["animation"] # Should be the same instance...
            rev: bool = data["reversed"]
            surf = data["surface"]
            surf.set_alpha(anim.update(rev))
            screen.blit(surf, (0, 0))
            if anim.Finished:
                if not rev:
                    data["wait_index"] += 1
                    if data["wait_index"] > data["wait_length"]:
                        data["reversed"] = True
                else:
                    data["reversed"] = False
                    data["wait_index"] = 0
                    ScreenEffects.Finish(ScreenEffects.Effects.FadeInOut)
        if ScreenEffects.Get(ScreenEffects.Effects.Glitch):
            data = ScreenEffects.EffectData.Glitch
            rptIndx = (int(data["repeat_index"]) + 1) % int(data["repeat_rate"])
            data["repeat_index"] = rptIndx
            if rptIndx == 0:
                glitchRandX = random.randrange(0, screen_size[0])
                glitchRandY = random.randrange(0, screen_size[1])
                # glitchRandW = random.randrange(screen_size[0], screen_size[0] + 1)
                glitchRandW = screen_size[0]
                glitchRandH = random.randrange(10, 50)
                data["current_glitch"] = (
                    (glitchRandX, glitchRandY, min(glitchRandW, screen_size[0] - glitchRandX), min(glitchRandH, screen_size[1] - glitchRandY)),
                    (random.randint(-10, 10) + glitchRandX, glitchRandY) # random.randint(0, 0) + glitchRandY)
                )
            current_glitch = data["current_glitch"]
            glitch_surf = screen.subsurface(current_glitch[0]).copy()
            if 0 <= current_glitch[1][0] < screen_size[0] and 0 <= current_glitch[1][1] < screen_size[1]:
                screen.blit(glitch_surf, current_glitch[1])

    if screen_overlay != None:
        screen.blit(screen_overlay, (0, 0))

    pygame.transform.scale(screen, display_size, display)

    #region Debug Mode
    if KDS.Debug.Enabled:
        frametime_ms: int = KDS.Clock.GetFrameTimeMs()
        raw_frametime_ms: int = KDS.Clock.GetRawFrameTimeMs()

        display.blit(KDS.Debug.RenderData({
            "FPS": KDS.Clock.GetFPS(3),
            "Frame Time": f"{frametime_ms} ms",
            "Raw Frame Time": f"{raw_frametime_ms} ms",
            "CPU Bound": f"{'Yes' if raw_frametime_ms >= frametime_ms else 'No'}", # When raw_frametime == frametime, we are CPU bound as we do not sleep anymore. Int comparison so it's accurate.
            "Player Position": Player.rect.topleft,
            "Enemies": f"{Enemy.total - Enemy.death_count} / {Enemy.total}",
            "Entities": f"{Entity.total - Entity.death_count} / {Entity.total} | Agro: {Entity.agro_count}",
            "Sounds Playing": f"{len(KDS.Audio.GetBusyChannels())} / {KDS.Audio.SoundMixer.get_num_channels()}",
            "Lights Rendering": len(Lights),
            "Particles Rendering": f"{renderedParticleCount} / {maxParticles}"
        }), (0, 0))
    #endregion

    if WalkieTalkie.storyTrigger or WalkieTalkie.storyRunning:
        if KDS.Story.WalkieTalkieEffect.Start(WalkieTalkie.storyTrigger, Player, display):
            KDS.Missions.SetProgress("explore", "find_walkie_talkie", 1.0)
            WalkieTalkie.storyRunning = False
            ScreenEffects.Trigger(ScreenEffects.Effects.Glitch)
        else:
            WalkieTalkie.storyRunning = True
        WalkieTalkie.storyTrigger = False

    pygame.display.flip()
#endregion
#region Data Update
    if KDS.Missions.GetFinished():
        level_finished = True

    for _teleportData in BaseTeleport.teleportDatas.values():
        _teleportData.Update()
#endregion
#region Conditional Events
    if Player.deathWait > 240:
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            if KDS.ConfigManager.Save.Active != None and KDS.Story.BadEndingTrigger:
                KDS.Scores.ScoreCounter.Stop()
                KDS.ConfigManager.Save.Active.save()
                KDS.ConfigManager.Save.Active = None

                KDS.Audio.StopAllSounds()
                KDS.Audio.Music.Stop()

                KDS.Story.EndCredits(display, KDS.Story.EndingType.Sad)
                main_menu()
            else:
                assert KDS.ConfigManager.Save.Active != None, "Cannot respawn player! No save loaded while in story mode!"
                play_story(KDS.ConfigManager.Save.Active.index, newSave=False, oldSurf=screen)
        else:
            respawn_function()
    if Player.rect.y > len(Tiles) * 34 + 340:
        Player.health = 0
        Player.rect.y = len(Tiles) * 34 + 340
    if esc_menu:
        KDS.Scores.ScoreCounter.Pause()
        KDS.Audio.Music.Pause()
        KDS.Audio.PauseAllSounds()
        pygame.transform.scale(screen, display_size, display)
        pygame.mouse.set_visible(True)
        esc_menu_f(screen)
        pygame.mouse.set_visible(False)
        KDS.Audio.Music.Unpause()
        KDS.Audio.UnpauseAllSounds()
        KDS.Scores.ScoreCounter.Unpause()
    if level_finished:
        KDS.Scores.ScoreCounter.Stop()
        KDS.Audio.StopAllSounds()
        KDS.Audio.Music.Stop()
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            assert KDS.ConfigManager.Save.Active != None, "Cannot finish level! No save loaded while in story mode."
            KDS.ConfigManager.Save.Active.Story.index += 1
            play_story(KDS.ConfigManager.Save.Active.Story.index, newSave=False, oldSurf=screen)
        else:
            pygame.mouse.set_visible(True)
            level_finished_menu(screen)
        level_finished = False
    if go_to_console:
        KDS.Audio.Music.Pause()
        KDS.Audio.PauseAllSounds()
        pygame.mouse.set_visible(True)
        console(screen)
        pygame.mouse.set_visible(False)
        KDS.Audio.Music.Unpause()
        KDS.Audio.UnpauseAllSounds()
    if go_to_main_menu:
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story and KDS.ConfigManager.Save.Active != None:
            KDS.Scores.ScoreCounter.Stop()
            KDS.ConfigManager.Save.Active.save()
            KDS.ConfigManager.Save.Active = None
        KDS.Audio.StopAllSounds()
        KDS.Audio.Music.Stop()
        main_menu()
#endregion
#region Ticks
    KDS.Clock.Tick()
#endregion
#endregion
#region Application Quitting
KDS.Jobs.quit()
KDS.Audio.Music.Unload()
KDS.System.emptdir(PersistentPaths.Cache)
KDS.Logging.quit()
pygame.mixer.quit()
pygame.display.quit()
pygame.quit()
if remove_data_on_quit:
    shutil.rmtree(PersistentPaths.AppData)
#endregion
