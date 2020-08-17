import os, pygame
from pygame.locals import *
import threading

pygame.init()
display_size = (1600, 800)

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")
main = True

clock = pygame.time.Clock()

inputThread_running = False

input_data = ""
input_text = ""
txt = ""

background_color = True
dark_mode = True

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
iron_bars = pygame.image.load("Assets/Textures/Building/iron_bars_texture.png").convert()
soil = pygame.image.load("Assets/Textures/Building/soil.png")
mossy_bricks = pygame.image.load("Assets/Textures/Building/mossy_bricks.png")
archvile = pygame.image.load("Assets/Textures/Animations/archvile_run_0.png")
zombie = pygame.image.load("Assets/Textures/Animations/z_attack_0.png")
serg = pygame.image.load("Assets/Textures/Animations/seargeant_shooting_1.png")
stone = pygame.image.load("Assets/Textures/Building/stone.png").convert()
hay = pygame.image.load("Assets/Textures/Building/hay.png").convert()
soil1 = pygame.image.load("Assets/Textures/Building/soil_2.png").convert()
wood = pygame.image.load("Assets/Textures/Building/wood.png").convert()

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

tip_font = pygame.font.Font("gamefont2.ttf", 23, bold=0, italic=0)

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
                    'V': archvile,
                    'v': stone,
                    'w': hay,
                    'å': soil1,
                    'ä': wood,
                    'C': landmine_texture,
                    'l':red_door_closed,
                    'n':green_door_closed,
                    'm':blue_door_closed}



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

dark_colors = [(50,50,50),(20,25,20),(230,230,230),(255,0,0)]
light_colors = [(240,230,234), (210,220,214),(20,20,20),(0,0,255)]

if dark_mode:
    colors = dark_colors.copy()
else:
    colors = light_colors.copy()

current_block = "a"
current_modifier = "none"

toplayer = pygame.Surface(display_size)

def inputThread(in_text=None):
    global inputThread_running, main, input_data, data_counter, current_block
    inputThread_running = True

    if in_text is None:
        input_text = "Command: "
    else:
        input_text = in_text

    data = input(input_text)
    
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

def material_selector(prev_material):
    material_selector_running = True

    material_list = []
    selector_rects = []

    scrl = 0

    #region bs
    x = len(tile_textures) + len(item_textures)
    x = int(x/4)
    for _ in range(x+1):
        material_list.append([])
        selector_rects.append([])
    #endregion

    p = 0
    index = 0
    y = 0
    x = 0
    for q in tile_textures:
        material_list[index].append(q)
        selector_rects[index].append(pygame.Rect(x*200,y*180, 120, 120))
        p += 1
        x += 1
        if p > 3:
            p = 0
            x = 0
            y += 1
            index += 1

    p = 0
    for q in item_textures:
        material_list[index].append(q)
        selector_rects[index].append(pygame.Rect(x*200,y*180, 120, 120))
        p += 1
        x += 1
        if p > 3:
            p = 0
            x = 0
            y += 1
            index += 1

    while material_selector_running:
        main_display.fill(colors[1])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                material_selector_running = False
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    material_selector_running = False
                    return prev_material
                if event.key == K_e:
                    material_selector_running = False
                    return prev_material
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    scrl -= 60
                    if scrl < 0:
                        scrl = 0
                elif event.button == 5:
                    scrl += 60
        y = 0
        for row in selector_rects:
            x = 0
            for rct in row:
                pygame.draw.rect(main_display,(255,100,100), (rct.x+100,rct.y-scrl,rct.width,rct.height))
                if material_list[y][x] in tile_textures:
                    main_display.blit(pygame.transform.scale(tile_textures[material_list[y][x]],(rct.width,rct.height)),(rct.x+100,rct.y-scrl))
                elif material_list[y][x] in item_textures:
                    main_display.blit(pygame.transform.scale(item_textures[material_list[y][x]],(rct.width,rct.height)),(rct.x+100,rct.y-scrl))
                if rct.collidepoint((pygame.mouse.get_pos()[0]-100,pygame.mouse.get_pos()[1]+scrl)):
                    pygame.draw.rect(main_display,(255,255,255), (rct.x+100,rct.y-scrl,rct.width,rct.height),3)
                    if pygame.mouse.get_pressed()[0]:
                        material_selector_running = False
                        return material_list[y][x]
                x += 1
            y += 1

        pygame.display.update()
        clock.tick(45)

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
            elif event.button == 2:
                ps = pygame.mouse.get_pos()
                ps = list(ps)
                ps[0] += scroll
                ps[1] += scroll_y
                y = 0
                for row in tile_rects:
                    x = 0
                    for tile in row:
                        if tile.collidepoint(ps):
                            if textmap[y][x] != "a":
                                current_block = textmap[y][x]
                            elif item_map[y][x] != "a":
                                current_block = item_map[y][x]
                            else:
                                current_block = "a"
                        x += 1
                    y += 1
        if event.type == KEYDOWN:
            if event.key == K_p:
                print(scroll)
            if event.key == K_LSHIFT:
                shiftPressed = True
            if event.key == K_F4:
                if colors[0][0] == 50:
                    colors = light_colors.copy()
                else:
                    colors = dark_colors.copy()
            if event.key == K_e:
                current_block = material_selector(current_block)
                if current_block in tile_textures:
                    current_modifier = "tile"
                elif current_block in item_textures:
                    current_modifier = "item"
                elif current_block == "a":
                    pass
                else:
                    current_modifier = "none"
        if event.type == KEYUP:
            if event.key == K_LSHIFT:
                shiftPressed = False

    if not inputThread_running and main == True:
        thread = threading.Thread(target=inputThread, args=[txt])
        thread.start()

    main_display.fill((20,20,29))
    toplayer.fill(colors[0])

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
        try:
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
        except Exception:
            print("Please state the level size (int,int)")
            data_counter = 0

    else:
        pass

    y = 0


    for layer in textmap:
        x = 0
        for tile in layer:
            if tile in tile_textures:
                toplayer.blit(    pygame.transform.scale(     tile_textures[tile]   ,(int(rectwidth),int(rectheight))     ), (x * rectwidth-scroll, y * rectheight-scroll_y)    )
            elif tile == "a":
                if background_color:
                    pygame.draw.rect(toplayer,colors[1], (x*rectwidth-scroll,y*rectheight-scroll_y, rectheight,rectheight))
            x += 1
        y += 1
    y = 0
    for layer in item_map:
        x = 0
        for item in layer:
            if item in item_textures:
                toplayer.blit(    pygame.transform.scale(     item_textures[item]   ,(int(rectwidth),int(rectheight))     ), (x * rectwidth-scroll, y * rectheight-scroll_y)    )
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
                crds = tip_font.render(str(x) + " , " + str(y), True, colors[3])
                toplayer.blit(crds,(display_size[0]-100,display_size[1]-30))

                pygame.draw.rect(toplayer, colors[2], (tile.x-scroll,tile.y-scroll_y,tile.width,tile.height), 3)

                if pygame.mouse.get_pressed()[0]:
                    if current_modifier == "tile":
                        textmap[y][x] = current_block
                    elif current_modifier == "item":
                        item_map[y][x] = current_block
            x += 1
        y += 1

    main_display.blit(toplayer,(0,0))

    pygame.display.update()
    clock.tick(45)

pygame.display.quit()
pygame.quit()