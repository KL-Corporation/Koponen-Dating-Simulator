import concurrent.futures
import math
import multiprocessing
import random
import threading
from typing import List, Tuple, Union

import numpy
import pygame

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.World

pygame.mixer.init()
pygame.init()
pygame.key.stop_text_input()

def ai_collision_test(rect, Tile_list):
    hit_list = []

    max_x = len(Tile_list[0]) - 1
    max_y = len(Tile_list) - 1
    x = KDS.Math.Clamp(int(rect.x / 34 - 3), 0, max_x)
    y = KDS.Math.Clamp(int(rect.y / 34 - 3), 0, max_y)
    end_x = KDS.Math.Clamp(x + 6, 0, max_x)
    end_y = KDS.Math.Clamp(y + 6, 0, max_y)

    for row in Tile_list[y:end_y]:
        for unit in row[x:end_x]:
            for tile in unit:
                if rect.colliderect(tile.rect) and not tile.air and tile.checkCollision:
                    hit_list.append(tile.rect)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False,
                       'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = ai_collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += int(movement[1])
    hit_list = ai_collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

imp_sight_sound = pygame.mixer.Sound("Assets/Audio/Entities/imp_sight.ogg")
imp_death_sound = pygame.mixer.Sound("Assets/Audio/Entities/imp_death.ogg")
zombie_sight_sound = pygame.mixer.Sound("Assets/Audio/Entities/zombie_sight.ogg")
zombie_death_sound = pygame.mixer.Sound("Assets/Audio/Entities/zombie_death.ogg")
shotgunShot = pygame.mixer.Sound("Assets/Audio/effects/shotgun_shoot.ogg")
cavemonster_gun = pygame.mixer.Sound("Assets/Audio/Entities/cavemonster_fire.ogg")
impAttack = pygame.mixer.Sound("Assets/Audio/entities/dsfirsht.ogg")
double_barrel_fire = pygame.mixer.Sound("Assets/Audio/Entities/double_barrel_fire.ogg")
basicGunshot = pygame.mixer.Sound("Assets/Audio/Entities/gunshot_basic1.ogg")
pistol_shot = pygame.mixer.Sound("Assets/Audio/Effects/pistol_shoot.ogg")
drug_dealer_sight = pygame.mixer.Sound("Assets/Audio/entities/dshight.ogg")
drug_dealer_death_sound = pygame.mixer.Sound("Assets/Audio/entities/ddth.ogg")
mafiaman_sight = pygame.mixer.Sound("Assets/Audio/entities/mafiaman_sight.ogg")
mafiaman_death = pygame.mixer.Sound("Assets/Audio/entities/mafiaman_death.ogg")
cavemonster_sight = pygame.mixer.Sound("Assets/Audio/entities/cavemonster_sight.ogg")
cavemonster_death = pygame.mixer.Sound("Assets/Audio/entities/cavemonster_death.ogg")
methmaker_death = pygame.mixer.Sound("Assets/Audio/entities/methmaker_death.ogg")
imp_sight_sound.set_volume(0.4)
imp_death_sound.set_volume(0.5)
zombie_sight_sound.set_volume(0.4)
zombie_death_sound.set_volume(0.5)

def init():
    global imp_fireball

    imp_fireball = pygame.image.load("Assets/Textures/Animations/imp_fireball.png").convert()
    imp_fireball.set_colorkey((255, 255, 255))

def searchForPlayer(targetRect, searchRect, direction, Surface, scroll, obstacles,  maxAngle=40, maxSearchUnits=24):
    if direction:
        if targetRect.x > searchRect.x:
            return False, 0
    else:
        if targetRect.x < searchRect.x:
            return False, 0

    angle = KDS.Math.getAngle((searchRect.centerx, searchRect.centery), targetRect.topleft)
    if abs(angle) < maxAngle:
        return False, 0
    if angle > 0:
        angle = 90-angle
    elif angle < 0:
        angle = -90 - angle
    slope = KDS.Math.getSlope2(angle)
    dirVar = KDS.Convert.ToMultiplier(direction)
    searchPointers = [(searchRect.centerx + x * 30 *dirVar, searchRect.centery + x * 30 * dirVar*slope) for x in range(maxSearchUnits)]
    for pointer in searchPointers:

        x = int(pointer[0] / 34)
        y = int(pointer[1] / 34)
        end_y = y + 1
        end_x = x + 1
        max_x = len(obstacles[0]) - 1
        max_y = len(obstacles) - 1

        if end_x > max_x:
            end_x = max_x
        if end_y > max_y:
            end_y = max_y
        for row in obstacles[y:end_y]:
            for unit in row[x:end_x]:
                for tile in unit:
                    if KDS.Logging.profiler_running:
                        pygame.draw.rect(Surface, KDS.Colors.Red, (tile.rect.x-scroll[0], tile.rect.y-scroll[1], 34, 34))
                    if not tile.air:
                        if tile.checkCollision:
                            return False, 0
                    if tile.rect.colliderect(targetRect):
                        return True, slope
    return False, 0

