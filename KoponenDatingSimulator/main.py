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
import pygame
import os
import random
import threading
from datetime import datetime
from pygame.locals import *
from PIL import Image
#endregion
#region PyGame Initialisation
pygame.init()
KDS.Logging.init()

KDS.ConfigManager.SetSetting("Settings", "DisplaySizeX", str(1200))
KDS.ConfigManager.SetSetting("Settings", "DisplaySizeY", str(800))
KDS.ConfigManager.SetSetting("Settings", "ScreenSizeX", str(600))
KDS.ConfigManager.SetSetting("Settings", "ScreenSizeY", str(400))

display_size = (int(KDS.ConfigManager.LoadSetting("Settings", "DisplaySizeX", str(
    1200))), int(KDS.ConfigManager.LoadSetting("Settings", "DisplaySizeY", str(800))))
screen_size = (int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeX", str(
    600))), int(KDS.ConfigManager.LoadSetting("Settings", "ScreenSizeY", str(400))))

pygame.mouse.set_cursor(*pygame.cursors.arrow)

main_display = pygame.display.set_mode(display_size)
screen = pygame.Surface(screen_size)
#endregion
#region Text Handling
class pygame_print_text:

    def __init__(self, color, topleft, width, display):
        self.text_font = pygame.font.Font("courier.ttf", 30, bold=0, italic=0)
        self.display_to_blit = display
        self.color = tuple(color)
        self.topleft = tuple(topleft)
        self.width = width

        self.row = 0
        self.row_height = 30

    def print_text(self, text):
        self.screen_text = self.text_font.render(text, True, self.color)
        self.display_to_blit.blit(
            self.screen_text, (self.topleft[0], self.topleft[1]+self.row))
        self.row += self.row_height

    def resetRow(self):
        self.row = 0

    def skipRow(self):
        self.row += self.row_height
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
                plasma_hitting.play()
        for zombie1 in zombies:
            if self.rect.colliderect(zombie1) == True and zombie1.playDeathAnimation == True:
                self.done = True
                zombie1.health -= 10
                plasma_hitting.play()

        for sergeant in sergeants:
            if self.rect.colliderect(sergeant) and sergeant.playDeathAnimation:
                self.done = True
                sergeant.health -= 12
                plasma_hitting.play()

        self.display.blit(
            plasma_ammo, (self.rect.x-scroll[0], self.rect.y-scroll[1]))

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
class Archvile:

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
                        archvile_attack.play()
                    self.attack_anim = True
                self.counter = 0
            else:
                self.attacking = "null"

            if not self.attack_anim:
                self.rect, self.hits = move(
                    self.rect, self.movement, tile_rects)
                if self.hits["right"] or self.hits["left"]:
                    self.movement[0] = -self.movement[0]

                if self.movement[0] > 0:
                    self.direction = True
                elif self.movement[0] < 0:
                    self.direction = False

                screen.blit(pygame.transform.flip(a_run, not self.direction,
                                                  False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))

            else:
                i, u = arhcvile_attack_animation.update()
                if u:
                    f = hit_scan(self)

                    if f != "wall" and player_rect.y-40 < archvile.rect.y:
                        player_health -= int(random.uniform(30, 80))
                        landmine_explosion.play()

                    del f

                    arhcvile_attack_animation.reset()
                    self.attack_anim = False
                screen.blit(pygame.transform.flip(
                    i, not self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))

        elif self.playDeathAnimation:
            self.attacking = "null"
            self.attack_anim = False
            if self.playDeathSound:
                self.playDeathSound = False
                archvile_death.play()
            l, p = archvile_death_animation.update()
            if not p:
                screen.blit(pygame.transform.flip(l, not self.direction, False),
                            (self.rect.x-scroll[0], self.rect.y-scroll[1]+15))

            if p:
                self.playDeathAnimation = False

        else:
            screen.blit(pygame.transform.flip(archvile_corpse, not self.direction,
                                              False), (self.rect.x-scroll[0], self.rect.y-scroll[1]+25))
#endregion
#region Fullscreen
def setFullscreen(reverseFullscreen):
    global fullscreen_var, main_display
    if reverseFullscreen:
        fullscreen_var = not fullscreen_var
    if fullscreen_var:
        main_display = pygame.display.set_mode(display_size)
        fullscreen_var = False
    else:
        main_display = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        fullscreen_var = True
    KDS.ConfigManager.SetSetting("Settings", "Fullscreen", str(fullscreen_var))
#endregion
#region Initialisation
printer = pygame_print_text((7, 8, 10), (50, 50), 680, main_display)

esc_menu_surface = pygame.Surface((500, 400))
alpha = pygame.Surface(screen_size)
alpha.fill((0, 0, 0))
alpha.set_alpha(170)

#region Downloads
pygame.display.set_caption("Koponen Dating Simulator")
game_icon = pygame.image.load("Assets/Textures/Game_Icon.png")
main_menu_background = pygame.image.load(
    "Assets/Textures/UI/Menus/main_menu_bc.png")
settings_background = pygame.image.load("Assets/Textures/UI/Menus/settings_bc.png")
agr_background = pygame.image.load("Assets/Textures/UI/Menus/tcagr_bc.png")
pygame.display.set_icon(game_icon)
clock = pygame.time.Clock()

