#region Importing
import pygame
import os
import random
import logging
import threading
import configparser
from datetime import datetime
from pygame.locals import *
#endregion
#region PyGame Initialisation

pygame.init()

display_size = (1200, 800)
screen_size = (600, 400)

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
        self.display_to_blit.blit(self.screen_text, (self.topleft[0], self.topleft[1]+self.row))
        self.row += self.row_height

    def resetRow(self):
        self.row = 0

    def skipRow(self):
        self.row += self.row_height

#endregion
#region Animator

class Animation:

    """
    Ensimmäinen argumentti odottaa animaation nimeä esim. "gasburner"
    Toinen argumentti odottaa kyseisen animaation kuvien määrää. Jos animaatiossa on 2 kuvaa, kannattaa toiseksi argumentiksi laittaa 2
    Kolmas argumentti odottaa yhden kuvan kestoa tickeinä. 

    Animaation kuvat tulee tallentaa animations-kansioon png-muodossa tähän malliin: 
        gasburner_0, gasburner_1, gasburner_2, gasburner_3 ja niin edelleen

    animation_name - string, number_of_images - int, duration - int

    """

    def __init__(self, animation_name, number_of_images, duration, colorkey):
        self.images = []
        self.duration = duration
        self.ticks = number_of_images * duration - 1
        self.tick = 0
        self.colorkey = colorkey

        for x in range(number_of_images):
            path = "resources/animations/" + animation_name + "_" + str(x) + ".png" #Kaikki animaation kuvat ovat oletusarvoisesti png-muotoisia
            image = pygame.image.load(path).convert()
            image.set_colorkey(self.colorkey) #Kaikki osat kuvasata joiden väri on RGB 255,255,255 muutetaan läpinäkyviksi

            for _ in range(duration):
                self.images.append(image)

        logging.debug(self.images)
                
    #update-funktio tulee kutsua silmukan jokaisella kierroksella, jotta animaatio toimii kunnolla
    #update-funktio palauttaa aina yhden pygame image-objektin

    def update(self):
        self.tick += 1
        if self.tick > self.ticks:
            self.tick = 0

        return self.images[self.tick]

#endregion
#region Initialisation

logFiles = os.listdir("logs/")

while len(logFiles) >= 5:
    logFiles = os.listdir("logs/")
    os.remove("logs/" + logFiles[0])

now = datetime.now()
logging.basicConfig(filename="logs/log_" + now.strftime("%Y-%m-%d-%H-%M-%S") + ".log", level=logging.NOTSET)
logging.info('Initialising Game...')

printer = pygame_print_text((7,8,10),(50,50),680,main_display)

esc_menu_surface = pygame.Surface((500, 400))
alpha = pygame.Surface(screen_size)
alpha.fill((0,0,0))
alpha.set_alpha(170)

#region Lataukset

pygame.display.set_caption("Koponen Dating Simulator")
game_icon = pygame.image.load("resources/game_icon.png")
main_menu_background = pygame.image.load("resources/main_menu/main_menu_bc.png")
settings_background = pygame.image.load("resources/settings_bc.png")
agr_background = pygame.image.load("resources/tcagr.png")
path = "resources/ads/koponen_talk_bc0.png"
bc = pygame.image.load(path)
pygame.display.set_icon(game_icon)
clock = pygame.time.Clock()

