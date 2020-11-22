#region Importing
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
import KDS.AI
import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.ConfigManager
import KDS.Console
import KDS.Convert
import KDS.Gamemode
import KDS.Keys
import KDS.Koponen
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.Scores
import KDS.System
import KDS.UI
import KDS.World
import numpy
import random
import threading
import concurrent.futures
import sys
import shutil
import json
import zipfile
import math
import time
import datetime
from pygame.locals import *
from typing import Any, Dict, List, Tuple
#endregion
#region Priority Initialisation
class PersistentPaths:
    AppDataPath = os.path.join(os.getenv('APPDATA'), "KL Corporation", "Koponen Dating Simulator")
    CachePath = os.path.join(AppDataPath, "cache")
    SavePath = os.path.join(AppDataPath, "saves")
    LogPath = os.path.join(AppDataPath, "logs")
    Screenshots = os.path.join(AppDataPath, "screenshots")
os.makedirs(PersistentPaths.CachePath, exist_ok=True)
os.makedirs(PersistentPaths.SavePath, exist_ok=True)
os.makedirs(PersistentPaths.Screenshots, exist_ok=True)
os.makedirs(PersistentPaths.LogPath, exist_ok=True)
KDS.System.hide(PersistentPaths.CachePath)

KDS.Logging.init(PersistentPaths.AppDataPath, PersistentPaths.LogPath)
KDS.ConfigManager.init(PersistentPaths.AppDataPath, PersistentPaths.CachePath, PersistentPaths.SavePath)

pygame.mixer.init()
pygame.init()

cursorIndex = KDS.ConfigManager.GetSetting("UI/cursor", 0)
cursorData = {
    1: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor1.xbm", "Assets/Textures/UI/Cursors/cursor1.xbm"),
    2: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor2.xbm", "Assets/Textures/UI/Cursors/cursor2.xbm"),
    3: pygame.cursors.load_xbm("Assets/Textures/UI/Cursors/cursor3.xbm", "Assets/Textures/UI/Cursors/cursor3.xbm"),
    4: pygame.cursors.arrow,
    5: pygame.cursors.tri_left
}
if cursorIndex in cursorData: pygame.mouse.set_cursor(*cursorData[cursorIndex])
else: pygame.mouse.set_system_cursor(SYSTEM_CURSOR_ARROW)
del cursorData

game_icon = pygame.image.load("Assets/Textures/Branding/gameIcon.png")
pygame.display.set_icon(game_icon)
pygame.display.set_caption("Koponen Dating Simulator")
display_size = (1200, 800)
display = pygame.display.set_mode(display_size, RESIZABLE | HWSURFACE | DOUBLEBUF | SCALED)
display_info = pygame.display.Info()
screen_size = (600, 400)
screen = pygame.Surface(screen_size)

CompanyLogo = pygame.image.load("Assets/Textures/Branding/kl_corporation-logo.png").convert()
display.fill(CompanyLogo.get_at((0, 0)))
display.blit(pygame.transform.scale(CompanyLogo, (500, 500)), (display_size[0] / 2 - 250, display_size[1] / 2 - 250))
pygame.display.update()

KDS.Audio.init(pygame.mixer)

clock = pygame.time.Clock()
profiler_enabled = False

text_icon = pygame.image.load("Assets/Textures/Branding/textIcon.png").convert()
text_icon.set_colorkey(KDS.Colors.White)
level_cleared_icon = pygame.image.load("Assets/Textures/UI/LevelCleared.png").convert()
level_cleared_icon.set_colorkey(KDS.Colors.White)

locked_fps = 60
#endregion
#region Quit Handling
def KDS_Quit(_restart: bool = False, _reset_data: bool = False):
    global main_running, main_menu_running, tcagr_running, esc_menu, settings_running, selectedSave, tick, restart, reset_data, level_finished_running
    main_menu_running = False
    main_running = False
    tcagr_running = False
    esc_menu = False
    KDS.Koponen.Talk.running = False
    settings_running = False
    restart = _restart
    reset_data = _reset_data
    level_finished_running = False
#endregion
#region Initialisation
KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising Game...")
KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising Display Driver...")
if KDS.ConfigManager.GetSetting("Renderer/fullscreen", False): pygame.display.toggle_fullscreen()
KDS.Logging.Log(KDS.Logging.LogType.debug, f"""Display Driver initialised.
I=====[ System Info ]=====I
   [Version Info]
   - PyGame Version: {pygame.version.ver}
   - SDL Version: {pygame.version.SDL.major}.{pygame.version.SDL.minor}.{pygame.version.SDL.patch}
   
   [Display Info]
   - Display Size: {(display_info.current_w, display_info.current_h)}
   
   [Driver Info]
   - SDL Video Driver: {pygame.display.get_driver()}
   - Hardware Acceleration: {KDS.Convert.ToBool(display_info.hw)}
   - Display Allowed: {KDS.Convert.ToBool(display_info.wm)}
   - Video Memory: {display_info.video_mem if display_info.video_mem != 0 else "unknown"}
   
   [Pixel Info]
   - Bit Size: {display_info.bitsize}
   - Byte Size: {display_info.bytesize}
   - Masks: {display_info.masks}
   - Shifts: {display_info.shifts}
   - Losses: {display_info.losses}
   
   [Hardware Acceleration]
   - Hardware Blitting: {KDS.Convert.ToBool(display_info.blit_hw)}
   - Hardware Colorkey Blitting: {KDS.Convert.ToBool(display_info.blit_hw_CC)}
   - Hardware Pixel Alpha Blitting: {KDS.Convert.ToBool(display_info.blit_hw_A)}
   - Software Blitting: {KDS.Convert.ToBool(display_info.blit_sw)}
   - Software Colorkey Blitting: {KDS.Convert.ToBool(display_info.blit_sw_CC)}
   - Software Pixel Alpha Blitting: {KDS.Convert.ToBool(display_info.blit_sw_A)}
I=====[ System Info ]=====I""")
KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising KDS modules...")
KDS.AI.init()
KDS.World.init()
KDS.Missions.init()
KDS.Scores.init()
KDS.Koponen.init("Sinä")
KDS.Logging.Log(KDS.Logging.LogType.debug, "KDS modules initialised.")
KDS.Console.init(display, display, clock, _KDS_Quit = KDS_Quit)
#endregion
#region Loading
#region Settings
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Settings...")
tcagr = KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)
current_map = KDS.ConfigManager.GetSetting("Player/currentMap", "01")
max_map = KDS.ConfigManager.GetSetting("Player/maxMap", 99)
maxParticles = KDS.ConfigManager.GetSetting("Renderer/Particle/maxCount", 128)
play_walk_sound = KDS.ConfigManager.GetSetting("Mixer/walkSound", True)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Settings Loaded.")
#endregion
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Assets...")
#region Fonts
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Fonts...")
score_font = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10, bold=0, italic=0)
tip_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10, bold=0, italic=0)
button_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 52, bold=0, italic=0)
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)
ArialSysFont = pygame.font.SysFont("Arial", 28, bold=0, italic=0)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Font Loading Complete.")
#endregion
#region Building Textures
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Building Textures...")
floor0 = pygame.image.load("Assets/Textures/Tiles/floor0v2.png").convert()
concrete0 = pygame.image.load(
    "Assets/Textures/Tiles/concrete0.png").convert()
wall0 = pygame.image.load("Assets/Textures/Tiles/wall0.png").convert()
table0 = pygame.image.load("Assets/Textures/Tiles/table0.png").convert()
tp_shitting = pygame.image.load("Assets/Textures/Tiles/player_shitting_toilet.png").convert()
lamp0 = pygame.image.load("Assets/Textures/Tiles/lamp0.png").convert()
trashcan = pygame.image.load("Assets/Textures/Tiles/trashcan.png").convert()
ground1 = pygame.image.load("Assets/Textures/Tiles/ground0.png").convert()
grass = pygame.image.load("Assets/Textures/Tiles/grass0.png").convert()
door_closed = pygame.image.load(
    "Assets/Textures/Tiles/door_closed.png").convert()
red_door_closed = pygame.image.load(
    "Assets/Textures/Tiles/red_door_closed.png").convert()
green_door_closed = pygame.image.load(
    "Assets/Textures/Tiles/green_door_closed.png").convert()
blue_door_closed = pygame.image.load(
    "Assets/Textures/Tiles/blue_door_closed.png").convert()
door_open = pygame.image.load("Assets/Textures/Tiles/door_front.png").convert()
exit_door_open = pygame.image.load("Assets/Textures/Tiles/door_open.png").convert_alpha()
respawn_anchor_on = pygame.image.load("Assets/Textures/Tiles/respawn_anchor_on.png").convert()
bricks = pygame.image.load("Assets/Textures/Tiles/bricks.png").convert()
tree = pygame.image.load("Assets/Textures/Tiles/tree.png").convert()
planks = pygame.image.load("Assets/Textures/Tiles/planks.png").convert()
jukebox_texture = pygame.image.load(
    "Assets/Textures/Tiles/jukebox.png").convert()
landmine_texture = pygame.image.load(
    "Assets/Textures/Tiles/landmine.png").convert()
ladder_texture = pygame.image.load(
    "Assets/Textures/Tiles/ladder.png").convert()
background_wall = pygame.image.load(
    "Assets/Textures/Tiles/background_wall.png").convert()
light_bricks = pygame.image.load(
    "Assets/Textures/Tiles/light_bricks.png").convert()
iron_bar = pygame.image.load(
    "Assets/Textures/Tiles/iron_bars_texture.png").convert()
soil = pygame.image.load("Assets/Textures/Tiles/soil.png").convert()
blh = pygame.image.load("Assets/Textures/Tiles/bloody_h.png").convert()
mossy_bricks = pygame.image.load(
    "Assets/Textures/Tiles/mossy_bricks.png").convert()
stone = pygame.image.load("Assets/Textures/Tiles/stone.png").convert()
hay = pygame.image.load("Assets/Textures/Tiles/hay.png").convert()
soil1 = pygame.image.load("Assets/Textures/Tiles/soil_2.png").convert()
wood = pygame.image.load("Assets/Textures/Tiles/wood.png").convert()
table0.set_colorkey(KDS.Colors.White)
lamp0.set_colorkey(KDS.Colors.White)
trashcan.set_colorkey(KDS.Colors.White)
door_closed.set_colorkey(KDS.Colors.White)
red_door_closed.set_colorkey(KDS.Colors.White)
green_door_closed.set_colorkey(KDS.Colors.White)
blue_door_closed.set_colorkey(KDS.Colors.White)
jukebox_texture.set_colorkey(KDS.Colors.White)
landmine_texture.set_colorkey(KDS.Colors.White)
ladder_texture.set_colorkey(KDS.Colors.White)
iron_bar.set_colorkey(KDS.Colors.White)
tree.set_colorkey(KDS.Colors.Black)
blh.set_colorkey(KDS.Colors.White)
tp_shitting.set_colorkey(KDS.Colors.White)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Building Texture Loading Complete.")
#endregion
#region Item Textures
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Item Textures...")
gasburner_off = pygame.image.load("Assets/Textures/Items/gasburner_off.png").convert()
knife = pygame.image.load("Assets/Textures/Items/knife.png").convert()
knife_blood = pygame.image.load("Assets/Textures/Items/knife.png").convert()
red_key = pygame.image.load("Assets/Textures/Items/red_key.png").convert()
green_key = pygame.image.load("Assets/Textures/Items/green_key2.png").convert()
blue_key = pygame.image.load("Assets/Textures/Items/blue_key.png").convert()
coffeemug = pygame.image.load("Assets/Textures/Items/coffeemug.png").convert()
ss_bonuscard = pygame.image.load("Assets/Textures/Items/ss_bonuscard.png").convert()
lappi_sytytyspalat = pygame.image.load("Assets/Textures/Items/lappi_sytytyspalat.png").convert()
plasmarifle = pygame.image.load("Assets/Textures/Items/plasmarifle.png").convert()
plasma_ammo = pygame.image.load("Assets/Textures/Items/plasma_ammo.png").convert()
cell = pygame.image.load("Assets/Textures/Items/cell.png")
pistol_texture = pygame.image.load("Assets/Textures/Items/pistol.png").convert()
pistol_f_texture = pygame.image.load("Assets/Textures/Items/pistol_firing.png").convert()
soulsphere = pygame.image.load("Assets/Textures/Items/soulsphere.png").convert()
turboneedle = pygame.image.load("Assets/Textures/Items/turboneedle.png").convert()
pistol_mag = pygame.image.load("Assets/Textures/Items/pistol_mag.png").convert()
rk62_texture = pygame.image.load("Assets/Textures/Items/rk62.png").convert()
rk62_f_texture = pygame.image.load("Assets/Textures/Items/rk62_firing.png").convert()
rk62_mag = pygame.image.load("Assets/Textures/Items/rk_mag.png").convert()
medkit = pygame.image.load("Assets/Textures/Items/medkit.png").convert()
shotgun = pygame.image.load("Assets/Textures/Items/shotgun.png").convert()
shotgun_f = pygame.image.load("Assets/Textures/Items/shotgun_firing.png").convert()
shotgun_shells_t = pygame.image.load("Assets/Textures/Items/shotgun_shells.png").convert()
ipuhelin_texture = pygame.image.load("Assets/Textures/Items/iPuhelin.png").convert()
ppsh41_f_texture = pygame.image.load("Assets/Textures/Items/ppsh41_f.png").convert()
ppsh41_texture = pygame.image.load("Assets/Textures/Items/ppsh41.png").convert()
awm_f_texture = pygame.image.load("Assets/Textures/Items/awm_f.png").convert()

gasburner_off.set_colorkey(KDS.Colors.White)
knife.set_colorkey(KDS.Colors.White)
knife_blood.set_colorkey(KDS.Colors.White)
red_key.set_colorkey(KDS.Colors.White)
green_key.set_colorkey(KDS.Colors.White)
blue_key.set_colorkey(KDS.Colors.White)
coffeemug.set_colorkey(KDS.Colors.White)
lappi_sytytyspalat.set_colorkey(KDS.Colors.White)
plasmarifle.set_colorkey(KDS.Colors.White)
plasma_ammo.set_colorkey(KDS.Colors.White)
cell.set_colorkey(KDS.Colors.White)
pistol_texture.set_colorkey(KDS.Colors.White)
pistol_f_texture.set_colorkey(KDS.Colors.White)
soulsphere.set_colorkey(KDS.Colors.White)
turboneedle.set_colorkey(KDS.Colors.White)
pistol_mag.set_colorkey(KDS.Colors.White)
rk62_texture.set_colorkey(KDS.Colors.White)
rk62_f_texture.set_colorkey(KDS.Colors.White)
rk62_mag.set_colorkey(KDS.Colors.White)
medkit.set_colorkey(KDS.Colors.White)
shotgun.set_colorkey(KDS.Colors.White)
shotgun_f.set_colorkey(KDS.Colors.White)
shotgun_shells_t.set_colorkey(KDS.Colors.White)
ipuhelin_texture.set_colorkey(KDS.Colors.White)
ppsh41_f_texture.set_colorkey(KDS.Colors.White)
ppsh41_texture.set_colorkey(KDS.Colors.White)
awm_f_texture.set_colorkey(KDS.Colors.White)

