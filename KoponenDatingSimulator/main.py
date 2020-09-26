#region Importing
import os
from inspect import currentframe
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
import KDS.AI
import KDS.Animator
import KDS.Colors
import KDS.ConfigManager
import KDS.Convert
import KDS.Gamemode
import KDS.Keys
import KDS.LevelLoader
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.System
import KDS.UI
import KDS.World
import numpy
import random
import threading
import concurrent.futures
import sys
import importlib
import shutil
import json
import zipfile
from pygame.locals import *
from PIL import Image, ImageFilter
#endregion
#region Priority Initialisation
class PersistentPaths:
    AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
    CachePath = os.path.join(AppDataPath, "cache")
if not os.path.isdir(os.path.join(os.getenv('APPDATA'), "Koponen Development Inc")):
    os.mkdir(os.path.join(os.getenv('APPDATA'), "Koponen Development Inc"))
if not os.path.isdir(PersistentPaths.AppDataPath):
    os.mkdir(PersistentPaths.AppDataPath)
if not os.path.isdir(PersistentPaths.CachePath):
    os.mkdir(PersistentPaths.CachePath)
KDS.System.hide(PersistentPaths.CachePath)

pygame.mixer.init()
pygame.init()
KDS.Logging.init()
KDS.ConfigManager.init()

monitor_info = pygame.display.Info()
monitor_size = (monitor_info.current_w, monitor_info.current_h)

pygame.mouse.set_cursor(*pygame.cursors.arrow)

game_icon = pygame.image.load("Assets/Textures/Game_Icon.png")
pygame.display.set_icon(game_icon)
pygame.display.set_caption("Koponen Dating Simulator")
window_size = (int(KDS.ConfigManager.LoadSetting("Settings", "WindowSizeX", str(
    1200))), int(KDS.ConfigManager.LoadSetting("Settings", "WindowSizeY", str(800))))
window = pygame.display.set_mode(window_size, pygame.RESIZABLE | pygame.DOUBLEBUF)
window_resize_size = window_size
display_size = (1200, 800)
display = pygame.Surface(display_size)
screen_size = (600, 400)
screen = pygame.Surface(screen_size)

clock = pygame.time.Clock()
profiler_enabled = False

window.blit(pygame.image.load("Assets/Textures/UI/loadingScreen.png"), (0, 0))
pygame.display.update()
#endregion
#region Window
class Fullscreen:
    size = display_size
    offset = (0, 0)
    scaling = 0

    @staticmethod
    def Set(reverseFullscreen=False):
        global isFullscreen, window, window_size, window_resize_size
        if reverseFullscreen:
            isFullscreen = not isFullscreen
        if isFullscreen:
            window_size = window_resize_size
            window = pygame.display.set_mode(
                window_size, pygame.RESIZABLE | pygame.DOUBLEBUF)
            isFullscreen = False
        else:
            window_size = monitor_size
            window = pygame.display.set_mode(
                window_size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            isFullscreen = True
        KDS.ConfigManager.SetSetting(
            "Settings", "Fullscreen", str(isFullscreen))
        if window_size[0] / window_size[1] > display_size[0] / display_size[1]:
            Fullscreen.size = (
                int(window_size[1] * (display_size[0] / display_size[1])), int(window_size[1]))
            Fullscreen.scaling = window_size[1] / display_size[1]
        else:
            Fullscreen.size = (int(window_size[0]), int(
                window_size[0] / (display_size[0] / display_size[1])))
            Fullscreen.scaling = window_size[0] / display_size[0]
        Fullscreen.offset = (int((window_size[0] / 2) - (Fullscreen.size[0] / 2)), int(
            (window_size[1] / 2) - (Fullscreen.size[1] / 2)))

def ResizeWindow(set_size: tuple):
    global window_resize_size
    if not isFullscreen:
        window_resize_size = set_size
        KDS.ConfigManager.SetSetting(
            "Settings", "WindowSizeX", str(set_size[0]))
        KDS.ConfigManager.SetSetting(
            "Settings", "WindowSizeY", str(set_size[1]))
    Fullscreen.Set(True)
#endregion
#region Audio
pygame.mixer.set_num_channels(32)

class Audio:
    MusicMixer = pygame.mixer.music
    MusicVolume = float(KDS.ConfigManager.LoadSetting("Settings", "MusicVolume", str(1)))
    EffectVolume = float(KDS.ConfigManager.LoadSetting("Settings", "SoundEffectVolume", str(1)))
    EffectChannels = []
    for i in range(pygame.mixer.get_num_channels()):
        EffectChannels.append(pygame.mixer.Channel(i))

    @staticmethod
    def playSound(sound: pygame.mixer.Sound, volume=EffectVolume):
        play_channel = pygame.mixer.find_channel(True)
        play_channel.play(sound)
        play_channel.set_volume(volume)
        return play_channel

    @staticmethod
    def stopAllSounds():
        for i in range(len(Audio.EffectChannels)):
            Audio.EffectChannels[i].stop()

    @staticmethod
    def pauseAllSounds():
        for i in range(len(Audio.EffectChannels)):
            Audio.EffectChannels[i].pause()

    @staticmethod
    def unpauseAllSounds():
        for i in range(len(Audio.EffectChannels)):
            Audio.EffectChannels[i].unpause()

    @staticmethod
    def getBusyChannels():
        busyChannels = []
        for channel in Audio.EffectChannels:
            if channel.get_busy():
                busyChannels.append(channel)
        return busyChannels

    @staticmethod
    def setVolume(volume: float):
        EffectVolume = volume
        for channel in Audio.EffectChannels:
            channel.set_volume(EffectVolume)
#endregion
#region Animations
monstersLeft = 0

class Archvile:
    global monstersLeft

    def __init__(self, position, health, speed):
        self.position = position
        self.health = health
        self.speed = speed
        self.rect = pygame.Rect(position[0], position[1], 65, 85)

        self.direction = True
        self.movement = [speed, 8]
        self.hits = {}
        self.playDeathAnimation = True
        self.attacking = "null"
        self.counter = 0
        self.attack_anim = False
        self.playDeathSound = True

    def update(self, a_run):
        global player_health, monstersLeft
        if not self.attack_anim:
            self.counter += 1

        def hit_scan(self):
            q = True
            counter = 0
            scan_position = [self.rect.centerx, self.rect.centery]
            while q:
                if self.direction:
                    scan_position[0] += 27
                else:
                    scan_position[0] -= 27

                for tile in WorldData.Legacy.tile_rects:
                    if tile.collidepoint(scan_position):
                        return "wall"

                if player_rect.collidepoint(scan_position):
                    return "player"

                counter += 1
                if counter > 40:
                    q = False

            return "null"

        if self.health > 0:
            if self.counter > 100:
                self.attacking = hit_scan(self)
                if self.attacking == "player":
                    if not self.attack_anim:
                        Audio.playSound(archvile_attack)
                    self.attack_anim = True
                self.counter = 0
            else:
                self.attacking = "null"

            if not self.attack_anim:
                self.rect, self.hits = move_entity(
                    self.rect, self.movement, WorldData.Legacy.tile_rects)
                if self.hits["right"] or self.hits["left"]:
                    self.movement[0] = -self.movement[0]

                if self.movement[0] > 0:
                    self.direction = True
                elif self.movement[0] < 0:
                    self.direction = False

                screen.blit(pygame.transform.flip(a_run, not self.direction,
                                                  False), (self.rect.x - scroll[0],
                                                           self.rect.y - scroll[1]))

            else:
                i, u = arhcvile_attack_animation.update()
                if u:
                    f = hit_scan(self)

                    if f != "wall" and player_rect.y-40 < archvile.rect.y:
                        player_health -= int(random.uniform(30, 80))
                        Audio.playSound(landmine_explosion)
                    del f

                    arhcvile_attack_animation.reset()
                    self.attack_anim = False
                screen.blit(pygame.transform.flip(
                    i, not self.direction, False), (self.rect.x - scroll[0],
                                                    self.rect.y - scroll[1]))

        elif self.playDeathAnimation:
            self.attacking = "null"
            self.attack_anim = False
            if self.playDeathSound:
                self.playDeathSound = False
                Audio.playSound(archvile_death)
            l, p = archvile_death_animation.update()
            if not p:
                screen.blit(pygame.transform.flip(l, not self.direction, False),
                            (self.rect.x - scroll[0], self.rect.y - scroll[1] + 15))

            if p:
                self.playDeathAnimation = False
                monstersLeft -= 1

        else:
            screen.blit(pygame.transform.flip(archvile_corpse, not self.direction,
                                              False), (self.rect.x - scroll[0],
                                                       self.rect.y - scroll[1]+25))
#endregion
#region Initialisation
KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising Game...")
black_tint = pygame.Surface(screen_size)
black_tint.fill((0, 0, 0))
black_tint.set_alpha(170)
#region Downloads
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Assets...")
main_menu_background = pygame.image.load(
    "Assets/Textures/UI/Menus/main_menu_bc.png").convert()
settings_background = pygame.image.load(
    "Assets/Textures/UI/Menus/settings_bc.png").convert()
agr_background = pygame.image.load(
    "Assets/Textures/UI/Menus/tcagr_bc.png").convert()

score_font = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10, bold=0, italic=0)
tip_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 10, bold=0, italic=0)
button_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 52, bold=0, italic=0)
text_font = pygame.font.Font("Assets/Fonts/courier.ttf", 30, bold=0, italic=0)
harbinger_font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25, bold=0, italic=0)

player_img = pygame.image.load("Assets/Textures/Player/stand0.png").convert()
player_corpse = pygame.image.load(
    "Assets/Textures/Player/corpse.png").convert()
player_corpse.set_colorkey(KDS.Colors.GetPrimary.White)
player_img.set_colorkey(KDS.Colors.GetPrimary.White)

floor0 = pygame.image.load("Assets/Textures/Map/floor0v2.png").convert()
concrete0 = pygame.image.load(
    "Assets/Textures/Map/concrete0.png").convert()
wall0 = pygame.image.load("Assets/Textures/Map/wall0.png").convert()
table0 = pygame.image.load("Assets/Textures/Map/table0.png").convert()
toilet0 = pygame.image.load("Assets/Textures/Map/toilet0.png").convert()
lamp0 = pygame.image.load("Assets/Textures/Map/lamp0.png").convert()
trashcan = pygame.image.load("Assets/Textures/Map/trashcan.png").convert()
ground1 = pygame.image.load("Assets/Textures/Map/ground0.png").convert()
grass = pygame.image.load("Assets/Textures/Map/grass0.png").convert()
door_closed = pygame.image.load(
    "Assets/Textures/Map/door_closed.png").convert()
red_door_closed = pygame.image.load(
    "Assets/Textures/Map/red_door_closed.png").convert()
green_door_closed = pygame.image.load(
    "Assets/Textures/Map/green_door_closed.png").convert()
blue_door_closed = pygame.image.load(
    "Assets/Textures/Map/blue_door_closed.png").convert()
door_open = pygame.image.load(
    "Assets/Textures/Map/door_open2.png").convert()
bricks = pygame.image.load("Assets/Textures/Map/bricks.png").convert()
tree = pygame.image.load("Assets/Textures/Map/tree.png").convert()
planks = pygame.image.load("Assets/Textures/Map/planks.png").convert()
jukebox_texture = pygame.image.load(
    "Assets/Textures/Map/jukebox.png").convert()
landmine_texture = pygame.image.load(
    "Assets/Textures/Map/landmine.png").convert()
ladder_texture = pygame.image.load(
    "Assets/Textures/Map/ladder.png").convert()
background_wall = pygame.image.load(
    "Assets/Textures/Map/background_wall.png").convert()
light_bricks = pygame.image.load(
    "Assets/Textures/Map/light_bricks.png").convert()
iron_bar = pygame.image.load(
    "Assets/Textures/Map/iron_bars_texture.png").convert()
soil = pygame.image.load("Assets/Textures/Map/soil.png").convert()
mossy_bricks = pygame.image.load(
    "Assets/Textures/Map/mossy_bricks.png").convert()
stone = pygame.image.load("Assets/Textures/Map/stone.png").convert()
hay = pygame.image.load("Assets/Textures/Map/hay.png").convert()
soil1 = pygame.image.load("Assets/Textures/Map/soil_2.png").convert()
wood = pygame.image.load("Assets/Textures/Map/wood.png").convert()
table0.set_colorkey(KDS.Colors.GetPrimary.White)
toilet0.set_colorkey(KDS.Colors.GetPrimary.White)
lamp0.set_colorkey(KDS.Colors.GetPrimary.White)
trashcan.set_colorkey(KDS.Colors.GetPrimary.White)
door_closed.set_colorkey(KDS.Colors.GetPrimary.White)
red_door_closed.set_colorkey(KDS.Colors.GetPrimary.White)
green_door_closed.set_colorkey(KDS.Colors.GetPrimary.White)
blue_door_closed.set_colorkey(KDS.Colors.GetPrimary.White)
jukebox_texture.set_colorkey(KDS.Colors.GetPrimary.White)
landmine_texture.set_colorkey(KDS.Colors.GetPrimary.White)
ladder_texture.set_colorkey(KDS.Colors.GetPrimary.White)
iron_bar.set_colorkey(KDS.Colors.GetPrimary.White)
tree.set_colorkey((0, 0, 0))

gasburner_off = pygame.image.load(
    "Assets/Textures/Items/gasburner_off.png").convert()
#gasburner_on = pygame.image.load("Assets/Textures/Items/gasburner_on.png").convert()
knife = pygame.image.load("Assets/Textures/Items/knife.png").convert()
knife_blood = pygame.image.load("Assets/Textures/Items/knife.png").convert()
red_key = pygame.image.load("Assets/Textures/Items/red_key.png").convert()
green_key = pygame.image.load("Assets/Textures/Items/green_key2.png").convert()
blue_key = pygame.image.load("Assets/Textures/Items/blue_key.png").convert()
coffeemug = pygame.image.load("Assets/Textures/Items/coffeemug.png").convert()
ss_bonuscard = pygame.image.load(
    "Assets/Textures/Items/ss_bonuscard.png").convert()
lappi_sytytyspalat = pygame.image.load(
    "Assets/Textures/Items/lappi_sytytyspalat.png").convert()
plasmarifle = pygame.image.load(
    "Assets/Textures/Items/plasmarifle.png").convert()
plasma_ammo = pygame.image.load(
    "Assets/Textures/Items/plasma_ammo.png").convert()
cell = pygame.image.load("Assets/Textures/Items/cell.png")
zombie_corpse = pygame.image.load(
    "Assets/Textures/Animations/z_death_4.png").convert()
pistol_texture = pygame.image.load(
    "Assets/Textures/Items/pistol.png").convert()
pistol_f_texture = pygame.image.load(
    "Assets/Textures/Items/pistol_firing.png").convert()
soulsphere = pygame.image.load(
    "Assets/Textures/Items/soulsphere.png").convert()
turboneedle = pygame.image.load(
    "Assets/Textures/Items/turboneedle.png").convert()
pistol_mag = pygame.image.load(
    "Assets/Textures/Items/pistol_mag.png").convert()
rk62_texture = pygame.image.load("Assets/Textures/Items/rk62.png").convert()
rk62_f_texture = pygame.image.load(
    "Assets/Textures/Items/rk62_firing.png").convert()
rk62_mag = pygame.image.load("Assets/Textures/Items/rk_mag.png").convert()
sergeant_corpse = pygame.image.load(
    "Assets/Textures/Animations/seargeant_dying_4.png").convert()
sergeant_aiming = pygame.image.load(
    "Assets/Textures/Animations/seargeant_shooting_0.png").convert()
sergeant_firing = pygame.image.load(
    "Assets/Textures/Animations/seargeant_shooting_1.png").convert()
imp_fireball_texture = pygame.image.load(
    "Assets/Textures/Animations/imp_fireball.png").convert()
