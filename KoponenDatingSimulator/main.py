#region Importing
import KDS.AI
import KDS.Animator
import KDS.Colors
import KDS.ConfigManager
import KDS.Convert
import KDS.Gamemode
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.UI
import KDS.LevelLoader
import pygame
import os
import random
import threading
import math
from pygame.locals import *
#endregion
#region Priority Initialisation
AppDataPath = os.path.join(os.getenv('APPDATA'),
                           "Koponen Development Inc", "Koponen Dating Simulator")
if not os.path.exists(os.path.join(os.getenv('APPDATA'), "Koponen Development Inc")) or not os.path.isdir(os.path.join(os.getenv('APPDATA'), "Koponen Development Inc")):
    os.mkdir(os.path.join(os.getenv('APPDATA'), "Koponen Development Inc"))
if not os.path.exists(AppDataPath) or not os.path.isdir(AppDataPath):
    os.mkdir(AppDataPath)

pygame.init()
KDS.Logging.init()
KDS.ConfigManager.init()

KDS.ConfigManager.SetSetting("Settings", "DisplaySizeX", str(1200))
KDS.ConfigManager.SetSetting("Settings", "DisplaySizeY", str(800))
KDS.ConfigManager.SetSetting("Settings", "ScreenSizeX", str(600))
KDS.ConfigManager.SetSetting("Settings", "ScreenSizeY", str(400))

display_size = (int(KDS.ConfigManager.LoadSetting("Settings", "DisplaySizeX", str(
    1200))), int(KDS.ConfigManager.LoadSetting("Settings", "DisplaySizeY", str(800))))
screen_size = (int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeX", str(
    600))), int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeY", str(400))))
window_size = display_size
monitor_info = pygame.display.Info()
monitor_size = (monitor_info.current_w, monitor_info.current_h)

pygame.mouse.set_cursor(*pygame.cursors.arrow)

main_display = pygame.display.set_mode(display_size)
screen = pygame.Surface(screen_size)
#endregion
#region Audio
pygame.mixer.init()
pygame.mixer.set_num_channels(12)
pygame.mixer.set_reserved(0)
pygame.mixer.set_reserved(11)
class Audio:
    MusicMixer = pygame.mixer.music
    MusicChannel1 = pygame.mixer.Channel(0)
    MusicChannel2 = pygame.mixer.Channel(11)
    EffectChannels = [pygame.mixer.Channel(1), pygame.mixer.Channel(2), pygame.mixer.Channel(3),
                      pygame.mixer.Channel(4), pygame.mixer.Channel(5), pygame.mixer.Channel(6),
                      pygame.mixer.Channel(7), pygame.mixer.Channel(8), pygame.mixer.Channel(9),
                      pygame.mixer.Channel(10)]
    @staticmethod
    def playSound(sound: pygame.mixer.Sound):
        global effect_volume
        play_channel = pygame.mixer.find_channel(True)
        play_channel.play(sound)
        play_channel.set_volume(effect_volume)
    @staticmethod
    def stopAllSounds():
        for i in range(len(Audio.EffectChannels)):
            Audio.EffectChannels[i].stop()
#endregion
#region Animations
class plasma_bullet:

    def __init__(self, starting_position, direction, display_to_blit):
        self.done = False
        self.direction = direction
        self.display = display_to_blit
        self.rect = pygame.Rect(
            starting_position[0], starting_position[1], 2, 2)

    def update(self, tile_rects):
        if self.direction:
            self.rect.centerx += 14
        else:
            self.rect.centerx -= 14

        for tile in tile_rects:
            if self.rect.colliderect(tile):
                self.done = True
                Audio.playSound(plasma_hitting)
        for zombie1 in zombies:
            if self.rect.colliderect(zombie1) == True and zombie1.playDeathAnimation == True:
                self.done = True
                zombie1.health -= 10
                Audio.playSound(plasma_hitting)
        for sergeant in sergeants:
            if self.rect.colliderect(sergeant) and sergeant.playDeathAnimation:
                self.done = True
                sergeant.health -= 12
                Audio.playSound(plasma_hitting)

        self.display.blit(
            plasma_ammo, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

        return self.done
class Bullet:


    def __init__(self, _position, _direction, damage):
        self.position = _position
        self.direction = not _direction
        self.move = 0
        self.damage = damage

    def shoot(self, _tile_rects):

        global zombies, screen, sergeants

        if self.direction:
            self.move = 28
        else:
            self.move = -28
        q = True
        counter = 0
        while q:

            self.position[0] += self.move

            for tile in _tile_rects:
                if tile.collidepoint(self.position):
                    q = False
                    return "wall"

            for zombie1 in zombies:
                if zombie1.health > 0:
                    if zombie1.rect.collidepoint(tuple(self.position)):
                        zombie1.health -= self.damage
                        q = False
                        return "enemy"

            for sergeant in sergeants:
                if sergeant.health > 0:
                    if sergeant.rect.collidepoint(tuple(self.position)):
                        sergeant.health -= self.damage
                        q = False
                        return "enemy"
            for archvile in archviles:
                if archvile.health > 0:
                    if archvile.rect.collidepoint(tuple(self.position)):
                        archvile.health -= self.damage
                        q = False
                        return "enemy"

            counter += 1
            if counter > 300:
                q = False
        return "null"

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
        global player_health
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

                for tile in tile_rects:
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
                    self.rect, self.movement, tile_rects)
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
                            (self.rect.x - scroll[0], self.rect.y - scroll[1]+15))

            if p:
                self.playDeathAnimation = False
                monstersLeft -= 1

        else:
            screen.blit(pygame.transform.flip(archvile_corpse, not self.direction,
                                              False), (self.rect.x - scroll[0],
                                                       self.rect.y - scroll[1]+25))
#endregion
#region Fullscreen
class FullscreenGet:
    try:
        size
        offset
        scaling
    except:
        size = None
        offset = None
        scaling = None
    size
    offset
    scaling

def FullscreenSet(reverseFullscreen=False):
    global isFullscreen, main_display, window_size
    if reverseFullscreen:
        isFullscreen = not isFullscreen
    if isFullscreen:
        main_display = pygame.display.set_mode(display_size)
        isFullscreen = False
        window_size = display_size
    else:
        main_display = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        isFullscreen = True
        window_size = monitor_size
    KDS.ConfigManager.SetSetting("Settings", "Fullscreen", str(isFullscreen))
    FullscreenGet.size = (int(window_size[1] * (display_size[0] / display_size[1])), int(window_size[1]))
    FullscreenGet.offset = ((window_size[0] / 2) - (FullscreenGet.size[0] / 2), (window_size[1] / 2) - (FullscreenGet.size[1] / 2))
    FullscreenGet.scaling = FullscreenGet.size[1] / display_size[1]
#endregion
#region Initialisation
black_tint = pygame.Surface(screen_size)
black_tint.fill((0, 0, 0))
black_tint.set_alpha(170)

#region Downloads
pygame.display.set_caption("Koponen Dating Simulator")
game_icon = pygame.image.load("Assets/Textures/Game_Icon.png")
main_menu_background = pygame.image.load(
    "Assets/Textures/UI/Menus/main_menu_bc.png").convert()
settings_background = pygame.image.load("Assets/Textures/UI/Menus/settings_bc.png").convert()
agr_background = pygame.image.load("Assets/Textures/UI/Menus/tcagr_bc.png").convert()
pygame.display.set_icon(game_icon)
clock = pygame.time.Clock()

score_font = pygame.font.Font("gamefont.ttf", 10, bold=0, italic=0)
tip_font = pygame.font.Font("gamefont2.ttf", 10, bold=0, italic=0)
button_font = pygame.font.Font("gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("gamefont2.ttf", 52, bold=0, italic=0)
text_font = pygame.font.Font("courier.ttf", 30, bold=0, italic=0)

player_img = pygame.image.load("Assets/Textures/Player/stand0.png").convert()
player_corpse = pygame.image.load("Assets/Textures/Player/corpse.png").convert()
player_corpse.set_colorkey(KDS.Colors.GetPrimary.White)
player_img.set_colorkey(KDS.Colors.GetPrimary.White)

floor0 = pygame.image.load("Assets/Textures/Building/floor0v2.png").convert()
concrete0 = pygame.image.load("Assets/Textures/Building/concrete0.png").convert()
wall0 = pygame.image.load("Assets/Textures/Building/wall0.png").convert()
table0 = pygame.image.load("Assets/Textures/Building/table0.png").convert()
toilet0 = pygame.image.load("Assets/Textures/Building/toilet0.png").convert()
lamp0 = pygame.image.load("Assets/Textures/Building/lamp0.png").convert()
trashcan = pygame.image.load("Assets/Textures/Building/trashcan.png").convert()
ground1 = pygame.image.load("Assets/Textures/Building/ground0.png").convert()
grass = pygame.image.load("Assets/Textures/Building/grass0.png").convert()
door_closed = pygame.image.load("Assets/Textures/Building/door_closed.png").convert()
red_door_closed = pygame.image.load(
    "Assets/Textures/Building/red_door_closed.png").convert()
green_door_closed = pygame.image.load(
    "Assets/Textures/Building/green_door_closed.png").convert()
blue_door_closed = pygame.image.load(
    "Assets/Textures/Building/blue_door_closed.png").convert()
door_open = pygame.image.load("Assets/Textures/Building/door_open2.png").convert()
bricks = pygame.image.load("Assets/Textures/Building/bricks.png").convert()
tree = pygame.image.load("Assets/Textures/Building/tree.png").convert()
planks = pygame.image.load("Assets/Textures/Building/planks.png").convert()
jukebox_texture = pygame.image.load("Assets/Textures/Building/jukebox.png").convert()
landmine_texture = pygame.image.load("Assets/Textures/Building/landmine.png").convert()
ladder_texture = pygame.image.load("Assets/Textures/Building/ladder.png").convert()
background_wall = pygame.image.load("Assets/Textures/Building/background_wall.png").convert()
light_bricks = pygame.image.load("Assets/Textures/Building/light_bricks.png").convert()
iron_bar = pygame.image.load("Assets/Textures/Building/iron_bars_texture.png").convert()
soil = pygame.image.load("Assets/Textures/Building/soil.png").convert()
mossy_bricks = pygame.image.load("Assets/Textures/Building/mossy_bricks.png").convert()
stone = pygame.image.load("Assets/Textures/Building/stone.png").convert()
hay = pygame.image.load("Assets/Textures/Building/hay.png").convert()
soil1 = pygame.image.load("Assets/Textures/Building/soil_2.png").convert()
wood = pygame.image.load("Assets/Textures/Building/wood.png").convert()
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
ss_bonuscard = pygame.image.load("Assets/Textures/Items/ss_bonuscard.png").convert()
lappi_sytytyspalat = pygame.image.load(
    "Assets/Textures/Items/lappi_sytytyspalat.png").convert()
plasmarifle = pygame.image.load("Assets/Textures/Items/plasmarifle.png").convert()
plasma_ammo = pygame.image.load("Assets/Textures/Items/plasma_ammo.png").convert()
cell = pygame.image.load("Assets/Textures/Items/cell.png")
zombie_corpse = pygame.image.load(
    "Assets/Textures/Animations/z_death_4.png").convert()
pistol_texture = pygame.image.load("Assets/Textures/Items/pistol.png").convert()
pistol_f_texture = pygame.image.load(
    "Assets/Textures/Items/pistol_firing.png").convert()
soulsphere = pygame.image.load("Assets/Textures/Items/soulsphere.png").convert()
turboneedle = pygame.image.load("Assets/Textures/Items/turboneedle.png").convert()
pistol_mag = pygame.image.load("Assets/Textures/Items/pistol_mag.png").convert()
rk62_texture = pygame.image.load("Assets/Textures/Items/rk62.png").convert()
rk62_f_texture = pygame.image.load("Assets/Textures/Items/rk62_firing.png").convert()
rk62_mag = pygame.image.load("Assets/Textures/Items/rk_mag.png").convert()
sergeant_corpse = pygame.image.load(
    "Assets/Textures/Animations/seargeant_dying_4.png").convert()
sergeant_aiming = pygame.image.load(
    "Assets/Textures/Animations/seargeant_shooting_0.png").convert()
sergeant_firing = pygame.image.load(
    "Assets/Textures/Animations/seargeant_shooting_1.png").convert()
medkit = pygame.image.load("Assets/Textures/Items/medkit.png").convert()
shotgun = pygame.image.load("Assets/Textures/Items/shotgun.png").convert()
shotgun_f = pygame.image.load("Assets/Textures/Items/shotgun_firing.png").convert()
shotgun_shells_t = pygame.image.load(
    "Assets/Textures/Items/shotgun_shells.png").convert()
archvile_corpse = pygame.image.load(
    "Assets/Textures/Animations/archvile_death_6.png").convert()
iphone_texture = pygame.image.load("Assets/Textures/Items/iPuhelin.png").convert()

gamemode_bc_1_1 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_1.png")).convert()
gamemode_bc_2_1 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_1.png")).convert()
gamemode_bc_2_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_2.png")).convert()
gamemode_bc_1_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_2.png")).convert()
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
iphone_texture.set_colorkey(KDS.Colors.GetPrimary.White)
soulsphere.set_colorkey(KDS.Colors.GetPrimary.White)
turboneedle.set_colorkey(KDS.Colors.GetPrimary.White)

Items_list = ["iPuhelin", "coffeemug"]
Items = {"iPuhelin": iphone_texture, "coffeemug": coffeemug}

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
lappi_sytytyspalat_sound = pygame.mixer.Sound("Assets/Audio/Effects/sytytyspalat.wav")
landmine_explosion = pygame.mixer.Sound("Assets/Audio/Effects/landmine.wav")
hurt_sound = pygame.mixer.Sound("Assets/Audio/Effects/dsplpain.wav")
plasmarifle_f_sound = pygame.mixer.Sound("Assets/Audio/Effects/dsplasma.wav")
weapon_pickup = pygame.mixer.Sound("Assets/Audio/Effects/weapon_pickup.wav")
item_pickup = pygame.mixer.Sound("Assets/Audio/Effects/dsitemup.wav")
plasma_hitting = pygame.mixer.Sound("Assets/Audio/Effects/dsfirxpl.wav")
pistol_shot = pygame.mixer.Sound("Assets/Audio/Effects/pistolshot.wav")
rk62_shot = pygame.mixer.Sound("Assets/Audio/Effects/rk62_shot.wav")
shotgun_shot = pygame.mixer.Sound("Assets/Audio/Effects/shotgun.wav")
player_shotgun_shot = pygame.mixer.Sound("Assets/Audio/Effects/player_shotgun.wav")
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

gradient_sphere = pygame.image.load("Assets/gradient_sphere.png").convert_alpha()

jukebox_tip = tip_font.render("Use jukebox [E]", True, KDS.Colors.GetPrimary.White)
#endregion

main_running = True
playerMovingRight = False
playerMovingLeft = False
playerSprinting = False
plasmarifle_fire = False
jukeboxMusicPlaying = 0
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

tcagr = KDS.Convert.ToBool(KDS.ConfigManager.LoadSetting(
    "Data", "TermsAccepted", str(False)))

if tcagr == None:
    KDS.Logging.Log(KDS.Logging.LogType.error,
                    "Error parcing terms and conditions bool.", False)
    tcagr = False

music_volume = float(KDS.ConfigManager.LoadSetting("Settings", "Music Volume", str(0.5)))
effect_volume = float(KDS.ConfigManager.LoadSetting("Settings", "Sound Effect Volume", str(0.5)))

isFullscreen = KDS.Convert.ToBool(
    KDS.ConfigManager.LoadSetting("Settings", "Fullscreen", str(False)))

if isFullscreen == None:
    KDS.Logging.Log(KDS.Logging.LogType.error,
                    "Error parcing fullscreen bool.", False)
FullscreenSet(True)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Settings Loaded:\n- Terms Accepted: " +
                str(tcagr) + "\n- Music Volume: " + str(music_volume) + "\n- Sound Effect Volume: " + str(effect_volume) + "\n- Fullscreen: " + str(isFullscreen), False)