ss_bonuscard.set_colorkey(KDS.Colors.Red)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Item Texture Loading Complete.")
#endregion
#region Menu Textures
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Menu Textures...")
gamemode_bc_1_1 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode_bc_1_1.png").convert()
gamemode_bc_1_2 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode_bc_1_2.png").convert()
gamemode_bc_2_1 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode_bc_2_1.png").convert()
gamemode_bc_2_2 = pygame.image.load("Assets/Textures/UI/Menus/Gamemode_bc_2_2.png").convert()
main_menu_background_2 = pygame.image.load("Assets/Textures/UI/Menus/main_menu_bc2.png").convert()
main_menu_background_3 = pygame.image.load("Assets/Textures/UI/Menus/main_menu_bc3.png").convert()
main_menu_background_4 = pygame.image.load("Assets/Textures/UI/Menus/main_menu_bc4.png").convert()
main_menu_background = pygame.image.load("Assets/Textures/UI/Menus/main_menu_bc.png").convert()
settings_background = pygame.image.load("Assets/Textures/UI/Menus/settings_bc.png").convert()
agr_background = pygame.image.load("Assets/Textures/UI/Menus/tcagr_bc.png").convert()
arrow_button = pygame.image.load("Assets/Textures/UI/Buttons/Arrow.png").convert_alpha()
main_menu_title = pygame.image.load("Assets/Textures/UI/Menus/main_menu_title.png").convert()
loadingScreen = pygame.image.load("Assets/Textures/UI/loadingScreen.png").convert()
main_menu_title.set_colorkey(KDS.Colors.White)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Menu Texture Loading Complete.")
#endregion
#region Audio
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Audio Files...")
gasburner_clip = pygame.mixer.Sound("Assets/Audio/Items/gasburner_pickup.ogg")
gasburner_fire = pygame.mixer.Sound("Assets/Audio/Items/gasburner_use.ogg")
door_opening = pygame.mixer.Sound("Assets/Audio/Tiles/door.ogg")
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
flicker_trigger_sound = pygame.mixer.Sound("Assets/Audio/Tiles/flicker_trigger.wav")
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
#Nice
KDS.Logging.Log(KDS.Logging.LogType.debug, "Audio File Loading Complete.")
#endregion
KDS.Logging.Log(KDS.Logging.LogType.debug, "Asset Loading Complete.")
#endregion
#region Variable Initialisation
ambient_tint = pygame.Surface(screen_size)
black_tint = pygame.Surface(screen_size)
black_tint.fill((20, 20, 20))
black_tint.set_alpha(170)

tmp_jukebox_data = tip_font.render("Use Jukebox [Click: E]", True, KDS.Colors.White)
tmp_jukebox_data2 = tip_font.render("Stop Jukebox [Hold: E]", True, KDS.Colors.White)
jukebox_tip = pygame.Surface((max(tmp_jukebox_data.get_width(), tmp_jukebox_data2.get_width()), tmp_jukebox_data.get_height() + tmp_jukebox_data2.get_height()))
jukebox_tip.blit(tmp_jukebox_data, ((tmp_jukebox_data2.get_width() - tmp_jukebox_data.get_width()) / 2, 0))
jukebox_tip.blit(tmp_jukebox_data2, ((tmp_jukebox_data.get_width() - tmp_jukebox_data2.get_width()) / 2, tmp_jukebox_data.get_height()))
del tmp_jukebox_data, tmp_jukebox_data2
decorative_head_tip = tip_font.render("Activate Head [Hold: E]", True, KDS.Colors.White)
respawn_anchor_tip = tip_font.render("Set Respawn Point [E]", True, KDS.Colors.White)
level_ender_tip = tip_font.render("Finish level [E]", True, KDS.Colors.White)
itemTip = tip_font.render("Nosta Esine [E]", True, KDS.Colors.White)

renderPadding = KDS.ConfigManager.GetSetting("Renderer/Tile/renderPadding", 4)
pauseOnFocusLoss = KDS.ConfigManager.GetSetting("Game/pauseOnFocusLoss", True)

restart = False
reset_data = False

colorInvert = False

monstersLeft = 0

main_running = True
plasmarifle_fire = False
gasburnerBurning = False
fireExtinguisherBurning = False
plasmabullets = []
tick = 0
knifeInUse = False
currently_on_mission = False
current_mission = "none"
weapon_fire = False
shoot = False

KDS.Logging.Log(KDS.Logging.LogType.debug, "Defining Variables...")
selectedSave = 0

explosion_positions = []
direction = True
esc_menu = False
onLadder = False
shotgun_loaded = True
shotgun_cooldown = 0
pistol_cooldown = 0
dark = False
darkness = (255, 255, 255)

gamemode_bc_1_alpha = KDS.Animator.Float(
    0.0, 255.0, 8, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
gamemode_bc_2_alpha = KDS.Animator.Float(
    0.0, 255.0, 8, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)

go_to_main_menu = False
go_to_console = False

main_menu_running = False
level_finished_running = False
tcagr_running = False
mode_selection_running = False
settings_running = False
vertical_momentum = 0
animation_counter = 0
animation_duration = 0
animation_image = 0
air_timer = 0
animation_has_played = False
death_wait = 0
attack_counter = 0
fart_counter = 0
monsterAmount = 0
monstersLeft = 0

renderPlayer = True

with open("Assets/Maps/map_names.txt", "r") as file:
    cntnts = file.read()
    cntnts = cntnts.split('\n')
    file.close()

map_names = tuple(cntnts)

Projectiles = []
Explosions = []
BallisticObjects = []
Lights = []
level_finished = False
Particles = []
HitTargets = {}
enemy_difficulty = 1
tiles = numpy.array([])
LightScroll = [0, 0]
onLadder = False
renderUI = True
godmode = False
walk_sound_delay = 0
ambient_light_tint = (255, 255, 255)
ambient_light = False
lightsUpdating = 0

Items = numpy.array([])
Enemies = numpy.array([])

true_scroll = [0, 0]

stand_size = (28, 63)
crouch_size = (28, 34)
jump_velocity = 2.0
check_crouch = False
koponen_rect = pygame.Rect(200, 200, 24, 64)
koponen_movement = [1, 6]
koponen_movingx = 0

koponen_talk_tip = tip_font.render(
    "Puhu Koposelle [E]", True, KDS.Colors.White)

task = ""
taskTaivutettu = ""

DebugMode = False

MenuMode = 0
game_pause_background = pygame.transform.scale(screen.copy(), display_size)

KDS.Logging.Log(KDS.Logging.LogType.debug, "Variable Defining Complete.")
#endregion
#region Game Settings
def LoadGameSettings():
    global fall_speed, fall_multiplier, fall_max_velocity, item_fall_speed, item_fall_max_velocity
    fall_speed = KDS.ConfigManager.GetGameData("Physics/Player/fallSpeed")
    fall_multiplier = KDS.ConfigManager.GetGameData("Physics/Player/fallMultiplier")
    fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Player/fallMaxVelocity")
    item_fall_speed = KDS.ConfigManager.GetGameData("Physics/Items/fallSpeed")
    item_fall_max_velocity = KDS.ConfigManager.GetGameData("Physics/Items/fallMaxVelocity")
LoadGameSettings()
#endregion
#region World Data
class WorldData():
    MapSize = (0, 0)
    @staticmethod
    def LoadMap(loadEntities: bool = True):
        global Items, tiles, Enemies, Projectiles
        MapPath = os.path.join("Assets", "Maps", "map" + current_map)
        PersistentMapPath = os.path.join(PersistentPaths.CachePath, "map")
        if os.path.isdir(PersistentMapPath):
            shutil.rmtree(PersistentMapPath)
        if os.path.isdir(MapPath):
            shutil.copytree(MapPath, PersistentMapPath)
        elif os.path.isfile(MapPath + ".map"):
            with zipfile.ZipFile(MapPath + ".map", "r") as mapZip:
                mapZip.extractall(PersistentMapPath)
        else:
            KDS.Logging.AutoError("Map file is not a valid format.")
            
        for fname in os.listdir(PersistentMapPath):
            fpath = os.path.join(PersistentMapPath, fname)
            if os.path.isdir(fpath):
                for _fname in os.listdir(fpath):
                    _fpath = os.path.join(fpath, _fname)
                    if os.path.isfile(_fpath):
                        shutil.copy(_fpath, PersistentMapPath)
                    else:
                        KDS.Logging.AutoError("Map file is not a valid format.")
                shutil.rmtree(fpath)
        with open(os.path.join(PersistentMapPath, "level.dat"), "r") as map_file:
            map_data = map_file.read().split("\n")

        global dark, darkness, ambient_light, ambient_light_tint
        dark = KDS.ConfigManager.GetLevelProp("Rendering/Darkness/enabled", False)
        dval = 255 - KDS.ConfigManager.GetLevelProp("Rendering/Darkness/strength", 0)
        darkness = (dval, dval, dval)
        ambient_light = KDS.ConfigManager.GetLevelProp("Rendering/AmbientLight/enabled", False)
        Player.light = KDS.ConfigManager.GetLevelProp("Rendering/Darkness/playerLight", True)
        ambient_light_tint = tuple(KDS.ConfigManager.GetLevelProp("Rendering/AmbientLight/tint", (255, 255, 255)))
        
        p_start_pos = KDS.ConfigManager.GetLevelProp("Entities/Player/startPos", (100, 100))
        k_start_pos = KDS.ConfigManager.GetLevelProp("Entities/Koponen/startPos", (200, 200))

        max_map_width = len(max(map_data))
        WorldData.MapSize = (max_map_width, len(map_data))

        # Luodaan valmiiksi koko kentän kokoinen numpy array täynnä ilma rectejä
        tiles = numpy.array([[Tile((x * 34, y * 34), 0) for x in range(
            WorldData.MapSize[0] + 1)] for y in range(WorldData.MapSize[1] + 1)])
        enemySerialNumbers = {
            1: KDS.AI.Imp,
            2: KDS.AI.SergeantZombie,
            3: KDS.AI.DrugDealer,
            4: KDS.AI.TurboShotgunner,
            5: KDS.AI.MafiaMan,
            6: KDS.AI.MethMaker,
            7: KDS.AI.CaveMonster
        }

        y = 0
        for row in map_data:
            x = 0
            for datapoint in row.split(" "):
                # Tänne jokaisen blockin käsittelyyn liittyvä koodi
                if datapoint != "/":
                    data = list(datapoint)
                    if len(data) > 1 and int(datapoint) != 0:
                        serialNumber = int(data[1] + data[2] + data[3])
                        if data[0] == "0":
                            if serialNumber not in specialTilesSerialNumbers:
                                tiles[y][x] = Tile((x * 34, y * 34), serialNumber=serialNumber)
                            else:
                                tiles[y][x] = specialTilesD[serialNumber](
                                    (x * 34, y * 34), serialNumber=serialNumber)
                        elif data[0] == "1":
                            if loadEntities:
                                Items = numpy.append(Items, Item.serialNumbers[serialNumber]((x * 34, y * 34), serialNumber=serialNumber, texture=i_textures[serialNumber]))
                        elif data[0] == "2":
                            if loadEntities:
                                Enemies = numpy.append(Enemies, enemySerialNumbers[serialNumber]((x*34,y*34)))
                        elif data[0] == "3":
                            temp_teleport = Teleport((x*34, y*34), serialNumber=serialNumber)
                            try: 
                                Teleport.teleportT_IDS[serialNumber].append(temp_teleport)
                            except KeyError:
                                Teleport.teleportT_IDS[serialNumber] = []
                                Teleport.teleportT_IDS[serialNumber].append(temp_teleport)                               
                            tiles[y][x] = temp_teleport
                            del temp_teleport
                else:
                    x += 1
            y += 1

        for row in tiles:
            for tile in row:
                if tile.serialNumber == 22:
                    tile.initHeight(tiles)

        KDS.Audio.Music.play(os.path.join(PersistentMapPath, "music.ogg"))
        return p_start_pos, k_start_pos
#endregion
#region Data
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Data...")

with open ("Assets/Textures/build.json", "r") as f:
    data = f.read()
buildData = json.loads(data)

t_textures = {}
for t in buildData["tile_textures"]:
    t_textures[int(t)] = pygame.image.load("Assets/Textures/Tiles/" + buildData["tile_textures"][t]).convert()
    t_textures[int(t)].set_colorkey(KDS.Colors.White)

i_textures = {}
for i in buildData["item_textures"]:
    i_textures[int(i)] = pygame.image.load("Assets/Textures/Items/" + buildData["item_textures"][i]).convert()
    i_textures[int(i)].set_colorkey(KDS.Colors.White)

inventory_items = buildData["inventory_items"]

specialTilesSerialNumbers = buildData["special_tiles"]

inventoryDobulesSerialNumbers = buildData["item_doubles"]

path_sounds_temp = buildData["tile_sounds"]
path_sounds = {}
default_paths = os.listdir("Assets/Audio/Tiles/path_sounds/default")
sounds = []
for p in default_paths:
    sounds.append(pygame.mixer.Sound(os.path.join("Assets/Audio/Tiles/path_sounds/default", p)))
path_sounds["default"] = sounds
#for p in path_sounds_temp:
#    path_sounds[int(p)] = pygame.mixer.Sound(path_sounds_temp[p])
del path_sounds_temp, default_paths, sounds

sref = buildData["checkCollisionFalse"]

""" CRASHAA PELIN, JOTEN DISABLOITU VÄLIAIKAISESTI
Items.init(inventoryDobulesSerialNumbers, inventory_items)
"""
#region Inventory
class Inventory:
    emptySlot = "none"
    doubleItem = "doubleItem"

    def __init__(self, size: int):
        self.storage = [Inventory.emptySlot for _ in range(size)]
        self.size = size
        self.SIndex = 0

    def empty(self):
        self.storage = [Inventory.emptySlot for _ in range(self.size)]

    def render(self, Surface: pygame.Surface):
        pygame.draw.rect(Surface, (192, 192, 192), (10, 75, self.size*34, 34), 3)

        if not isinstance(self.storage[self.SIndex], str) and self.storage[self.SIndex].serialNumber in inventoryDobulesSerialNumbers:
            slotwidth = 68
        else:
            slotwidth = 34

        pygame.draw.rect(screen, (70, 70, 70), ((
            (self.SIndex) * 34) + 10, 75, slotwidth, 34), 3)

        index = 0
        for i in self.storage:
            if not isinstance(i, str) and i.serialNumber in i_textures:
                Surface.blit(i.texture, (int(index * 34 + 10 + i.texture_size[0] / 4), int(75 + i.texture_size[1] / 4)))
            index += 1

    def moveRight(self):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        self.SIndex += 1
        if self.SIndex < self.size:
            if self.storage[self.SIndex] == Inventory.doubleItem:
                self.SIndex += 1

        if self.SIndex >= self.size:
            self.SIndex = 0

    def moveLeft(self):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        self.SIndex -= 1
        if self.SIndex >= 0:
            if self.storage[self.SIndex] == Inventory.doubleItem:
                self.SIndex -= 1
                
        if self.SIndex < 0:
            self.SIndex = self.size - 1
            if self.storage[self.SIndex] == Inventory.doubleItem:
                self.SIndex -= 1

    def pickSlot(self, index: int):
        KDS.Missions.Listeners.InventorySlotSwitching.Trigger()
        if 0 <= index <= len(self.storage)-1:
            if self.storage[index] == Inventory.doubleItem:
                self.SIndex = index - 1
            else:
                self.SIndex = index

    def dropItem(self):
        if self.storage[self.SIndex] != Inventory.emptySlot:
            if self.SIndex < self.size - 1:
                if self.storage[self.SIndex + 1] == Inventory.doubleItem:
                    self.storage[self.SIndex + 1] = Inventory.emptySlot
                elif self.storage[self.SIndex] == 6:
                    KDS.Missions.Listeners.iPuhelinDrop.Trigger()
            temp = self.storage[self.SIndex]
            self.storage[self.SIndex] = Inventory.emptySlot
            return temp

    def useItem(self, Surface: pygame.Surface, *args):
        if not isinstance(self.storage[self.SIndex], Lantern) and self.storage[self.SIndex] != Inventory.emptySlot and self.storage[self.SIndex] != Inventory.doubleItem:
            dumpValues = self.storage[self.SIndex].use(args, Surface)
            if Player.direction:
                renderOffset = -dumpValues.get_size()[0]
            else:
                renderOffset = Player.rect.width + 2

            Surface.blit(pygame.transform.flip(dumpValues, Player.direction, False), (Player.rect.x - scroll[0] + renderOffset, Player.rect.y + 10 -scroll[1]))
        return None

    def useSpecificItem(self, index: int, Surface: pygame.Surface, *args):
        dumpValues = nullLantern.use(args, Surface)
        if direction:
            renderOffset = -dumpValues.get_size()[0]
        else:
            renderOffset = Player.rect.width + 2

        Surface.blit(pygame.transform.flip(dumpValues, direction, False), (Player.rect.x - scroll[0] + renderOffset, Player.rect.y + 10 -scroll[1]))
        return None

    def getHandItem(self):
        return self.storage[self.SIndex]

    def getCount(self):
        count = 0
        for i in range(self.size):
            if self.storage[i] != Inventory.emptySlot:
                count += 1
        return count
#endregion

KDS.Logging.Log(KDS.Logging.LogType.debug, "Data Loading Complete.")

#region Tiles
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Tiles...")
class Tile:
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.serialNumber = serialNumber
        if serialNumber:
            self.texture = t_textures[serialNumber]
            self.air = False
        else:
            self.air = True
        self.specialTileFlag = True if serialNumber in specialTilesSerialNumbers else False
        self.checkCollision = True if self.serialNumber not in sref else False

    @staticmethod
    # Tile_list is a 2d numpy array
    def renderUpdate(Tile_list, Surface: pygame.Surface, scroll: list, center_position: Tuple[int, int], *args):
        tilesUpdating = 0
        x = round((center_position[0] / 34) - ((Surface.get_width() / 34) / 2)) - 1 - renderPadding
        y = round((center_position[1] / 34) - ((Surface.get_height() / 34) / 2)) - 1 - renderPadding
        x = max(x, 0)
        y = max(y, 0)
        max_x = len(Tile_list[0])
        max_y = len(Tile_list)
        end_x = round((center_position[0] / 34) + ((Surface.get_width() / 34) / 2)) + renderPadding
        end_y = round((center_position[1] / 34) + ((Surface.get_height() / 34) / 2)) + renderPadding
        end_x = min(end_x, max_x)
        end_y = min(end_y, max_y)
        for row in Tile_list[y : end_y]:
            for renderable in row[x : end_x]:
                if not renderable.air:
                    tilesUpdating += 1
                    if not renderable.specialTileFlag:
                        Surface.blit(renderable.texture, (renderable.rect.x -
                                                        scroll[0], renderable.rect.y - scroll[1]))
                    else: 
                        Surface.blit(renderable.update(), (renderable.rect.x -
                                                        scroll[0], renderable.rect.y - scroll[1]))                        

    def update(self):
        return self.texture
        
class Toilet(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int, _burning=False):        
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = t_textures[serialNumber]
        self.animation = KDS.Animator.Animation("toilet_anim", 3, 5, (KDS.Colors.White), KDS.Animator.OnAnimationEnd.Loop)
        self.checkCollision = True
        self.light_scale = 150

    def update(self):
        global renderPlayer
        if KDS.Math.getDistance((Player.rect.centerx, Player.rect.centery), self.rect.center) < 50 and gasburnerBurning and not self.burning:
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
            Lights.append(KDS.World.Lighting.Light(self.rect.center, pygame.transform.scale(KDS.World.Lighting.Shapes.circle.get(256, 1700), (self.light_scale, self.light_scale)), True))
            return self.animation.update()
        else:
            return self.texture

class Trashcan(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int, _burning=False):        
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = trashcan
        self.animation = KDS.Animator.Animation("trashcan", 3, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.checkCollision = True
        self.light_scale = 150

    def update(self):
        
        if KDS.Math.getDistance((Player.rect.centerx, Player.rect.centery), self.rect.center) < 48 and gasburnerBurning and not self.burning:
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
            Lights.append(KDS.World.Lighting.Light(self.rect.center, pygame.transform.scale(KDS.World.Lighting.Shapes.circle.get(256, 1700), (self.light_scale, self.light_scale)), True))
            return self.animation.update()
        else:
            return self.texture

class Jukebox(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):      
        positionC = (position[0], position[1] - 26)
        super().__init__(positionC, serialNumber)
        self.texture = jukebox_texture
        self.rect = pygame.Rect(position[0], position[1] - 27, 40, 60)
        self.checkCollision = False
        self.playing = -1
        self.lastPlayed = [-69 for _ in range(5)]
        
        musikerna = os.listdir("Assets/Audio/JukeboxMusic/")
        self.songs = []
        for musiken in musikerna:
            self.songs.append(pygame.mixer.Sound("Assets/Audio/JukeboxMusic/" + musiken))
        random.shuffle(self.songs)

    def stopPlayingTrack(self):
        for music in self.songs:
            music.stop()
        self.playing = -1
        KDS.Audio.Music.unpause()

    def update(self):
        if self.rect.colliderect(Player.rect):
            screen.blit(jukebox_tip, (self.rect.centerx - scroll[0] - jukebox_tip.get_width() / 2, self.rect.y - scroll[1] - 30))
            if KDS.Keys.functionKey.clicked and not KDS.Keys.functionKey.holdClicked:
                self.stopPlayingTrack()
                KDS.Audio.Music.pause()
                loopStopper = 0
                while (self.playing in self.lastPlayed or self.playing == -1) and loopStopper < 10:
                    self.playing = random.randint(0, len(self.songs) - 1)
                    loopStopper += 1
                del self.lastPlayed[0]
                self.lastPlayed.append(self.playing)
                KDS.Audio.playSound(self.songs[self.playing], KDS.Audio.MusicVolume)
            elif KDS.Keys.functionKey.held: self.stopPlayingTrack()
        if self.playing != -1:
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, Player.rect.midbottom) / 350
            jukebox_volume = KDS.Math.Lerp(1, 0, KDS.Math.Clamp(lerp_multiplier, 0, 1))
            self.songs[self.playing].set_volume(jukebox_volume)

        return self.texture

class Door(Tile):
    keys = {
        24: "red",
        25: "blue",
        26: "green"
    }

    def __init__(self, position: Tuple[int, int], serialNumber: int, closingCounter = 600):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = door_open
        self.rect = pygame.Rect(position[0], position[1], 5, 68)
        self.checkCollision = True
        self.open = False
        self.maxclosingCounter = closingCounter
        self.closingCounter = 0
    
    def update(self):
        if self.open:
            self.closingCounter += 1
            if self.closingCounter > self.maxclosingCounter:
                KDS.Audio.playSound(door_opening)
                self.open = False
                self.checkCollision = True
                self.closingCounter = 0
        if KDS.Math.getDistance(Player.rect.midbottom, self.rect.midbottom) < 20 and KDS.Keys.functionKey.clicked:
            if self.serialNumber == 23 or Player.keys[Door.keys[self.serialNumber]]:
                KDS.Audio.playSound(door_opening)
                self.closingCounter = 0
                self.open = not self.open
                if not self.open:
                    if self.rect.centerx - Player.rect.centerx > 0: Player.rect.right = self.rect.left
                    else: Player.rect.left = self.rect.right
                self.checkCollision = not self.checkCollision
        return self.texture if not self.open else self.opentexture

class Landmine(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = landmine_texture
        self.rect = pygame.Rect(position[0], position[1]+26, 22, 11)
        self.checkCollision = False

    def update(self):
        if self.rect.colliderect(Player.rect) or True in map(lambda r: r.rect.colliderect(self.rect), Enemies):
            if KDS.Math.getDistance(Player.rect.center, self.rect.center) < 100:
                Player.health -= 100 - KDS.Math.getDistance(Player.rect.center, self.rect.center)
            for enemy in Enemies:
                if KDS.Math.getDistance(enemy.rect.center, self.rect.center) < 100:
                    enemy.health -= 120 - KDS.Math.getDistance(enemy.rect.center, self.rect.center)
            self.air = True
            KDS.Audio.playSound(landmine_explosion)
            Explosions.append(KDS.World.Explosion(KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop), (self.rect.x - 60, self.rect.y - 60)))           
        return self.texture

class Ladder(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = ladder_texture
        self.rect = pygame.Rect(position[0]+6, position[1], 23, 34)
        self.checkCollision = False

    def update(self):
        global onLadder
        if self.rect.colliderect(Player.rect):
            onLadder = True
        return self.texture

class Lamp(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = lamp0
        self.rect = pygame.Rect(position[0], position[1], 14, 21)
        self.checkCollision = True
        self.coneheight = 90

    def initHeight(self, tiles):
        y = 0
        r = True
        while r:
            y += 33
            for row in tiles:
                for tile in row:
                    if not tile.air and tile.rect.collidepoint((self.rect.centerx, self.rect.y + self.rect.height + y)) and tile.serialNumber != 22 and tile.checkCollision:
                        y = y - (self.rect.y + self.rect.height + y - tile.rect.y) + 8
                        r = False
            if y > 154:
                r = False
        self.coneheight = y

    def update(self):
        if random.randint(0, 10) != 10:
            btmidth = int(self.coneheight*80/90)
            Lights.append(KDS.World.Lighting.Light((self.rect.x - btmidth/2 + 7, self.rect.y + 16), KDS.World.Lighting.lamp_cone(10, btmidth, self.coneheight, (200, 200, 200))))
        return self.texture

class DecorativeHead(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[43]
        self.rect = pygame.Rect(position[0], position[1]-26, 28, 60)
        self.checkCollision = False
        self.praying = False
        self.prayed = False

    def update(self):
        if self.rect.colliderect(Player.rect):
            if not self.prayed:
                screen.blit(decorative_head_tip, (self.rect.centerx - scroll[0] - int(decorative_head_tip.get_width() / 2), self.rect.top - scroll[1] - 20))
                if KDS.Keys.functionKey.pressed:
                    if not self.praying and not self.prayed:
                        KDS.Audio.playSound(pray_sound)
                        self.praying = True
                else:
                    pray_sound.stop()
                    self.praying = False
                if KDS.Keys.functionKey.held:
                    self.prayed = True
                    self.justPrayed = True
                    KDS.Audio.playSound(decorative_head_wakeup_sound)
            else:
                if not KDS.Keys.functionKey.pressed:
                    pray_sound.stop()
                    self.praying = False
                if Player.health > 0: Player.health = min(Player.health + 0.01, 100)
        else:
            pray_sound.stop()
            self.praying = False
        if self.prayed:
            if dark:
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 1900), True))
            else:
                day_light = KDS.World.Lighting.Shapes.circle.get(150, 1900).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - int(day_light.get_width() / 2), self.rect.centery - scroll[1] - int(day_light.get_height() / 2)))
        return self.texture

