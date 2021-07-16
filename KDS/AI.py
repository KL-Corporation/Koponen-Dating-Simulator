from __future__ import annotations

from enum import IntEnum, auto
import math
import random
from tkinter.filedialog import Directory
from typing import List, Optional, Sequence, Tuple, Union

import pygame
import pygame.draw

import KDS.Animator
import KDS.Audio
import KDS.Colors
import KDS.Convert
import KDS.Logging
import KDS.Math
import KDS.Missions
import KDS.World
import KDS.Build
import KDS.Debug

pygame.mixer.init()
pygame.init()
pygame.key.stop_text_input()

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

def searchRect(targetRect: pygame.Rect, searchRect: pygame.Rect, direction: bool, surface: pygame.Surface, scroll: Sequence[int], obstacles: List[List[List[KDS.Build.Tile]]],  maxAngle: int = 40, maxSearchUnits: int = 24) -> Tuple[bool, float]:
    if direction:
        if targetRect.x > searchRect.x:
            return False, 0
    elif targetRect.x < searchRect.x:
        return False, 0

    angle = KDS.Math.GetAngle2((searchRect.centerx, searchRect.centery), (targetRect.x + 5, targetRect.y + 5))
    if abs(angle) < maxAngle:
        return False, 0
    if angle > 0:
        angle = 90 - angle
    elif angle < 0: # Why the fuck this check is here? I don't think you need to not run this if it's zero
        angle = -90 - angle
    slope = KDS.Math.getSlope2(angle)
    dirVar = KDS.Convert.ToMultiplier(direction)
    searchPointers = [(searchRect.centerx + x * 30 * dirVar, searchRect.centery + x * 30 * dirVar * slope) for x in range(maxSearchUnits)]
    for pointer in searchPointers:
        # pygame.draw.rect(surface, KDS.Colors.EmeraldGreen, (int(pointer[0]) - scroll[0], int(pointer[1]) - scroll[1], 3, 3))
        x = int(pointer[0] / 34)
        y = int(pointer[1] / 34)
        max_x = len(obstacles[0]) - 1
        max_y = len(obstacles) - 1
        end_x = min(x + 1, max_x)
        end_y = min(y + 1, max_y)

        if end_x > max_x:
            end_x = max_x
        if end_y > max_y:
            end_y = max_y
        for row in obstacles[y:end_y]:
            for unit in row[x:end_x]:
                if len(unit) > 0:
                    for tile in unit:
                        if KDS.Debug.Enabled:
                            pygame.draw.rect(surface, KDS.Colors.Red, (tile.rect.x - scroll[0], tile.rect.y - scroll[1], 34, 34))
                        if tile.checkCollision:
                            return False, 0.0
                        if tile.rect.colliderect(targetRect):
                            return True, slope
                else:
                    if KDS.Debug.Enabled:
                        pygame.draw.rect(surface, KDS.Colors.Red, (int(pointer[0]) - scroll[0], int(pointer[1]) - scroll[1], 13, 13))
                    if targetRect.collidepoint( (int(pointer[0]), int(pointer[1]))):
                        return True, slope
    return False, 0.0