medkit = pygame.image.load("Assets/Textures/Items/medkit.png").convert()
shotgun = pygame.image.load("Assets/Textures/Items/shotgun.png").convert()
shotgun_f = pygame.image.load(
    "Assets/Textures/Items/shotgun_firing.png").convert()
shotgun_shells_t = pygame.image.load(
    "Assets/Textures/Items/shotgun_shells.png").convert()
archvile_corpse = pygame.image.load(
    "Assets/Textures/Animations/archvile_death_6.png").convert()
ipuhelin_texture = pygame.image.load(
    "Assets/Textures/Items/iPuhelin.png").convert()
rk62_bullet_t = pygame.image.load("Assets/Textures/Animations/rk62_bullet.png").convert()

gamemode_bc_1_1 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_1.png")).convert()
gamemode_bc_1_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_2.png")).convert()
gamemode_bc_2_1 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_1.png")).convert()
gamemode_bc_2_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_2.png")).convert()
arrow_button = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Buttons", "Arrow.png"))

gasburner_off.set_colorkey(KDS.Colors.GetPrimary.White)
knife.set_colorkey(KDS.Colors.GetPrimary.White)
knife_blood.set_colorkey(KDS.Colors.GetPrimary.White)
red_key.set_colorkey(KDS.Colors.GetPrimary.White)
green_key.set_colorkey(KDS.Colors.GetPrimary.White)
blue_key.set_colorkey(KDS.Colors.GetPrimary.White)
coffeemug.set_colorkey(KDS.Colors.GetPrimary.White)
ss_bonuscard.set_colorkey((255, 0, 0))
lappi_sytytyspalat.set_colorkey(KDS.Colors.GetPrimary.White)
plasmarifle.set_colorkey(KDS.Colors.GetPrimary.White)
plasma_ammo.set_colorkey(KDS.Colors.GetPrimary.White)
cell.set_colorkey(KDS.Colors.GetPrimary.White)
zombie_corpse.set_colorkey(KDS.Colors.GetPrimary.White)
pistol_texture.set_colorkey(KDS.Colors.GetPrimary.White)
pistol_f_texture.set_colorkey(KDS.Colors.GetPrimary.White)
pistol_mag.set_colorkey(KDS.Colors.GetPrimary.White)
rk62_texture.set_colorkey(KDS.Colors.GetPrimary.White)
rk62_f_texture.set_colorkey(KDS.Colors.GetPrimary.White)
rk62_mag.set_colorkey(KDS.Colors.GetPrimary.White)
sergeant_corpse.set_colorkey(KDS.Colors.GetPrimary.White)
sergeant_aiming.set_colorkey(KDS.Colors.GetPrimary.White)
sergeant_firing.set_colorkey(KDS.Colors.GetPrimary.White)
medkit.set_colorkey(KDS.Colors.GetPrimary.White)
shotgun.set_colorkey(KDS.Colors.GetPrimary.White)
shotgun_f.set_colorkey(KDS.Colors.GetPrimary.White)
shotgun_shells_t.set_colorkey(KDS.Colors.GetPrimary.White)
archvile_corpse.set_colorkey(KDS.Colors.GetPrimary.White)
ipuhelin_texture.set_colorkey(KDS.Colors.GetPrimary.White)
soulsphere.set_colorkey(KDS.Colors.GetPrimary.White)
turboneedle.set_colorkey(KDS.Colors.GetPrimary.White)
imp_fireball_texture.set_colorkey(KDS.Colors.GetPrimary.White)

Items_list = ["iPuhelin", "coffeemug"]
Items = {"iPuhelin": ipuhelin_texture, "coffeemug": coffeemug}

text_icon = pygame.image.load("Assets/Textures/Text_Icon.png").convert()
text_icon.set_colorkey(KDS.Colors.GetPrimary.White)

gasburner_clip = pygame.mixer.Sound("Assets/Audio/Effects/gasburner_clip.wav")
gasburner_fire = pygame.mixer.Sound("Assets/Audio/Effects/gasburner_fire.wav")
door_opening = pygame.mixer.Sound("Assets/Audio/Effects/door.wav")
player_death_sound = pygame.mixer.Sound("Assets/Audio/Effects/dspldeth.wav")
player_walking = pygame.mixer.Sound("Assets/Audio/Effects/walking.wav")
coffeemug_sound = pygame.mixer.Sound("Assets/Audio/Effects/coffeemug.wav")
knife_pickup = pygame.mixer.Sound("Assets/Audio/Effects/knife.wav")
key_pickup = pygame.mixer.Sound("Assets/Audio/Effects/pickup_key.wav")
ss_sound = pygame.mixer.Sound("Assets/Audio/Effects/ss.wav")
lappi_sytytyspalat_sound = pygame.mixer.Sound(
    "Assets/Audio/Effects/sytytyspalat.wav")
landmine_explosion = pygame.mixer.Sound("Assets/Audio/Effects/landmine.wav")
hurt_sound = pygame.mixer.Sound("Assets/Audio/Effects/dsplpain.wav")
plasmarifle_f_sound = pygame.mixer.Sound("Assets/Audio/Effects/dsplasma.wav")
weapon_pickup = pygame.mixer.Sound("Assets/Audio/Effects/weapon_pickup.wav")
item_pickup = pygame.mixer.Sound("Assets/Audio/Effects/dsitemup.wav")
plasma_hitting = pygame.mixer.Sound("Assets/Audio/Effects/dsfirxpl.wav")
pistol_shot = pygame.mixer.Sound("Assets/Audio/Effects/pistolshot.wav")
rk62_shot = pygame.mixer.Sound("Assets/Audio/Effects/rk62_shot.wav")
shotgun_shot = pygame.mixer.Sound("Assets/Audio/Effects/shotgun.wav")
player_shotgun_shot = pygame.mixer.Sound(
    "Assets/Audio/Effects/player_shotgun.wav")
archvile_attack = pygame.mixer.Sound("Assets/Audio/Effects/dsflame.wav")
archvile_death = pygame.mixer.Sound("Assets/Audio/Effects/dsvildth.wav")
fart = pygame.mixer.Sound("Assets/Audio/Effects/fart_attack.wav")
soulsphere_pickup = pygame.mixer.Sound("Assets/Audio/Effects/dsgetpow.wav")
plasmarifle_f_sound.set_volume(0.05)
hurt_sound.set_volume(0.6)
plasma_hitting.set_volume(0.03)
rk62_shot.set_volume(0.9)
shotgun_shot.set_volume(0.9)
player_shotgun_shot.set_volume(0.8)

KDS.Logging.Log(KDS.Logging.LogType.debug, "Asset Loading Complete.")
#endregion
jukebox_tip = pygame.Surface((tip_font.size("Use Jukebox [Press: E]")[0], tip_font.size("Use Jukebox [Press: E]")[1] * 2), pygame.SRCALPHA, 32)
jukebox_tip.blit(tip_font.render("Use Jukebox [Press: E]", True, KDS.Colors.GetPrimary.White), (0, 0))
jukebox_tip.blit(tip_font.render("Stop Jukebox [Hold: E]", True, KDS.Colors.GetPrimary.White), (int((jukebox_tip.get_width() - tip_font.size("Stop Jukebox [Hold: E]")[0]) / 2), int(jukebox_tip.get_height() / 2)))

restart = False
reset_data = False
clearLag = KDS.Convert.ToBool(KDS.ConfigManager.LoadSetting("Settings", "ClearLag", str(False)))

main_running = True
plasmarifle_fire = False
jukeboxMusicPlaying = -1
lastJukeboxSong = [0, 0, 0, 0, 0]
playerStamina = 100.0
gasburnerBurning = False
plasmabullets = []
tick = 0
knifeInUse = False
currently_on_mission = False
current_mission = "none"
player_name = "Sinä"
weapon_fire = False
isFullscreen = False
shoot = False

KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Settings...")
tcagr = KDS.Convert.ToBool(KDS.ConfigManager.LoadSetting(
    "Data", "TermsAccepted", str(False)))

if tcagr == None:
    KDS.Logging.AutoError(
        "Error parcing terms and conditions bool.", currentframe())
    tcagr = False

isFullscreen = KDS.Convert.ToBool(
    KDS.ConfigManager.LoadSetting("Settings", "Fullscreen", str(False)))

if isFullscreen == None:
    KDS.Logging.AutoError("Error parcing fullscreen bool.",
                          currentframe())
Fullscreen.Set(True)
KDS.Logging.Log(KDS.Logging.LogType.debug, 
                f"Settings Loading Complete.\nSettings Loaded:\n - Terms Accepted: {tcagr}\n - Music Volume: {Audio.MusicVolume}\n - Sound Effect Volume: {Audio.EffectVolume}\n - Fullscreen: {isFullscreen}\n - Clear Lag: {clearLag}", False)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Defining Variables...")
selectedSave = 0

koponen_animation_stats = [0, 7, 0]
explosion_positions = []
player_hand_item = "none"
player_keys = {"red": False, "green": False, "blue": False}
direction = True
esc_menu = False
onLadder = False
shotgun_loaded = True
shotgun_cooldown = 0
pistol_cooldown = 0
dark = False

gamemode_bc_1_alpha = KDS.Animator.Lerp(
    0.0, 1.0, 8, KDS.Animator.OnAnimationEnd.Stop)
gamemode_bc_2_alpha = KDS.Animator.Lerp(
    0.0, 1.0, 8, KDS.Animator.OnAnimationEnd.Stop)

go_to_main_menu = False

main_menu_running = False
tcagr_running = False
koponenTalking = False
mode_selection_running = False
settings_running = False
vertical_momentum = 0
animation_counter = 0
animation_duration = 0
animation_image = 0
air_timer = 0
player_health = 100
last_player_health = 100
player_death_event = False
animation_has_played = False
death_wait = 0
attack_counter = 0
fart_counter = 0
monsterAmount = 0
monstersLeft = 0
farting = False

current_map = KDS.ConfigManager.LoadSetting("Settings", "CurrentMap", "01")

with open("Assets/Maps/map_names.txt", "r") as file:
    cntnts = file.read()
    cntnts = cntnts.split('\n')
    file.close()

#######################################TEMPORARY#######################################
max_map = KDS.ConfigManager.SetSetting("Settings", "MaxMap", f"{len(cntnts) - 1:02d}")
#######################################TEMPORARY#######################################
max_map = int(KDS.ConfigManager.LoadSetting("Settings", "MaxMap", "05"))
map_names = tuple(cntnts)

ammunition_plasma = 50
pistol_bullets = 8
rk_62_ammo = 30
shotgun_shells = 8

Projectiles = []
Explosions = []

inventory = ["none", "none", "none", "none", "none"]
inventoryDoubles = []
inventoryDobulesSerialNumbers = []
with open("Assets/Textures/item_doubles.txt", "r") as file:
    data = file.read().split("\n")
    for d in data:
        inventoryDobulesSerialNumbers.append(int(d))
    file.close()

inventoryDoubleOffset = 0
for none in inventory:
    inventoryDoubles.append(False)

player_score = 0

true_scroll = [0, 0]

test_rect = pygame.Rect(0, 0, 60, 40)
stand_size = (28, 63)
crouch_size = (28, 34)
jump_velocity = 2.0
fall_multiplier = 2.5
moveUp_released = True
check_crouch = False
player_rect = pygame.Rect(100, 100, stand_size[0], stand_size[1])
koponen_rect = pygame.Rect(200, 200, 24, 64)
koponen_recog_rec = pygame.Rect(0, 0, 72, 64)
koponen_movement = [1, 6]
koponen_movingx = 0
koponen_happines = 40

koponen_talk_tip = tip_font.render(
    "Puhu Koposelle [E]", True, KDS.Colors.GetPrimary.White)

task = ""
taskTaivutettu = ""

DebugMode = False

MenuMode = 0
esc_menu_background = pygame.Surface(display_size)

KDS.Logging.Log(KDS.Logging.LogType.debug, "Variable Defining Complete.")
#endregion
#region Save System
def LoadSave(save_index: int):
    global Saving, player_rect, player_name, player_health, last_player_health, playerStamina, farting
    player_rect.x = int(KDS.ConfigManager.LoadSave(save_index, "PlayerPosition", "X", str(player_rect.x)))
    player_rect.y = int(KDS.ConfigManager.LoadSave(save_index, "PlayerPosition", "Y", str(player_rect.y)))
    player_health = int(KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Health", str(player_health)))
    last_player_health = player_health
    player_name = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Name", player_name)
    playerStamina = float(KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Stamina", str(playerStamina)))
    player_inventory.storage[0] = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Inventory0", player_inventory.storage[0])
    player_inventory.storage[1] = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Inventory1", player_inventory.storage[1])
    player_inventory.storage[2] = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Inventory2", player_inventory.storage[2])
    player_inventory.storage[3] = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Inventory3", player_inventory.storage[3])
    player_inventory.storage[4] = KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Inventory4", player_inventory.storage[4])
    farting = KDS.Convert.ToBool(KDS.ConfigManager.LoadSave(save_index, "PlayerData", "Farting", "f"))
def SaveData():
    global Saving, player_rect, selectedSave, player_name, player_health, last_player_health, farting
    #region Player
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerPosition", "X", str(player_rect.x))
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerPosition", "Y", str(player_rect.y))
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Health", str(player_health))
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Name", str(player_name))
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Stamina", str(playerStamina))
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory0", player_inventory.storage[0])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory1", player_inventory.storage[1])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory2", player_inventory.storage[2])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory3", player_inventory.storage[3])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory4", player_inventory.storage[4])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Farting", str(farting))
    #endregion
    #region Map
    
    #endregion
    #region Enemies
    
    #endregion
#endregion
#region Quit Handling
def KDS_Quit(_restart: bool = False, _reset_data: bool = False):
    global main_running, main_menu_running, tcagr_running, koponenTalking, esc_menu, settings_running, selectedSave, tick, restart, reset_data
    main_menu_running = False
    main_running = False
    tcagr_running = False
    koponenTalking = False
    esc_menu = False
    settings_running = False
    restart = _restart
    reset_data = _reset_data