score_font = pygame.font.Font("gamefont.ttf", 10, bold=0, italic=0)
tip_font = pygame.font.Font("gamefont2.ttf",10,bold=0, italic=0)
button_font = pygame.font.Font("gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("gamefont2.ttf", 52, bold=0, italic=0)

player_img = pygame.image.load("resources/player/stand0.png").convert()
player_corpse = pygame.image.load("resources/player/corpse.png").convert()
player_corpse.set_colorkey((255,255,255))
player_img.set_colorkey((255, 255, 255))

floor1 = pygame.image.load("resources/build/floor0v2.png")
concrete1 = pygame.image.load("resources/build/concrete0.png")
wall1 = pygame.image.load("resources/build/wall0.png")
table1 = pygame.image.load("resources/build/table0.png").convert()
toilet1 = pygame.image.load("resources/build/toilet0.png").convert()
lamp1 = pygame.image.load("resources/build/lamp0.png").convert()
trashcan = pygame.image.load("resources/build/trashcan.png").convert()
ground1 = pygame.image.load("resources/build/ground0.png")
grass = pygame.image.load("resources/build/grass0.png")
door_closed = pygame.image.load("resources/build/door_closed.png").convert()
red_door_closed = pygame.image.load("resources/build/red_door_closed.png").convert()
green_door_closed = pygame.image.load("resources/build/green_door_closed.png").convert()
blue_door_closed = pygame.image.load("resources/build/blue_door_closed.png").convert()
door_open = pygame.image.load("resources/build/door_open2.png")
bricks = pygame.image.load("resources/build/bricks.png")
tree = pygame.image.load("resources/build/tree.png")
planks = pygame.image.load("resources/build/planks.png")
table1.set_colorkey((255, 255, 255))
toilet1.set_colorkey((255, 255, 255))
lamp1.set_colorkey((255, 255, 255))
trashcan.set_colorkey((255,255,255))
door_closed.set_colorkey((255,255,255))
red_door_closed.set_colorkey((255,255,255))
green_door_closed.set_colorkey((255,255,255))
blue_door_closed.set_colorkey((255,255,255))
tree.set_colorkey((0,0,0))

gasburner_off = pygame.image.load("resources/items/gasburner_off.png").convert()
#gasburner_on = pygame.image.load("resources/items/gasburner_on.png").convert()
knife = pygame.image.load("resources/items/knife.png").convert()
knife_blood = pygame.image.load("resources/items/knife.png").convert()
red_key = pygame.image.load("resources/items/red_key.png").convert()
green_key = pygame.image.load("resources/items/green_key2.png").convert()
blue_key = pygame.image.load("resources/items/blue_key.png").convert()
coffeemug = pygame.image.load("resources/items/coffeemug.png").convert()
ss_bonuscard = pygame.image.load("resources/items/ss_bonuscard.png").convert()
lappi_sytytyspalat = pygame.image.load("resources/items/lappi_sytytyspalat.png").convert()
gasburner_off.set_colorkey((255, 255, 255))
knife.set_colorkey((255, 255, 255))
knife_blood.set_colorkey((255, 255, 255))
red_key.set_colorkey((255,255,255))
green_key.set_colorkey((255,255,255))
blue_key.set_colorkey((255,255,255))
coffeemug.set_colorkey((255,255,255))
ss_bonuscard.set_colorkey((255,0,0))
lappi_sytytyspalat.set_colorkey((255,255,255))


text_icon = pygame.image.load("resources/text_icon.png").convert()
text_icon.set_colorkey((255,255,255))

gasburner_clip = pygame.mixer.Sound("audio/misc/gasburner_clip.wav")
gasburner_fire = pygame.mixer.Sound("audio/misc/gasburner_fire.wav")
door_opening = pygame.mixer.Sound("audio/misc/door.wav")
player_death_sound = pygame.mixer.Sound("audio/misc/dspldeth.wav")
player_walking = pygame.mixer.Sound("audio/misc/walking.wav")
coffeemug_sound = pygame.mixer.Sound("audio/misc/coffeemug.wav")
knife_pickup = pygame.mixer.Sound("audio/misc/knife.wav")
key_pickup = pygame.mixer.Sound("audio/misc/pickup_key.wav")
ss_sound = pygame.mixer.Sound("audio/misc/ss.wav")
lappi_sytytyspalat_sound = pygame.mixer.Sound("audio/misc/sytytyspalat.wav")

#endregion Lataukset

main_running = True
playerMovingRight = False
playerMovingLeft = False
playerSprinting = False
playerStamina = 100.0
gasburnerBurning = False
tick = 0
knifeInUse = False
currently_on_mission = False
current_mission = "none"
player_name = "Sinä"

configParser = configparser.RawConfigParser()
configFilePath = os.path.join(os.path.dirname(__file__), 'settings.cfg')
configParser.read(configFilePath)

try:
    tcagr = bool(configParser.get("Data", "TermsAccepted"))
except:
    configParser.add_section("Data")
    configParser.set("Data", "TermsAccepted", False)
    tcagr = False
    with open("settings.cfg", "w") as cfgFile:
        configParser.write(cfgFile)
try:
    volume_data = configParser.get("Settings", "Volume")
except:
    configParser.add_section("Settings")
    configParser.set("Settings", "Volume", 15)
    volume_data = 15
    with open("settings.cfg", "w") as cfgFile:
        configParser.write(cfgFile)
logging.debug("Settings Loaded:\nTerms Accepted: " + str(tcagr) + "\nVolume: " + str(configParser))

volume = float(volume_data)/100
gasburner_animation_stats = [0, 4, 0]
knife_animation_stats = [0, 10, 0]
toilet_animation_stats = [0,5,0]
koponen_animation_stats = [0,7,0]
player_hand_item = "none"
player_keys = {"red":False,"green":False,"blue":False}
direction = True
FunctionKey = False
AltPressed = False
F4Pressed = False
esc_menu = False
mouseLeftPressed = False

go_to_main_menu = False

main_menu_running = False
settings_running = False
vertical_momentum = 0
animation_counter = 0
animation_duration = 0
animation_image = 0
air_timer = 0
player_health = 100
player_death_event = False
animation_has_played = False
inventory = ["none"]
global player_score
player_score = 0
true_scroll = [0, 0]
inventory_slot = 0

test_rect = pygame.Rect(0, 0, 60, 40)
player_rect = pygame.Rect(100, 100, 33, 65)
koponen_rect = pygame.Rect(200,200,24,64)
koponen_recog_rec = pygame.Rect(0,0,72,64)
koponen_movement = [0,6]
koponen_movingx = 0
koponen_happines = 40

task = ""
taskTaivutettu = ""

DebugMode = False

#endregion
#region Pickup Sound
def play_key_pickup():
    pygame.mixer.Sound.play(key_pickup)
#endregion
#region Loading

def load_map(path):
    with open(path + '.kds', 'r') as f:
        data = f.read()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


def load_items(path):
    with open(path + '.kds', 'r') as f:
        data = f.read()
    data = data.split('\n')
    item_map = []
    for row in data:
        item_map.append(list(row))
    return item_map

def load_music():
    original_path = os.getcwd()
    os.chdir("audio/music/")
    music_files = os.listdir()

    random.shuffle(music_files)
    logging.debug("Music Files Initialised: " + str(len(music_files)))
    for track in music_files:
        logging.debug("Initialised Music File: " + track)

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

def load_ads():
    ad_files = os.listdir("resources/ads/")

    random.shuffle(ad_files)
    logging.debug("Ad Files Initialised: " + str(len(ad_files)))
    for ad in ad_files:
        logging.debug("Initialised Ad File: " + ad)

    ad_images = []
    
    for ad in ad_files:
        path = str("resources/ads/" + ad)
        ad_images.append(pygame.image.load(path))

    return ad_images

#world_gen = load_map("resources/game_map")
#item_gen = load_items("resources/item_map")


def load_rects():
    tile_rects = []
    toilets = []
    trashcans = []
    burning_toilets = []
    burning_trashcans = []
    w = [0,0]
    y = 0
    for layer in world_gen:
        x = 0
        for tile in layer:
            if tile != 'a':
                if tile == 'f':
                    tile_rects.append(pygame.Rect(x*34, y*34, 14,21))
                elif tile == 'e':
                    w = list(toilet1.get_size())
                    toilets.append(pygame.Rect(x*34-2,y*34,34,34))
                    burning_toilets.append(False)
                    tile_rects.append(pygame.Rect(x*34, y*34, w[0], w[1]))
                elif tile == 'g':
                    w = list(trashcan.get_size())
                    trashcans.append(pygame.Rect(x*34-1,y*34,w[0]+2,w[1]))
                    burning_trashcans.append(False)
                    tile_rects.append(pygame.Rect(x*34, y*34+8, w[0], w[1]))
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
                else:
                    tile_rects.append(pygame.Rect(x*34, y*34, 34, 34))
                
            x += 1
        y += 1
    return tile_rects, toilets, burning_toilets, trashcans, burning_trashcans


def load_item_rects():
    def append_rect():
        item_rects.append(pygame.Rect(x*34, y*34, 34, 34))
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
            x += 1
        y += 1
    return item_rects, item_ids, task_items

def load_doors():
    y = 0
    door_rects = []
    doors_open = []
    color_keys = [] 
    for layer in world_gen:
        x = 0
        for door in layer:
            if door == 'k':
                size = list(door_closed.get_size())
                door_rects.append(pygame.Rect(x*34-1,y*34,size[0]+1,size[1]))
                doors_open.append(False)
                color_keys.append("none")
            if door == 'l':
                size = list(red_door_closed.get_size())
                door_rects.append(pygame.Rect(x*34-1,y*34,size[0]+1,size[1]))
                doors_open.append(False)
                color_keys.append("red")
            if door == 'm':
                size = list(green_door_closed.get_size())
                door_rects.append(pygame.Rect(x*34-1,y*34,size[0]+1,size[1]))
                doors_open.append(False)
                color_keys.append("green")
            if door == 'n':
                size = list(blue_door_closed.get_size())
                door_rects.append(pygame.Rect(x*34-1,y*34,size[0]+1,size[1]))
                doors_open.append(False)
                color_keys.append("blue")
            x+=1
        y += 1
    return door_rects, doors_open, color_keys

#tile_rects, toilets, burning_toilets, trashcans, burning_trashcans = load_rects()
#item_rects, item_ids = load_item_rects()

#door_rects, doors_open, color_keys = load_doors()

def load_animation(name, number_of_images):
    animation_list = []
    for i in range(number_of_images):
        path = "resources/player/" + name + str(i) + ".png"
        img = pygame.image.load(path).convert()
        img.set_colorkey((255, 255, 255))
        animation_list.append(img)
    return animation_list

#endregion
#region Collisions

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def door_collision_test():
    x = 0

    def door_sound():
        pygame.mixer.Sound.play(door_opening)

    global door_rects, doors_open, color_keys, player_movement
    hit_list = collision_test(player_rect,door_rects)
    if player_rect.colliderect(door_rects[0]):
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
    b = 0
    global player_hand_item, player_score, inventory
    itemTipVisible = False
    for item in items:
        if rect.colliderect(item):
            hit_list.append(item)
            if not itemTipVisible:
                itemTip = tip_font.render("Nosta Esine Painamalla [E]", True, (255,255,255))
                screen.blit(itemTip, (item.x - scroll[0] - 60, item.y - scroll[1] - 10))
                itemTipVisible = True
            if FunctionKey == True:
                if item_ids[b] == "gasburner":
                    if "gasburner" not in inventory:
                        pygame.mixer.Sound.play(gasburner_clip)
                        player_score += 10
                        inventory.append("gasburner")
                        item_rects.remove(item)
                        del item_ids[b]

                elif item_ids[b] == "knife":
                    if "knife" not in inventory:
                        player_score += 6
                        item_rects.remove(item)
                        pygame.mixer.Sound.play(knife_pickup)
                        inventory.append("knife")
                        del item_ids[b]

                elif item_ids[b] == "coffeemug":
                    if "coffeemug" not in inventory:
                        player_score += 5
                        item_rects.remove(item)
                        inventory.append("coffeemug")
                        pygame.mixer.Sound.play(coffeemug_sound)
                        del item_ids[b]

                elif item_ids[b] == "ss_bonuscard":
                    if "ss_bonuscard" not in inventory:
                        player_score += 30
                        item_rects.remove(item)
                        inventory.append("ss_bonuscard")
                        pygame.mixer.Sound.play(ss_sound)
                        del item_ids[b]

                elif item_ids[b] == "lappi_sytytyspalat":
                    if "lappi_sytytyspalat" not in inventory:
                        player_score += 40
                        item_rects.remove(item)
                        inventory.append("lappi_sytytyspalat")
                        pygame.mixer.Sound.play(lappi_sytytyspalat_sound)
                        del item_ids[b]

                elif item_ids[b] == "red_key":
                    player_keys["red"] = True
                    item_rects.remove(item)
                    play_key_pickup()
                    del item_ids[b]
                elif item_ids[b] == "green_key":
                    player_keys["green"] = True
                    item_rects.remove(item)
                    play_key_pickup()
                    del item_ids[b]
                elif item_ids[b] == "blue_key":
                    player_keys["blue"] = True
                    item_rects.remove(item)
                    play_key_pickup()
                    del item_ids[b]            
        b += 1
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
    rect.y += movement[1]
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
menu_gasburner_animation = Animation("main_menu_bc_gasburner", 2, 8,(255, 255, 255))
burning_tree = Animation("tree_burning", 4, 5,(0, 0, 0))
#endregion
#region Load Game

world_gen = load_map("resources/game_map")
item_gen = load_items("resources/item_map")

tile_rects, toilets, burning_toilets, trashcans, burning_trashcans = load_rects()
item_rects, item_ids, task_items = load_item_rects()
random.shuffle(task_items)

door_rects, doors_open, color_keys = load_doors()

ad_images = load_ads()

#endregion
#region Console

def console():
    global inventory, player_keys, player_health, koponen_happines

    command_input = input("command: ")
    command_input = command_input.lower()
    command_list = command_input.split()

    if command_list[0] == "give":
        if command_list[1] != "key":
            try:
                inventory.append(command_list[1])
                print("Item was given")
            except Exception:
                print("That item does not exist")
        elif command_list[1] == "key":
            try:
                player_keys[command_list[2]] = True
                print("Item was given")
            except Exception:
                print("That item does not exist")

    elif command_list[0] == "playboy":
        koponen_happines = 1000
        print("You are now a playboy")
        print("Koponen happines: {}".format(koponen_happines))

    elif command_list[0] == "kill":
        player_health = 0
    elif command_list[0] == "dstrms":
        setTerms = ""
        try:
            if command_list[1] == "true" or "True" or "T" or "t":
                setTerms = True
            elif command_list[1] == "false" or "False" or "F" or "f":
                setTerms = False
            else:
                setTerms = "[Error]"
                print("Please provide a proper state for terms & conditions")
        except Exception:
            if(setTerms != "[Error]"):
                configParser.set("Data", "TermsAccepted", command_list[1])
                with open("settings.cfg", "w") as cfgFile:
                    configParser.write(cfgFile)
                print("Terms and Conditions set as: " + command_list[1])
                print(Exception)

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
        logging.info("Terms and Conditions have been accepted.")
        logging.info("You said you will not get offended... Dick!")
        configParser.set("Data", "TermsAccepted", True)
        with open("settings.cfg", "w") as cfgFile:
            configParser.write(cfgFile)
        logging.debug("Terms Agreed. Updated Value: " + configParser.get("Data", "TermsAccepted"))

        return False

    buttons.append(pygame.Rect(249,353, 200, 160))
    texts.append(button_font1.render("I Agree", True, (255,255,255)))
    functions.append(agree)

    while tcagr_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tcagr_running = False
                main_running = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
        main_display.blit(agr_background, (0,0))

        y = 0
        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    tcagr_running = functions[y]()
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90,90,90)
                else:
                    button_color = (115,115,115)
            else:
                button_color = (100,100,100)

            pygame.draw.rect(main_display,button_color,button)

            main_display.blit(texts[y],(button.x+10,button.y+5))
            y += 1

        pygame.display.update()
        c = False