class Bulldog:

    a = False

    def __init__(self, position: Tuple[int, int], health: int, speed: int, animation):
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

    def AI_Update(self, surface: pygame.Surface, scroll: Tuple[int, int], render_rect: pygame.Rect):
        if not self.a:
            if self.movement[0] < 0:
                self.direction = True
            elif self.movement[0] > 0:
                self.direction = False
        if self.rect.colliderect(render_rect):
            surface.blit(pygame.transform.flip(self.animation.get_frame(), self.direction, False),(self.rect.x - scroll[0], self.rect.y - scroll[1]))
        return self.damage

class HostileEnemy:
    def __init__(self, rect : pygame.Rect, w: KDS.Animator.Animation, a: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, sight_sound: pygame.mixer.Sound, death_sound: pygame.mixer.Sound, health, mv, attackPropability, sleep = True, direction = False, listener: str = None):
        self.rect = rect
        self.health = health
        self.sleep = sleep
        self.direction = direction

        self.animation = KDS.Animator.MultiAnimation(walk = w, attack = a, death = d, idle = i)

        self.a_propability = attackPropability
        self.sight_sound = sight_sound
        self.death_sound = death_sound

        self.target_found = False
        self.playDeathSound = True
        self.playSightSound = True
        self.attackF = False
        self.attackRunning = False
        self.manualAttackHandling = False
        self.movement = mv
        self.clearlagcounter = 0
        self.c = None

        self.enabled = True

        # Currently there is no way to assign a listener.
        if listener != None:
            self.enabled = False
            listenerInstance = getattr(KDS.Missions.Listeners, listener, None)
            if listenerInstance != None and isinstance(listenerInstance, KDS.Missions.ItemListener):
                listenerInstance.OnTrigger += lambda: setattr(self, "enabled", True) # Have to do it like this, because = does not work in lamda.

    def onDeath(self):
        return []

    def attack(self, slope, env_obstacles, target, *args):
        KDS.Logging.AutoError("This code should not execute.")
        return []

    def update(self, Surface: pygame.Surface, scroll: Union[Tuple[int, int], List[int]], tiles, targetRect, debug: bool = False):
        enemyProjectiles = None
        dropItems = []

        if self.health:
            s = searchForPlayer(targetRect=targetRect, searchRect=self.rect, direction=self.direction, Surface=Surface, scroll=scroll, obstacles=tiles)[0]
        else:
            s = False
        if s:
            self.sleep = False

        self.lateUpdate(tiles, targetRect, debug, scroll, Surface)

        if self.health > 0 and not self.sleep:
            if s:
                if not self.attackRunning and not self.manualAttackHandling:
                    if not random.randint(0, self.a_propability):
                        self.attackRunning = True
            if self.attackRunning:
                self.animation.trigger("attack")
                if self.animation.active.done:
                    df, sl2 = searchForPlayer(targetRect=targetRect, searchRect=self.rect, direction=self.direction, Surface=Surface, scroll=scroll, obstacles=tiles)
                    if df:
                        enemyProjectiles = self.attack((sl2 * -1) * 3, tiles, targetRect)
                    self.attakF = False
                    self.attackRunning = False
                    self.animation.active.tick = 0
            else:
                if self.playSightSound:
                    KDS.Audio.PlaySound(self.sight_sound)
                    self.playSightSound = False
                self.rect, self.c = move(self.rect, self.movement, tiles)
                if self.c["right"] or self.c["left"]:
                    self.movement[0] = -self.movement[0]
                    self.direction = not self.direction
                self.animation.trigger("walk")
        elif self.health > 0:
            self.rect, c = move(self.rect, [0,8], tiles)
            self.animation.trigger("idle")
        elif self.health < 1:
            if self.playDeathSound:
                KDS.Audio.PlaySound(self.death_sound)
                items = self.onDeath()
                for item in items:
                    if item:
                        dropItems.append(item)
                self.playDeathSound = False
            self.rect, c = move(self.rect, [0,8], tiles)
            self.animation.trigger("death")
            self.clearlagcounter += 1
            if self.clearlagcounter > 3600:
                self.clearlagcounter = 3600

        if debug:
            pygame.draw.rect(Surface, KDS.Colors.Orange, pygame.Rect(self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height))
        Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        return enemyProjectiles, dropItems

    def lateUpdate(self, *args):
        pass

    def dmg(self, dmgAmount):
        self.health -= dmgAmount
        if self.health < 0:
            self.health = 0