#region Old Bulldog
# class Bulldog:
#
#     a = False
#
#     def __init__(self, position: Tuple[int, int], health: int, speed: int, animation):
#         self.position = position
#         self.health = health
#         self.speed = speed
#         self.rect = pygame.Rect(position[0], position[1], 44, 32)
#         self.direction = False
#         self.movement = [speed, 8]
#         self.hits = {'top': False, 'bottom': False, 'right': False, 'left': False}
#         self.playDeathAnimation = False
#         self.a = False
#
#         self.animation = animation
#         self.damage = 0
#
#     def startUpdateThread(self, _rect, tile_rects):
#
#         def _update(self, __rect, tile_rects):
#             def __move(rect, movement, tiles):
#                 def collision_test(rect, tiles):
#                     hit_list = []
#                     for tile in tiles:
#                         if rect.colliderect(tile):
#                             hit_list.append(tile)
#                     return hit_list
#
#                 collision_types = {'top': False, 'bottom': False,
#                                 'right': False, 'left': False}
#                 rect.x += movement[0]
#                 hit_list = collision_test(rect, tiles)
#                 for tile in hit_list:
#                     if movement[0] > 0:
#                         rect.right = tile.left
#                         collision_types['right'] = True
#                     elif movement[0] < 0:
#                         rect.left = tile.right
#                         collision_types['left'] = True
#                 rect.y += int(movement[1])
#                 hit_list = collision_test(rect, tiles)
#                 for tile in hit_list:
#                     if movement[1] > 0:
#                         rect.bottom = tile.top
#                         collision_types['bottom'] = True
#                     elif movement[1] < 0:
#                         rect.top = tile.bottom
#                         collision_types['top'] = True
#                 return rect, collision_types
#
#             j = self.animation.update()
#             del j
#
#             if not self.rect.colliderect(__rect) or self.a == False:
#                 self.damage = 0
#                 if self.a:
#                     if self.rect.x > __rect.x:
#                         self.direction = True
#                         if self.movement[0] > -1:
#                             self.movement[0] = -self.movement[0]
#                     else:
#                         self.direction = False
#                         if self.movement[0] < 1:
#                             self.movement[0] = -self.movement[0]
#
#                 self.rect, self.hits = __move(self.rect, self.movement, tile_rects)
#                 if self.hits["right"] or self.hits["left"]:
#                     self.movement[0] = -self.movement[0]
#             else:
#                 self.damage = 100
#
#         bdThread = threading.Thread(target=_update,args=[self, _rect, tile_rects])
#         bdThread.start()
#
#     def SetAngry(self, state: bool):
#         self.a = state
#
#     def getAttributes(self):
#         if not self.a:
#             if self.movement[0] < 0:
#                 self.direction = True
#             elif self.movement[0] > 0:
#                 self.direction = False
#         return self.rect, self.animation.get_frame(), self.direction, self.damage
#
#     def AI_Update(self, surface: pygame.Surface, scroll: Tuple[int, int], render_rect: pygame.Rect):
#         if not self.a:
#             if self.movement[0] < 0:
#                 self.direction = True
#             elif self.movement[0] > 0:
#                 self.direction = False
#         if self.rect.colliderect(render_rect):
#             surface.blit(pygame.transform.flip(self.animation.get_frame(), self.direction, False),(self.rect.x - scroll[0], self.rect.y - scroll[1]))
#         return self.damage
#endregion