#endregion
#region World Data
imps = []
iron_bars = []
class WorldData():

    MapSize = (0, 0)

    class Legacy:
        #region Lists
        world_gen = []
        item_gen = []
        tile_rects = []
        toilets = []
        burning_toilets = []
        trashcans = []
        burning_trashcans = []
        jukeboxes = []
        landmines = []
        zombies = []
        sergeants = []
        archviles = []
        ladders = []
        bulldogs = []
        item_rects = []
        item_ids = []
        task_items = []
        color_keys = []
        door_rects = []
        doors_open = []
        tile_textures = {}
        tile_textures_loaded = False
        #endregion

        @staticmethod
        def WorldGeneration():
            global imps, iron_bars

            buildingBitmap = pygame.image.load(os.path.join(
                "Assets", "Maps", "map" + current_map, "map_buildings.map")).convert()
            decorationBitmap = pygame.image.load(os.path.join(
                "Assets", "Maps", "map" + current_map, "map_decorations.map")).convert()
            enemyBitmap = pygame.image.load(os.path.join(
                "Assets", "Maps", "map" + current_map, "map_enemies.map")).convert()
            itemBitmap = pygame.image.load(os.path.join(
                "Assets", "Maps", "map" + current_map, "map_items.map")).convert()

            convertBuildingRules = []
            convertBuildingColors = []
            convertDecorationRules = []
            convertDecorationColors = []
            convertEnemyRules = []
            convertEnemyColors = []
            convertItemRules = []
            convertItemColors = []
            with open(os.path.join("Assets", "Maps", "resources_convert_rules.txt"), 'r') as f:
                raw = f.read()
                f.close()
                raw = raw.replace(" ", "")
                rowSplit = raw.split('\n')

                # Adds air to all convert rules
                array = rowSplit[0].split(',')
                array[2] = array[2].replace("(", "")
                array[4] = array[4].replace(")", "")
                convertBuildingRules.append(array[1])
                convertBuildingColors.append(
                    (int(array[2]), int(array[3]), int(array[4])))
                convertDecorationRules.append(array[1])
                convertDecorationColors.append(
                    (int(array[2]), int(array[3]), int(array[4])))
                convertEnemyRules.append(array[1])
                convertEnemyColors.append(
                    (int(array[2]), int(array[3]), int(array[4])))
                convertItemRules.append(array[1])
                convertItemColors.append(
                    (int(array[2]), int(array[3]), int(array[4])))

                Type = -1
                for row in rowSplit:
                    array = row.split(',')
                    if len(array) > 1:
                        array[2] = array[2].replace("(", "")
                        array[4] = array[4].replace(")", "")
                    skip = True
                    if array[0] == "building:":
                        Type = 0
                    elif array[0] == "decoration:":
                        Type = 1
                    elif array[0] == "enemies:":
                        Type = 2
                    elif array[0] == "items:":
                        Type = 3
                    else:
                        if len(array[0]) > 0 and rowSplit.index(row) != 0:
                            skip = False

                    if skip == False and Type != -1:
                        if Type == 0:
                            convertBuildingRules.append(array[1])
                            convertBuildingColors.append(
                                (int(array[2]), int(array[3]), int(array[4])))
                            if not WorldData.Legacy.tile_textures_loaded and not "door" in array[0]:
                                try:
                                    global_texture1 = globals()[str(array[0])]
                                except KeyError:
                                    global_texture1 = None
                                try:
                                    global_texture2 = globals(
                                    )[str(array[0] + "_texture")]
                                except KeyError:
                                    global_texture2 = None

                                if isinstance(global_texture1, pygame.Surface):
                                    WorldData.Legacy.tile_textures[array[1]] = global_texture1.copy(
                                    )
                                elif isinstance(global_texture2, pygame.Surface):
                                    WorldData.Legacy.tile_textures[array[1]] = global_texture2.copy(
                                    )
                                else:
                                    KDS.Logging.AutoError(
                                        "Texture not found. " + array[0], currentframe())

                        elif Type == 1:
                            convertDecorationRules.append(array[1])
                            convertDecorationColors.append(
                                (int(array[2]), int(array[3]), int(array[4])))
                        elif Type == 2:
                            convertEnemyRules.append(array[1])
                            convertEnemyColors.append(
                                (int(array[2]), int(array[3]), int(array[4])))
                        elif Type == 3:
                            convertItemRules.append(array[1])
                            convertItemColors.append(
                                (int(array[2]), int(array[3]), int(array[4])))

            WorldData.Legacy.tile_textures_loaded = True

            building_gen = []
            decoration_gen = []
            enemy_gen = []
            WorldData.Legacy.item_gen = []

            BitmapSize = buildingBitmap.get_size()
            for i in range(BitmapSize[1]):
                building_layer = []
                decoration_layer = []
                enemy_layer = []
                item_layer = []
                for j in range(BitmapSize[0]):
                    building_layer.append(convertBuildingRules[convertBuildingColors.index(
                        buildingBitmap.get_at((j, i))[:3])])
                    decoration_layer.append(convertDecorationRules[convertDecorationColors.index(
                        decorationBitmap.get_at((j, i))[:3])])
                    enemy_layer.append(
                        convertEnemyRules[convertEnemyColors.index(enemyBitmap.get_at((j, i))[:3])])
                    item_layer.append(
                        convertItemRules[convertItemColors.index(itemBitmap.get_at((j, i))[:3])])

                building_gen.append(building_layer)
                decoration_gen.append(decoration_layer)
                enemy_gen.append(enemy_layer)
                WorldData.Legacy.item_gen.append(item_layer)

            WorldData.Legacy.world_gen = (
                building_gen, decoration_gen, enemy_gen, WorldData.Legacy.item_gen)

            # Use the index to get the letter and make the file using the letters

            WorldData.Legacy.tile_rects, WorldData.Legacy.toilets, WorldData.Legacy.burning_toilets, WorldData.Legacy.trashcans, WorldData.Legacy.burning_trashcans, WorldData.Legacy.jukeboxes, WorldData.Legacy.landmines, WorldData.Legacy.zombies, WorldData.Legacy.sergeants, WorldData.Legacy.archviles, WorldData.Legacy.ladders, WorldData.Legacy.bulldogs, iron_bars, imps = load_rects()
            KDS.Logging.Log(KDS.Logging.LogType.debug,
                            "Zombies Initialised: " + str(len(WorldData.Legacy.zombies)), False)
            for zombie in WorldData.Legacy.zombies:
                KDS.Logging.Log(KDS.Logging.LogType.debug,
                                "Initialised Zombie: " + str(zombie), False)

            WorldData.Legacy.item_rects, WorldData.Legacy.item_ids, WorldData.Legacy.task_items = load_item_rects()
            random.shuffle(WorldData.Legacy.task_items)

            KDS.Logging.Log(KDS.Logging.LogType.debug,
                            "Items Initialised: " + str(len(WorldData.Legacy.item_ids)), False)
            for i_id in WorldData.Legacy.item_ids:
                KDS.Logging.Log(KDS.Logging.LogType.debug,
                                "Initialised Item: (ID)" + i_id, False)
            WorldData.Legacy.door_rects, WorldData.Legacy.doors_open, WorldData.Legacy.color_keys = load_doors()

    @staticmethod
    def LoadMap():
        global tiles, items, enemies, decoration, specialTiles, Projectiles
        MapPath = os.path.join("Assets", "Maps", "map" + current_map)
        PersistentMapPath = os.path.join(PersistentPaths.CachePath, "map")
        if os.path.isdir(PersistentMapPath):
            shutil.rmtree(PersistentMapPath)
        if os.path.isdir(MapPath):
            shutil.copytree(MapPath, PersistentMapPath)
        elif os.path.isfile(MapPath + ".map"):
            with zipfile.ZipFile(MapPath + ".map", "r") as mapZip:
                mapZip.extractall(PersistentMapPath)
                mapZip.close()
        else:
            KDS.Logging.AutoError("Map file is not a valid format.", currentframe())
            
        for fname in os.listdir(PersistentMapPath):
            fpath = os.path.join(PersistentMapPath, fname)
            if os.path.isdir(fpath):
                for _fname in os.listdir(fpath):
                    _fpath = os.path.join(fpath, _fname)
                    if os.path.isfile(_fpath):
                        shutil.copy(_fpath, PersistentMapPath)
                    else:
                        KDS.Logging.AutoError("Map file is not a valid format.", currentframe())
                shutil.rmtree(fpath)
        with open(os.path.join(PersistentMapPath, "level.dat"), "r") as map_file:
            map_data = map_file.read().split("\n")
            map_file.close()
        items = numpy.array([])
        enemies = numpy.array([])
        decoration = numpy.array([])
        specialTiles = numpy.array([])

        max_map_width = len(max(map_data))
        WorldData.MapSize = (max_map_width, len(map_data))

        # Luodaan valmiiksi koko kentän kokoinen numpy array täynnä ilma rectejä
        tiles = numpy.array([[Tile((x * 34, y * 34), 0) for x in range(
            WorldData.MapSize[0] + 1)] for y in range(WorldData.MapSize[1] + 1)])

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
                                tiles[y][x] = Tile(
                                    (x * 34, y * 34), serialNumber=serialNumber)
                            else:
                                tiles[y][x] = specialTilesD[serialNumber](
                                    (x * 34, y * 34), serialNumber=serialNumber)
                        elif data[0] == "1":
                            items = numpy.append(items, Item(
                                (x * 34, y * 34), serialNumber=serialNumber))
                        elif data[0] == "2":
                            pass
                        elif data[0] == "3":
                            pass
                else:
                    x += 1
            y += 1
        
        Audio.MusicMixer.load(os.path.join(PersistentMapPath, "music.mp3"))
        Audio.MusicMixer.play(-1)
        Audio.MusicMixer.set_volume(Audio.MusicVolume)
#endregion
#region Data
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Data...")
with open("Assets/Textures/tile_textures.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
t_textures = {}
for element in data:
    num = int(element.split(",")[0])
    res = element.split(",")[1]
    t_textures[num] = pygame.image.load(
        "Assets/Textures/Map/" + res).convert()
    t_textures[num].set_colorkey(KDS.Colors.GetPrimary.White)

with open("Assets/Textures/item_textures.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
i_textures = {}
for element in data:
    num = int(element.split(",")[0])
    res = element.split(",")[1]
    i_textures[num] = pygame.image.load(
        "Assets/Textures/Items/" + res).convert()
    i_textures[num].set_colorkey(KDS.Colors.GetPrimary.White)

with open("Assets/Textures/inventory_items.txt", "r") as f:
    data = f.read().split("\n")
    f.close()
inventory_items = []
for element in data:
    inventory_items.append(int(element))

class Inventory:

    def __init__(self, size):
        self.storage = ["none" for _ in range(size)]
        self.size = size
        self.SIndex = 0

    def render(self, Surface: pygame.Surface):
        pygame.draw.rect(Surface, (192, 192, 192),
                         (10, 75, self.size*34, 34), 3)

        if self.storage[self.SIndex] in inventoryDobulesSerialNumbers:
            slotwidth = 68
        else:
            slotwidth = 34

        pygame.draw.rect(screen, (70, 70, 70), ((
            (self.SIndex) * 34) + 10, 75, slotwidth, 34), 3)

        index = 0
        for i in self.storage:
            if i in i_textures:
                Surface.blit(i_textures[i], (int(index * 34 + 10 + i_textures[i].get_size()[0] / 4), int(75 + i_textures[i].get_size()[1] / 4)))
            index += 1

    def moveRight(self):
        KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.InventorySlotSwitching)
        self.SIndex += 1
        if self.SIndex < self.size:
            if self.storage[self.SIndex] == "doubleItemPlaceholder":
                self.SIndex += 1

        if self.SIndex > self.size - 1:
            self.SIndex = 0

    def moveLeft(self):
        KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.InventorySlotSwitching)
        self.SIndex -= 1
        if self.SIndex >= 0:
            if self.storage[self.SIndex] == "doubleItemPlaceholder":
                self.SIndex -= 1
        if self.SIndex < 0:
            self.SIndex = self.size - 1

    def pickSlot(self, index):
        KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.InventorySlotSwitching)
        if 0 < index < len(self.storage)-1:
            if self.storage[index] == "doubleItemPlaceholder":
                self.SIndex = index-2
            else:
                self.SIndex = index-1

    def dropItem(self):
        if self.storage[self.SIndex] != "none":
            if self.SIndex < self.size - 1:
                if self.storage[self.SIndex + 1] == "doubleItemPlaceholder":
                    serialNumber = self.storage[self.SIndex]
                    self.storage[self.SIndex] = "none"
                    self.storage[self.SIndex + 1] = "none"
                    return serialNumber
            serialNumber = self.storage[self.SIndex]
            self.storage[self.SIndex] = "none"
            return serialNumber

    def useItem(self, Surface: pygame.Surface, *args):
        if self.storage[self.SIndex] != "none":
            dumpValues = Ufunctions[self.storage[self.SIndex]](args, Surface)
            if direction:
                renderOffset = -dumpValues.get_size()[0]
            else:
                renderOffset = player_rect.width + 2

            Surface.blit(pygame.transform.flip(dumpValues, direction, False), (player_rect.x - scroll[0] + renderOffset, player_rect.y + 10 -scroll[1]))
        return None

    def getHandItem(self):
        return self.storage[self.SIndex]

player_inventory = Inventory(5)

with open("Assets/Textures/special_tiles.txt", 'r') as f:
    specialTilesSerialNumbers = [int(number) for number in f.read().split("\n")]
    f.close()
KDS.Logging.Log(KDS.Logging.LogType.debug, "Data Loading Complete.")
KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Tiles...")
class Tile:

    def __init__(self, position: (int, int), serialNumber: int):
        self.rect = pygame.Rect(position[0], position[1], 34, 34)
        self.serialNumber = serialNumber
        if serialNumber:
            self.texture = t_textures[serialNumber]
            self.air = False
        else:
            self.air = True
        self.specialTileFlag = True if serialNumber in specialTilesSerialNumbers else False
        self.checkCollision = True

    @staticmethod
    # Tile_list is a 2d numpy array
    def renderUpdate(Tile_list, Surface: pygame.Surface, scroll: list, position: (int, int), *args):
        x = int(position[0] / 34)
        y = int(position[1] / 34)
        x -= 11
        y -= 8
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        max_x = len(Tile_list[0])-1
        max_y = len(Tile_list) - 1
        end_x = x + 22
        end_y = y + 15
        if end_x > max_x:
            end_x = max_x
        if end_y > max_y:
            end_y = max_y

        for row in Tile_list[y:end_y]:
            for renderable in row[x:end_x]:
                if not renderable.air:
                    if not renderable.specialTileFlag:
                        Surface.blit(renderable.texture, (renderable.rect.x -
                                                        scroll[0], renderable.rect.y - scroll[1]))
                    else: 
                        Surface.blit(renderable.update(), (renderable.rect.x -
                                                        scroll[0], renderable.rect.y - scroll[1]))                        

#region Erikois-tilet >>>>>>>>>>>>>>

class Toilet(Tile):
    def __init__(self, position:(int, int), serialNumber: int, _burning=False):        
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = toilet0
        self.animation = KDS.Animator.Animation("toilet_anim", 3, 5, (KDS.Colors.GetPrimary.White), -1)
        self.checkCollision = True

    def update(self):
        
        if KDS.Math.getDistance((player_rect.centerx, player_rect.centery),(self.rect.centerx, self.rect.centery)) < 50 and gasburnerBurning and not self.burning:
            self.burning = True
            global player_score
            player_score += 30
        if self.burning:
            return self.animation.update()
        else:
            return self.texture

class Trashcan(Tile):
    def __init__(self, position:(int, int), serialNumber: int, _burning=False):        
        super().__init__(position, serialNumber)
        self.burning = _burning
        self.texture = trashcan
        self.animation = KDS.Animator.Animation("trashcan", 3, 6, KDS.Colors.GetPrimary.White, -1)
        self.checkCollision = True

    def update(self):
        
        if KDS.Math.getDistance((player_rect.centerx, player_rect.centery),(self.rect.centerx, self.rect.centery)) < 48 and gasburnerBurning and not self.burning:
            self.burning = True
            global player_score
            player_score += 20
        if self.burning:
            return self.animation.update()
        else:
            return self.texture

class Jukebox(Tile):
    def __init__(self, position:(int, int), serialNumber: int):        
        positionC = (position[0], position[1] - 26)
        super().__init__(positionC, serialNumber)
        self.texture = jukebox_texture
        self.rect = pygame.Rect(position[0], position[1] - 27, 40, 60)
        self.checkCollision = False

    def stopPlayingTrack(self):
        global jukeboxMusicPlaying
        for music in jukebox_music:
            music.stop()
        jukeboxMusicPlaying = -1
        Audio.MusicMixer.unpause()
        Audio.MusicMixer.set_volume(Audio.MusicVolume)

    def update(self):
        global jukeboxMusicPlaying
        if self.rect.colliderect(player_rect):
            screen.blit(jukebox_tip, (self.rect.x - scroll[0] - 20, self.rect.y - scroll[1]-30))
            if KDS.Keys.GetClicked(KDS.Keys.functionKey):
                self.stopPlayingTrack()
                Audio.MusicMixer.pause()
                loopStopper = 0
                while (jukeboxMusicPlaying in lastJukeboxSong or jukeboxMusicPlaying == -1) and loopStopper < 10:
                    jukeboxMusicPlaying = int(random.uniform(0, len(jukebox_music)))
                    loopStopper += 1
                lastJukeboxSong.pop(0)
                lastJukeboxSong.append(jukeboxMusicPlaying)
                Audio.playSound(jukebox_music[jukeboxMusicPlaying], Audio.MusicVolume)
            elif KDS.Keys.GetHeld(KDS.Keys.functionKey):
                self.stopPlayingTrack()
        if jukeboxMusicPlaying != -1:
            lerp_multiplier = KDS.Math.getDistance(self.rect.midbottom, player_rect.midbottom) / 350
            jukebox_volume = KDS.Math.Lerp(0, 1, KDS.Math.Clamp(lerp_multiplier, 0, 1))
            jukebox_music[jukeboxMusicPlaying].set_volume(jukebox_volume)

        return self.texture

