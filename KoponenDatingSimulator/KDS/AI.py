import pygame, threading, multiprocessing, numpy, math, random
import concurrent.futures
import KDS.Animator, KDS.Math, KDS.Colors
pygame.mixer.init()

def __collision_test(rect, Tile_list):
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

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False,
                       'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = __collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += int(movement[1])
    hit_list = __collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

imp_sight_sound = pygame.mixer.Sound("Assets/Audio/Entities/imp_sight.wav")
imp_death_sound = pygame.mixer.Sound("Assets/Audio/Entities/imp_death.wav")
zombie_sight_sound = pygame.mixer.Sound("Assets/Audio/Entities/zombie_sight.wav")
zombie_death_sound = pygame.mixer.Sound("Assets/Audio/Entities/zombie_death.wav")
imp_sight_sound.set_volume(0.4)
imp_death_sound.set_volume(0.5)
zombie_sight_sound.set_volume(0.4)
zombie_death_sound.set_volume(0.5)

def searchForPlayer(targetRect, searchRect, direction, Surface, scroll, obstacles,  maxAngle=40, maxSearchUnits=24):
    if direction:
        if targetRect.x > searchRect.x:
            return False
    else:
        if targetRect.x < searchRect.x:
            return False
            
    angle = KDS.Math.getAngle((searchRect.centerx, searchRect.centery), (targetRect.centerx, targetRect.centery))
    if KDS.Math.toPositive(angle) < maxAngle:
        return False
    if angle > 0:
        angle = 90-angle
    elif angle < 0:
        angle = -90 - angle
    slope = KDS.Math.getSlope2(angle)
    dirVar = KDS.Math.Jd(direction)
    searchPointers = [(searchRect.centerx + x * 30 *dirVar, searchRect.centery + x * 30 * dirVar*slope) for x in range(maxSearchUnits)]
    for pointer in searchPointers:
        
        x = int(pointer[0]/34)
        y = int(pointer[1]/34)
        end_y = y + 1
        end_x = x + 1
        max_x = len(obstacles[0])-1
        max_y = len(obstacles)-1

        if end_x > max_x:
            end_x = max_x
        if end_y > max_y:
            end_y = max_y
        for row in obstacles[y:end_y]:
            for tile in row[x:end_x]:
                pygame.draw.rect(Surface, (255,255, 0), (tile.rect.x-scroll[0], tile.rect.y-scroll[1], 34, 34))
                if not tile.air:
                    return False
                if tile.rect.colliderect(targetRect):
                    return True

class Zombie:


    def __init__(self, position, health, speed):
        self.position = position
        self.health = health
        self.speed = speed
        self.rect = pygame.Rect(position[0], position[1], 32, 64)
        self.walking = True
        self.direction = False
        self.movement = [speed, 8]
        self.hits = {}
        self.playDeathAnimation = True
        self.attacking = False
        self.true_movement = self.movement.copy()

    def search(self, search_object):

        if self.rect.colliderect(search_object):
            self.attacking = True
            return self.attacking

class Bulldog:

    a = False

    def __init__(self, position: tuple, health: int, speed: int, animation):
        self.position = position
        self.health = health
        self.speed = speed
        self.rect = pygame.Rect(position[0], position[1], 44, 32)
        self.direction = False
        self.movement = [speed, 8]
        self.hits = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.playDeathAnimation = False
        self.a = False

        self.animation = animation
        self.damage = 0

    def startUpdateThread(self, _rect, tile_rects):

        def _update(self, __rect, tile_rects):
            def __move(rect, movement, tiles):
                def collision_test(rect, tiles):
                    hit_list = []
                    for tile in tiles:
                        if rect.colliderect(tile):
                            hit_list.append(tile)
                    return hit_list

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

            j = self.animation.update()
            del j

            if not self.rect.colliderect(__rect) or self.a == False:
                self.damage = 0
                if self.a:
                    if self.rect.x > __rect.x:
                        self.direction = True
                        if self.movement[0] > -1:
                            self.movement[0] = -self.movement[0]
                    else:
                        self.direction = False
                        if self.movement[0] < 1:
                            self.movement[0] = -self.movement[0]

                self.rect, self.hits = __move(self.rect, self.movement, tile_rects)
                if self.hits["right"] or self.hits["left"]:
                    self.movement[0] = -self.movement[0]
            else:
                self.damage = 100

        bdThread = threading.Thread(target=_update,args=[self, _rect, tile_rects])
        bdThread.start()

    def SetAngry(self, state: bool):
        self.a = state

    def getAttributes(self):
        if not self.a:
            if self.movement[0] < 0:
                self.direction = True
            elif self.movement[0] > 0:
                self.direction = False
        return self.rect, self.animation.get_frame(), self.direction, self.damage

    def AI_Update(self, surface: pygame.Surface, scroll: (int, int), render_rect: pygame.Rect):
        if not self.a:
            if self.movement[0] < 0:
                self.direction = True
            elif self.movement[0] > 0:
                self.direction = False
        if self.rect.colliderect(render_rect):
            surface.blit(pygame.transform.flip(self.animation.get_frame(), self.direction, False),(self.rect.x - scroll[0], self.rect.y - scroll[1]))
        return self.damage