selectedSave = 0

gasburner_animation_stats = [0, 4, 0]
knife_animation_stats = [0, 10, 0]
burning_animation_stats = [0, 5, 0]
koponen_animation_stats = [0, 7, 0]
explosion_positions = []
plasmarifle_cooldown = 0
rk62_cooldown = 0
rk62_sound_cooldown = 0
player_hand_item = "none"
player_keys = {"red": False, "green": False, "blue": False}
direction = True
FunctionKey = False
AltPressed = False
F4Pressed = False
esc_menu = False
moveUp = False
moveDown = False
onLadder = False
mouseLeftPressed = False
shotgun_loaded = True
shotgun_cooldown = 0
pistol_cooldown = 0
dark = False

gamemode_bc_1_alpha = KDS.Animator.Lerp(0.0, 1.0, 8, KDS.Animator.OnAnimationEnd.Stop)
gamemode_bc_2_alpha = KDS.Animator.Lerp(0.0, 1.0, 8, KDS.Animator.OnAnimationEnd.Stop)

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

current_map = KDS.ConfigManager.LoadSetting("Settings", "CurrentMap", "02")

with open("Assets/Maps/map_names.txt", "r") as file:
    cntnts = file.read()
    cntnts = cntnts.split('\n')


max_map = int(KDS.ConfigManager.LoadSetting("Settings", "MaxMap", "05"))

map_names = tuple(cntnts)

ammunition_plasma = 50
pistol_bullets = 8
rk_62_ammo = 30
shotgun_shells = 8

inventory = ["none", "none", "none", "none", "none"]
inventoryDoubles = []
inventoryDoubleOffset = 0
for none in inventory:
    inventoryDoubles.append(False)

global player_score
player_score = 0
true_scroll = [0, 0]
inventory_slot = 0
doubleWidthAdd = 0

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

koponen_talk_tip = tip_font.render("Puhu Koposelle [E]", True, KDS.Colors.GetPrimary.White)

task = ""
taskTaivutettu = ""

DebugMode = False

MenuMode = 0
esc_menu_background = pygame.Surface(window_size)
#endregion
#region Save System
def LoadSave():
    global Saving, player_rect, selectedSave, player_name, player_health, last_player_health, playerStamina
    player_rect.x = int(KDS.ConfigManager.LoadSave(
        selectedSave, "PlayerPosition", "X", str(player_rect.x)))
    player_rect.y = int(KDS.ConfigManager.LoadSave(
        selectedSave, "PlayerPosition", "Y", str(player_rect.y)))
    player_health = int(KDS.ConfigManager.LoadSave(
        selectedSave, "PlayerData", "Health", str(player_health)))
    last_player_health = player_health
    player_name = KDS.ConfigManager.LoadSave(
        selectedSave, "PlayerData", "Name", player_name)
    playerStamina = float(KDS.ConfigManager.LoadSave(
        selectedSave, "PlayerData", "Stamina", str(playerStamina)))
    inventory[0] = KDS.ConfigManager.LoadSave(selectedSave, "PlayerData", "Inventory0", inventory[0])
    inventory[1] = KDS.ConfigManager.LoadSave(selectedSave, "PlayerData", "Inventory1", inventory[1])
    inventory[2] = KDS.ConfigManager.LoadSave(selectedSave, "PlayerData", "Inventory2", inventory[2])
    inventory[3] = KDS.ConfigManager.LoadSave(selectedSave, "PlayerData", "Inventory3", inventory[3])
    inventory[4] = KDS.ConfigManager.LoadSave(selectedSave, "PlayerData", "Inventory4", inventory[4])
def SaveData():
    global Saving, player_rect, selectedSave, player_name, player_health, last_player_health
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
        selectedSave, "PlayerData", "Inventory0", inventory[0])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory1", inventory[1])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory2", inventory[2])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory3", inventory[3])
    KDS.ConfigManager.SetSave(
        selectedSave, "PlayerData", "Inventory4", inventory[4])
#endregion
#region Quit Handling
def KDS_Quit():
    global main_running, main_menu_running, tcagr_running, koponenTalking, esc_menu, settings_running, selectedSave, tick
    main_menu_running = False
    main_running = False
    tcagr_running = False
    koponenTalking = False
    esc_menu = False
    settings_running = False
#endregion
#region World Generation
#region Lists
world_gen = list()
item_gen = list()
tile_rects = list()
toilets = list()
burning_toilets = list()
trashcans = list()
burning_trashcans = list()
jukeboxes = list()
landmines = list()
zombies = list()
sergeants = list()
archviles = list()
ladders = list()
bulldogs = list()
item_rects = list()
item_ids = list()
task_items = list()
color_keys = list()
door_rects = list()
doors_open = list()
tile_textures = dict()
tile_textures_loaded = False
#endregion
def WorldGeneration():
    global world_gen, item_gen, tile_rects, toilets, burning_toilets, trashcans, burning_trashcans
    global jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs, item_rects, item_ids
    global task_items, door_rects, doors_open, color_keys, iron_bars, tile_textures, tile_textures_loaded

    buildingBitmap = pygame.image.load(os.path.join("Assets", "Maps", "map" + current_map, "map_buildings.map")).convert()
    decorationBitmap = pygame.image.load(os.path.join("Assets", "Maps", "map" + current_map, "map_decorations.map")).convert()
    enemyBitmap = pygame.image.load(os.path.join("Assets", "Maps", "map" + current_map, "map_enemies.map")).convert()
    itemBitmap = pygame.image.load(os.path.join("Assets", "Maps", "map" + current_map, "map_items.map")).convert()

    convertBuildingRules = list()
    convertBuildingColors = list()
    convertDecorationRules = list()
    convertDecorationColors = list()
    convertEnemyRules = list()
    convertEnemyColors = list()
    convertItemRules = list()
    convertItemColors = list()
    with open(os.path.join("Assets", "Maps", "resources_convert_rules.txt"), 'r') as f:
        raw = f.read()
        raw = raw.replace(" ", "")
        rowSplit = raw.split('\n')

        #Adds air to all convert rules
        array = rowSplit[0].split(',')
        array[2] = array[2].replace("(", "")
        array[4] = array[4].replace(")", "")
        convertBuildingRules.append(array[1])
        convertBuildingColors.append((int(array[2]), int(array[3]), int(array[4])))
        convertDecorationRules.append(array[1])
        convertDecorationColors.append((int(array[2]), int(array[3]), int(array[4])))
        convertEnemyRules.append(array[1])
        convertEnemyColors.append((int(array[2]), int(array[3]), int(array[4])))
        convertItemRules.append(array[1])
        convertItemColors.append((int(array[2]), int(array[3]), int(array[4])))

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
                    convertBuildingColors.append((int(array[2]), int(array[3]), int(array[4])))
                    if not tile_textures_loaded and not "door" in array[0]:
                        try:
                            global_texture1 = globals()[str(array[0])]
                        except KeyError:
                            global_texture1 = None
                        try:
                            global_texture2 = globals()[str(array[0] + "_texture")]
                        except KeyError:
                            global_texture2 = None

                        if isinstance(global_texture1, pygame.Surface):
                            tile_textures[array[1]] = global_texture1.copy()
                        elif isinstance(global_texture2, pygame.Surface):
                            tile_textures[array[1]] = global_texture2.copy()
                        else:
                            KDS.Logging.Log(KDS.Logging.LogType.error, "Texture not found. " + array[0], True)

                elif Type == 1:
                    convertDecorationRules.append(array[1])
                    convertDecorationColors.append((int(array[2]), int(array[3]), int(array[4])))
                elif Type == 2:
                    convertEnemyRules.append(array[1])
                    convertEnemyColors.append((int(array[2]), int(array[3]), int(array[4])))
                elif Type == 3:
                    convertItemRules.append(array[1])
                    convertItemColors.append((int(array[2]), int(array[3]), int(array[4])))

    tile_textures_loaded = True

    building_gen = list()
    decoration_gen = list()
    enemy_gen = list()
    item_gen = list()

    BitmapSize = (buildingBitmap.get_width(), buildingBitmap.get_height())
    for i in range(BitmapSize[1]):
        building_layer = list()
        decoration_layer = list()
        enemy_layer = list()
        item_layer = list()
        for j in range(BitmapSize[0]):
            building_layer.append(convertBuildingRules[convertBuildingColors.index(buildingBitmap.get_at((j, i))[:3])])
            decoration_layer.append(convertDecorationRules[convertDecorationColors.index(decorationBitmap.get_at((j, i))[:3])])
            enemy_layer.append(convertEnemyRules[convertEnemyColors.index(enemyBitmap.get_at((j, i))[:3])])
            item_layer.append(convertItemRules[convertItemColors.index(itemBitmap.get_at((j, i))[:3])])

        building_gen.append(building_layer)
        decoration_gen.append(decoration_layer)
        enemy_gen.append(enemy_layer)
        item_gen.append(item_layer)


    world_gen = (building_gen, decoration_gen, enemy_gen, item_gen)

    #Use the index to get the letter and make the file using the letters

    tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs, iron_bars = load_rects()
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Zombies Initialised: " + str(len(zombies)), False)
    for zombie in zombies:
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        "Initialised Zombie: " + str(zombie), False)

    item_rects, item_ids, task_items = load_item_rects()
    random.shuffle(task_items)

    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Items Initialised: " + str(len(item_ids)), False)
    for i_id in item_ids:
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        "Initialised Item: (ID)" + i_id, False)
    door_rects, doors_open, color_keys = load_doors()
#endregion
#region Pickup Sound
def play_key_pickup():
    pygame.mixer.Sound.play(key_pickup)