class Door(Tile):

    def __init__(self, position:(int, int), serialNumber: int, closingCounter = 600):        
        super().__init__(position, serialNumber)
        self.texture = t_textures[serialNumber]
        self.opentexture = door_open
        self.rect = pygame.Rect(position[0], position[1], 5, 68)
        self.checkCollision = True
        self.open = False
        self.maxclosingCounter = closingCounter
        self.closingCounter = 0
    
    def update(self):
        keys = {
            24: "red",
            25: "green",
            26: "blue"
        }
        if self.open:
            self.closingCounter += 1
            if self.closingCounter > self.maxclosingCounter:
                door_opening.play()
                self.open = False
                self.checkCollision = True
                self.closingCounter = 0
        if KDS.Math.getDistance((player_rect.centerx, player_rect.centery), (self.rect.centerx,self.rect.centery)) < 20 and KDS.Keys.GetClicked(KDS.Keys.functionKey):
            if self.serialNumber == 23 or player_keys[keys[self.serialNumber]]:
                door_opening.play()
                self.open = not self.open
                self.checkCollision = not self.checkCollision
        if not self.open:
            return self.texture
        else:
            return self.opentexture

class Landmine(Tile):
    def __init__(self, position:(int, int), serialNumber: int):        
        super().__init__(position, serialNumber)
        self.texture = landmine_texture
        self.rect = pygame.Rect(position[0], position[1]+26, 22, 11)
        self.checkCollision = False

    def update(self):
        if self.rect.colliderect(player_rect):
            self.air = True
            landmine_explosion.play()
            Explosions.append(KDS.World.Explosion(KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.GetPrimary.White, 1), (self.rect.x-60, self.rect.y-60)))           
        return self.texture

specialTilesD = {
    15: Toilet,
    16: Trashcan,
    19: Jukebox,
    21: Landmine,
    23: Door,
    24: Door,
    25: Door,
    26: Door
}

KDS.Logging.Log(KDS.Logging.LogType.debug, "Tile Loading Complete.")
#endregion

itemTip = tip_font.render(
    "Nosta Esine Painamalla [E]", True, KDS.Colors.GetPrimary.White)
player_score = 0

class pickupFunctions:  # Jokaiselle itemille määritetään funktio, joka kutsutaan, kun item poimitaan maasta
    @staticmethod
    def gasburner_p():
        global player_score
        gasburner_clip.play()
        player_score += 10

        return False

    @staticmethod
    def coffeemug_p():
        global player_score
        coffeemug_sound.play()
        player_score += 6

        return False

    @staticmethod
    def knife_p():
        global player_score
        knife_pickup.play()
        player_score += 10

        return False

    @staticmethod
    def ss_bonuscard_p():
        global player_score
        ss_sound.play()
        player_score += 10

        return False

    @staticmethod
    def lappi_sytytyspalat_p():
        global player_score
        lappi_sytytyspalat_sound.play()
        player_score += 10

        return False

    @staticmethod
    def iPuhelin_p():
        global player_score
        item_pickup.play()
        player_score -= 10

        return False

    @staticmethod
    def plasmarifle_p():
        global player_score
        weapon_pickup.play()
        player_score += 20

        return False

    @staticmethod
    def pistol_p():
        global player_score
        weapon_pickup.play()
        player_score += 20

        return False

    @staticmethod
    def rk62_p():
        global player_score, rk_62_ammo
        weapon_pickup.play()
        player_score += 20
        rk_62_ammo += 30

        return False

    @staticmethod
    def shotgun_p():
        global player_score
        weapon_pickup.play()
        player_score += 20

        return False

    @staticmethod
    def cell_p():
        global player_score, ammunition_plasma
        item_pickup.play()
        player_score += 1

        ammunition_plasma += 30
        return True

    @staticmethod
    def red_key_p():
        global player_keys
        key_pickup.play()
        player_keys["red"] = True

        return True

    @staticmethod
    def green_key_p():
        global player_keys
        key_pickup.play()
        player_keys["green"] = True

        return True

    @staticmethod
    def blue_key_p():
        global player_keys
        key_pickup.play()
        player_keys["blue"] = True

        return True

    @staticmethod
    def medkit_p():
        global player_health
        item_pickup.play()
        if player_health < 100:
            player_health += 25
            if player_health > 100:
                player_health = 100

        return True

    @staticmethod
    def pistol_mag_p():
        global pistol_bullets
        item_pickup.play()
        pistol_bullets += 7

        return True

    @staticmethod
    def rk_mag_p():
        global rk_62_ammo
        rk_62_ammo += 30
        item_pickup.play()

        return True

    @staticmethod
    def shotgun_shells_p():
        global shotgun_shells
        shotgun_shells += 4
        item_pickup.play()

        return True

    @staticmethod
    def soulsphere_p():
        global player_health
        player_health += 100
        if player_health > 200:
            player_health = 200

        return True

    @staticmethod
    def turboneedle_p():
        global playerStamina
        playerStamina += 250

    @staticmethod
    def empyOperation():
        return True


class itemFunctions:  # Jokaiselle inventoryyn menevälle itemille määritetään funktio, joka kutsutaan itemiä käytettäessä
    #rk62_C = KDS.World.itemTools.rk62()
    # Ensimmäisenä funktion tulee palauttaa itemin näytöllä näytettävä tekstuuri

    @staticmethod
    def gasburner_u(*args):
        global gasburnerBurning
        
        if args[0][0] == True:
            gasburnerBurning = True
            gasburner_fire.stop()
            gasburner_fire.play()
            return gasburner_animation_object.update()
        else:
            gasburner_fire.stop()
            gasburnerBurning = False
            return gasburner_off

            
    @staticmethod
    def coffeemug_u(*args):

        return coffeemug

    @staticmethod
    def iPuhelin_u(*args):

        return ipuhelin_texture

    @staticmethod
    def knife_u(*args):
        if args[0][0]:
            return knife_animation_object.update()
        else:
            return knife

    @staticmethod
    def lappi_sytytyspalat_u(*args):

        return lappi_sytytyspalat

    @staticmethod
    def pistol_u(*args):
        global pistol_bullets, Projectile, tiles
        args[1].blit(harbinger_font.render("Ammo: " + str(pistol_bullets), True, KDS.Colors.GetPrimary.White), (10, 360))      
        if args[0][0] and KDS.World.pistol_C.counter > 50 and pistol_bullets > 0:
            pistol_shot.play()
            KDS.World.pistol_C.counter = 0
            pistol_bullets -= 1
            Projectiles.append(KDS.World.Bullet(pygame.Rect(player_rect.centerx+30*KDS.Math.Jd(direction),player_rect.centery-19,2,2),direction, -1, tiles, 55))
            return pistol_f_texture
        else:
            KDS.World.pistol_C.counter += 1
            return pistol_texture

    @staticmethod
    def plasmarifle_u(*args):
        global ammunition_plasma
        args[1].blit(harbinger_font.render("Ammo: " + str(ammunition_plasma), True, KDS.Colors.GetPrimary.White), (10, 360))                    
        if args[0][0] and ammunition_plasma > 0 and KDS.World.plasmarifle_C.counter > 3:
            KDS.World.plasmarifle_C.counter = 0
            plasmarifle_f_sound.play()
            ammunition_plasma -= 1
            if direction:
                temp = 80
            else:
                temp = -80
            Projectiles.append(KDS.World.Bullet(pygame.Rect(player_rect.centerx-temp,player_rect.centery-19,2,2),direction, 27, tiles, 20, plasma_ammo))
            return plasmarifle_animation.update()
        else:
            KDS.World.plasmarifle_C.counter += 1
            return plasmarifle

    @staticmethod
    def rk62_u(*args):
        global rk_62_ammo, tiles, Projectiles
        args[1].blit(harbinger_font.render("Ammo: " + str(rk_62_ammo), True, KDS.Colors.GetPrimary.White), (10, 360))
        if args[0][0] and KDS.World.rk62_C.counter > 4 and rk_62_ammo > 0:
            KDS.World.rk62_C.counter = 0
            rk62_shot.stop()
            rk62_shot.play()
            rk_62_ammo -= 1
            Projectiles.append(KDS.World.Bullet(pygame.Rect(player_rect.centerx+60*KDS.Math.Jd(direction),player_rect.centery-19,2,2),direction, -1, tiles, 25))
            return rk62_f_texture
        else:
            if not args[0][0]:
                rk62_shot.stop() 
            KDS.World.rk62_C.counter += 1
            return rk62_texture

    @staticmethod
    def shotgun_u(*args):
        global shotgun_shells, Projectile, tile
        args[1].blit(harbinger_font.render("Ammo: " + str(shotgun_shells), True, KDS.Colors.GetPrimary.White), (10, 360))
        if args[0][1] and KDS.World.shotgun_C.counter > 50 and shotgun_shells > 0:
            KDS.World.shotgun_C.counter = 0
            player_shotgun_shot.play()
            shotgun_shells -= 1
            shotgun_shots()
            return shotgun_f
        else:
            KDS.World.shotgun_C.counter += 1
            return shotgun

    @staticmethod
    def ss_bonuscard_u(*args):
        
        return ss_bonuscard

    @staticmethod
    def empyOperation(*args):

        return i_textures[0]


Pfunctions = {
    0: pickupFunctions.empyOperation,
    1: pickupFunctions.blue_key_p,
    2: pickupFunctions.cell_p,
    3: pickupFunctions.coffeemug_p,
    4: pickupFunctions.gasburner_p,
    5: pickupFunctions.green_key_p,
    6: pickupFunctions.iPuhelin_p,
    7: pickupFunctions.knife_p,
    8: pickupFunctions.lappi_sytytyspalat_p,
    9: pickupFunctions.medkit_p,
    10: pickupFunctions.pistol_p,
    11: pickupFunctions.pistol_mag_p,
    12: pickupFunctions.plasmarifle_p,
    13: pickupFunctions.red_key_p,
    14: pickupFunctions.rk_mag_p,
    15: pickupFunctions.rk62_p,
    16: pickupFunctions.shotgun_p,
    17: pickupFunctions.shotgun_shells_p,
    18: pickupFunctions.soulsphere_p,
    19: pickupFunctions.ss_bonuscard_p,
    20: pickupFunctions.turboneedle_p
}

Ufunctions = {
    0: itemFunctions.empyOperation,
    3: itemFunctions.coffeemug_u,
    4: itemFunctions.gasburner_u,
    6: itemFunctions.iPuhelin_u,
    7: itemFunctions.knife_u,
    8: itemFunctions.lappi_sytytyspalat_u,
    10: itemFunctions.pistol_u,
    12: itemFunctions.plasmarifle_u,
    15: itemFunctions.rk62_u,
    16: itemFunctions.shotgun_u,
    19: itemFunctions.ss_bonuscard_u

}

KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Items...")
class Item:

    def __init__(self, position: (int, int), serialNumber: int):
        if serialNumber:
            self.texture = i_textures[serialNumber]
        self.rect = pygame.Rect(position[0], position[1]+(34-self.texture.get_size()[
                                1]), self.texture.get_size()[0], self.texture.get_size()[1])
        self.serialNumber = serialNumber

    @staticmethod
    # Item_list is a 2d numpy array
    def render(Item_list, Surface: pygame.Surface, scroll: list, position: (int, int)):

        for renderable in Item_list:
            if DebugMode:
                pygame.draw.rect(screen, KDS.Colors.GetPrimary.Blue, pygame.Rect(renderable.rect.x - scroll[0], renderable.rect.y - scroll[1], renderable.rect.width, renderable.rect.height))
            Surface.blit(renderable.texture, (renderable.rect.x - scroll[0], renderable.rect.y-scroll[1]))

    @staticmethod
    def checkCollisions(Item_list, collidingRect: pygame.Rect, Surface: pygame.Surface, scroll, functionKey: bool, inventory: Inventory):
        index = 0
        showItemTip = True
        collision = False
        shortest_index = 0
        shortest_distance = sys.maxsize
        for item in Item_list:
            if collidingRect.colliderect(item.rect):
                collision = True
                distance = KDS.Math.getDistance(item.rect.midbottom, player_rect.midbottom)
                if distance < shortest_distance:
                    shortest_index = index
                    shortest_distance = distance
                if functionKey:
                    if item.serialNumber not in inventoryDobulesSerialNumbers:
                        if inventory.storage[inventory.SIndex] == "none":
                            temp_var = Pfunctions[item.serialNumber]()
                            if not temp_var:
                                inventory.storage[inventory.SIndex] = item.serialNumber
                            Item_list = numpy.delete(Item_list, index)
                            showItemTip = False
                        elif item.serialNumber not in inventory_items:
                            Pfunctions[item.serialNumber]()
                            Item_list = numpy.delete(Item_list, index)
                            showItemTip = False
                    else:
                        if inventory.SIndex < inventory.size-1 and inventory.storage[inventory.SIndex] == "none":
                            if inventory.storage[inventory.SIndex + 1] == "none":
                                Pfunctions[item.serialNumber]()
                                inventory.storage[inventory.SIndex] = item.serialNumber
                                inventory.storage[inventory.SIndex +
                                                  1] = "doubleItemPlaceholder"
                                Item_list = numpy.delete(Item_list, index)
                                showItemTip = False
            index += 1
        
        if collision and showItemTip:
            Surface.blit(itemTip, (Item_list[shortest_index].rect.centerx - int(itemTip.get_width() / 2) - scroll[0], Item_list[shortest_index].rect.bottom - 45 - scroll[1]))

        return Item_list, inventory
KDS.Logging.Log(KDS.Logging.LogType.debug, "Item Loading Complete.")

def load_items(path):
    with open(path, 'r') as f:
        data = f.read()
        f.close()
    data = data.split('\n')
    item_map = []
    for row in data:
        item_map.append(list(row))
    return item_map


def load_jukebox_music():
    musikerna = os.listdir("Assets/Audio/JukeboxMusic/")
    musics = []
    for musiken in musikerna:
        musics.append(pygame.mixer.Sound("Assets/Audio/JukeboxMusic/" + musiken))
    random.shuffle(musics)
    return musics
jukebox_music = load_jukebox_music()


def shakeScreen():
    scroll[0] += random.randint(-10, 10)
    scroll[1] += random.randint(-10, 10)

def load_ads():
    ad_files = os.listdir("Assets/Textures/KoponenTalk/ads")

    random.shuffle(ad_files)
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    f"Initialising {len(ad_files)} Ad Files...", False)

    ad_images = []

    for ad in ad_files:
        path = str("Assets/Textures/KoponenTalk/ads/" + ad)
        image = pygame.image.load(path).convert()
        image.set_colorkey(KDS.Colors.GetPrimary.Red)
        ad_images.append(image)
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        f"Initialised Ad File: {ad}", False)

    return ad_images

KDS.Logging.Log(KDS.Logging.LogType.debug, "Loading Animations...")
ad_images = load_ads()
koponen_talking_background = pygame.image.load(
    "Assets/Textures/KoponenTalk/background.png").convert()
koponen_talking_foreground_indexes = [0, 0, 0, 0, 0]