class Imp(HostileEnemy):
    def __init__(self, pos):
        health = 200
        w_anim = KDS.Animator.Animation("imp_walking", 4, 11, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("imp_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("imp_attacking", 2, 27, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("imp_dying", 5, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 55)
        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=imp_sight_sound, death_sound=imp_death_sound, health=health, mv=[1, 8], attackPropability=40)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        impAttack.set_volume(dist)
        KDS.Audio.PlaySound(impAttack)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, 6, env_obstacles, random.randint(20, 50), texture=imp_fireball, maxDistance=2000, slope=KDS.Math.getSlope(self.rect.center, target.center)*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        return [0]

class SergeantZombie(HostileEnemy):
    def __init__(self, pos):
        health = 125
        w_anim = KDS.Animator.Animation("seargeant_walking", 4, 11, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("seargeant_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("seargeant_shooting", 2, 1, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("seargeant_dying", 5, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 63)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        for _ in range(40):
            a_anim.images.append(aim_im)
        for _ in range(2):
            a_anim.images.append(shoot_im)
        for _ in range(10):
            a_anim.images.append(aim_im)
        a_anim.ticks = 51
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8], attackPropability=60)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        shotgunShot.set_volume(dist)
        KDS.Audio.PlaySound(shotgunShot)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 35), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        items = []
        if random.choice([True, False]):
            items.append(17)
        return items

class DrugDealer(HostileEnemy):
    def __init__(self, pos):
        health = 100
        w_anim = KDS.Animator.Animation("drug_dealer_walking", 5, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("drug_dealer_idle", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("drug_dealer_shooting", 4, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("drug_dealer_dying", 6, 6, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 35, 70)

        #region Handling the i_anim:
        af = a_anim.images.copy()
        a_anim.images.clear()
        for _ in range(30):
            a_anim.images.append(af[0])
        for __ in range(4):
            a_anim.images.append(af[16])
        for __ in range(4):
            a_anim.images.append(af[32])
        for __ in range(4):
            a_anim.images.append(af[63])

        a_anim.ticks = len(a_anim.images)-1
        del af
        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=drug_dealer_sight, death_sound=drug_dealer_death_sound, health=health, mv=[2, 8], attackPropability=20)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        pistol_shot.set_volume(dist)
        KDS.Audio.PlaySound(pistol_shot)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(40, 60), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        items = []
        if random.randint(0, 15) == 0:
            items.append(20)
        if random.randint(0, 4) == 0:
            items.append(11)
        return items

class TurboShotgunner(HostileEnemy):
    def __init__(self, pos):
        health = 220
        w_anim = KDS.Animator.Animation("turbo_shotgunner_walking", 4, 11, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("turbo_shotgunner_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("turbo_shotgunner_shooting", 2, 1, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim0 = KDS.Animator.Animation("turbo_shotgunner_dying", 6, 13, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim1 = KDS.Animator.Animation("turbo_shotgunner_dying1", 5, 13, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-24, 40, 58)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        for _ in range(50):
            a_anim.images.append(aim_im)
        for _ in range(2):
            a_anim.images.append(shoot_im)
        for _ in range(10):
            a_anim.images.append(aim_im)
        a_anim.ticks = 61
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=random.choice([d_anim0, d_anim1]), i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8], attackPropability=80)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        double_barrel_fire.set_volume(dist)
        KDS.Audio.PlaySound(double_barrel_fire)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 20), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction)+(3-fd)*1.5 ) for fd in range(6)]

    def onDeath(self):
        items = []
        if random.choice([True, False]):
            items.append(17)
        return items