#endregion
#region Koponen Talk

def koponen_talk():
    global main_running, inventory, currently_on_mission, inventory, player_score, ad_images, task_items, playerMovingLeft, playerMovingRight, playerSprinting

    koponenTalking = True
    pygame.mouse.set_visible(True)

    playerMovingLeft = False
    playerMovingRight = False
    playerSprinting = False

    c = False

    exit_button = pygame.Rect(940,700,230, 80)
    mission_button = pygame.Rect(50,700,450,80)
    date_button = pygame.Rect(50, 610, 450,80)
    return_mission_button = pygame.Rect(510, 700, 420,80)

    koponen_talk_foreground = ad_images[int(random.uniform(0,len(ad_images)))].copy()

    def renderText(text):
        text_object = button_font1.render(text, True, (255,255,255))
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
            conversations.append("Koponen: Toisitko minulle {}".format(taskTaivutettu))
            currently_on_mission = True


    def date_function():
        global koponen_happines

        conversations.append("{}: Tulisitko kanssani treffeille?".format(player_name))

        if koponen_happines > 90:
            conversations.append("Koponen: Tulisin mielelläni kanssasi")
        elif 91 > koponen_happines > 70:
            if int(random.uniform(0,3)):
                conversations.append("Koponen: Kyllä ehdottomasti")
            else:
                conversations.append("Koponen: En tällä kertaa")
                koponen_happines -= 3
        elif 71 > koponen_happines > 50:
            if int(random.uniform(0,2)):
                conversations.append("Koponen: Tulen kanssasi")
            else:
                conversations.append("Koponen: Ei kiitos")
                koponen_happines -= 3
        elif 51 > koponen_happines > 30:
            if int(random.uniform(0,3)) == 3:
                conversations.append("Koponen: Tulen")
            else:
                conversations.append("Koponen: En tule")
                koponen_happines -= 7
        elif 31 > koponen_happines > 10:
            if int(random.uniform(0,5)) == 5:
                conversations.append("Koponen: Kyllä")
            else:
                conversations.append("Koponen: Ei.")
                koponen_happines -= 10
        else:
            conversations.append("Koponen: ...Ei")

    def end_mission():
        global current_mission, currently_on_mission, player_score, koponen_happines

        try:
            taskTaivutettu
        except NameError:
            logging.warning("Task not defined. Defining task...")
            task = ""
            taskTaivutettu = ""

        if not currently_on_mission:
            conversations.append("Koponen: Sinulla ei ole palautettavaa")
            conversations.append("         tehtävää")
        else:
            if current_mission in inventory:
                conversations.append("Koponen: Loistavaa työtä")
                conversations.append("Game: Player score +60")
                player_score += 60
                koponen_happines += 10
                inventory.remove(current_mission)
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
            if event.type == pygame.QUIT:
                koponenTalking = False
                main_running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponenTalking = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
        main_display.blit(koponen_talk_foreground,(0,0))
        pygame.draw.rect(main_display,(230,230,230),(40,40, 700, 400))
        pygame.draw.rect(main_display,(30,30,30),(40,40, 700, 400), 3)
        printer.resetRow()


        y = 0

        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    if not y:
                        koponenTalking = functions[y]()
                    else:
                        functions[y]()
                button_color = (115,115,115)
                    
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90,90,90)
            else:
                button_color = (100,100,100)
                
            if y == 0:
                text_offset = 60
            else:
                text_offset = 10
                
            pygame.draw.rect(main_display, button_color, button)
            main_display.blit(texts[y],(button.x+text_offset,button.y+14))
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
    c = False
    resume_button = pygame.Rect(150,170,200,30)
    settings_button = pygame.Rect(150,210,200,30)
    main_menu_button = pygame.Rect(150,250,200,30)

    resume_text = button_font.render("Resume", True, (255,255,255))
    settings_text = button_font.render("Settings", True, (255,255,255))
    main_menu_text = button_font.render("Main menu", True, (255,255,255))

    buttons = []
    functions = []
    texts = []

    texts.append(resume_text)
    texts.append(settings_text)
    texts.append(main_menu_text)

    def resume():
        global esc_menu
        esc_menu = False
        pygame.mouse.set_visible(False)
        pygame.mixer.music.unpause()

    def settings():
        settings_menu()
    def goto_main_menu():
        global esc_menu, go_to_main_menu
        esc_menu = False
        go_to_main_menu = True
        

    functions.append(resume)
    functions.append(settings)
    functions.append(goto_main_menu)

    buttons.append(resume_button)
    buttons.append(settings_button)
    buttons.append(main_menu_button)

    while esc_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global main_running
                main_running = False
                esc_menu = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    esc_menu = False
                    pygame.mouse.set_visible(False)
                    pygame.mixer.music.unpause()
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
        esc_menu_surface.fill((123,134,111))
        esc_menu_surface.blit(pygame.transform.scale(text_icon, (250,139)),(125,10))
        point = list(pygame.mouse.get_pos())
        point[0] -= display_size[0]/2-250
        point[1] -= 120
        y = 0
        for button in buttons:
            if button.collidepoint(point[0],point[1]):
                if c:
                    functions[y]()
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90,90,90)
                else:
                    button_color = (115,115,115)
            else:
                button_color = (100,100,100)
            pygame.draw.rect(esc_menu_surface,button_color,button)
            if y == 0:
                x = 50
            elif y == 1:
                x = 40
            else:
                x = 30

            esc_menu_surface.blit(texts[y],(button.x+x,button.y+3))
            y += 1

        main_display.blit(esc_menu_surface,(display_size[0]/2-250,120))
        pygame.display.update()
        c = False

    del buttons, resume_button, settings_button, main_menu_button, c, resume, settings, goto_main_menu, functions, texts, resume_text, settings_text, main_menu_text

