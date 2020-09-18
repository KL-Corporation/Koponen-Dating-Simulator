import pygame, threading, multiprocessing, numpy, math, random
import concurrent.futures
import KDS.Animator, KDS.Math, KDS.Colors
pygame.mixer.init()

def __collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def __move(rect, movement, tiles):
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

imp_sight_sound.set_volume(0.4)

class SergeantZombie:

    def __init__(self, position, health, speed):
        self.position = position
        self.health = health
        self.rect = pygame.Rect(position[0], position[1], 34, 64)
        self.direction = True
        self.playDeathAnimation = True
        self.movement = [speed, 8]
        self.shooting = False
        self.hits = {}
        self.xvar = False
        self.hitscanner_cooldown = 0
        self.shoot = False
        self.bullet_pos =  [0, 0]
        self.loot_dropped = False

    def hit_scan(self, _rect, _player_health, _tile_rects):
        _player_health, _tile_rects
        if self.rect.topleft[1] < _rect.centery < self.rect.bottomleft[1]:
            if self.direction:
                if self.rect.x < _rect.x:
                    self.bullet_pos = [self.rect.centerx,self.rect.centery-20]

                    q = True
                    counter = 0
                    while q:
                        for tile in _tile_rects:
                            if tile.collidepoint(self.bullet_pos):
                                return False

                        if _rect.collidepoint(self.bullet_pos):
                            return True

                        self.bullet_pos[0] += 27

                        counter += 1

                        if counter > 40:
                            q = False
                    
            else:
                if self.rect.x > _rect.x:
                    self.bullet_pos = [self.rect.centerx,self.rect.centery-20]

                    q = True
                    counter = 0
                    while q:
                        for tile in _tile_rects:
                            if tile.collidepoint(self.bullet_pos):
                                return False
                        if _rect.collidepoint(self.bullet_pos):
                            return True
                        self.bullet_pos[0] -= 27

                        counter += 1

                        if counter > 40:
                            q = False 

        return False

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

class hostileEnemy:
    def __init__(self:int, _health:int, _speed:int, _position:(int,int),__tilerects:list, _animation_name: str):
        self.health = _health
        self.speed = -_speed
        self.position = _position
        self.baseAnimation = KDS.Animator.Animation(_animation_name,4,14,KDS.Colors.GetPrimary.White,-1)
        #self.rect = pygame.Rect(_position[0],_position[1],self.baseAnimation.images[0].width,self.baseAnimation.images[0].height)
        self.rect = pygame.Rect(_position[0], _position[1], self.baseAnimation.images[0].get_size()[0], self.baseAnimation.images[0].get_size()[1]-2)
        self.movement = [self.speed, 8]
        self.collsisions = dict()
        self.obstacleRects = __tilerects
        self.sleep = True
        self.targetFound = False
        self.direction = False
        self.search_results = [True, False, self.movement]
        self.search_counter = random.randint(0, 30)

        self.baseAnimation.tick = random.randint(0, len(self.baseAnimation.images)-1)

    def r(self):
        while True:
            self.rect.y += 1
            for obstacle in self.obstacleRects:
                if self.rect.colliderect(obstacle):
                    return "continue"
                    
            if self.rect.y > len(self.obstacleRects)*35+500:
                return "destroy"

    def dmg(self, dmgAmount):
        self.health -= dmgAmount
        if self.health < 0:
            self.health = 0
        
    def _move(self):
        def _movementUpdateThread(obj:Imp):
            if not obj.sleep:

                def collision_test(rect, tiles):
                    hits1 = []
                    for tile in tiles:
                        if rect.colliderect(tile):
                            hits1.append(tile)
                    return hits1

                obj.rect.x += obj.movement[0]
                
                hit_list = collision_test(obj.rect, obj.obstacleRects)
                obj.collsisions = {"Right": False, "Left": False}
                for tile in hit_list:
                    if obj.movement[0] > 0:
                        obj.rect.right = tile.left
                        obj.collsisions["Right"] = True

                    if obj.movement[0] < 0:
                        obj.rect.left = tile.right
                        obj.collsisions["Left"] = True

                obj.rect.y += obj.movement[1]
                hit_list = collision_test(obj.rect, obj.obstacleRects)
                for tile in hit_list:
                    if obj.movement[1] > 0:
                        obj.rect.bottom = tile.top
                    elif obj.movement[1] < 0:
                        obj.rect.top = tile.bottom
                if obj.collsisions["Right"]:
                    obj.speed = -obj.speed
                    obj.movement[0] = obj.speed
                if obj.collsisions["Left"]:
                    obj.speed = -obj.speed
                    obj.movement[0] = obj.speed


            if obj.speed > 0:
                obj.direction = True
            elif obj.speed < 0:
                obj.direction = False
                
            return obj.rect, obj.movement, obj.direction, obj.speed

        return _movementUpdateThread(self)