class Tree(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]-50, 47, 84)
        self.checkCollision = False

    def update(self):
        return self.texture

class Rock0(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]+19, 32, 15)
        self.checkCollision = True

    def update(self):
        return self.texture

class Torch(Tile):
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
        Lights.append(KDS.World.Lighting.Light((self.rect.x - 64, self.rect.y - 70), KDS.World.Lighting.Shapes.circle.get(self.light_scale, 1850)))
        return self.texture.update()

class GoryHead(Tile):
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
            self.texture = blh
            HitTargets.pop(self)
        return self.texture

class LevelEnder(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):       
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1] - 16, 34, 50)
        self.checkCollision = False

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx, self.rect.top + 10), KDS.World.Lighting.Shapes.circle.get(40, 40000), True))
        if self.rect.colliderect(Player.rect):
            screen.blit(level_ender_tip, (self.rect.centerx - level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                KDS.Missions.Listeners.LevelEnder.Trigger()
        return t_textures[self.serialNumber]
    
class LevelEnderDoor(Tile):
    def __init__(self, position: Tuple[int, int], serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = exit_door_open
        self.rect = pygame.Rect(position[0], position[1] - 34, 34, 68)
        self.checkCollision = False
        self.opened = False

    def update(self):
        if self.rect.colliderect(Player.rect):
            screen.blit(level_ender_tip, (self.rect.centerx - level_ender_tip.get_width() / 2 - scroll[0], self.rect.centery - 50 - scroll[1]))
            if KDS.Keys.functionKey.clicked:
                KDS.Missions.Listeners.LevelEnder.Trigger()
                KDS.Audio.playSound(door_opening)
                self.opened = True
        return t_textures[self.serialNumber] if not self.opened else self.opentexture

class Candle(Tile):
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
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - self.light_scale / 2, self.rect.y - self.light_scale / 2), KDS.World.Lighting.Shapes.circle.get(self.light_scale, 2000)))
        return self.texture.update()

class Teleport(Tile):
    tex = pygame.image.load("Assets/Textures/Misc/telep.png").convert()
    tex.set_colorkey((255, 255, 255))
    def __init__(self, position: Tuple[int, int], serialNumber: int):        
        super().__init__(position, 1)
        self.texture = Teleport.tex
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.checkCollision = False
        self.specialTileFlag = True
        self.teleportReady = True
        self.serialNumber = serialNumber
    
    def update(self):
        #Calculating next teleport with same serial number
        index = Teleport.teleportT_IDS[self.serialNumber].index(self) + 1
        if index > len(Teleport.teleportT_IDS[self.serialNumber]) - 1:
            index = 0
        if self.rect.colliderect(Player.rect) and Teleport.teleportT_IDS[self.serialNumber][Teleport.teleportT_IDS[self.serialNumber].index(self)].teleportReady: #Checking if teleporting is possible
            #Executing teleporting process
            Player.rect.center = (Teleport.teleportT_IDS[self.serialNumber][index].rect.centerx, Teleport.teleportT_IDS[self.serialNumber][index].rect.y - 17)
            Teleport.teleportT_IDS[self.serialNumber][index].teleportReady = False
            Teleport.last_teleported = True
            #Reseting scroll
            true_scroll[0] += (Player.rect.x - true_scroll[0] - (screen_size[0] / 2))
            true_scroll[1] += (Player.rect.y - true_scroll[1] - 220) 
        if not self.rect.colliderect(Player.rect): #Checking if it is possible to release teleport from teleport-lock
            Teleport.teleportT_IDS[self.serialNumber][Teleport.teleportT_IDS[self.serialNumber].index(self)].teleportReady = True

        return pygame.Surface((0, 0))

    teleportT_IDS = {}

class LampPoleLamp(Tile):
    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[58]
        self.rect = pygame.Rect(position[0]-6, position[1]-6, 40, 40)
        self.checkCollision = False
    
    def update(self):
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5000), True))
        return self.texture

class Chair(Tile):
    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[59]
        self.rect = pygame.Rect(position[0]-6, position[1]-8, 40, 42)
        self.checkCollision = False

    def update(self):
        return self.texture

class SkullTile(Tile):
    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[66]
        self.rect = pygame.Rect(position[0]+7, position[1]+7, 27, 27)
        self.checkCollision = False

    def update(self):
        return self.texture

class WallLight(Tile):
    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[71]
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.checkCollision = False
        self.direction = True if serialNumber == 72 else False
        self.texture = pygame.transform.flip(self.texture, self.direction, False)
        self.light_t = pygame.transform.flip(KDS.World.Lighting.Shapes.cone_hard.get(100, 6200), self.direction, False).convert_alpha()

    def update(self):
        Lights.append(KDS.World.Lighting.Light((self.rect.centerx - 17 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery), self.light_t, True))
        return self.texture

