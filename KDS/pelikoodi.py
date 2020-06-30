import pygame
import os
import random
from pygame.locals import *

#Testi kommentti 6969420

pygame.init()

display_size = (1200, 800)
screen_size = (600, 400)
        
class pygame_print_text:

    def __init__(self, color, topleft, width, display):
        self.text_font = pygame.font.Font("COURIER.ttf", 30, bold=0, italic=0)
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
        

main_display = pygame.display.set_mode(display_size)
screen = pygame.Surface(screen_size)
printer = pygame_print_text((7,8,10),(50,50),680,main_display)

esc_menu_surface = pygame.Surface((500, 400))
alpha = pygame.Surface(screen_size)
alpha.fill((0,0,0))
alpha.set_alpha(170)

pygame.display.set_caption("Koponen dating simulator")
game_icon = pygame.image.load("resources/game_icon.png")
main_menu_background = pygame.image.load("resources/main_menu_bc.png")
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

gasburner_off = pygame.image.load(
    "resources/items/gasburner_off.png").convert()
#gasburner_on = pygame.image.load("resources/items/gasburner_on.png").convert()
knife = pygame.image.load("resources/items/knife.png").convert()
knife_blood = pygame.image.load("resources/items/knife.png").convert()
red_key = pygame.image.load("resources/items/red_key.png").convert()
green_key = pygame.image.load("resources/items/green_key2.png").convert()
blue_key = pygame.image.load("resources/items/blue_key.png").convert()
coffeemug = pygame.image.load("resources/items/coffeemug.png").convert()
ss_bonuscard = pygame.image.load("resources/items/ss_bonuscard.png").convert()
gasburner_off.set_colorkey((255, 255, 255))
knife.set_colorkey((255, 255, 255))
knife_blood.set_colorkey((255, 255, 255))
red_key.set_colorkey((255,255,255))
green_key.set_colorkey((255,255,255))
blue_key.set_colorkey((255,255,255))
coffeemug.set_colorkey((255,255,255))
ss_bonuscard.set_colorkey((255,0,0))


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
main_running = True
playerMovingRight = False
playerMovingLeft = False
gasburnerBurning = False
knifeInUse = False
currently_on_mission = False
current_mission = "none"
player_name = "Sinä"

with open("settings/volume.txt", 'r') as f:
    volume_data = f.read()

with open("settings/tc.agr", "r") as f:
    tcagr = f.read()
    print(tcagr)

volume = float(volume_data)/100
gasburner_animation_stats = [0, 4, 0]
knife_animation_stats = [0, 10, 0]
toilet_animation_stats = [0,5,0]
koponen_animation_stats = [0,7,0]
player_hand_item = "none"
player_keys = {"red":False,"green":False,"blue":False}
direction = True
SpaceBar = False
esc_menu = False

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

def play_key_pickup():
    pygame.mixer.Sound.play(key_pickup)

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
    print(music_files)

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
    print(ad_files)

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
                    player_rect.right = door.left+1
                if not doors_open[x]:
                    if SpaceBar:
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
                    player_rect.left = door.right-1

        x += 1


def item_collision_test(rect, items):
    hit_list = []
    b = 0
    global player_hand_item, player_score, inventory
    for item in items:
        if rect.colliderect(item):
            hit_list.append(item)
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
                    player_score += 5
                    item_rects.remove(item)
                    inventory.append("ss_bonuscard")
                    pygame.mixer.Sound.play(ss_sound)
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
knife_animation = load_animation("knife",2)
toilet_animation = load_animation("toilet_anim",3)
trashcan_animation = load_animation("trashcan",3)
koponen_stand = load_animation("koponen_standing",2)
koponen_run = load_animation("koponen_running",2)
death_animation = load_animation("death",5)


world_gen = load_map("resources/game_map")
item_gen = load_items("resources/item_map")

tile_rects, toilets, burning_toilets, trashcans, burning_trashcans = load_rects()
item_rects, item_ids, task_items = load_item_rects()
random.shuffle(task_items)

door_rects, doors_open, color_keys = load_doors()

ad_images = load_ads()

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
        try:
            if command_list[1] == "true" or "false":
                with open("settings/tc.agr", "w") as f:
                    f.write(command_list[1])
            else:
                print("Please provide a proper state for terms & conditions")
        except Exception:
            print(Exception)


def agr(tcagr):

    if tcagr == "false":
        tcagr_running = True
    else:
        tcagr_running = False

    global main_running
    c = False

    buttons = []
    texts = []
    functions = []

    def agree():
        print("dick")
        with open("settings/tc.agr", "w") as f:
            f.write("true")
        with open("settings/tc.agr", "r") as f:
            print(f.read())

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


def koponen_talk():
    global main_running, inventory, currently_on_mission, inventory, player_score, ad_images, task_items
    koponen_talk_running = True
    c = False
    exit_button = pygame.Rect(940,700,230, 80)
    mission_button = pygame.Rect(50,700,450,80)
    date_button = pygame.Rect(50, 610, 450,80)
    return_mission_button = pygame.Rect(510, 700, 420,80)

    koponen_talk_background = ad_images[int(random.uniform(0,len(ad_images)))].copy()

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
        global currently_on_mission, current_mission

        conversations.append("{}: Saisinko tehtävän?".format(player_name))
        if currently_on_mission:
            conversations.append("Koponen: Olen pahoillani, sinulla on")
            conversations.append("         tehtävä kesken")
        elif task_items:
            currently_on_mission = True
            current_mission = task_items[0]
            task_items.remove(task_items[0])
            if current_mission == "coffeemug":
                task = "kahvikupin"
            elif current_mission == "ss_bonuscard":
                task = "SS-etukortin"
            conversations.append("Koponen: Toisitko minulle {}".format(task))
        else:
            conversations.append("Koponen: Olet suorittanut kaikki")
            conversations.append("         tehtävät")
            
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
                conversations.append("Koponen: Sinä et ole suorittanut")
                conversations.append("         haluamaani tehtävää")

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


    while koponen_talk_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                koponen_talk_running = False
                main_running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koponen_talk_running = False
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
        main_display.blit(koponen_talk_background,(0,0))
        pygame.draw.rect(main_display,(230,230,230),(40,40, 700, 400))
        pygame.draw.rect(main_display,(30,30,30),(40,40, 700, 400), 3)
        printer.resetRow()


        y = 0

        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    if not y:
                        koponen_talk_running = functions[y]()
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