class HostileEnemy:
    def __init__(self, rect : pygame.Rect, w, a, d, i, sight_sound, death_sound, health, mv, sleep = True, direction = False):
        self.rect = rect
        self.health = 175
        self.sleep = sleep
        self.direction = direction
        self.w_anim = w
        self.a_anim = a
        self.d_anim = d
        self.i_anim = i

        self.sight_sound = sight_sound
        self.death_sound = death_sound

        self.target_found = False
        self.playDeathSound = True
        self.playSightSound = True
        self.attackF = False
        self.attackRunning = False
        self.movement = mv
        self.clearlagcounter = 0

    def update(self, Surface: pygame.Surface, scroll:[int, int], tiles, targetRect):
        s = searchForPlayer(targetRect=targetRect, searchRect=self.rect, direction=self.direction, Surface=Surface, scroll=scroll, obstacles=tiles)
        if s:
            self.sleep = False
            print(f"Pelaaja löytyi {random.randint(1, 100)}")
        if self.health > 0 and not self.sleep:
            if s:
                if not self.attackRunning:
                    if random.randint(1, 30) == 25:
                        print("Osui")
                        self.attackRunning = True
            if self.attackRunning:
                if self.attackF:
                    self.attack()
                    self.attakF = False
                animation, dResult = self.a_anim.update()
                Surface.blit(pygame.transform.flip(animation, self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
                if dResult:
                    self.attackRunning = False
            else:
                if self.playSightSound:
                    self.sight_sound.play()
                    self.playSightSound = False
                self.rect, c = move(self.rect, self.movement, tiles)
                if c["right"] or c["left"]:
                    self.movement[0] = -self.movement[0]
                    self.direction = not self.direction
                Surface.blit(pygame.transform.flip(self.w_anim.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        elif self.health > 0:
            self.rect, c = move(self.rect, [0,8], tiles)
            Surface.blit(pygame.transform.flip(self.i_anim.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))          
        elif self.health < 1:
            if self.playDeathSound:
                self.death_sound.play()
                self.playDeathSound = False
            self.rect, c = move(self.rect, [0,8], tiles)
            Surface.blit(pygame.transform.flip(self.d_anim.update()[0], self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
            self.clearlagcounter += 1
            if self.clearlagcounter > 3600:
                self.clearlagcounter = 3600

    def dmg(self, dmgAmount):
        self.health -= dmgAmount
        if self.health < 0:
            self.health = 0


class Imp(HostileEnemy):
    def __init__(self, pos):
        health = 200
        w_anim = KDS.Animator.Animation("imp_walking", 4, 11, KDS.Colors.GetPrimary.White, -1)
        i_anim = KDS.Animator.Animation("imp_walking", 2, 16, KDS.Colors.GetPrimary.White, -1)
        a_anim = KDS.Animator.Animation("imp_attacking", 2, 16, KDS.Colors.GetPrimary.White, 1)
        d_anim = KDS.Animator.Animation("imp_dying", 5, 16, KDS.Colors.GetPrimary.White, 1)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 55)
        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=imp_sight_sound, death_sound=imp_death_sound, health=health, mv=[1, 8])
        self.corpse = self.d_anim.images[-1]
    
    def attack(self):
        print("Imp")

class SergeantZombie(HostileEnemy):
    def __init__(self, pos):
        health = 125
        w_anim = KDS.Animator.Animation("seargeant_walking", 4, 11, KDS.Colors.GetPrimary.White, -1)
        i_anim = KDS.Animator.Animation("seargeant_walking", 2, 16, KDS.Colors.GetPrimary.White, -1)
        a_anim = KDS.Animator.Animation("seargeant_shooting", 2, 16, KDS.Colors.GetPrimary.White, 1)
        d_anim = KDS.Animator.Animation("seargeant_dying", 5, 16, KDS.Colors.GetPrimary.White, 1)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 55)
        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8])
        self.corpse = self.d_anim.images[-1]

    def attack(self):
        print("Sergeant")

class Projectile:
    pass

class Hitscanner:
    pass