class RespawnAnchor(Tile):
    respawnPoint = None
    active = None
    rspP_list = []
    
    def __init__(self, position, serialNumber: int):
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.ontexture = respawn_anchor_on
        self.checkCollision = False
        self.sound = random.choice(respawn_anchor_sounds)
        RespawnAnchor.rspP_list.append(self)
    
    def update(self):
        if RespawnAnchor.active == self:
            if dark:
                Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.circle.get(150, 2400), True))
            else:
                day_light = KDS.World.Lighting.Shapes.splatter.get(150, 2400).copy()
                day_light.fill((255, 255, 255, 32), None, pygame.BLEND_RGBA_MULT)
                screen.blit(day_light, (self.rect.centerx - scroll[0] - int(day_light.get_width() / 2), self.rect.centery - scroll[1] - int(day_light.get_height() / 2)))
            return self.ontexture
        elif self.rect.colliderect(Player.rect):
            screen.blit(respawn_anchor_tip, (self.rect.centerx - scroll[0] - int(respawn_anchor_tip.get_width() / 2), self.rect.top - scroll[1] - 50))
            if KDS.Keys.functionKey.clicked:
                RespawnAnchor.active = self
                RespawnAnchor.respawnPoint = (self.rect.x, self.rect.y - Player.rect.height + 34)
                loopStopper = 0
                oldSound = self.sound
                while self.sound == oldSound and loopStopper < 10:
                    self.sound = random.choice(respawn_anchor_sounds)
                    loopStopper += 1
                KDS.Audio.playSound(self.sound)
        return self.texture

class Spruce(Tile):
    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] - 10, position[1] - 40, 63, 75)
        self.checkCollision = False

    def update(self):
        return self.texture
    
class AllahmasSpruce(Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.rect = pygame.Rect(position[0] - 10, position[1] - 40, 63, 75)
        self.checkCollision = False
        self.spruce_kColors = (1000, 2500, 40000)
        self.colorIndex = 0
        self.colorTicks = 60
        self.colorTick = 0
        
    def update(self):
        self.colorTick += 1
        if self.colorTick > self.colorTicks:
            self.colorTick = 0
            self.colorIndex += 1
            self.colorIndex = 0 if self.colorIndex >= len(self.spruce_kColors) else self.colorIndex
        Lights.append(KDS.World.Lighting.Light(self.rect.center, KDS.World.Lighting.Shapes.splatter.get(150, self.spruce_kColors[self.colorIndex]), True))
        return self.texture

class Methtable(Tile):

    o_sounds = [pygame.mixer.Sound("Assets/Audio/Tiles/methtable_0.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/methtable_1.ogg"), pygame.mixer.Sound("Assets/Audio/Tiles/methtable_2.ogg")]

    def __init__(self, position, serialNumber: int):        
        super().__init__(position, serialNumber)
        self.animation = KDS.Animator.Animation("methtable", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        for index, im in enumerate(self.animation.images):
            self.animation.images[index] = pygame.transform.scale(im, (int(im.get_width()/2.5), int(im.get_height()/2.5)))
        self.rect = pygame.Rect(position[0] - (self.animation.images[0].get_width() - 34), position[1] - (self.animation.images[0].get_height() - 34), self.animation.images[0].get_width(), self.animation.images[0].get_height())
        self.checkCollision = False

    def update(self):
        if random.randint(0, 105) == 50 and KDS.Math.getDistance(self.rect.center, Player.rect.center) < 355:
            KDS.Audio.playSound(random.choice(Methtable.o_sounds))
        return self.animation.update()

class FlickerTrigger(Tile):
    def __init__(self, position, serialNumber, repeating: bool = False, animationLength: int = 12, animationSpeed: int = 2) -> None:
        super().__init__(position, serialNumber)
        self.checkCollision = False
        self.exited = True
        self.tick = 0
        self.ticks = animationLength
        self.anim = False
        self.animTick = 0
        self.animTicks = animationSpeed
        self.repeating = repeating
        self.stopAnim = False
    
    def update(self):
        if self.rect.colliderect(Player.rect):
            if self.exited:
                self.anim = True
                self.exited = False
                KDS.Audio.pauseAllSounds()
                KDS.Audio.playSound(flicker_trigger_sound)
        else:
            if self.repeating: self.tick = 0
            self.exited = True
            self.stopAnim = True
        if self.tick < self.ticks:
            if self.anim:
                self.tick += 1
                if self.animTick >= self.animTicks: self.animTick = 0
                global colorInvert
                if self.animTick == 0: colorInvert = True
                self.animTick += 1
        else:
            self.stopAnim = True
        
        if self.stopAnim:
            self.anim = False
            flicker_trigger_sound.stop()
            KDS.Audio.unpauseAllSounds()
            self.stopAnim = False
            
        return pygame.Surface((0, 0))

class ImpaledBody(Tile):
    def __init__(self, position, serialNumber) -> None:
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.animation = KDS.Animator.Animation("impaled_corpse", 2, 50, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        self.rect = pygame.Rect(position[0] - (self.animation.images[0].get_width() - 34), position[1] - (self.animation.images[0].get_height() - 34), self.animation.images[0].get_width(), self.animation.images[0].get_height())
        self.checkCollision = False

    def update(self):
        return self.animation.update()
        
specialTilesD = {
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
    85: ImpaledBody
}

KDS.Logging.Log(KDS.Logging.LogType.debug, "Tile Loading Complete.")
#endregion

#region Items
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Items...")
class Item:

    serialNumbers = {}

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture: pygame.Surface = None):
        self.texture = texture
        self.texture_size = self.texture.get_size() if self.texture != None else (0, 0)
        self.rect = pygame.Rect(position[0], position[1] + (34 - self.texture_size[1]), self.texture_size[0], self.texture_size[1])
        self.serialNumber = serialNumber
        self.physics = False
        self.momentum = 0

    @staticmethod
    # Item_list is a 2d numpy array
    def renderUpdate(Item_list, Surface: pygame.Surface, scroll: list, DebugMode = False):
        for renderable in Item_list:
            if DebugMode:
                pygame.draw.rect(Surface, KDS.Colors.Blue, pygame.Rect(renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
            if renderable.texture != None:
                Surface.blit(renderable.texture, (renderable.rect.x - scroll[0], renderable.rect.y-scroll[1]))
            if renderable.physics:
                renderable.momentum = min(renderable.momentum + item_fall_speed, item_fall_max_velocity)
                renderable.rect.y += renderable.momentum
                collisions = KDS.World.collision_test(renderable.rect, tiles)
                if len(collisions) > 0:
                    renderable.rect.bottom = collisions[0].rect.top
                    renderable.physics = False

    @staticmethod
    def checkCollisions(Item_list: Any, collidingRect: pygame.Rect, Surface: pygame.Surface, scroll: Tuple[int, int], functionKey: bool, inventory: Inventory) -> Tuple[Any, Inventory]:
        index = 0
        showItemTip = True
        collision = False
        shortest_index = 0
        shortest_distance = sys.maxsize
        for item in Item_list:
            if collidingRect.colliderect(item.rect):
                collision = True
                distance = KDS.Math.getDistance(item.rect.midbottom, collidingRect.midbottom)
                if distance < shortest_distance:
                    shortest_index = index
                    shortest_distance = distance
                if functionKey:
                    if item.serialNumber not in inventoryDobulesSerialNumbers:
                        if inventory.storage[inventory.SIndex] == "none":
                            temp_var = item.pickup()
                            if not temp_var:
                                inventory.storage[inventory.SIndex] = item
                                if item.serialNumber == 6:
                                    KDS.Missions.Listeners.iPuhelinPickup.Trigger()
                            Item_list = numpy.delete(Item_list, index)
                            showItemTip = False
                        elif item.serialNumber not in inventory_items:
                            try:
                                item.pickup()
                                Item_list = numpy.delete(Item_list, index)
                                showItemTip = False
                            except IndexError as e:
                                KDS.Logging.Log(KDS.Logging.LogType.critical, f"A non-inventory item was tried to pick up and caused error: {e}")
                    else:
                        if inventory.SIndex < inventory.size-1 and inventory.storage[inventory.SIndex] == "none":
                            if inventory.storage[inventory.SIndex + 1] == "none":
                                item.pickup()
                                inventory.storage[inventory.SIndex] = item
                                inventory.storage[inventory.SIndex + 1] = Inventory.doubleItem
                                Item_list = numpy.delete(Item_list, index)
                                showItemTip = False
            index += 1
        
        if collision and showItemTip:
            Surface.blit(itemTip, (Item_list[shortest_index].rect.centerx - int(itemTip.get_width() / 2) - scroll[0], Item_list[shortest_index].rect.bottom - 45 - scroll[1]))

        return Item_list, inventory

    def toSave(self):
        """Converts all textures to strings
        """
        if not isinstance(self.texture, list):
            self.texture = pygame.surfarray.array2d(self.texture).tolist()
            
    def fromSave(self):
        """Converts all strings back to textures
        """
        if isinstance(self.texture, list):
            self.texture = pygame.surfarray.make_surface(numpy.array(self.texture)).convert()
            self.texture.set_colorkey(KDS.Colors.White)

    def pickup(self):
        
        return False

    def use(self, *args):
        return self.texture

    def drop(self):
        pass

    def init(self):
        pass

class BlueKey(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Audio.playSound(key_pickup)
        Player.keys["blue"] = True

        return True

class Cell(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Scores.score += 4
        KDS.Audio.playSound(item_pickup)
        Plasmarifle.ammunition += 30
        return True

class Coffeemug(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        KDS.Scores.score += 6
        KDS.Audio.playSound(coffeemug_sound)
        return False

class Gasburner(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global gasburnerBurning
        
        if args[0][0] == True:
            gasburnerBurning = True
            gasburner_fire.stop()
            KDS.Audio.playSound(gasburner_fire)
            return gasburner_animation_object.update()
        else:
            gasburner_fire.stop()
            gasburnerBurning = False
            return gasburner_off

    def pickup(self):
        KDS.Scores.score += 12
        KDS.Audio.playSound(gasburner_clip)
        return False

class GreenKey(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Audio.playSound(key_pickup)
        Player.keys["green"] = True

        return True

class iPuhelin(Item):
    #pickup_sound = pygame.mixer.Sound("Assets/Audio/Legacy/apple_o_paskaa.ogg")
    realistic_texture = pygame.image.load("Assets/Textures/Items/iPuhelin_realistic.png").convert()
    realistic_texture.set_colorkey(KDS.Colors.White)
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)
        self.useCount = 0

    def use(self, *args):
        if KDS.Keys.functionKey.clicked:
            self.useCount += 1
        if self.useCount > 7:
            self.useCount = 7
            self.texture = iPuhelin.realistic_texture
        return self.texture

    def pickup(self):
        KDS.Scores.score -= 6
        KDS.Audio.playSound(item_pickup)
        return False

class Knife(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        if args[0][0]:
            if KDS.World.knife_C.counter > 40:
                KDS.World.knife_C.counter = 0
                Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 13 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 1, 1),direction, -1, tiles, 25, maxDistance=40))
            KDS.World.knife_C.counter  += 1
            return knife_animation_object.update()
        else:
            KDS.World.knife_C.counter  += 1
            if KDS.World.knife_C.counter > 100:
                KDS.World.knife_C.counter = 100
            return knife

    def pickup(self):
        KDS.Scores.score += 15
        KDS.Audio.playSound(knife_pickup)
        return False

class LappiSytytyspalat(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        KDS.Scores.score += 14
        KDS.Audio.playSound(lappi_sytytyspalat_sound)
        return True

class Medkit(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Audio.playSound(item_pickup)
        Player.health = min(Player.health + 25, 100)
        return True

class Pistol(Item):
    
    ammunition = 8

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global tiles
        if args[0][0] and KDS.World.pistol_C.counter > 30 and Pistol.ammunition > 0:
            KDS.Audio.playSound(pistol_shot)
            KDS.World.pistol_C.counter = 0
            Pistol.ammunition -= 1
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 30 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 2, 2),direction, -1, tiles, 100))
            return pistol_f_texture
        else:
            KDS.World.pistol_C.counter += 1
            return pistol_texture

    def pickup(self):
        KDS.Scores.score += 18
        KDS.Audio.playSound(weapon_pickup)
        return False

class PistolMag(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        Pistol.ammunition += 7
        KDS.Scores.score += 7
        KDS.Audio.playSound(item_pickup)
        return True

class rk62(Item):

    ammunition = 30

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global tiles
        if args[0][0] and KDS.World.rk62_C.counter > 4 and rk62.ammunition > 0:
            KDS.World.rk62_C.counter = 0
            rk62_shot.stop()
            KDS.Audio.playSound(rk62_shot)
            rk62.ammunition -= 1
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 50 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 2, 2), direction, -1, tiles, 25))
            return rk62_f_texture
        else:
            if not args[0][0]:
                rk62_shot.stop() 
            KDS.World.rk62_C.counter += 1
            return rk62_texture

    def pickup(self):
        KDS.Scores.score += 29
        KDS.Audio.playSound(weapon_pickup)
        return False

class Shotgun(Item):

    ammunition = 8

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global tiles
        if args[0][1] and KDS.World.shotgun_C.counter > 50 and Shotgun.ammunition > 0:
            KDS.World.shotgun_C.counter = 0
            KDS.Audio.playSound(shotgun_shot)
            Shotgun.ammunition -= 1
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            for x in range(10):
                Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 60 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 2, 2), direction, -1, tiles, 25, maxDistance=1400, slope=3 - x / 1.5))
            return shotgun_f
        else:
            KDS.World.shotgun_C.counter += 1
            return shotgun

    def pickup(self):
        KDS.Scores.score += 23
        KDS.Audio.playSound(weapon_pickup)
        return False

class rk62Mag(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        rk62.ammunition += 30
        KDS.Scores.score += 8
        KDS.Audio.playSound(item_pickup)
        return True

class ShotgunShells(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        Shotgun.ammunition += 4
        KDS.Scores.score += 5
        KDS.Audio.playSound(item_pickup)
        return True

class Plasmarifle(Item):

    ammunition = 36

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):               
        if args[0][0] and Plasmarifle.ammunition > 0 and KDS.World.plasmarifle_C.counter > 3:
            KDS.World.plasmarifle_C.counter = 0
            KDS.Audio.playSound(plasmarifle_f_sound)
            Plasmarifle.ammunition -= 1
            if direction:
                temp = 100
            else:
                temp = -80
            Lights.append(KDS.World.Lighting.Light((Player.rect.centerx - temp / 1.4, Player.rect.centery - 30), KDS.World.Lighting.Shapes.circle.get(40, 40000)))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx - temp,Player.rect.centery - 19, 2, 2), direction, 27, tiles, 20, plasma_ammo, 2000, random.randint(-1, 1)/27))
            return plasmarifle_animation.update()
        else:
            KDS.World.plasmarifle_C.counter += 1
            return plasmarifle

    def pickup(self):
        KDS.Scores.score += 25
        KDS.Audio.playSound(weapon_pickup)
        return False

class Soulsphere(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Scores.score += 20
        Player.health += 100
        KDS.Audio.playSound(item_pickup)
        return True

class RedKey(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        KDS.Audio.playSound(key_pickup)
        Player.keys["red"] = True

        return True

class SSBonuscard(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        KDS.Scores.score += 30
        KDS.Audio.playSound(ss_sound)
        return False

class Turboneedle(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        return True

class Ppsh41(Item):

    ammunition = 72

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global tiles
        if args[0][0] and KDS.World.ppsh41_C.counter > 2 and Ppsh41.ammunition > 0:
            KDS.World.ppsh41_C.counter = 0
            smg_shot.stop()
            KDS.Audio.playSound(smg_shot)
            Ppsh41.ammunition -= 1
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 60 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 2, 2), direction, -1, tiles, 10, slope=random.uniform(-0.5, 0.5)))
            return ppsh41_f_texture
        else:
            if not args[0][0]:
                smg_shot.stop() 
            KDS.World.ppsh41_C.counter += 1
            return ppsh41_texture

    def pickup(self):
        return False

class Awm(Item):

    ammunition = 5

    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        global tiles, awm_ammo
        if args[0][0] and KDS.World.awm_C.counter > 130 and Awm.ammunition > 0:
            KDS.World.awm_C.counter = 0
            KDS.Audio.playSound(awm_shot)
            Awm.ammunition -= 1
            Lights.append(KDS.World.Lighting.Light(Player.rect.center, KDS.World.Lighting.Shapes.circle_hard.get(300, 5500), True))
            Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 90 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 19, 2, 2), direction, -1, tiles, random.randint(300, 590), slope=0))
            return awm_f_texture
        else:
            KDS.World.awm_C.counter += 1
            return i_textures[24]    

    def pickup(self):
        return False

