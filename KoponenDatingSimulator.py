#region Importing
from __future__ import annotations

from dataclasses import dataclass
import os
from uuid import UUID

import KDS.BuildData
import KDS.MapProp
import KDS.Money
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
from typing import Any, Callable, Dict, Final, Iterable, List, NamedTuple, Optional, Self, Sequence, Tuple, Type, Union

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
    # Cache = os.path.join(AppData, "cache")
    Saves = os.path.join(AppData, "saves")
    CampaignSaves = os.path.join(AppData, "saves_campaign")
    Logs = os.path.join(AppData, "logs")
    Screenshots = os.path.join(AppData, "screenshots")
    CustomMaps = os.path.join(AppData, "custom_maps")
os.makedirs(PersistentPaths.AppData, exist_ok=True)
# os.makedirs(PersistentPaths.Cache, exist_ok=True)
# KDS.System.emptdir(PersistentPaths.Cache)
# KDS.System.hide(PersistentPaths.Cache)
os.makedirs(PersistentPaths.Saves, exist_ok=True)
os.makedirs(PersistentPaths.CampaignSaves, exist_ok=True)
os.makedirs(PersistentPaths.Logs, exist_ok=True)
os.makedirs(PersistentPaths.Screenshots, exist_ok=True)
os.makedirs(PersistentPaths.CustomMaps, exist_ok=True)

KDS.Logging.init(PersistentPaths.AppData, PersistentPaths.Logs)
KDS.ConfigManager.init(PersistentPaths.AppData, PersistentPaths.Saves, PersistentPaths.CampaignSaves)
game_whole_initialization_logger: Final = KDS.Logging.ExecutionTimeLogger.debug()
game_initialization_logger: Final = KDS.Logging.ExecutionTimeLogger.debug(4 * " ")
game_whole_initialization_logger.start("Initialising Game...")

game_initialization_logger.start("Initialising Display Driver...")
if KDS.ConfigManager.GetSetting("Renderer/fullscreen", ...):
    pygame.display.toggle_fullscreen()
game_initialization_logger.stop("Display Driver initialised.")

game_initialization_logger.start("Initialising KDS modules...")
KDS.Audio.init()
KDS.Jobs.init()
KDS.AI.init()
KDS.World.init()
KDS.Missions.init()
KDS.Scores.init()
KDS.Koponen.init()
KDS.Console.init(display, display, _KDS_Quit = KDS_Quit)
KDS.School.init(display)
# more initialisations in build data loading (those initialisations need textures)
KDS.Keys.LoadCustomBindings()
game_initialization_logger.stop("KDS modules initialised.")