class Imp(hostileEnemy):
    def __init__(self, _health:int, _speed:int, _position: (int,int), __tilerects:list, _animation_name: str, _attack_animation: str, _death_animation: str):
        super().__init__(_health, _speed, _position,__tilerects, _animation_name)
        self._death_animation = KDS.Animator.Animation(_death_animation, 5,16,KDS.Colors.GetPrimary.White, 1)
        self._attack_animation = KDS.Animator.Animation(_attack_animation,2,16,KDS.Colors.GetPrimary.White,-1)
        self.corpse_texture = self._death_animation.images[-1]
        self.idle_texture = self.baseAnimation.images[1]
        self.playSightSound = True

    def update(self, searchObject: pygame.Rect, surface: pygame.Surface, searchObject_H: int, scroll: list, debug_mode = False):
        surface.blit(pygame.transform.flip(self.baseAnimation.update(), self.direction, False), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        self.search_counter += 1

        def search_target(obj: Imp, target: pygame.Rect):
            def angle_search(max_angle, direction, target: pygame.Rect):
                angle = int(KDS.Math.getAngle((obj.rect.centerx, obj.rect.centery), (target.centerx, target.centery)))
                
                if (direction and target.x > obj.rect.x) or (not direction and target.x < obj.rect.x) and KDS.Math.getDistance(obj.rect.topleft, target.topleft) < 1600:
                    if 90-KDS.Math.toPositive(angle) < max_angle:
                        return angle
                return None

            angle_result = angle_search(60, obj.direction, target)
            
            if angle_result != None:
                #Tästä eteen päin koodin tarkempi tarkastelu ehdottomasti kielletty
                if angle_result > 0:
                    angle_result = 90-angle_result
                elif angle_result < 0:
                    angle_result = -90 - angle_result
                
                slope = KDS.Math.getSlope(angle_result)

                counter = 0

                if obj.direction:
                    t = 20
                else:
                    t = -20
                #print(int(KDS.Math.getDistance(searchObject.topleft, obj.rect.topleft)))
                #counter = int(KDS.Math.getDistance(searchObject.topleft, obj.rect.topleft)/20)

                while counter < 33:
                    if debug_mode:
                        pygame.draw.rect(surface, (255, 100, 45), (obj.rect.centerx + counter*t - scroll[0], obj.rect.centery + counter*t* slope - scroll[1], 5 ,5) )
                    for obstacle in obj.obstacleRects:
                        if obstacle.collidepoint(obj.rect.centerx + counter*t, obj.rect.centery + counter*t* slope):
                            if obj.sleep:
                                return True, False, obj.movement
                            else:
                                return False, False, obj.movement
                            counter = 100

                    if searchObject.collidepoint(obj.rect.centerx + counter*t, obj.rect.centery + counter*t* slope):
                        if obj.playSightSound:
                            imp_sight_sound.play()
                            obj.playSightSound = False
                        counter = 100
                        return False, True, obj.movement

                    counter += 1


            else:
                if obj.sleep:
                    return True, False, obj.movement
                else:
                    return False, False, obj.movement
        if self.search_counter > 30:
            self.search_results = search_target(self, searchObject)
            self.search_counter = 0
        return self.search_results
        #search_target(self, searchObject)

class Projectile:
    pass

class Hitscanner:
    pass