#endregion
#region Loading
def load_map(path):
    with open(path, 'r') as f:
        data = f.read()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map
def load_items(path):
    with open(path, 'r') as f:
        data = f.read()
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

def play_map_music(_current_map):
    pygame.mixer.music.load(os.path.join("Assets", "Maps", "map" + _current_map, "music.mid"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(music_volume)
def load_ads():
    ad_files = os.listdir("Assets/Textures/KoponenTalk/ads")

    random.shuffle(ad_files)
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Ad Files Initialised: " + str(len(ad_files)), False)

    ad_images = []

    for ad in ad_files:
        path = str("Assets/Textures/KoponenTalk/ads/" + ad)
        image = pygame.image.load(path).convert()
        image.set_colorkey(KDS.Colors.GetPrimary.Red)
        ad_images.append(image)
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        "Initialised Ad File: " + ad, False)

    return ad_images
ad_images = load_ads()
koponen_talking_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png").convert()
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
    w = [0, 0]
    for i in range(len(world_gen) - 1):
        y = 0
        for layer in world_gen[i]:
            x = 0
            for tile in layer:
                if tile != 'a':
                    if tile == 'f':
                        tile_rects.append(pygame.Rect(x * 34, y * 34, 14, 21))
                    elif tile == 'e':
                        w = list(toilet0.get_size())
                        toilets.append(pygame.Rect(x * 34-2, y * 34, 34, 34))
                        burning_toilets.append(False)
                        tile_rects.append(pygame.Rect(x * 34, y * 34, w[0], w[1]))
                    elif tile == 'g':
                        w = list(trashcan.get_size())
                        trashcans.append(pygame.Rect(x * 34-1, y * 34, w[0]+2, w[1]))
                        burning_trashcans.append(False)
                        tile_rects.append(pygame.Rect(x * 34, y * 34+8, w[0], w[1]))
                    elif tile == 'q':
                        ladders.append(pygame.Rect((x * 34) + 16, (y * 34) - 2, 2, 38))
                    elif tile == 'k':
                        pass
                    elif tile == 'l':
                        pass
                    elif tile == 'm':
                        pass
                    elif tile == 'n':
                        pass
                    elif tile == 's':
                        iron_bars.append(pygame.Rect(x*34, y*34, 1, 1))
                    elif tile == 'A':
                        pass
                    elif tile == 'B':
                        jukeboxes.append(pygame.Rect(x * 34, y * 34 - 26, 42, 60))
                    elif tile == 'C':
                        landmines.append(pygame.Rect(x * 34+6, y * 34+23, 22, 11))
                    elif tile == 'Z':
                        zombies.append(KDS.AI.Zombie((x * 34, y * 34 - 34), 100, 1))
                        monsterAmount += 1
                    elif tile == 'S':
                        sergeants.append(KDS.AI.SergeantZombie(
                            (x * 34, y * 34 - 34), 220, 1))
                        monsterAmount += 1
                    elif tile == 'V':
                        archviles.append(Archvile((x * 34, y * 34-51), 750, 2))
                        monsterAmount += 1
                    elif tile == 'K':
                        bulldogs.append(KDS.AI.Bulldog((x * 34, y * 34), 80, 3, bulldog_run_animation))
                        monsterAmount += 1
                    else:
                        tile_rects.append(pygame.Rect(x * 34, y * 34, 34, 34))

                x += 1
            y += 1
    monstersLeft = monsterAmount
    return tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs, iron_bars
def load_item_rects():
    def append_rect():
        item_rects.append(pygame.Rect(x * 34, y * 34, 34, 34))
    item_rects = []
    item_ids = []
    task_items = []
    y = 0
    for layer in item_gen:
        x = 0
        for item in layer:
            if item == '0':
                append_rect()
                item_ids.append("gasburner")
            if item == '1':
                append_rect()
                item_ids.append("knife")
            if item == '2':
                append_rect()
                item_ids.append("red_key")
            if item == '3':
                append_rect()
                item_ids.append("green_key")
            if item == '4':
                append_rect()
                item_ids.append("blue_key")
            if item == '5':
                item_ids.append("coffeemug")
                task_items.append("coffeemug")
                append_rect()
            if item == '6':
                task_items.append("ss_bonuscard")
                item_ids.append("ss_bonuscard")
                append_rect()
            if item == '7':
                item_ids.append("lappi_sytytyspalat")
                append_rect()
            if item == '8':
                item_ids.append("plasmarifle")
                append_rect()
            if item == '9':
                item_ids.append("cell")
                append_rect()
            if item == '!':
                item_ids.append("pistol")
                append_rect()
            if item == '#':
                item_ids.append("pistol_mag")
                append_rect()
            if item == '%':
                item_ids.append("rk62")
                append_rect()
            if item == '&':
                item_ids.append("rk62_mag")
                append_rect()
            if item == '(':
                item_ids.append("medkit")
                append_rect()
            if item == ')':
                item_ids.append("shotgun")
                append_rect()
            if item == '=':
                item_ids.append("shotgun_shells")
                append_rect()
            if item == '+':
                item_ids.append("soulsphere")
                append_rect()
            if item == "'":
                item_ids.append("turboneedle")
                append_rect()
            x += 1
        y += 1
    return item_rects, item_ids, task_items
def load_doors():
    y = 0
    door_rects = list()
    doors_open = list()
    color_keys = list()
    for i in range(len(world_gen)):
        for layer in world_gen[i]:
            x = 0
            for door in layer:
                if door == 'k':
                    size = list(door_closed.get_size())
                    door_rects.append(pygame.Rect(
                        x * 34-1, y * 34, size[0]+1, size[1]))
                    doors_open.append(False)
                    color_keys.append("none")
                elif door == 'l':
                    size = list(red_door_closed.get_size())
                    door_rects.append(pygame.Rect(
                        x * 34-1, y * 34, size[0]+1, size[1]))
                    doors_open.append(False)
                    color_keys.append("red")
                elif door == 'm':
                    size = list(green_door_closed.get_size())
                    door_rects.append(pygame.Rect(
                        x * 34-1, y * 34, size[0]+1, size[1]))
                    doors_open.append(False)
                    color_keys.append("green")
                elif door == 'n':
                    size = list(blue_door_closed.get_size())
                    door_rects.append(pygame.Rect(
                        x * 34-1, y * 34, size[0]+1, size[1]))
                    doors_open.append(False)
                    color_keys.append("blue")
                x += 1
            y += 1

    return door_rects, doors_open, color_keys
def load_animation(name, number_of_images):
    animation_list = []
    for i in range(number_of_images):
        path = "Assets/Textures/Player/" + name + str(i) + ".png"
        img = pygame.image.load(path).convert()
        img.set_colorkey(KDS.Colors.GetPrimary.White)
        animation_list.append(img)
    return animation_list
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

        for tile in tile_rects:
            for shot in shots:
                if tile.collidepoint(shot):
                    shots.remove(shot)

        for zombie1 in zombies:
            for shot in shots:
                if zombie1.rect.collidepoint(shot):
                    shots.remove(shot)
                    zombie1.health -= 35

        for sergeant in sergeants:
            for shot in shots:
                if sergeant.rect.collidepoint(shot):
                    shots.remove(shot)
                    sergeant.health -= 35

        for archvile in archviles:
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
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list
def damage(health, min_damage: int, max_damage: int):
    health -= int(random.uniform(min_damage, max_damage))
    if health < 0:
        health = 0

    return health
def door_collision_test():
    x = 0

    def door_sound():
        pygame.mixer.Sound.play(door_opening)

    global door_rects, doors_open, color_keys, player_movement
    hit_list = collision_test(player_rect, door_rects)
    if len(door_rects) > 0 and player_rect.colliderect(door_rects[0]):
        pass

    for recta in door_rects:
        if recta.colliderect(render_rect):
            for door in hit_list:
                if recta == door:
                    if player_movement[0] > 0 and doors_open[x] == False:
                        player_rect.right = door.left + 1
                    if not doors_open[x]:
                        if FunctionKey == True:
                            if color_keys[x] != "none":
                                if color_keys[x] == "red":
                                    if player_keys["red"]:
                                        doors_open[x] = True
                                        door_sound()
                                elif color_keys[x] == "green":
                                    if player_keys["green"]:
                                        doors_open[x] = True
                                        door_sound()
                                elif color_keys[x] == "blue":
                                    if player_keys["blue"]:
                                        doors_open[x] = True
                                        door_sound()
                            else:
                                doors_open[x] = True
                                door_sound()

                    if player_movement[0] < 0 and doors_open[x] == False:
                        player_rect.left = door.right - 1

            x += 1
def item_collision_test(rect, items):
    hit_list = []
    x = 0
    global player_hand_item, player_score, inventory, inventory_slot, item_ids, player_keys, item_rects, ammunition_plasma, pistol_bullets, rk_62_ammo, player_health, shotgun_shells, playerStamina

    def s(score):
        global player_score

        player_score += score

    itemTipVisible = False
    for item in items:
        if rect.colliderect(item):
            hit_list.append(item)
            if not itemTipVisible:
                itemTip = tip_font.render(
                    "Nosta Esine Painamalla [E]", True, KDS.Colors.GetPrimary.White)
                screen.blit(
                    itemTip, (item.x - scroll[0] - 60, item.y - scroll[1] - 10))
                itemTipVisible = True
            if FunctionKey == True:
                i = item_ids[x]

                if inventory[inventory_slot] == "none":
                    if i == "gasburner":
                        inventory[inventory_slot] = "gasburner"
                        Audio.playSound(gasburner_clip)
                        item_rects.remove(item)
                        del item_ids[x]

                        s(5)
                    elif i == "knife":
                        inventory[inventory_slot] = "knife"
                        Audio.playSound(knife_pickup)
                        item_rects.remove(item)
                        del item_ids[x]
                        s(5)
                    elif i == "plasmarifle":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "plasmarifle"
                            Audio.playSound(weapon_pickup)
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "ss_bonuscard":
                        inventory[inventory_slot] = "ss_bonuscard"
                        Audio.playSound(ss_sound)
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "coffeemug":
                        inventory[inventory_slot] = "coffeemug"
                        Audio.playSound(coffeemug_sound)
                        item_rects.remove(item)
                        del item_ids[x]
                        s(3)
                    elif i == "lappi_sytytyspalat":
                        inventory[inventory_slot] = "lappi_sytytyspalat"
                        Audio.playSound(lappi_sytytyspalat_sound)
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "pistol":
                        inventory[inventory_slot] = "pistol"
                        Audio.playSound(weapon_pickup)
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "rk62":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "rk62"
                            Audio.playSound(weapon_pickup)
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "shotgun":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "shotgun"
                            Audio.playSound(weapon_pickup)
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "iPuhelin":
                        inventory[inventory_slot] = "iPuhelin"
                        item_rects.remove(item)
                        del item_ids[x]

                if i == "red_key":
                    player_keys["red"] = True
                    Audio.playSound(key_pickup)
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "green_key":
                    player_keys["green"] = True
                    Audio.playSound(key_pickup)
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "blue_key":
                    player_keys["blue"] = True
                    Audio.playSound(key_pickup)
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "cell":
                    ammunition_plasma += 30
                    item_rects.remove(item)
                    Audio.playSound(item_pickup)
                    del item_ids[x]
                elif i == "pistol_mag":
                    pistol_bullets += 8
                    item_rects.remove(item)
                    Audio.playSound(item_pickup)
                    del item_ids[x]
                elif i == "rk62_mag":
                    rk_62_ammo += 30
                    item_rects.remove(item)
                    Audio.playSound(item_pickup)
                    del item_ids[x]
                elif i == "shotgun_shells":
                    shotgun_shells += 4
                    item_rects.remove(item)
                    Audio.playSound(item_pickup)
                    del item_ids[x]
                elif i == "medkit":
                    if player_health < 100:
                        player_health += 25
                        if player_health > 100:
                            player_health = 100
                    item_rects.remove(item)
                    Audio.playSound(item_pickup)
                    del item_ids[x]
                elif i == "soulsphere":
                    player_health += 100
                    if player_health > 300:
                        player_health = 300
                    item_rects.remove(item)
                    Audio.playSound(soulsphere_pickup)
                    del item_ids[x]
                elif i == "turboneedle":
                    playerStamina = 250
                    item_rects.remove(item)
                    Audio.playSound(soulsphere_pickup)
                    del item_ids[x]

        x += 1
    return hit_list
def toilet_collisions(rect, burnstate):
    global burning_toilets, player_score, burning_trashcans
    o = 0
    for toilet in toilets:
        if rect.colliderect(toilet):
            if not rect.bottom == toilet.top:
                if (rect.colliderect(toilet) and burnstate):
                    if burning_toilets[o] == False:
                        player_score += 15
                    burning_toilets[o] = True
        o += 1
    o = 0
    for trashcan1 in trashcans:
        if rect.colliderect(trashcan1):
            if not rect.bottom == trashcan1.top:
                if (rect.colliderect(trashcan1) and burnstate):
                    if burning_trashcans[o] == False:
                        player_score += 15
                    burning_trashcans[o] = True
        o += 1
#endregion
#region Player
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

stand_animation = load_animation("stand", 2)
run_animation = load_animation("run", 2)
short_stand_animation = load_animation("shortplayer_stand", 2)
short_run_animation = load_animation("shortplayer_run", 2)

gasburner_animation = load_animation("gasburner_on", 2)
knife_animation = load_animation("knife", 2)
toilet_animation = load_animation("toilet_anim", 3)
trashcan_animation = load_animation("trashcan", 3)
koponen_stand = load_animation("koponen_standing", 2)
koponen_run = load_animation("koponen_running", 2)
death_animation = load_animation("death", 5)
menu_gasburner_animation = KDS.Animator.Animation(
    "main_menu_bc_gasburner", 2, 5, KDS.Colors.GetPrimary.White, -1)
menu_toilet_animation = KDS.Animator.Animation(
    "toilet_anim", 3, 6, KDS.Colors.GetPrimary.White, -1)
menu_trashcan_animation = KDS.Animator.Animation(
    "trashcan", 3, 6, KDS.Colors.GetPrimary.White, -1)
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
flames_animation = KDS.Animator.Animation("flames", 5, 3, KDS.Colors.GetPrimary.White, -1)
bulldog_run_animation = KDS.Animator.Animation("bulldog", 5, 6, KDS.Colors.GetPrimary.White, - 1)
#region Sergeant fixing
sergeant_shoot_animation.images = []
for _ in range(5):
    for _ in range(6):
        sergeant_shoot_animation.images.append(sergeant_aiming)
for _ in range(2):
    sergeant_shoot_animation.images.append(sergeant_firing)
for _ in range(2):
    for _ in range(6):
        sergeant_shoot_animation.images.append(sergeant_aiming)
KDS.Logging.Log(KDS.Logging.LogType.debug,
                "Sergeant Shoot Animation Images Initialised: " + str(len(sergeant_shoot_animation.images)), False)
for animation in sergeant_shoot_animation.images:
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Initialised Sergeant Shoot Animation Image: " + str(animation), False)
sergeant_shoot_animation.ticks = 43
#endregion
sergeant_death_animation = KDS.Animator.Animation(
    "seargeant_dying", 5, 8, KDS.Colors.GetPrimary.White, 1)
#endregion
#region Console
def console():
    global inventory, player_keys, player_health, koponen_happines, bulldogs

    command_input = input("command: ")
    command_input = command_input.lower()
    command_list = command_input.split()

    if command_list[0] == "give":
        if command_list[1] != "key":
            try:
                inventory[inventory_slot] = command_list[1]
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Item was given: " + str(command_list[1]), True)
            except Exception:
                KDS.Logging.Log(
                    KDS.Logging.LogType.info, "That item does not exist: " + str(command_list[1]), True)
        elif command_list[1] == "key":
            try:
                player_keys[command_list[2]] = True
                KDS.Logging.Log(KDS.Logging.LogType.info, "Item was given: " +
                                str(command_list[1]) + " " + str(command_list[2]), True)
            except Exception:
                KDS.Logging.Log(KDS.Logging.LogType.info, "That item does not exist: " +
                                str(command_list[1]) + " " + str(command_list[2]), True)
    elif command_list[0] == "playboy":
        koponen_happines = 1000
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "You are now a playboy", True)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Koponen happines: {}".format(koponen_happines), True)
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
                KDS.Logging.Log(KDS.Logging.LogType.info, "Terms status set to: " + str(setTerms), True)
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
                for dog in bulldogs:
                    KDS.Logging.Log(KDS.Logging.LogType.info, str(dog) + " woof status has been set to: " + str(woofState), True)
                    KDS.AI.Bulldog.SetAngry(dog, woofState)
            else:
                KDS.Logging.Log(KDS.Logging.LogType.info,
                                "Please provide a proper state for woof", True)
        else:
            KDS.Logging.Log(KDS.Logging.LogType.info,
                            "Please provide a proper state for woof", True)
    else:
        KDS.Logging.Log(KDS.Logging.LogType.info, "This command does not exist")
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

    agree_button = KDS.UI.New.Button(pygame.Rect(465, 500, 270, 135), tcagr_agree_function, button_font1.render("I Agree", True, KDS.Colors.GetPrimary.White))

    while tcagr_running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    FullscreenSet()
                elif event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                elif event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
        main_display.blit(pygame.transform.scale(agr_background, (int(agr_background.get_width() * FullscreenGet.scaling), int(agr_background.get_height() * FullscreenGet.scaling))), (int(FullscreenGet.offset[0]), int(FullscreenGet.offset[1])))
        agree_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        pygame.display.update()
        c = False
    del agree_button