score_font = pygame.font.Font("gamefont.ttf", 10, bold=0, italic=0)
tip_font = pygame.font.Font("gamefont2.ttf", 10, bold=0, italic=0)
button_font = pygame.font.Font("gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("gamefont2.ttf", 52, bold=0, italic=0)

player_img = pygame.image.load("Assets/Textures/Player/stand0.png").convert()
player_corpse = pygame.image.load("Assets/Textures/Player/corpse.png").convert()
player_corpse.set_colorkey((255, 255, 255))
player_img.set_colorkey((255, 255, 255))

floor1 = pygame.image.load("Assets/Textures/Building/floor0v2.png")
concrete1 = pygame.image.load("Assets/Textures/Building/concrete0.png")
wall1 = pygame.image.load("Assets/Textures/Building/wall0.png")
table1 = pygame.image.load("Assets/Textures/Building/table0.png").convert()
toilet1 = pygame.image.load("Assets/Textures/Building/toilet0.png").convert()
lamp1 = pygame.image.load("Assets/Textures/Building/lamp0.png").convert()
trashcan = pygame.image.load("Assets/Textures/Building/trashcan.png").convert()
ground1 = pygame.image.load("Assets/Textures/Building/ground0.png")
grass = pygame.image.load("Assets/Textures/Building/grass0.png")
door_closed = pygame.image.load("Assets/Textures/Building/door_closed.png").convert()
red_door_closed = pygame.image.load(
    "Assets/Textures/Building/red_door_closed.png").convert()
green_door_closed = pygame.image.load(
    "Assets/Textures/Building/green_door_closed.png").convert()
blue_door_closed = pygame.image.load(
    "Assets/Textures/Building/blue_door_closed.png").convert()
door_open = pygame.image.load("Assets/Textures/Building/door_open2.png")
bricks = pygame.image.load("Assets/Textures/Building/bricks.png")
tree = pygame.image.load("Assets/Textures/Building/tree.png")
planks = pygame.image.load("Assets/Textures/Building/planks.png")
jukebox_texture = pygame.image.load("Assets/Textures/Building/jukebox.png")
landmine_texture = pygame.image.load("Assets/Textures/Building/landmine.png")
ladder_texture = pygame.image.load("Assets/Textures/Building/ladder.png")
table1.set_colorkey((255, 255, 255))
toilet1.set_colorkey((255, 255, 255))
lamp1.set_colorkey((255, 255, 255))
trashcan.set_colorkey((255, 255, 255))
door_closed.set_colorkey((255, 255, 255))
red_door_closed.set_colorkey((255, 255, 255))
green_door_closed.set_colorkey((255, 255, 255))
blue_door_closed.set_colorkey((255, 255, 255))
jukebox_texture.set_colorkey((255, 255, 255))
landmine_texture.set_colorkey((255, 255, 255))
ladder_texture.set_colorkey((255, 255, 255))
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
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_1.png"))
gamemode_bc_2_1 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_1.png"))
gamemode_bc_2_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_2_2.png"))
gamemode_bc_1_2 = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Menus", "Gamemode_bc_1_2.png"))
arrow_button = pygame.image.load(
    os.path.join("Assets", "Textures", "UI", "Buttons", "Arrow.png"))

gasburner_off.set_colorkey((255, 255, 255))
knife.set_colorkey((255, 255, 255))
knife_blood.set_colorkey((255, 255, 255))
red_key.set_colorkey((255, 255, 255))
green_key.set_colorkey((255, 255, 255))
blue_key.set_colorkey((255, 255, 255))
coffeemug.set_colorkey((255, 255, 255))
ss_bonuscard.set_colorkey((255, 0, 0))
lappi_sytytyspalat.set_colorkey((255, 255, 255))
plasmarifle.set_colorkey((255, 255, 255))
plasma_ammo.set_colorkey((255, 255, 255))
cell.set_colorkey((255, 255, 255))
zombie_corpse.set_colorkey((255, 255, 255))
pistol_texture.set_colorkey((255, 255, 255))
pistol_f_texture.set_colorkey((255, 255, 255))
pistol_mag.set_colorkey((255, 255, 255))
rk62_texture.set_colorkey((255, 255, 255))
rk62_f_texture.set_colorkey((255, 255, 255))
rk62_mag.set_colorkey((255, 255, 255))
sergeant_corpse.set_colorkey((255, 255, 255))
sergeant_aiming.set_colorkey((255, 255, 255))
sergeant_firing.set_colorkey((255, 255, 255))
medkit.set_colorkey((255, 255, 255))
shotgun.set_colorkey((255, 255, 255))
shotgun_f.set_colorkey((255, 255, 255))
shotgun_shells_t.set_colorkey((255, 255, 255))
archvile_corpse.set_colorkey((255, 255, 255))
iphone_texture.set_colorkey((255, 255, 255))

Items_list = ["iPuhelin", "coffeemug"]
Items = {"iPuhelin": iphone_texture, "coffeemug": coffeemug}

text_icon = pygame.image.load("Assets/Textures/Text_Icon.png").convert()
text_icon.set_colorkey((255, 255, 255))

gasburner_clip = pygame.mixer.Sound("Assets/Audio/misc/gasburner_clip.wav")
gasburner_fire = pygame.mixer.Sound("Assets/Audio/misc/gasburner_fire.wav")
door_opening = pygame.mixer.Sound("Assets/Audio/misc/door.wav")
player_death_sound = pygame.mixer.Sound("Assets/Audio/misc/dspldeth.wav")
player_walking = pygame.mixer.Sound("Assets/Audio/misc/walking.wav")
coffeemug_sound = pygame.mixer.Sound("Assets/Audio/misc/coffeemug.wav")
knife_pickup = pygame.mixer.Sound("Assets/Audio/misc/knife.wav")
key_pickup = pygame.mixer.Sound("Assets/Audio/misc/pickup_key.wav")
ss_sound = pygame.mixer.Sound("Assets/Audio/misc/ss.wav")
lappi_sytytyspalat_sound = pygame.mixer.Sound("Assets/Audio/misc/sytytyspalat.wav")
landmine_explosion = pygame.mixer.Sound("Assets/Audio/misc/landmine.wav")
hurt_sound = pygame.mixer.Sound("Assets/Audio/misc/dsplpain.wav")
plasmarifle_f_sound = pygame.mixer.Sound("Assets/Audio/misc/dsplasma.wav")
weapon_pickup = pygame.mixer.Sound("Assets/Audio/misc/weapon_pickup.wav")
item_pickup = pygame.mixer.Sound("Assets/Audio/misc/dsitemup.wav")
plasma_hitting = pygame.mixer.Sound("Assets/Audio/misc/dsfirxpl.wav")
pistol_shot = pygame.mixer.Sound("Assets/Audio/misc/pistolshot.wav")
rk62_shot = pygame.mixer.Sound("Assets/Audio/misc/rk62_shot.wav")
shotgun_shot = pygame.mixer.Sound("Assets/Audio/misc/shotgun.wav")
player_shotgun_shot = pygame.mixer.Sound("Assets/Audio/misc/player_shotgun.wav")
archvile_attack = pygame.mixer.Sound("Assets/Audio/misc/dsflame.wav")
archvile_death = pygame.mixer.Sound("Assets/Audio/misc/dsvildth.wav")
fart = pygame.mixer.Sound("Assets/Audio/misc/fart_attack.wav")

plasmarifle_f_sound.set_volume(0.05)
hurt_sound.set_volume(0.6)
plasma_hitting.set_volume(0.03)
rk62_shot.set_volume(0.9)
shotgun_shot.set_volume(0.9)
player_shotgun_shot.set_volume(0.8)

jukebox_tip = tip_font.render("Use jukebox [E]", True, (255, 255, 255))
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
pistolFire = False
fullscreen_var = False
shoot = False

tcagr = KDS.Convert.ToBool(KDS.ConfigManager.LoadSetting(
    "Data", "TermsAccepted", str(False)))

if tcagr == None:
    KDS.Logging.Log(KDS.Logging.LogType.error,
                    "Error parcing terms and conditions bool.", False)
    tcagr = False

volume_data = int(KDS.ConfigManager.LoadSetting("Settings", "Volume", str(15)))

fullscreen_var = KDS.Convert.ToBool(
    KDS.ConfigManager.LoadSetting("Settings", "Fullscreen", str(False)))

if fullscreen_var == None:
    KDS.Logging.Log(KDS.Logging.LogType.error,
                    "Error parcing fullscreen bool.", False)
setFullscreen(True)
KDS.Logging.Log(KDS.Logging.LogType.debug, "Settings Loaded:\n- Terms Accepted: " +
                str(tcagr) + "\n- Volume: " + str(volume_data) + "\n- Fullscreen: " + str(fullscreen_var), False)

selectedSave = 0

volume = float(volume_data) / 100
gasburner_animation_stats = [0, 4, 0]
knife_animation_stats = [0, 10, 0]
toilet_animation_stats = [0, 5, 0]
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
KeyW = False
KeyS = False
mouseLeftPressed = False
shotgun_loaded = True
shotgun_cooldown = 0
pistol_cooldown = 0

gamemode_bc_1_alpha = KDS.Animator.Lerp(0.0, 1.0, 8)
gamemode_bc_2_alpha = KDS.Animator.Lerp(0.0, 1.0, 8)

go_to_main_menu = False

main_menu_running = False
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
attack_counter = 0
fart_counter = 0
farting = False

current_map = KDS.ConfigManager.LoadSetting("Settings", "CurrentMap", "02")
max_map = int(KDS.ConfigManager.LoadSetting("Settings", "MaxMap", "02"))
map_names = (
    "Placeholder",
    "Beginnings...",
    "More Monsters"
)

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
player_rect = pygame.Rect(100, 100, 28, 65)
koponen_rect = pygame.Rect(200, 200, 24, 64)
koponen_recog_rec = pygame.Rect(0, 0, 72, 64)
koponen_movement = [0, 6]
koponen_movingx = 0
koponen_happines = 40

koponen_talk_tip = tip_font.render("Puhu Koposelle [E]", True, (255, 255, 255))

task = ""
taskTaivutettu = ""

DebugMode = False

MenuMode = 0
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
    pygame.display.quit()
    pygame.quit()
    exit()
#endregion
#region World Generation
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
def WorldGeneration():
    global world_gen, item_gen, tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs, item_rects, item_ids, task_items, door_rects, doors_open, color_keys
    buildingBitmap = Image.open(os.path.join("Assets", "Maps", "map" + current_map, "map_buildings.map"))
    decorationBitmap = Image.open(os.path.join("Assets", "Maps", "map" + current_map, "map_decorations.map"))
    enemyBitmap = Image.open(os.path.join("Assets", "Maps", "map" + current_map, "map_enemies.map"))
    itemBitmap = Image.open(os.path.join("Assets", "Maps", "map" + current_map, "map_items.map"))

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
        rowSplit = raw.split('\n')

        array = rowSplit[0].split(',')
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
                elif Type == 1:
                    convertDecorationRules.append(array[1])
                    convertDecorationColors.append((int(array[2]), int(array[3]), int(array[4])))
                elif Type == 2:
                    convertEnemyRules.append(array[1])
                    convertEnemyColors.append((int(array[2]), int(array[3]), int(array[4])))
                elif Type == 3:
                    convertItemRules.append(array[1])
                    convertItemColors.append((int(array[2]), int(array[3]), int(array[4])))

    building_gen = list()
    decoration_gen = list()
    enemy_gen = list()
    item_gen = list()

    BitmapSize = buildingBitmap.size
    progress = 1
    progressMax = BitmapSize[0] * BitmapSize[1]
    for i in range(BitmapSize[1]):
        building_layer = list()
        decoration_layer = list()
        enemy_layer = list()
        item_layer = list()
        for j in range(BitmapSize[0]):
            building_layer.append(convertBuildingRules[convertBuildingColors.index(buildingBitmap.getpixel((j, i))[:3])])
            decoration_layer.append(convertDecorationRules[convertDecorationColors.index(decorationBitmap.getpixel((j, i))[:3])])
            enemy_layer.append(convertEnemyRules[convertEnemyColors.index(enemyBitmap.getpixel((j, i))[:3])])
            item_layer.append(convertItemRules[convertItemColors.index(itemBitmap.getpixel((j, i))[:3])])
        
        building_gen.append(building_layer)
        decoration_gen.append(decoration_layer)
        enemy_gen.append(enemy_layer)
        item_gen.append(item_layer)


    world_gen = (building_gen, decoration_gen, enemy_gen, item_gen)

    #Use the index to get the letter and make the file using the letters

    tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs = load_rects()
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
    musikerna = os.listdir("Assets/Audio/jukebox_music/")
    musics = []

    for musiken in musikerna:
        musics.append(pygame.mixer.Sound("Assets/Audio/jukebox_music/" + musiken))

    random.shuffle(musics)

    return musics
def shakeScreen():
    scroll[0] += random.randint(-10, 10)
    scroll[1] += random.randint(-10, 10)
def load_music():
    original_path = os.getcwd()
    os.chdir("Assets/Audio/music/")
    music_files = os.listdir()

    random.shuffle(music_files)
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Music Files Initialised: " + str(len(music_files)), False)
    for track in music_files:
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        "Initialised Music File: " + track, False)

    pygame.mixer.music.stop()

    pygame.mixer.music.load(music_files[0])

    pos = 0
    for track in music_files:
        if pos:
            pygame.mixer.music.queue(track)
        pos += 1

    os.chdir(original_path)
    del original_path
    del pos