class MafiaMan(HostileEnemy):
    def __init__(self, pos):
        health = 125
        w_anim = KDS.Animator.Animation("mafiaman_walking", 4, 11, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("mafiaman_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("mafiaman_shooting", 2, 1, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("mafiaman_dying", 5, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-19, 40, 53)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        for _ in range(20):
            a_anim.images.append(aim_im)
        for _ in range(2):
            a_anim.images.append(shoot_im)
        for _ in range(5):
            a_anim.images.append(aim_im)
        a_anim.ticks = 26
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=mafiaman_sight, death_sound=mafiaman_death, health=health, mv=[1, 8], attackPropability=40)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        basicGunshot.set_volume(dist)
        KDS.Audio.PlaySound(basicGunshot)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        if random.choice([True, False, False, False, False, False, False]):
            items.append(32)
        return items

class MethMaker(HostileEnemy):
    def __init__(self, pos):
        health = 250
        w_anim = KDS.Animator.Animation("methmaker_walking", 4, 11, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("methmaker_idle", 2, 16, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("methmaker_shooting", 2, 1, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("methmaker_dying", 5, 16, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-19, 40, 53)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        for _ in range(35):
            a_anim.images.append(aim_im)
        for _ in range(2):
            a_anim.images.append(shoot_im)
        for _ in range(8):
            a_anim.images.append(aim_im)
        a_anim.ticks = 44
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=methmaker_death, health=health, mv=[2, 8], attackPropability=50)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        basicGunshot.set_volume(dist)
        KDS.Audio.PlaySound(basicGunshot)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        if random.choice([True, False, False, False, False]):
            items.append(11)
        elif random.choice([True, False, False]):
            items.append(27)
        return items

class CaveMonster(HostileEnemy):
    def __init__(self, pos):
        health = 200
        w_anim = KDS.Animator.Animation("undead_monster_walking", 4, 11, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("undead_monster_walking", 2, 16, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("undead_monster_shooting", 2, 1, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("undead_monster_dying", 5, 16, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0]-20, pos[1]-23, 54, 57)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        for _ in range(40):
            a_anim.images.append(aim_im)
        for _ in range(2):
            a_anim.images.append(shoot_im)
        for _ in range(10):
            a_anim.images.append(aim_im)
        a_anim.ticks = 51
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=cavemonster_sight, death_sound=cavemonster_death, health=health, mv=[2, 8], attackPropability=50)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        cavemonster_gun.set_volume(dist)
        KDS.Audio.PlaySound(cavemonster_gun)
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        return items

class Mummy(HostileEnemy):
    soundboard_hits = (pygame.mixer.Sound("Assets/Audio/Entities/hit0.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/hit1.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/hit2.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/hit3.ogg"))

    soundboard_scream = (pygame.mixer.Sound("Assets/Audio/Entities/monster_scream.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/monster_growl.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/monster_growl2.ogg"),
                        pygame.mixer.Sound("Assets/Audio/Entities/monster_growl3.ogg")
                        )

    sound_death = pygame.mixer.Sound("Assets/Audio/Entities/monster_death.ogg")

    def __init__(self, pos):
        health = 200
        w_anim = KDS.Animator.Animation("mummy_walking", 8, 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("mummy_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("mummy_attack", 3, 12, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("mummy_dying", 10, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0]-17, pos[1]-38, 51, 72)

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=random.choice(Mummy.soundboard_scream), death_sound=Mummy.sound_death, health=health, mv=[1, 8], attackPropability=50)

        self.manualAttackHandling = True

    def attack(self, slope, env_obstacles, target, *args):
        KDS.Audio.PlaySound(random.choice(Mummy.soundboard_hits))
        return [KDS.World.Bullet(pygame.Rect(self.rect.centerx + (self.rect.width / 2 + 1) * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), maxDistance=18, slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        return items

    def lateUpdate(self, *args):
        if not self.sleep and self.health > 0:
            s = searchForPlayer(targetRect=args[1], searchRect=self.rect, direction= self.direction, Surface=args[4], scroll=args[3], obstacles=args[0])[0]
            s1 = searchForPlayer(targetRect=args[1], searchRect=self.rect, direction= not self.direction, Surface=args[4], scroll=args[3], obstacles=args[0])[0]
            if self.c != None:
                def AI_pathfinder(Mummy_o : Mummy, obstacles, collision_type : str):
                    x_coor = 0
                    if collision_type == "right":
                        x_coor = (Mummy_o.rect.x + Mummy_o.rect.w) // 34
                    else:
                        x_coor = (Mummy_o.rect.x) // 34
                    y_coor = (Mummy_o.rect.y) // 34
                    try:
                        jump = True
                        for y in range(3):
                            if not obstacles[y_coor - 1 + y][x_coor].air or not obstacles[y_coor - 1 + y][x_coor].checkCollision:
                                jump = False
                                return Mummy_o
                        if jump:
                            Mummy_o.direction = not Mummy_o.direction
                            Mummy_o.movement[0] = -Mummy_o.movement[0]
                            Mummy_o.rect.y -= 35
                        return Mummy_o
                    except IndexError:
                        return Mummy_o

                if self.c["right"]:
                    self = AI_pathfinder(self, args[0], "right")
                elif self.c["left"]:
                    self = AI_pathfinder(self, args[0], "left")

            if s or s1:
                if self.rect.centerx < args[1].centerx: self.movement[0] = abs(self.movement[0]); self.direction = False
                elif self.rect.centerx > args[1].centerx: self.movement[0] = abs(self.movement[0]) * -1; self.direction = True
            dist = KDS.Math.getDistance(self.rect.center, args[1].center)
            if dist < 40 and not self.attackRunning:
                self.attackRunning = True
            if random.randint(0, 500) == 69 and dist < 560: KDS.Audio.PlaySound(random.choice(Mummy.soundboard_scream[1:]))


class Projectile:
    pass

class Hitscanner:
    pass
