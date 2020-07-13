import pygame

pygame.mixer.init()

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