def esc_menu_f():
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
        clock.tick(60)

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

        if music_slider.collidepoint(pygame.mouse.get_pos()):
            slider_color = (115,115,115)
            if pygame.mouse.get_pressed()[0]:
                slider_color = (90,90,90)
                position = int(pygame.mouse.get_pos()[0])
                if position < 560:
                    position = 560
                if position > 1000:
                    position = 900
                position -= 560
                position = int(position/3.4)
                with open("settings/volume.txt", 'w') as f:
                    f.write(str(position))
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
        print("Press F4 to commit suicide")
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

        main_display.blit(main_menu_background,(0,0))

        y = 0

        for button in buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                if c:
                    functions[y]()
                button_color = (115,115,115)
                if pygame.mouse.get_pressed()[0]:
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

agr(tcagr)

if tcagr != "false":
    main_menu()

koponen_talk_tip = tip_font.render("Puhu Koposelle [Space]", True, (255,255,255))
print(item_ids)

while main_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main_running = False

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                playerMovingRight = True
            if event.key == K_LEFT:
                playerMovingLeft = True
            if event.key == K_UP:
                if air_timer < 6:
                    vertical_momentum = -10
            if event.key == K_p:
                if player_hand_item == "gasburner":
                    gasburnerBurning = True
                if player_hand_item == "knife":
                    knifeInUse = True
            if event.key == K_SPACE:
                SpaceBar = True
            if event.key == K_ESCAPE:
                esc_menu = False if esc_menu else True
            if event.key == K_j:
                inventory_slot -= 1
            if event.key == K_k:
                inventory_slot += 1
            if event.key == K_t:
                console()
            if event.key == K_F4:
                player_health = 0
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                playerMovingRight = False
            if event.key == K_LEFT:
                playerMovingLeft = False
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
            if event.button == 4:
                inventory_slot += 1
            if event.button == 5:
                inventory_slot -= 1

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

    if player_health < 1 and not animation_has_played:
        player_death_event = True
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(player_death_sound)
        player_death_sound.set_volume(0.5)
        animation_has_played = True

    item_collision_test(player_rect, item_rects)
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
                screen.blit(tree,(x*34-scroll[0],y*34-scroll[1]-50))
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
        b += 1

    player_movement = [0, 0]

    koponen_recog_rec.center = koponen_rect.center

    if playerMovingRight == True:
        player_movement[0] += 4
    if playerMovingLeft == True:
        player_movement[0] -= 4

    player_movement[1] += vertical_momentum
    vertical_momentum += 0.4
    if vertical_momentum > 8:
        vertical_momentum = 8

    toilet_collisions(player_rect,gasburnerBurning)
    if player_health > 0:
        player_rect, collisions = move(player_rect, player_movement, tile_rects)
    koponen_rect, k_collisions = move(koponen_rect, koponen_movement, tile_rects)

    if k_collisions["left"]:
        koponen_movingx = koponen_movingx*-1
    elif k_collisions["right"]:
        koponen_movingx = koponen_movingx*-1


    door_collision_test()

    score = score_font.render(("Score: " + str(player_score)), True, (230, 240, 220))
    fps = score_font.render("Fps: " + str(int(clock.get_fps())), True, (255,255,255))
    health = score_font.render("Health: " + str(player_health), True, (255,255,255))

    if collisions['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
    else:
        air_timer += 1
    if collisions['top'] == True:
        vertical_momentum = 0

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
            

        else:
            animation = stand_animation.copy()
            animation_duration = 10
    else:
        if player_death_event:
            animation = death_animation.copy()
            animation_duration = 10


    if koponen_movement[0] != 0:
        koponen_animation = koponen_run.copy()
    else:
        koponen_animation = koponen_stand.copy()


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

    if player_rect.colliderect(koponen_recog_rec):
        screen.blit(koponen_talk_tip,(koponen_recog_rec.topleft[0]-scroll[0],koponen_recog_rec.topleft[1]-scroll[1]-10))
        koponen_movement[0] = 0
        if knifeInUse:
            koponen_alive = False
        if SpaceBar:
            koponen_talk()
    else:
        koponen_movement[0] = koponen_movingx
    h = 0

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

    screen.blit(score, (10, 50))
    screen.blit(fps, (10, 60))

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
            y+=1
    if inventory_slot:
        pygame.draw.rect(screen,(70,70,70),((inventory_slot-1)*34+10,75, 34,34),4)
    else:
        pygame.draw.rect(screen,(70,70,70),((len(inventory)-1)*34+10,75, 34,34),4)
    screen.blit(health,(10,120))

    main_display.blit(pygame.transform.scale(screen, display_size), (0, 0))
    pygame.display.update()
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
    SpaceBar = False
    toilet_animation_stats[2] += 1
    koponen_animation_stats[2] += 1
    clock.tick(60)