def load_rects():
    global monsterAmount, monstersLeft
    tile_rects = []
    toilets = []
    trashcans = []
    burning_toilets = []
    burning_trashcans = []
    jukeboxes = []
    landmines = []
    zombies = []
    sergeants = []
    archviles = []
    ladders = []
    bulldogs = []
    iron_bars = []
    imps = []
    w = [0, 0]
    for i in range(len(WorldData.Legacy.world_gen) - 1):
        y = 0
        for layer in WorldData.Legacy.world_gen[i]:
            x = 0
            for tile in layer:
                if tile != 'a':
                    if tile == 'f':
                        WorldData.Legacy.tile_rects.append(
                            pygame.Rect(x * 34, y * 34, 14, 21))
                    elif tile == 'e':
                        w = list(toilet0.get_size())
                        WorldData.Legacy.toilets.append(
                            pygame.Rect(x * 34-2, y * 34, 34, 34))
                        WorldData.Legacy.burning_toilets.append(False)
                        WorldData.Legacy.tile_rects.append(
                            pygame.Rect(x * 34, y * 34, w[0], w[1]))
                    elif tile == 'g':
                        w = list(trashcan.get_size())
                        WorldData.Legacy.trashcans.append(
                            pygame.Rect(x * 34-1, y * 34, w[0]+2, w[1]))
                        WorldData.Legacy.burning_trashcans.append(False)
                        WorldData.Legacy.tile_rects.append(
                            pygame.Rect(x * 34, y * 34+8, w[0], w[1]))
                    elif tile == 'q':
                        WorldData.Legacy.ladders.append(
                            pygame.Rect((x * 34) + 16, (y * 34) - 2, 2, 38))
                    elif tile == 'k':
                        pass
                    elif tile == 'l':
                        pass
                    elif tile == 'm':
                        pass
                    elif tile == 'n':
                        pass
                    elif tile == 's':
                        iron_bars.append(pygame.Rect(x * 34, y * 34, 1, 1))
                    elif tile == 'A':
                        pass
                    elif tile == 'B':
                        WorldData.Legacy.jukeboxes.append(
                            pygame.Rect(x * 34, y * 34 - 26, 42, 60))
                    elif tile == 'C':
                        WorldData.Legacy.landmines.append(
                            pygame.Rect(x * 34+6, y * 34+23, 22, 11))
                    elif tile == 'Z':
                        WorldData.Legacy.zombies.append(
                            KDS.AI.Zombie((x * 34, y * 34 - 34), 100, 1))
                        monsterAmount += 1
                    elif tile == 'S':
                        WorldData.Legacy.sergeants.append(KDS.AI.SergeantZombie(
                            (x * 34, y * 34 - 34), 220, 1))
                        monsterAmount += 1
                    elif tile == 'V':
                        WorldData.Legacy.archviles.append(
                            Archvile((x * 34, y * 34-51), 750, 2))
                        monsterAmount += 1
                    elif tile == 'K':
                        WorldData.Legacy.bulldogs.append(KDS.AI.Bulldog(
                            (x * 34, y * 34), 80, 3, bulldog_run_animation))
                        monsterAmount += 1
                    elif tile == 'I':
                        imps.append(KDS.AI.Imp(280, 1, (x * 34, y * 34-34),
                                               WorldData.Legacy.tile_rects, "imp_walking", "imp_attacking", "imp_dying"))
                        imp_temp = imps[-1].r()
                        if imp_temp == "continue":
                            monsterAmount += 1
                        else:
                            del imps[-1]
                        del imp_temp
                        pass
                    else:
                        WorldData.Legacy.tile_rects.append(
                            pygame.Rect(x * 34, y * 34, 34, 34))

                x += 1
            y += 1
    monstersLeft = monsterAmount
    return tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, WorldData.Legacy.landmines, zombies, sergeants, archviles, ladders, bulldogs, iron_bars, imps

#endregion
#region Collisions

def shotgun_shots():
    shots = []
    global direction
    shots_direction = not direction
    for _ in range(7):
        shots.append([player_rect.centerx, player_rect.centery-20])

    q = True
    counter = 0
    dir_counter = 0
    while q:

        for tile in WorldData.Legacy.tile_rects:
            for shot in shots:
                if tile.collidepoint(shot):
                    shots.remove(shot)

        for zombie1 in WorldData.Legacy.zombies:
            for shot in shots:
                if zombie1.rect.collidepoint(shot):
                    shots.remove(shot)
                    zombie1.health -= 35

        for sergeant in WorldData.Legacy.sergeants:
            for shot in shots:
                if sergeant.rect.collidepoint(shot):
                    shots.remove(shot)
                    sergeant.health -= 35

        for archvile in WorldData.Legacy.archviles:
            for shot in shots:
                if archvile.rect.collidepoint(shot):
                    shots.remove(shot)
                    archvile.health -= 35

        for x in range(len(shots)):
            if shots_direction:
                shots[x][0] += 26
                if dir_counter > 4:
                    shots[x][1] += int((x - 2)*3)
            else:
                shots[x][0] -= 26
                shots[x][1] += int((x - 2)*3)

        counter += 1
        dir_counter += 1
        if dir_counter > 5:
            dir_counter = 0
        if counter > 80:
            q = False


def damage(health, min_damage: int, max_damage: int):
    health -= int(random.uniform(min_damage, max_damage))
    if health < 0:
        health = 0

    return health

def item_collision_test(rect, items):
    """Tests for item collisions.

    Args:
        rect (pygame.Rect): The rect to be tested.
        items (list): A list of item rects to be tested on.

    Returns:
        list: A list of all collided rects.
    """
    hit_list = []
    x = 0
    global player_hand_item, player_score, inventory, inventory_slot, player_keys, ammunition_plasma, pistol_bullets, rk_62_ammo, player_health, shotgun_shells, playerStamina

    itemTip = tip_font.render(
        "Nosta Esine Painamalla [E]", True, KDS.Colors.GetPrimary.White)

    def s(score):
        global player_score

        player_score += score

#endregion
#region Player

def collision_test(rect, Tile_list):
    hit_list = []
    x = int((rect.x/34)-3)
    y = int((rect.y/34)-3)
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    max_x = len(Tile_list[0])-1
    max_y = len(Tile_list)-1
    end_x = x+6
    end_y = y+6

    if end_x > max_x:
        end_x = max_x

    if end_y > max_y:
        end_y = max_y

    for row in Tile_list[y:end_y]:
        for tile in row[x:end_x]:
            if rect.colliderect(tile.rect) and not tile.air and tile.checkCollision:
                hit_list.append(tile.rect)
    return hit_list


def move_entity(rect, movement, tiles, skip_horisontal_movement_check=False, skip_vertical_movement_check=False):
    collision_types = {'top': False, 'bottom': False,
                       'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0 or skip_horisontal_movement_check:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0 or skip_horisontal_movement_check:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += int(movement[1])
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0 or skip_vertical_movement_check:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0 or skip_vertical_movement_check:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

stand_animation = KDS.Animator.Legacy.load_animation("stand", 2)
run_animation = KDS.Animator.Legacy.load_animation("run", 2)
short_stand_animation = KDS.Animator.Legacy.load_animation(
    "shortplayer_stand", 2)
short_run_animation = KDS.Animator.Legacy.load_animation("shortplayer_run", 2)
koponen_stand = KDS.Animator.Legacy.load_animation("koponen_standing", 2)
koponen_run = KDS.Animator.Legacy.load_animation("koponen_running", 2)
death_animation = KDS.Animator.Legacy.load_animation("death", 5)
menu_gasburner_animation = KDS.Animator.Animation(
    "main_menu_bc_gasburner", 2, 5, KDS.Colors.GetPrimary.White, -1)
gasburner_animation_object = KDS.Animator.Animation(
    "gasburner_on", 2, 5, KDS.Colors.GetPrimary.White, -1)
menu_toilet_animation = KDS.Animator.Animation(
    "menu_toilet_anim", 3, 6, KDS.Colors.GetPrimary.White, -1)
menu_trashcan_animation = KDS.Animator.Animation(
    "menu_trashcan", 3, 6, KDS.Colors.GetPrimary.White, -1)
burning_tree = KDS.Animator.Animation("tree_burning", 4, 5, (0, 0, 0), -1)
explosion_animation = KDS.Animator.Animation(
    "explosion", 7, 5, KDS.Colors.GetPrimary.White, 1)
plasmarifle_animation = KDS.Animator.Animation(
    "plasmarifle_firing", 2, 3, KDS.Colors.GetPrimary.White, -1)
zombie_death_animation = KDS.Animator.Animation(
    "z_death", 5, 6, KDS.Colors.GetPrimary.White, 1)
zombie_walk_animation = KDS.Animator.Animation(
    "z_walk", 3, 10, KDS.Colors.GetPrimary.White, -1)
zombie_attack_animation = KDS.Animator.Animation(
    "z_attack", 4, 10, KDS.Colors.GetPrimary.White, -1)
sergeant_walk_animation = KDS.Animator.Animation(
    "seargeant_walking", 4, 8, KDS.Colors.GetPrimary.White, -1)
sergeant_shoot_animation = KDS.Animator.Animation(
    "seargeant_shooting", 2, 6, KDS.Colors.GetPrimary.White, 1)

archvile_run_animation = KDS.Animator.Animation(
    "archvile_run", 3, 9, KDS.Colors.GetPrimary.White, -1)
arhcvile_attack_animation = KDS.Animator.Animation(
    "archvile_attack", 6, 16, KDS.Colors.GetPrimary.White, 1)
archvile_death_animation = KDS.Animator.Animation(
    "archvile_death", 7, 12, KDS.Colors.GetPrimary.White, 1)
flames_animation = KDS.Animator.Animation(
    "flames", 5, 3, KDS.Colors.GetPrimary.White, -1)
bulldog_run_animation = KDS.Animator.Animation(
    "bulldog", 5, 6, KDS.Colors.GetPrimary.White, - 1)

imp_walking = KDS.Animator.Animation(
    "imp_walking", 4, 19, KDS.Colors.GetPrimary.White, -1)
imp_attacking = KDS.Animator.Animation(
    "imp_attacking", 2, 16, KDS.Colors.GetPrimary.White, -1)
imp_dying = KDS.Animator.Animation(
    "imp_dying", 5, 16, KDS.Colors.GetPrimary.White, 1)

knife_animation_object = KDS.Animator.Animation(
    "knife", 2, 20, KDS.Colors.GetPrimary.White, -1)

#region Sergeant fixing
sergeant_shoot_animation.images = []
KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising Sergeant Shoot Animation Images...")
for _ in range(5):
    for _ in range(6):
        sergeant_shoot_animation.images.append(sergeant_aiming)
for _ in range(2):
    sergeant_shoot_animation.images.append(sergeant_firing)
for _ in range(2):
    for _ in range(6):
        sergeant_shoot_animation.images.append(sergeant_aiming)
KDS.Logging.Log(KDS.Logging.LogType.debug, f"Successfully Initialised {len(sergeant_shoot_animation.images)} Sergeant Shoot Animation Images...", False)
sergeant_shoot_animation.ticks = 43
#endregion
sergeant_death_animation = KDS.Animator.Animation(
    "seargeant_dying", 5, 8, KDS.Colors.GetPrimary.White, 1)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Animation Loading Complete.")
KDS.Logging.Log(KDS.Logging.LogType.debug, "Game Initialisation Complete.")
#endregion
#region Console
def console():
    global inventory, player_keys, player_health, koponen_happines
    wasFullscreen = False
    if isFullscreen:
        Fullscreen.Set()
        wasFullscreen = True

    command_input = input("command: ")
    command_input = command_input.lower()
    command_list = command_input.split()

    if command_list[0] == "give":
        if command_list[1] != "key":
            inventory[inventory_slot] = command_list[1]
            KDS.Logging.Log(KDS.Logging.LogType.info,
                            "Item was given: " + str(command_list[1]), True)
        else:
            if command_list[2] in player_keys:
                player_keys[command_list[2]] = True
                KDS.Logging.Log(KDS.Logging.LogType.info, "Item was given: " +
                                str(command_list[1]) + " " + str(command_list[2]), True)
            else:
                KDS.Logging.Log(KDS.Logging.LogType.info, "That item does not exist: " +
                                str(command_list[1]) + " " + str(command_list[2]), True)
    elif command_list[0] == "remove":
        if command_list[1] == "item":
            if inventory[inventory_slot] != "none":
                old_item = inventory[inventory_slot]
                inventory[inventory_slot] = "none"
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Item was removed: " + str(old_item), True)
            else:
                KDS.Logging.Log(
                    KDS.Logging.LogType.info, "Selected inventory slot is empty already!", True)
        elif command_list[1] == "key":
            if command_list[2] in player_keys:
                if player_keys[command_list[2]] == True:
                    player_keys[command_list[2]] = False
                    KDS.Logging.Log(KDS.Logging.LogType.info, "Item was removed: " +
                                    str(command_list[1]) + " " + str(command_list[2]), True)
                else:
                    KDS.Logging.Log(
                        KDS.Logging.LogType.info, "You don't have that item!", True)
            else:
                KDS.Logging.Log(KDS.Logging.LogType.info, "That item does not exist: " +
                                str(command_list[1]) + " " + str(command_list[2]), True)
        else:
            KDS.Logging.Log(KDS.Logging.LogType.info,
                            "Not a valid remove command.", True)
    elif command_list[0] == "playboy":
        koponen_happines = 1000
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "You are now a playboy", True)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        f"Koponen happines: {koponen_happiness}", True)
    elif command_list[0] == "kill" or command_list[0] == "stop":
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Stop command issued through console.", True)
        KDS_Quit()
    elif command_list[0] == "killme":
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Player kill command issued through console.", True)
        player_health = 0
    elif command_list[0] == "terms":
        setTerms = False
        if len(command_list) > 1:
            setTerms = KDS.Convert.ToBool(command_list[1])
            if setTerms != None:
                KDS.ConfigManager.SetSetting(
                    "Data", "TermsAccepted", str(setTerms))
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Terms status set to: " + str(setTerms), True)
            else:
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Please provide a proper state for terms & conditions", True)
        else:
            KDS.Logging.Log(KDS.Logging.LogType.info,
                            "Please provide a proper state for terms & conditions", True)
    elif command_list[0] == "woof":
        if len(command_list) > 1:
            woofState = KDS.Convert.ToBool(command_list[1])
            if woofState != None:
                for dog in WorldData.Legacy.bulldogs:
                    KDS.Logging.Log(KDS.Logging.LogType.info, str(
                        dog) + " woof status has been set to: " + str(woofState), True)
                    KDS.AI.Bulldog.SetAngry(dog, woofState)
            else:
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Please provide a proper state for woof", True)
        else:
            KDS.Logging.Log(KDS.Logging.LogType.info,
                            "Please provide a proper state for woof", True)
    else:
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "This command does not exist.", True)

    if wasFullscreen:
        Fullscreen.Set()
#endregion
#region Terms and Conditions
def agr(tcagr):
    global tcagr_running
    if tcagr == False:
        tcagr_running = True
    else:
        tcagr_running = False

    global main_running
    c = False

    def tcagr_agree_function():
        global tcagr_running
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Terms and Conditions have been accepted.", False)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "You said you will not get offended... Dick!", False)
        KDS.ConfigManager.SetSetting("Data", "TermsAccepted", "True")
        KDS.Logging.Log(KDS.Logging.LogType.debug, "Terms Agreed. Updated Value: " +
                        KDS.ConfigManager.LoadSetting("Data", "TermsAccepted", "False"), False)
        tcagr_running = False

    agree_button = KDS.UI.New.Button(pygame.Rect(465, 500, 270, 135), tcagr_agree_function, button_font1.render(
        "I Agree", True, KDS.Colors.GetPrimary.White))

    while tcagr_running:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    Fullscreen.Set()
                elif event.key == K_F4:
                    if pygame.key.get_pressed(K_LALT):
                        KDS_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)
        display.blit(agr_background, (0, 0))
        agree_button.update(display, mouse_pos, c)
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        c = False
    del agree_button