class HostileEnemy:
    def __init__(self, pos: Tuple[int, int]):
        pass

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        if not self.enabled:
            return

        if value < self._health and value > 0:
            self.sleep = False

        self._health = max(value, 0)

    def internalInit(self, rect : pygame.Rect, w: KDS.Animator.Animation, a: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, sight_sound: Optional[pygame.mixer.Sound], death_sound: Optional[pygame.mixer.Sound], health: int, mv: List[int], attackPropability: int, sleep: bool = True, direction: bool = False):
        self.rect = rect
        self._health = health
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
        self.allowJump: bool = True
        self.collisions = KDS.World.Collisions()

        self.enabled = True
        self.listener = None
        self.listenerInstance: Optional[KDS.Missions.Listener] = None
        self.listenerRegistered = False

        self.mover = KDS.World.EntityMover()

    def lateInit(self):
        if self.listener != None and not self.listenerRegistered:
            self.enabled = False
            self.listenerRegistered = True
            tmpListener: Optional[Union[KDS.Missions.Listener, KDS.Missions.ItemListener]] = getattr(KDS.Missions.Listeners, self.listener, None)
            if tmpListener != None and not isinstance(tmpListener, KDS.Missions.ItemListener):
                self.listenerInstance = tmpListener
                self.listenerInstance.OnTrigger += self.listenerTrigger
        if self.direction:
            self.movement[0] = -self.movement[0]

    def onDeath(self) -> List[int]:
        return []

    def attack(self, slope, env_obstacles, target, *args) -> List[KDS.World.Bullet]:
        KDS.Logging.AutoError(f"{type(self).__name__} attack is not overloaded!")
        return []

    def listenerTrigger(self):
        self.enabled = True
        assert self.listenerInstance != None, "Why have we been triggered by a listener when listenerInstance is None????"
        self.listenerInstance.OnTrigger -= self.listenerTrigger
        self.listenerInstance = None

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
        enemyProjectiles: List[KDS.World.Bullet] = []
        dropItems: List[int] = []

        if self.health:
            s = searchRect(targetRect=targetRect, searchRect=self.rect, direction=self.direction, surface=Surface, scroll=scroll, obstacles=tiles)[0]
        else:
            s = False
        if s:
            self.sleep = False

        self.lateUpdate(Surface, scroll, tiles, targetRect)

        if self.health > 0:
            if not self.sleep:
                if s:
                    if not self.attackRunning and not self.manualAttackHandling:
                        if not random.randint(0, self.a_propability):
                            self.attackRunning = True
                if self.attackRunning:
                    self.animation.trigger("attack")
                    if self.animation.active.done:
                        df, sl2 = searchRect(targetRect=targetRect, searchRect=self.rect, direction=self.direction, surface=Surface, scroll=scroll, obstacles=tiles)
                        if df:
                            enemyProjectiles = self.attack((sl2 * -1) * 3, tiles, targetRect)
                        self.attakF = False
                        self.attackRunning = False
                        self.animation.active.tick = 0
                else:
                    if self.playSightSound:
                        if self.sight_sound != None:
                            KDS.Audio.PlaySound(self.sight_sound)
                        self.playSightSound = False
                    self.collisions = self.mover.move(self.rect, self.movement, tiles)
                    if self.collisions.right or self.collisions.left:
                        self.movement[0] = -self.movement[0]
                        self.direction = not self.direction
                        if self.allowJump:
                            self.AI_jump(tiles, self.collisions, Surface, scroll)
                    self.animation.trigger("walk")
            else:
                _ = self.mover.move(self.rect, [0,8], tiles)
                self.animation.trigger("idle")
        elif self.playDeathSound:
            self.animation.trigger("death")
            if self.death_sound != None:
                KDS.Audio.PlaySound(self.death_sound)
            items = self.onDeath()
            KDS.Missions.Listeners.EnemyDeath.Trigger()
            for item in items:
                if item:
                    dropItems.append(item)
            self.playDeathSound = False

        self.onBeforeRender()
        if KDS.Debug.Enabled:
            pygame.draw.rect(Surface, KDS.Colors.Orange, pygame.Rect(self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height))
        Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        return enemyProjectiles, dropItems

    def lateUpdate(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
        return

    def onBeforeRender(self):
        return

    def AI_jump(self, obstacles: List[List[List[KDS.Build.Tile]]], collisions: KDS.World.Collisions, surface: pygame.Surface, scroll: Sequence[int]):
        x_coor: float = self.rect.x
        if collisions.right:
            x_coor += self.rect.width
        elif collisions.left:
            x_coor -= 34 # Collision check does not work on doors
        x_coor /= 34
        y_coor = (self.rect.y + self.rect.h) / 34 - 1

        jump: bool
        try:
            jump = True
            obst = None
            for y in range(math.ceil(self.rect.h / 34) * 2 - 2):
                for obst in obstacles[int(y_coor) - 1 - y][int(x_coor)]:
                    if obst.checkCollision:
                        jump = False
                        break
            if KDS.Debug.Enabled:
                if obst != None:
                    pygame.draw.rect(surface, KDS.Colors.Orange, (obst.rect.x - scroll[0] - 3, obst.rect.y - scroll[1] - 3, obst.rect.width + 6, obst.rect.height + 6), width=3)
                debug_x = int(x_coor)
                debug_y_start = int(y_coor) - 1
                debug_y_end = debug_y_start - math.ceil(self.rect.h / 34)
                pygame.draw.line(surface, KDS.Colors.Cyan, (debug_x * 34 - scroll[0], debug_y_start * 34 - scroll[1]), (debug_x * 34 - scroll[0], debug_y_end * 34 - scroll[1]), 3)
        except Exception as e:
            KDS.Logging.AutoError(e)
            jump = False

        if jump:
            self.direction = not self.direction
            self.movement[0] = -self.movement[0]
            self.rect.y -= 35

class Imp(HostileEnemy):
    def __init__(self, pos):
        health = 65
        w_anim = KDS.Animator.Animation("imp_walking", 4, 11, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("imp_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("imp_attacking", 2, 27, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("imp_dying", 5, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 55)
        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=imp_sight_sound, death_sound=imp_death_sound, health=health, mv=[1, 8], attackPropability=40)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        impAttack.set_volume(dist)
        KDS.Audio.PlaySound(impAttack)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, 6, env_obstacles, random.randint(20, 50), texture=imp_fireball, maxDistance=2000, slope=KDS.Math.getSlope(self.rect.center, target.center)*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        return [0]

class SergeantZombie(HostileEnemy):
    def __init__(self, pos):
        health = 30
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8], attackPropability=60)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        shotgunShot.set_volume(dist)
        KDS.Audio.PlaySound(shotgunShot)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 35), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        items = []
        if random.choice([True, False]):
            items.append(17)
        return items

