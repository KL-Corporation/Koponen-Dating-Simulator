import pygame, threading, multiprocessing, numpy, math, random
import concurrent.futures
import KDS.Animator, KDS.Math, KDS.Colors, KDS.Logging, KDS.World, KDS.Convert
pygame.mixer.init()
pygame.init()

Audio = None

def init(AudioClass):
    global Audio
    Audio = AudioClass

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
shotgunShot = pygame.mixer.Sound("Assets/Audio/effects/player_shotgun.wav")
impAtack = pygame.mixer.Sound("Assets/Audio/entities/dsfirsht.wav")
pistol_shot = pygame.mixer.Sound("Assets/Audio/Effects/pistolshot.wav")
drug_dealer_sight = pygame.mixer.Sound("Assets/Audio/entities/dshight.ogg")
drug_dealer_death_sound = pygame.mixer.Sound("Assets/Audio/entities/ddth.ogg")
imp_sight_sound.set_volume(0.4)
imp_death_sound.set_volume(0.5)
zombie_sight_sound.set_volume(0.4)
zombie_death_sound.set_volume(0.5)

initCompleted = False

imp_fireball = None
def initTextures():
    global initCompleted, imp_fireball

    imp_fireball = pygame.image.load("Assets/Textures/Animations/imp_fireball.png").convert()
    imp_fireball.set_colorkey((255,255,255))

    initCompleted = True

def searchForPlayer(targetRect, searchRect, direction, Surface, scroll, obstacles,  maxAngle=40, maxSearchUnits=24):
    if direction:
        if targetRect.x > searchRect.x:
            return False, 0
    else:
        if targetRect.x < searchRect.x:
            return False, 0
            
    angle = KDS.Math.getAngle((searchRect.centerx, searchRect.centery), targetRect.topleft)
    if KDS.Math.toPositive(angle) < maxAngle:
        return False, 0
    if angle > 0:
        angle = 90-angle
    elif angle < 0:
        angle = -90 - angle
    slope = KDS.Math.getSlope2(angle)
    dirVar = KDS.Convert.ToMultiplier(direction)
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
                if KDS.Logging.profiler_running:
                    pygame.draw.rect(Surface, KDS.Colors.GetPrimary.Red, (tile.rect.x-scroll[0], tile.rect.y-scroll[1], 34, 34))
                if not tile.air:
                    if tile.checkCollision:
                        return False, 0
                if tile.rect.colliderect(targetRect):
                    return True, slope
    return False, 0

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


    def __init__(self, rect : pygame.Rect, w: KDS.Animator.Animation, a: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, sight_sound: pygame.mixer.Sound, death_sound: pygame.mixer.Sound, health, mv, attackPropability, sleep = True, direction = False):
        global initCompleted
        if not initCompleted:
            raise Exception("KDS.Error: AI textures are not initialized")

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
        self.movement = mv
        self.clearlagcounter = 0

    def toString(self):
        """Converts all textures and audios to strings
        """
        self.animation
        if isinstance(self.sight_sound, pygame.mixer.Sound):
            self.sight_sound = self.sight_sound.get_raw()
        if isinstance(self.death_sound, pygame.mixer.Sound):
            self.death_sound = self.death_sound.get_raw()
    
    def fromString(self):
        """Converts all strings back to textures
        """
        self.animation
        if not isinstance(self.sight_sound, pygame.mixer.Sound):
            self.sight_sound = pygame.mixer.Sound(self.sight_sound)
        if not isinstance(self.death_sound, pygame.mixer.Sound):
            self.death_sound = pygame.mixer.Sound(self.death_sound)

    def onDeath(self):
        pass
    def attack(self):
        pass

    def update(self, Surface: pygame.Surface, scroll: list, tiles, targetRect):
        enemyProjectiles = None
        dropItems = []
        if self.health:
            s = searchForPlayer(targetRect=targetRect, searchRect=self.rect, direction=self.direction, Surface=Surface, scroll=scroll, obstacles=tiles)[0]
        else:
            s = False
        if s:
            self.sleep = False
        if self.health > 0 and not self.sleep:
            if s:
                if not self.attackRunning:
                    if not random.randint(0, self.a_propability):
                        self.attackRunning = True
            if self.attackRunning:
                self.animation.trigger("attack")
                Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
                if self.animation.active.done:
                    df, sl2 = searchForPlayer(targetRect=targetRect, searchRect=self.rect, direction=self.direction, Surface=Surface, scroll=scroll, obstacles=tiles)
                    if df:
                        enemyProjectiles = self.attack((sl2*-1)*3, tiles, targetRect)
                    self.attakF = False
                    self.attackRunning = False
                    self.animation.active.tick = 0
            else:
                if self.playSightSound:
                    Audio.playSound(self.sight_sound)
                    self.playSightSound = False
                self.rect, c = move(self.rect, self.movement, tiles)
                if c["right"] or c["left"]:
                    self.movement[0] = -self.movement[0]
                    self.direction = not self.direction
                self.animation.trigger("walk")
                Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        elif self.health > 0:
            self.rect, c = move(self.rect, [0,8], tiles)
            self.animation.trigger("idle")
            Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))          
        elif self.health < 1:
            if self.playDeathSound:
                Audio.playSound(self.death_sound)
                items = self.onDeath()
                for item in items:
                    if item:
                        dropItems.append(item)
                self.playDeathSound = False
            self.rect, c = move(self.rect, [0,8], tiles)
            self.animation.trigger("death")
            Surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
            self.clearlagcounter += 1
            if self.clearlagcounter > 3600:
                self.clearlagcounter = 3600

        return enemyProjectiles, dropItems

    def dmg(self, dmgAmount):
        self.health -= dmgAmount
        if self.health < 0:
            self.health = 0

