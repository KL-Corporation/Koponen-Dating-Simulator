import pygame, threading

pygame.mixer.init()

def __move(rect, movement, tiles):
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
        self.bullet_pos =  [0,0]

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