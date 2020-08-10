import os, pygame
from pygame.locals import *
import threading

pygame.init()
display_size = (1600, 800)

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")
main = True

inputThread_running = False

input_data = ""

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
background_wall = pygame.image.load("Assets/Textures/Building/background_wall.png")
light_bricks = pygame.image.load("Assets/Textures/Building/light_bricks.png")
iron_bars = pygame.image.load("Assets/Textures/Building/iron_bars.png").convert()
soil = pygame.image.load("Assets/Textures/Building/soil.png")
mossy_bricks = pygame.image.load("Assets/Textures/Building/mossy_bricks.png")
archvile = pygame.image.load("Assets/Textures/Animations/archvile_run_0.png")
zombie = pygame.image.load("Assets/Textures/Animations/z_attack_0.png")
serg = pygame.image.load("Assets/Textures/Animations/seargeant_shooting_1.png")

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
medkit = pygame.image.load("Assets/Textures/Items/medkit.png").convert()
shotgun = pygame.image.load("Assets/Textures/Items/shotgun.png").convert()
shotgun_f = pygame.image.load("Assets/Textures/Items/shotgun_firing.png").convert()
shotgun_shells_t = pygame.image.load(
    "Assets/Textures/Items/shotgun_shells.png").convert()
iphone_texture = pygame.image.load("Assets/Textures/Items/iPuhelin.png").convert()


item_textures = {'0':gasburner_off,
                    '1': gasburner_off,
                    '2': knife,
                    '3': red_key,
                    '4': green_key,
                    '5': blue_key,
                    '6': ss_bonuscard,
                    '7': lappi_sytytyspalat,
                    '8': plasmarifle,
                    '9': cell,
                    '!': pistol_texture,
                    '#': pistol_mag,
                    '%': rk62_texture,
                    '&': rk62_mag,
                    '(': medkit,
                    ')': shotgun,
                    '=': shotgun_shells_t,
                    '+': soulsphere,
                    "'": turboneedle}

tile_textures = {'b': floor1,
                    'c': wall1,
                    'd': table1,
                    'e': toilet1,
                    'f': lamp1,
                    'g': trashcan,
                    'h': ground1,
                    'i': grass,
                    'j': concrete1,
                    'o': bricks,
                    'A': tree,
                    'p': planks,
                    'q': ladder_texture,
                    'r': light_bricks,
                    's': iron_bars,
                    't': soil,
                    'u': mossy_bricks,
                    'Z': zombie,
                    'S': serg,
                    'V': archvile}


data_counter = 0
textmap = []
item_map = []
rectMap = []
tile_rects = []
rectwidth = 0
rectheight = 0
scroll = 0
scroll_y = 0
shiftPressed = False

current_block = "a"
current_modifier = "none"

toplayer = pygame.Surface((2,2))

def inputThread():
    global inputThread_running, main, input_data, data_counter, current_block
    inputThread_running = True
    data = input("input -->  ")
    
    input_data = data
    data_counter += 1

    inputThread_running = False
    if data == "exit": 
        inputThread_running = True

    if not main:
        inputThread_running = True

    if len(data) == 1:
        current_block = data

def save(_tiles, Items):
    tile_string = ""
    item_string = ""

    for layer in _tiles:
        for tile in layer:
            tile_string = tile_string + tile
        tile_string = tile_string + "\n"

    for layer in Items:
        for item in layer:
            item_string = item_string + item
        item_string = item_string + "\n"

    with open("exportedMap_items.kds", "w") as file:
        file.write(item_string)
    with open("exportedMap_build.kds", "w") as file:
        file.write(tile_string)

while main:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main = False
            inputThread_running = True
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 4:
                if shiftPressed:
                    scroll_y -= rectwidth
                else:
                    scroll -= rectwidth
            elif event.button == 5:
                if shiftPressed:
                    scroll_y += rectwidth
                else:
                    scroll += rectwidth
        if event.type == KEYDOWN:
            if event.key == K_p:
                print(scroll)
            if event.key == K_LSHIFT:
                shiftPressed = True
        if event.type == KEYUP:
            if event.key == K_LSHIFT:
                shiftPressed = False

    if not inputThread_running and main == True:
        thread = threading.Thread(target=inputThread)
        thread.start()

    main_display.fill((20,20,29))
    toplayer.fill((230,240,240))

    if input_data == "exit":
        main = False
    if input_data == "export":
        save(textmap, item_map)
    if input_data in tile_textures:
        current_modifier = "tile"
    elif input_data in item_textures:
        current_modifier = "item"
    elif input_data == "a":
        pass
    else:
        current_modifier = "none"

    if data_counter == 1 and input_data != "" and input_data != "exit":
        q = input_data.split(",")

        wd = int(q[0])
        hg = int(q[1])

        for y in range(hg):
            row = []
            for x in range(wd):
                row.append("a")
            textmap.append(row)
            item_map.append(row)
        input_data = ""

        rectwidth = 50
        rectheight = 50

        y = 0
        u = 0
        for j in textmap:
            x = 0
            row = []
            for o in j:
                row.append(pygame.Rect(x*rectwidth, y*rectheight, rectwidth, rectheight))
                x += 1
            tile_rects.append(row)
            y += 1
        del toplayer
        toplayer = pygame.Surface((int(rectwidth*len(textmap[0])), int(rectheight*len(textmap))))

    else:
        pass

    y = 0

    for layer in textmap:
        x = 0
        for tile in layer:
            if tile in tile_textures:
                toplayer.blit(    pygame.transform.scale(     tile_textures[tile]   ,(int(rectwidth),int(rectheight))     ), (x * rectwidth, y * rectheight)    )
            x += 1
        y += 1
    y = 0
    for layer in item_map:
        x = 0
        for item in layer:
            if item in item_textures:
                toplayer.blit(    pygame.transform.scale(     item_textures[item]   ,(int(rectwidth),int(rectheight))     ), (x * rectwidth, y * rectheight)    )
            x += 1
        y += 1

    y = 0
    ps = pygame.mouse.get_pos()
    ps = list(ps)
    ps[0] += scroll
    ps[1] += scroll_y
    for row in tile_rects:
        x = 0
        for tile in row:
            if tile.collidepoint(ps):
                pygame.draw.rect(toplayer, (20,20,20), tile, 3)
                if pygame.mouse.get_pressed()[0]:
                    if current_modifier == "tile":
                        textmap[y][x] = current_block
                    elif current_modifier == "item":
                        item_map[y][x] = current_block
            x += 1
        y += 1

    main_display.blit(toplayer,(0-scroll,0-scroll_y))

    pygame.display.update()