#endregion
#region Koponen Talk
def koponen_talk():
    global main_running, inventory, currently_on_mission, inventory, player_score, ad_images, koponen_talking_background, koponen_talking_foreground_indexes, koponenTalking
    conversations = []

    KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.KoponenTalk)

    koponenTalking = True
    pygame.mouse.set_visible(True)

    KDS.Keys.SetProgress(KDS.Keys.moveLeft, False)
    KDS.Keys.SetProgress(KDS.Keys.moveRight, False)
    KDS.Keys.SetPressed(KDS.Keys.moveRun, False)

    c = False

    for i in range(len(koponen_talking_foreground_indexes), 0):
        koponen_talking_foreground_indexes[i] = koponen_talking_foreground_indexes[i - 1]
    random_foreground = int(random.uniform(0, len(ad_images)))
    while random_foreground == koponen_talking_foreground_indexes[0] or random_foreground == koponen_talking_foreground_indexes[1] or random_foreground == koponen_talking_foreground_indexes[2] or random_foreground == koponen_talking_foreground_indexes[3] or random_foreground == koponen_talking_foreground_indexes[4]:
        random_foreground = int(random.uniform(0, len(ad_images)))
    koponen_talking_foreground_indexes[4] = random_foreground
    koponen_talk_foreground = ad_images[random_foreground].copy()

    def exit_function1():
        global koponenTalking
        koponenTalking = False

    def mission_function():
        global currently_on_mission, current_mission, taskTaivutettu, task

        conversations.append(f"{player_name}: Saisinko tehtävän?")
        if currently_on_mission:
            conversations.append("Koponen: Olen pahoillani, sinulla on")
            conversations.append("         tehtävä kesken")
            conversations.append("Koponen: Tehtäväsi oli tuoda minulle")
            conversations.append(f"         {task}.")
        elif WorldData.Legacy.task_items:
            current_mission = WorldData.Legacy.task_items[0]
            WorldData.Legacy.task_items.remove(WorldData.Legacy.task_items[0])
        if current_mission == "coffeemug":
            task = "kahvikuppi"
            taskTaivutettu = "kahvikupin"
        elif current_mission == "ss_bonuscard":
            task = "SS-etukortti"
            taskTaivutettu = "SS-etukortin"
        else:
            task = "[FINISHED]"
            taskTaivutettu = "[FINISHED]"

        if task == "[FINISHED]" or taskTaivutettu == "[FINISHED]":
            conversations.append("Koponen: Olet suorittanut kaikki")
            conversations.append("         tehtävät")
        elif currently_on_mission == False:
            conversations.append(
                f"Koponen: Toisitko minulle {taskTaivutettu}")
            currently_on_mission = True

    def date_function():
        global koponen_happines

        conversations.append(
            f"{player_name}: Tulisitko kanssani treffeille?")

        if koponen_happines > 90:
            conversations.append("Koponen: Tulisin mielelläni kanssasi")
        elif 91 > koponen_happines > 70:
            if int(random.uniform(0, 3)):
                conversations.append("Koponen: Kyllä ehdottomasti")
            else:
                conversations.append("Koponen: En tällä kertaa")
                koponen_happines -= 3
        elif 71 > koponen_happines > 50:
            if int(random.uniform(0, 2)):
                conversations.append("Koponen: Tulen kanssasi")
            else:
                conversations.append("Koponen: Ei kiitos")
                koponen_happines -= 3
        elif 51 > koponen_happines > 30:
            if int(random.uniform(0, 3)) == 3:
                conversations.append("Koponen: Tulen")
            else:
                conversations.append("Koponen: En tule")
                koponen_happines -= 7
        elif 31 > koponen_happines > 10:
            if int(random.uniform(0, 5)) == 5:
                conversations.append("Koponen: Kyllä")
            else:
                conversations.append("Koponen: Ei.")
                koponen_happines -= 10
        else:
            conversations.append("Koponen: Ei ei ei")

    def end_mission():
        global current_mission, currently_on_mission, player_score, koponen_happines

        try:
            taskTaivutettu
        except NameError:
            KDS.Logging.Log(KDS.Logging.LogType.warning,
                            "Task not defined. Defining task...", False)
            task = ""
            taskTaivutettu = ""

        if not currently_on_mission:
            conversations.append("Koponen: Sinulla ei ole palautettavaa")
            conversations.append("         tehtävää")
        else:
            if current_mission in inventory:
                missionRemoveRange = range(len(inventory))
                itemFound = False
                for i in missionRemoveRange:
                    if itemFound == False:
                        if inventory[i] == current_mission:
                            inventory[i] = "none"
                            itemFound = True
                conversations.append("Koponen: Loistavaa työtä")
                conversations.append("Game: Player score +60")
                player_score += 60
                koponen_happines += 10
                currently_on_mission = False
                current_mission = "none"
            else:
                conversations.append("Koponen: Housuistasi ei löydy")
                conversations.append("         pyytämääni esinettä.")
                conversations.append("Koponen: Tehtäväsi oli tuoda minulle.")
                conversations.append(f"         {task}")

    c = False

    conversations.append("Koponen: Hyvää päivää")

    exit_button = KDS.UI.New.Button(pygame.Rect(940, 700, 230, 80), exit_function1, button_font1.render(
        "EXIT", True, KDS.Colors.GetPrimary.White))
    mission_button = KDS.UI.New.Button(pygame.Rect(50, 700, 450, 80), mission_function, button_font1.render(
        "REQUEST MISSION", True, KDS.Colors.GetPrimary.White))
    date_button = KDS.UI.New.Button(pygame.Rect(50, 610, 450, 80), date_function, button_font1.render(
        "ASK FOR A DATE", True, KDS.Colors.GetPrimary.White))
    r_mission_button = KDS.UI.New.Button(pygame.Rect(510, 700, 420, 80), end_mission, button_font1.render(
        "RETURN MISSION", True, KDS.Colors.GetPrimary.White))

    while koponenTalking:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponenTalking = False
                elif event.key == K_F11:
                    Fullscreen.Set()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)
        display.blit(pygame.transform.scale(koponen_talking_background, (int(
            koponen_talking_background.get_width()), int(koponen_talking_background.get_height()))), (0, 0))
        display.blit(pygame.transform.scale(koponen_talk_foreground, (int(
            koponen_talk_foreground.get_width()), int(koponen_talk_foreground.get_height()))), (40, 474))
        pygame.draw.rect(display, (230, 230, 230),
                         pygame.Rect(40, 40, 700, 400))
        pygame.draw.rect(display, (30, 30, 30),
                         pygame.Rect(40, 40, 700, 400), 3)

        exit_button.update(display, mouse_pos, c)
        mission_button.update(display, mouse_pos, c)
        date_button.update(display, mouse_pos, c)
        r_mission_button.update(display, mouse_pos, c)

        while len(conversations) > 13:
            del conversations[0]
        for i in range(len(conversations)):
            row_text = text_font.render(conversations[i], True, (7, 8, 10))
            row_text_size = text_font.size(conversations[i])
            display.blit(pygame.transform.scale(row_text, (int(
                row_text_size[0]), int(row_text_size[1]))), (50, int(50 + (i * 30))))
        c = False
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        window.fill((0, 0, 0))
    pygame.mouse.set_visible(False)
#endregion
#region Game Start
def play_function(gamemode: KDS.Gamemode.Modes, reset_scroll):
    global main_menu_running, current_map, inventory, Audio, player_health, player_keys, player_hand_item, player_death_event, player_rect, animation_has_played, death_wait, true_scroll, farting, selectedSave
    KDS.Gamemode.SetGamemode(gamemode, int(current_map))
    player_inventory.storage = ["none", "none", "none", "none", "none"]
    if int(current_map) < 2:
        inventory[0] = "iPuhelin"
    WorldData.LoadMap()
    pygame.mouse.set_visible(False)
    main_menu_running = False
    player_hand_item = "none"

    player_death_event = False
    animation_has_played = False
    death_wait = 0

    player_rect.x = 100
    player_rect.y = 100
    if reset_scroll:
        true_scroll = [-200, -190]
    player_health = 100

    farting = False

    for key in player_keys:
        player_keys[key] = False
    KDS.Logging.Log(KDS.Logging.LogType.info,
                    "Press F4 to commit suicide", False)
    KDS.Logging.Log(KDS.Logging.LogType.info,
                    "Press Alt + F4 to get depression", False)
    
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
        LoadSave(selectedSave)
    else:
        LoadSave(-1)


def load_campaign(reset_scroll):
    global main_menu_running, current_map, inventory, Audio, player_health, player_keys, player_hand_item, player_death_event, player_rect, animation_has_played, death_wait, true_scroll
    KDS.Gamemode.SetGamemode(KDS.Gamemode.Modes.Campaign, int(current_map))
#endregion
#region Menus
def esc_menu_f():
    global esc_menu, go_to_main_menu, DebugMode, clock, c
    c = False

    esc_surface = pygame.Surface(display_size)
    
    esc_menu_background_proc = esc_menu_background.copy()
    esc_menu_background_proc.blit(black_tint, (0, 0))
    blurred = Image.frombytes("RGB", screen_size, pygame.image.tostring(esc_menu_background_proc, "RGB")).filter(ImageFilter.GaussianBlur(radius=6))
    esc_menu_background_blur = pygame.image.fromstring(blurred.tobytes("raw", "RGB"), screen_size, "RGB")

    def resume():
        global esc_menu
        esc_menu = False

    def save():
        SaveData()

    def settings():
        settings_menu()

    def goto_main_menu():
        global esc_menu, go_to_main_menu
        pygame.mixer.unpause()
        esc_menu = False
        go_to_main_menu = True

    resume_button = KDS.UI.New.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 400, 200, 30), resume, button_font.render("Resume", True, KDS.Colors.GetPrimary.White))
    save_button_enabled = True
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
        save_button_enabled = False
    save_button = KDS.UI.New.Button(pygame.Rect(int(display_size[0] / 2 - 100), 438, 200, 30), save, button_font.render(
        "Save", True, KDS.Colors.GetPrimary.White), enabled=save_button_enabled)
    settings_button = KDS.UI.New.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 475, 200, 30), settings, button_font.render("Settings", True, KDS.Colors.GetPrimary.White))
    main_menu_button = KDS.UI.New.Button(pygame.Rect(int(
        display_size[0] / 2 - 100), 513, 200, 30), goto_main_menu, button_font.render("Main menu", True, KDS.Colors.GetPrimary.White))

    anim_lerp_x = KDS.Animator.Lerp(1.0, 0.0, 15, KDS.Animator.OnAnimationEnd.Stop)

    while esc_menu:
        display.blit(pygame.transform.scale(esc_menu_background, display_size), (0, 0))
        anim_x = anim_lerp_x.update(False)
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    Fullscreen.Set()
                elif event.key == K_ESCAPE:
                    esc_menu = False
                elif event.key == K_F4:
                    if pygame.key.get_pressed(K_LALT):
                        KDS_Quit()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)

        esc_surface.blit(pygame.transform.scale(
            esc_menu_background_blur, display_size), (0, 0))
        pygame.draw.rect(esc_surface, (123, 134, 111), (int(
            (display_size[0] / 2) - 250), int((display_size[1] / 2) - 200), 500, 400))
        esc_surface.blit(pygame.transform.scale(
            text_icon, (250, 139)), (int(display_size[0] / 2 - 125), int(display_size[1] / 2 - 175)))

        resume_button.update(esc_surface, mouse_pos, c)
        save_button.update(esc_surface, mouse_pos, c)
        settings_button.update(esc_surface, mouse_pos, c)
        main_menu_button.update(esc_surface, mouse_pos, c)

        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.GetPrimary.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))
        esc_surface.set_alpha(int(255 * anim_x))
        display.blit(esc_surface, (0, 0))
        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        window.fill(KDS.Colors.GetPrimary.Black)
        display.fill(KDS.Colors.GetPrimary.Black)
        c = False
        clock.tick(60)

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, DebugMode, clearLag
    c = False
    settings_running = True

    def return_def():
        global settings_running
        settings_running = False

    def reset_settings():
        return_def()
        os.remove(os.path.join(PersistentPaths.AppDataPath, "settings.cfg"))
        importlib.reload(KDS.ConfigManager)
    
    def reset_data():
        KDS_Quit(True, True)
    
    return_button = KDS.UI.New.Button(pygame.Rect(465, 700, 270, 60), return_def, button_font1.render(
        "Return", True, KDS.Colors.GetPrimary.White))
    music_volume_slider = KDS.UI.New.Slider(
        "MusicVolume", pygame.Rect(450, 135, 340, 20), (20, 30), 1)
    effect_volume_slider = KDS.UI.New.Slider(
        "SoundEffectVolume", pygame.Rect(450, 185, 340, 20), (20, 30), 1)
    clearLag_switch = KDS.UI.New.Switch("ClearLag", pygame.Rect(450, 240, 100, 30), (30, 50))
    reset_settings_button = KDS.UI.New.Button(pygame.Rect(465, 340, 220, 40), reset_settings, button_font.render("Reset Settings", True, KDS.Colors.GetPrimary.White))
    reset_data_button = KDS.UI.New.Button(pygame.Rect(465, 390, 220, 40), reset_data, button_font.render("Reset Data", True, KDS.Colors.GetPrimary.White))
    music_volume_text = button_font.render(
        "Music Volume", True, KDS.Colors.GetPrimary.White)
    effect_volume_text = button_font.render(
        "Sound Effect Volume", True, KDS.Colors.GetPrimary.White)
    clear_lag_text = button_font.render(
        "Clear Lag", True, KDS.Colors.GetPrimary.White)

    while settings_running:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    Fullscreen.Set()
                elif event.key == K_F4:
                    if pygame.key.get_pressed(K_LALT):
                        KDS_Quit()
                elif event.key == K_ESCAPE:
                    settings_running = False
                elif event.key == K_F3:
                    DebugMode = not DebugMode
            elif event.type == pygame.QUIT:
                KDS_Quit()

            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)

        display.blit(settings_background, (0, 0))

        display.blit(pygame.transform.flip(
            menu_trashcan_animation.update(), False, False), (279, 515))

        display.blit(music_volume_text, (50, 135))
        display.blit(effect_volume_text, (50, 185))
        display.blit(clear_lag_text, (50, 240))
        set_music_volume = music_volume_slider.update(display, mouse_pos)
        set_effect_volume = effect_volume_slider.update(display, mouse_pos)

        if set_music_volume != Audio.MusicVolume:
            MusicVolume = set_music_volume
            Audio.MusicMixer.set_volume(MusicVolume)
        elif set_effect_volume != Audio.EffectVolume:
            Audio.setVolume(set_effect_volume)

        return_button.update(display, mouse_pos, c)
        reset_settings_button.update(display, mouse_pos, c)
        reset_data_button.update(display, mouse_pos, c)
        clearLag = clearLag_switch.update(display, mouse_pos, c)

        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.GetPrimary.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))

        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        window.fill((0, 0, 0))
        c = False
        clock.tick(60)

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

    Audio.MusicMixer.load("Assets/Audio/Music/lobbymusic.mp3")
    Audio.MusicMixer.play(-1)
    Audio.MusicMixer.set_volume(Audio.MusicVolume)

    def settings_function():
        settings_menu()

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
            if current_map_int > max_map:
                current_map_int = max_map
            current_map = f"{current_map_int:02d}"
            KDS.ConfigManager.SetSetting("Settings", "CurrentMap", current_map)

    def menu_mode_selector(mode):
        global MenuMode
        MenuMode = mode

    #region Main Menu
    main_menu_play_button = KDS.UI.New.Button(pygame.Rect(
        450, 180, 300, 60), menu_mode_selector, button_font1.render("PLAY", True, KDS.Colors.GetPrimary.White))
    main_menu_settings_button = KDS.UI.New.Button(pygame.Rect(
        450, 250, 300, 60), settings_function, button_font1.render("SETTINGS", True, KDS.Colors.GetPrimary.White))
    main_menu_quit_button = KDS.UI.New.Button(pygame.Rect(
        450, 320, 300, 60), KDS_Quit, button_font1.render("QUIT", True, KDS.Colors.GetPrimary.White))
    #endregion
    #region Mode Selection Menu
    mode_selection_modes = []
    mode_selection_modes.append(KDS.Gamemode.Modes.Story)
    mode_selection_modes.append(KDS.Gamemode.Modes.Campaign)
    mode_selection_buttons = []
    story_mode_button = pygame.Rect(
        0, 0, display_size[0], int(display_size[1] / 2))
    campaign_mode_button = pygame.Rect(
        0, int(display_size[1] / 2), display_size[0], int(display_size[1] / 2))
    mode_selection_buttons.append(story_mode_button)
    mode_selection_buttons.append(campaign_mode_button)
    #endregion
    #region Story Menu
    story_save_button_0_rect = pygame.Rect(14, 14, 378, 500)
    story_save_button_1_rect = pygame.Rect(410, 14, 378, 500)
    story_save_button_2_rect = pygame.Rect(806, 14, 378, 500)
    story_save_button_0 = KDS.UI.New.Button(story_save_button_0_rect, play_function)
    story_save_button_1 = KDS.UI.New.Button(story_save_button_1_rect, play_function)
    story_save_button_2 = KDS.UI.New.Button(story_save_button_2_rect, play_function)
    #endregion 
    #region Campaign Menu
    campaign_right_button_rect = pygame.Rect(1084, 200, 66, 66)
    campaign_left_button_rect = pygame.Rect(50, 200, 66, 66)
    campaign_play_button_rect = pygame.Rect(int(display_size[0] / 2) - 150, display_size[1] - 300, 300, 100)
    campaign_return_button_rect = pygame.Rect(int(display_size[0] / 2) - 150, display_size[1] - 150, 300, 100)
    campaign_play_text = button_font1.render("START", True, (KDS.Colors.Get.EmeraldGreen))
    campaign_return_text = button_font1.render("RETURN", True, (KDS.Colors.Get.AviatorRed))
    campaign_play_button = KDS.UI.New.Button(campaign_play_button_rect, play_function, campaign_play_text)
    campaign_return_button = KDS.UI.New.Button(campaign_return_button_rect, menu_mode_selector, campaign_return_text)
    campaign_left_button = KDS.UI.New.Button(campaign_left_button_rect, level_pick.left)
    campaign_right_button = KDS.UI.New.Button(campaign_right_button_rect, level_pick.right)
    #endregion
    while main_menu_running:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    Fullscreen.Set()
                elif event.key == K_F4:
                    if pygame.key.get_pressed(K_LALT):
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
            elif event.type == pygame.VIDEORESIZE:
                ResizeWindow(event.size)

        if MenuMode == Mode.MainMenu:

            display.blit(main_menu_background, (0, 0))
            display.blit(pygame.transform.flip(
                menu_gasburner_animation.update(), False, False), (625, 445))
            display.blit(pygame.transform.flip(
                menu_toilet_animation.update(), False, False), (823, 507))
            display.blit(pygame.transform.flip(
                menu_trashcan_animation.update(), False, False), (283, 585))

            main_menu_play_button.update(display, mouse_pos, c, Mode.ModeSelectionMenu)
            main_menu_settings_button.update(display, mouse_pos, c)
            main_menu_quit_button.update(display, mouse_pos, c)

        elif MenuMode == Mode.ModeSelectionMenu:

            display.blit(gamemode_bc_1_1, (0, 0))
            display.blit(gamemode_bc_2_1, (0, int(display_size[1] / 2)))
            for y in range(len(mode_selection_buttons)):
                if mode_selection_buttons[y].collidepoint(mouse_pos):
                    if y == 0:
                        display.blit(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(gamemode_bc_1_alpha.update(
                            False) * 255.0)), (story_mode_button.x, story_mode_button.y))
                    elif y == 1:
                        display.blit(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(gamemode_bc_2_alpha.update(
                            False) * 255.0)), (campaign_mode_button.x, campaign_mode_button.y))
                    if c:
                        if mode_selection_modes[y] == KDS.Gamemode.Modes.Story:
                            MenuMode = Mode.StoryMenu
                        elif mode_selection_modes[y] == KDS.Gamemode.Modes.Campaign:
                            MenuMode = Mode.CampaignMenu
                            c = False
                        else:
                            KDS.Logging.AutoError("Invalid mode_selection_mode! Value: " + str(
                                mode_selection_modes[y]), currentframe())
                else:
                    if y == 0:
                        display.blit(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(gamemode_bc_1_alpha.update(
                            True) * 255.0)), (story_mode_button.x, story_mode_button.y))
                    elif y == 1:
                        display.blit(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(gamemode_bc_2_alpha.update(
                            True) * 255.0)), (campaign_mode_button.x, campaign_mode_button.y))

        elif MenuMode == Mode.StoryMenu:
            pygame.draw.rect(
                display, KDS.Colors.GetPrimary.DarkGray, story_save_button_0_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.GetPrimary.DarkGray, story_save_button_1_rect, 10)
            pygame.draw.rect(
                display, KDS.Colors.GetPrimary.DarkGray, story_save_button_2_rect, 10)
            story_save_button_0.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)
            story_save_button_1.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)
            story_save_button_2.update(
                display, mouse_pos, c, KDS.Gamemode.Modes.Story, True)

        elif MenuMode == Mode.CampaignMenu:
            pygame.draw.rect(display, (192, 192, 192), (50, 200, int(display_size[0] - 100), 66))

            campaign_play_button.update(display, mouse_pos, c, KDS.Gamemode.Modes.Campaign, True)
            campaign_return_button.update(display, mouse_pos, c, Mode.MainMenu)
            campaign_left_button.update(display, mouse_pos, c)
            campaign_right_button.update(display, mouse_pos, c)

            display.blit(pygame.transform.flip(arrow_button, True, False), (58, 208))
            display.blit(arrow_button, (1092, 208))
            current_map_int = int(current_map)

            if current_map_int < len(map_names):
                map_name = map_names[current_map_int]
            else:
                map_name = map_names[0]
            level_text = button_font1.render(f"{current_map} - {map_name}", True, (0, 0, 0))
            display.blit(level_text, (125, 209))

        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.GetPrimary.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))

        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        display.fill(KDS.Colors.GetPrimary.Black)
        pygame.display.update()
        window.fill(KDS.Colors.GetPrimary.Black)
        c = False
        clock.tick(60)

