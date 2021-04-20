from __future__ import annotations
from typing import List, Sequence, TYPE_CHECKING, Tuple
import pygame

import KDS.Animator
import KDS.AI
import KDS.World
import KDS.Missions
import KDS.Build
import KDS.Inventory
import KDS.Math
import KDS.Audio
from enum import IntFlag

TEACHER_FALL_SPEED = 8

if TYPE_CHECKING:
    from KoponenDatingSimulator import PlayerClass
else:
    PlayerClass = None

class TeacherState(IntFlag):
    Neutral = 0 # Walks normally
    RemovingContraband = 1 # Follows player and removes seen contraband from inventory
    Alerted = 2 # Starts combat if sees player
    Searching = 4 # Actively searches for the player
    Combat = 8 # In combat with player
    ClearingInventory = 16 # Goes to a specific place to clear inventory from confiscated contraband (NOT IMPLEMENTED)

class Teacher:
    def __init__(self, pos: Tuple[int, int]) -> None:
        pass

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        if value < self._health:
            self.onDamage()
        self._health = value

    def internalInit(self, rect: pygame.Rect, w: KDS.Animator.Animation, a: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, agro_sound: pygame.mixer.Sound, death_sound: pygame.mixer.Sound, health: int, weapon: KDS.Build.Weapon, walk_speed: int, run_speed: int, attackPropability: int, sleep: bool = True, direction: bool = False) -> None:
        self.rect = rect
        self._health = health

        self.sleep = sleep
        self.direction = direction

        self.inventory = KDS.Inventory.Inventory(5, (KDS.Inventory.EMPTYSLOT, weapon))

        self.animation = KDS.Animator.MultiAnimation(walk = w, attack = a, death = d, idle = i)

        self.a_propability = attackPropability
        self.agro_sound = agro_sound
        self.death_sound = death_sound

        self.state: TeacherState = TeacherState.Neutral
        self.seenContrabandSerials: List[int] = []

        self.playSightSound = True
        self.walk_speed = walk_speed
        self.run_speed = run_speed
        self.allowJump: bool = True
        self.collisions = KDS.World.Collisions()

        self.enabled = True

        self.mover = KDS.World.EntityMover()

        self.deathHandled = False

    def pickup(self, itemInstance: KDS.Build.Item) -> bool:
        """bool tells if item was picked up succesfully"""
        for i in range(2, len(self.inventory)):
            if self.inventory[i] == None:
                return self.inventory.pickupItem(itemInstance)
        return False

    def onDeath(self) -> List[int]:
        return [x.serialNumber for x in self.inventory if x != None]

    def onDamage(self):
        # Sub-optimal, but works
        if TeacherState.Combat not in self.state:
            self.state |= TeacherState.Combat
        if TeacherState.Alerted not in self.state:
            self.state |= TeacherState.Alerted

    def render(self, surface: pygame.Surface, scroll: Sequence[int], debug: bool):
        surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def neutralBehaviour(self, lineOfSight: bool) -> int:
        pass

    def contrabandBehaviour(self, lineOfSight: bool) -> int:
        pass

    def alertedBehaviour(self, lineOfSight: bool) -> int:
        pass

    def searchingBehaviour(self, lineOfSight: bool) -> int:
        pass

    def combatBehaviour(self, lineOfSight: bool) -> int:
        pass

    def inventoryFullBehaviour(self, lineOfSight: bool) -> int:
        return KDS.Math.MINVALUE

    def update(self, tiles: List[List[List[KDS.Build.Tile]]], player: PlayerClass) -> Tuple[List[KDS.World.Bullet], List[int]]:
        enemyProjectiles: List[KDS.World.Bullet] = []
        dropItems: List[int] = []

        #region Dead
        if self.health <= 0:
            self.animation.trigger("death")
            if not self.deathHandled:
                KDS.Audio.PlaySound(self.death_sound)
                items = self.onDeath()
                KDS.Missions.Listeners.EnemyDeath.Trigger()
                for item in items:
                    if item:
                        dropItems.append(item)
                self.deathHandled = True
            return enemyProjectiles, dropItems
        #endregion
        hasLineOfSight, _ = KDS.AI.searchRect(player.rect, self.rect, self.direction, None, None, tiles, maxSearchUnits=8)
        #region Behaviour Triggers
        if all([x != None for x in self.inventory]) and TeacherState.ClearingInventory not in self.state:
            self.state |= TeacherState.ClearingInventory
        if hasLineOfSight:
            playerHandItem = player.inventory.getHandItem()
            if not isinstance(playerHandItem, str) and playerHandItem.serialNumber in KDS.Build.Item.contraband and TeacherState.RemovingContraband not in self.state:
                self.state |= TeacherState.RemovingContraband
            if TeacherState.Alerted in self.state and TeacherState.Combat not in self.state:
                self.state |= TeacherState.Combat
        else:
            if TeacherState.Combat in self.state:
                self.state &= TeacherState.Combat
                if TeacherState.Searching not in self.state:
                    self.state |= TeacherState.Searching
        #endregion
        #region States
        xMovement = 0
        if TeacherState.Combat in self.state:
            xMovement = self.combatBehaviour(hasLineOfSight)
        elif TeacherState.Searching in self.state:
            xMovement = self.searchingBehaviour(hasLineOfSight)
        elif TeacherState.Alerted in self.state:
            xMovement = self.alertedBehaviour(hasLineOfSight)
        elif TeacherState.RemovingContraband in self.state:
            xMovement = self.contrabandBehaviour(hasLineOfSight)
        else:
            xMovement = self.neutralBehaviour(hasLineOfSight)
        #endregion
        #region Movement
        self.mover.move(self.rect, (xMovement, TEACHER_FALL_SPEED), tiles)
        #endregion
        return enemyProjectiles, dropItems

class LaaTo(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()

class KuuMa(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()