class Imp(HostileEnemy):
    def __init__(self, pos):
        health = 200
        w_anim = KDS.Animator.Animation("imp_walking", 4, 11, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("imp_walking", 2, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("imp_attacking", 2, 27, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("imp_dying", 5, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 55)
        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=imp_sight_sound, death_sound=imp_death_sound, health=health, mv=[1, 8], attackPropability=40)
    
    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        impAtack.set_volume(dist)
        impAtack.play()
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, 6, env_obstacles, random.randint(20, 50), texture=imp_fireball, maxDistance=2000, slope=KDS.Math.getSlope(self.rect.center, target.center)*KDS.Convert.ToMultiplier(self.direction))]
    def onDeath(self):
        return [0]

class SergeantZombie(HostileEnemy):
    def __init__(self, pos):
        health = 125
        w_anim = KDS.Animator.Animation("seargeant_walking", 4, 11, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("seargeant_walking", 2, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("seargeant_shooting", 2, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("seargeant_dying", 5, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
        rect = pygame.Rect(pos[0], pos[1]-36, 34, 63)

        #region Handling the i_anim:
        aim_im = a_anim.images[0]
        shoot_im = a_anim.images[1]
        a_anim.images.clear()
        #for _ in range(25):
            #a_anim.images.append(aim_im)
        for _ in range(20):
            a_anim.images.append(shoot_im)
        a_anim.ticks = 19
        del aim_im, shoot_im

        #endregion

        super().__init__(rect, w=w_anim, a=a_anim, d=d_anim, i=i_anim, sight_sound=zombie_sight_sound, death_sound=zombie_death_sound, health=health, mv=[1, 8], attackPropability=40)

    def attack(self, slope, env_obstacles, target, *args):
        dist = KDS.Math.getDistance(self.rect.center, target.center)
        dist = min(1200, dist)
        dist = max(0, dist)
        dist = 1200 - dist
        dist /= 1200
        shotgunShot.set_volume(dist)
        shotgunShot.play()
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(10, 20), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction))]


    def onDeath(self):
        items = []
        if random.randint(0, 2) == 0:
            items.append(17)
        return items

class DrugDealer(HostileEnemy):
    def __init__(self, pos):
        health = 100
        w_anim = KDS.Animator.Animation("drug_dealer_walking", 5, 7, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        i_anim = KDS.Animator.Animation("drug_dealer_idle", 2, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Loop)
        a_anim = KDS.Animator.Animation("drug_dealer_shooting", 4, 16, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
        d_anim = KDS.Animator.Animation("drug_dealer_dying", 6, 6, KDS.Colors.GetPrimary.White, KDS.Animator.OnAnimationEnd.Stop)
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
        pistol_shot.play()
        #print(KDS.Math.getSlope(self.rect.center, target.center))
        return [KDS.World.Bullet(pygame.Rect(self.rect.x + 30 * KDS.Convert.ToMultiplier(self.direction), self.rect.centery-20, 10, 10), self.direction, -1, env_obstacles, random.randint(40, 60), slope=KDS.Math.getSlope(self.rect.center, target.center)*18*KDS.Convert.ToMultiplier(self.direction))]

    def onDeath(self):
        items = []
        if random.randint(0, 15) == 10:
            items.append(20)
        if random.randint(0, 4) == 4:
            items.append(11)
        return []

class Projectile:
    pass

class Hitscanner:
    pass