def load_music_for_map(_current_map):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join("Assets", "Maps", "map" + _current_map, "music.mid"))
def load_ads():
    ad_files = os.listdir("Assets/Textures/KoponenTalk/ads")

    random.shuffle(ad_files)
    KDS.Logging.Log(KDS.Logging.LogType.debug,
                    "Ad Files Initialised: " + str(len(ad_files)), False)
    for ad in ad_files:
        KDS.Logging.Log(KDS.Logging.LogType.debug,
                        "Initialised Ad File: " + ad, False)

    ad_images = []

    for ad in ad_files:
        path = str("Assets/Textures/KoponenTalk/ads/" + ad)
        ad_images.append(pygame.image.load(path))

    return ad_images
ad_images = load_ads()
koponen_talking_background = pygame.image.load("Assets/Textures/KoponenTalk/background.png")
koponen_talking_foreground_indexes = [0, 0, 0, 0, 0]
def load_rects():
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
                        w = list(toilet1.get_size())
                        toilets.append(pygame.Rect(x * 34-2, y * 34, 34, 34))
                        burning_toilets.append(False)
                        tile_rects.append(pygame.Rect(x * 34, y * 34, w[0], w[1]))
                    elif tile == 'g':
                        w = list(trashcan.get_size())
                        trashcans.append(pygame.Rect(x * 34-1, y * 34, w[0]+2, w[1]))
                        burning_trashcans.append(False)
                        tile_rects.append(pygame.Rect(x * 34, y * 34+8, w[0], w[1]))
                    elif tile == 'q':
                        ladders.append(pygame.Rect(x * 34, y * 34, 34, 34))
                    elif tile == 'k':
                        pass
                    elif tile == 'l':
                        pass
                    elif tile == 'm':
                        pass
                    elif tile == 'n':
                        pass
                    elif tile == 'A':
                        pass
                    elif tile == 'B':
                        jukeboxes.append(pygame.Rect(x * 34, y * 34 - 26, 42, 60))
                    elif tile == 'C':
                        landmines.append(pygame.Rect(x * 34+6, y * 34+23, 22, 11))
                    elif tile == 'Z':
                        zombies.append(KDS.AI.Zombie((x * 34, y * 34 - 34), 100, 1))
                    elif tile == 'S':
                        sergeants.append(KDS.AI.SergeantZombie(
                            (x * 34, y * 34 - 34), 220, 1))
                    elif tile == 'V':
                        archviles.append(Archvile((x * 34, y * 34-51), 750, 2))
                    elif tile == 'K':
                        bulldogs.append(KDS.AI.Bulldog((x * 34, y * 34), 80, 3, bulldog_run_animation))
                    else:
                        tile_rects.append(pygame.Rect(x * 34, y * 34, 34, 34))

                x += 1
            y += 1
    return tile_rects, toilets, burning_toilets, trashcans, burning_trashcans, jukeboxes, landmines, zombies, sergeants, archviles, ladders, bulldogs
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
#tile_rects, toilets, burning_toilets, trashcans, burning_trashcans = load_rects()
#item_rects, item_ids = load_item_rects()
#door_rects, doors_open, color_keys = load_doors()
def load_animation(name, number_of_images):
    animation_list = []
    for i in range(number_of_images):
        path = "Assets/Textures/Player/" + name + str(i) + ".png"
        img = pygame.image.load(path).convert()
        img.set_colorkey((255, 255, 255))
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
    global player_hand_item, player_score, inventory, inventory_slot, item_ids, player_keys, item_rects, ammunition_plasma, pistol_bullets, rk_62_ammo, player_health, shotgun_shells

    def s(score):
        global player_score

        player_score += score

    itemTipVisible = False
    for item in items:
        if rect.colliderect(item):
            hit_list.append(item)
            if not itemTipVisible:
                itemTip = tip_font.render(
                    "Nosta Esine Painamalla [E]", True, (255, 255, 255))
                screen.blit(
                    itemTip, (item.x - scroll[0] - 60, item.y - scroll[1] - 10))
                itemTipVisible = True
            if FunctionKey == True:
                i = item_ids[x]

                if inventory[inventory_slot] == "none":
                    if i == "gasburner":
                        inventory[inventory_slot] = "gasburner"
                        gasburner_clip.play()
                        item_rects.remove(item)
                        del item_ids[x]

                        s(5)
                    elif i == "knife":
                        inventory[inventory_slot] = "knife"
                        knife_pickup.play()
                        item_rects.remove(item)
                        del item_ids[x]
                        s(5)
                    elif i == "plasmarifle":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "plasmarifle"
                            weapon_pickup.play()
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "ss_bonuscard":
                        inventory[inventory_slot] = "ss_bonuscard"
                        ss_sound.play()
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "coffeemug":
                        inventory[inventory_slot] = "coffeemug"
                        coffeemug_sound.play()
                        item_rects.remove(item)
                        del item_ids[x]
                        s(3)
                    elif i == "lappi_sytytyspalat":
                        inventory[inventory_slot] = "lappi_sytytyspalat"
                        lappi_sytytyspalat_sound.play()
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "pistol":
                        inventory[inventory_slot] = "pistol"
                        weapon_pickup.play()
                        item_rects.remove(item)
                        del item_ids[x]
                        s(20)
                    elif i == "rk62":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "rk62"
                            weapon_pickup.play()
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "shotgun":
                        if inventory_slot != len(inventory) - 1:
                            inventory[inventory_slot] = "shotgun"
                            weapon_pickup.play()
                            item_rects.remove(item)
                            del item_ids[x]
                            s(20)
                    elif i == "iPuhelin":
                        inventory[inventory_slot] = "iPuhelin"
                        item_rects.remove(item)
                        del item_ids[x]

                if i == "red_key":
                    player_keys["red"] = True
                    key_pickup.play()
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "green_key":
                    player_keys["green"] = True
                    key_pickup.play()
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "blue_key":
                    player_keys["blue"] = True
                    key_pickup.play()
                    item_rects.remove(item)
                    del item_ids[x]
                elif i == "cell":
                    ammunition_plasma += 30
                    item_rects.remove(item)
                    item_pickup.play()
                    del item_ids[x]
                elif i == "pistol_mag":
                    pistol_bullets += 8
                    item_rects.remove(item)
                    item_pickup.play()
                    del item_ids[x]
                elif i == "rk62_mag":
                    rk_62_ammo += 30
                    item_rects.remove(item)
                    item_pickup.play()
                    del item_ids[x]
                elif i == "shotgun_shells":
                    shotgun_shells += 4
                    item_rects.remove(item)
                    item_pickup.play()
                    del item_ids[x]
                elif i == "medkit":
                    if player_health < 100:
                        player_health += 25
                        if player_health > 100:
                            player_health = 100
                    item_rects.remove(item)
                    item_pickup.play()
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
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False,
                       'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += int(movement[1])
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

stand_animation = load_animation("stand", 2)
run_animation = load_animation("run", 2)
gasburner_animation = load_animation("gasburner_on", 2)
knife_animation = load_animation("knife", 2)
toilet_animation = load_animation("toilet_anim", 3)
trashcan_animation = load_animation("trashcan", 3)
koponen_stand = load_animation("koponen_standing", 2)
koponen_run = load_animation("koponen_running", 2)
death_animation = load_animation("death", 5)
menu_gasburner_animation = KDS.Animator.Animation(
    "main_menu_bc_gasburner", 2, 5, (255, 255, 255), -1)
burning_tree = KDS.Animator.Animation("tree_burning", 4, 5, (0, 0, 0), -1)
explosion_animation = KDS.Animator.Animation(
    "explosion", 7, 5, (255, 255, 255), 1)