class DrugDealer(HostileEnemy):
    def __init__(self, pos):
        health = 25
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=drug_dealer_sight, death_sound=drug_dealer_death_sound, health=health, mv=[2, 8], attackPropability=20)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        pistol_shot.set_volume(dist)
        KDS.Audio.PlaySound(pistol_shot)
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
        health = 55
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=random.choice([d_anim0, d_anim1]), i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8], attackPropability=80)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        double_barrel_fire.set_volume(dist)
        KDS.Audio.PlaySound(double_barrel_fire)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 20), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction)+(3-fd)*1.5 ) for fd in range(6)]

    def onDeath(self):
        items = []
        if random.choice([True, False]):
            items.append(17)
        return items

class MafiaMan(HostileEnemy):
    def __init__(self, pos):
        health = 30
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=mafiaman_sight, death_sound=mafiaman_death, health=health, mv=[1, 8], attackPropability=40)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        basicGunshot.set_volume(dist)
        KDS.Audio.PlaySound(basicGunshot)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        if random.choice([True, False, False, False, False, False, False]):
            items.append(32)
        return items

class MethMaker(HostileEnemy):
    def __init__(self, pos):
        health = 65
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=methmaker_death, health=health, mv=[2, 8], attackPropability=50)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        basicGunshot.set_volume(dist)
        KDS.Audio.PlaySound(basicGunshot)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery - 20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center) * 18 * KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        if random.choice([True, False, False, False, False]):
            items.append(11)
        elif random.choice([True, False, False]):
            items.append(27)
        return items