game_initialization_logger.start("Initialising cursors and surface arrays...")
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
game_initialization_logger.stop("Cursors and surface arrays initialised.")
#endregion
#region Loading
#region Settings
game_initialization_logger.start("Loading Settings...")
tcagr: bool = KDS.ConfigManager.GetSetting("Data/Terms/accepted", ...)
quickload: Final[bool] = KDS.ConfigManager.GetSetting("Data/quickload", ...)
allow_console_in_storymode: Final[bool] = KDS.ConfigManager.GetSetting("Data/allowConsoleInStoryMode", ...)
current_map_index: int = int(KDS.ConfigManager.GetSetting("Player/currentMap", ...)) # if it is already int, nothing will happen
maxParticles: int = KDS.ConfigManager.GetSetting("Renderer/Particle/maxCount", ...)
play_walk_sound: bool = KDS.ConfigManager.GetSetting("Mixer/walkSound", ...)
pause_on_focus_loss: bool = KDS.ConfigManager.GetSetting("Game/pauseOnFocusLoss", ...)
game_initialization_logger.stop("Settings Loaded.")
#endregion
game_initialization_logger.start("Loading Assets...")
asset_loading_logger: Final = KDS.Logging.ExecutionTimeLogger.debug(8 * " ")
pygame.event.pump()
#region Fonts
asset_loading_logger.start("Loading Fonts...")
score_font = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10)
tip_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10)
tip_font_extended = pygame.font.Font("Assets/Fonts/gamefont2_extended.ttf", 10) # mostly used in teleports
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25)
ArialFont = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", 28)
ArialTitleFont = pygame.font.Font("Assets/Fonts/Windows/arial.ttf", 72)
asset_loading_logger.stop("Font Loading Complete.")
#endregion
pygame.event.pump()
#region UI Textures
asset_loading_logger.start("Loading UI Textures...")
text_icon = pygame.image.load("Assets/Textures/Branding/textIcon.png").convert()
text_icon.set_colorkey(KDS.Colors.White)
level_cleared_icon = pygame.image.load("Assets/Textures/UI/LevelCleared.png").convert()
level_cleared_icon.set_colorkey(KDS.Colors.White)
asset_loading_logger.stop("UI Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Building Textures
asset_loading_logger.start("Loading Building Textures...")
door_open: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/door_front.png").convert()
exit_door_open: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/door_open.png").convert_alpha()
asset_loading_logger.stop("Building Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Item Textures
asset_loading_logger.start("Loading Item Textures...")
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
asset_loading_logger.stop("Item Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Menu Textures
asset_loading_logger.start("Loading Menu Textures...")
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
asset_loading_logger.stop("Menu Texture Loading Complete.")
#endregion
pygame.event.pump()
#region Audio
asset_loading_logger.start("Loading Audio Files...")
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
asset_loading_logger.stop("Audio File Loading Complete.")
#endregion
pygame.event.pump()
game_initialization_logger.stop("Asset Loading Complete.")
#endregion
#region Variable Initialisation
game_initialization_logger.start("Defining Variables...")
ambient_tint = pygame.Surface(screen_size)
black_tint = pygame.Surface(screen_size) # , SRCALPHA) I don't think we need SRCALPHA as we use BLEND_RGB_MULT on blit so the alpha would be ignored anyways
black_tint.fill((20, 20, 20))
black_tint.set_alpha(170)

remove_data_on_quit = False

main_running = True
currently_on_mission = False
current_mission = "none"
shoot = False

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

price_tip_tick: int = 0
price_tip_last_item: KDS.Build.Item | None = None

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

koponen_talk_tip = KDS.UI.KeybindFormattedText(tip_font, f"Puhu Koposelle [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

Notifications: list[KDS.UI.Notification] = []

game_initialization_logger.stop("Variable Defining Complete.")
#endregion
#region Game Settings
fall_speed: float = 0.4
fall_multiplier: float = 2.5
fall_max_velocity: float = 8.0
def LoadGameSettings():
    global fall_speed, fall_multiplier, fall_max_velocity
    fall_speed = KDS.ConfigManager.GetGameData("Physics/Player/fallSpeed")
    fall_multiplier = KDS.ConfigManager.GetGameData("Physics/Player/fallMultiplier")
    fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Player/fallMaxVelocity")

    KDS.Build.Item.fall_speed = KDS.ConfigManager.GetGameData("Physics/Items/fallSpeed")
    KDS.Build.Item.fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Items/fallMaxVelocity")
try:
    LoadGameSettings()
except:
    KDS.Logging.AutoError("Game Settings could not be loaded!")

storyLevelCount: Final[int] = KDS.ConfigManager.GetGameData("Story/levelCount")
assert(isinstance(storyLevelCount, int))
campaignOfficialLevelCount: Final[int] = KDS.ConfigManager.GetGameData("Campaign/officialLevelCount")
assert(isinstance(campaignOfficialLevelCount, int))
campaignTotalLevelCount: Final[int] = KDS.ConfigManager.GetGameData("Campaign/totalLevelCount")
assert(isinstance(campaignTotalLevelCount, int))
#endregion
#region World Data
class WorldData:
    MapSize = (0, 0)
    PlayerStartPos = (-1, -1)

    @staticmethod
    def LoadMap(MapPath: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        map_load_profiler: KDS.Logging.MapLoadingProfiler | None = None
        if KDS.Debug.Enabled:
            map_load_profiler = KDS.Logging.MapLoadingProfiler.start()

        map_whole_load_logger: Final = KDS.Logging.ExecutionTimeLogger.debug("MAP THREAD: ")
        map_load_logger: Final = KDS.Logging.ExecutionTimeLogger.debug("MAP THREAD: ")
        map_whole_load_logger.start("Loading map...")

        global Items, Tiles, Enemies, Projectiles, overlays, Player, Zones
        if not (os.path.isdir(MapPath) and os.path.isfile(os.path.join(MapPath, "level.dat")) and os.path.isfile(os.path.join(MapPath, "levelprop.kdf")) ):
            #region Error String
            KDS.Logging.AutoError(f"""##### MAP FILE ERROR #####
    Map Directory: {os.path.isdir(MapPath)}
        Level File: {os.path.isfile(os.path.join(MapPath, "level.dat"))}
        LevelProp File: {os.path.isfile(os.path.join(MapPath, "levelprop.kdf"))}
        Level Music Audio File (optional): {os.path.isfile(os.path.join(MapPath, "music.ogg"))}
        Properties File (optional): {os.path.isfile(os.path.join(MapPath, "properties.kdf"))}
        Level Background Image File (optional): {os.path.isfile(os.path.join(MapPath, "background.png"))}

        CampaignProp File (optional): {os.path.isfile(os.path.join(MapPath, "campaignprop.kdf"))}
        Campaign Preview Image File (optional): {os.path.isfile(os.path.join(MapPath, "campaign_preview.png"))}
    ##### MAP FILE ERROR #####""")
            #endregion
            KDS.System.MessageBox.Show("Map Error", "This map is currently unplayable. You can find more details in the log file.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.EXCLAMATION)
            KDS.Loading.Circle.Stop()
            return None

        map_load_logger.start("Loading Properties ...")
                        #pos,     type,      key,  value
        properties: Dict[str, Dict[str, Dict[str, Union[str, int, float, bool]]]] = {}
        if os.path.isfile(os.path.join(MapPath, "properties.kdf")):
            properties = KDS.ConfigManager.JSON.Get(os.path.join(MapPath, "properties.kdf"), KDS.ConfigManager.JSON.NULLPATH, {}, encoding="utf-8")
        map_load_logger.stop("Properties Loaded.")
        global level_background_img
        map_load_logger.start("Loading Level Background...")
        if os.path.isfile(os.path.join(MapPath, "background.png")):
            level_background_img = pygame.image.load(os.path.join(MapPath, "background.png")).convert()
        else:
            level_background_img = None
        map_load_logger.stop("Level Background Loaded." if level_background_img is not None else "Level Background Loading Skipped.")

        map_load_logger.start("Loading Map data...")
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
        map_load_logger.stop("Map data Loaded.")

        map_load_logger.start("Loading LevelProp...")
        KDS.MapProp.LevelProp.init(MapPath)
        KDS.MapProp.CampaignProp.init(MapPath)
        KDS.World.Dark.Configure(KDS.MapProp.LevelProp.Get("Rendering/Darkness/enabled", False), KDS.MapProp.LevelProp.Get("Rendering/Darkness/strength", 0))
        Player.load_levelprop()

        tmpInventory: Dict[str, int] = KDS.MapProp.LevelProp.Get("Entities/Player/Inventory", {})
        for k, v in tmpInventory.items():
            if k.isnumeric() and int(k) < len(Player.inventory) and v in KDS.Build.Item.serialNumbers:
                Player.inventory.pickupItemToIndex(int(k), KDS.Build.Item.serialNumbers[v]((0, 0), v), force=True)
            else:
                KDS.Logging.AutoError(f"Value: {v} cannot be assigned to index: {k} of Player Inventory.")
        Wallet.set_balance(KDS.Money.Euro.from_float(KDS.MapProp.LevelProp.Get("Entities/Player/walletBalance", 0)))
        KDS.Build.Item.infiniteAmmo = KDS.MapProp.LevelProp.Get("Data/infiniteAmmo", False)

        WorldData.PlayerStartPos: Tuple[int, int] = KDS.MapProp.LevelProp.Get("Entities/Player/startPos", (100, 100))
        k_start_pos: Tuple[int, int] = KDS.MapProp.LevelProp.Get("Entities/Koponen/startPos", (200, 200))
        global Koponen
        Koponen = KDS.Koponen.KoponenEntity(k_start_pos, (24, 64))
        Koponen.setEnabled(KDS.MapProp.LevelProp.Get("Entities/Koponen/enabled", False))
        Koponen.forceIdle = KDS.MapProp.LevelProp.Get("Entities/Koponen/forceIdle", False)
        Koponen.allow_talk = KDS.MapProp.LevelProp.Get("Entities/Koponen/talk", False)
        Koponen.force_talk = KDS.MapProp.LevelProp.Get("Entities/Koponen/forceTalk", False)
        Koponen.start_with_talk = KDS.MapProp.LevelProp.Get("Entities/Koponen/startWithTalk", False)
        Koponen.setListeners(KDS.MapProp.LevelProp.Get("Entities/Koponen/listeners", []))
        koponen_script = KDS.MapProp.LevelProp.Get("Entities/Koponen/lscript", [])
        if len(koponen_script) > 0:
            Koponen.loadScript(koponen_script)

        KDS.UI.Indicator.Enabled = KDS.MapProp.LevelProp.Get("Rendering/Indicator/enabled", True)
        map_load_logger.stop("LevelProp Loaded.")

        map_load_logger.start("Constructing Map...")
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
                                    if not v and value.texture != None and isinstance(value.texture, pygame.Surface): # type: ignore  Some tiles have animations as texture
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
                                elif (k == "storePrice" or k == "storeDiscountPrice") and isinstance(value, KDS.Build.Item):
                                    if isinstance(v, (int, float)):
                                        prop_euro: Final = KDS.Money.Euro.from_float(v)
                                        if k == "storePrice":
                                            value.storePrice = prop_euro
                                        else:
                                            assert(k == "storeDiscountPrice")
                                            value.storeDiscountPrice = prop_euro
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
        map_load_logger.stop("Map Constructed.")

        map_object_initialising_logger: Final = KDS.Logging.ExecutionTimeLogger.debug("MAP THREAD:     ")
        map_load_logger.start("Initialising Objects...")
        #region LateInit
        map_object_initialising_logger.start("Executing lateInit()...")
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
        map_object_initialising_logger.stop("lateInit() execution complete.")
        #endregion

        map_object_initialising_logger.start("Sorting teleport data by order...")
        for teleportData in BaseTeleport.teleportDatas.values():
            teleportData.Order()
        map_object_initialising_logger.stop("Teleport data sorting complete.")
        map_load_logger.stop("Object Initialisation Complete.")

        map_load_logger.start("Loading Music...")
        music_file_exists: Final[bool] = os.path.isfile(os.path.join(MapPath, "music.ogg"))
        if music_file_exists:
            KDS.Audio.Music.Load(os.path.join(MapPath, "music.ogg"))
        else:
            KDS.Audio.Music.Unload()
        map_load_logger.stop("Music Loaded." if music_file_exists else "Music Loading Skipped.")

        map_whole_load_logger.stop("Map loading complete.")
        KDS.Logging.debug(f"Unmeasured loading execution time: {map_whole_load_logger.accumulatedTime - map_load_logger.accumulatedTime:.3f}")

        if map_load_profiler is not None:
            map_load_profiler.stop()

        assert(not map_whole_load_logger.is_running)
        assert(not map_load_logger.is_running)
        assert(not map_object_initialising_logger.is_running)

        return WorldData.PlayerStartPos, k_start_pos
#endregion
#region Data
game_initialization_logger.start("Loading Data...")

def load_path_sounds() -> dict[str, list[pygame.mixer.Sound]]:
    path_sounds: Dict[str, List[pygame.mixer.Sound]] = {}
    default_paths = os.listdir("Assets/Audio/Tiles/path_sounds/default")
    sounds = []
    for p in default_paths:
        sounds.append(pygame.mixer.Sound(os.path.join("Assets/Audio/Tiles/path_sounds/default", p)))
    path_sounds["default"] = sounds
    #for p in path_sounds_temp:
    #    path_sounds[int(p)] = pygame.mixer.Sound(path_sounds_temp[p])

    return path_sounds

KDS.Build.init(tile_data=KDS.BuildData.load_tiles(), item_data=KDS.BuildData.load_items())
KDS.Money.init()

telep_textures: dict[int, pygame.Surface] = KDS.BuildData.load_teleports().textures
path_sounds: Final[dict[str, list[pygame.mixer.Sound]]] = load_path_sounds()

def defaultEventHandler(event: pygame.event.Event, *, ignore_quit: bool = False) -> bool:
    KDS.Keys.RegisterEvent(event)

    if event.type == QUIT:
        if ignore_quit:
            return False
        else:
            KDS_Quit(confirm=True)
            return True
    return False

class ScreenEffects:
    class Effects(IntFlag):
        Flicker = 1
        FadeInOut = 2
        Glitch = 4
        Drunk = 8

    triggered: Effects
    OnEffectFinish = KDS.Events.Event()

    class EffectData:
        class Flicker:
            repeat_rate: int
            repeat_length: int
            repeat_index: int

            @classmethod
            def reset(cls):
                cls.repeat_rate = 2
                cls.repeat_length = 12
                cls.repeat_index = 0

        class FadeInOut:
            animation: Final = KDS.Animator.Value(0.0, 255.0, 120)
            reversed: bool
            wait_index: int
            wait_length: int
            surface: Final = pygame.Surface(screen_size).convert()

            @classmethod
            def reset(cls):
                cls.animation.tick = 0
                cls.reversed = False
                cls.wait_index = 0
                cls.wait_length = 240

        class Glitch:
            # no idea what this tuple is supposed to represent...
            current_glitch: tuple[tuple[int, int, int, int], tuple[int, int]] = ((0, 0, 0, 0), (0, 0))

            @classmethod
            def reset(cls):
                cls.repeat_rate = 2
                cls.repeat_index = 0

        class Drunk:
            phase: float
            phase_speed: Final[float] = 0.05
            phase_length: Final[float] = 2 * KDS.Math.PI

            amplitude_rise: Final = KDS.Animator.Value(0.0, 10.0, 180, KDS.Animator.AnimationType.EaseOutCubic)
            amplitude_fall: Final = KDS.Animator.Value(10.0, 0.0, 540, KDS.Animator.AnimationType.EaseInCubic)

            wave_count: Final[int] = 6

            @classmethod
            def reset(cls):
                cls.phase = 0.0

                cls.amplitude_rise.tick = 0
                # cls.amplitude_rise.Finished = False
                cls.amplitude_fall.tick = 0
                # cls.amplitude_fall.Finished = False

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
    def Reset():
        ScreenEffects.triggered = ScreenEffects.Effects(0)

        ScreenEffects.EffectData.Flicker.reset()
        ScreenEffects.EffectData.FadeInOut.reset()
        ScreenEffects.EffectData.Glitch.reset()
        ScreenEffects.EffectData.Drunk.reset()

ScreenEffects.Reset()

#region Animations
animation_loading_logger: Final = KDS.Logging.ExecutionTimeLogger.debug(8 * " ")
animation_loading_logger.start("Loading Animations...")

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

animation_loading_logger.stop("Animation Loading Complete.")
#endregion
game_initialization_logger.stop("Data Loading Complete.")
#endregion
#region Tiles
game_initialization_logger.start("Loading Tiles...")
class Toilet(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int, _burning=False):
        super().__init__(position, serialNumber)
        self.burning = _burning
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

# def _load_jukebox_songs() -> list[pygame.mixer.Sound]:
#     musikerna = os.listdir("Assets/Audio/JukeboxMusic/")
#     # songs = []
#     # for musiken in musikerna:
#     #     songs.append(pygame.mixer.Sound("Assets/Audio/JukeboxMusic/" + musiken))
#     # random.shuffle(songs)
#     # This feels useless as we access songs randomly anyways...

#     return songs
def _load_jukebox_songs() -> tuple[str, ...]:
    DIRNAME: str = "Assets/Audio/JukeboxMusic"
    musikerna = os.listdir(DIRNAME)
    return tuple(os.path.join(DIRNAME, m) for m in musikerna)

class Jukebox(KDS.Build.Tile):
    PARTICLE_RATE: int = 15 # try place every 15 ticks (0,25 seconds)
    MIN_PARTICLE_RATE: int = 120 # force place every 150 ticks (2 seconds)

    songs: Final[tuple[str, ...]] = _load_jukebox_songs()

    tooltip1 = KDS.UI.KeybindFormattedText(tip_font, f"Use Jukebox [Click: {{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    tooltip2 = KDS.UI.KeybindFormattedText(tip_font, f"Stop Jukebox [Hold: {{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    # jukebox_tip: pygame.Surface = pygame.Surface((max(tooltip1.get_width(), tooltip2.get_width()), tooltip1.get_height() + tooltip2.get_height()), SRCALPHA)
    # jukebox_tip.blit(tooltip1, ((tooltip2.get_width() - tooltip1.get_width()) / 2, 0))
    # jukebox_tip.blit(tooltip2, ((tooltip1.get_width() - tooltip2.get_width()) / 2, tooltip1.get_height()))
    # del tooltip1, tooltip2

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.checkCollision = False

        self.lastPlayed = [-69 for _ in range(5)]

        self.playing_index: int = -1
        self.playing: KDS.Audio.MusicOverrideHandle | None = None

        self.particle_counter: int = 0
        self.last_particle_counter: int = 0
        self.last_particle_offset: int | None = None

    def stopPlayingTrack(self):
        if self.playing is not None:
            self.playing.Stop()
            self.playing = None

    def playRandomTrack(self):
        if self.playing is not None:
            self.stopPlayingTrack()
            assert(self.playing is None)

        loopStopper = 0
        while (self.playing_index in self.lastPlayed or self.playing_index == -1) and loopStopper < 10:
            self.playing_index = random.randint(0, len(Jukebox.songs) - 1) # randint end is inclusive
            loopStopper += 1

        self.lastPlayed.pop(0)
        self.lastPlayed.append(self.playing_index)

        self.playing = KDS.Audio.Music.Override(Jukebox.songs[self.playing_index], loop=False)

    def update(self):
        if self.rect.colliderect(Player.rect):
            # screen.blit(Jukebox.jukebox_tip, (self.rect.centerx - scroll[0] - Jukebox.jukebox_tip.get_width() / 2, self.rect.y - scroll[1] - 30))

            tooltip1: pygame.Surface = Jukebox.tooltip1.get_surface()
            tooltip1_pos: tuple[int, int] = (self.rect.centerx - scroll[0] - round(tooltip1.get_width() / 2), self.rect.y - scroll[1] - 30)
            tooltip2: pygame.Surface = Jukebox.tooltip2.get_surface()
            tooltip2_pos: tuple[int, int] = (self.rect.centerx - scroll[0] - round(tooltip2.get_width() / 2), tooltip1_pos[1] + tip_font.get_height())

            screen.blit(tooltip1, tooltip1_pos)
            screen.blit(tooltip2, tooltip2_pos)

            if KDS.Keys.functionKey.clicked and not KDS.Keys.functionKey.holdClicked:
                self.stopPlayingTrack()
                self.playRandomTrack()
            elif KDS.Keys.functionKey.held:
                self.stopPlayingTrack()
        if self.playing is not None:
            assert(KDS.Audio.Music.Overridden is self.playing)
            if not KDS.Audio.Music.GetPlaying():
                self.playRandomTrack()

            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 600 # Bigger value means volume gets smaller at a smaller rate
            jukebox_volume = KDS.Math.Clamp01(KDS.Math.Lerp(1.5, 0, lerp_multiplier))
            self.playing.SetLocalVolume(jukebox_volume)

            # if check is useless, light isn't rendered if dark is disabled.
            # if KDS.World.Dark.enabled:
            Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(100, 1000), True))

            self.last_particle_counter += 1
            if self.last_particle_counter > Jukebox.MIN_PARTICLE_RATE:
                self.last_particle_offset = None

            self.particle_counter += 1
            if self.particle_counter > Jukebox.PARTICLE_RATE:
                self.particle_counter = 0

                PARTICLE_SIZE: int = KDS.World.Lighting.NoteParticle.SIZE
                particle_offset: int = random.randint(-PARTICLE_SIZE, PARTICLE_SIZE)

                if self.last_particle_offset is None or abs(self.last_particle_offset - particle_offset) > PARTICLE_SIZE:
                    self.last_particle_offset = particle_offset
                    self.last_particle_counter = 0

                    particle_x: int = self.rect.centerx + particle_offset - KDS.World.Lighting.NoteParticle.HALF_SIZE
                    particle_y: int = self.rect.top - KDS.World.Lighting.NoteParticle.HALF_SIZE

                    Particles.append(KDS.World.Lighting.NoteParticle((particle_x, particle_y), angleDeg=random.randint(-15, 15)))

        return self.texture

class Door(KDS.Build.Tile):
    key_names: dict[int, str] = {
        24: "red",
        25: "blue",
        26: "green"
    }
    key_colors: dict[int, tuple[int, int, int]] = {
        24: (237, 28, 36),
        25: (63, 72, 204),
        26: (34, 177, 76),
    }

    def __init__(self, position: Tuple[int, int], serialNumber: int, closingCounter = -1):
        super().__init__(position, serialNumber)
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
            if self.serialNumber == 23 or Player.keys[Door.key_names[self.serialNumber]]:
                KDS.Audio.PlaySound(door_opening)
                self.closingCounter = 0
                self.open = not self.open
                if not self.open:
                    # Use direction to offset the player center
                    # this way we can prefer to push the player backwards (face towards the door)
                    player_ref: int = Player.rect.centerx - ((Player.rect.width // 8) * KDS.Convert.ToMultiplier(Player.direction))
                    if self.rect.centerx >= player_ref: # use >= instead of > because centerx might get rounded down and be biased towards the left
                        Player.rect.right = self.rect.left
                    else:
                        Player.rect.left = self.rect.right
            else:
                KDS.Audio.PlaySound(door_locked)
                Notifications.append(KDS.UI.Notification(f"Missing {Door.key_names[self.serialNumber]} key", color=Door.key_colors[self.serialNumber]))
                KDS.Missions.Listeners.KeyDoorLocked.Trigger()

        return self.texture if not self.open else self.opentexture

class Landmine(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
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
        assert(self.texture is not None)
        assert(self.texture_size is not None)
        self.rect = pygame.Rect(position[0] + round(17 - self.texture_size[0] / 2), position[1] + round(17 - self.texture_size[1] / 2), self.texture_size[0], self.texture_size[1])
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
        self.rect = pygame.Rect(position[0], position[1], 14, 21)
        self.checkCollision = True
        self.coneheight = 90

    def lateInit(self):
        global Tiles
        y = 0
        r = True
        while r:
            y += 34
            # BRUH THIS CHECKS THE ENTIRE MAP WTFFFFF
            # for row in Tiles:
            #     for unit in row:
            #         for tile in unit:
            #             if tile.rect.collidepoint() and tile.serialNumber != 22 and tile.checkCollision:
            #                 y = y - (self.rect.bottom + y - tile.rect.y) + 5
            #                 r = False

            # NOTE: This collision check does not do any overscan
            # problems might arise with big collidable objects like Molok.
            check_pos: tuple[int, int] = (self.rect.centerx, self.rect.bottom + y)
            grid_pos: tuple[int, int] = (int(check_pos[0] / 34), int(check_pos[1] / 34))
            for tile in Tiles[grid_pos[1]][grid_pos[0]]:
                if tile.rect.collidepoint(check_pos) and tile.serialNumber != 22 and tile.checkCollision:
                    y = y - (self.rect.bottom + y - tile.rect.y) + 5
                    r = False

            if y > 154:
                r = False
        self.coneheight = y

    def update(self):
        if random.randint(0, 10) != 10:
            btmidth: int = int(self.coneheight * 80 / 90)
            light_shape: pygame.Surface = KDS.World.Lighting.lamp_cone(10, btmidth, self.coneheight, (200, 200, 200))
            Lights.append(KDS.World.Lighting.Light((self.rect.centerx - light_shape.get_width() // 2 - 1, self.rect.y + 18), light_shape))
        return self.texture

class LampChain(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0] + 6, position[1], 1, 34)
        self.checkCollision = True

    def update(self):
        return self.texture

class DecorativeHead(KDS.Build.Tile):
    decorative_head_tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Activate Head [Hold: {{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1]-26, 28, 60)
        self.checkCollision = False
        self.praying = False
        self.prayed = False

    def update(self):
        if self.rect.colliderect(Player.rect):
            if not self.prayed:
                decorative_head_tip: pygame.Surface = DecorativeHead.decorative_head_tip.get_surface()
                screen.blit(decorative_head_tip, (self.rect.centerx - scroll[0] - decorative_head_tip.get_width() // 2, self.rect.top - scroll[1] - 20))
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
                if Player.health > 0 and Player.health < 100:
                    # check < 100 so that we don't remove any health if health is above 100
                    Player.health = min(Player.health + 0.01, 100)
        else:
            pray_sound.stop()
            self.praying = False

        if self.prayed:
            if KDS.World.Dark.GetEnabled():
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 1900), True))
            else:
                day_light = KDS.World.Lighting.Shapes.circle.get(150, 1900).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - day_light.get_width() // 2, self.rect.centery - scroll[1] - day_light.get_height() // 2))
        return self.texture

class Tree(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1]-50, 47, 84)
        self.checkCollision = False

    def update(self):
        return self.texture

class Rock0(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1]+19, 32, 15)
        self.checkCollision = True

    def update(self):
        return self.texture

class Torch(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("tall_torch_burning", 4, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
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
        return self.animation.update()

class GoryHead(KDS.Build.Tile):
    blh: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/bloody_h.png").convert()
    blh.set_colorkey(KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
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
    level_ender_tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Finish level [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0], position[1] - 16, 34, 50)
        self.checkCollision = False

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.top + 10), KDS.World.Lighting.Shapes.circle.get(40, 40000), True))
        if self.rect.colliderect(Player.rect):
            level_ender_tip: pygame.Surface = LevelEnder.level_ender_tip.get_surface()
            screen.blit(level_ender_tip, (self.rect.centerx - level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                KDS.Missions.Listeners.LevelEnder.Trigger()
        return self.texture

class LevelEnderDoor(KDS.Build.Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.opentexture = exit_door_open
        self.rect = pygame.Rect(position[0], position[1] - 34, 34, 68)
        self.checkCollision = False
        self.opened = False
        self.propOpen = False
        self.interactable: bool = True
        self.showTip = False

    def update(self):
        if self.rect.colliderect(Player.rect) or self.propOpen:
            if self.showTip:
                level_ender_tip: pygame.Surface = LevelEnder.level_ender_tip.get_surface()
                screen.blit(level_ender_tip, (self.rect.centerx - level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
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
        self.animation = KDS.Animator.Animation("candle_burning", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0], position[1]+14, 20, 20)
        self.checkCollision = False
        self.light_scale = 40

    def update(self):
        if random.randint(0, 5) == 5:
            self.light_scale = random.randint(20, 60)
        if random.randint(0, 50) == 0:
            Particles.append(KDS.World.Lighting.Fireparticle((self.rect.centerx - 3, self.rect.y), random.randint(3, 6), 20, 0.01))
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - self.light_scale // 2, self.rect.y - self.light_scale // 2), KDS.World.Lighting.Shapes.circle.get(self.light_scale, 2000)))
        return self.animation.update()

class LampPoleLamp(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0]-6, position[1]-6, 40, 40)
        self.checkCollision = False

    def update(self):
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5000), True))
        return self.texture

class Chair(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0]-6, position[1]-8, 40, 42)
        self.checkCollision = False

    def update(self):
        return self.texture

class SkullTile(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0]+7, position[1]+7, 27, 27)
        self.checkCollision = False

    def update(self):
        return self.texture

class WallLight(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.direction: bool = serialNumber == 72
        self.light_t: pygame.Surface = pygame.transform.flip(KDS.World.Lighting.Shapes.cone_hard.get(100, 6200), self.direction, False)

    def lateInit(self) -> None:
        assert(self.checkCollision == False)
        self.darkOverlay = None

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - (17 * KDS.Convert.ToMultiplier(self.direction)), self.rect.centery), self.light_t, True))
        return self.texture

class WallLightVertical(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.direction: bool = serialNumber == 180
        self.light_t: pygame.Surface = pygame.transform.flip(KDS.World.Lighting.Shapes.cone_hard_up.get(100, 6200), False, self.direction)

    def lateInit(self) -> None:
        assert(self.checkCollision == False)
        self.darkOverlay = None

    def update(self) -> pygame.Surface | None:
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.centery + (17 * KDS.Convert.ToMultiplier(self.direction))), self.light_t, positionFromCenter=True))
        return self.texture

class RespawnAnchor(KDS.Build.Tile):
    respawn_anchor_on: pygame.Surface = pygame.image.load("Assets/Textures/Tiles/respawn_anchor_on.png").convert()

    active: Optional[RespawnAnchor] = None
    rspP_list = []
    respawn_anchor_tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Set Respawn Point [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.ontexture = RespawnAnchor.respawn_anchor_on
        self.checkCollision = False
        RespawnAnchor.rspP_list.append(self)

    def update(self):
        if RespawnAnchor.active is self:
            if KDS.World.Dark.GetEnabled():
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 2400), True))
            else:
                day_light = KDS.World.Lighting.Shapes.circle.get(150, 2400).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - day_light.get_width() // 2, self.rect.centery - scroll[1] - day_light.get_height() // 2))
            return self.ontexture

        if self.rect.colliderect(Player.rect):
            respawn_anchor_tip: pygame.Surface = RespawnAnchor.respawn_anchor_tip.get_surface()
            screen.blit(respawn_anchor_tip, (self.rect.centerx - scroll[0] - respawn_anchor_tip.get_width() // 2, self.rect.top - scroll[1] - 50))
            if KDS.Keys.functionKey.clicked:
                RespawnAnchor.active = self
                KDS.Audio.PlaySound(random.choice(respawn_anchor_sounds))
        return self.texture

class Spruce(KDS.Build.Tile):
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.rect = pygame.Rect(position[0] - 10, position[1] - 40, 63, 75)
        self.checkCollision = False

    def update(self):
        return self.texture

class AllahmasSpruce(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
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

        return None

class ImpaledBody(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("impaled_corpse", 2, 50, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0] - (self.animation.get_width() - 34), position[1] - (self.animation.get_height() - 34), self.animation.get_width(), self.animation.get_height())
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

    def lateInit(self):
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        return self.texture

class RoofPlanks(KDS.Build.Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        w, h = self.texture_size
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
                level_ender_tip: pygame.Surface = LevelEnder.level_ender_tip.get_surface()
                screen.blit(level_ender_tip, (self.rect.centerx - level_ender_tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
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
    tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Toggle Sleep [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

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
            tip: pygame.Surface = Sleepable.tip.get_surface()
            screen.blit(tip, (self.rect.centerx - tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
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

        return None

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
    tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Matkusta bussilla [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

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
            tip: pygame.Surface = Nysse.tip.get_surface()
            screen.blit(tip, (self.rect.centerx - tip.get_width() // 2 - scroll[0], self.rect.y - 5 - tip.get_height() - scroll[1]))
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
    tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font_extended, f"Väitä pesseesi kädet [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

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
            self.renderedMessage = tip_font_extended.render(self.message, True, KDS.Colors.White)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            tip: pygame.Surface | None = PistokoeDoor.tip.get_surface() if not self.used else None
            if self.renderedMessage != None:
                screen.blit(self.renderedMessage, (self.rect.centerx - self.renderedMessage.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1] - ((tip.get_height() + 5) if tip is not None else 0)))
            if tip is not None:
                screen.blit(tip, (self.rect.centerx - tip.get_width() // 2 - scroll[0], self.rect.centery - 50 - scroll[1]))

            if KDS.Keys.functionKey.clicked and not self.used:
                KDS.Missions.SetProgress("story_exam", "go_to_class", 1.0)
                KDS.Audio.Music.Pause()
                quit_temp, exam_grade = KDS.School.Exam()
                KDS.Audio.Music.Unpause()
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
    class ItemAnimation:
        def __init__(self, item: KDS.Build.Item, item_rect: pygame.Rect) -> None:
            assert(item_rect is item.rect)
            self.expected_rect: pygame.Rect = item_rect.copy()
            self.item: KDS.Build.Item = item

    class PriceAnimation:
        RAW_PRICE_TICKS: Final[int] = 180
        PRICE_UPDATING_TICKS: Final[int] = 15

        def __init__(self) -> None:
            self.reset()

        def update(self) -> None:
            self._tick += 1

            # le = less or equal
            show_price_le: int = CashRegister.PriceAnimation.RAW_PRICE_TICKS
            hide_price_le: int = CashRegister.PriceAnimation.RAW_PRICE_TICKS + CashRegister.PriceAnimation.PRICE_UPDATING_TICKS

            if self._tick <= show_price_le:
                self.show_price = True
                self.show_rounded_price = False
            elif self._tick <= hide_price_le:
                self.show_price = False
                self.show_rounded_price = False
            else:
                self._tick = hide_price_le + 1
                self.show_price = True
                self.show_rounded_price = True

        def reset(self):
            self._tick: int = 0
            self._payment_given: bool = False

            self.show_price: bool = True
            self.show_rounded_price: bool = False

        def ss_bonuscard_shown(self) -> None:
            if not self._payment_given and self._tick < CashRegister.PriceAnimation.RAW_PRICE_TICKS:
                self.reset()

        def any_payment_given(self) -> None:
            if not self._payment_given and self._tick < CashRegister.PriceAnimation.RAW_PRICE_TICKS:
                self._tick = CashRegister.PriceAnimation.RAW_PRICE_TICKS
            self._payment_given = True

    dropItemTip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Aseta ostos [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    ssCardTip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Nayta SS-Etukortti [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    sound: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Tiles/cashregister_new.opus")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("cashRegister", 2, 40, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

        self.items_animating: List[CashRegister.ItemAnimation] = []
        self.cost_render: tuple[str, pygame.Surface] | None = None
        self.dropItemsRect: pygame.Rect = pygame.Rect(124 + self.rect.x, 0 + self.rect.y, 80, 102)
        self.payRect: pygame.Rect = pygame.Rect(57 + self.rect.x, 0 + self.rect.y, 41, 102)
        self.itemsBottomTarget: int = 74 + self.rect.y
        self.itemsLeftMoveRange: Tuple[int, int] = (45 + self.rect.x, 4 + self.rect.x)
        self.itemsMoveSpeed: int = 1

        self.ssBonuscardShown: bool
        self.items_cost: KDS.Money.Euro
        self.discount_items_cost: KDS.Money.Euro
        self.items: list[KDS.Build.Item] = []
        self.price_animation: Final = CashRegister.PriceAnimation()
        self._reset()

    @property
    def RawCost(self) -> KDS.Money.Euro:
        if not self.ssBonuscardShown:
            return self.items_cost
        else:
            return self.discount_items_cost

    @property
    def RoundedCost(self) -> KDS.Money.Euro:
        return round(self.RawCost)

    def lateInit(self) -> None:
        self.darkOverlay = None

    def update(self) -> Optional[pygame.Surface]:
        # Removed so that the user can pay after picking up the item
        # toRm: List[KDS.Build.Item] = []
        # for item in self.items:
        #     if item not in self.itemIndexes or self.itemIndexes[item] >= len(Items) or Items[self.itemIndexes[item]] is not item:
        #         if item in Items:
        #             self.itemIndexes[item] = Items.index(item) # Index saved, because checking if Item exists would rape the FPS so hard that Python would commit suicide
        #         else:
        #             # Removed as it is not clear what triggered the shoplifting now
        #             # as TheftDetectors have been fixed and the alarm sounds only when passing the detector
        #             # KDS.Missions.Listeners.Shoplifting.Trigger()
        #             toRm.append(item)

        # for item in toRm:
        #     self.items.remove(item)

        # fix for animation still running after item pickup
        # as we removed the toRm function
        stop_animate: list[CashRegister.ItemAnimation] = []
        for animate_item in self.items_animating: # It is possible to re-enable the animation if the item is put on the exactly correct spot, but I'm not too worried about that very rare case
            if animate_item.expected_rect != animate_item.item.rect:
                stop_animate.append(animate_item)
            else: # only animate if item is exactly where we expect it to be
                animate_distance: int = animate_item.expected_rect.left - self.itemsLeftMoveRange[1] # do not overshoot
                animate_move: int = min(self.itemsMoveSpeed, animate_distance) # animation move amount
                animate_item.expected_rect.left -= animate_move
                animate_item.item.rect.left -= animate_move
                assert(animate_item.expected_rect.left == animate_item.item.rect.left)

        for stop_animate_item in stop_animate:
            self.items_animating.remove(stop_animate_item)

        # TODO: Implement item removal

        # removed as we handle this in a separate list now
        # for item in self.items: # Maybe don't need this one, but I still put it just in case
        #     if item.rect.left > self.itemsLeftMoveRange[1]:
        #         item.rect.left += self.itemsMoveSpeed

        if self.payRect.colliderect(Player.rect):
            hndItm = Player.inventory.getHandItem()
            if isinstance(hndItm, Wallet) and self.RoundedCost > 0:
                handEuro: KDS.Money.Euro | None = hndItm.get_hand_euro()
                if handEuro is not None:
                    payTip: pygame.Surface = tip_font.render(f"Maksa {str(handEuro)} euroa [{KDS.UI.KeybindFormattedText.get_binding_text(KDS.Keys.functionKey.get_primary_binding())}]", True, KDS.Colors.White)
                    screen.blit(payTip, (self.payRect.centerx - payTip.get_width() // 2 - scroll[0], self.payRect.y - 10 - scroll[1]))
                    if KDS.Keys.functionKey.clicked:
                        _ = self._try_pay_from_wallet()
            elif isinstance(hndItm, SSBonuscard):
                ssCardTip = CashRegister.ssCardTip.get_surface()
                screen.blit(ssCardTip, (self.payRect.centerx - ssCardTip.get_width() // 2 - scroll[0], self.payRect.y - 10 - scroll[1]))
                if KDS.Keys.functionKey.clicked:
                    self.ssBonuscardShown = True
                    self.purchaseStateUpdate()
                    self.price_animation.ss_bonuscard_shown()
        elif self.dropItemsRect.colliderect(Player.rect):
            hndItm = Player.inventory.getHandItem()
            if isinstance(hndItm, KDS.Build.Item) and hndItm.storePrice != None:
                dropItemTip = CashRegister.dropItemTip.get_surface()
                screen.blit(dropItemTip, (self.dropItemsRect.centerx - dropItemTip.get_width() // 2 - scroll[0], self.dropItemsRect.y + 20 - scroll[1]))
                if KDS.Keys.functionKey.clicked:
                    drpd = Player.inventory.dropItem()
                    if drpd != None:
                        if self.addItem(drpd):
                            KDS.Audio.PlaySound(CashRegister.sound)
                            self.price_animation.reset()
                        else:
                            Player.inventory.pickupItem(drpd)

        if len(self.items) > 0:
            self.price_animation.update()

        cost_txt: str = str(self.RoundedCost if self.price_animation.show_rounded_price else self.RawCost)
        if self.cost_render is None or self.cost_render[0] != cost_txt:
            cost_render: pygame.Surface = tip_font.render(cost_txt, True, KDS.Colors.Green)
            self.cost_render = (cost_txt, cost_render)

        screen.blit(self.animation.update(), (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        if self.price_animation.show_price:
            screen.blit(self.cost_render[1], (self.rect.x - scroll[0] + 109 - int(self.cost_render[1].get_width() / 2), self.rect.y - scroll[1] + 56))

        return None

    def _try_pay_from_wallet(self) -> bool:
        paid: KDS.Money.Euro | None = Wallet.try_pay()
        if paid is None:
            return False

        self.price_animation.any_payment_given()

        self.items_cost -= paid
        self.discount_items_cost -= paid

        self.purchaseStateUpdate()
        return True

    def purchaseStateUpdate(self):
        if self.RoundedCost <= 0:
            self._finish_transaction()

    def _finish_transaction(self):
        for item in self.items:
            item.storePrice = None
            item.storeDiscountPrice = None
            KDS.Missions.Listeners.ItemPurchase.Trigger(item.serialNumber)

        Wallet.add_balance(-self.RoundedCost) # palautettava vaihtoraha
        self._reset()

    def _reset(self) -> None:
        self.items.clear()

        self.ssBonuscardShown = False
        self.items_cost = KDS.Money.Euro.zero()
        self.discount_items_cost = KDS.Money.Euro.zero()

        self.price_animation.reset()

    def addItem(self, item: KDS.Build.Item) -> bool:
        global Items
        if item.storePrice is None:
            return False

        item.rect.bottomleft = (self.itemsLeftMoveRange[0], self.itemsBottomTarget)

        existing_animations: tuple[CashRegister.ItemAnimation, ...] = tuple(KDS.Linq.Where(self.items_animating, lambda ia: item is ia.item))
        for ea in existing_animations:
            self.items_animating.remove(ea)
        self.items_animating.append(CashRegister.ItemAnimation(item, item.rect))

        if item not in self.items:
            self.items.append(item)
            self.items_cost += item.storePrice
            self.discount_items_cost += item.storeDiscountPrice if item.storeDiscountPrice != None else item.storePrice
            self.purchaseStateUpdate()

        Items.append(item)
        return True

class TheftDetector(KDS.Build.Tile):
    alarmTicks: int = 0
    alarmWaitTicks: Final[int] = 180

    theftDetectorSoundIsPlaying: bool = False
    theftDetectorSound: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Tiles/theft_detector.ogg")
    theftDetectorSound.set_volume(0.5)

    @staticmethod
    def globalUpdate() -> None:
        TheftDetector.alarmTicks -= 1
        if not TheftDetector.get_running():
            TheftDetector.theftDetectorSound.stop()
            TheftDetector.theftDetectorSoundIsPlaying = False
            TheftDetector.alarmTicks = 0

    @staticmethod
    def globalReset() -> None:
        TheftDetector.alarmTicks = 0
        TheftDetector.globalUpdate()

    @staticmethod
    def get_running() -> bool:
        return TheftDetector.alarmTicks > 0

    @staticmethod
    def _shoplifting() -> None:
        if not TheftDetector.theftDetectorSoundIsPlaying:
            TheftDetector.theftDetectorSoundIsPlaying = True
            KDS.Audio.PlaySound(TheftDetector.theftDetectorSound, loops=-1)

        TheftDetector.alarmTicks = TheftDetector.alarmWaitTicks
        KDS.Missions.Listeners.Shoplifting.Trigger()

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("theft_detector", 2, 15, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, alpha=True)

    def lateInit(self) -> None:
        self.darkOverlay = None

        top: int = self.rect.top
        height: int = self.rect.height

        center: int = self.rect.centerx
        width: float = self.rect.width / 2

        self.detection_rect: pygame.Rect = pygame.Rect(center - (width / 2), top, width, height)

    def update(self) -> Optional[pygame.Surface]:
        if self.detection_rect.colliderect(Player.rect):
            for item in Player.inventory:
                if item != None and item.storePrice != None:
                    TheftDetector._shoplifting()
                    break

        if TheftDetector.get_running():
            return self.animation.update()
        else:
            self.animation.tick = 0
            return self.texture

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
        # self.setDark: Optional[int] = None
        # Didn't seem like it was being used
        # and I didn't like that it reset the darkness on every teleport

        super().__init__(position, serialNumber, textureLookupOverride=telep_textures)
        self.texture = telep_textures[self.serialNumber]
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
            self.renderedMessage = tip_font_extended.render(self.message, True, KDS.Colors.White)
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
        # if self.setDark != None:
        #     KDS.World.Dark.Set(True, self.setDark)
        # else:
        #     KDS.World.Dark.Reset()
        # Triggering Listener
        KDS.Missions.Listeners.Teleport.Trigger()

    def onTeleport(self):
        pass

class InvisibleTeleport(BaseTeleport):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.lastCollision: bool = False

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

    tip_render: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Use Keycard [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    acceptSound = pygame.mixer.Sound("Assets/Audio/Tiles/hotel_door_accept.ogg")

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.resetStateTimer = 0
        self.state = HotelDoor.DoorState.Default
        self.allowEnterWithoutKeycard = False
        self.lightPos = (self.rect.x + 26, self.rect.y + 25)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            self.messageOffset = (0, -50)

            allowEnter: bool = bool(self.allowEnterWithoutKeycard)
            if isinstance(Player.inventory.getHandItem(), HotelKeycard):
                allowEnter = True

                self.messageOffset = (0, -50 - tip_font_extended.get_height() - 5)
                messageSize = self.renderedMessage.get_size() if self.renderedMessage != None else (0, 0)
                normalMessagePos = (self.rect.centerx - messageSize[0] // 2 - scroll[0] + self.messageOffset[0], self.rect.centery - messageSize[1] // 2 - scroll[1] + self.messageOffset[1])

                tip_render: pygame.Surface = HotelDoor.tip_render.get_surface()
                screen.blit(tip_render, (self.rect.centerx - tip_render.get_width() // 2 - scroll[0], normalMessagePos[1] + messageSize[1] + 5))

            if allowEnter and KDS.Keys.functionKey.clicked:
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
    MUFFLED_VOLUME_MIN: Final[float] = 0.30
    MUFFLED_VOLUME_MAX: Final[float] = 0.75

    tip_render: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Knock [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
    alt_tip_render: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Enter [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

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
        self.song_muffled.set_volume(HotelGuardDoor.MUFFLED_VOLUME_MIN)
        e = KDS.NPC.DoorGuardNPC((self.rect.right, self.rect.top + 34))
        e.enabled = False
        self.entity = e
        global Entities
        Entities.append(e)

        self.messageOffset = (0, -50 - tip_font_extended.get_height() - 5)

    def lateInit(self):
        super().lateInit()
        KDS.Audio.PlaySound(self.song, loops=-1)
        KDS.Audio.PlaySound(self.song_muffled, loops=-1)

    def update(self) -> Optional[pygame.Surface]:
        if self.rect.colliderect(Player.rect):
            self.renderMessage()

            messageSize = self.renderedMessage.get_size() if self.renderedMessage != None else (0, 0)
            normalMessagePos = (self.rect.centerx - messageSize[0] // 2 - scroll[0] + self.messageOffset[0], self.rect.centery - messageSize[1] // 2 - scroll[1] + self.messageOffset[1])

            tip_render: pygame.Surface | None = None
            if not self.open:
                tip_render = HotelGuardDoor.tip_render.get_surface()
            elif self.entity.health <= 0:
                tip_render = HotelGuardDoor.alt_tip_render.get_surface()

            if tip_render is not None:
                screen.blit(tip_render, (self.rect.centerx - tip_render.get_width() // 2 - scroll[0], normalMessagePos[1] + messageSize[1] + 5))

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
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 300 # Bigger value means volume gets smaller at a smaller rate
            muffled_volume = KDS.Math.Lerp(HotelGuardDoor.MUFFLED_VOLUME_MAX, HotelGuardDoor.MUFFLED_VOLUME_MIN, lerp_multiplier)
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
        self.rect = pygame.Rect(position[0], position[1] - self.texture_size[1] + 34, self.texture_size[0], self.texture_size[1])
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
            tip: pygame.Surface = Nysse.tip.get_surface()
            screen.blit(tip, (self.rect.centerx - tip.get_width() // 2 - scroll[0], self.rect.y - 5 - tip.get_height() - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                self.teleport()
        return self.texture

class HologramTeleport(BaseTeleport):
    tip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Teleport [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)
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
            tip: pygame.Surface = HologramTeleport.tip.get_surface()
            screen.blit(tip, (self.rect.centerx - tip.get_width() // 2 - scroll[0], self.rect.y - 45 - scroll[1]))
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
    169: TheftDetector,
    179: WallLightVertical,
    180: WallLightVertical
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

game_initialization_logger.stop("Tile Loading Complete.")
#endregion
#region Items
game_initialization_logger.start("Loading Items...")
itemTip: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Nosta Esine [{{binding:{KDS.Keys.functionKey.name}}}]", True, KDS.Colors.White)

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
        self.try_give_pickup_score(6)
        KDS.Audio.PlaySound(coffeemug_sound)

class Gasburner(KDS.Build.Item):
    burning = False
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.sound = False

    def use(self):
        if KDS.Keys.actionKey.pressed:
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
        self.try_give_pickup_score(12)
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
            # HACK: Reassign Final variable to restore original iPuhelin behaviour with the new texture rendering behaviour.
            self.texture = iPuhelin.realistic_texture # type: ignore
        return self.texture

    def pickup(self) -> None:
        KDS.Scores.score -= 6 # first iPuhelin was released on June
        KDS.Audio.PlaySound(item_pickup)

    def drop(self) -> bool:
        KDS.Scores.score += 6
        return True

class Knife(KDS.Build.Weapon):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(40, KDS.Math.INFINITY, knife_animation_object, None, allowHold=True)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 13 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 1, 1), holderData.direction, -1, Tiles, 10, maxDistance=40))
        return output

    def use(self) -> pygame.Surface:
        self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))
        if KDS.Keys.actionKey.pressed:
            return knife_animation_object.update()
        else:
            knife_animation_object.tick = 0
            return self.texture

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(5)
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
            if KDS.Keys.actionKey.held:
                TileFire.createInstanceAtPosition(pos)
        return self.texture

    def pickup(self) -> None:
        self.try_give_pickup_score(14)
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
        self.try_give_pickup_score(18)
        KDS.Audio.PlaySound(weapon_pickup)

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 30 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 25))
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
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 50 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 6))
        return output


    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(29)
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
                Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 60 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 6, maxDistance=1400, slope=(5 - x) / 20))
        return output

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(23)
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
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx - asset_offset, holderData.rect.y + 13, 2, 2), holderData.direction, 27, Tiles, 5, plasma_ammo, 2000, random.randint(-1, 1) / 27))
        return output

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(35)
        KDS.Audio.PlaySound(weapon_pickup)

class Soulsphere(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def pickup(self) -> None:
        self.try_give_pickup_score(20)
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
        self.try_give_pickup_score(30)
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
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 60 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, 3, slope=random.uniform(-0.5, 0.5) / 5))
        return output

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(15)

class Awm(KDS.Build.Weapon):
    AimOffset: int = 0

    @staticmethod
    def globalUpdate(isHandItem: bool):
        if not isHandItem:
            Awm.AimOffset = 0
        elif Player.movement[0] != 0 or not Player.is_grounded or Player.crouching:
            Awm.AimOffset = 0
        else:
            if KDS.Keys.aim.onDown:
                if Awm.AimOffset == 0:
                    Awm.AimOffset = 250
                else:
                    Awm.AimOffset = 0

    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(130, 5, awm_f_texture, awm_shot)

    def use(self) -> pygame.Surface:
        return self.internalUse(KDS.Build.Weapon.WeaponHolderData.fromPlayer(Player))

    def shoot(self, holderData: KDS.Build.Weapon.WeaponHolderData) -> bool:
        output = super().shoot(holderData)
        if output:
            Lights.append(KDS.World.Lighting.Light(holderData.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(holderData.rect.centerx + 90 * KDS.Convert.ToMultiplier(holderData.direction), holderData.rect.y + 13, 2, 2), holderData.direction, -1, Tiles, random.randint(125, 150), slope=0))
        return output

    def pickup(self) -> None:
        super().pickup()
        self.try_give_pickup_score(25)

class AwmMag(KDS.Build.Ammo):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.internalInit(Awm, 5, 10, item_pickup)

class EmptyFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, *, give_pickup_score: bool = True):
        super().__init__(position, serialNumber)

        # so that flasks that have been drank don't give pickup score again
        self.give_score: bool = give_pickup_score

    def use(self):
        return self.texture

    def pickup(self) -> None:
        if self.give_score:
            self.try_give_pickup_score(1)
        KDS.Audio.PlaySound(coffeemug_sound)

class MethFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.actionKey.pressed:
            KDS.Scores.score += 1
            Player.health += random.choice([random.randint(10, 30), random.randint(-30, 30)])
            Player.inventory.pickupItem(EmptyFlask((0, 0), 26, give_pickup_score=False), force=True)
            KDS.Audio.PlaySound(glug_sound)
        return self.texture

    def pickup(self) -> None:
        self.try_give_pickup_score(10)
        KDS.Audio.PlaySound(coffeemug_sound)

class BloodFlask(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
    def use(self):
        if KDS.Keys.actionKey.pressed:
            KDS.Scores.score += 1
            Player.health += random.randint(0, 10)
            Player.inventory.pickupItem(EmptyFlask((0, 0), 26, give_pickup_score=False), force=True)
            KDS.Audio.PlaySound(glug_sound)
        return self.texture

    def pickup(self) -> None:
        KDS.Audio.PlaySound(coffeemug_sound)
        self.try_give_pickup_score(7)

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
        if KDS.Keys.actionKey.pressed:
            KDS.Audio.PlaySound(grenade_throw)
            Player.inventory.dropItem(forceDrop=True)
            BallisticObjects.append(KDS.World.BallisticProjectile(pygame.Rect(Player.rect.centerx, Player.rect.centery - 25, 10, 10), Grenade.Slope, Grenade.Force, Player.direction, gravitational_factor=0.4, flight_time=140, texture=self.texture))
        return self.texture

    def pickup(self) -> None:
        self.try_give_pickup_score(7)

class FireExtinguisher(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        return self.texture

class LevelEnderItem(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.actionKey.pressed:
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
            if KDS.Keys.actionKey.pressed:
                Chainsaw.ammunition = max(0, Chainsaw.ammunition - 0.05)
                Projectiles.append(KDS.World.Bullet(Player.rect, pygame.Rect(Player.rect.centerx + 18 * KDS.Convert.ToMultiplier(Player.direction), Player.rect.y + 28, 1, 1), Player.direction, -1, Tiles, damage=1, maxDistance=80))
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
    pickup_sound = pygame.mixer.Sound("Assets/Audio/Items/gascanister_shake.ogg")
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

class Euro_DEPRECATED(KDS.Build.Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)

    def use(self):
        if KDS.Keys.actionKey.pressed:
            # give Wallet with one euro stored in the balance
            assert(KDS.Build.Item.serialNumbers[42] is Wallet)
            wallet = Wallet((0, 0), 42, balance=1)
            picked: bool = Player.inventory.pickupItem(wallet, force=True)
            assert(picked)
            wallet.pickup() # give the one euro stored in the serial number

        return self.texture

class Lager(KDS.Build.Item):
    sound: Final[pygame.mixer.Sound] = pygame.mixer.Sound("Assets/Audio/Items/lager_open_stolenfromoispakaljaa.mp3")

    def use(self):
        if KDS.Keys.actionKey.clicked:
            if self.storePrice is None:
                dropped: KDS.Build.Item | None = Player.inventory.dropItem(forceDrop=True)
                if dropped is None:
                    KDS.Logging.AutoError("Could not remove Lager from inventory after use.")
                KDS.Audio.PlaySound(Lager.sound)
                ScreenEffects.Trigger(ScreenEffects.Effects.Drunk)
            else:
                Notifications.append(KDS.UI.Notification(f"Lager must be purchased before drinking.", color=(217, 98, 59)))

        return self.texture

class Wallet(KDS.Build.Item):
    """
    To set balance:
        LevelBuilder: use `balance` property
        Inventory: set `walletBalance` in levelprop.kdf
        Code: set the `balance` argument
    """

    _SelectedIndex: int = 0
    _Balance: Final[list[tuple[KDS.Money.Euro, KDS.Math.SmoothDamp]]] = []
    # Balance is reset when a new levelProp.kdf is loaded.

    RENDER_POS: Final[tuple[int, int]] = (10, 150)
    RENDER_SPACING: int = 10

    TIP: KDS.UI.KeybindFormattedText = KDS.UI.KeybindFormattedText(tip_font, f"Rotate Wallet [{{binding:{KDS.Keys.rotate_wallet.name}}}]", True, KDS.Colors.White)

    def __init__(self, position: Tuple[int, int], serialNumber: int, *, balance: int | float = 0):
        super().__init__(position, serialNumber)
        self.balance: int | float = balance

        self._press_was_registered: bool = False

    def pickup(self) -> None:
        Wallet.add_balance(KDS.Money.Euro.from_float(self.balance))
        self.balance = 0

    @staticmethod
    def add_balance(euro: KDS.Money.Euro) -> None:
        units, unhandled = euro.split_units()
        if unhandled != 0:
            KDS.Logging.AutoError(f"Unaccounted cents during balance add: {unhandled}")
        Wallet._Balance.extend((u, Wallet._create_animation()) for u in units)
        Wallet._sort_balance()

    @staticmethod
    def _sort_balance() -> None:
        Wallet._Balance.sort(key=lambda b: b[0], reverse=True)

    @staticmethod
    def set_balance(euro: KDS.Money.Euro) -> None:
        Wallet._Balance.clear()
        Wallet.add_balance(euro)

    @staticmethod
    def get_balance() -> KDS.Money.Euro:
        return sum((b[0] for b in Wallet._Balance), start=KDS.Money.Euro.zero())

    @staticmethod
    def try_pay() -> KDS.Money.Euro | None:
        if len(Wallet._Balance) < 1:
            return None
        return Wallet._Balance.pop(Wallet._SelectedIndex % len(Wallet._Balance))[0]

    @staticmethod
    def get_hand_euro() -> KDS.Money.Euro | None:
        if len(Wallet._Balance) < 1:
            return None
        return Wallet._Balance[Wallet._SelectedIndex % len(Wallet._Balance)][0]

    def use(self):
        if KDS.Keys.rotate_wallet.pressed:
            self._press_was_registered = True

        # do not check for click events when press wasn't registered
        # so for example when we come out of Koponen talk by clicking exit the wallet isn't rotated
        # We check press instead of onDown, because unlike onDown, pressed will be set as False once the koponen talk exit click button is raised
        # when checking onDown, we have a situation where both onDown and onUp are True which means the rotate gets executed.
        if self._press_was_registered:
            if KDS.Keys.rotate_wallet.held:
                Wallet._SelectedIndex = 0
            if KDS.Keys.rotate_wallet.clicked and not KDS.Keys.rotate_wallet.holdClicked:
                Wallet._SelectedIndex += 1

        if not KDS.Keys.rotate_wallet.pressed:
            self._press_was_registered = False

        return self.texture

    @staticmethod
    def _renderReset() -> None:
        Wallet._SelectedIndex = 0
        for _, anim in Wallet._Balance:
            anim.value = 0.0
            anim.velocity = 0.0

    @staticmethod
    def _create_animation() -> KDS.Math.SmoothDamp:
        return KDS.Math.SmoothDamp(0.0, smooth_time=0.15, max_speed=10000.0)

    @staticmethod
    def iterateUnitsOrdered() -> Iterable[tuple[KDS.Money.Euro, KDS.Math.SmoothDamp]]:
        units: list[tuple[KDS.Money.Euro, KDS.Math.SmoothDamp]] = Wallet._Balance
        for tmp_i in range(len(units)):
            i: int = (tmp_i + Wallet._SelectedIndex) % len(units)
            yield units[i]

    @staticmethod
    def globalRenderUpdate(surface: pygame.Surface, isHandItem: bool, renderUI: bool) -> None:
        if not isHandItem:
            Wallet._renderReset()
            return

        if len(Wallet._Balance) > 0:
            Wallet._SelectedIndex %= len(Wallet._Balance)
        else:
            Wallet._SelectedIndex = 0

        current_x: int | None = None
        units_ordered: tuple[tuple[KDS.Money.Euro, KDS.Math.SmoothDamp], ...] = tuple(Wallet.iterateUnitsOrdered())
        for unit, animation in units_ordered:
            x: int
            width: int = KDS.Money.get_texture(unit).get_width()
            if current_x is None:
                x = 0
                current_x = width
            else:
                current_x += Wallet.RENDER_SPACING
                x = current_x
                current_x += width

            animation.update(x)

        if renderUI:
            # render reversed so that overlapping animations are ordered correctly (the one moving to the end of the list is below)
            for unit, animation in reversed(units_ordered):
                rend_x: float = animation.value
                surface.blit(KDS.Money.get_texture(unit), (Wallet.RENDER_POS[0] + round(rend_x), Wallet.RENDER_POS[1]))
            if len(units_ordered) > 0:
                surface.blit(Wallet.TIP.get_surface(), (Wallet.RENDER_POS[0], Wallet.RENDER_POS[1] + 37)) # 50 € is 35 tall

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
    40: Euro_DEPRECATED,
    41: Lager,
    42: Wallet
}
game_initialization_logger.stop("Item Loading Complete.")
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
        if renderUI and enemy.health > 0 and not KDS.Math.IsPositiveInfinity(enemy.health):
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
game_initialization_logger.start("Loading Player...")
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

    def reset(self, clear_inventory: bool = True, clear_keys: bool = True, load_levelprop: bool = False):
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
        self.is_grounded: bool = False
        self.visible: bool = True
        self.lockMovement: bool = False
        self.animations.reset()
        self.deathSound.stop()

        if load_levelprop:
            self.load_levelprop()

    def load_levelprop(self):
        self.light = KDS.MapProp.LevelProp.Get("Rendering/Darkness/playerLight", True)
        self.disableSprint = KDS.MapProp.LevelProp.Get("Entities/Player/disableSprint", False)
        self.direction = KDS.MapProp.LevelProp.Get("Entities/Player/spawnInverted", False)

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
                test_rect: pygame.Rect = pygame.Rect(Player.rect.x, Player.rect.y - crouch_size[1], Player.rect.width, Player.rect.height)
                if KDS.World.collision_test_fast(test_rect, Tiles) is not None:
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

            run_pressed: bool = KDS.Keys.moveRun.pressed and not KDS.Keys.moveDown.pressed

            if KDS.Keys.moveRight.pressed:
                if not self.crouching: self.movement[0] += 4
                else: self.movement[0] += 2
                if run_pressed and self.stamina > 0 and not self.crouching and not self.disableSprint:
                    self.movement[0] += 4
                elif self.stamina <= 0: KDS.Keys.moveRun.SetState(False)

            if KDS.Keys.moveLeft.pressed:
                if not self.crouching: self.movement[0] -= 4
                else: self.movement[0] -= 2
                if run_pressed and self.stamina > 0 and not self.crouching and not self.disableSprint:
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

            # HACK: Apparently the bottom doesn't collide each frame when the y-axis movement rounds to 0
            # so we implement this dirty solution so that AWM can know when we are grounded
            # so that AWM can allow the player to aim.
            self.is_grounded = collisions.bottom or round(self.movement[1]) == 0

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
game_initialization_logger.stop("Player Loading Complete.")
#endregion
#region Console
game_initialization_logger.start("Loading Console...")
def console(oldSurf: pygame.Surface):
    global level_finished, go_to_console, Player
    go_to_console = False

    itemDict: Dict[str, Union[str, Dict[str, str]]] = {}
    for itemName, _data in KDS.Build.Item.DATA.items():
        if _data["supportsInventory"] != True:
            continue
        modName = itemName.replace(" ", "_").lower().replace("(", "").replace(")", "")
        itemDict[modName.encode("ascii", "ignore").decode("ascii")] = f"""{_data["serialNumber"]:03d}"""
    keyDict = {}
    for key in Player.keys:
        keyDict[key] = "break"
    itemDict["key"] = keyDict

    effectDict: dict[str, ScreenEffects.Effects] = {str(e.name).lower(): e for e in ScreenEffects.Effects}

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
            "cavemonster": "break",
            "mummy" : "break",
            "mafiaman" : "break",
            "kuuma" : "break",
            "laato" : "break",
            "securityguard" : "break",
            "bulldog" : "break",
            "zombie" : "break"
        },
        "fly": trueFalseTree,
        "godmode": trueFalseTree,
        "money": { str(Wallet.get_balance()): "break" },
        "rosebud": "break",
        "motherlode": "break",
        "effect": {
            e: "break" for e in effectDict.keys()
        },
        "runprog": {
            "exam": "break",
            "story_sad_ending": "break",
            "certificate": "break",
        },
        "tickspeed": {
            "default": "break"
        },
        "help": "break"
    }

    consoleRunning = True

    blurred_background = KDS.Convert.ToBlur(pygame.transform.scale(oldSurf.copy(), display_size), 6)

    blurred_background_black_overlay = pygame.Surface(blurred_background.get_size())
    blurred_background_black_overlay.set_alpha(128)

    blurred_background.blit(blurred_background_black_overlay, (0, 0))

    while consoleRunning:
        command_list: list = KDS.Console.Start(prompt="Enter Command:", allowEscape=True, checkType=KDS.Console.CheckTypes.Commands(), background=blurred_background, commands=commandTree, autoFormat=True, enableOld=True, showFeed=True)
        if command_list == None: # type: ignore
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
                        Player.inventory.pickupItem(KDS.Build.Item.serialNumbers[consoleItemSerialInt]((0, 0), consoleItemSerialInt), allow_find_empty_slot=True, force=True)
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
                if len(command_list) in (2, 3):
                    infinite_command: str = command_list[1]

                    infinite_state: bool | None
                    stateIsValid: bool
                    if len(command_list) > 2:
                        infinite_state = KDS.Convert.String.ToBool(command_list[2], None)
                        stateIsValid = infinite_state is not None
                    else:
                        infinite_state = None
                        stateIsValid = True


                    if stateIsValid:
                        infinite_command_matched: bool = True
                        match infinite_command:
                            case "health":
                                if infinite_state is None:
                                    infinite_state = not Player.infiniteHealth
                                Player.infiniteHealth = infinite_state
                            case "ammo":
                                if infinite_state is None:
                                    infinite_state = not KDS.Build.Item.infiniteAmmo
                                KDS.Build.Item.infiniteAmmo = infinite_state
                            case "damage":
                                if infinite_state is None:
                                    infinite_state = not KDS.World.Bullet.GodMode
                                KDS.World.Bullet.GodMode = infinite_state
                            case "stamina":
                                if infinite_state is None:
                                    infinite_state = not Player.infiniteStamina
                                Player.infiniteStamina = infinite_state
                            case _:
                                infinite_command_matched = False

                        if infinite_command_matched:
                            KDS.Console.Feed.append(f"infinite {infinite_command} state has been set to: {infinite_state}")
                        else:
                            KDS.Console.Feed.append("Please provide a proper command for infinite.")
                    else:
                        KDS.Console.Feed.append(f"Please provide a proper state for infinite {infinite_command}.")
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
                        KDS.Console.Feed.append(f"Active mission \"{tmpFinishMission.text.build_raw_text()}\" finished.")
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
                    teleport_command_x_valid: bool = True
                    teleport_command_y_valid: bool = True

                    if command_list[1][0] == "~":
                        if len(command_list[1]) < 2:
                            command_list[1] += "0"
                        xt = command_list[1][1:]
                        try:
                            xt = Player.rect.x + int(xt)
                        except ValueError:
                            teleport_command_x_valid = False
                    else:
                        xt = command_list[1]
                        try:
                            xt = int(xt)
                        except ValueError:
                            teleport_command_x_valid = False

                    if command_list[2][0] == "~":
                        if len(command_list[2]) < 2:
                            command_list[2] += "0"
                        yt = command_list[2][1:]
                        try:
                            yt = Player.rect.y + int(yt)
                        except ValueError:
                            teleport_command_y_valid = False
                    else:
                        yt = command_list[2]
                        try:
                            yt = int(yt)
                        except ValueError:
                            teleport_command_y_valid = False

                    if not teleport_command_x_valid or not teleport_command_y_valid:
                        teleport_command_msg: str
                        if not teleport_command_x_valid and not teleport_command_y_valid:
                            teleport_command_msg = "X and Y -coordinates invalid."
                        elif not teleport_command_x_valid:
                            teleport_command_msg = "X-coordinate invalid."
                        else:
                            assert(not teleport_command_y_valid)
                            teleport_command_msg = "Y-coordinate invalid."
                        KDS.Console.Feed.append(teleport_command_msg)

                    if isinstance(xt, int) and isinstance(yt, int):
                        Player.rect.topleft = (xt, yt)
                        KDS.Console.Feed.append(f"Teleported player to {xt}, {yt}")
                else: KDS.Console.Feed.append("Please provide proper coordinates for teleporting.")
            elif command_list[0] == "summon":
                if len(command_list) > 1:
                    summonEntity: Dict[str, Type[KDS.AI.HostileEnemy | KDS.Teachers.Teacher]] = {
                        "imp": KDS.AI.Imp,
                        "sergeantzombie": KDS.AI.SergeantZombie,
                        "drugdealer": KDS.AI.DrugDealer,
                        "turboshotgunner": KDS.AI.TurboShotgunner,
                        "methmaker": KDS.AI.MethMaker,
                        "cavemonster": KDS.AI.CaveMonster,
                        "mummy" : KDS.AI.Mummy,
                        "mafiaman" : KDS.AI.MafiaMan,
                        "kuuma" : KDS.Teachers.KuuMa,
                        "laato" : KDS.Teachers.LaaTo,
                        "securityguard" : KDS.AI.SecurityGuard,
                        "bulldog" : KDS.AI.Bulldog,
                        "zombie" : KDS.AI.Zombie
                    }
                    try:
                        ent = summonEntity[command_list[1]]
                        Entities.append(ent(Player.rect.topright))
                        KDS.Console.Feed.append(f"Summoned Entity: \"{ent.__name__}\".")
                    except KeyError:
                        KDS.Console.Feed.append(f"Entity name {command_list[1]} is not valid.")
            elif command_list[0] == "fly":
                if len(command_list) in (1, 2):
                    flyState: bool | None
                    if len(command_list) > 1:
                        flyState = KDS.Convert.String.ToBool(command_list[1], None)
                    else:
                        flyState = not Player.fly

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
            elif command_list[0] == "money":
                if len(command_list) == 2:
                    moneyAmount: float | None
                    try:
                        moneyAmount = float(command_list[1])
                    except ValueError:
                        moneyAmount = None

                    if moneyAmount is not None:
                        moneyEuroAmount: KDS.Money.Euro = KDS.Money.Euro.from_float(moneyAmount)
                        Wallet.set_balance(moneyEuroAmount)
                        KDS.Console.Feed.append(f"Wallet money balance has been set to: {moneyEuroAmount}")
                    else:
                        KDS.Console.Feed.append("Please provide a proper amount of money")
                else:
                    KDS.Console.Feed.append("Please provide a proper amount of money")
            elif command_list[0] == "rosebud":
                if len(command_list) == 1:
                    Wallet.add_balance(KDS.Money.Euro.from_parts(euros=1))
                else:
                    KDS.Console.Feed.append("rosebud does not take any arguments")
            elif command_list[0] == "motherlode":
                if len(command_list) == 1:
                    Wallet.add_balance(KDS.Money.Euro.from_parts(euros=50))
                else:
                    KDS.Console.Feed.append("motherlode does not take any arguments")
            elif command_list[0] == "effect":
                if command_list[1] in effectDict:
                    screenEffect: ScreenEffects.Effects = effectDict[command_list[1]]
                    ScreenEffects.Trigger(screenEffect)
                    KDS.Console.Feed.append(f"Effect triggered: {screenEffect.name}")
                else: KDS.Console.Feed.append(f"Effect not found: '{command_list[1]}'")
            elif command_list[0] == "runprog":
                if len(command_list) == 2:
                    if command_list[1] == "exam":
                        quit_, grade = KDS.School.Exam()
                        KDS.Console.Feed.append(f"Exam grade: {grade}")
                        if quit_:
                            KDS_Quit()
                    elif command_list[1] == "story_sad_ending":
                        KDS.Story.Tombstones(display)
                    elif command_list[1] == "certificate":
                        KDS.School.Certificate(display, KDS.Colors.DefaultBackground)
                    else:
                        KDS.Console.Feed.append("Not a valid runprog program.")
                else:
                    KDS.Console.Feed.append("Please provide a proper program for runprog")
            elif command_list[0] == "tickspeed":
                if len(command_list) == 2:
                    command_tickspeed: float | None
                    if command_list[1] == "default":
                        command_tickspeed = KDS.Clock.DEFAULT_FRAMERATE
                    else:
                        try:
                            command_tickspeed = float(command_list[1])
                        except ValueError:
                            command_tickspeed = None

                    if command_tickspeed is not None:
                        KDS.Clock.framerate = command_tickspeed
                        KDS.Console.Feed.append(f"Global tick speed has been set to: {command_tickspeed}")
                    else:
                        KDS.Console.Feed.append(f"Invalid tick speed: '{command_list[1]}'")
                else:
                    KDS.Console.Feed.append("Please provide a proper tick speed")
            elif command_list[0] == "help":
                KDS.Console.Feed.append("""
Console Help:
    - give: Add the specified item to your inventory.
    - remove: Remove the specified item from your inventory.
    - kill | stop: Stop the game.
    - killme: Kill the player.
    - killall: Kill all entities.
    - terms: Set Terms and Conditions accepted to the specified value.
    - woof: Set all bulldogs anger to the specified value.
    - finish: Force a level finish.
        Finish all missions or finish the currently active mission.
    - infinite: Set the specified infinite type to the specified value.
        If value is not given, infinity is toggled.
    - teleport: Teleport player to static or relative coordinates.
    - summon: Summon an enemy to the coordinates of player's rect's top-left corner.
    - fly: Set fly mode to the specified value.
        If value is not given, infinity is toggled.
    - godmode: Activate God Mode.
        Gives the player some buffs like infinite health
    - money: Set the amount of money stored in the wallet.
    - rosebud: Give 1 €
    - motherlode: Give 50 €
    - runprog: Run an internal KDS program.
    - tickspeed: Change the runtime tick speed (framerate) of the program.
    - help: Show the list of commands.""")
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
            if defaultEventHandler(event, ignore_quit=True):
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
game_initialization_logger.stop("Console Loading Complete.")
game_whole_initialization_logger.stop("Game Initialisation Complete.", consoleVisible=True)
game_whole_initialization_duration: Final[float] = game_whole_initialization_logger.accumulatedTime
KDS.Logging.debug(f"Unmeasured loading execution time: {game_whole_initialization_duration - game_initialization_logger.accumulatedTime:.3f}")
KDS.Loading.fake_load_extra(game_whole_initialization_duration, quickload)

assert(not game_whole_initialization_logger.is_running)
assert(not game_initialization_logger.is_running)
assert(not asset_loading_logger.is_running)
assert(not animation_loading_logger.is_running)
#endregion
#region Game Functions
class PlayCustomLoadscreen(NamedTuple):
    start: Callable[[], None]
    end: Callable[[], None]

def play_function(mapPath: str | None, gamemode: KDS.Gamemode.Modes, reset_scroll: bool, custom_load: PlayCustomLoadscreen | None = None, auto_play_music: bool = True):
    game_loading_logger: Final = KDS.Logging.ExecutionTimeLogger.debug()
    game_loading_logger.start("Loading Game...")

    global main_menu_running, true_scroll, selectedSave

    pygame.mouse.set_visible(False)
    KDS.Audio.Music.Stop()

    if custom_load is not None:
        custom_load.start()
    else:
        KDS.Loading.Circle.Start(display)

    if gamemode == KDS.Gamemode.Modes.CustomCampaign:
        assert(mapPath is not None)
        gamemode = KDS.Gamemode.Modes.Campaign
    elif gamemode == KDS.Gamemode.Modes.Story:
        assert KDS.ConfigManager.Save.Active != None, "Could not load story mode map! No save active."
        assert(mapPath is None)
        mapPath = os.path.join("Assets/Maps/Story", f"map{KDS.ConfigManager.Save.Active.Story.index:02d}")
    else:
        assert(gamemode == KDS.Gamemode.Modes.Campaign)
        campaignMapPath: Final[str] = os.path.join("Assets/Maps/Campaign", f"map{current_map_index:02d}")
        assert(mapPath is None or mapPath == campaignMapPath)
        mapPath = campaignMapPath

    KDS.World.Lighting.Shapes.clear()

    global Player
    Player = PlayerClass()

    #region World Data
    TheftDetector.globalReset()
    # Wallet.globalReset()
    # levelprop.kdf defines the level's wallet balance so this isn't needed anymore

    global Items, Explosions, BallisticObjects, Projectiles, Entities, Zones, Particles
    Items.clear()
    Explosions.clear()
    BallisticObjects.clear()
    Projectiles.clear()
    Entities.clear()
    Particles.clear()

    Zones.clear()
    KDS.World.Zone.reset()
    #endregion
    #region Class Data
    KDS.NPC.NPC.InstanceList.clear()
    KDS.Teachers.Teacher.InstanceList.clear()
    KDS.World.Zone.StaffOnlyCollisions = 0
    RespawnAnchor.active = None
    BaseTeleport.teleportDatas = {}
    ScreenEffects.Reset()
    #endregion

    #region Reset ammo
    # TODO: We don't seem to be using this old style ammo handling anymore...
    # consider removing
    for c in KDS.Build.Item.serialNumbers.values():
        defaultAmmo = getattr(c, "defaultAmmunition", None)
        if defaultAmmo != None:
            setattr(c, "ammunition", defaultAmmo)
    #endregion

    # It's probably fine if we only load this during startup
    # LoadGameSettings()

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

    KDS.Gamemode.SetGamemode(gamemode, KDS.MapProp.LevelProp.Get("Data/missionsId", "missing"), Enemy.total)

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
    game_loading_logger.stop(f"Game Loaded.", consoleVisible=True)
    KDS.Loading.fake_load_extra(game_loading_logger.accumulatedTime, quickload)

    if custom_load is not None:
        custom_load.end()
    else:
        KDS.Loading.Circle.Stop()

    #LoadMap will assign Loaded if it finds a song for the level. If not found LoadMap will call Unload to set Loaded as None.
    if auto_play_music and KDS.Audio.Music.Loaded != None:
        KDS.Audio.Music.Play()

def play_story(saveIndex: int, newSave: bool = True, oldSurf: Optional[pygame.Surface] = None):
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

    if KDS.ConfigManager.Save.Active.Story.index > storyLevelCount:
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

    custom_load: PlayCustomLoadscreen | None
    if animationOverride:
        custom_load_active_save: Final = KDS.ConfigManager.Save.Active
        custom_load = PlayCustomLoadscreen(
            start=lambda: KDS.Loading.Story.Start(display, oldSurf, map_names[custom_load_active_save.Story.index], ArialTitleFont, ArialFont),
            end=lambda: KDS.Loading.Story.WaitForExit(pump_events=True)
        )
    else:
        custom_load = None

    KDS.Koponen.setPlayerPrefix(KDS.ConfigManager.Save.Active.Story.playerName)
    play_function(None, KDS.Gamemode.Modes.Story, True, custom_load=custom_load, auto_play_music=False)
    if KDS.Audio.Music.Loaded != None:
        KDS.Audio.Music.Play()

def respawn_function():
    global level_finished
    KDS.Scores.levelDeaths += 1
    Player.reset(clear_inventory=False, clear_keys=False, load_levelprop=True)
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
    global main_menu_running, esc_menu, main_running, settings_running, pause_on_focus_loss, play_walk_sound
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
        pause_on_focus_loss = pause_loss_switch.update(display, mouse_pos, c)

        return_button.update(display, mouse_pos, c)
        controls_settings_button.update(display, mouse_pos, c)
        reset_settings_button.update(display, mouse_pos, c)
        remove_data_button.update(display, mouse_pos, c)
        give_feedback_button.update(display, mouse_pos, c)
        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({"FPS": KDS.Clock.GetFPS(3)}), (0, 0))

        pygame.display.flip()
        # display.fill(KDS.Colors.Black)
        # I don't know why this is here... It made everything flicker when exiting settings
        c = False
        KDS.Clock.Tick()

def main_menu():
    global current_map_index

    pygame.mouse.set_visible(True)

    class Mode(IntEnum):
        MainMenu = 0
        ModeSelectionMenu = 1
        StoryMenu = 2
        CampaignMenu = 3
    MenuMode: Mode = Mode.MainMenu

    global main_menu_running, main_running, go_to_main_menu
    go_to_main_menu = False

    main_menu_running = True
    c = False
    skip_render_this_frame = False

    KDS.Audio.Music.Play("Assets/Audio/Music/lobbymusic.ogg" if KDS.ConfigManager.GetSetting("Mixer/legacyLobbyMusic", False) == False else "Assets/Audio/Music/Legacy/lobbymusic.ogg")

    custom_maps_paths: list[str] = []
    def load_custom_maps():
        nonlocal custom_maps_paths
        custom_maps_paths.clear()
        try:
            for p in os.listdir(PersistentPaths.CustomMaps):
                custom_maps_paths.append(os.path.join(PersistentPaths.CustomMaps, p))
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")

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
            global current_map_index
            if direction == level_pick.direction.left:
                current_map_index -= 1
            elif direction == level_pick.direction.right:
                current_map_index += 1
            if len(custom_maps_paths) > 0:
                current_map_index = KDS.Math.Clamp(current_map_index, -len(custom_maps_paths), campaignTotalLevelCount)
            else:
                current_map_index = KDS.Math.Clamp(current_map_index, 1, campaignTotalLevelCount)
            KDS.ConfigManager.SetSetting("Player/currentMap", current_map_index)
    level_pick.pick(level_pick.direction.none)

    @dataclass(frozen=True)
    class CampaignShowScores:
        surface: pygame.Surface | None
        """None if campaign scores cannot be calculated."""

        height_animation: KDS.Animator.Value

        @classmethod
        def load(cls, save_uuid: UUID, surface_size: tuple[int, int], background_color: tuple[int, int, int]) -> KDS.Jobs.JobHandle[Self]:
            def _construct() -> Self:
                surf: pygame.Surface | None = KDS.Scores.render_campaign_scores(
                    save_uuid,
                    font=ArialFont,
                    size=surface_size,
                    padding=16,
                    background_color=background_color
                )

                return cls(
                    surface=surf,
                    height_animation=KDS.Animator.Value(0, 1, 60, KDS.Animator.AnimationType.EaseInOutCubic)
                )

            return KDS.Jobs.Schedule(_construct)

    @dataclass
    class CampaignData:
        map_index: int
        map_dirpath: str | None

        load_job: KDS.Jobs.JobHandle[None] | None

        show_scores_countdown: int | None = None
        show_scores: KDS.Jobs.JobHandle[CampaignShowScores] | None = None

        campaign: KDS.MapProp.CampaignPropData | None = None
        preview: pygame.Surface | None = None

        @classmethod
        def load(cls, map_index: int) -> Self:
            map_dirpath: str | None
            if map_index < 0:
                custom_map_index: int = abs(map_index)
                if custom_map_index < len(custom_maps_paths):
                    map_dirpath = os.path.join(PersistentPaths.CustomMaps, custom_maps_paths[custom_map_index])
                else:
                    map_dirpath = None
            elif map_index > 0:
                map_dirpath = os.path.join("Assets/Maps/Campaign", f"map{map_index:02d}")
                if not os.path.isdir(map_dirpath):
                    map_dirpath = None
            else: # map_index == 0
                map_dirpath = None

            dat = cls(
                map_index=map_index,
                map_dirpath=map_dirpath,
                load_job=None
            )
            dat.load_job = KDS.Jobs.Schedule(dat._load).AddErrorLogger()
            return dat

        def _load(self):
            campaign_prop: KDS.MapProp.CampaignPropData | None = None
            if self.map_dirpath is not None:
                campaign_prop_path: str = os.path.join(self.map_dirpath, "campaignprop.kdf")
                if os.path.isfile(campaign_prop_path):
                    try:
                        campaign_prop = KDS.MapProp.CampaignPropData.load(campaign_prop_path)
                    except Exception as e:
                        KDS.Logging.AutoError(f"CampaignProp loading failed with error:\n{e}")
                        campaign_prop = KDS.MapProp.CampaignPropData.errored()
                else:
                    campaign_prop = KDS.MapProp.CampaignPropData.default()
            else:
                campaign_prop = KDS.MapProp.CampaignPropData.errored()
            self.campaign = campaign_prop

            campaign_preview: pygame.Surface | None = None
            if self.map_dirpath is not None:
                campaign_preview_path: str = os.path.join(self.map_dirpath, "campaign_preview.png")
                if os.path.isfile(campaign_preview_path):
                    try:
                        campaign_preview = pygame.image.load(campaign_preview_path).convert()
                    except Exception as e:
                        KDS.Logging.AutoError(f"Campaign preview image loading failed with error:\n{e}")
            self.preview = campaign_preview if campaign_preview is not None else pygame.Surface(display_size)

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

    campaign_map_name_rect = pygame.Rect(50, 200, int(display_size[0] - 100), 66)
    # campaign stats are centered vertically inside rect, switch rect y position to 'campaign_map_name_rect.bottom + 50' if more space is needed
    campaign_stats_rect = pygame.Rect(campaign_play_button_rect.right + 50, campaign_play_button_rect.top, 0, 0)
    campaign_stats_rect.width = (display_size[0] - 50) - campaign_stats_rect.x
    campaign_stats_rect.height = (display_size[1] - 50) - campaign_stats_rect.y

    campaignDatas: dict[int, CampaignData] = {}
    campaignAnimatingBackgrounds: list[tuple[CampaignData, KDS.Animator.Value]] = []

    def campaign_play_handler(data: CampaignData):
        if data.map_index != 0:
            assert(data.map_dirpath is not None)
            play_function(data.map_dirpath, KDS.Gamemode.Modes.Campaign if data.map_index > 0 else KDS.Gamemode.Modes.CustomCampaign, True)

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
            if defaultEventHandler(event, ignore_quit=True):
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
                            campaignAnimatingBackgrounds.clear() # reset background animation
                            for cmpDat in campaignDatas.values(): # reset show scores
                                cmpDat.show_scores_countdown = None
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
                            f"""Playtime: {KDS.Convert.FormatDuration(data["playtime"])}""",
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
            while len(campaignDatas) > 10: # remove old campaign datas before inserting new ones as sometimes the current data was unloaded before it was accessed...
                campaignDatas.pop(next(iter(campaignDatas))) # remove oldest element

            if current_map_index not in campaignDatas:
                campaignDatas[current_map_index] = CampaignData.load(current_map_index)
            for load_padding in (1,): # dict can be extended if necessary (i.e.: 1, 2)
                for multiplier in (-1, 1):
                    campaign_loadpad: int = current_map_index + (load_padding * multiplier)
                    if campaign_loadpad not in campaignDatas:
                        campaignDatas[campaign_loadpad] = CampaignData.load(campaign_loadpad)
                    else:
                        # remove and re-add so that the data is at the bottom of the dictionary
                        # so that it isn't removed when campaignDatas length is over maximum
                        campaign_loadpad_tmp_rmv: CampaignData = campaignDatas.pop(campaign_loadpad)
                        campaignDatas[campaign_loadpad] = campaign_loadpad_tmp_rmv

            current_map_data: Final[CampaignData] = campaignDatas[current_map_index]
            assert(current_map_data.map_index == current_map_index)

            for cmpDat in campaignDatas.values():
                if cmpDat is not current_map_data or cmpDat.show_scores_countdown is None:
                    cmpDat.show_scores_countdown = 180
                    cmpDat.show_scores = None
                else:
                    cmpDat.show_scores_countdown -= 1
                    if cmpDat.show_scores_countdown < 0:
                        cmpDat.show_scores_countdown = 0
                        if cmpDat.show_scores is None and cmpDat.campaign is not None and cmpDat.campaign.scoresGuid is not None:
                            cmpDat.show_scores = CampaignShowScores.load(cmpDat.campaign.scoresGuid, surface_size=campaign_stats_rect.size, background_color=(100, 100, 100))

            # looked ugly so I un-added (removed) it
            # while len(campaignBgs) > 3: # added due to poor performance
            #     campaignBgs.pop(1) # leave the bottom one as is, it's the one where we first started panning

            if len(campaignAnimatingBackgrounds) < 1 or campaignAnimatingBackgrounds[-1][0].map_index != current_map_data.map_index:
                campaignAnimatingBackgrounds.append((current_map_data, KDS.Animator.Value(0, 255, 30)))

            campaign_anim_finished_count: int = 0
            for cmpDat, bgAlphaAnim in campaignAnimatingBackgrounds:
                if cmpDat.preview is not None:
                    bgAlphaAnim.update()
                    if bgAlphaAnim.Finished:
                        campaign_anim_finished_count += 1

            for _ in range(campaign_anim_finished_count - 1):
                campaignAnimatingBackgrounds.pop(0)

            if campaign_anim_finished_count < 1:
                display.fill((0, 0, 0))
            for cmpDat, bgAlphaAnim in campaignAnimatingBackgrounds:
                if cmpDat.preview is not None:
                    cmpDat.preview.set_alpha(int(bgAlphaAnim.get_value()))
                    display.blit(cmpDat.preview, (0, 0))

            if len(os.listdir(PersistentPaths.CustomMaps)) != len(custom_maps_paths):
                KDS.Logging.debug("New custom maps detected.", True)
                load_custom_maps()
                level_pick.pick(level_pick.direction.none)

            pygame.draw.rect(display, KDS.Colors.LightGray, campaign_map_name_rect)

            if current_map_data.show_scores is not None and current_map_data.show_scores.IsComplete:
                show_scores: CampaignShowScores = current_map_data.show_scores.Complete()
                if show_scores.surface is not None:
                    show_scores_unscaled: pygame.Surface = show_scores.surface
                    show_scores_scaled: pygame.Surface
                    if not show_scores.height_animation.Finished:
                        show_scores_height: int = int(show_scores_unscaled.height * show_scores.height_animation.update())
                        show_scores_scaled = pygame.transform.smoothscale(show_scores_unscaled, (show_scores_unscaled.width, show_scores_height))
                    else:
                        show_scores_scaled = show_scores_unscaled

                    display.blit(show_scores_scaled, (campaign_stats_rect.left, campaign_stats_rect.centery - (show_scores_unscaled.height // 2)))

            render_map_name: str | None = None
            if current_map_index > 0:
                if current_map_data.campaign is not None:
                    render_map_name = f"{current_map_index} - {current_map_data.campaign.levelName}"
            elif current_map_index < 0:
                if current_map_data.campaign is not None:
                    render_map_name = f"CUSTOM - {current_map_data.campaign.levelName}"
            else: # current_map_index == 0
                render_map_name = "<= Custom                Campaign =>"
            level_text = KDS.UI.ButtonFont.render(render_map_name, True, (0, 0, 0))
            display.blit(level_text, (125, 209))

            skip_render_this_frame = campaign_play_button.update(display, mouse_pos, c, current_map_data)
            return_button.update(display, mouse_pos, c, Mode.MainMenu)
            campaign_left_button.update(display, mouse_pos, c)
            campaign_right_button.update(display, mouse_pos, c)

        if KDS.Debug.Enabled:
            display.blit(KDS.Debug.RenderData({
                "FPS": KDS.Clock.GetFPS(3),
                "Campaign Datas In Memory": len(campaignDatas),
                "Campaign Datas Loading": KDS.Linq.Count(campaignDatas.values(), lambda cd: cd.load_job is not None and not cd.load_job.IsComplete),
                "Campaign Backgrounds Rendering": len(campaignAnimatingBackgrounds)
            }), (0, 0))

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

    calculated_scores: Final = KDS.Scores.ScoreCounter.GetScores()
    KDS.Scores.ScoreAnimation.init(calculated_scores)

    if KDS.MapProp.CampaignProp.data is not None and KDS.MapProp.CampaignProp.data.countScores:
        assert(KDS.MapProp.CampaignProp.data.scoresGuid is not None)
        KDS.Jobs.Schedule(
            KDS.ConfigManager.CampaignSave.add_run,
            KDS.MapProp.CampaignProp.data.scoresGuid,
            KDS.ConfigManager.CampaignRun.from_scores(calculated_scores)
        ).AddErrorLogger()

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
        global level_finished_running, current_map_index
        nonlocal render_level_finished
        level_finished_running = False
        current_map_index += 1
        play_function(None, KDS.Gamemode.Modes.Campaign, True)
        render_level_finished = False

    next_level_bool = current_map_index < campaignOfficialLevelCount

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
            timeTakenText = ArialFont.render(f"Time Taken: {KDS.Convert.FormatDuration(KDS.Scores.GameTime.GetGameTime())}", True, score_color)
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
            if event.key == K_ESCAPE:
                esc_menu = True
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                KDS.Keys.actionKey.SetState(True)
                rk62_sound_cooldown = 11
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                KDS.Keys.actionKey.SetState(False)
        elif event.type == MOUSEWHEEL:
            tmpAmount = event.x - event.y
            if tmpAmount > 0:
                for _ in range(abs(tmpAmount)): Player.inventory.moveRight()
            else:
                for _ in range(abs(tmpAmount)): Player.inventory.moveLeft()
        elif event.type == WINDOWFOCUSLOST:
            if pause_on_focus_loss: esc_menu = True

    if KDS.Keys.dropItem.onDown:
        if Player.inventory.getHandItem() != KDS.Inventory.EMPTYSLOT and Player.inventory.getHandItem() != KDS.Inventory.DOUBLEITEM:
            droppedItem: Final = Player.inventory.dropItem()
            if droppedItem is not None:
                KDS.Build.Item.modDroppedPropertiesAndAddToList(Items, droppedItem, Player)
    if KDS.Keys.fart.onDown:
        if Player.stamina == 100:
            Player.stamina = -1000.0
            Player.farting = True
            KDS.Audio.PlaySound(fart)
    if KDS.Keys.hideUI.onDown:
        renderUI = not renderUI
    if KDS.Keys.terminal.onDown: # onDown required double tap to enter console because console swallowed up the event
        if KDS.Gamemode.gamemode != KDS.Gamemode.Modes.Story or allow_console_in_storymode: # Console is disabled in story mode if debug setting not overridden in GameData.
            go_to_console = True
    if KDS.Keys.screenshot.onDown:
        pygame.image.save(screen, os.path.join(PersistentPaths.Screenshots, datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"))
        # Uses the last frame's screen state which is why the notification isn't visible
        Notifications.append(KDS.UI.Notification("Screenshot saved", KDS.Colors.Cyan))
        KDS.Audio.PlaySound(camera_shutter)

    for inventoryKey in KDS.Keys.INVENTORYKEYS:
        if inventoryKey.onDown:
            Player.inventory.pickSlot(inventoryKey.index)
#endregion
#region Data
    display.fill(KDS.Colors.DefaultBackground)
    screen_overlay = None

    Lights.clear()

    scroll_target: tuple[int, int] = (
        Player.rect.centerx + (Awm.AimOffset * KDS.Convert.ToMultiplier(Player.direction)),
        Player.rect.y
    )

    true_scroll[0] += (scroll_target[0] - true_scroll[0] - (screen_size[0] / 2)) / 12
    true_scroll[1] += (scroll_target[1] - true_scroll[1] - 220) / 12

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

    # MUST BE BEFORE TILE RENDER (which is called by KDS.Build.Tile.renderUpdate)
    TheftDetector.globalUpdate()

#endregion
#region Rendering
    ###### TÄNNE UUSI ASIOIDEN KÄSITTELY ######
    KDS.Build.Item.checkCollisions(Items, Player.rect, Player.inventory, Notifications)
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
                _koponen_talk_tip_surf: Final[pygame.Surface] = koponen_talk_tip.get_surface()
                screen.blit(_koponen_talk_tip_surf, (Koponen.rect.centerx - scroll[0] - _koponen_talk_tip_surf.get_width() // 2, Koponen.rect.top - scroll[1] - 20))
                if KDS.Keys.functionKey.pressed:
                    KDS.Keys.Reset()
                    talk = True
        if talk:
            Koponen.start_with_talk = False
            result = KDS.Koponen.Talk.start(display, Player.inventory, defaultEventHandler=defaultEventHandler, autoExit=Koponen.force_talk)
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

        Awm.globalUpdate(isinstance(Player.inventory.getHandItem(), Awm))

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
                Projectiles.append(KDS.World.Bullet(None, pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), True, -1, Tiles, 25, maxDistance=82, slope=x))
                Projectiles.append(KDS.World.Bullet(None, pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), False, -1, Tiles, 25, maxDistance=82, slope=x))

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

    # Do not check enabled for each particle render, only check when necessary
    if KDS.Debug.Enabled:
        for particle in Particles:
            pygame.draw.rect(screen, KDS.Colors.Purple, (particle.rect.x - scroll[0], particle.rect.y - scroll[1], particle.rect.w, particle.rect.h))

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
        tip_rnd_surf: Final[pygame.Surface] = itemTip.get_surface()
        tip_rnd_pos = (KDS.Build.Item.tipItem.rect.centerx - tip_rnd_surf.get_width() // 2, KDS.Build.Item.tipItem.rect.bottom - 45)
        screen.blit(tip_rnd_surf, (tip_rnd_pos[0] - scroll[0], tip_rnd_pos[1] - scroll[1]))

        if KDS.Build.Item.tipItem.storePrice is not None:
            if KDS.Build.Item.tipItem is not price_tip_last_item:
                price_tip_last_item = KDS.Build.Item.tipItem
                price_tip_tick = 0

            price_tip_txt: str | None = None
            if KDS.Build.Item.tipItem.storeDiscountPrice is not None:
                price_tip_tick += 1
                price_tip_tick %= 180
                if price_tip_tick >= (180 // 2):
                    price_tip_txt = f"SS-Etukortilla: {KDS.Build.Item.tipItem.storeDiscountPrice}"
            if price_tip_txt is None:
                price_tip_txt = f"{KDS.Build.Item.tipItem.storePrice} euroa"

            price_tip = tip_font.render(price_tip_txt, True, KDS.Colors.White)
            screen.blit(price_tip, (KDS.Build.Item.tipItem.rect.centerx - price_tip.get_width() // 2 - scroll[0], tip_rnd_pos[1] + tip_rnd_surf.get_height() - scroll[1]))
        else:
            price_tip_last_item = None

    #Valojen käsittely
    darkness_value: Final[tuple[int, int, int]] | None = KDS.World.Dark.Update()
    if darkness_value is not None:
        if not KDS.World.Dark.Disco.enabled:
            black_tint.fill(darkness_value)
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
        if KDS.World.Dark.GetEnabled():
            for light in Lights:
                black_tint.blit(light.surf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
                if KDS.Debug.Enabled:
                    rectSurf = pygame.Surface(light.surf.get_size())
                    rectSurf.fill(KDS.Colors.Yellow)
                    rectSurf.set_alpha(128)
                    screen.blit(rectSurf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
                #black_tint.blit(KDS.World.Lighting.Shapes.circle.get(40, 40000), (20, 20))

        # !!! This made colored lights lighter... !!!
        # if not KDS.World.Dark.Disco.enabled: # fix lights being black when darkness is small
        #     black_tint.fill(darkness_value, special_flags=BLEND_MAX)
        screen.blit(black_tint, (0, 0), special_flags=BLEND_MULT)

    #UI
    Wallet.globalRenderUpdate(
        screen,
        isHandItem=isinstance(Player.inventory.getHandItem(), Wallet),
        renderUI=(renderUI and Player.health > 0 and Player.visible)
    )
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

            if int(data.repeat_index) % int(data.repeat_rate) == 0:
                invPix = pygame.surfarray.pixels2d(screen)
                invPix ^= 2 ** 32 - 1
                del invPix
                # pygame.transform.invert(screen, screen)
                # pygame.transform is slower (it seems to create a new surface which is slow)
                # while pixels2d seems to be almost instant (we manipulate the screen directly)

            data.repeat_index += 1
            if data.repeat_index > data.repeat_length:
                data.repeat_index = 0
                ScreenEffects.Finish(ScreenEffects.Effects.Flicker)
        if ScreenEffects.Get(ScreenEffects.Effects.FadeInOut):
            data = ScreenEffects.EffectData.FadeInOut # Should be the same instance...
            anim: KDS.Animator.Value = data.animation # Should be the same instance...
            rev: bool = data.reversed
            surf = data.surface
            surf.set_alpha(round(anim.update(rev)))
            screen.blit(surf, (0, 0))
            if anim.Finished:
                if not rev:
                    data.wait_index += 1
                    if data.wait_index > data.wait_length:
                        data.reversed = True
                else:
                    data.reversed = False
                    data.wait_index = 0
                    ScreenEffects.Finish(ScreenEffects.Effects.FadeInOut)
        if ScreenEffects.Get(ScreenEffects.Effects.Glitch): # pygame.surfarray.pixels2d was tested on these. It was slower.
            data = ScreenEffects.EffectData.Glitch
            rptIndx = (int(data.repeat_index) + 1) % int(data.repeat_rate)
            data.repeat_index = rptIndx
            if rptIndx == 0:
                glitchRandX = random.randrange(0, screen_size[0])
                glitchRandY = random.randrange(0, screen_size[1])
                # glitchRandW = random.randrange(screen_size[0], screen_size[0] + 1)
                glitchRandW = screen_size[0]
                glitchRandH = random.randrange(10, 50)
                data.current_glitch = (
                    (glitchRandX, glitchRandY, min(glitchRandW, screen_size[0] - glitchRandX), min(glitchRandH, screen_size[1] - glitchRandY)),
                    (random.randint(-10, 10) + glitchRandX, glitchRandY) # random.randint(0, 0) + glitchRandY)
                )
            current_glitch = data.current_glitch
            glitch_surf = screen.subsurface(current_glitch[0]).copy() # Copy is necessary as otherwise the screen will be kept locked
            if 0 <= current_glitch[1][0] < screen_size[0] and 0 <= current_glitch[1][1] < screen_size[1]:
                screen.blit(glitch_surf, current_glitch[1])
        if ScreenEffects.Get(ScreenEffects.Effects.Drunk): # pygame.surfarray.pixels2d was tested on these. It was slower.
            data = ScreenEffects.EffectData.Drunk
            data.phase += data.phase_speed
            data.phase %= data.phase_length

            drunkAmplitude: float = data.amplitude_rise.update()
            if data.amplitude_rise.Finished:
                drunkAmplitude = data.amplitude_fall.update()

            for y in range(screen.get_height()):
                drunkLocalPhase: float = data.wave_count * data.phase_length * (y / screen.get_height())
                drunkLocalPhase *= -1 # reverse so that waves move downwards

                # ceil because otherwise the animation will round to 0 but still run
                # thus disallowing new animations to proceed.
                offset: int = KDS.Math.CeilToInt(drunkAmplitude * KDS.Math.Sin(drunkLocalPhase + data.phase))
                drunk_surf = screen.subsurface((0, y, screen.get_width(), 1)).copy()
                screen.blit(drunk_surf, (offset, y))

            # we check rise and fall since we don't update fall before rise has finished
            # and thus fall can have its old Finished value.
            if data.amplitude_rise.Finished and data.amplitude_fall.Finished:
                data.reset()
                ScreenEffects.Finish(ScreenEffects.Effects.Drunk)

    if screen_overlay != None:
        screen.blit(screen_overlay, (0, 0))

    pygame.transform.scale(screen, display_size, display)

    #region Notifications
    notif_rmv_count: int = 0
    for notif_i in range(len(Notifications)):
        notif_index: int = notif_i - notif_rmv_count
        notif: KDS.UI.Notification = Notifications[notif_index]
        notif_data = notif.update(ArialFont, display_size)
        if notif_data is None:
            Notifications.pop(notif_index)
            notif_rmv_count += 1
        else:
            display.blit(notif_data[1], notif_data[0])
    #endregion

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
            "Sounds Playing": f"{len(KDS.Audio.GetBusyChannels())} / {KDS.Audio._SoundMixer.get_num_channels()}",
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
# KDS.System.emptdir(PersistentPaths.Cache)
KDS.Logging.quit()
pygame.mixer.quit()
pygame.display.quit()
pygame.quit()
if remove_data_on_quit:
    shutil.rmtree(PersistentPaths.AppData)
#endregion