plasmarifle_animation = KDS.Animator.Animation(
    "plasmarifle_firing", 2, 3, (255, 255, 255), -1)
zombie_death_animation = KDS.Animator.Animation(
    "z_death", 5, 6, (255, 255, 255), 1)
zombie_walk_animation = KDS.Animator.Animation(
    "z_walk", 3, 10, (255, 255, 255), -1)
zombie_attack_animation = KDS.Animator.Animation(
    "z_attack", 4, 10, (255, 255, 255), -1)
sergeant_walk_animation = KDS.Animator.Animation(
    "seargeant_walking", 4, 8, (255, 255, 255), -1)
sergeant_shoot_animation = KDS.Animator.Animation(
    "seargeant_shooting", 2, 6, (255, 255, 255), 1)

archvile_run_animation = KDS.Animator.Animation(
    "archvile_run", 3, 9, (255, 255, 255), -1)
arhcvile_attack_animation = KDS.Animator.Animation(
    "archvile_attack", 6, 16, (255, 255, 255), 1)
archvile_death_animation = KDS.Animator.Animation(
    "archvile_death", 7, 12, (255, 255, 255), 1)
flames_animation = KDS.Animator.Animation("flames", 5, 3, (255, 255, 255), -1)
bulldog_run_animation = KDS.Animator.Animation("bulldog", 5, 6,(255,255,255),-1)
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
    "seargeant_dying", 5, 8, (255, 255, 255), 1)
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

    if tcagr == False:
        tcagr_running = True
    else:
        tcagr_running = False

    global main_running
    c = False

    buttons = []
    texts = []
    functions = []

    def agree():
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Terms and Conditions have been accepted.", False)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "You said you will not get offended... Dick!", False)
        KDS.ConfigManager.SetSetting("Data", "TermsAccepted", "True")
        KDS.Logging.Log(KDS.Logging.LogType.debug, "Terms Agreed. Updated Value: " +
                        KDS.ConfigManager.LoadSetting("Data", "TermsAccepted", "False"), False)
        return False

    buttons.append(pygame.Rect(249, 353, 200, 160))
    texts.append(button_font1.render("I Agree", True, (255, 255, 255)))
    functions.append(agree)

    while tcagr_running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    setFullscreen(False)
                if event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                if event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    c = True
            if event.type == pygame.QUIT:
                KDS_Quit()
        main_display.blit(agr_background, (0, 0))

        y = 0
        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    tcagr_running = functions[y]()
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90, 90, 90)
                else:
                    button_color = (115, 115, 115)
            else:
                button_color = (100, 100, 100)

            pygame.draw.rect(main_display, button_color, button)

            main_display.blit(texts[y], (button.x+10, button.y+5))
            y += 1

        pygame.display.update()
        c = False
#endregion
#region Koponen Talk
def koponen_talk():
    global main_running, inventory, currently_on_mission, inventory, player_score, ad_images, task_items, playerMovingLeft, playerMovingRight, playerSprinting, koponen_talking_background, koponen_talking_foreground_indexes

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

    exit_button = pygame.Rect(940, 700, 230, 80)
    mission_button = pygame.Rect(50, 700, 450, 80)
    date_button = pygame.Rect(50, 610, 450, 80)
    return_mission_button = pygame.Rect(510, 700, 420, 80)

    for i in range(len(koponen_talking_foreground_indexes), 0):
        koponen_talking_foreground_indexes[i] = koponen_talking_foreground_indexes[i - 1]
    random_foreground = int(random.uniform(0, len(ad_images)))
    while random_foreground == koponen_talking_foreground_indexes[0] or random_foreground == koponen_talking_foreground_indexes[1] or random_foreground == koponen_talking_foreground_indexes[2] or random_foreground == koponen_talking_foreground_indexes[3] or random_foreground == koponen_talking_foreground_indexes[4]:
        random_foreground = int(random.uniform(0, len(ad_images)))
    koponen_talking_foreground_indexes[4] = random_foreground
    koponen_talk_foreground = ad_images[random_foreground].copy()

    def renderText(text):
        text_object = button_font1.render(text, True, (255, 255, 255))
        return text_object

    exit_text = renderText("Exit")
    mission_text = renderText("Ask for mission")
    date_text = renderText("Ask for date")
    return_mission = renderText("Return mission")

    def exit_function1():
        return False

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
    buttons = []
    texts = []
    functions = []
    conversations = []

    buttons.append(exit_button)
    buttons.append(mission_button)
    buttons.append(date_button)
    buttons.append(return_mission_button)
    texts.append(exit_text)
    texts.append(mission_text)
    texts.append(date_text)
    texts.append(return_mission)
    functions.append(exit_function1)
    functions.append(mission_function)
    functions.append(date_function)
    functions.append(end_mission)

    conversations.append("Koponen: Hyvää päivää")

    while koponenTalking:

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponenTalking = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            if event.type == pygame.QUIT:
                KDS_Quit()
        main_display.blit(koponen_talking_background, (0, 0))
        main_display.blit(koponen_talk_foreground, (40, 474))
        pygame.draw.rect(main_display, (230, 230, 230), (40, 40, 700, 400))
        pygame.draw.rect(main_display, (30, 30, 30), (40, 40, 700, 400), 3)
        printer.resetRow()

        y = 0

        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    if not y:
                        koponenTalking = functions[y]()
                    else:
                        functions[y]()
                button_color = (115, 115, 115)

                if pygame.mouse.get_pressed()[0]:
                    button_color = (90, 90, 90)
            else:
                button_color = (100, 100, 100)

            if y == 0:
                text_offset = 60
            else:
                text_offset = 10

            pygame.draw.rect(main_display, button_color, button)
            main_display.blit(texts[y], (button.x+text_offset, button.y+14))
            y += 1
        if len(conversations) > 13:
            conversations.remove(conversations[0])
        for line in conversations:
            printer.print_text(line)
        c = False
        pygame.display.update()
    pygame.mouse.set_visible(False)
#endregion
#region Menus
def esc_menu_f():
    pygame.mouse.set_visible(True)
    global esc_menu, go_to_main_menu
    file = pygame.image.load("im314.png")
    c = False
    resume_button = pygame.Rect(150, 170, 200, 30)
    save_button = pygame.Rect(150, 210, 200, 30)
    settings_button = pygame.Rect(150, 250, 200, 30)
    main_menu_button = pygame.Rect(150, 290, 200, 30)

    resume_text = button_font.render("Resume", True, (255, 255, 255))
    save_text = button_font.render("Save", True, (255, 255, 255))
    settings_text = button_font.render("Settings", True, (255, 255, 255))
    main_menu_text = button_font.render("Main menu", True, (255, 255, 255))
    
    buttons = []
    functions = []
    texts = []

    texts.append(resume_text)
    texts.append(save_text)
    texts.append(settings_text)
    texts.append(main_menu_text)

    def resume():
        global esc_menu
        esc_menu = False
        pygame.mouse.set_visible(False)
        pygame.mixer.unpause()
        pygame.mixer.music.unpause()

    def save():
        SaveData()

    def settings():
        settings_menu()

    def goto_main_menu():
        global esc_menu, go_to_main_menu
        pygame.mixer.unpause()
        pygame.mixer.music.unpause()
        esc_menu = False
        go_to_main_menu = True

    functions.append(resume)
    functions.append(save)
    functions.append(settings)
    functions.append(goto_main_menu)

    buttons.append(resume_button)
    buttons.append(save_button)
    buttons.append(settings_button)
    buttons.append(main_menu_button)

    while esc_menu:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    esc_menu = False
                    pygame.mouse.set_visible(False)
                    pygame.mixer.music.unpause()
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            if event.type == pygame.QUIT:
                KDS_Quit()
        esc_menu_surface.fill((123, 134, 111))
        main_display.blit(file, (0, 0))
        esc_menu_surface.blit(pygame.transform.scale(
            text_icon, (250, 139)), (125, 10))
        point = list(pygame.mouse.get_pos())
        point[0] -= display_size[0] / 2 - 250
        point[1] -= 120
        y = 0
        for button in buttons:
            if button.collidepoint(int(point[0]), int(point[1])):
                if c:
                    functions[y]()
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90, 90, 90)
                else:
                    button_color = (115, 115, 115)
            else:
                button_color = (100, 100, 100)
            pygame.draw.rect(esc_menu_surface, button_color, button)
            if y == 0:
                x = 50
            elif y == 1:
                x = 40
            else:
                x = 30

            esc_menu_surface.blit(texts[y], (button.x+x, button.y+3))
            y += 1

        main_display.blit(esc_menu_surface,
                          (int(display_size[0]) / 2 - 250, 120))
        pygame.display.update()
        c = False

    del buttons, resume_button, settings_button, main_menu_button, c, resume, settings, goto_main_menu, functions, texts, resume_text, settings_text, main_menu_text

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, volume
    c = False
    settings_running = True

    return_button = pygame.Rect(465, 700, 270, 60)
    music_slider = pygame.Rect(560, 141, 30, 28)

    return_text = button_font1.render("Return", True, (255, 255, 255))

    def return_def():
        global settings_running
        settings_running = False

    buttons = []
    texts = []
    functions = []

    buttons.append(return_button)
    texts.append(return_text)
    functions.append(return_def)

    dragSlider = False

    while settings_running:

        volume_text = button_font1.render(
            "Music Volume", True, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    setFullscreen(False)
                if event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                if event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
                if event.key == K_ESCAPE:
                    settings_running = False
            if event.type == pygame.QUIT:
                KDS_Quit()

        main_display.blit(settings_background, (0, 0))

        main_display.blit(volume_text, (190, 130))
        pygame.draw.rect(main_display, (120, 120, 120), (560, 145, 340, 20))

        music_slider.x = int(560 + (volume * 100) * 3.4 - 15)

        if pygame.mouse.get_pressed()[0] == False:
            dragSlider = False

        if music_slider.collidepoint(pygame.mouse.get_pos()):
            slider_color = (115, 115, 115)
            if pygame.mouse.get_pressed()[0]:
                dragSlider = True
        if dragSlider:
            slider_color = (90, 90, 90)
            position = int(pygame.mouse.get_pos()[0])
            if position < 560:
                position = 560
            if position > 900:
                position = 900
            position -= 560
            position = int(position/3.4)
            KDS.ConfigManager.SetSetting("Settings", "Volume", str(position))
            volume = position/100
            pygame.mixer.music.set_volume(volume)
        else:
            slider_color = (100, 100, 100)

        pygame.draw.rect(main_display, (slider_color), music_slider)

        y = 0
        for button in buttons:

            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    functions[y]()
                    pass
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90, 90, 90)
                else:
                    button_color = (115, 115, 115)
            else:
                button_color = (100, 100, 100)

            pygame.draw.rect(main_display, button_color, button)
            main_display.blit(texts[y], (button.x+50, button.y+6))
            y += 1

        c = False
        pygame.display.update()