class CaveMonster(HostileEnemy):
    def __init__(self, pos):
        health = 50
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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=cavemonster_sight, death_sound=cavemonster_death, health=health, mv=[2, 8], attackPropability=50)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        cavemonster_gun.set_volume(dist)
        KDS.Audio.PlaySound(cavemonster_gun)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery - 20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 25), slope=KDS.Math.getSlope(self.rect.center, target.center) * 18 * KDS.Convert.ToMultiplier(self.direction) )]

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
        health = 60
        w_anim = KDS.Animator.Animation("mummy_walking", 8, 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("mummy_walking", 2, 16, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("mummy_attack", 3, 12, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("mummy_dying", 10, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0]-17, pos[1]-38, 51, 72)

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=random.choice(Mummy.soundboard_scream), death_sound=Mummy.sound_death, health=health, mv=[1, 8], attackPropability=50)

        self.manualAttackHandling = True
        self.timeSinceLastSwitch: int = 0

    def attack(self, slope, env_obstacles, target, *args):
        KDS.Audio.PlaySound(random.choice(Mummy.soundboard_hits))
        return [KDS.World.Bullet(pygame.Rect(self.rect.centerx + (self.rect.width / 2 + 1) * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(20, 35), maxDistance=18, slope=KDS.Math.getSlope(self.rect.center, target.center) * 18 * KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        return items

    # def pathfinder(self, obstacles: List[List[List[KDS.Build.Tile]]], collision_type : str) -> None:
    #     x_coor = 0
    #     if collision_type == "right":
    #         x_coor = (self.rect.x + self.rect.w) // 34
    #     else:
    #         x_coor = (self.rect.x) // 34
    #     y_coor = (self.rect.y) // 34
    #     try:
    #         jump = True
    #         for y in range(3):
    #             # if not obstacles[y_coor - 1 + y][x_coor].checkCollision:
    #             if all(not AaroTääVitunKoodiEiToimiUudenVitunTilesysteeminKaaPerkele.checkCollision for AaroTääVitunKoodiEiToimiUudenVitunTilesysteeminKaaPerkele in obstacles[y_coor - 1 + y][x_coor]):
    #                 jump = False
    #         if jump:
    #             self.direction = not self.direction
    #             self.movement[0] = -self.movement[0]
    #             self.rect.y -= 35
    #     except Exception as e:
    #         KDS.Logging.AutoError(e)

    # def lateUpdate(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
    #     if not self.sleep and self.health > 0:
    #         s = searchRect(targetRect=targetRect, searchRect=self.rect, direction= self.direction, surface=Surface, scroll=scroll, obstacles=tiles)[0]
    #         s1 = searchRect(targetRect=targetRect, searchRect=self.rect, direction= not self.direction, surface=Surface, scroll=scroll, obstacles=tiles)[0]
    #         if self.collisions != None:
    #             if self.collisions.right:
    #                 self.pathfinder(tiles, "right")
    #             elif self.collisions.left:
    #                 self.pathfinder(tiles, "left")
    #
    #         if s or s1:
    #             if self.rect.centerx < targetRect.centerx:
    #                 self.movement[0] = abs(self.movement[0])
    #                 self.direction = False
    #             elif self.rect.centerx > targetRect.centerx:
    #                 self.movement[0] = abs(self.movement[0]) * -1
    #                 self.direction = True
    #         dist = KDS.Math.getDistance(self.rect.center, targetRect.center)
    #         if dist < 40 and not self.attackRunning:
    #             self.attackRunning = True
    #         if random.randint(0, 500) == 69 and dist < 560:
    #             KDS.Audio.PlaySound(random.choice(Mummy.soundboard_scream[1:]))

    # Toivottavasti en raiskannu liikaa Aaron kaunista Mummy AI logiikkaa... Tän pitäis sentään toimia
    def lateUpdate(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
        if self.sleep or self.health <= 0:
            return

        self.timeSinceLastSwitch += 1

        targetDirection = self.rect.centerx > targetRect.centerx
        if self.direction != targetDirection:
            s, _ = searchRect(targetRect, self.rect, targetDirection, Surface, scroll, tiles)
            if s and self.timeSinceLastSwitch > 60 and not self.attackRunning:
                self.direction = targetDirection
                self.movement[0] = abs(self.movement[0]) * (-1 if self.direction else 1)
                self.timeSinceLastSwitch = 0

        dist = KDS.Math.getDistance(self.rect.midbottom, targetRect.midbottom)
        if dist < 40:
            self.attackRunning = True
        if random.randint(0, 500) == 69 and dist < 560:
            KDS.Audio.PlaySound(random.choice(Mummy.soundboard_scream[1:]))

class SecurityGuard(HostileEnemy):
    sight_sounds = (
        pygame.mixer.Sound("Assets/Audio/Entities/security_guard_wakeup.ogg"),
        pygame.mixer.Sound("Assets/Audio/Entities/security_guard_wakeup1.ogg"),
        pygame.mixer.Sound("Assets/Audio/Entities/security_guard_wakeup2.ogg")
    )

    death_sound = pygame.mixer.Sound("Assets/Audio/Entities/security_guard_death.ogg")

    def __init__(self, pos):
        health = 1250

        w_anim = KDS.Animator.Animation("security_guard_walking", 4, 11, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("security_guard_idle", 2, 40, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("security_guard_shooting", 2, 1, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("security_guard_dying", 5, 13, KDS.Colors.Cyan, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0] - 20, pos[1] - 23, 40, 73)

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

        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=random.choice(SecurityGuard.sight_sounds), death_sound=SecurityGuard.death_sound, health=health, mv=[1, 8], attackPropability=40)

    def lateInit(self):
        super().lateInit()
        self.lastTargetDirection = KDS.Math.Sign(self.movement[0])
        self.ticksSinceSwitch = 0

    def update(self, Surface: pygame.Surface, scroll: Union[Tuple[int, int], List[int]], tiles, targetRect: pygame.Rect):
        tmp = super().update(Surface, scroll, tiles, targetRect)
        distance = self.rect.centerx - targetRect.centerx
        targetDirection = KDS.Math.Sign(distance)
        if self.lastTargetDirection != targetDirection and (abs(distance) > 170 or self.ticksSinceSwitch > 120) and self.health > 0: # If over five blocks away from target or hasn't turned for two seconds while player is behind; turn around
            self.direction = not self.direction
            self.movement[0] = -self.movement[0]
            self.lastTargetDirection = targetDirection
            self.ticksSinceSwitch = 0
        self.ticksSinceSwitch += 1
        return tmp

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = KDS.Math.Clamp(dist, 0, 1200)
        dist = 1200 - dist
        dist /= 1200
        KDS.Audio.PlayFromFile("Assets/Audio/Entities/gunshot_basic2.ogg", dist)
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(15, 40), slope=KDS.Math.getSlope(self.rect.center, target.center) * 18 * KDS.Convert.ToMultiplier(self.direction) )]

    def onDeath(self):
        items = []
        return items

class Bulldog(HostileEnemy):
    def __init__(self, pos: Tuple[int, int]):
        health = 10
        w_anim = KDS.Animator.Animation("bulldog", 5, 2, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = w_anim
        a_anim = w_anim
        d_anim = w_anim
        rect = pygame.Rect(pos[0], pos[1], 44, 30)

        self.internalInit(rect, w_anim, a_anim, d_anim, i_anim, None, None, health, [5, 8], KDS.Math.MAXVALUE)
        self.manualAttackHandling = True
        self.disableDamage: bool = False

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        if not self.enabled:
            return

        if value < self._health and value > 0:
            self.sleep = False

        if not self.disableDamage:
            self._health = max(value, 0)

    def lateInit(self):
        self.normalMovement = self.movement
        super().lateInit()

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
        bullets: List[KDS.World.Bullet] = []
        if self.rect.colliderect(targetRect):
            self.movement = [0, 8]
            bullets = self.attack(69, tiles, targetRect)
        else:
            self.movement = self.normalMovement if not self.direction else [-self.normalMovement[0], self.normalMovement[1]]

        super().update(Surface, scroll, tiles, targetRect)
        distance = self.rect.centerx - targetRect.centerx
        self.direction = distance > 0
        return bullets, []

    def attack(self, slope, env_obstacles: List[List[List[KDS.Build.Tile]]], target: pygame.Rect, *args) -> List[KDS.World.Bullet]:
        if random.randint(0, 30) == 0:
            return [KDS.World.Bullet(pygame.Rect((self.rect.centerx + (KDS.Math.Ceil(self.rect.width / 2) + 6) * KDS.Convert.ToMultiplier(self.direction)) - 5, self.rect.centery, 10, 10), self.direction, 1, env_obstacles, 10, maxDistance=2)]
        return []

class Zombie(HostileEnemy):
    def __init__(self, pos):
        health = 25
        w_anim = KDS.Animator.Animation("z_walk", 3, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("z_walk", 3, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("z_attack", 4, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        d_anim = KDS.Animator.Animation("z_death", 5, 10, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1] - 36, 34, 55)
        self.internalInit(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=None, death_sound=None, health=health, mv=[1, 8], attackPropability=40)
        self.manualAttackHandling = True
        self.sleep = False
        self.movementBeforeFreeze = self.movement
        self.attackAnim = False
        self.allowJump = False

    def update(self, Surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], targetRect: pygame.Rect):
        bullets: List[KDS.World.Bullet] = []
        self.attackAnim = False
        if self.health > 0 and self.rect.colliderect(targetRect):
            if self.movement[0] != 0:
                self.movementBeforeFreeze = self.movement
            self.movement = [0, 8]
            bullets = self.attack(69, tiles, targetRect)
            self.attackAnim = True
        elif self.movement[0] == 0:
            self.movement = self.movementBeforeFreeze
        super().update(Surface, scroll, tiles, targetRect)
        return bullets, []

    def onBeforeRender(self):
        if self.attackAnim:
            self.animation.trigger("attack")

    def attack(self, slope, env_obstacles, target, *args):
        if random.randint(0, 60) == 0:
            return [KDS.World.Bullet(pygame.Rect((self.rect.centerx + (KDS.Math.Ceil(self.rect.width / 2) + 6) * KDS.Convert.ToMultiplier(self.direction)) - 5, self.rect.centery, 10, 10), self.direction, 1, env_obstacles, 10, maxDistance=2)]
        return []