def level_finished_menu():
    print("Level finishing not added yet...")
#endregion
#region Check Terms
agr(tcagr)
tcagr = KDS.Convert.ToBool(KDS.ConfigManager.LoadSetting(
    "Data", "TermsAccepted", str(False)))
if tcagr != False:
    main_menu()
#endregion
#region Main Running
while main_running:
#region Events
    KDS.Keys.Update()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_d:
                KDS.Keys.SetPressed(KDS.Keys.moveRight, True)
            elif event.key == K_a:
                KDS.Keys.SetPressed(KDS.Keys.moveLeft, True)
            elif event.key == K_w:
                KDS.Keys.SetPressed(KDS.Keys.moveUp, True)
            elif event.key == K_s:
                KDS.Keys.SetPressed(KDS.Keys.moveDown, True)
            elif event.key == K_SPACE:
                KDS.Keys.SetPressed(KDS.Keys.moveUp, True)
            elif event.key == K_LCTRL:
                KDS.Keys.SetPressed(KDS.Keys.moveDown, True)
            elif event.key == K_LSHIFT:
                if not KDS.Keys.GetPressed(KDS.Keys.moveDown):
                    KDS.Keys.SetPressed(KDS.Keys.moveRun, True)
            elif event.key == K_e:
                KDS.Keys.SetPressed(KDS.Keys.functionKey, True)
            elif event.key == K_ESCAPE:
                esc_menu = True
            elif event.key in KDS.Keys.inventoryKeys:
                player_inventory.pickSlot(KDS.Keys.inventoryKeys.index(event.key))
            elif event.key == K_q:
                if player_inventory.getHandItem() != "none":
                    serialNumber = player_inventory.dropItem()
                    tempItem = Item((player_rect.x, player_rect.y), serialNumber=serialNumber)
                    counter = 0
                    while True:
                        tempItem.rect.y += tempItem.rect.height
                        for collision in collision_test(tempItem.rect, tiles):
                            tempItem.rect.bottom = collision.top
                            counter = 250
                        counter += 1
                        if counter > 250:
                            break
                        
                    items = numpy.append(items, tempItem)
            elif event.key == K_f:
                if playerStamina == 100:
                    playerStamina = -1000
                    farting = True
                    Audio.playSound(fart)
                    KDS.Missions.SetProgress("tutorial", "fart", 1.0)
            elif event.key == K_t:
                console()
            elif event.key == K_F3:
                DebugMode = not DebugMode
            elif event.key == K_F4:
                if pygame.key.get_pressed(K_LALT):
                    KDS_Quit()
                else:
                    player_health = 0
            elif event.key == K_F11:
                Fullscreen.Set()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                KDS.Keys.SetPressed(KDS.Keys.mainKey, True)
                rk62_sound_cooldown = 11
                weapon_fire = True
        elif event.type == KEYUP:
            if event.key == K_d:
                KDS.Keys.SetPressed(KDS.Keys.moveRight, False)
            elif event.key == K_a:
                KDS.Keys.SetPressed(KDS.Keys.moveLeft, False)
            elif event.key == K_w:
                KDS.Keys.SetPressed(KDS.Keys.moveUp, False)
            elif event.key == K_s:
                KDS.Keys.SetPressed(KDS.Keys.moveDown, False)
            elif event.key == K_SPACE:
                KDS.Keys.SetPressed(KDS.Keys.moveUp, False)
            elif event.key == K_LCTRL:
                KDS.Keys.SetPressed(KDS.Keys.moveDown, False)
            elif event.key == K_LSHIFT:
                KDS.Keys.SetPressed(KDS.Keys.moveRun, False)
            elif event.key == K_e:
                KDS.Keys.SetPressed(KDS.Keys.functionKey, False)
            elif event.key == K_c:
                if player_hand_item == "gasburner":
                    gasburnerBurning = not gasburnerBurning
                    gasburner_fire.stop()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                KDS.Keys.SetPressed(KDS.Keys.mainKey, False)
            elif event.button == 4:
                player_inventory.moveLeft()
            elif event.button == 5:
                player_inventory.moveRight()
        elif event.type == pygame.QUIT:
            KDS_Quit()
        elif event.type == pygame.VIDEORESIZE:
            ResizeWindow(event.size)
#endregion
#region Data
    def inventoryDoubleOffsetCounter():
        global inventoryDoubleOffset
        inventoryDoubleOffset = 0
        for i in range(0, inventory_slot - 1):
            if inventoryDoubles[i] == True:
                inventoryDoubleOffset += 1
        return inventoryDoubleOffset

    window.fill((20, 25, 20))
    screen.fill((20, 25, 20))

    true_scroll[0] += (player_rect.x - true_scroll[0] -
                       (screen_size[0] / 2)) / 12
    true_scroll[1] += (player_rect.y - true_scroll[1] - 220) / 12
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    if farting:
        shakeScreen()
    player_hand_item = "none"
    mouse_pos = (int((pygame.mouse.get_pos()[0] - Fullscreen.offset[0]) / Fullscreen.scaling), int(
        (pygame.mouse.get_pos()[1] - Fullscreen.offset[1]) / Fullscreen.scaling))
#endregion
#region Player Death
    if player_health < 1 and not animation_has_played:
        player_death_event = True
        Audio.MusicMixer.stop()
        pygame.mixer.Sound.play(player_death_sound)
        player_death_sound.set_volume(0.5)
        animation_has_played = True
    elif player_health < 1:
        death_wait += 1
        if death_wait > 240:
            play_function(KDS.Gamemode.gamemode, False)
#endregion
#region Rendering

    ###### TÄNNE UUSI ASIOIDEN KÄSITTELY ######
    items, inventory = Item.checkCollisions(
        items, player_rect, screen, scroll, KDS.Keys.GetPressed(KDS.Keys.functionKey), player_inventory)
    Tile.renderUpdate(tiles, screen, scroll, (player_rect.x, player_rect.y))
    Item.render(items, screen, scroll, (player_rect.x, player_rect.y))
    player_inventory.useItem(screen, KDS.Keys.GetPressed(KDS.Keys.mainKey), weapon_fire)
    player_inventory.render(screen)

    for Projectile in Projectiles:
        v = Projectile.update(screen, scroll)
        
        if v == "wall" or v == "air":
            Projectiles.remove(Projectile)
    
    for unit in Explosions:
        finished = unit.update(screen, scroll)
        if finished:
            Explosions.remove(unit)

    ###########################################
    ###########################################
    ###########################################