def main_menu():
    global current_map, MenuMode

    class Mode():
        MainMenu = 0
        ModeSelectionMenu = 1
        StoryMenu = 2
        CampaignMenu = 3
    MenuMode = Mode.MainMenu

    current_map_int = 0
    current_map_int = int(current_map)
    try:
        jukebox_music[jukeboxMusicPlaying].stop()
    except:
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Jukebox music has not been defined yet.", False)
    pygame.mixer.music.unpause()

    global main_menu_running, main_running, go_to_main_menu
    go_to_main_menu = False

    main_menu_running = True
    c = False

    pygame.mixer.music.load("Assets/Audio/lobbymusic.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(volume)

    play_button = pygame.Rect(450, 180, 300, 60)
    settings_button = pygame.Rect(450, 250, 300, 60)
    quit_button = pygame.Rect(450, 320, 300, 60)

    play_text = button_font1.render("PLAY", True, (255, 255, 255))
    settings_text = button_font1.render("SETTINGS", True, (255, 255, 255))
    quit_text = button_font1.render("QUIT", True, (255, 255, 255))

    def play_function(gamemode: KDS.Gamemode.Modes):
        global main_menu_running, current_map, inventory
        KDS.Gamemode.SetGamemode(gamemode, int(current_map))
        inventory = ["none", "none", "none", "none", "none"]
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story or int(current_map) < 2:
            inventory[0] = "iPuhelin"
        WorldGeneration()
        pygame.mouse.set_visible(False)
        main_menu_running = False
        #load_music()
        load_music_for_map(current_map)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(volume)
        global player_keys, player_hand_item
        player_hand_item = "none"

        player_rect.x = 100
        player_rect.y = 100
        for key in player_keys:
            player_keys[key] = False
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Press F4 to commit suicide", False)
        KDS.Logging.Log(KDS.Logging.LogType.info,
                        "Press Alt + F4 to get depression", False)
        LoadSave()

    def settings_function():
        settings_menu()

    class level_pick():
        class direction():
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

    main_menu_buttons = list()
    main_menu_functions = list()
    main_menu_texts = list()
    main_menu_buttons.append(play_button)
    main_menu_buttons.append(settings_button)
    main_menu_buttons.append(quit_button)
    main_menu_functions.append(mode_selection_function)
    main_menu_functions.append(settings_function)
    main_menu_functions.append(KDS_Quit)
    main_menu_texts.append(play_text)
    main_menu_texts.append(settings_text)
    main_menu_texts.append(quit_text)

    mode_selection_buttons = list()
    mode_selection_modes = list()
    story_mode_button = pygame.Rect(0, 0, int(display_size[0]), int(display_size[1] / 2))
    campaign_mode_button = pygame.Rect(0, int(display_size[1] / 2), int(display_size[0]), int(display_size[1] / 2))
    mode_selection_buttons.append(story_mode_button)
    mode_selection_buttons.append(campaign_mode_button)
    mode_selection_modes.append(KDS.Gamemode.Modes.Story)
    mode_selection_modes.append(KDS.Gamemode.Modes.Campaign)

    campaign_right_button = pygame.Rect(display_size[0] - 50 - 66, 200, 66, 66)
    campaign_left_button = pygame.Rect(50, 200, 66, 66)
    campaign_play_button = pygame.Rect(display_size[0] / 2 - 150, display_size[1] - 300, 300, 100)
    campaign_return_button = pygame.Rect(display_size[0] / 2 - 150, display_size[1] - 150, 300, 100)
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
    campaign_return_text = button_font1.render("RETURN", True, (KDS.Colors.Get.AviatorRed))

    while main_menu_running:

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    setFullscreen(False)
                if event.key == K_F4:
                    F4Pressed = True
                    if AltPressed == True and F4Pressed == True:
                        KDS_Quit()
                if event.key == K_LALT or event.key == K_RALT:
                    AltPressed = True
                if event.key == K_ESCAPE:
                    if MenuMode != Mode.MainMenu:
                        MenuMode = Mode.MainMenu
            if event.type == pygame.QUIT:
                KDS_Quit()

        if MenuMode == Mode.MainMenu:
            main_display.blit(main_menu_background, (0, 0))
            main_display.blit(pygame.transform.flip(
                menu_gasburner_animation.update(), False, False), (625, 450))

            for y in range(len(main_menu_buttons)):
                if main_menu_buttons[y].collidepoint(pygame.mouse.get_pos()):
                    if c:
                        main_menu_functions[y]()
                        c = False
                    button_color = (115, 115, 115)
                    if pygame.mouse.get_pressed()[0]:
                        button_color = (90, 90, 90)
                else:
                    button_color = (100, 100, 100)

                pygame.draw.rect(main_display, button_color, main_menu_buttons[y])

                main_display.blit(main_menu_texts[y], (int(main_menu_buttons[y].x + ((main_menu_buttons[y].width - main_menu_texts[y].get_width()) / 2)), int(main_menu_buttons[y].y + ((main_menu_buttons[y].height - main_menu_texts[y].get_height()) / 2))))

        if MenuMode == Mode.ModeSelectionMenu:
            main_display.blit(gamemode_bc_1_1, (0, 0))
            main_display.blit(gamemode_bc_2_1, (0, int(display_size[1] / 2)))
            for y in range(len(mode_selection_buttons)):
                if mode_selection_buttons[y].collidepoint(pygame.mouse.get_pos()):
                    if y == 0:
                        main_display.blit(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(round(gamemode_bc_1_alpha.update(False) * 255.0))), (0, 0))
                    elif y == 1:
                        main_display.blit(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(round(gamemode_bc_2_alpha.update(False) * 255.0))), (0, int(display_size[1] / 2)))
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
                        main_display.blit(KDS.Convert.ToAlpha(gamemode_bc_1_2, int(round(gamemode_bc_1_alpha.update(True) * 255.0))), (0, 0))
                    elif y == 1:
                        main_display.blit(KDS.Convert.ToAlpha(gamemode_bc_2_2, int(round(gamemode_bc_2_alpha.update(True) * 255.0))), (0, int(display_size[1] / 2)))

        if MenuMode == Mode.StoryMenu:
            print("Wow... So empty.")

        if MenuMode == Mode.CampaignMenu:
            pygame.draw.rect(main_display, (192, 192, 192), (50, 200, display_size[0] - 100, 66))
            for y in range(len(campaign_menu_buttons)):
                if campaign_menu_buttons[y].collidepoint(pygame.mouse.get_pos()):
                    if c:
                        if y < 2:
                            campaign_menu_functions[y]()
                        elif y == 2:
                            campaign_menu_functions[y](KDS.Gamemode.Modes.Campaign)
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
                    main_display.blit(pygame.transform.flip(arrow_button, True, False), (campaign_menu_buttons[y].x + 8, campaign_menu_buttons[y].y + 8))
                elif y == 1:
                    main_display.blit(arrow_button, (int(campaign_menu_buttons[y].x + 8), int(campaign_menu_buttons[y].y + 8)))
                elif y == 2:
                    main_display.blit(campaign_play_text, (campaign_play_button.x + (campaign_play_button.width / 4), campaign_play_button.y + (campaign_play_button.height / 4)))
                elif y == 3:
                    main_display.blit(campaign_return_text, (campaign_return_button.x + (campaign_return_button.width / 5), campaign_return_button.y + (campaign_return_button.height / 4)))

                current_map_int = int(current_map)

                if current_map_int < len(map_names):
                    map_name = map_names[current_map_int]
                else:
                    map_name = map_names[0]
                level_text = button_font1.render(current_map + " - " + map_name, True, (0, 0, 0))
                main_display.blit(level_text, (125, 209))

        pygame.display.update()
        main_display.fill((0, 0, 0))
        c = False
        clock.tick(60)