class AwmMag(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        Awm.ammunition += 5
        KDS.Audio.playSound(item_pickup)
        
        return True

class EmptyFlask(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        KDS.Scores.score += 1
        KDS.Audio.playSound(coffeemug_sound)
        return False

class MethFlask(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        if args[0][0]:
            KDS.Scores.score += 1
            Player.health += random.choice([random.randint(10, 30), random.randint(-30, 30)])
            Player.inventory.storage[Player.inventory.SIndex] = Item.serialNumbers[26]((0, 0), 26, i_textures[26])
            KDS.Audio.playSound(glug_sound)
        return i_textures[27]

    def pickup(self):
        KDS.Scores.score += 10
        KDS.Audio.playSound(coffeemug_sound)
        return False

class BloodFlask(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        if args[0][0]:
            KDS.Scores.score += 1
            Player.health += random.randint(0, 10)
            Player.inventory.storage[Player.inventory.SIndex] = Item.serialNumbers[26]((0, 0), 26, i_textures[26])
            KDS.Audio.playSound(glug_sound)
        return i_textures[28]

    def pickup(self):
        KDS.Audio.playSound(coffeemug_sound)
        KDS.Scores.score += 7
        return False

class Grenade(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):

        if KDS.Keys.altUp.pressed:
            KDS.World.Grenade_O.Slope += 0.03
        elif KDS.Keys.altDown.pressed:
            KDS.World.Grenade_O.Slope -= 0.03

        pygame.draw.line(screen, (255, 10, 10), (Player.rect.centerx - scroll[0], Player.rect.y + 10 - scroll[1]), (Player.rect.centerx + (KDS.World.Grenade_O.force + 15)*KDS.Convert.ToMultiplier(direction) - scroll[0], Player.rect.y+ 10 + KDS.World.Grenade_O.Slope*(KDS.World.Grenade_O.force + 15)*-1 - scroll[1]) )
        if args[0][0]:
            KDS.Audio.playSound(grenade_throw)
            Player.inventory.storage[Player.inventory.SIndex] = Inventory.emptySlot
            BallisticObjects.append(KDS.World.BallisticProjectile((Player.rect.centerx, Player.rect.centery - 25), 10, 10, KDS.World.Grenade_O.Slope, KDS.World.Grenade_O.force, direction, gravitational_factor=0.4, flight_time=140, texture = i_textures[29]))
        return i_textures[29]

    def pickup(self):
        KDS.Scores.score += 7
        return False

class FireExtinguisher(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        return self.texture

    def pickup(self):
        return False

class LevelEnderItem(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        if args[0][0]:
            KDS.Missions.Listeners.LevelEnder.Trigger()

        return i_textures[31]

    def pickup(self):
        KDS.Audio.playSound(weapon_pickup)
        return False

class Ppsh41Mag(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)
    
    def pickup(self):
        KDS.Audio.playSound(item_pickup)
        Ppsh41.ammunition += 69

        return True

class Lantern(Item):
    Ianimation = KDS.Animator.Animation("lantern_burning", 2, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def use(self, *args):
        scale = random.randint(180, 220)
        Lights.append( KDS.World.Lighting.Light( (Player.rect.centerx - scale/2, Player.rect.centery - scale/2) , KDS.World.Lighting.Shapes.circle_hardest.get(scale, 5000).convert_alpha() ))
        return Lantern.Ianimation.update()

    def pickup(self):
        KDS.Audio.playSound(lantern_pickup)

        return False

nullLantern = Lantern((0, 0), 33, texture = i_textures[33])

class Chainsaw(Item):
    pickup_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_start.ogg")
    freespin_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_freespin.ogg")
    throttle_sound = pygame.mixer.Sound("Assets/Audio/Items/chainsaw_throttle.ogg")
    soundCounter = 70
    soundCounter1 = 122
    ammunition = 100.0
    a_a = False
    Ianimation = KDS.Animator.Animation("chainsaw_animation", 2, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)
        self.pickupFinished = False
        self.pickupCounter = 0

    def use(self, *args):
        if self.pickupFinished and Chainsaw.ammunition > 0:
            if args[0][0]:
                Chainsaw.ammunition = max(0, Chainsaw.ammunition - 0.05)
                Projectiles.append(KDS.World.Bullet(pygame.Rect(Player.rect.centerx + 18 * KDS.Convert.ToMultiplier(direction), Player.rect.centery - 4, 1, 1), direction, -1, tiles, damage=1, maxDistance=80))
                if Chainsaw.soundCounter > 70:
                    Chainsaw.freespin_sound.stop()
                    KDS.Audio.playSound(Chainsaw.throttle_sound)
                    Chainsaw.soundCounter = 0
                Chainsaw.a_a = True

            elif not args[0][0]:
                Chainsaw.a_a = False
                if Chainsaw.soundCounter1 > 103:
                    Chainsaw.soundCounter1 = 0
                    Chainsaw.throttle_sound.stop()
                    Chainsaw.ammunition = round(max(0, Chainsaw.ammunition - 0.1), 1)
                    KDS.Audio.playSound(Chainsaw.freespin_sound)
        else:
            self.pickupCounter += 1
            if self.pickupCounter > 180:
                self.pickupFinished = True
        Chainsaw.soundCounter += 1
        Chainsaw.soundCounter1 += 1
        if Chainsaw.a_a:
            return Chainsaw.Ianimation.update()
        return self.texture

    def pickup(self):
        KDS.Audio.playSound(Chainsaw.pickup_sound)
        return False

class GasCanister(Item):
    def __init__(self, position: Tuple[int, int], serialNumber: int, texture = None):
        super().__init__(position, serialNumber, texture)

    def pickup(self):
        Chainsaw.ammunition = min(100, Chainsaw.ammunition + 50)
        return True

Item.serialNumbers = {
    1: BlueKey,
    2: Cell,
    3: Coffeemug,
    4: Gasburner,
    5: GreenKey,
    6: iPuhelin,
    7: Knife,
    8: LappiSytytyspalat,
    9: Medkit,
    10:Pistol,
    11:PistolMag,
    12:Plasmarifle,
    13:RedKey,
    14:rk62Mag,
    15:rk62,
    16:Shotgun,
    17:ShotgunShells,
    18:Soulsphere,
    19:SSBonuscard,
    20:Turboneedle,
    21:Ppsh41,
    22:"",
    23:"",
    24:Awm,
    25:AwmMag,
    26:EmptyFlask,
    27:MethFlask,
    28:BloodFlask,
    29:Grenade,
    30:FireExtinguisher,
    31:LevelEnderItem,
    32:Ppsh41Mag,
    33:Lantern,
    34:Chainsaw,
    35:GasCanister
}
KDS.Logging.Log(KDS.Logging.LogType.debug, "Item Loading Complete.")
#endregion

#region Animations
koponen_animations = KDS.Animator.MultiAnimation(
    idle = KDS.Animator.Animation("koponen_idle", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
    walk = KDS.Animator.Animation("koponen_walk", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player")
)
menu_gasburner_animation = KDS.Animator.Animation(
    "main_menu_bc_gasburner", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
gasburner_animation_object = KDS.Animator.Animation(
    "gasburner_on", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
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

KDS.Logging.Log(KDS.Logging.LogType.debug, "Animation Loading Complete.")
KDS.Logging.Log(KDS.Logging.LogType.debug, "Game Initialisation Complete.")
#endregion
#endregion
#region Player
class PlayerClass:
    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(100, 100, stand_size[0], stand_size[1])
        self.name: str = "Sinä"
        self.health: float = 100.0
        self.lastHealth: float = self.health
        self.stamina: float = 100.0
        self.inventory: Inventory = Inventory(5)
        self.keys: Dict[str, bool] = { "red": False, "green": False, "blue": False }
        self.farting: bool = False
        self.light: bool = False
        self.godmode: bool = False
        self.dead: bool = False
        self.direction: bool = False
        self.walking: bool = False
        self.check_crouch: bool = False
        self.air_timer: int = 0
        self.movement: List[float] = [0, 0]
        self.walk_sound_delay: float = 9999
        self.vertical_momentum: float = 0
        self.animations: KDS.Animator.MultiAnimation = KDS.Animator.MultiAnimation(
            idle = KDS.Animator.Animation("idle", 2, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            walk = KDS.Animator.Animation("walk", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            run = KDS.Animator.Animation("walk", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            idle_short = KDS.Animator.Animation("idle_short", 2, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            walk_short = KDS.Animator.Animation("walk_short", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            run_short = KDS.Animator.Animation("walk_short", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Player"),
            death = KDS.Animator.Animation("death", 6, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop, animation_dir="Player")
        )
        self.deathSound: pygame.mixer.Sound = pygame.mixer.Sound("Assets/Audio/Effects/player_death.ogg")

    def reset(self):
        self.rect = pygame.Rect(100, 100, stand_size[0], stand_size[1])
        self.name = "Sinä"
        self.health = 100.0
        self.lastHealth = self.health
        self.stamina = 100.0
        self.inventory = Inventory(5)
        self.keys = { "red": False, "green": False, "blue": False }
        self.farting = False
        self.light = False
        self.dead = False
        self.animations.reset()
        self.deathSound.stop()
        
    def update(self):
        if self.godmode: self.health = 100.0
        if self.health > 0:
            self.movement = [0, 0]
            fspeed_copy = fall_speed
            if KDS.Keys.moveUp.pressed and KDS.Keys.moveUp.ticksHeld == 0 and not KDS.Keys.moveDown.pressed and self.air_timer < 6 and not onLadder:
                self.vertical_momentum = -10
            elif vertical_momentum > 0:
                fspeed_copy *= fall_multiplier
            elif not KDS.Keys.moveUp.pressed:
                fspeed_copy *= fall_multiplier
            if KDS.Keys.moveRun.pressed:
                if self.stamina <= 0: KDS.Keys.moveRun.SetState(False)
                else: self.stamina -= 0.75     
            elif self.stamina < 100.0: self.stamina += 0.25

            if KDS.Keys.moveRight.pressed:
                if not KDS.Keys.moveDown.pressed: self.movement[0] += 4
                else: self.movement[0] += 2
                if KDS.Keys.moveRun.pressed and self.stamina > 0: self.movement[0] += 4

            if KDS.Keys.moveLeft.pressed:
                if not KDS.Keys.moveDown.pressed: self.movement[0] -= 4
                else: self.movement[0] -= 2
                if KDS.Keys.moveRun.pressed and self.stamina > 0: self.movement[0] -= 4

            if not self.movement[0] or self.air_timer > 1:
                self.walk_sound_delay = 9999
            self.walk_sound_delay += abs(self.movement[0])
            s = (self.walk_sound_delay > 60) if play_walk_sound else False
            if s: self.walk_sound_delay = 0

            self.movement[1] += self.vertical_momentum
            self.vertical_momentum = min(self.vertical_momentum + fspeed_copy, fall_max_velocity)

            if self.check_crouch == True:
                crouch_collisions = KDS.World.move_entity(pygame.Rect(Player.rect.x, Player.rect.y - crouch_size[1], Player.rect.width, Player.rect.height), (0, 0), tiles, False, True)[1]
            else:
                crouch_collisions = KDS.World.Collisions()

            if KDS.Keys.moveDown.pressed and not onLadder and self.rect.height != crouch_size[1] and death_wait < 1:
                self.rect = pygame.Rect(self.rect.x, self.rect.y + (stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
                self.check_crouch = True
            elif (not KDS.Keys.moveDown.pressed or onLadder or death_wait > 0) and Player.rect.height != stand_size[1] and crouch_collisions.bottom == False:
                self.rect = pygame.Rect(self.rect.x, self.rect.y + (crouch_size[1] - stand_size[1]), stand_size[0], stand_size[1])
                self.check_crouch = False
            elif not KDS.Keys.moveDown.pressed and crouch_collisions.bottom == True and self.rect.height != crouch_size[1] and death_wait < 1:
                self.rect = pygame.Rect(self.rect.x, self.rect.y + (stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
                self.check_crouch = True
            self.rect, collisions = KDS.World.move_entity(self.rect, self.movement, tiles, w_sounds=path_sounds, playWalkSound=s)

            if collisions.bottom:
                self.air_timer = 0
                self.vertical_momentum = 0
            else:
                self.air_timer += 1
            if collisions.top:
                self.vertical_momentum = 0
            if self.movement[0] > 0:
                self.direction = False
                self.walking = True
            elif self.movement[0] < 0:
                self.direction = True
                self.walking = True
            else:
                self.walking = False
            if self.walking:
                if not KDS.Keys.moveRun.pressed:
                    if self.rect.height == stand_size[1]:
                        self.animations.trigger("walk")
                    else:
                        self.animations.trigger("walk_short")
                else:
                    if self.rect.height == stand_size[1]:
                        self.animations.trigger("run")
                    else:
                        self.animations.trigger("run_short")
            else:
                if self.rect.height == stand_size[1]:
                    self.animations.trigger("idle")
                else:
                    self.animations.trigger("idle_short")
            if self.health < self.lastHealth and self.health > 0: KDS.Audio.playSound(hurt_sound)
            self.lastHealth = self.health  
        else:
            self.animations.trigger("death")

Player = PlayerClass()
#endregion
#region Console
def console():
    global level_finished, go_to_console
    go_to_console = False

    itemDict = {}
    for itemKey in buildData["item_textures"]:
        if int(itemKey) in buildData["inventory_items"]: itemDict[os.path.splitext(buildData["item_textures"][itemKey])[0]] = itemKey
    itemDict["key"] = {}
    for key in Player.keys: itemDict["key"][key] = "break"
    
    trueFalseTree = {"true": "break", "false": "break"}
    
    commandTree = {
        "give": itemDict,
        "remove": {
            "item": "break",
            "key": "break"
        },
        "playboy": "break",
        "kill": "break",
        "stop": "break",
        "killme": "break",
        "terms": trueFalseTree,
        "woof": trueFalseTree,
        "invl": trueFalseTree,
        "finish": { "missions": "break" },
        "teleport": {
         "~": { "~": "break" },
        },
        "summon": {
            "imp": "break",
            "sergeant": "break",
            "drugdealer": "break",
            "supershotgunner": "break",
            "methmaker": "break",
            "fucker69": "break" 
        }
    }
    
    consoleRunning = True
    
    blurred_background = KDS.Convert.ToBlur(game_pause_background, 6)
    
    #command_input = input("command: ")
    """
    command_input = inputConsole("Command >>> ")
    if not command_input:
        return None
    command_input = command_input.lower()
    command_list = command_input.split()
    """
    while consoleRunning:
        command_list: list = KDS.Console.Start(prompt="Enter Command:", allowEscape=True, checkType=KDS.Console.CheckTypes.Commands(), background=blurred_background, commands=commandTree, autoFormat=True, enableOld=True, showFeed=True)
        if command_list == None:
            consoleRunning = False
            break

        if command_list[0] == "give":
            if command_list[1] != "key":
                if command_list[1] in itemDict:
                    consoleItemSerial = int(itemDict[command_list[1]])
                    Player.inventory.storage[Player.inventory.SIndex] = Item.serialNumbers[consoleItemSerial]((0, 0), consoleItemSerial, i_textures[consoleItemSerial])
                    KDS.Console.Feed.append(f"Item was given: [{itemDict[command_list[1]]}: {command_list[1]}]")
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
                if Player.inventory.storage[Player.inventory.SIndex] != Inventory.emptySlot:
                    KDS.Console.Feed.append(f"Item was removed: {Player.inventory.storage[Player.inventory.SIndex]}")
                    Player.inventory.storage[Player.inventory.SIndex] = Inventory.emptySlot
                else: KDS.Console.Feed.append("Selected inventory slot is already empty!")
            elif command_list[1] == "key":
                if command_list[2] in Player.keys:
                    if Player.keys[command_list[2]] == True:
                        Player.keys[command_list[2]] = False
                        KDS.Console.Feed.append(f"Item was removed: {command_list[1]} {command_list[2]}")
                    else: KDS.Console.Feed.append("You don't have that item!")
                else: KDS.Console.Feed.append(f"Item [{command_list[1]} {command_list[2]}] does not exist!")
            else: KDS.Console.Feed.append("Not a valid remove command.")
        elif command_list[0] == "playboy":
            KDS.Scores.koponen_happiness = 1000
            KDS.Console.Feed.append("You are now a playboy")
            KDS.Console.Feed.append(f"Koponen happines: {KDS.Scores.koponen_happiness}")
        elif command_list[0] == "kill" or command_list[0] == "stop":
            KDS.Console.Feed.append("Stopping Game...")
            KDS.Logging.Log(KDS.Logging.LogType.info, "Stop command issued through console.", True)
            KDS_Quit()
        elif command_list[0] == "killme":
            KDS.Console.Feed.append("Player Killed.")
            KDS.Logging.Log(KDS.Logging.LogType.info, "Player kill command issued through console.", True)
            Player.health = 0
        elif command_list[0] == "terms":
            setTerms = False
            if len(command_list) > 1:
                setTerms = KDS.Convert.ToBool(command_list[1])
                if setTerms != None:
                    KDS.ConfigManager.SetSetting("Data/Terms/accepted", setTerms)
                    KDS.Console.Feed.append(f"Terms status set to: {setTerms}")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for terms & conditions")
            else:
                KDS.Console.Feed.append("Please provide a proper state for terms & conditions")
        elif command_list[0] == "woof":
            if len(command_list) > 1:
                woofState = KDS.Convert.ToBool(command_list[1])
                if woofState != None:
                    KDS.Console.Feed.append("Woof state assignment has not been implemented for the new AI system yet.")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for woof")
            else:
                KDS.Console.Feed.append("Please provide a proper state for woof")
        elif command_list[0] == "invl":
            if len(command_list) > 1:
                invlState = KDS.Convert.ToBool(command_list[1])
                if invlState != None:
                    global godmode
                    godmode = invlState
                    KDS.Console.Feed.append(f"Invulnerability state has been set to: {godmode}")
                else:
                    KDS.Console.Feed.append("Please provide a proper state for invl")
            else:
                KDS.Console.Feed.append("Please provide a proper state for invl")
        elif command_list[0] == "finish":
            if len(command_list) > 1 and command_list[1] == "missions":
                KDS.Console.Feed.append("Missions Finished.")
                KDS.Logging.Log(KDS.Logging.LogType.info, "Mission finish issued through console.", True)
                KDS.Missions.Finish()
            elif len(command_list) == 1:
                KDS.Console.Feed.append("Level Finished.")
                KDS.Logging.Log(KDS.Logging.LogType.info, "Level finish issued through console.", True)
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
                summonEntity = {
                    "imp": lambda e : numpy.append(e, KDS.AI.Imp(Player.rect.topright)),
                    "sergeant": lambda e : numpy.append(e, KDS.AI.SergeantZombie(Player.rect.topright)),
                    "drugdealer": lambda e : numpy.append(e, KDS.AI.DrugDealer(Player.rect.topright)),
                    "supershotgunner": lambda e : numpy.append(e, KDS.AI.TurboShotgunner(Player.rect.topright)),
                    "methmaker": lambda e : numpy.append(e, KDS.AI.MethMaker(Player.rect.topright)),
                    "fucker69": lambda e : numpy.append(e, KDS.AI.CaveMonster(Player.rect.topright))
                }
                try:
                    global Enemies
                    Enemies = summonEntity[command_list[1]](Enemies)
                except KeyError:
                    KDS.Console.Feed.append(f"Entity name {command_list[1]} is not valid.")
        elif command_list[0] == "help":
            KDS.Console.Feed.append("""
    Console Help:
        - give => Adds the specified item to your inventory.
        - playboy => Sets Koponen's happiness to unseen levels.
        - kill | stop => Stops the game.
        - killme => Kills the player.
        - terms => Sets Terms and Conditions accepted to the specified value.
        - woof => Sets all bulldogs anger to the specified value.
        - finish => Finishes level or missions.
        - invl => Sets invulnerability mode to the specified value.
        - teleport => Teleports player either to static coordinates or relative coordinates.
        - summon => Summons enemy to the coordinates of player's rectangle's top left corner.
        - help => Shows the list of commands.
    """)
        else:
            KDS.Console.Feed.append("Invalid Command.")
#endregion
#region Terms and Conditions
def agr(tcagr: bool):
    global tcagr_running
    if tcagr == False:
        tcagr_running = True
    else:
        tcagr_running = False

    global main_running
    c = False

    def tcagr_agree_function():
        global tcagr_running, main_menu_running
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Terms and Conditions have been accepted.", False)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "You said you will not get offended... Dick!", False)
        KDS.ConfigManager.SetSetting("Data/Terms/accepted", True)
        KDS.Logging.Log(KDS.Logging.LogType.debug, "Terms Agreed. Updated Value: {}".format(KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)), False)
        tcagr_running = False
        

    agree_button = KDS.UI.Button(pygame.Rect(465, 500, 270, 135), tcagr_agree_function, button_font1.render(
        "I Agree", True, KDS.Colors.White))

    while tcagr_running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                    KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        KDS_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == QUIT:
                KDS_Quit()
        display.blit(agr_background, (0, 0))
        agree_button.update(display, mouse_pos, c)
        pygame.display.update()
        c = False
    return True
#endregion
#region Game Functions
def play_function(gamemode: KDS.Gamemode.Modes and int, reset_scroll: bool, show_loading: bool = True, loadEntities: bool = True):
    KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Game...")
    global main_menu_running, current_map, animation_has_played, death_wait, true_scroll, selectedSave
    if show_loading:
        scaled_loadingScreen = KDS.Convert.AspectScale(loadingScreen, display_size)
        display.fill(scaled_loadingScreen.get_at((0, 0)))
        display.blit(scaled_loadingScreen, (display_size[0] / 2 - scaled_loadingScreen.get_width() / 2, display_size[1] / 2 - scaled_loadingScreen.get_height() / 2))
        pygame.display.update()

    KDS.Audio.Music.unload()
    KDS.Gamemode.SetGamemode(gamemode, int(current_map))
    
    Player.reset()
    
    #region Load World Data
    global Items, Enemies, Explosions, BallisticObjects
    Items = numpy.array(KDS.ConfigManager.Save.GetWorld("items", []))
    Enemies = numpy.array(KDS.ConfigManager.Save.GetWorld("enemies", []))
    Explosions = KDS.ConfigManager.Save.GetWorld("explosions", [])
    BallisticObjects = KDS.ConfigManager.Save.GetWorld("ballistic_objects", [])
    #endregion
    
    LoadGameSettings()

    Player.rect.topleft, koponen_rect.topleft = WorldData.LoadMap(loadEntities)

    #region Set Game Data
    global animation_has_played, level_finished, death_wait
    animation_has_played = False
    level_finished = False
    death_wait = 0
    is_new_save = KDS.ConfigManager.Save.GetExistence(KDS.ConfigManager.Save.SaveIndex)
    #endregion
    
    ########## iPuhelin ##########
    if int(current_map) < 2 or (KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story and is_new_save):
        Player.inventory.storage[0] = Item.serialNumbers[6]((0, 0), 6, i_textures[6])

    pygame.mouse.set_visible(False)
    main_menu_running = False
    KDS.Scores.ScoreCounter.start()
    if reset_scroll: true_scroll = [-200, -190]
    pygame.event.clear()
    KDS.Keys.Reset()
    KDS.Logging.Log(KDS.Logging.LogType.debug, "Game Loaded.")

def save_function():
    KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Save...")
    global Items, Enemies, Explosions, BallisticObjects
    KDS.ConfigManager.Save.SetWorld("items", Items.tolist())
    KDS.ConfigManager.Save.SetWorld("enemies", Enemies.tolist())
    KDS.ConfigManager.Save.SetWorld("explosions", Explosions)
    KDS.ConfigManager.Save.SetWorld("ballistic_objects", BallisticObjects)
    KDS.ConfigManager.Save.SetWorld("missions", KDS.Missions.Missions)
    global Player
    KDS.ConfigManager.Save.SetData("Player/position", Player.rect.topleft)
    KDS.ConfigManager.Save.SetData("Player/health", Player.health)
    KDS.ConfigManager.Save.SetData("Player/stamina", Player.stamina)
    KDS.ConfigManager.Save.SetData("Player/Inventory/storage", Player.inventory.storage)
    KDS.ConfigManager.Save.SetData("Player/Inventory/index", Player.inventory.SIndex)
    KDS.ConfigManager.Save.SetData("Player/keys", Player.keys)
    KDS.ConfigManager.Save.SetData("Player/farting", Player.farting)
    global koponen_rect, scroll
    KDS.ConfigManager.Save.SetData("Koponen/position", koponen_rect.topleft)
    KDS.ConfigManager.Save.SetData("Renderer/scroll", scroll)
    KDS.ConfigManager.Save.quit()
    KDS.Logging.Log(KDS.Logging.LogType.debug, "Save Loaded.")
    global tiles, specialTilesD
    KDS.ConfigManager.Save.SetTiles(tiles, specialTilesD)

def load_function():
    newSave = KDS.ConfigManager.Save.init(1)
    play_function(KDS.Gamemode.gamemode, True, True, newSave)
    
    if not newSave:
        global Items, Enemies, Explosions, BallisticObjects
        Items = numpy.array(KDS.ConfigManager.Save.GetWorld("items", []))
        Enemies = numpy.array(KDS.ConfigManager.Save.GetWorld("enemies", []))
        Explosions = KDS.ConfigManager.Save.GetWorld("explosions", [])
        BallisticObjects = KDS.ConfigManager.Save.GetWorld("ballistic_objects", [])
        global Player
        Player.rect.topleft = tuple(KDS.ConfigManager.Save.GetData("Player/position", Player.rect.topleft))
        Player.health = KDS.ConfigManager.Save.GetData("Player/health", Player.health)
        Player.stamina = KDS.ConfigManager.Save.GetData("Player/stamina", Player.stamina)
        Player.inventory.storage = KDS.ConfigManager.Save.GetData("Player/Inventory/storage", Player.inventory.storage)
        Player.inventory.SIndex = KDS.ConfigManager.Save.GetData("Player/Inventory/index", Player.inventory.SIndex)
        Player.keys = KDS.ConfigManager.Save.GetData("Player/keys", Player.keys)
        Player.farting = KDS.ConfigManager.Save.GetData("Player/farting", Player.farting)
        global tiles
        KDS.ConfigManager.Save.GetTiles(tiles)

def respawn_function():
    global animation_has_played, level_finished, death_wait
    Player.reset()
    animation_has_played = False
    level_finished = False
    death_wait = 0
    if RespawnAnchor.active != None: Player.rect.bottomleft = RespawnAnchor.active.rect.bottomleft
    else: Player.rect.topleft = KDS.ConfigManager.GetLevelProp("Entities/Player/startPos", (100, 100))
    KDS.Audio.Music.stop()
#endregion
#region Menus
def esc_menu_f():
    global esc_menu, go_to_main_menu, DebugMode, clock, c
    c = False

    esc_surface = pygame.Surface(display_size)
    
    blurred_background = KDS.Convert.ToBlur(game_pause_background, 6)

    def resume():
        global esc_menu
        esc_menu = False

    def settings():
        settings_menu()

    def goto_main_menu():
        global esc_menu, go_to_main_menu
        pygame.mixer.unpause()
        esc_menu = False
        go_to_main_menu = True

    resume_button = KDS.UI.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 400, 200, 30), resume, button_font.render("RESUME", True, KDS.Colors.White))
    save_button_enabled = True
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
        save_button_enabled = False
    save_button = KDS.UI.Button(pygame.Rect(int(display_size[0] / 2 - 100), 438, 200, 30), save_function, button_font.render(
        "Save", True, KDS.Colors.White), enabled=save_button_enabled)
    settings_button = KDS.UI.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 475, 200, 30), settings, button_font.render("SETTINGS", True, KDS.Colors.White))
    main_menu_button = KDS.UI.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 513, 200, 30), goto_main_menu, button_font.render("MAIN MENU", True, KDS.Colors.White))

    anim_lerp_x = KDS.Animator.Float(0.0, 1.0, 15, KDS.Animator.AnimationType.EaseOut, KDS.Animator.OnAnimationEnd.Stop)

    while esc_menu:
        display.blit(pygame.transform.scale(game_pause_background, display_size), (0, 0))
        anim_x = anim_lerp_x.update(False)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                    KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.key == K_ESCAPE:
                    esc_menu = False
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        KDS_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()

        esc_surface.blit(pygame.transform.scale(
            blurred_background, display_size), (0, 0))
        pygame.draw.rect(esc_surface, (123, 134, 111), (int(
            (display_size[0] / 2) - 250), int((display_size[1] / 2) - 200), 500, 400))
        esc_surface.blit(pygame.transform.scale(
            text_icon, (250, 139)), (int(display_size[0] / 2 - 125), int(display_size[1] / 2 - 175)))

        resume_button.update(esc_surface, mouse_pos, c)
        save_button.update(esc_surface, mouse_pos, c)
        settings_button.update(esc_surface, mouse_pos, c)
        main_menu_button.update(esc_surface, mouse_pos, c)

        KDS.Logging.Profiler(DebugMode)
        esc_surface.set_alpha(int(KDS.Math.Lerp(0, 255, anim_x)))
        display.blit(esc_surface, (0, 0))
        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))
        
            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = score_font.render(fps_text, True, KDS.Colors.White)
            display.blit(pygame.transform.scale(fps_text, (int(fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))
        display.blit(pygame.transform.scale(display, display_size), (0, 0))
        pygame.display.update()
        display.fill(KDS.Colors.Black)
        c = False
        clock.tick(locked_fps)

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, DebugMode, pauseOnFocusLoss
    c = False
    settings_running = True

    def return_def():
        global settings_running
        settings_running = False

    def reset_settings():
        return_def()
        os.remove(os.path.join(PersistentPaths.AppDataPath, "settings.cfg"))
        KDS.ConfigManager.init(PersistentPaths.AppDataPath, PersistentPaths.CachePath, PersistentPaths.SavePath)
        KDS.ConfigManager.SetSetting("Data/Terms/accepted", True)
    
    def reset_data():
        KDS_Quit(True, True)
    
    return_button = KDS.UI.Button(pygame.Rect(465, 700, 270, 60), return_def, "RETURN")
    music_volume_slider = KDS.UI.Slider("musicVolume", pygame.Rect(450, 135, 340, 20), (20, 30), 1, custom_path="Mixer/Volume/music")
    effect_volume_slider = KDS.UI.Slider("effectVolume", pygame.Rect(450, 185, 340, 20), (20, 30), 1, custom_path="Mixer/Volume/effect")
    pause_loss_switch = KDS.UI.Switch("pauseOnFocusLoss", pygame.Rect(450, 240, 100, 30), (30, 50), True, custom_path="Game/pauseOnFocusLoss")
    reset_settings_button = KDS.UI.Button(pygame.Rect(340, 585, 240, 40), reset_settings, button_font.render("Reset Settings", True, KDS.Colors.White))
    reset_data_button = KDS.UI.Button(pygame.Rect(620, 585, 240, 40), reset_data, button_font.render("Reset Data", True, KDS.Colors.White))
    music_volume_text = button_font.render(
        "Music Volume", True, KDS.Colors.White)
    effect_volume_text = button_font.render(
        "Sound Effect Volume", True, KDS.Colors.White)
    pause_loss_text = button_font.render("Pause On Focus Loss", True, KDS.Colors.White)

    while settings_running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                    KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        KDS_Quit()
                elif event.key == K_ESCAPE:
                    settings_running = False
                elif event.key == K_F3:
                    DebugMode = not DebugMode
            elif event.type == pygame.QUIT:
                KDS_Quit()

        display.blit(settings_background, (0, 0))

        display.blit(pygame.transform.flip(
            menu_trashcan_animation.update(), False, False), (279, 515))

        display.blit(music_volume_text, (50, 135))
        display.blit(effect_volume_text, (50, 185))
        display.blit(pause_loss_text, (50, 240))
        KDS.Audio.Music.setVolume(music_volume_slider.update(display, mouse_pos))
        KDS.Audio.setVolume(effect_volume_slider.update(display, mouse_pos))
        pauseOnFocusLoss = pause_loss_switch.update(display, mouse_pos, c)

        return_button.update(display, mouse_pos, c)
        reset_settings_button.update(display, mouse_pos, c)
        reset_data_button.update(display, mouse_pos, c)
        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))
            
            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))

        pygame.display.update()
        display.fill((0, 0, 0))
        c = False
        clock.tick(locked_fps)

def main_menu():
    global current_map, MenuMode, DebugMode
    
    class Mode:
        MainMenu = 0
        ModeSelectionMenu = 1
        StoryMenu = 2
        CampaignMenu = 3
    MenuMode = Mode.MainMenu

    current_map_int = 0
    current_map_int = int(current_map)

    global main_menu_running, main_running, go_to_main_menu
    go_to_main_menu = False

    main_menu_running = True
    c = False

    KDS.Audio.Music.play("Assets/Audio/music/lobbymusic.ogg")

    class level_pick:
        class direction:
            left = 0
            right = 1

        def right():
            level_pick.pick(level_pick.direction.right)

        def left():
            level_pick.pick(level_pick.direction.left)

        def pick(direction: direction):
            global current_map, max_map
            current_map_int = int(current_map)
            if direction == level_pick.direction.left:
                current_map_int -= 1
            else:
                current_map_int += 1
            if current_map_int < 1:
                current_map_int = 1
            if current_map_int > int(max_map):
                current_map_int = int(max_map)
            current_map = f"{current_map_int:02d}"
            KDS.ConfigManager.SetSetting("Player/currentMap", current_map)

    def menu_mode_selector(mode):
        global MenuMode
        MenuMode = mode

    #region Main Menu

    #Main menu variables:
    framecounter = 0
    current_frame = 0
    framechange_lerp = KDS.Animator.Float(0.0, 255.0, 100, KDS.Animator.AnimationType.SmoothStep, KDS.Animator.OnAnimationEnd.Stop)
    framechange_lerp.tick = framechange_lerp.ticks

    main_menu_play_button = KDS.UI.Button(pygame.Rect(450, 180, 300, 60), menu_mode_selector, "PLAY")
    main_menu_settings_button = KDS.UI.Button(pygame.Rect(450, 250, 300, 60), settings_menu, "SETTINGS")
    main_menu_quit_button = KDS.UI.Button(pygame.Rect(450, 320, 300, 60), KDS_Quit, "QUIT")
    #Frame 2
    Frame2 = pygame.Surface(display_size)
    Frame2.blit(main_menu_background_2, (0,0))
    #Frame 3
    Frame3 = pygame.Surface(display_size)
    Frame3.blit(main_menu_background_3, (0, 0))
    #Frame 4
    Frame4 = pygame.Surface(display_size)
    Frame4.blit(main_menu_background_4, (0, 0))
    #endregion
    #region Mode Selection Menu
    mode_selection_modes = []
    mode_selection_modes.append(KDS.Gamemode.Modes.Story)
    mode_selection_modes.append(KDS.Gamemode.Modes.Campaign)
    mode_selection_buttons = []
    story_mode_button = pygame.Rect(0, 0, display_size[0], int(display_size[1] / 2))
    campaign_mode_button = pygame.Rect(0, int(display_size[1] / 2), display_size[0], int(display_size[1] / 2))
    mode_selection_buttons.append(story_mode_button)
    mode_selection_buttons.append(campaign_mode_button)
    #endregion
    #region Story Menu
    story_save_button_0_rect = pygame.Rect(14, 14, 378, 500)
    story_save_button_1_rect = pygame.Rect(410, 14, 378, 500)
    story_save_button_2_rect = pygame.Rect(806, 14, 378, 500)
    story_save_buttons_rects = (story_save_button_0_rect, story_save_button_1_rect, story_save_button_2_rect)
    story_save_button_0 = KDS.UI.Button(story_save_button_0_rect, play_function)
    story_save_button_1 = KDS.UI.Button(story_save_button_1_rect, play_function)
    story_save_button_2 = KDS.UI.Button(story_save_button_2_rect, play_function)
    story_new_save = button_font1.render("Start New Save", True, KDS.Colors.White)
    #endregion 
    #region Campaign Menu
    campaign_right_button_rect = pygame.Rect(1084, 200, 66, 66)
    campaign_left_button_rect = pygame.Rect(50, 200, 66, 66)
    campaign_play_button_rect = pygame.Rect(int(display_size[0] / 2) - 150, display_size[1] - 300, 300, 100)
    campaign_return_button_rect = pygame.Rect(int(display_size[0] / 2) - 150, display_size[1] - 150, 300, 100)
    campaign_play_text = button_font1.render("START", True, (KDS.Colors.EmeraldGreen))
    campaign_return_text = button_font1.render("RETURN", True, (KDS.Colors.AviatorRed))
    campaign_play_button = KDS.UI.Button(campaign_play_button_rect, play_function, campaign_play_text)
    campaign_return_button = KDS.UI.Button(campaign_return_button_rect, menu_mode_selector, campaign_return_text)
    campaign_left_button = KDS.UI.Button(campaign_left_button_rect, level_pick.left, pygame.transform.flip(arrow_button, True, False))
    campaign_right_button = KDS.UI.Button(campaign_right_button_rect, level_pick.right, arrow_button)

    Frame1 = pygame.Surface(display_size)
    frames = [Frame1, Frame2, Frame3, Frame4]
    #endregion
    while main_menu_running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                    KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        KDS_Quit()
                elif event.key == K_F3:
                    DebugMode = not DebugMode
                elif event.key == K_ESCAPE:
                    if MenuMode == Mode.ModeSelectionMenu or MenuMode == Mode.MainMenu:
                        MenuMode = Mode.MainMenu
                    else:
                        menu_mode_selector(Mode.ModeSelectionMenu)
            elif event.type == pygame.QUIT:
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
            display.blit(gamemode_bc_2_1, (0, int(display_size[1] / 2)))
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
            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_0_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_1_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.DarkGray, story_save_button_2_rect, 10)
            
            story_save_button_0.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)
            story_save_button_1.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)
            story_save_button_2.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)
            
            #Äh, teen joskus
            
        elif MenuMode == Mode.CampaignMenu:
            pygame.draw.rect(display, (192, 192, 192), (50, 200, int(display_size[0] - 100), 66))

            campaign_play_button.update(display, mouse_pos, c, KDS.Gamemode.Modes.Campaign, True)
            campaign_return_button.update(display, mouse_pos, c, Mode.MainMenu)
            campaign_left_button.update(display, mouse_pos, c)
            campaign_right_button.update(display, mouse_pos, c)

            current_map_int = int(current_map)

            if current_map_int < len(map_names):
                map_name = map_names[current_map_int]
            else:
                map_name = map_names[0]
            level_text = button_font1.render(f"{current_map} - {map_name}", True, (0, 0, 0))
            display.blit(level_text, (125, 209))

        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))
            
            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))

        c = False
        pygame.display.update()
        display.fill(KDS.Colors.Black)
        clock.tick(locked_fps)

def level_finished_menu():
    global game_pause_background, DebugMode, level_finished_running
    
    score_color = KDS.Colors.Cyan
    padding = 50
    textVertOffset = 40
    textStartVertOffset = 300
    totalVertOffset = 25
    timeTakenVertOffset = 100
    scoreTexts = (
        ArialSysFont.render("Score:", True, score_color),
        ArialSysFont.render("Koponen Happiness:", True, score_color),
        ArialSysFont.render("Time Bonus:", True, score_color),
        ArialSysFont.render("Total:", True, score_color)
    )
    
    KDS.Audio.Music.play("Assets/Audio/Music/level_cleared.ogg")
    
    KDS.Scores.ScoreAnimation.init()
    anim_lerp_x = KDS.Animator.Float(0.0, 1.0, 15, KDS.Animator.AnimationType.EaseOut, KDS.Animator.OnAnimationEnd.Stop)
    level_f_surf = pygame.Surface(display_size)
    blurred_background = KDS.Convert.ToBlur(game_pause_background, 6)
    menu_rect = pygame.Rect(int((display_size[0] / 2) - 250), int((display_size[1] / 2) - 300), 500, 600)
    
    def goto_main_menu():
        global level_finished_running, go_to_main_menu
        level_finished_running = False
        go_to_main_menu = True
        KDS.Audio.Music.unpause()

    def next_level():
        global level_finished_running, current_map
        level_finished_running = False
        current_map = f"{int(current_map) + 1:02}"
        play_function(KDS.Gamemode.Modes.Campaign, True)

    next_level_bool = True if int(current_map) < int(max_map) else False
    
    main_menu_button = KDS.UI.Button(pygame.Rect(int(display_size[0] / 2 - 220), menu_rect.bottom - padding, 200, 30), goto_main_menu, button_font.render("Main Menu", True, KDS.Colors.White))
    next_level_button = KDS.UI.Button(pygame.Rect(int(display_size[0] / 2 + 20), menu_rect.bottom - padding, 200, 30), next_level, button_font.render("Next Level", True, KDS.Colors.White), enabled=next_level_bool)
    
    pre_rendered_scores = {}
    
    level_finished_running = True
    while level_finished_running:
        display.blit(game_pause_background, (0, 0))
        anim_x = anim_lerp_x.update(False)
        mouse_pos = pygame.mouse.get_pos()
        
        c = False
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()
                    KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        KDS_Quit()
                elif event.key == K_F3:
                    DebugMode = not DebugMode
            elif event.type == KEYUP:
                if event.key in (K_SPACE, K_RETURN, K_ESCAPE):
                    KDS.Scores.ScoreAnimation.skip()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    KDS.Scores.ScoreAnimation.skip()
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()

        level_f_surf.blit(pygame.transform.scale(blurred_background, display_size), (0, 0))
        pygame.draw.rect(level_f_surf, (123, 134, 111), menu_rect)
        level_f_surf.blit(pygame.transform.scale(level_cleared_icon, (250, 139)), (int(display_size[0] / 2 - 125), int(display_size[1] / 2 - 275)))
            
        values = KDS.Scores.ScoreAnimation.update(True if anim_lerp_x.tick >= anim_lerp_x.ticks else False)
        comparisonValue = KDS.Math.Clamp(KDS.Scores.ScoreAnimation.animationIndex + 1, 0, len(values))
        lineY = textStartVertOffset + (len(values) - 1) * textVertOffset + round(totalVertOffset / 2)
        pygame.draw.line(level_f_surf, KDS.Colors.Cyan, (menu_rect.left + padding, lineY), (menu_rect.right - padding, lineY), 3)
        for i in range(len(scoreTexts)):
            totalOffset = True if i == len(values) - 1 else False
            textY = textStartVertOffset + i * textVertOffset + (0 if not totalOffset else totalVertOffset)
            if i < comparisonValue:
                value = str(values[i])
                if value not in pre_rendered_scores:
                    rend_txt = ArialSysFont.render(value, True, score_color)
                    if KDS.Scores.ScoreAnimation.animationList[i].Finished:
                        pre_rendered_scores[value] = rend_txt
                else:
                    rend_txt = pre_rendered_scores[value]
                level_f_surf.blit(rend_txt, (menu_rect.right - rend_txt.get_width() - padding, textY))
            level_f_surf.blit(scoreTexts[i], (menu_rect.left + padding, textY))
            
        if KDS.Scores.ScoreAnimation.finished:
            timeTakenText = ArialSysFont.render(f"Time Taken: {KDS.Scores.GameTime.formattedGameTime}", True, score_color)
            textY = textStartVertOffset + (len(values) - 1) * textVertOffset + totalVertOffset
            level_f_surf.blit(timeTakenText, (menu_rect.left + padding, textY + timeTakenVertOffset))

            main_menu_button.update(level_f_surf, mouse_pos, c)
            next_level_button.update(level_f_surf, mouse_pos, c)

        KDS.Logging.Profiler(DebugMode)
        level_f_surf.set_alpha(round(KDS.Math.Lerp(0, 255, anim_x)))
        display.blit(level_f_surf, (0, 0))
        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))
        
            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = score_font.render(fps_text, True, KDS.Colors.White)
            display.blit(pygame.transform.scale(fps_text, (int(fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))
        pygame.display.update()
        display.fill(KDS.Colors.Black)
        clock.tick(locked_fps)
#endregion
#region Check Terms
agr(tcagr)
tcagr = KDS.ConfigManager.GetSetting("Data/Terms/accepted", False)
if tcagr:
    main_menu()
else:
    agr(tcagr)
#endregion
#region Main Running
while main_running:
#region Events
    KDS.Keys.Update()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_d:
                KDS.Keys.moveRight.SetState(True)
            elif event.key == K_a:
                KDS.Keys.moveLeft.SetState(True)
            elif event.key == K_w:
                KDS.Keys.moveUp.SetState(True)
            elif event.key == K_s:
                KDS.Keys.moveDown.SetState(True)
            elif event.key == K_SPACE:
                KDS.Keys.moveUp.SetState(True)
            elif event.key == K_LCTRL:
                KDS.Keys.moveDown.SetState(True)
            elif event.key == K_LSHIFT:
                if not KDS.Keys.moveDown.pressed:
                    KDS.Keys.moveRun.SetState(True)
            elif event.key == K_e:
                KDS.Keys.functionKey.SetState(True)
            elif event.key == K_ESCAPE:
                esc_menu = True
            elif event.key in KDS.Keys.inventoryKeys:
                Player.inventory.pickSlot(KDS.Keys.inventoryKeys.index(event.key))
            elif event.key == K_q:
                if Player.inventory.getHandItem() != "none" and Player.inventory.getHandItem() != Inventory.doubleItem:
                    temp = Player.inventory.dropItem()
                    temp.rect.midbottom = Player.rect.midbottom
                    temp.physics = True
                    # Set momentum as player momentum?
                    temp.momentum = 0
                    Items = numpy.append(Items, temp)
            elif event.key == K_f:
                if Player.stamina == 100:
                    Player.stamina = -1000.0
                    Player.farting = True
                    KDS.Audio.playSound(fart)
                    KDS.Missions.SetProgress("tutorial", "fart", 1.0)
            elif event.key == K_DOWN:
                KDS.Keys.altDown.SetState(True)
            elif event.key == K_UP:
                KDS.Keys.altUp.SetState(True)
            elif event.key == K_LEFT:
                KDS.Keys.altLeft.SetState(True)
            elif event.key == K_RIGHT:
                KDS.Keys.altRight.SetState(True)
            elif event.key == K_F1:
                renderUI = not renderUI
            elif event.key == K_t:
                go_to_console = True
            elif event.key == K_F3:
                DebugMode = not DebugMode
            elif event.key == K_F4:
                if pygame.key.get_pressed()[K_LALT]:
                    KDS_Quit()
                else:
                    Player.health = 0
            elif event.key == K_F11:
                pygame.display.toggle_fullscreen()
                KDS.ConfigManager.SetSetting("Renderer/fullscreen", not KDS.ConfigManager.GetSetting("Renderer/fullscreen", False))
            elif event.key == K_F12:
                pygame.image.save(screen, os.path.join(PersistentPaths.Screenshots, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"))
                KDS.Audio.playSound(camera_shutter, 1)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                KDS.Keys.mainKey.SetState(True)
                rk62_sound_cooldown = 11
                weapon_fire = True
        elif event.type == KEYUP:
            if event.key == K_d:
                KDS.Keys.moveRight.SetState(False)
            elif event.key == K_a:
                KDS.Keys.moveLeft.SetState(False)
            elif event.key == K_w:
                KDS.Keys.moveUp.SetState(False)
            elif event.key == K_s:
                KDS.Keys.moveDown.SetState(False)
            elif event.key == K_SPACE:
                KDS.Keys.moveUp.SetState(False)
            elif event.key == K_LCTRL:
                KDS.Keys.moveDown.SetState(False)
            elif event.key == K_LSHIFT:
                KDS.Keys.moveRun.SetState(False)
            elif event.key == K_e:
                KDS.Keys.functionKey.SetState(False)
            elif event.key == K_DOWN:
                KDS.Keys.altDown.SetState(False)
            elif event.key == K_UP:
                KDS.Keys.altUp.SetState(False)
            elif event.key == K_LEFT:
                KDS.Keys.altLeft.SetState(False)
            elif event.key == K_RIGHT:
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
        elif event.type == QUIT:
            KDS_Quit()
        elif event.type == WINDOWEVENT:
            if event.event == WINDOWEVENT_FOCUS_LOST:
                if pauseOnFocusLoss: esc_menu = True
#endregion
#region Data

    display.fill((20, 25, 20))
    screen.fill((20, 25, 20))

    Lights.clear()

    true_scroll[0] += (Player.rect.x - true_scroll[0] - (screen_size[0] / 2)) / 12
    true_scroll[1] += (Player.rect.y - true_scroll[1] - 220) / 12

    scroll = [round(true_scroll[0]), round(true_scroll[1])]
    if Player.farting:
        scroll[0] += random.randint(-10, 10)
        scroll[1] += random.randint(-10, 10)
    mouse_pos = pygame.mouse.get_pos()
    onLadder = False
#endregion
#region Player Death
    if Player.health <= 0:
        if not animation_has_played:
            Player.dead = True
            KDS.Audio.Music.stop()
            pygame.mixer.Sound.play(Player.deathSound)
            Player.deathSound.set_volume(0.5)
            animation_has_played = True
        else:
            death_wait += 1
            if death_wait > 240:
                if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
                    respawn_function()
                else:
                    pass
#endregion
#region Rendering
    ###### TÄNNE UUSI ASIOIDEN KÄSITTELY ######
    Items, Player.inventory = Item.checkCollisions(Items, Player.rect, screen, scroll, KDS.Keys.functionKey.pressed, Player.inventory)
    Tile.renderUpdate(tiles, screen, scroll, (Player.rect.centerx - (Player.rect.x - scroll[0] - 301), Player.rect.centery - (Player.rect.y - scroll[1] - 221)))
    for enemy in Enemies:
        if KDS.Math.getDistance(Player.rect.center, enemy.rect.center) < 1200:
            result = enemy.update(screen, scroll, tiles, Player.rect)
            if result[0]:
                #print(len(result[0]))
                for r in result[0]:
                    Projectiles.append(r)
            if result[1]:
                for serialNumber in result[1]:
                        tempItem = Item((enemy.rect.center), serialNumber=serialNumber, texture = i_textures[serialNumber])
                        counter = 0
                        while True:
                            tempItem.rect.y += tempItem.rect.height
                            for collision in KDS.World.collision_test(tempItem.rect, tiles):
                                tempItem.rect.bottom = collision.rect.top
                                counter = 250
                            counter += 1
                            if counter > 250:
                                break
                        Items = numpy.append(Items, tempItem)
                        del tempItem

    Player.update()
    Item.renderUpdate(Items, screen, scroll, DebugMode)
    Player.inventory.useItem(screen, KDS.Keys.mainKey.pressed, weapon_fire)
    for item in Player.inventory.storage:
        if isinstance(item, Lantern):
            Player.inventory.useSpecificItem(0, screen)
            break

    for Projectile in Projectiles:
        result = Projectile.update(screen, scroll, Enemies, HitTargets, Particles, Player.rect, Player.health, DebugMode)
        if result:
            v = result[0]
            Enemies = result[1]
            Player.health = result[2]
            HitTargets = result[3]
        else:
            v = None
        
        if v == "wall" or v == "air":
            Projectiles.remove(Projectile)

    for B_Object in BallisticObjects:
        r2 = B_Object.update(tiles, screen, scroll)
        if r2:
            for x in range(8):
                x = -x
                x /= 8
                Projectiles.append(KDS.World.Bullet(pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), 1, -1, tiles, 25, maxDistance=82, slope=x))
            for x in range(8):
                x = -x
                x /= 8
                Projectiles.append(KDS.World.Bullet(pygame.Rect(B_Object.rect.centerx, B_Object.rect.centery, 1, 1), 0, -1, tiles, 25, maxDistance=82, slope=x))

            KDS.Audio.playSound(landmine_explosion)
            Explosions.append(KDS.World.Explosion(KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop), (B_Object.rect.x - 60, B_Object.rect.y - 55)))
             
            BallisticObjects.remove(B_Object)

    #Räjähdykset
    for unit in Explosions:
        finished, etick = unit.update(screen, scroll)
        if finished:
            Explosions.remove(unit)
        elif etick < 10:
            Lights.append(KDS.World.Lighting.Light((unit.xpos - 80, unit.ypos - 80), KDS.World.Lighting.Shapes.circle_hard.get(300, 5500)))

    #Partikkelit
    #Particles.append(KDS.World.Lighting.Sparkparticle((Player.rect.x, Player.rect.y - 20), random.randint(1, 20), random.randint(1, 20), random.randint(1, 9)))
    while len(Particles) > maxParticles:
        Particles.pop(0)
    for particle in Particles:
        result = particle.update(screen, scroll)
        if isinstance(result, pygame.Surface): Lights.append(KDS.World.Lighting.Light((particle.rect.x, particle.rect.y), result))
        else: Particles.remove(particle)

    #Valojen käsittely
    lightsUpdating = 0
    if ambient_light:
        ambient_tint.fill(ambient_light_tint)
        screen.blit(ambient_tint, (0, 0), special_flags=BLEND_ADD)
    #dark = False if Player.rect.x > 500 else 1
    if dark:
        black_tint.fill(darkness)
        for light in Lights:
            lightsUpdating += 1
            black_tint.blit(light.surf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
            if DebugMode:
                rectSurf = pygame.Surface((light.surf.get_width(), light.surf.get_height()))
                rectSurf.fill(KDS.Colors.Yellow)
                rectSurf.set_alpha(128)
                screen.blit(rectSurf, (int(light.position[0] - scroll[0]), int(light.position[1] - scroll[1])))
            #black_tint.blit(KDS.World.Lighting.Shapes.circle.get(40, 40000), (20, 20))
        if Player.light:
            black_tint.blit(KDS.World.Lighting.Shapes.circle_soft.get(300, 5500), (int(Player.rect.centerx - scroll[0] - 150), int(Player.rect.centery - scroll[1] - 150)))
        screen.blit(black_tint, (0, 0), special_flags=BLEND_MULT)
    #UI
    if renderUI:
        Player.health = max(Player.health, 0)
        ui_hand_item = Player.inventory.getHandItem()

        screen.blit(score_font.render(f"SCORE: {KDS.Scores.score}", True, KDS.Colors.White), (10, 45))
        screen.blit(score_font.render(f"HEALTH: {math.ceil(Player.health)}", True, KDS.Colors.White), (10, 55))
        screen.blit(score_font.render(f"STAMINA: {math.ceil(Player.stamina)}", True, KDS.Colors.White), (10, 120))
        screen.blit(score_font.render(f"KOPONEN HAPPINESS: {KDS.Scores.koponen_happiness}", True, KDS.Colors.White), (10, 130))
        if hasattr(ui_hand_item, "ammunition"):
            tmpAmmo = ui_hand_item.ammunition if isinstance(ui_hand_item.ammunition, int) else math.ceil(ui_hand_item.ammunition * 10) / 10
            screen.blit(harbinger_font.render(f"AMMO: {tmpAmmo}", True, KDS.Colors.White), (10, 360))

        KDS.Missions.Render(screen)

        Player.inventory.render(screen)

    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################

#endregion
#region AI
    koponen_rect, k_collisions = KDS.World.move_entity(koponen_rect, koponen_movement, tiles)
    if k_collisions.left:
        koponen_movingx = -koponen_movingx
    elif k_collisions.right:
        koponen_movingx = -koponen_movingx

#endregion
#region Pelaajan elämätilanteen käsittely
#endregion
#region Player Data
#endregion
#region Koponen Movement
    if koponen_movement[0] != 0:
        koponen_animations.trigger("walk")
    else:
        koponen_animations.trigger("idle")
#endregion
#region Items
    if animation_counter > animation_duration:
        animation_counter = 0
        animation_image += 1
    if Player.dead and Player.animations.tick >= Player.animations.active.ticks:
            Player.dead = False
            animation_has_played = True

    if Player.farting:
        fart_counter += 1
        if fart_counter > 250:
            Player.farting = False
            fart_counter = 0
            for enemy in Enemies:
                if KDS.Math.getDistance(enemy.rect.topleft, Player.rect.topleft) < 800:
                    enemy.dmg(random.randint(500, 1000))

    if Player.keys["red"]:
        screen.blit(red_key, (10, 20))
    if Player.keys["green"]:
        screen.blit(green_key, (24, 20))
    if Player.keys["blue"]:
        screen.blit(blue_key, (38, 20))
#endregion
#region Koponen Tip
    if Player.rect.colliderect(koponen_rect):
        screen.blit(
            koponen_talk_tip, (koponen_rect.centerx - scroll[0] - int(koponen_talk_tip.get_width() / 2), koponen_rect.top - scroll[1] - 20))
        koponen_movement[0] = 0
        if knifeInUse:
            koponen_alive = False
        if KDS.Keys.functionKey.pressed:
            KDS.Keys.Reset()
            KDS.Koponen.Talk.start(display, Player.inventory, KDS_Quit, clock, locked_fps)
    else:
        koponen_movement[0] = koponen_movingx
    h = 0
#endregion
#region Interactable Objects
    if DebugMode:
        pygame.draw.rect(screen, KDS.Colors.Magenta, pygame.Rect(koponen_rect.x - scroll[0], koponen_rect.y - scroll[1], koponen_rect.width, koponen_rect.height))
    screen.blit(koponen_animations.update(), (koponen_rect.x - scroll[0], koponen_rect.y - scroll[1]))

    if DebugMode:
        pygame.draw.rect(screen, (KDS.Colors.Green), (Player.rect.x - scroll[0], Player.rect.y - scroll[1], Player.rect.width, Player.rect.height))

    screen.blit(pygame.transform.flip(Player.animations.update(), Player.direction, False), (int(Player.rect.topleft[0] - scroll[0] + ((Player.rect.width - Player.animations.active.size[0]) / 2)), int(Player.rect.bottomleft[1] - scroll[1] - Player.animations.active.size[1])))

#endregion
#region Debug Mode
    KDS.Logging.Profiler(DebugMode)
    if DebugMode:
        debugSurf = pygame.Surface((score_font.size(f"Player Position: {Player.rect.topleft}")[0] + 10, 60))
        debugSurf.fill(KDS.Colors.DarkGray)
        debugSurf.set_alpha(128)
        screen.blit(debugSurf, (0, 0))
        
        screen.blit(score_font.render(f"FPS: {round(clock.get_fps())}", True, KDS.Colors.White), (5, 5))
        screen.blit(score_font.render(f"Player Position: {Player.rect.topleft}", True, KDS.Colors.White), (5, 15))
        screen.blit(score_font.render(f"Total Monsters: {monstersLeft} / {monsterAmount}", True, KDS.Colors.White), (5, 25))
        screen.blit(score_font.render(f"Sounds Playing: {len(KDS.Audio.getBusyChannels())} / {pygame.mixer.get_num_channels()}", True, KDS.Colors.White), (5, 35))
        screen.blit(score_font.render(f"Lights Rendering: {lightsUpdating}", True, KDS.Colors.White), (5, 45))
#endregion
#region Screen Rendering
    if colorInvert:
        invPix = pygame.surfarray.pixels2d(screen)
        invPix ^= 2 ** 32 - 1
        del invPix
        colorInvert = False

    display.fill(KDS.Colors.Black)
    display.blit(pygame.transform.scale(screen, display_size), (0, 0))
    #Updating display object
    pygame.display.update()
#endregion
#region Data Update
    animation_counter += 1
    weapon_fire = False
    if KDS.Missions.GetFinished():
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
            level_finished = True
        else:
            pass

#endregion
#region Conditional Events
    if Player.rect.y > len(tiles) * 34 + 340:
        Player.health = 0
        Player.rect.y = len(tiles) * 34 + 340
    if esc_menu:
        KDS.Scores.ScoreCounter.pause()
        KDS.Audio.Music.pause()
        KDS.Audio.pauseAllSounds()
        display.fill(KDS.Colors.Black)
        display.blit(pygame.transform.scale(screen, display_size), (0, 0))
        game_pause_background = pygame.transform.scale(screen.copy(), display_size)
        pygame.mouse.set_visible(True)
        esc_menu_f()
        pygame.mouse.set_visible(False)
        KDS.Audio.Music.unpause()
        KDS.Audio.unpauseAllSounds()
        KDS.Scores.ScoreCounter.unpause()
    if level_finished:
        KDS.Scores.ScoreCounter.stop()
        KDS.Audio.stopAllSounds()
        KDS.Audio.Music.stop()
        pygame.mouse.set_visible(True)
        game_pause_background = pygame.transform.scale(screen.copy(), display_size)
        level_finished_menu()
        level_finished = False
    if go_to_console:
        KDS.Audio.Music.pause()
        KDS.Audio.pauseAllSounds()
        game_pause_background = pygame.transform.scale(screen.copy(), display_size)
        pygame.mouse.set_visible(True)
        console()
        pygame.mouse.set_visible(False)
        KDS.Audio.Music.unpause()
        KDS.Audio.unpauseAllSounds()
    if go_to_main_menu:
        KDS.Audio.stopAllSounds()
        KDS.Audio.Music.stop()
        pygame.mouse.set_visible(True)
        main_menu()
#endregion
#region Ticks
    tick += 1
    if tick > 60:
        tick = 0
    clock.tick(locked_fps)
#endregion
#endregion
#region Application Quitting
KDS.ConfigManager.Save.quit()
KDS.Audio.Music.unload()
KDS.System.emptdir(PersistentPaths.CachePath)
KDS.Logging.quit()
pygame.mixer.quit()
pygame.display.quit()
pygame.quit()
if reset_data:
    shutil.rmtree(PersistentPaths.AppDataPath)
if restart:
    os.execl(sys.executable, os.path.abspath(__file__))
#endregion