#endregion
#region Koponen Talk
def koponen_talk():
    global main_running, inventory, currently_on_mission, inventory, player_score, ad_images, task_items, playerMovingLeft, playerMovingRight, playerSprinting, koponen_talking_background, koponen_talking_foreground_indexes, koponenTalking
    conversations = list()

    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
        KDS.Missions.SetProgress("koponen_introduction", "talk", 1.0)
    elif KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
        if int(current_map) < 2:
            KDS.Missions.SetProgress("koponen_introduction", "talk", 1.0)
        elif int(current_map) == 2:
            KDS.Missions.SetProgress("koponen_talk", "talk", 1.0)

    koponenTalking = True
    pygame.mouse.set_visible(True)

    playerMovingLeft = False
    playerMovingRight = False
    playerSprinting = False

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

        conversations.append("{}: Saisinko tehtävän?".format(player_name))
        if currently_on_mission:
            conversations.append("Koponen: Olen pahoillani, sinulla on")
            conversations.append("         tehtävä kesken")
            conversations.append("Koponen: Tehtäväsi oli tuoda minulle")
            conversations.append("         {}.".format(task))
        elif task_items:
            current_mission = task_items[0]
            task_items.remove(task_items[0])
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
                "Koponen: Toisitko minulle {}".format(taskTaivutettu))
            currently_on_mission = True

    def date_function():
        global koponen_happines

        conversations.append(
            "{}: Tulisitko kanssani treffeille?".format(player_name))

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
                conversations.append("         {}".format(task))

    c = False

    conversations.append("Koponen: Hyvää päivää")

    exit_button = KDS.UI.New.Button(pygame.Rect(940, 700, 230, 80), exit_function1, button_font1.render("EXIT", True, KDS.Colors.GetPrimary.White))
    mission_button = KDS.UI.New.Button(pygame.Rect(50, 700, 450, 80), mission_function, button_font1.render("REQUEST MISSION", True, KDS.Colors.GetPrimary.White))
    date_button = KDS.UI.New.Button(pygame.Rect(50, 610, 450, 80), date_function, button_font1.render("ASK FOR A DATE", True, KDS.Colors.GetPrimary.White))
    r_mission_button = KDS.UI.New.Button(pygame.Rect(510, 700, 420, 80), end_mission, button_font1.render("RETURN MISSION", True, KDS.Colors.GetPrimary.White))

    while koponenTalking:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponenTalking = False
                elif event.key == K_F11:
                    FullscreenSet()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()
        main_display.blit(pygame.transform.scale(koponen_talking_background, (int(koponen_talking_background.get_width() * FullscreenGet.scaling), int(koponen_talking_background.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1])))
        main_display.blit(pygame.transform.scale(koponen_talk_foreground, (int(koponen_talk_foreground.get_width() * FullscreenGet.scaling), int(koponen_talk_foreground.get_height() * FullscreenGet.scaling))), (int(40 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(474 * FullscreenGet.scaling + FullscreenGet.offset[1])))
        pygame.draw.rect(main_display, (230, 230, 230), (int(40 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(40 * FullscreenGet.scaling + FullscreenGet.offset[1]), int(700 * FullscreenGet.scaling), int(400 * FullscreenGet.scaling)))
        pygame.draw.rect(main_display, (30, 30, 30), (int(40 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(40 * FullscreenGet.scaling + FullscreenGet.offset[1]), int(700 * FullscreenGet.scaling), int(400 * FullscreenGet.scaling)), 3)

        exit_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        mission_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        date_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        r_mission_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)

        while len(conversations) > 13:
            del conversations[0]
        for i in range(len(conversations)):
            row_text = text_font.render(conversations[i], True, (7, 8, 10))
            row_text_size = text_font.size(conversations[i])
            main_display.blit(pygame.transform.scale(row_text, (int(row_text_size[0] * FullscreenGet.scaling), int(row_text_size[1] * FullscreenGet.scaling))), (int(50 * FullscreenGet.scaling + FullscreenGet.offset[0]), int((50 + (i * 30)) * FullscreenGet.scaling + FullscreenGet.offset[1])))
        c = False
        pygame.display.update()
        main_display.fill((0, 0, 0))
    pygame.mouse.set_visible(False)
#endregion
#region Menus
def esc_menu_f():
    global esc_menu, go_to_main_menu, DebugMode, clock
    c = False

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

    resume_button = KDS.UI.New.Button(pygame.Rect(int(display_size[0] / 2 - 100), 400, 200, 30), resume, button_font.render("Resume", True, KDS.Colors.GetPrimary.White))
    save_button_enabled = True
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
        save_button_enabled = False
    save_button = KDS.UI.New.Button(pygame.Rect(int(display_size[0] / 2 - 100), 438, 200, 30), save, button_font.render("Save", True, KDS.Colors.GetPrimary.White), (100, 100, 100), (115, 115, 115), (90, 90, 90), (75, 75, 75), save_button_enabled)
    settings_button = KDS.UI.New.Button(pygame.Rect(int(display_size[0] / 2 - 100), 475, 200, 30), settings, button_font.render("Settings", True, KDS.Colors.GetPrimary.White))
    main_menu_button = KDS.UI.New.Button(pygame.Rect(int(display_size[0] / 2 - 100), 513, 200, 30), goto_main_menu, button_font.render("Main menu", True, KDS.Colors.GetPrimary.White))

    while esc_menu:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    FullscreenSet()
                if event.key == K_ESCAPE:
                    esc_menu = False
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == pygame.QUIT:
                KDS_Quit()

        game_background_scaling = FullscreenGet.size[1] / esc_menu_background.get_height()
        main_display.blit(pygame.transform.scale(esc_menu_background, (int(esc_menu_background.get_width() * game_background_scaling), int(esc_menu_background.get_height() * game_background_scaling))), (0, 0))
        pygame.draw.rect(main_display, (123, 134, 111), (int((window_size[0] / 2) - 250 * FullscreenGet.scaling), int((window_size[1] / 2) - 200 * FullscreenGet.scaling), int(500 * FullscreenGet.scaling), int(400 * FullscreenGet.scaling)))
        main_display.blit(pygame.transform.scale(
            text_icon, (int(250 * FullscreenGet.scaling), int(139 * FullscreenGet.scaling))), (int(window_size[0] / 2 - 125 * FullscreenGet.scaling), int(window_size[1] / 2 - 175 * FullscreenGet.scaling)))

        resume_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        save_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        settings_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
        main_menu_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)

        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            main_display.blit(pygame.transform.scale(score_font.render(fps_text, True, KDS.Colors.GetPrimary.White), (int(score_font.size(fps_text)[0] * 2 * FullscreenGet.scaling), int(score_font.size(fps_text)[1] * 2 * FullscreenGet.scaling))), (int(10 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(10 * FullscreenGet.scaling + FullscreenGet.offset[1])))

        pygame.display.update()
        main_display.fill((0, 0, 0))
        c = False

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, music_volume, effect_volume, DebugMode
    c = False
    settings_running = True

    def return_def():
        global settings_running
        settings_running = False

    return_button = KDS.UI.New.Button(pygame.Rect(465, 700, 270, 60), return_def, button_font1.render("Return", True, KDS.Colors.GetPrimary.White))
    music_volume_slider = KDS.UI.New.Slider("Music Volume", pygame.Rect(450, 135, 340, 20), (20, 30), 0.5)
    effect_volume_slider = KDS.UI.New.Slider("Sound Effect Volume", pygame.Rect(450, 185, 340, 20), (20, 30), 0.5)

    while settings_running:

        music_volume_text = button_font.render("Music Volume", True, KDS.Colors.GetPrimary.White)
        effect_volume_text = button_font.render("Sound Effect Volume", True, KDS.Colors.GetPrimary.White)

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    FullscreenSet()
                elif event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                elif event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
                elif event.key == K_ESCAPE:
                    settings_running = False
                elif event.key == K_F3:
                    DebugMode = not DebugMode
            elif event.type == pygame.QUIT:
                KDS_Quit()

        main_display.blit(pygame.transform.scale(settings_background, (int(settings_background.get_width() * FullscreenGet.scaling), int(settings_background.get_height() * FullscreenGet.scaling))), (int(FullscreenGet.offset[0]), int(FullscreenGet.offset[1])))

        main_display.blit(pygame.transform.flip(pygame.transform.scale(
            menu_trashcan_animation.update(), (int(menu_trashcan_animation.get_frame().get_width() * 2 * FullscreenGet.scaling),
                                               int(menu_trashcan_animation.get_frame().get_height() * 2 * FullscreenGet.scaling))),
                                                False, False), (int((279 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int((515 * FullscreenGet.scaling) + FullscreenGet.offset[1])))

        main_display.blit(pygame.transform.scale(music_volume_text, (int(music_volume_text.get_width() * FullscreenGet.scaling), int(music_volume_text.get_height() * FullscreenGet.scaling))), (int(50 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(135 * FullscreenGet.scaling + FullscreenGet.offset[1])))
        main_display.blit(pygame.transform.scale(effect_volume_text, (int(effect_volume_text.get_width() * FullscreenGet.scaling), int(effect_volume_text.get_height() * FullscreenGet.scaling))), (int(50 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(185 * FullscreenGet.scaling + FullscreenGet.offset[1])))
        set_music_volume = music_volume_slider.update(main_display, FullscreenGet.scaling, FullscreenGet.offset)
        set_effect_volume = effect_volume_slider.update(main_display, FullscreenGet.scaling, FullscreenGet.offset)

        if set_music_volume != music_volume:
            music_volume = set_music_volume
            pygame.mixer.music.set_volume(music_volume)
            Audio.MusicChannel1.set_volume(music_volume)
            Audio.MusicChannel2.set_volume(music_volume)
        elif set_effect_volume != effect_volume:
            effect_volume = set_effect_volume

        return_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)

        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            main_display.blit(pygame.transform.scale(score_font.render(fps_text, True, KDS.Colors.GetPrimary.White), (int(score_font.size(fps_text)[0] * 2 * FullscreenGet.scaling), int(score_font.size(fps_text)[1] * 2 * FullscreenGet.scaling))), (int(10 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(10 * FullscreenGet.scaling + FullscreenGet.offset[1])))

        pygame.display.update()
        main_display.fill((0, 0, 0))
        c = False
        clock.tick(60)

def play_function(gamemode: KDS.Gamemode.Modes, reset_scroll):
    global main_menu_running, current_map, inventory, Audio, music_volume, player_health, player_keys, player_hand_item, player_death_event, player_rect, animation_has_played, death_wait, true_scroll
    KDS.Gamemode.SetGamemode(gamemode, int(current_map))
    inventory = ["none", "none", "none", "none", "none"]
    if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story or int(current_map) < 2:
        inventory[0] = "iPuhelin"
    WorldGeneration()
    pygame.mouse.set_visible(False)
    main_menu_running = False
    play_map_music(current_map)
    player_hand_item = "none"

    player_death_event = False
    animation_has_played = False
    death_wait = 0

    player_rect.x = 100
    player_rect.y = 100
    if reset_scroll:
        true_scroll = [-200, -190]
    player_health = 100

    for key in player_keys:
        player_keys[key] = False
    KDS.Logging.Log(KDS.Logging.LogType.info,
                    "Press F4 to commit suicide", False)
    KDS.Logging.Log(KDS.Logging.LogType.info,
                    "Press Alt + F4 to get depression", False)
    LoadSave()

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

    pygame.mixer.music.load("Assets/Audio/Music/lobbymusic.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(music_volume)

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
            if current_map_int < 10:
                current_map = "0" + str(current_map_int)
            else:
                current_map = str(current_map_int)
            KDS.ConfigManager.SetSetting("Settings", "CurrentMap", current_map)

    def mode_selection_function():
        global MenuMode
        MenuMode = Mode.ModeSelectionMenu

    main_menu_play_button = KDS.UI.New.Button(pygame.Rect(450, 180, 300, 60), mode_selection_function, button_font1.render("PLAY", True, KDS.Colors.GetPrimary.White))
    main_menu_settings_button = KDS.UI.New.Button(pygame.Rect(450, 250, 300, 60), settings_function, button_font1.render("SETTINGS", True, KDS.Colors.GetPrimary.White))
    main_menu_quit_button = KDS.UI.New.Button(pygame.Rect(450, 320, 300, 60), KDS_Quit, button_font1.render("QUIT", True, KDS.Colors.GetPrimary.White))

    while main_menu_running:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    FullscreenSet()
                elif event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                elif event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
                elif event.key == K_F3:
                    DebugMode = not DebugMode
                elif event.key == K_ESCAPE:
                    if MenuMode != Mode.MainMenu:
                        MenuMode = Mode.MainMenu
            elif event.type == pygame.QUIT:
                KDS_Quit()

        if MenuMode == Mode.MainMenu:

            main_display.blit(pygame.transform.scale(main_menu_background, FullscreenGet.size), (int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1])))
            main_display.blit(pygame.transform.flip(pygame.transform.scale(
                menu_gasburner_animation.update(), (int(menu_gasburner_animation.get_frame().get_width() * FullscreenGet.scaling),
                                                    int(menu_gasburner_animation.get_frame().get_height() * FullscreenGet.scaling))),
                                                    False, False), (int((625 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int((445 * FullscreenGet.scaling) + FullscreenGet.offset[1])))
            main_display.blit(pygame.transform.flip(pygame.transform.scale(
                menu_toilet_animation.update(), (int(menu_toilet_animation.get_frame().get_width() * 2 * FullscreenGet.scaling),
                                                 int(menu_toilet_animation.get_frame().get_height() * 2 * FullscreenGet.scaling))),
                                                    False, False), (int((823 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int((507 * FullscreenGet.scaling) + FullscreenGet.offset[1])))
            main_display.blit(pygame.transform.flip(pygame.transform.scale(
                menu_trashcan_animation.update(), (int(menu_trashcan_animation.get_frame().get_width() * 2 * FullscreenGet.scaling),
                                                   int(menu_trashcan_animation.get_frame().get_height() * 2 * FullscreenGet.scaling))),
                                                    False, False), (int((283 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int((585 * FullscreenGet.scaling) + FullscreenGet.offset[1])))

            main_menu_play_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
            main_menu_settings_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)
            main_menu_quit_button.update(main_display, c, FullscreenGet.scaling, FullscreenGet.offset)

        elif MenuMode == Mode.ModeSelectionMenu:
            mode_selection_buttons = list()
            mode_selection_modes = list()
            story_mode_button = pygame.Rect(int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1]), int(FullscreenGet.size[0]), int(FullscreenGet.size[1] / 2))
            campaign_mode_button = pygame.Rect(int(0 + FullscreenGet.offset[0]), int(FullscreenGet.size[1] / 2), int(FullscreenGet.size[0]), int(FullscreenGet.size[1] / 2))
            mode_selection_buttons.append(story_mode_button)
            mode_selection_buttons.append(campaign_mode_button)
            mode_selection_modes.append(KDS.Gamemode.Modes.Story)
            mode_selection_modes.append(KDS.Gamemode.Modes.Campaign)

            main_display.blit(pygame.transform.scale(gamemode_bc_1_1, (int(gamemode_bc_1_1.get_width() * FullscreenGet.scaling), int(gamemode_bc_1_1.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1])))
            main_display.blit(pygame.transform.scale(gamemode_bc_2_1, (int(gamemode_bc_2_1.get_width() * FullscreenGet.scaling), int(gamemode_bc_2_1.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int((display_size[1] * FullscreenGet.scaling) / 2 + FullscreenGet.offset[1])))
            for y in range(len(mode_selection_buttons)):
                if mode_selection_buttons[y].collidepoint(pygame.mouse.get_pos()):
                    if y == 0:
                        main_display.blit(pygame.transform.scale(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(gamemode_bc_1_alpha.update(False) * 255.0)), (int(gamemode_bc_1_2.get_width() * FullscreenGet.scaling), int(gamemode_bc_1_2.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1])))
                    elif y == 1:
                        main_display.blit(pygame.transform.scale(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(gamemode_bc_2_alpha.update(False) * 255.0)), (int(gamemode_bc_2_2.get_width() * FullscreenGet.scaling), int(gamemode_bc_2_2.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int((display_size[1] * FullscreenGet.scaling) / 2 + FullscreenGet.offset[1])))
                    if c:
                        if mode_selection_modes[y] == KDS.Gamemode.Modes.Story:
                            MenuMode = Mode.StoryMenu
                        elif mode_selection_modes[y] == KDS.Gamemode.Modes.Campaign:
                            MenuMode = Mode.CampaignMenu
                            c = False
                        else:
                            frameinfo = getframeinfo(currentframe())
                            KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + frameinfo.lineno + ")\nInvalid mode_selection_mode! Value: " + mode_selection_modes[y])
                else:
                    if y == 0:
                        main_display.blit(pygame.transform.scale(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(gamemode_bc_1_alpha.update(True) * 255.0)), (int(gamemode_bc_1_2.get_width() * FullscreenGet.scaling), int(gamemode_bc_1_2.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int(0 + FullscreenGet.offset[1])))
                    elif y == 1:
                        main_display.blit(pygame.transform.scale(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(gamemode_bc_2_alpha.update(True) * 255.0)), (int(gamemode_bc_2_2.get_width() * FullscreenGet.scaling), int(gamemode_bc_2_2.get_height() * FullscreenGet.scaling))), (int(0 + FullscreenGet.offset[0]), int((display_size[1] * FullscreenGet.scaling) / 2 + FullscreenGet.offset[1])))

        elif MenuMode == Mode.StoryMenu:
            print("Wow... So empty.")

        elif MenuMode == Mode.CampaignMenu:
            campaign_right_button = pygame.Rect(int(FullscreenGet.size[0] - (50 * FullscreenGet.scaling) - (66 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int(200 * FullscreenGet.scaling + FullscreenGet.offset[1]), int(66 * FullscreenGet.scaling), int(66 * FullscreenGet.scaling))
            campaign_left_button = pygame.Rect(int(50 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(200 * FullscreenGet.scaling + FullscreenGet.offset[1]), int(66 * FullscreenGet.scaling), int(66 * FullscreenGet.scaling))
            campaign_play_button = pygame.Rect(int(FullscreenGet.size[0] / 2 - (150 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int(FullscreenGet.size[1] - (300 * FullscreenGet.scaling) + FullscreenGet.offset[1]), int(300 * FullscreenGet.scaling), int(100 * FullscreenGet.scaling))
            campaign_return_button = pygame.Rect(int(FullscreenGet.size[0] / 2 - (150 * FullscreenGet.scaling) + FullscreenGet.offset[0]), int(FullscreenGet.size[1] - (150 * FullscreenGet.scaling) + FullscreenGet.offset[1]), int(300 * FullscreenGet.scaling), int(100 * FullscreenGet.scaling))
            campaign_menu_buttons = list()
            campaign_menu_functions = list()
            campaign_menu_buttons.append(campaign_left_button)
            campaign_menu_buttons.append(campaign_right_button)
            campaign_menu_buttons.append(campaign_play_button)
            campaign_menu_buttons.append(campaign_return_button)
            campaign_menu_functions.append(level_pick.left)
            campaign_menu_functions.append(level_pick.right)
            campaign_menu_functions.append(play_function)
            campaign_menu_functions.append("useless, just like me.")
            campaign_play_text = button_font1.render("START", True, (KDS.Colors.Get.EmeraldGreen))
            campaign_play_text_size = button_font1.size("START")
            campaign_return_text = button_font1.render("RETURN", True, (KDS.Colors.Get.AviatorRed))
            campaign_return_text_size = button_font1.size("RETURN")

            pygame.draw.rect(main_display, (192, 192, 192), (int(50 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(200 * FullscreenGet.scaling + FullscreenGet.offset[1]), int(FullscreenGet.size[0] - (100 * FullscreenGet.scaling)), int(66 * FullscreenGet.scaling)))
            for y in range(len(campaign_menu_buttons)):
                if campaign_menu_buttons[y].collidepoint(pygame.mouse.get_pos()):
                    if c:
                        if y < 2:
                            campaign_menu_functions[y]()
                        elif y == 2:
                            campaign_menu_functions[y](KDS.Gamemode.Modes.Campaign, True)
                        else:
                            MenuMode = Mode.MainMenu
                        c = False
                    button_color = (115, 115, 115)
                    if pygame.mouse.get_pressed()[0]:
                        button_color = (90, 90, 90)
                else:
                    button_color = (100, 100, 100)

                pygame.draw.rect(main_display, button_color, campaign_menu_buttons[y])

                if y == 0:
                    main_display.blit(pygame.transform.scale(pygame.transform.flip(arrow_button, True, False), (int(arrow_button.get_width() * FullscreenGet.scaling), int(arrow_button.get_height() * FullscreenGet.scaling))), (campaign_menu_buttons[y].x + 8, campaign_menu_buttons[y].y + 8))
                elif y == 1:
                    main_display.blit(pygame.transform.scale(arrow_button, (int(arrow_button.get_width() * FullscreenGet.scaling), int(arrow_button.get_height() * FullscreenGet.scaling))), (int(campaign_menu_buttons[y].x + 8), int(campaign_menu_buttons[y].y + 8)))
                elif y == 2:
                    main_display.blit(pygame.transform.scale(campaign_play_text, (int(campaign_play_text_size[0] * FullscreenGet.scaling), int(campaign_play_text_size[1] * FullscreenGet.scaling))), (int(campaign_play_button.x + (campaign_play_button.width / 4)), int(campaign_play_button.y + (campaign_play_button.height / 4))))
                elif y == 3:
                    main_display.blit(pygame.transform.scale(campaign_return_text, (int(campaign_return_text_size[0] * FullscreenGet.scaling), int(campaign_return_text_size[1] * FullscreenGet.scaling))), (int(campaign_return_button.x + (campaign_return_button.width / 5)), int(campaign_return_button.y + (campaign_return_button.height / 4))))

                current_map_int = int(current_map)

                if current_map_int < len(map_names):
                    map_name = map_names[current_map_int]
                else:
                    map_name = map_names[0]
                level_text = button_font1.render(current_map + " - " + map_name, True, (0, 0, 0))
                level_text_size = button_font1.size(current_map + " - " + map_name)
                main_display.blit(pygame.transform.scale(level_text, (int(level_text_size[0] * FullscreenGet.scaling), int(level_text_size[1] * FullscreenGet.scaling))), (int(125 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(209 * FullscreenGet.scaling + FullscreenGet.offset[1])))

        if DebugMode:
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            main_display.blit(pygame.transform.scale(score_font.render(fps_text, True, KDS.Colors.GetPrimary.White), (int(score_font.size(fps_text)[0] * 2 * FullscreenGet.scaling), int(score_font.size(fps_text)[1] * 2 * FullscreenGet.scaling))), (int(10 * FullscreenGet.scaling + FullscreenGet.offset[0]), int(10 * FullscreenGet.scaling + FullscreenGet.offset[1])))

        pygame.display.update()
        main_display.fill((0, 0, 0))
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
#region Inventory Slot Switching
def inventoryLeft():
    global inventory_slot, inventoryDoubles, inventory
    KDS.Missions.SetProgress("tutorial", "inventory", 0.2)
    checkSlot = inventory_slot - 2
    if checkSlot < 0:
        checkSlot = len(inventory) + checkSlot
    if(inventoryDoubles[checkSlot] == True):
        inventory_slot -= 2
    else:
        inventory_slot -= 1
def inventoryRight():
    global inventory_slot, inventoryDoubles
    KDS.Missions.SetProgress("tutorial", "inventory", 0.2)
    if inventory_slot < len(inventoryDoubles):
        if inventoryDoubles[inventory_slot] == True:
            inventory_slot += 2
        else:
            inventory_slot += 1
#endregion
#region Main Running 
while main_running:
#region Events
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_d:
                playerMovingRight = True
            elif event.key == K_a:
                playerMovingLeft = True
            elif event.key == K_SPACE:
                moveUp = True
            elif event.key == K_LCTRL:
                moveDown = True
            elif event.key == K_LSHIFT:
                if not moveDown:
                    playerSprinting = True
            elif event.key == K_e:
                FunctionKey = True
            elif event.key == K_ESCAPE:
                esc_menu = True
            elif event.key == K_j:
                inventoryLeft()
            elif event.key == K_k:
                inventoryRight()
            elif event.key == K_t:
                console()
            elif event.key == K_w:
                moveUp = True
            elif event.key == K_s:
                moveDown = True
            elif event.key == K_f:
                if playerStamina == 100:
                    playerStamina = -1000
                    farting = True
                    Audio.playSound(fart)
                    KDS.Missions.SetProgress("tutorial", "fart", 1.0)
            elif event.key == K_q:
                if inventory[inventory_slot] != "none":
                    if inventory[inventory_slot] == "iPuhelin":
                        KDS.Missions.SetProgress("tutorial", "trash", 1.0)
                    if not direction:
                        item_rects.append(pygame.Rect((int(player_rect.bottomright[0] - 17), int(player_rect.bottomright[1])), (34, 34)))
                    else:
                        item_rects.append(pygame.Rect((int(player_rect.bottomleft[0] - 17), int(player_rect.bottomleft[1])), (34, 34)))
                    item_ids.append(inventory[inventory_slot])
                    u = True
                    while u:
                        item_rects[-1].y += 30
                        for tile in tile_rects:
                            if item_rects[-1].colliderect(tile):
                                item_rects[-1].bottom = tile.top
                                u = False
                if inventoryDoubles[inventory_slot] == True:
                    inventory[inventory_slot + 1] = "none"
                    inventoryDoubles[inventory_slot] = False
                inventory[inventory_slot] = "none"
            elif event.key == K_F3:
                DebugMode = not DebugMode
            elif event.key == K_F4:
                F4Pressed = True
                if AltPressed == True and F4Pressed == True:
                    KDS_Quit()
                else:
                    player_health = 0
            elif event.key == K_LALT or event.key == K_RALT:
                AltPressed = True
            elif event.key == K_F11:
                FullscreenSet()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseLeftPressed = True
                rk62_sound_cooldown = 11
                weapon_fire = True
                if player_hand_item == "gasburner":
                    gasburnerBurning = True
                if player_hand_item == "knife":
                    knifeInUse = True
                if player_hand_item == "plasmarifle":
                    plasmarifle_fire = True
        elif event.type == KEYUP:
            if event.key == K_d:
                playerMovingRight = False
            elif event.key == K_a:
                playerMovingLeft = False
            elif event.key == K_SPACE:
                moveUp = False
            elif event.key == K_LCTRL:
                moveDown = False
            elif event.key == K_LSHIFT:
                playerSprinting = False
            elif event.key == K_F4:
                F4Pressed = False
            elif event.key == K_LALT or event.key == K_RALT:
                AltPressed = False
            elif event.key == K_w:
                moveUp = False
            elif event.key == K_s:
                moveDown = False
            elif event.key == K_c:
                if player_hand_item == "gasburner":
                    gasburnerBurning = not gasburnerBurning
                    gasburner_fire.stop()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                mouseLeftPressed = False
                if player_hand_item == "gasburner":
                    gasburnerBurning = False
                if player_hand_item == "knife":
                    knifeInUse = False
                if player_hand_item == "plasmarifle":
                    plasmarifle_fire = False
            elif event.button == 4:
                inventoryLeft()
            elif event.button == 5:
                inventoryRight()
        elif event.type == pygame.QUIT:
            KDS_Quit()
#endregion
#region Inventory Code
    def inventoryDoubleOffsetCounter():
        inventoryDoubleOffset = 0
        for i in range(0, inventory_slot - 1):
            if inventoryDoubles[i] == True:
                inventoryDoubleOffset += 1
    inventoryDoubleOffsetCounter()
    if inventory_slot >= len(inventory):
        inventory_slot = len(inventory) - inventory_slot
    if inventory_slot < 0:
        inventory_slot = len(inventory) + inventory_slot

    main_display.fill((20, 25, 20))
    screen.fill((20, 25, 20))

    true_scroll[0] += (player_rect.x - true_scroll[0] - (screen_size[0] / 2)) / 12
    true_scroll[1] += (player_rect.y - true_scroll[1] - 220) / 12
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    if farting:
        shakeScreen()
    player_hand_item = inventory[inventory_slot]
    mouse_pos = pygame.mouse.get_pos()
#endregion
#region Player Death
    if player_health < 1 and not animation_has_played:
        player_death_event = True
        Audio.MusicChannel1.stop()
        Audio.MusicChannel2.stop()
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(player_death_sound)
        player_death_sound.set_volume(0.5)
        animation_has_played = True
    elif player_health < 1:
        death_wait += 1
        if death_wait == 240:
            play_function(KDS.Gamemode.gamemode, False)
#endregion
#region Rendering

    # Rendering: World Generation
    render_rect = pygame.Rect(scroll[0], scroll[1], screen_size[0], screen_size[1])
    vertical_render_position = [math.floor(max(0, (scroll[1] / 34) - 0)), math.ceil(min(len(world_gen[0]), ((scroll[1] + screen_size[1]) / 34) + 0))]
    horisontal_render_position = [math.floor(max(0, (scroll[0] / 34) - 0)), math.ceil(min(len(world_gen[0][0]), ((scroll[0] + screen_size[0]) / 34) + 0))]
    for y in range(vertical_render_position[0], vertical_render_position[1]):
        for x in range(horisontal_render_position[0], horisontal_render_position[1]):
            if world_gen[0][y][x] in tile_textures:
                screen.blit(tile_textures[world_gen[0][y][x]], (x * 34 - scroll[0], y * 34 - scroll[1]))


    # Rendering: Doors
    for i in range(len(door_rects)):
        if door_rects[i].colliderect(render_rect):
            if doors_open[i]:
                screen.blit(door_open, (door_rects[i].x - scroll[0]+2, door_rects[i].y - scroll[1]))
            else:
                if color_keys[i] == "red":
                    screen.blit(red_door_closed,
                                (door_rects[i].x - scroll[0], door_rects[i].y - scroll[1]))
                elif color_keys[i] == "green":
                    screen.blit(green_door_closed,
                                (door_rects[i].x - scroll[0], door_rects[i].y - scroll[1]))
                elif color_keys[i] == "blue":
                    screen.blit(blue_door_closed,
                                (door_rects[i].x - scroll[0], door_rects[i].y - scroll[1]))
                else:
                    screen.blit(door_closed, (door_rects[i].x - scroll[0], door_rects[i].y - scroll[1]))

    # Rendering: Jukeboxes
    for jukebox in jukeboxes:
        if jukebox.colliderect(render_rect):
            screen.blit(jukebox_texture, (jukebox.x -
                                        scroll[0], jukebox.y - scroll[1]))

    # Rendering: Landimes
    for landmine in landmines:
        if landmine.colliderect(render_rect):
            screen.blit(landmine_texture, (landmine.x - scroll[0], landmine.y - scroll[1]))
            if player_rect.colliderect(landmine):
                landmines.remove(landmine)
                Audio.playSound(landmine_explosion)
                player_health -= 60
                if player_health < 0:
                    player_health = 0
                explosion_positions.append((landmine.x-40, landmine.y-58))

    
        for zombie1 in zombies:
            if zombie1.rect.colliderect(landmine):
                landmines.remove(landmine)
                Audio.playSound(landmine_explosion)
                zombie1.health -= 140
                if zombie1.health < 0:
                    zombie1.health = 0
                explosion_positions.append((landmine.x-40, landmine.y-58))
        for sergeant in sergeants:
            if sergeant.rect.colliderect(landmine):
                landmines.remove(landmine)
                Audio.playSound(landmine_explosion)
                sergeant.health -= 220

                explosion_positions.append((landmine.x-40, landmine.y-58))

    # Rendering: Player's hand item
    if player_hand_item != "none":
        if player_hand_item == "plasmarifle":
            
            if plasmarifle_fire and plasmarifle_cooldown > 3 and ammunition_plasma > 0:
                plasmarifle_cooldown = 0

                if direction:
                    j_direction = False
                else:
                    j_direction = True
                if j_direction:
                    plasmabullets.append(plasma_bullet(
                        (player_rect.x + 50, player_rect.y + 17), j_direction, screen))
                else:
                    plasmabullets.append(plasma_bullet(
                        (player_rect.x - 50, player_rect.y + 17), j_direction, screen))

                Audio.playSound(plasmarifle_f_sound)
                ammunition_plasma -= 1

            ammo_count = score_font.render(
                "Ammo: " + str(ammunition_plasma), True, KDS.Colors.GetPrimary.White)
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "pistol":

            ammo_count = score_font.render(
                "Ammo: " + str(pistol_bullets), True, KDS.Colors.GetPrimary.White)
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "rk62":

            ammo_count = score_font.render(
                "Ammo: " + str(rk_62_ammo), True, KDS.Colors.GetPrimary.White)
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "shotgun":

            ammo_count = score_font.render(
                "Ammo: " + str(shotgun_shells), True, KDS.Colors.GetPrimary.White)
            screen.blit(ammo_count, (10, 360))

    # Rendering: Bullets
    for bullet in plasmabullets:
        state = bullet.update(tile_rects)
        if state:
            plasmabullets.remove(bullet)

    while len(plasmabullets) > 50:
        plasmabullets.remove(plasmabullets[0])

    # Rendering: Explosions
    for explosion in explosion_positions:
        explosion_image, done_state = explosion_animation.update()
        if not done_state:
            if pygame.Rect(explosion, (140, 70)).colliderect(render_rect):
                screen.blit(explosion_image, (explosion[0] - scroll[0], explosion[1] - scroll[1]))
        else:
            explosion_positions.remove(explosion)
            explosion_animation.reset()

    # Rendering: Items
    item_collision_test(player_rect, item_rects)
    for i in range(len(item_rects)):
        if item_rects[i].colliderect(render_rect):
            if DebugMode:
                pygame.draw.rect(screen,(2,2,220),(item_rects[i].x-scroll[0],item_rects[i].y-scroll[1],item_rects[i].width,item_rects[i].height))
            if item_ids[i] == 'gasburner':
                screen.blit(gasburner_off, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+10))
            if item_ids[i] == "knife":
                screen.blit(knife, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+26))
            if item_ids[i] == "red_key":
                screen.blit(red_key, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+16))
            if item_ids[i] == "green_key":
                screen.blit(green_key, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+16))
            if item_ids[i] == "blue_key":
                screen.blit(blue_key, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+16))
            if item_ids[i] == "coffeemug":
                screen.blit(
                    coffeemug, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1] + 14))
            if item_ids[i] == "ss_bonuscard":
                screen.blit(ss_bonuscard, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+14))
            if item_ids[i] == "lappi_sytytyspalat":
                screen.blit(lappi_sytytyspalat,
                            (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+17))
            if item_ids[i] == "plasmarifle":
                screen.blit(plasmarifle, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+17))
            if item_ids[i] == "cell":
                screen.blit(cell, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+17))
            if item_ids[i] == "pistol":
                screen.blit(pistol_texture,
                            (item_rects[i].x - scroll[0]-23, item_rects[i].y - scroll[1]+18))
            if item_ids[i] == "pistol_mag":
                screen.blit(pistol_mag, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+19))
            if item_ids[i] == "rk62":
                screen.blit(rk62_texture, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+17))
            if item_ids[i] == "rk62_mag":
                screen.blit(rk62_mag, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+14))
            if item_ids[i] == "medkit":
                screen.blit(medkit, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+15))
            if item_ids[i] == "shotgun":
                screen.blit(shotgun, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+22))
            if item_ids[i] == "shotgun_shells":
                screen.blit(shotgun_shells_t,
                            (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+25))
            if item_ids[i] == "iPuhelin":
                screen.blit(iphone_texture,
                            (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]+10))
            if item_ids[i] == 'soulsphere':
                screen.blit(soulsphere, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]))
            if item_ids[i] == 'turboneedle':
                screen.blit(turboneedle, (item_rects[i].x - scroll[0], item_rects[i].y - scroll[1]))
