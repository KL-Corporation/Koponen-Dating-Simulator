from typing import List, Optional, Sequence, TYPE_CHECKING, Tuple
import pygame

import KDS.Animator
import KDS.AI
import KDS.World
import KDS.Missions
import KDS.Build
import KDS.Inventory

TEACHER_FALL_SPEED = 8

if TYPE_CHECKING:
    from KoponenDatingSimulator import PlayerClass
else:
    PlayerClass = None

class Teacher:
    def __init__(self, pos: Tuple[int, int]) -> None:
        pass

    def internalInit(self, rect: pygame.Rect, w: KDS.Animator.Animation, a: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, agro_sound: pygame.mixer.Sound, death_sound: pygame.mixer.Sound, health: int, weapon: KDS.Build.Weapon, walk_speed: int, run_speed: int, attackPropability: int, sleep: bool = True, direction: bool = False) -> None:
        self.rect = rect
        self.health = health
        self.sleep = sleep
        self.direction = direction

        self.inventory = KDS.Inventory.Inventory(5, (KDS.Inventory.EMPTYSLOT, weapon))

        self.animation = KDS.Animator.MultiAnimation(walk = w, attack = a, death = d, idle = i)

        self.a_propability = attackPropability
        self.agro_sound = agro_sound
        self.death_sound = death_sound

        self.agroed = False

        self.playDeathSound = True
        self.playSightSound = True
        self.walk_speed = walk_speed
        self.run_speed = run_speed
        self.allowJump: bool = True
        self.collisions = KDS.World.Collisions()

        self.enabled = True

        self.mover = KDS.World.EntityMover()

    def pickup(self, itemInstance: KDS.Build.Item) -> bool:
        """bool tells if item was picked up succesfully"""
        for i in range(2, len(self.inventory)):
            if self.inventory[i] == None:
                return self.inventory.pickupItem(itemInstance)
        return False

    def update(self, surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], player: PlayerClass, debug: bool = False) -> Tuple[List[KDS.World.Bullet], List[int]]:
        pass

class LaaTo(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()

class KuuMa(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()