#endregion
#region Check Terms
agr(tcagr)
jukebox_music = load_jukebox_music()
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
            if event.key == K_a:
                playerMovingLeft = True
            if event.key == K_SPACE:
                if air_timer < 6:
                    vertical_momentum = -10
            if event.key == K_LSHIFT:
                playerSprinting = True
            if event.key == K_e:
                FunctionKey = True
            if event.key == K_ESCAPE:
                esc_menu = False if esc_menu else True
            if event.key == K_j:
                inventoryLeft()
            if event.key == K_k:
                inventoryRight()
            if event.key == K_t:
                console()
            if event.key == K_w:
                KeyW = True
            if event.key == K_s:
                KeyS = True
            if event.key == K_f:
                if playerStamina == 100:
                    playerStamina = -1000
                    farting = True
                    fart.play()
                    KDS.Missions.SetProgress("tutorial", "fart", 1.0)
            if event.key == K_q:
                if inventory[inventory_slot] != "none":
                    if inventory[inventory_slot] == "iPuhelin":
                        KDS.Missions.SetProgress("tutorial", "trash", 1.0)
                    item_rects.append(pygame.Rect(
                        player_rect.x, player_rect.y, 34, 34))
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
            if event.key == K_F3:
                DebugMode = not DebugMode
            if event.key == K_F4:
                F4Pressed = True
                if AltPressed == True and F4Pressed == True:
                    KDS_Quit()
                else:
                    player_health = 0
            if event.key == K_LALT or event.key == K_RALT:
                AltPressed = True
            if event.key == K_F11:
                setFullscreen(False)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseLeftPressed = True
                rk62_sound_cooldown = 11
                pistolFire = True
                if player_hand_item == "gasburner":
                    gasburnerBurning = True
                if player_hand_item == "knife":
                    knifeInUse = True
                if player_hand_item == "plasmarifle":
                    plasmarifle_fire = True
        if event.type == KEYUP:
            if event.key == K_d:
                playerMovingRight = False
            if event.key == K_a:
                playerMovingLeft = False
            if event.key == K_LSHIFT:
                playerSprinting = False
            if event.key == K_F4:
                F4Pressed = False
            if event.key == K_LALT or event.key == K_RALT:
                AltPressed = False
            if event.key == K_w:
                KeyW = False
            if event.key == K_s:
                KeyS = False
            if event.key == K_c:
                if player_hand_item == "gasburner":
                    gasburnerBurning = not gasburnerBurning
                    gasburner_fire.stop()
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                mouseLeftPressed = False
                if player_hand_item == "gasburner":
                    gasburnerBurning = False
                if player_hand_item == "knife":
                    knifeInUse = False
                if player_hand_item == "plasmarifle":
                    plasmarifle_fire = False
            if event.button == 4:
                inventoryLeft()
            if event.button == 5:
                inventoryRight()
        if event.type == pygame.QUIT:
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

    true_scroll[0] += (player_rect.x - true_scroll[0] - 285) / 12
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
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(player_death_sound)
        player_death_sound.set_volume(0.5)
        animation_has_played = True