#endregion
#region PlayerMovement
    fall_speed = 0.4

    player_movement = [0, 0]
    onLadder = False
    for ladder in ladders:
        if player_rect.colliderect(ladder):
            onLadder = True
            vertical_momentum = 0
            air_timer = 0
            if moveUp:
                player_movement[1] = -1
            elif moveDown:
                player_movement[1] = 1
            else:
                player_movement[1] = 0

    if moveUp and not moveDown and air_timer < 6 and moveUp_released and not onLadder:
        moveUp_released = False
        vertical_momentum = -10
    elif vertical_momentum > 0:
        fall_speed *= fall_multiplier
    elif not moveUp:
        moveUp_released = True
        fall_speed *= fall_multiplier
   
    if player_health > 0:
        if playerSprinting == False and playerStamina < 100.0:
            playerStamina += 0.25
        elif playerSprinting and playerStamina > 0:
            playerStamina -= 0.75
        elif playerSprinting and playerStamina <= 0:
            playerSprinting = False

    koponen_recog_rec.center = koponen_rect.center

    if playerMovingRight == True:
        if not moveDown:
            player_movement[0] += 4
        else:
            player_movement[0] += 2
        KDS.Missions.SetProgress("tutorial", "walk", 0.005)
        if playerSprinting == True and playerStamina > 0:
            player_movement[0] += 4
            KDS.Missions.SetProgress("tutorial", "walk", 0.005)

    if playerMovingLeft == True:
        if not moveDown:
            player_movement[0] -= 4
        else:
            player_movement[0] -= 2
        KDS.Missions.SetProgress("tutorial", "walk", 0.005)
        if playerSprinting == True and playerStamina > 0:
            player_movement[0] -= 4
            KDS.Missions.SetProgress("tutorial", "walk", 0.005)
    player_movement[1] += vertical_momentum
    vertical_momentum += fall_speed
    if vertical_momentum > 8:
        vertical_momentum = 8


    if check_crouch == True:
        crouch_collisions = move_entity(pygame.Rect(player_rect.x, player_rect.y - crouch_size[1], player_rect.width, player_rect.height), (0, 0), tile_rects, False, True)[1]
    else:
        crouch_collisions = collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

    if moveDown and not onLadder and player_rect.height != crouch_size[1] and death_wait < 1:
        player_rect = pygame.Rect(player_rect.x, player_rect.y + (stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
        check_crouch = True
    elif (not moveDown or onLadder or death_wait > 0) and player_rect.height != stand_size[1] and crouch_collisions['bottom'] == False:
        player_rect = pygame.Rect(player_rect.x, player_rect.y + (crouch_size[1] - stand_size[1]), stand_size[0], stand_size[1])
        check_crouch = False
    elif not moveDown and crouch_collisions['bottom'] == True and player_rect.height != crouch_size[1] and death_wait < 1:
        player_rect = pygame.Rect(player_rect.x, player_rect.y + (stand_size[1] - crouch_size[1]), crouch_size[0], crouch_size[1])
        check_crouch = True

    toilet_collisions(player_rect, gasburnerBurning)

    if player_health > 0:
        player_rect, collisions = move_entity(
            player_rect, player_movement, tile_rects)
    else:
        player_rect, collisions = move_entity(player_rect, [0, 8], tile_rects)
#endregion
#region AI
    koponen_rect, k_collisions = move_entity(koponen_rect, koponen_movement, tile_rects)

    wa = zombie_walk_animation.update()
    sa = sergeant_walk_animation.update()

    for sergeant in sergeants:
        if DebugMode:
            pygame.draw.rect(screen,(220,2,2),(sergeant.rect.x-scroll[0],sergeant.rect.y-scroll[1],sergeant.rect.width,sergeant.rect.height))
        if sergeant.health > 0:
            if sergeant.hitscanner_cooldown > 100:
                hitscan = sergeant.hit_scan(
                    player_rect, player_health, tile_rects)
                sergeant.hitscanner_cooldown = 0
                if hitscan:
                    sergeant.shoot = True

            else:
                hitscan = False
            if not sergeant.shoot:
                sergeant.rect, sergeant.hits = move_entity(
                    sergeant.rect, sergeant.movement, tile_rects)

                if sergeant.movement[0] > 0:
                    sergeant.direction = True
                elif sergeant.movement[0] < 0:
                    sergeant.direction = False

                if sergeant.rect.colliderect(render_rect):
                    screen.blit(pygame.transform.flip(sa, sergeant.direction, False),
                                (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))

                if sergeant.hits["right"] or sergeant.hits["left"]:
                    sergeant.movement[0] = -sergeant.movement[0]

            else:
                u, i = sergeant_shoot_animation.update()

                if sergeant.rect.colliderect(render_rect):
                    screen.blit(pygame.transform.flip(u, sergeant.direction, False),
                                (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))

                if sergeant_shoot_animation.tick > 30 and not sergeant.xvar:
                    sergeant.xvar = True
                    Audio.playSound(shotgun_shot)
                    if sergeant.hit_scan(player_rect, player_health, tile_rects):
                        player_health = damage(player_health, 20, 50)
                if i:
                    sergeant_shoot_animation.reset()
                    sergeant.shoot = False
                    sergeant.xvar = False

        elif sergeant.playDeathAnimation:
            d, s = sergeant_death_animation.update()
            if not s and sergeant.rect.colliderect(render_rect):
                screen.blit(pygame.transform.flip(d, sergeant.direction, False),
                            (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]))
            if s:
                sergeant.playDeathAnimation = False
                sergeant_death_animation.reset()
                monstersLeft -= 1
        else:
            screen.blit(pygame.transform.flip(sergeant_corpse, sergeant.direction,
                                              False), (sergeant.rect.x - scroll[0], sergeant.rect.y - scroll[1]+10))
            if not sergeant.loot_dropped:
                sergeant.loot_dropped = True
                if round(random.uniform(0, 3)) == 0:
                    item_rects.append(pygame.Rect(sergeant.rect.x, sergeant.rect.y + (sergeant.rect.height / 2) - 2, sergeant.rect.width, sergeant.rect.height / 2))
                    item_ids.append("shotgun_shells")
            
    for zombie1 in zombies:
        if DebugMode:
            pygame.draw.rect(screen,(220,2,2),(zombie1.rect.x-scroll[0],zombie1.rect.y-scroll[1],zombie1.rect.width,zombie1.rect.height))
        if zombie1.health > 0:
            search = zombie1.search(player_rect)
            if not search:
                zombie1.rect, zombie1.hits = move_entity(
                    zombie1.rect, zombie1.movement, tile_rects)
                if zombie1.movement[0] != 0:
                    zombie1.walking = True
                    if zombie1.movement[0] > 0:
                        zombie1.direction = False
                    else:
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
                                              False), (zombie1.rect.x - scroll[0], zombie1.rect.y - scroll[1]+14))

    # Zombien käsittely loppuu tähän

    arch_run = archvile_run_animation.update()
    for archvile in archviles:
        if DebugMode:
            pygame.draw.rect(screen,(220,2,2),(archvile.rect.x-scroll[0],archvile.rect.y-scroll[1],archvile.rect.width,archvile.rect.height))
        archvile.update(arch_run)

    for bulldog in bulldogs:
        bulldog.startUpdateThread(player_rect, tile_rects)
    
    for bulldog in bulldogs:
        if DebugMode:
            if bulldog.a:
                pygame.draw.rect(screen,(220,2,2),(bulldog.rect.x-scroll[0],bulldog.rect.y-scroll[1],bulldog.rect.width,bulldog.rect.height))
            else:
                pygame.draw.rect(screen,(220,220,0),(bulldog.rect.x-scroll[0],bulldog.rect.y-scroll[1],bulldog.rect.width,bulldog.rect.height))
        bd_attr = bulldog.getAttributes()
        screen.blit(pygame.transform.flip(bd_attr[1],bd_attr[2], False),(bd_attr[0].x - scroll[0],bd_attr[0].y - scroll[1]))
        player_health -= bd_attr[3]

    if k_collisions["left"]:
        koponen_movingx = -koponen_movingx
    elif k_collisions["right"]:
        koponen_movingx = -koponen_movingx

    door_collision_test()
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
            if playerSprinting:
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

    if player_hand_item == "gasburner":
        if gasburner_animation_stats[2] > gasburner_animation_stats[1]:
            gasburner_animation_stats[0] += 1
            gasburner_animation_stats[2] = 0
            if gasburner_animation_stats[0] > 1:
                gasburner_animation_stats[0] = 0

    if player_hand_item == "knife":
        if knife_animation_stats[2] > knife_animation_stats[1]:
            knife_animation_stats[0] += 1
            knife_animation_stats[2] = 0
            if knife_animation_stats[0] > 1:
                knife_animation_stats[0] = 0

    if burning_animation_stats[2] > burning_animation_stats[1]:
        burning_animation_stats[0] += 1
        burning_animation_stats[2] = 0
        if burning_animation_stats[0] > 2:
            burning_animation_stats[0] = 0

    if koponen_animation_stats[2] > koponen_animation_stats[1]:
        koponen_animation_stats[0] += 1
        koponen_animation_stats[2] = 0
        if koponen_animation_stats[0] > 1:
            koponen_animation_stats[0] = 0

    if player_hand_item != "none" and player_health:
        if direction:
            offset_c = 49
            offset_k = 75
            offset_p = 75
            offset_pi = 80
            offset_rk = 80
        else:
            offset_c = 8
            offset_k = 10
            offset_p = 14
            offset_pi = 2
            offset_rk = 14
            
        if player_hand_item == "gasburner":
            offset = 11
            if direction:
                offset = -offset - 29
            if gasburnerBurning:
                if gasburner_animation_stats[0]:
                    gasburner_fire.stop()
                    pygame.mixer.Sound.play(gasburner_fire)
                screen.blit(pygame.transform.flip(gasburner_animation[gasburner_animation_stats[0]], direction, False), (
                    int(player_rect.centerx + offset - scroll[0]), int(player_rect.y - scroll[1])))
            else:
                screen.blit(pygame.transform.flip(gasburner_off, direction, False), (
                    int(player_rect.centerx + offset - scroll[0]), int(player_rect.y - scroll[1])))
        elif player_hand_item == "knife":
            offset = 14
            if direction:
                offset = -offset - 26
            if knifeInUse:
                if direction:
                    offset -= 20
                else:
                    offset -= 1
                screen.blit(pygame.transform.flip(knife_animation[knife_animation_stats[0]], direction, False), (
                    player_rect.centerx + offset - scroll[0], player_rect.y - scroll[1] + 14))
            else:
                screen.blit(pygame.transform.flip(knife, direction, False), (
                    player_rect.centerx + offset - scroll[0], player_rect.y - scroll[1] + 14))
        elif player_hand_item == "coffeemug":
            offset = 24
            if direction:
                offset = -offset
            screen.blit(pygame.transform.flip(coffeemug, direction, False), (
                int(player_rect.centerx + offset - scroll[0] - (coffeemug.get_width() / 2)), int(player_rect.y - scroll[1] + 14)))
        elif player_hand_item == "iPuhelin":
            offset = 20
            if direction:
                offset = -offset
            screen.blit(pygame.transform.flip(iphone_texture, direction, False), (
                int(player_rect.centerx + offset - scroll[0] - (iphone_texture.get_width() / 2)), int(player_rect.y - scroll[1] + 10)))
        elif player_hand_item == "plasmarifle":
            if plasmarifle_fire and ammunition_plasma > 0:
                screen.blit(pygame.transform.flip(plasmarifle_animation.update(), direction, False), (
                    player_rect.right-offset_p - scroll[0], player_rect.y - scroll[1]+14))

            else:
                screen.blit(pygame.transform.flip(plasmarifle, direction, False), (
                    player_rect.right-offset_p - scroll[0], player_rect.y - scroll[1]+14))
        elif player_hand_item == "pistol":
            pistol_cooldown += 1
            if weapon_fire and pistol_cooldown > 25:
                pistol_cooldown = 0
                if pistol_bullets > 0:
                    pistol_bullets -= 1
                    screen.blit(pygame.transform.flip(pistol_f_texture, not direction, False), (
                        player_rect.right-offset_pi - scroll[0], player_rect.y - scroll[1]+14))
                    bullet = Bullet(
                        [player_rect.x, player_rect.y+20], direction, 50)
                    hit = bullet.shoot(tile_rects)
                    del hit, bullet
                    Audio.playSound(pistol_shot)
            else:
                screen.blit(pygame.transform.flip(pistol_texture, not direction, False), (
                    player_rect.right-offset_pi - scroll[0], player_rect.y - scroll[1]+14))
        elif player_hand_item == "rk62":
            if mouseLeftPressed and rk_62_ammo > 0 and rk62_cooldown > 4:
                rk_62_ammo -= 1
                rk62_cooldown = 0
                screen.blit(pygame.transform.flip(rk62_f_texture, direction, False), (
                    player_rect.right-offset_rk - scroll[0], player_rect.y - scroll[1]+14))
                bullet = Bullet(
                    [player_rect.x, player_rect.y+20], direction, 25)
                hit = bullet.shoot(tile_rects)
                KDS.Logging.Log(KDS.Logging.LogType.debug,
                                ("rk62 hit an object: " + str(hit)), False)
                del hit, bullet
                rk62_sound_cooldown += 1
                if rk62_sound_cooldown > 10:
                    rk62_sound_cooldown
                    rk62_shot.stop()
                    Audio.playSound(rk62_shot)

            else:
                if not mouseLeftPressed:
                    rk62_shot.stop()
                screen.blit(pygame.transform.flip(rk62_texture, direction, False), (
                    player_rect.right-offset_rk - scroll[0], player_rect.y - scroll[1]+14))
        elif player_hand_item == "shotgun":
            if not shotgun_loaded:
                shotgun_cooldown += 1
                if shotgun_cooldown > 60:
                    shotgun_loaded = True
            if weapon_fire and shotgun_shells > 0 and shotgun_loaded:
                shotgun_loaded = False
                shotgun_cooldown = 0
                shotgun_shells -= 1
                shotgun_thread = threading.Thread(target=shotgun_shots)
                shotgun_thread.start()
                Audio.playSound(player_shotgun_shot)
                screen.blit(pygame.transform.flip(shotgun_f, direction, False), (
                    player_rect.right-offset_p - scroll[0], player_rect.y - scroll[1]+14))

            else:
                screen.blit(pygame.transform.flip(shotgun, direction, False), (
                    player_rect.right-offset_p - scroll[0], player_rect.y - scroll[1]+14))

    if farting:
        fart_counter += 1
        if fart_counter > 250:
            farting = False
            fart_counter = 0

            damage_rect = pygame.Rect(0, 0, 800, 600)

            damage_rect.centerx = player_rect.centerx
            damage_rect.centery = player_rect.centery

            for archvile in archviles:
                if damage_rect.colliderect(archvile.rect):
                    archvile.health -= 600
            for zombie1 in zombies:
                if damage_rect.colliderect(zombie1.rect):
                    zombie1.health -= 600
            for sergeant in sergeants:
                if damage_rect.colliderect(sergeant.rect):
                    sergeant.health -= 600

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
        if FunctionKey:
            koponen_talk()
    else:
        koponen_movement[0] = koponen_movingx
    h = 0