#endregion
#region PlayerMovement
    fall_speed = 0.4

    player_movement = [0, 0]
    onLadder = False
    for ladder in WorldData.Legacy.ladders:
        if player_rect.colliderect(ladder):
            onLadder = True
            vertical_momentum = 0
            air_timer = 0
            if KDS.Keys.GetPressed(KDS.Keys.moveUp):
                player_movement[1] = -1
            elif KDS.Keys.GetPressed(KDS.Keys.moveDown):
                player_movement[1] = 1
            else:
                player_movement[1] = 0

    if KDS.Keys.GetPressed(KDS.Keys.moveUp) and not KDS.Keys.GetPressed(KDS.Keys.moveDown) and air_timer < 6 and moveUp_released and not onLadder:
        moveUp_released = False
        vertical_momentum = -10
    elif vertical_momentum > 0:
        fall_speed *= fall_multiplier
    elif not KDS.Keys.GetPressed(KDS.Keys.moveUp):
        moveUp_released = True
        fall_speed *= fall_multiplier

    if player_health > 0:
        if not KDS.Keys.GetPressed(KDS.Keys.moveRun) and playerStamina < 100.0:
            playerStamina += 0.25
        elif KDS.Keys.GetPressed(KDS.Keys.moveRun) and playerStamina > 0:
            playerStamina -= 0.75
        elif KDS.Keys.GetPressed(KDS.Keys.moveRun) and playerStamina <= 0:
            KDS.Keys.SetPressed(KDS.Keys.moveRun, False)

    koponen_recog_rec.center = koponen_rect.center

    if KDS.Keys.GetPressed(KDS.Keys.moveRight):
        if not KDS.Keys.GetPressed(KDS.Keys.moveDown):
            player_movement[0] += 4
        else:
            player_movement[0] += 2
        KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.Movement)
        if KDS.Keys.GetPressed(KDS.Keys.moveRun) and playerStamina > 0:
            player_movement[0] += 4
            KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.Movement)

    if KDS.Keys.GetPressed(KDS.Keys.moveLeft):
        if not KDS.Keys.GetPressed(KDS.Keys.moveDown):
            player_movement[0] -= 4
        else:
            player_movement[0] -= 2
        KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.Movement)
        if KDS.Keys.GetPressed(KDS.Keys.moveRun) and playerStamina > 0:
            player_movement[0] -= 4
            KDS.Missions.TriggerListener(KDS.Missions.ListenerTypes.Movement)
    player_movement[1] += vertical_momentum
    vertical_momentum += fall_speed
    if vertical_momentum > 8:
        vertical_momentum = 8

    if check_crouch == True:
        crouch_collisions = move_entity(pygame.Rect(
            player_rect.x, player_rect.y - crouch_size[1], player_rect.width, player_rect.height), (0, 0), tiles, False, True)[1]
    else:
        crouch_collisions = collision_types = {
            'top': False, 'bottom': False, 'right': False, 'left': False}

    if KDS.Keys.GetPressed(KDS.Keys.moveDown) and not onLadder and player_rect.height != crouch_size[1] and death_wait < 1:
        player_rect = pygame.Rect(player_rect.x, player_rect.y + (
            stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
        check_crouch = True
    elif (not KDS.Keys.GetPressed(KDS.Keys.moveDown) or onLadder or death_wait > 0) and player_rect.height != stand_size[1] and crouch_collisions['bottom'] == False:
        player_rect = pygame.Rect(player_rect.x, player_rect.y +
                                  (crouch_size[1] - stand_size[1]), stand_size[0], stand_size[1])
        check_crouch = False
    elif not KDS.Keys.GetPressed(KDS.Keys.moveDown) and crouch_collisions['bottom'] == True and player_rect.height != crouch_size[1] and death_wait < 1:
        player_rect = pygame.Rect(player_rect.x, player_rect.y + (
            stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
        check_crouch = True

    #toilet_collisions(player_rect, gasburnerBurning)

    if player_health > 0:
        player_rect, collisions = move_entity(
            player_rect, player_movement, tiles)

    else:
        player_rect, collisions = move_entity(player_rect, [0, 8], tiles)
#endregion
#region AI
    koponen_rect, k_collisions = move_entity(
        koponen_rect, koponen_movement, tiles)

    wa = zombie_walk_animation.update()
    sa = sergeant_walk_animation.update()

    for sergeant in WorldData.Legacy.sergeants:
        if DebugMode:
            pygame.draw.rect(screen, (KDS.Colors.GetPrimary.Red), (sergeant.rect.x -
                                                                   scroll[0], sergeant.rect.y-scroll[1], sergeant.rect.width, sergeant.rect.height))
        if sergeant.health > 0:
            if sergeant.hitscanner_cooldown > 100:
                hitscan = sergeant.hit_scan(
                    player_rect, player_health, WorldData.Legacy.tile_rects)
                sergeant.hitscanner_cooldown = 0
                if hitscan:
                    sergeant.shoot = True

            else:
                hitscan = False
            if not sergeant.shoot:
                sergeant.rect, sergeant.hits = move_entity(
                    sergeant.rect, sergeant.movement, WorldData.Legacy.tile_rects)

                if sergeant.movement[0] > 0:
                    sergeant.direction = True
                elif sergeant.movement[0] < 0:
                    sergeant.direction = False

                screen.blit(pygame.transform.flip(sa, sergeant.direction, False),
                            (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))

                if sergeant.hits["right"] or sergeant.hits["left"]:
                    sergeant.movement[0] = -sergeant.movement[0]

            else:
                u, i = sergeant_shoot_animation.update()

                screen.blit(pygame.transform.flip(u, sergeant.direction, False),
                            (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))

                if sergeant_shoot_animation.tick > 30 and not sergeant.xvar:
                    sergeant.xvar = True
                    Audio.playSound(shotgun_shot)
                    if sergeant.hit_scan(player_rect, player_health, WorldData.Legacy.tile_rects):
                        player_health = damage(player_health, 20, 50)
                if i:
                    sergeant_shoot_animation.reset()
                    sergeant.shoot = False
                    sergeant.xvar = False

        elif sergeant.playDeathAnimation:
            d, s = sergeant_death_animation.update()
            if not s:
                screen.blit(pygame.transform.flip(d, sergeant.direction, False),
                            (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))
            if s:
                sergeant.playDeathAnimation = False
                sergeant_death_animation.reset()
                monstersLeft -= 1
        else:
            screen.blit(pygame.transform.flip(sergeant_corpse, sergeant.direction,
                                              False), (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1] + 10))
            if not sergeant.loot_dropped:
                sergeant.loot_dropped = True
                if round(random.uniform(0, 3)) == 0:
                    WorldData.Legacy.item_rects.append(pygame.Rect(sergeant.rect.x, int(
                        sergeant.rect.y + (sergeant.rect.height / 2) - 2), sergeant.rect.width, int(sergeant.rect.height / 2)))
                    WorldData.Legacy.item_ids.append("shotgun_shells")

    for zombie1 in WorldData.Legacy.zombies:
        if DebugMode:
            pygame.draw.rect(screen, (KDS.Colors.GetPrimary.Red), (zombie1.rect.x -
                                                                   scroll[0], zombie1.rect.y-scroll[1], zombie1.rect.width, zombie1.rect.height))
        if zombie1.health > 0:
            search = zombie1.search(player_rect)
            if not search:
                zombie1.rect, zombie1.hits = move_entity(
                    zombie1.rect, zombie1.movement, WorldData.Legacy.tile_rects)
                if zombie1.movement[0] != 0:
                    zombie1.walking = True
                    if zombie1.movement[0] > 0:
                        zombie1.direction = False
                    elif zombie1.movement[0] < 0:
                        zombie1.direction = True
                else:
                    zombie1.walking = False

                screen.blit(pygame.transform.flip(wa, zombie1.direction, False),
                            (zombie1.rect.x - scroll[0], zombie1.rect.y - scroll[1]))

                if zombie1.hits["left"]:
                    zombie1.movement[0] = -zombie1.movement[0]
                elif zombie1.hits["right"]:
                    zombie1.movement[0] = -zombie1.movement[0]
            else:
                zombie1.rect, zombie1.hits = move_entity(
                    zombie1.rect, [0, zombie1.movement[1]], WorldData.Legacy.tile_rects)
                attack_counter += 1
                if attack_counter > 40:
                    attack_counter = 0
                    player_health -= int(random.uniform(1, 11))
                if player_rect.centerx > zombie1.rect.centerx:
                    zombie1.direction = False
                else:
                    zombie1.direction = True
                screen.blit(pygame.transform.flip(zombie_attack_animation.update(
                ), zombie1.direction, False), (zombie1.rect.x - scroll[0], zombie1.rect.y - scroll[1]))

        elif zombie1.playDeathAnimation:
            d, s = zombie_death_animation.update()
            if not s:
                screen.blit(pygame.transform.flip(d, zombie1.direction, False),
                            (zombie1.rect.x - scroll[0], zombie1.rect.y - scroll[1]))
            if s:
                zombie1.playDeathAnimation = False
                zombie_death_animation.reset()
                monstersLeft -= 1
        else:
            screen.blit(pygame.transform.flip(zombie_corpse, zombie1.direction,
                                              False), (zombie1.rect.x - scroll[0], zombie1.rect.y - scroll[1] + 14))

    # Zombien käsittely loppuu tähän

    # //////////////////////////////////////////////////////////////
    #*****    New enemies handling & enemies thread handling ******#
    arch_run = archvile_run_animation.update()
    for archvile in WorldData.Legacy.archviles:
        if DebugMode:
            pygame.draw.rect(screen, (KDS.Colors.GetPrimary.Red), (archvile.rect.x -
                                                                   scroll[0], archvile.rect.y-scroll[1], archvile.rect.width, archvile.rect.height))
        archvile.update(arch_run)

    with concurrent.futures.ThreadPoolExecutor() as e:
        I_thread_results = [e.submit(imp._move) for imp in imps]
        I_updatethread_results = [e.submit(
            imp.update, player_rect, screen, 20, scroll, DebugMode) for imp in imps]

    for bulldog in WorldData.Legacy.bulldogs:
        bulldog.startUpdateThread(player_rect, WorldData.Legacy.tile_rects)

    for bulldog in WorldData.Legacy.bulldogs:
        if DebugMode:
            pygame.draw.rect(screen, (KDS.Colors.GetPrimary.Red), (bulldog.rect.x -
                                                                   scroll[0], bulldog.rect.y-scroll[1], bulldog.rect.width, bulldog.rect.height))
        bd_attr = bulldog.getAttributes()
        screen.blit(pygame.transform.flip(
            bd_attr[1], bd_attr[2], False), (bd_attr[0].x - scroll[0], bd_attr[0].y - scroll[1]))
        player_health -= bd_attr[3]

    if k_collisions["left"]:
        koponen_movingx = -koponen_movingx
    elif k_collisions["right"]:
        koponen_movingx = -koponen_movingx

#endregion
#region UI
    score = score_font.render(
        ("SCORE: " + str(player_score)), True, KDS.Colors.GetPrimary.White)

    if player_health < 0:
        player_health = 0

    health = score_font.render(
        "HEALTH: " + str(player_health), True, KDS.Colors.GetPrimary.White)
    stamina = score_font.render(
        "STAMINA: " + str(round(int(playerStamina))), True, KDS.Colors.GetPrimary.White)
#endregion
#region Pelaajan elämätilanteen käsittely
    if player_health < last_player_health and player_health != 0:
        hurted = True
    else:
        hurted = False

    last_player_health = player_health

    if hurted:
        Audio.playSound(hurt_sound)
#endregion
#region More Collisions
    if collisions['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
    else:
        air_timer += 1
    if collisions['top'] == True:
        vertical_momentum = 0
#endregion
#region Player Data
    if player_health:
        if player_movement[0] > 0:
            direction = False
            running = True
        if player_movement[0] < 0:
            direction = True
            running = True
        if player_movement[0] == 0:
            running = False

    animation = []
    if player_health > 0:
        if running:
            if player_rect.height == stand_size[1]:
                animation = run_animation.copy()
            else:
                animation = short_run_animation.copy()
            animation_duration = 7
            if KDS.Keys.GetPressed(KDS.Keys.moveRun):
                animation_duration = 3
        else:
            if player_rect.height == stand_size[1]:
                animation = stand_animation.copy()
            else:
                animation = short_stand_animation.copy()
            animation_duration = 10
    else:
        if player_death_event:
            animation = death_animation.copy()
            animation_duration = 10
#endregion
#region Koponen Movement
    if koponen_movement[0] != 0:
        koponen_animation = koponen_run.copy()
    else:
        koponen_animation = koponen_stand.copy()
#endregion
#region Items
    if animation_counter > animation_duration:
        animation_counter = 0
        animation_image += 1
        if animation_image > (len(animation)-1):
            animation_image = 0
            if player_death_event:
                player_death_event = False
                animation_has_played = True

    if koponen_animation_stats[2] > koponen_animation_stats[1]:
        koponen_animation_stats[0] += 1
        koponen_animation_stats[2] = 0
        if koponen_animation_stats[0] > 1:
            koponen_animation_stats[0] = 0

    if farting:
        fart_counter += 1
        if fart_counter > 250:
            farting = False
            fart_counter = 0

            damage_rect = pygame.Rect(0, 0, 800, 600)

            damage_rect.centerx = player_rect.centerx
            damage_rect.centery = player_rect.centery

            for archvile in WorldData.Legacy.archviles:
                if damage_rect.colliderect(archvile.rect):
                    archvile.health -= 600
            for zombie1 in WorldData.Legacy.zombies:
                if damage_rect.colliderect(zombie1.rect):
                    zombie1.health -= 600
            for sergeant in WorldData.Legacy.sergeants:
                if damage_rect.colliderect(sergeant.rect):
                    sergeant.health -= 600
            for imp in imps:
                if damage_rect.colliderect(imp.rect):
                    imp.dmg(600)
            del damage_rect

    if player_keys["red"]:
        screen.blit(red_key, (10, 20))
    if player_keys["green"]:
        screen.blit(green_key, (24, 20))
    if player_keys["blue"]:
        screen.blit(blue_key, (38, 20))
#endregion
#region Koponen Tip
    if player_rect.colliderect(koponen_recog_rec):
        screen.blit(
            koponen_talk_tip, (koponen_recog_rec.topleft[0] - scroll[0], koponen_recog_rec.topleft[1] - scroll[1]-10))
        koponen_movement[0] = 0
        if knifeInUse:
            koponen_alive = False
        if KDS.Keys.GetPressed(KDS.Keys.functionKey):
            koponen_talk()
    else:
        koponen_movement[0] = koponen_movingx
    h = 0
#endregion
#region Interactable Objects

    screen.blit(koponen_animation[koponen_animation_stats[0]], (
        koponen_rect.x - scroll[0], koponen_rect.y - scroll[1]))

    if player_health or player_death_event:
        if DebugMode:
            pygame.draw.rect(screen, (KDS.Colors.GetPrimary.Green), (player_rect.x -
                                                                     scroll[0], player_rect.y - scroll[1], player_rect.width, player_rect.height))
        screen.blit(pygame.transform.flip(animation[animation_image], direction, False), (
            int(player_rect.topleft[0] - scroll[0] + ((player_rect.width - animation[animation_image].get_width()) / 2)), int(player_rect.bottomleft[1] - scroll[1] - animation[animation_image].get_height())))
    else:
        screen.blit(pygame.transform.flip(player_corpse, direction, False), (
            player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for archvile in WorldData.Legacy.archviles:
        if archvile.attack_anim:
            screen.blit(flames_animation.update(),
                        (player_rect.x - scroll[0], player_rect.y - scroll[1]-20))

    for iron_bar1 in iron_bars:
        screen.blit(iron_bar, (iron_bar1.x -
                               scroll[0], iron_bar1.y - scroll[1]))

#endregion
#region Debug Mode
    screen.blit(score, (10, 55))
    KDS.Logging.Profiler(DebugMode)
    if DebugMode:
        screen.blit(score_font.render(
            "FPS: " + str(int(round(clock.get_fps()))), True, KDS.Colors.GetPrimary.White), (5, 5))
        screen.blit(score_font.render("Total Monsters: " + str(monstersLeft) +
                                      "/" + str(monsterAmount), True, KDS.Colors.GetPrimary.White), (5, 15))
        screen.blit(score_font.render("Sounds Playing: " + str(len(Audio.getBusyChannels())) +
                                      "/" + str(pygame.mixer.get_num_channels()), True, KDS.Colors.GetPrimary.White), (5, 25))
#endregion
#region UI Rendering
    screen.blit(health, (10, 120))
    screen.blit(stamina, (10, 130))

    missions_background_width = KDS.Missions.GetMaxWidth()
    Mission_Render_Data = KDS.Missions.RenderMission(screen)

    for i in range(KDS.Missions.GetRenderCount()):
        KDS.Missions.RenderTask(screen, i)
#endregion
#region Screen Rendering
    if dark:
        screen.blit(black_tint, (0, 0))
    window.fill(KDS.Colors.GetPrimary.Black)
    window.blit(pygame.transform.scale(screen, Fullscreen.size),
                (Fullscreen.offset[0], Fullscreen.offset[1]))
    pygame.display.update()
#endregion
#region Data Update
    animation_counter += 1
    weapon_fire = False
    koponen_animation_stats[2] += 1
    for sergeant in WorldData.Legacy.sergeants:
        sergeant.hitscanner_cooldown += 1
    if KDS.Missions.GetFinished() == True:
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
            level_finished_menu()

    #print("Player position: " + str(player_rect.topleft) + " Angle: " + str(KDS.Math.getAngle((player_rect.x,player_rect.y),imps[0].rect.topleft)))

#endregion
#region Conditional Events
    if player_rect.y > len(tiles)*34+400:
        player_health = 0
    if esc_menu:
        Audio.MusicMixer.pause()
        Audio.pauseAllSounds()
        window.fill(KDS.Colors.GetPrimary.Black)
        window.blit(pygame.transform.scale(screen, Fullscreen.size),
                    (Fullscreen.offset[0], Fullscreen.offset[1]))
        esc_menu_background = screen.copy()
        pygame.mouse.set_visible(True)
        esc_menu_f()
        pygame.mouse.set_visible(False)
        Audio.MusicMixer.unpause()
        Audio.unpauseAllSounds()
    if go_to_main_menu:
        Audio.stopAllSounds()
        Audio.MusicMixer.stop()
        pygame.mouse.set_visible(True)
        main_menu()
#endregion
#region Gathering all threading results
    # Imps
    for x in range(len(imps)):
        if I_thread_results[x].result() != None:
            imps[x].rect, imps[x].movement, imps[x].direction, imps[x].speed = I_thread_results[x].result()
        if I_updatethread_results[x].result() != None:
            imps[x].sleep, imps[x].targetFound, imps[x].movement = I_updatethread_results[x].result()
#endregion
#region Ticks
    tick += 1
    if tick > 60:
        tick = 0
    clock.tick(60)
#endregion
#endregion
#region Application Quitting
pygame.mixer.music.load("Assets/Audio/Music/lobbymusic.mp3")
KDS.System.emptdir(PersistentPaths.CachePath)
KDS.Logging.Quit()
pygame.mixer.quit()
pygame.display.quit()
pygame.quit()
if reset_data:
    shutil.rmtree(PersistentPaths.AppDataPath)
if restart:
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
#endregion