#endregion
#region Rendering
    for i in range(len(world_gen)):
        y = 0
        for layer in world_gen[i]:
            x = 0
            for tile in layer:
                if tile == 'b':
                    screen.blit(floor1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'c':
                    screen.blit(wall1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'd':
                    screen.blit(table1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'e':
                    screen.blit(toilet1, (x * 34-scroll[0], y * 34-scroll[1]+1))
                if tile == 'f':
                    screen.blit(lamp1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'g':
                    screen.blit(trashcan, (x * 34-scroll[0]+2, y * 34-scroll[1]+7))
                if tile == 'h':
                    screen.blit(ground1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'i':
                    screen.blit(grass, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'j':
                    screen.blit(concrete1, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'o':
                    screen.blit(bricks, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'A':
                    screen.blit(tree, (x * 34-scroll[0], y * 34-scroll[1]-50))
                if tile == 'p':
                    screen.blit(planks, (x * 34-scroll[0], y * 34-scroll[1]))
                if tile == 'q':
                    screen.blit(ladder_texture, (x * 34-scroll[0], y * 34-scroll[1]))
                x += 1
            y += 1

    x = 0
    for door in door_rects:
        if doors_open[x]:
            screen.blit(door_open, (door.x-scroll[0]+2, door.y-scroll[1]))
        else:
            if color_keys[x] == "red":
                screen.blit(red_door_closed,
                            (door.x-scroll[0], door.y-scroll[1]))
            elif color_keys[x] == "green":
                screen.blit(green_door_closed,
                            (door.x-scroll[0], door.y-scroll[1]))
            elif color_keys[x] == "blue":
                screen.blit(blue_door_closed,
                            (door.x-scroll[0], door.y-scroll[1]))
            else:
                screen.blit(door_closed, (door.x-scroll[0], door.y-scroll[1]))
        x += 1

    for jukebox in jukeboxes:
        screen.blit(jukebox_texture, (jukebox.x -
                                      scroll[0], jukebox.y-scroll[1]))
        if player_rect.colliderect(jukebox):
            screen.blit(jukebox_tip, (jukebox.x -
                                      scroll[0]-20, jukebox.y-scroll[1]-30))
            if FunctionKey:
                pygame.mixer.music.pause()
                jukebox_music[jukeboxMusicPlaying].stop()
                while jukeboxMusicPlaying == lastJukeboxSong[0] or jukeboxMusicPlaying == lastJukeboxSong[1] or jukeboxMusicPlaying == lastJukeboxSong[2] or jukeboxMusicPlaying == lastJukeboxSong[3] or jukeboxMusicPlaying == lastJukeboxSong[4]:
                    jukeboxMusicPlaying = int(
                        random.uniform(0, len(jukebox_music)))

                lastJukeboxSong[4] = lastJukeboxSong[3]
                lastJukeboxSong[3] = lastJukeboxSong[2]
                lastJukeboxSong[2] = lastJukeboxSong[1]
                lastJukeboxSong[1] = lastJukeboxSong[0]
                lastJukeboxSong[0] = jukeboxMusicPlaying
                jukebox_music[jukeboxMusicPlaying].play()
        else:
            pygame.mixer.music.unpause()
            for x in range(len(jukebox_music)):
                jukebox_music[x].stop()

    for landmine in landmines:
        screen.blit(landmine_texture, (landmine.x -
                                       scroll[0], landmine.y-scroll[1]))
        if player_rect.colliderect(landmine):
            landmines.remove(landmine)
            landmine_explosion.play()
            player_health -= 60
            if player_health < 0:
                player_health = 0
            explosion_positions.append((landmine.x-40, landmine.y-58))
        for zombie1 in zombies:
            if zombie1.rect.colliderect(landmine):
                landmines.remove(landmine)
                landmine_explosion.play()
                zombie1.health -= 140
                if zombie1.health < 0:
                    zombie1.health = 0
                explosion_positions.append((landmine.x-40, landmine.y-58))

        for sergeant in sergeants:
            if sergeant.rect.colliderect(landmine):
                landmines.remove(landmine)
                landmine_explosion.play()
                sergeant.health -= 220

                explosion_positions.append((landmine.x-40, landmine.y-58))

    if player_hand_item == "plasmarifle" and plasmarifle_fire == True:

        if plasmarifle_cooldown > 3 and ammunition_plasma > 0:
            plasmarifle_cooldown = 0

            if direction:
                j_direction = False
            else:
                j_direction = True
            if j_direction:
                plasmabullets.append(plasma_bullet(
                    (player_rect.x+50, player_rect.y+17), j_direction, screen))
            else:
                plasmabullets.append(plasma_bullet(
                    (player_rect.x-50, player_rect.y+17), j_direction, screen))

            plasmarifle_f_sound.play()
            ammunition_plasma -= 1

    if player_hand_item != "none":
        if player_hand_item == "plasmarifle":

            ammo_count = score_font.render(
                "Ammo: " + str(ammunition_plasma), True, (255, 255, 255))
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "pistol":

            ammo_count = score_font.render(
                "Ammo: " + str(pistol_bullets), True, (255, 255, 255))
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "rk62":

            ammo_count = score_font.render(
                "Ammo: " + str(rk_62_ammo), True, (255, 255, 255))
            screen.blit(ammo_count, (10, 360))

        elif player_hand_item == "shotgun":

            ammo_count = score_font.render(
                "Ammo: " + str(shotgun_shells), True, (255, 255, 255))
            screen.blit(ammo_count, (10, 360))

    for bullet in plasmabullets:
        state = bullet.update(tile_rects)
        if state:
            plasmabullets.remove(bullet)

    if len(plasmabullets) > 50:
        plasmabullets.remove(plasmabullets[0])

    for explosion in explosion_positions:
        explosion_image, done_state = explosion_animation.update()
        if not done_state:
            screen.blit(explosion_image,
                        (explosion[0]-scroll[0], explosion[1]-scroll[1]))
        else:
            explosion_positions.remove(explosion)
            explosion_animation.reset()

    item_collision_test(player_rect, item_rects)
    b = 0
    for item in item_rects:
        if item_ids[b] == 'gasburner':
            screen.blit(gasburner_off, (item.x-scroll[0], item.y-scroll[1]+10))
        if item_ids[b] == "knife":
            screen.blit(knife, (item.x-scroll[0], item.y-scroll[1]+26))
        if item_ids[b] == "red_key":
            screen.blit(red_key, (item.x-scroll[0], item.y-scroll[1]+16))
        if item_ids[b] == "green_key":
            screen.blit(green_key, (item.x-scroll[0], item.y-scroll[1]+16))
        if item_ids[b] == "blue_key":
            screen.blit(blue_key, (item.x-scroll[0], item.y-scroll[1]+16))
        if item_ids[b] == "coffeemug":
            screen.blit(
                coffeemug, (item.x - scroll[0], item.y - scroll[1] + 14))
        if item_ids[b] == "ss_bonuscard":
            screen.blit(ss_bonuscard, (item.x-scroll[0], item.y-scroll[1]+14))
        if item_ids[b] == "lappi_sytytyspalat":
            screen.blit(lappi_sytytyspalat,
                        (item.x-scroll[0], item.y-scroll[1]+17))
        if item_ids[b] == "plasmarifle":
            screen.blit(plasmarifle, (item.x-scroll[0], item.y-scroll[1]+17))
        if item_ids[b] == "cell":
            screen.blit(cell, (item.x-scroll[0], item.y-scroll[1]+17))
        if item_ids[b] == "pistol":
            screen.blit(pistol_texture,
                        (item.x-scroll[0]-23, item.y-scroll[1]+18))
        if item_ids[b] == "pistol_mag":
            screen.blit(pistol_mag, (item.x-scroll[0], item.y-scroll[1]+19))
        if item_ids[b] == "rk62":
            screen.blit(rk62_texture, (item.x-scroll[0], item.y-scroll[1]+17))
        if item_ids[b] == "rk62_mag":
            screen.blit(rk62_mag, (item.x-scroll[0], item.y-scroll[1]+14))
        if item_ids[b] == "medkit":
            screen.blit(medkit, (item.x-scroll[0], item.y-scroll[1]+15))
        if item_ids[b] == "shotgun":
            screen.blit(shotgun, (item.x-scroll[0], item.y-scroll[1]+22))
        if item_ids[b] == "shotgun_shells":
            screen.blit(shotgun_shells_t,
                        (item.x-scroll[0], item.y-scroll[1]+25))
        if item_ids[b] == "iPuhelin":
            screen.blit(iphone_texture,
                        (item.x-scroll[0], item.y-scroll[1]+10))
        b += 1

#endregion
#region PlayerMovement
    if player_health > 0:
        if playerSprinting == False and playerStamina < 100.0:
            playerStamina += 0.25
        elif playerSprinting and playerStamina > 0:
            playerStamina -= 0.75
        elif playerSprinting and playerStamina <= 0:
            playerSprinting = False

    player_movement = [0, 0]

    koponen_recog_rec.center = koponen_rect.center

    if playerMovingRight == True:
        player_movement[0] += 4
        KDS.Missions.SetProgress("tutorial", "walk", 0.005)
        if playerSprinting == True and playerStamina > 0:
            player_movement[0] += 4
            KDS.Missions.SetProgress("tutorial", "walk", 0.005)

    if playerMovingLeft == True:
        player_movement[0] -= 4
        KDS.Missions.SetProgress("tutorial", "walk", 0.005)
        if playerSprinting == True and playerStamina > 0:
            player_movement[0] -= 4
            KDS.Missions.SetProgress("tutorial", "walk", 0.005)

    player_movement[1] += vertical_momentum
    vertical_momentum += 0.4
    if vertical_momentum > 8:
        vertical_momentum = 8

    for ladder in ladders:
        if player_rect.colliderect(ladder):
            vertical_momentum = 0
            if KeyW:
                player_movement[1] = -1
            elif KeyS:
                player_movement[1] = 1
            else:
                player_movement[1] = 0

#endregion
#region AI
    toilet_collisions(player_rect, gasburnerBurning)

    if player_health > 0:
        player_rect, collisions = move(
            player_rect, player_movement, tile_rects)
    else:
        player_rect, collisions = move(player_rect, [0, 8], tile_rects)

    koponen_rect, k_collisions = move(
        koponen_rect, koponen_movement, tile_rects)

    wa = zombie_walk_animation.update()
    sa = sergeant_walk_animation.update()

    for sergeant in sergeants:
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
                sergeant.rect, sergeant.hits = move(
                    sergeant.rect, sergeant.movement, tile_rects)

                if sergeant.movement[0] > 0:
                    sergeant.direction = True
                elif sergeant.movement[0] < 0:
                    sergeant.direction = False

                screen.blit(pygame.transform.flip(sa, sergeant.direction, False),
                            (sergeant.rect.x-scroll[0], sergeant.rect.y-scroll[1]))

                if sergeant.hits["right"] or sergeant.hits["left"]:
                    sergeant.movement[0] = -sergeant.movement[0]

            else:
                u, i = sergeant_shoot_animation.update()

                screen.blit(pygame.transform.flip(u, sergeant.direction, False),
                            (sergeant.rect.x-scroll[0], sergeant.rect.y-scroll[1]))

                if sergeant_shoot_animation.tick > 30 and not sergeant.xvar:
                    sergeant.xvar = True
                    shotgun_shot.play()
                    if sergeant.hit_scan(player_rect, player_health, tile_rects):
                        player_health = damage(player_health, 20, 50)
                if i:
                    sergeant_shoot_animation.reset()
                    sergeant.shoot = False
                    sergeant.xvar = False

        elif sergeant.playDeathAnimation:
            d, s = sergeant_death_animation.update()
            if not s:
                screen.blit(pygame.transform.flip(d, sergeant.direction, False),
                            (sergeant.rect.x-scroll[0], sergeant.rect.y-scroll[1]))
            if s:
                sergeant.playDeathAnimation = False
                sergeant_death_animation.reset()
        else:
            screen.blit(pygame.transform.flip(sergeant_corpse, sergeant.direction,
                                              False), (sergeant.rect.x-scroll[0], sergeant.rect.y-scroll[1]+10))

    for zombie1 in zombies:
        if zombie1.health > 0:
            search = zombie1.search(player_rect)
            if not search:
                zombie1.rect, zombie1.hits = move(
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
                ), zombie1.direction, False), (zombie1.rect.x-scroll[0], zombie1.rect.y-scroll[1]))

        elif zombie1.playDeathAnimation:
            d, s = zombie_death_animation.update()
            if not s:
                screen.blit(pygame.transform.flip(d, zombie1.direction, False),
                            (zombie1.rect.x-scroll[0], zombie1.rect.y-scroll[1]))
            if s:
                zombie1.playDeathAnimation = False
                zombie_death_animation.reset()
        else:
            screen.blit(pygame.transform.flip(zombie_corpse, zombie1.direction,
                                              False), (zombie1.rect.x-scroll[0], zombie1.rect.y-scroll[1]+14))

    # Zombien käsittely loppuu tähän

    arch_run = archvile_run_animation.update()
    for archvile in archviles:
        archvile.update(arch_run)

    for bulldog in bulldogs:
        bulldog.startUpdateThread(player_rect, tile_rects)
    
    for bulldog in bulldogs:
        bd_attr = bulldog.getAttributes()
        screen.blit(pygame.transform.flip(bd_attr[1],bd_attr[2], False),(bd_attr[0].x-scroll[0],bd_attr[0].y-scroll[1]))
        player_health -= bd_attr[3]

    if k_collisions["left"]:
        koponen_movingx = -koponen_movingx
    elif k_collisions["right"]:
        koponen_movingx = -koponen_movingx

    door_collision_test()
#endregion
#region UI
    score = score_font.render(
        ("Score: " + str(player_score)), True, (255, 255, 255))
    if DebugMode:
        fps = score_font.render(
            "Fps: " + str(int(clock.get_fps())), True, (255, 255, 255))

    if player_health < 0:
        player_health = 0

    health = score_font.render(
        "Health: " + str(player_health), True, (255, 255, 255))
    stamina = score_font.render(
        "Stamina: " + str(round(int(playerStamina))), True, (255, 255, 255))
#endregion
#region Pelaajan elämätilanteen käsittely
    if player_health < last_player_health and player_health != 0:
        hurted = True
    else:
        hurted = False

    last_player_health = player_health

    if hurted:
        hurt_sound.play()
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
            animation = run_animation.copy()
            animation_duration = 7
            if playerSprinting:
                animation_duration = 3
        else:
            animation = stand_animation.copy()
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

    if toilet_animation_stats[2] > toilet_animation_stats[1]:
        toilet_animation_stats[0] += 1
        toilet_animation_stats[2] = 0
        if toilet_animation_stats[0] > 2:
            toilet_animation_stats[0] = 0

    if koponen_animation_stats[2] > koponen_animation_stats[1]:
        koponen_animation_stats[0] += 1
        koponen_animation_stats[2] = 0
        if koponen_animation_stats[0] > 1:
            koponen_animation_stats[0] = 0

    if player_hand_item != "none":
        if player_health:
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
            if player_hand_item in Items_list:
                o = Items[player_hand_item]
                if direction:
                    offset = player_rect.width - o.get_width() / 2
                else:
                    offset = -player_rect.width - -(o.get_width() / 2)

            if player_hand_item == "gasburner":
                if gasburnerBurning:
                    if gasburner_animation_stats[0]:
                        gasburner_fire.stop()
                        pygame.mixer.Sound.play(gasburner_fire)
                    screen.blit(pygame.transform.flip(gasburner_animation[gasburner_animation_stats[0]], direction, False), (
                        player_rect.right-offset_c-scroll[0], player_rect.y-scroll[1]))
                else:
                    screen.blit(pygame.transform.flip(gasburner_off, direction, False),
                                (player_rect.right-offset_c-scroll[0], player_rect.y-scroll[1]))

            if player_hand_item == "knife":
                if knifeInUse:
                    screen.blit(pygame.transform.flip(knife_animation[knife_animation_stats[0]], direction, False), (
                        player_rect.right-offset_k-scroll[0], player_rect.y-scroll[1]+14))
                else:
                    screen.blit(pygame.transform.flip(knife, direction, False), (
                        player_rect.right-offset_c-scroll[0], player_rect.y-scroll[1]+14))

            if player_hand_item == "coffeemug":
                screen.blit(pygame.transform.flip(coffeemug, direction, False), (
                    player_rect.center[0] - offset - scroll[0], player_rect.y - scroll[1] + 14))

            if player_hand_item == "iPuhelin":
                screen.blit(pygame.transform.flip(iphone_texture, direction, False), (
                    player_rect.center[0] - offset - scroll[0], player_rect.y - scroll[1] + 14))

            if player_hand_item == "plasmarifle":
                if plasmarifle_fire and ammunition_plasma > 0:
                    screen.blit(pygame.transform.flip(plasmarifle_animation.update(), direction, False), (
                        player_rect.right-offset_p-scroll[0], player_rect.y-scroll[1]+14))

                else:
                    screen.blit(pygame.transform.flip(plasmarifle, direction, False), (
                        player_rect.right-offset_p-scroll[0], player_rect.y-scroll[1]+14))

            if player_hand_item == "pistol":
                pistol_cooldown += 1
                if pistolFire and pistol_cooldown > 25:
                    pistol_cooldown = 0
                    if pistol_bullets > 0:
                        pistol_bullets -= 1
                        screen.blit(pygame.transform.flip(pistol_f_texture, not direction, False), (
                            player_rect.right-offset_pi-scroll[0], player_rect.y-scroll[1]+14))
                        bullet = Bullet(
                            [player_rect.x, player_rect.y+20], direction, 50)
                        hit = bullet.shoot(tile_rects)
                        del hit, bullet
                        pistol_shot.play()
                else:
                    screen.blit(pygame.transform.flip(pistol_texture, not direction, False), (
                        player_rect.right-offset_pi-scroll[0], player_rect.y-scroll[1]+14))

            if player_hand_item == "rk62":
                if mouseLeftPressed and rk_62_ammo > 0 and rk62_cooldown > 4:
                    rk_62_ammo -= 1
                    rk62_cooldown = 0
                    screen.blit(pygame.transform.flip(rk62_f_texture, direction, False), (
                        player_rect.right-offset_rk-scroll[0], player_rect.y-scroll[1]+14))
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
                        rk62_shot.play()

                else:
                    if not mouseLeftPressed:
                        rk62_shot.stop()
                    screen.blit(pygame.transform.flip(rk62_texture, direction, False), (
                        player_rect.right-offset_rk-scroll[0], player_rect.y-scroll[1]+14))

            if player_hand_item == "shotgun":
                if not shotgun_loaded:
                    shotgun_cooldown += 1
                    if shotgun_cooldown > 60:
                        shotgun_loaded = True
                else:
                    shotgun_cooldown = 0
                if pistolFire and shotgun_shells > 0 and shotgun_loaded:
                    shotgun_shells -= 1
                    shotgun_loaded = False
                    shotgun_thread = threading.Thread(target=shotgun_shots)
                    shotgun_thread.start()
                    player_shotgun_shot.play()
                    screen.blit(pygame.transform.flip(shotgun_f, direction, False), (
                        player_rect.right-offset_p-scroll[0], player_rect.y-scroll[1]+14))

                else:
                    screen.blit(pygame.transform.flip(shotgun, direction, False), (
                        player_rect.right-offset_p-scroll[0], player_rect.y-scroll[1]+14))

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
            koponen_talk_tip, (koponen_recog_rec.topleft[0]-scroll[0], koponen_recog_rec.topleft[1]-scroll[1]-10))
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
        if burning_toilets[h] == True:
            screen.blit(toilet_animation[toilet_animation_stats[0]],
                        (toilet.x-scroll[0]+2, toilet.y-scroll[1]+1))
        h += 1
    h = 0
    for trashcan2 in trashcans:
        if burning_trashcans[h] == True:
            screen.blit(trashcan_animation[toilet_animation_stats[0]],
                        (trashcan2.x-scroll[0]+3, trashcan2.y-scroll[1]+6))
        h += 1

    screen.blit(koponen_animation[koponen_animation_stats[0]], (
        koponen_rect.x-scroll[0], koponen_rect.y-scroll[1]))

    if player_health or player_death_event:
        screen.blit(pygame.transform.flip(animation[animation_image], direction, False), (
            player_rect.x-scroll[0], player_rect.y-scroll[1]))
    else:
        screen.blit(pygame.transform.flip(player_corpse, direction, False), (
            player_rect.x-scroll[0], player_rect.y-scroll[1]))

    for archvile in archviles:
        if archvile.attack_anim:
            screen.blit(flames_animation.update(),
                        (player_rect.x-scroll[0], player_rect.y-scroll[1]-20))

#endregion
#region Debug Mode
    screen.blit(score, (10, 55))
    if DebugMode:
        screen.blit(fps, (10, 10))
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
                screen.blit(iphone_texture, ((i * 34) + 10 +
                                             (34 / iphone_texture.get_width() * 2), 80))
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
                screen.blit(shotgun, ((i * 34) + 20 +
                                      (68 / shotgun.get_width() * 2), 80))
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
    main_display.blit(pygame.transform.scale(screen, display_size), (0, 0))
    pygame.display.update()
#endregion
#region Conditional Events
    if esc_menu:
        pygame.mixer.pause()
        pygame.mixer.music.pause()
        screen.blit(alpha, (0, 0))
        main_display.blit(pygame.transform.scale(screen, display_size), (0, 0))
        pygame.image.save(main_display, "im314.png")
        esc_menu_f()
    if go_to_main_menu:
        pygame.mixer.music.stop()
        main_menu()
    animation_counter += 1
    if player_hand_item == "gasburner":
        gasburner_animation_stats[2] += 1
    elif player_hand_item == "knife":
        knife_animation_stats[2] += 1
    FunctionKey = False
    pistolFire = False
    toilet_animation_stats[2] += 1
    koponen_animation_stats[2] += 1
    plasmarifle_cooldown += 1
    rk62_cooldown += 1
    for sergeant in sergeants:
        sergeant.hitscanner_cooldown += 1
#endregion
#region Ticks
    tick += 1
    if tick > 60:
        tick = 0
    clock.tick(60)
#endregion
#endregion