def settings_menu():
    global main_menu_running, esc_menu, main_running, settings_running, volume
    c = False
    settings_running = True

    return_button = pygame.Rect(465, 700, 270, 60)
    music_slider = pygame.Rect(560,141,30,28)
    
    return_text = button_font1.render("Return", True, (255,255,255))

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

        volume_text = button_font1.render("Music Volume", True, (255,255,255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_menu_running = False
                esc_menu = False
                main_running = False
                settings_running = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
        
        main_display.blit(settings_background,(0,0))

        main_display.blit(volume_text,(190,130))
        pygame.draw.rect(main_display,(120,120,120),(560,145,340,20))
        

        music_slider.x = int(560 + (volume*100)*3.4-15)

        if pygame.mouse.get_pressed()[0] == False:
            dragSlider = False
            
        if music_slider.collidepoint(pygame.mouse.get_pos()):
            slider_color = (115,115,115)
            if pygame.mouse.get_pressed()[0]:
                dragSlider = True
        if dragSlider:
            slider_color = (90,90,90)
            position = int(pygame.mouse.get_pos()[0])
            if position < 560:
                position = 560
            if position > 900:
                position = 900
            position -= 560
            position = int(position/3.4)
            configParser.set("Settings", "Volume", position)
            with open("settings.cfg", "w") as cfgFile:
                configParser.write(cfgFile)
            volume = position/100
            pygame.mixer.music.set_volume(volume)
        else:
            slider_color = (100,100,100)

        pygame.draw.rect(main_display,(slider_color),music_slider)

        y = 0
        for button in buttons:

            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    functions[y]()
                    pass
                if pygame.mouse.get_pressed()[0]:
                    button_color = (90,90,90)
                else:
                    button_color = (115,115,115)
            else:
                button_color = (100,100,100)

            pygame.draw.rect(main_display,button_color,button)
            main_display.blit(texts[y],(button.x+50,button.y+6))
            y += 1

        c = False
        pygame.display.update()

def main_menu():
    global main_menu_running, main_running, go_to_main_menu
    go_to_main_menu = False
    main_menu_running = True
    c = False

    pygame.mixer.music.load("audio/lobbymusic.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(volume)

    play_button = pygame.Rect(450,180,300, 60)
    settings_button = pygame.Rect(450,250,300,60)
    quit_button = pygame.Rect(450, 320, 300, 60)

    play_text = button_font1.render("Play", True, (255,255,255))
    settings_text = button_font1.render("Settings", True, (255,255,255))
    quit_text = button_font1.render("Quit", True, (255,255,255))

    def play_function():
        pygame.mouse.set_visible(False)
        global main_menu_running
        main_menu_running = False
        load_music()
        pygame.mixer.music.play(1)
        pygame.mixer.music.set_volume(volume)
        global player_keys, player_hand_item
        player_hand_item = "none"
        player_rect.x = 100
        player_rect.y = 100
        for key in player_keys:
            player_keys[key] = False
        logging.info("Press F4 to commit suicide")
    def settings_function():
        settings_menu()

    def quit_function():
        global main_running, main_menu_running
        main_menu_running = False
        main_running = False

    buttons = []
    functions = []
    texts = []

    buttons.append(play_button)
    buttons.append(settings_button)
    buttons.append(quit_button)

    functions.append(play_function)
    functions.append(settings_function)
    functions.append(quit_function)

    texts.append(play_text)
    texts.append(settings_text)
    texts.append(quit_text)

    while main_menu_running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_menu_running = False
                main_running = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True

        main_display.blit(main_menu_background, (0, 0))
        main_display.blit(pygame.transform.flip(menu_gasburner_animation.update(), False, False), (625, 450))
        y = 0

        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    functions[y]()
                button_color = (115,115,115)
                if mouseLeftPressed:
                    button_color = (90,90,90)
            else:
                button_color = (100,100,100)
            if y == 0:
                text_offset = 100
            elif y == 1:
                text_offset = 40
            else:
                text_offset = 100
            pygame.draw.rect(main_display,button_color,button)
            main_display.blit(texts[y],(button.x+text_offset,button.y+6))

            y += 1

        pygame.display.update()
        c = False

#endregion
#region Check Terms
agr(tcagr)

if tcagr != "false":
    main_menu()
#endregion
#region Koponen Talk Tip Text
koponen_talk_tip = tip_font.render("Puhu Koposelle [E]", True, (255,255,255))
#endregion
#region Item Initialisation

logging.debug("Items Initialised: " + str(len(item_ids)))
for i_id in item_ids:
    logging.debug("Initialised Item: (ID)" + i_id)

#endregion
#region Events

while main_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main_running = False
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
                inventory_slot -= 1
            if event.key == K_k:
                inventory_slot += 1
            if event.key == K_t:
                console()
            if event.key == K_F3:
                DebugMode = not DebugMode
            if event.key == K_F4:
                F4Pressed = True
                if AltPressed == True and F4Pressed ==  True:
                    pygame.QUIT()
                else:
                    player_health = 0
            if event.key == K_LALT or event.key == K_RALT:
                AltPressed = True
                if AltPressed == True and F4Pressed ==  True:
                    pygame.QUIT()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseLeftPressed = True
                if player_hand_item == "gasburner":
                    gasburnerBurning = True
                if player_hand_item == "knife":
                    knifeInUse = True
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
            if event.key == K_p:
                if player_hand_item == "gasburner":
                    gasburnerBurning = False
                    gasburner_fire.stop()
                if player_hand_item == "knife":
                    knifeInUse = False
            if event.key == K_q:
                if inventory[inventory_slot] != "none":
                    inventory.remove(inventory[inventory_slot])
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                mouseLeftPressed = False
                if player_hand_item == "gasburner":
                    gasburnerBurning = False
                if player_hand_item == "knife":
                    knifeInUse = False
            if event.button == 4:
                inventory_slot += 1
            if event.button == 5:
                inventory_slot -= 1

#endregion
#region Inventory Code

    if inventory_slot > len(inventory)-1:
        inventory_slot = 0

    if inventory_slot < 0:
        inventory_slot = len(inventory)-1

    main_display.fill((20, 25, 20))
    screen.fill((20, 25, 20))

    true_scroll[0] += (player_rect.x-true_scroll[0]-285)/12
    true_scroll[1] += (player_rect.y-true_scroll[1]-220)/12
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
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
#region More Collisions
    y = 0
    for layer in world_gen:
        x = 0
        for tile in layer:
            if tile == 'b':
                screen.blit(floor1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'c':
                screen.blit(wall1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'd':
                screen.blit(table1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'e':
                screen.blit(toilet1, (x*34-scroll[0], y*34-scroll[1]+1))
            if tile == 'f':
                screen.blit(lamp1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'g':
                screen.blit(trashcan, (x*34-scroll[0]+2, y*34-scroll[1]+7))
            if tile == 'h':
                screen.blit(ground1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'i':
                screen.blit(grass, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'j':
                screen.blit(concrete1, (x*34-scroll[0], y*34-scroll[1]))
            if tile == 'o':
                screen.blit(bricks, (x*34-scroll[0], y*34-scroll[1]))
            if tile =='A':
                screen.blit(burning_tree.update(),(x*34-scroll[0],y*34-scroll[1]-50))
            if tile == 'p':
                screen.blit(planks, (x*34-scroll[0], y*34-scroll[1]))
            x += 1
        y += 1

    x = 0
    for door in door_rects:
        if doors_open[x]:
            screen.blit(door_open, (door.x-scroll[0]+2,door.y-scroll[1]))
        else:
            if color_keys[x] == "red":
                screen.blit(red_door_closed, (door.x-scroll[0], door.y-scroll[1]))
            elif color_keys[x] == "green":
                screen.blit(green_door_closed, (door.x-scroll[0], door.y-scroll[1]))
            elif color_keys[x] == "blue":
                screen.blit(blue_door_closed, (door.x-scroll[0], door.y-scroll[1]))
            else:
                screen.blit(door_closed, (door.x-scroll[0], door.y-scroll[1]))
        x += 1

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
            screen.blit(coffeemug, (item.x-scroll[0], item.y-scroll[1]+14))
        if item_ids[b] == "ss_bonuscard":
            screen.blit(ss_bonuscard, (item.x-scroll[0], item.y-scroll[1]+14))
        if item_ids[b] == "lappi_sytytyspalat":
            screen.blit(lappi_sytytyspalat, (item.x-scroll[0], item.y-scroll[1]+17))
        b += 1

#endregion
#region PlayerMovement

    if playerSprinting == False and playerStamina < 100.0:
        playerStamina += 0.25
    elif playerSprinting and playerStamina > 0:
        playerStamina -= 0.75
    elif playerSprinting and playerStamina <= 0:
        playerSprinting = False
    elif int(round(playerStamina)) < 0:
        playerStamina = 0.0

    player_movement = [0, 0]

    koponen_recog_rec.center = koponen_rect.center

    if playerMovingRight == True:
        player_movement[0] += 4
        if playerSprinting == True and playerStamina > 0:
            player_movement[0] += 4

    if playerMovingLeft == True:
        player_movement[0] -= 4
        if playerSprinting ==  True and playerStamina > 0:
            player_movement[0] -= 4

    player_movement[1] += vertical_momentum
    vertical_momentum += 0.4
    if vertical_momentum > 8:
        vertical_momentum = 8

#endregion
#region Even More Collisions

    toilet_collisions(player_rect,gasburnerBurning)
    if player_health > 0:
        player_rect, collisions = move(player_rect, player_movement, tile_rects)
    koponen_rect, k_collisions = move(koponen_rect, koponen_movement, tile_rects)

    if k_collisions["left"]:
        koponen_movingx = -koponen_movingx
    elif k_collisions["right"]:
        koponen_movingx = -koponen_movingx


    door_collision_test()

    #endregion
#region UI

    score = score_font.render(("Score: " + str(player_score)), True, (255,255,255))
    if DebugMode:
        fps = score_font.render("Fps: " + str(int(clock.get_fps())), True, (255,255,255))
    health = score_font.render("Health: " + str(player_health), True, (255,255,255))
    stamina = score_font.render("Stamina: " + str(round(int(playerStamina))), True, (255,255,255))

#endregion
#region Even Even More Collisions

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
                offset = 49
                offset_k = 75
            else:
                offset = 7
                offset_k = 10
            if player_hand_item == "gasburner":
                if gasburnerBurning:
                    if gasburner_animation_stats[0]:
                        gasburner_fire.stop()
                        pygame.mixer.Sound.play(gasburner_fire)
                    screen.blit(pygame.transform.flip(gasburner_animation[gasburner_animation_stats[0]], direction, False), (
                        player_rect.right-offset-scroll[0], player_rect.y-scroll[1]))
                else:
                    screen.blit(pygame.transform.flip(gasburner_off, direction, False),
                        (player_rect.right-offset-scroll[0], player_rect.y-scroll[1]))

            if player_hand_item == "knife":
                if knifeInUse:
                    screen.blit(pygame.transform.flip(knife_animation[knife_animation_stats[0]], direction, False), (
                        player_rect.right-offset_k-scroll[0], player_rect.y-scroll[1]+14))
                else:
                    screen.blit(pygame.transform.flip(knife, direction, False), (
                        player_rect.right-offset-scroll[0], player_rect.y-scroll[1]+14))

            if player_hand_item == "coffeemug":
                screen.blit(pygame.transform.flip(coffeemug, direction, False), (
                    player_rect.right-offset-scroll[0], player_rect.y-scroll[1]+14))

    if player_keys["red"] == True:
        screen.blit(red_key, (10, 20))
    if player_keys["green"] == True:
        screen.blit(green_key, (24, 20))
    if player_keys["blue"] == True:
        screen.blit(blue_key, (38, 20))

#endregion
#region Koponen Tip

    if player_rect.colliderect(koponen_recog_rec):
        screen.blit(koponen_talk_tip,(koponen_recog_rec.topleft[0]-scroll[0],koponen_recog_rec.topleft[1]-scroll[1]-10))
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
            screen.blit(toilet_animation[toilet_animation_stats[0]], (toilet.x-scroll[0]+2, toilet.y-scroll[1]+1))
        h += 1
    h = 0

    for trashcan2 in trashcans:
        if burning_trashcans[h] == True:
            screen.blit(trashcan_animation[toilet_animation_stats[0]], (trashcan2.x-scroll[0]+3, trashcan2.y-scroll[1]+6))
        h+=1

    screen.blit(koponen_animation[koponen_animation_stats[0]], (
        koponen_rect.x-scroll[0], koponen_rect.y-scroll[1]))

    if player_health or player_death_event:
        screen.blit(pygame.transform.flip(animation[animation_image], direction, False), (
            player_rect.x-scroll[0], player_rect.y-scroll[1]))
    else:
        screen.blit(pygame.transform.flip(player_corpse, direction, False), (
            player_rect.x-scroll[0], player_rect.y-scroll[1]))

#endregion
#region Debug Mode

    screen.blit(score, (10, 55))
    if DebugMode:
        screen.blit(fps, (10, 10))

#endregion
#region Inventory Rendering

    y = 0
    for item in inventory:
        if item != "none":
            if item == "gasburner":
                screen.blit(gasburner_off,(y*34+15,80))
            elif item == "knife":
                screen.blit(knife,(y*34+15,80))
            elif item == "coffeemug":
                screen.blit(coffeemug,(y*34+15,80))
            elif item == "ss_bonuscard":
                screen.blit(ss_bonuscard,(y*34+15,80))
            elif item == "lappi_sytytyspalat":
                screen.blit(lappi_sytytyspalat,(y*34+15,80))
            y+=1
    if inventory_slot:
        pygame.draw.rect(screen,(70,70,70),((inventory_slot-1)*34+10,75, 34,34),4)
    else:
        pygame.draw.rect(screen,(70,70,70),((len(inventory)-1)*34+10,75, 34,34),4)
    screen.blit(health, (10, 120))
    screen.blit(stamina, (10, 130))

#endregion
#region Rendering
    main_display.blit(pygame.transform.scale(screen, display_size), (0, 0))
    pygame.display.update()
#endregion
#region Conditional Events

    if esc_menu:
        pygame.mixer.music.pause()
        screen.blit(alpha,(0,0))
        main_display.blit(pygame.transform.scale(screen, display_size), (0, 0))
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
    toilet_animation_stats[2] += 1
    koponen_animation_stats[2] += 1

#endregion
#region Ticks
    tick += 1
    if tick > 60:
        tick = 0
    clock.tick(60)
#endregion