#endregion
#region Interactable Objects
    for toilet in toilets:
        if toilet.colliderect(render_rect):
            if burning_toilets[h] == True:
                screen.blit(toilet_animation[burning_animation_stats[0]],
                            (toilet.x - scroll[0]+2, toilet.y - scroll[1]+1))
        h += 1
    h = 0
    for trashcan2 in trashcans:
        if trashcan2.colliderect(render_rect):
            if burning_trashcans[h] == True:
                screen.blit(trashcan_animation[burning_animation_stats[0]],
                            (trashcan2.x - scroll[0]+3, trashcan2.y - scroll[1]+6))
        h += 1

    screen.blit(koponen_animation[koponen_animation_stats[0]], (
        koponen_rect.x - scroll[0], koponen_rect.y - scroll[1]))

    if player_health or player_death_event:
        if DebugMode:
            pygame.draw.rect(screen, (0, 255, 0), (player_rect.x - scroll[0], player_rect.y - scroll[1], player_rect.width, player_rect.height))
        screen.blit(pygame.transform.flip(animation[animation_image], direction, False), (
            int(player_rect.topleft[0] - scroll[0] + ((player_rect.width - animation[animation_image].get_width()) / 2)), int(player_rect.bottomleft[1] - scroll[1] - animation[animation_image].get_height())))
    else:
        screen.blit(pygame.transform.flip(player_corpse, direction, False), (
            player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for archvile in archviles:
        if archvile.attack_anim:
            screen.blit(flames_animation.update(),
                        (player_rect.x - scroll[0], player_rect.y - scroll[1]-20))

    for iron_bar1 in iron_bars:
        screen.blit(iron_bar, (iron_bar1.x - scroll[0], iron_bar1.y - scroll[1]))

    jukebox_collision = False

    for jukebox in jukeboxes:
        if player_rect.colliderect(jukebox):
            screen.blit(jukebox_tip, (jukebox.x - scroll[0]-20, jukebox.y - scroll[1]-30))
            jukebox_collision = True

    if jukebox_collision:
        if FunctionKey:
            pygame.mixer.music.stop()
            for x in range(len(jukebox_music)):
                jukebox_music[x].stop()
            while jukeboxMusicPlaying == lastJukeboxSong[0] or jukeboxMusicPlaying == lastJukeboxSong[1] or jukeboxMusicPlaying == lastJukeboxSong[2] or jukeboxMusicPlaying == lastJukeboxSong[3] or jukeboxMusicPlaying == lastJukeboxSong[4]:
                jukeboxMusicPlaying = int(
                    random.uniform(0, len(jukebox_music)))
            for i in range(len(lastJukeboxSong) - 1):
                lastJukeboxSong[i] = lastJukeboxSong[i + 1]
            lastJukeboxSong[4] = jukeboxMusicPlaying
            Audio.MusicChannel2.play(jukebox_music[jukeboxMusicPlaying])
            Audio.MusicChannel2.set_volume(music_volume)
    else:
        if not pygame.mixer.music.get_busy():
            Audio.MusicChannel2.stop()
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(music_volume)
#endregion
#region Debug Mode
    screen.blit(score, (10, 55))
    if DebugMode:
        screen.blit(score_font.render("FPS: " + str(int(round(clock.get_fps()))), True, KDS.Colors.GetPrimary.White), (10, 10))
        screen.blit(score_font.render("Total Monsters: " + str(monstersLeft) + "/" + str(monsterAmount), True, KDS.Colors.GetPrimary.White), (10, 20))
#endregion
#region UI Rendering
    for i in range(len(inventory)):
        if inventory[i] != "none":
            if inventory[i] == "gasburner":
                screen.blit(gasburner_off, ((i * 34) + 17, 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "knife":
                screen.blit(knife, ((i * 34) + 15, 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "coffeemug":
                screen.blit(coffeemug, ((i * 34) + 17, 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "ss_bonuscard":
                screen.blit(ss_bonuscard, ((i * 34) + 12, 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "lappi_sytytyspalat":
                screen.blit(lappi_sytytyspalat, ((i * 34) + 15, 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "pistol":
                screen.blit(pistol_texture, ((i * 34) + 10 +
                                             (34 / pistol_texture.get_width() * 2) - 30, 80))
            elif inventory[i] == "iPuhelin":
                screen.blit(iphone_texture, (int((i * 34) + 10 +
                                             (34 / iphone_texture.get_width() * 2)), 80))
                inventoryDoubles[i] = False
            elif inventory[i] == "plasmarifle":
                screen.blit(plasmarifle, ((i * 34) + 15, 80))
                inventoryDoubles[i] = True  # True, koska vie kaksi slottia
            elif inventory[i] == "rk62":
                # Yksi 34 vaihdetaan 68, koska kyseinen esine vie kaksi paikkaa.
                screen.blit(rk62_texture, ((i * 34) + 20 +
                                           (68 / rk62_texture.get_width() * 2), 80))
                inventoryDoubles[i] = True  # True, koska vie kaksi slottia
            elif inventory[i] == "shotgun":
                # Yksi 34 vaihdetaan 68, koska kyseinen esine vie kaksi paikkaa.
                screen.blit(shotgun, (int((i * 34) + 20 +
                                      (68 / shotgun.get_width() * 2)), 80))
                inventoryDoubles[i] = True  # True, koska vie kaksi slottia

    for double in inventoryDoubles:
        if double:
            doubleWidthAdd += 1

    pygame.draw.rect(screen, (192, 192, 192), (10, 75, 170, 34), 3)

    if inventoryDoubles[inventory_slot] == True:
        scaledSlotWidth = 68
    else:
        scaledSlotWidth = 34
    inventoryDoubleOffsetCounter()
    pygame.draw.rect(screen, (70, 70, 70), ((
        (inventory_slot + inventoryDoubleOffset) * 34) + 10, 75, scaledSlotWidth, 34), 3)

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
    main_display.fill(KDS.Colors.GetPrimary.Black)
    main_display.blit(pygame.transform.scale(screen, FullscreenGet.size), (int(FullscreenGet.offset[0]), int(FullscreenGet.offset[1])))
    pygame.display.update()
#endregion
#region Data Update
    animation_counter += 1
    if player_hand_item == "gasburner":
        gasburner_animation_stats[2] += 1
    elif player_hand_item == "knife":
        knife_animation_stats[2] += 1
    FunctionKey = False
    weapon_fire = False
    burning_animation_stats[2] += 1
    koponen_animation_stats[2] += 1
    plasmarifle_cooldown += 1
    rk62_cooldown += 1
    for sergeant in sergeants:
        sergeant.hitscanner_cooldown += 1
    if KDS.Missions.GetFinished() == True:
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Campaign:
            level_finished_menu()
#endregion
#region Conditional Events
    if esc_menu:
        Audio.MusicChannel1.fadeout(500)
        Audio.MusicChannel2.fadeout(500)
        pygame.mixer.music.fadeout(500)
        screen.blit(black_tint, (0, 0))
        main_display.fill(KDS.Colors.GetPrimary.Black)
        main_display.blit(pygame.transform.scale(screen, FullscreenGet.size), (int(FullscreenGet.offset[0]), int(FullscreenGet.offset[1])))
        esc_menu_background = main_display.copy()
        pygame.mouse.set_visible(True)
        esc_menu_f()
        pygame.mouse.set_visible(False)
        pygame.mixer.music.play()
    if go_to_main_menu:
        Audio.MusicChannel1.stop()
        Audio.MusicChannel2.stop()
        pygame.mixer.music.stop()
        pygame.mouse.set_visible(True)
        main_menu()
#endregion
#region Ticks
    tick += 1
    if tick > 60:
        tick = 0
    clock.tick(60)
#endregion
#endregion
pygame.display.quit()
pygame.quit()