from __future__ import annotations
import random
from typing import Dict, List, Optional, Sequence, TYPE_CHECKING, Tuple, Type
import pygame

import KDS.Animator
import KDS.AI
import KDS.World
import KDS.Missions
import KDS.Build
import KDS.Inventory
import KDS.Math
import KDS.Audio
import KDS.Convert
import KDS.Linq
import KDS.Logging
import KDS.Colors
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
    serialNumbers: Dict[int, Type[Teacher]] = {}

    def __init__(self, pos: Tuple[int, int]) -> None:
        pass

    def lateInit(self) -> None:
        self.lastTargetDirection = self.direction

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        if value < self._health:
            self.onDamage()
        self._health = max(value, 0)

    def internalInit(self, rect: pygame.Rect, w: KDS.Animator.Animation, r: KDS.Animator.Animation, s: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, agro_sound: Optional[pygame.mixer.Sound], death_sound: Optional[pygame.mixer.Sound], health: int, weapon_serial: int, walk_speed: int, run_speed: int, idle: bool = False, direction: bool = False) -> None:
        self.rect = rect
        self._health = health

        self.idle = idle
        self.idleTime: Optional[int] = None
        self.direction = direction

        weapon = KDS.Build.Item.serialNumbers[weapon_serial]((0, 0), weapon_serial)
        if not isinstance(weapon, KDS.Build.Weapon):
            KDS.Logging.AutoError(f"Unexpected weapon type! Expected: {KDS.Build.Weapon.__name__}, Got: {type(weapon).__name__}")
            weapon = KDS.Inventory.EMPTYSLOT
        self.inventory = KDS.Inventory.Inventory(5, (KDS.Inventory.EMPTYSLOT, weapon))

        self.animation = KDS.Animator.MultiAnimation(walk = w, run = r, search = s, death = d, idle = i)

        self.agro_sound = agro_sound
        self.death_sound = death_sound

        self.state: TeacherState = TeacherState.Neutral
        self.seenContrabandSerials: List[int] = []

        self.playSightSound = True
        self.walk_speed = walk_speed
        self.run_speed = run_speed
        self.search_speed = KDS.Math.RoundCustomInt(KDS.Math.Lerp(self.walk_speed, self.run_speed, 0.5), KDS.Math.MidpointRounding.AwayFromZero)
        self.allowJump: bool = True
        self.collisions = KDS.World.Collisions()

        self.searchTime = 10 * 60
        self.currentSearch = 0
        self.lineOfSight = False

        self.alertTimeBeforeCombat = 3 * 60
        self.alertTime = 0

        self.enabled = True

        self.mover = KDS.World.EntityMover()

        self.deathHandled = False

        self.ticksSinceSwitch = 0

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
            if self.agro_sound != None:
                KDS.Audio.PlaySound(self.agro_sound)
        if TeacherState.Alerted not in self.state:
            self.state |= TeacherState.Alerted
            KDS.Missions.Listeners.TeacherAgro.Trigger()

    def render(self, surface: pygame.Surface, scroll: Sequence[int], debug: bool):
        indicatorColor: Optional[Tuple[int, int, int]] = None
        if TeacherState.Combat in self.state:
            indicatorColor = KDS.Colors.Red
        elif TeacherState.Alerted in self.state:
            indicatorColor = KDS.Math.LerpColor(KDS.Colors.White, KDS.Colors.Orange, self.alertTime / self.alertTimeBeforeCombat)
        elif TeacherState.RemovingContraband in self.state:
            indicatorColor = KDS.Colors.Cyan

        if indicatorColor != None:
            pygame.draw.circle(surface, indicatorColor, (self.rect.centerx, self.rect.y - 9), 2)

        self.inventory.useItem(self.rect, self.direction, surface, scroll)
        surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, tiles: List[List[List[KDS.Build.Tile]]], player: PlayerClass) -> Tuple[List[KDS.World.Bullet], List[int]]:
        def neutralBehaviour():
            self.animation.trigger("walk")
            self.inventory.pickSlot(0)
            self.collisions = self.mover.move(self.rect, (self.walk_speed * KDS.Convert.ToMultiplier(self.direction), TEACHER_FALL_SPEED), tiles)
            if self.collisions.right or self.collisions.left:
                self.direction = not self.direction
                self.idle = True
                self.idleTime = random.randint(1 * 60, 5 * 60)

        def idleBehaviour():
            self.animation.trigger("idle")
            self.inventory.pickSlot(0)
            if self.idleTime != None:
                self.idleTime -= 1
                if self.idleTime < 0:
                    self.idleTime = None
                    self.idle = False

        def contrabandBehaviour():
            self.animation.trigger("run")
            self.inventory.pickSlot(0)
            self.collisions = self.mover.move(self.rect, (self.run_speed * KDS.Convert.ToMultiplier(self.direction), TEACHER_FALL_SPEED), tiles)
            distance = self.rect.centerx - player.rect.centerx
            self.direction = True if distance >= 0 else False
            if self.rect.colliderect(player.rect):
                firstEmptySlot = None
                for i in range(len(self.inventory)):
                    if self.inventory[i] == None:
                        firstEmptySlot = i
                        break
                if firstEmptySlot == None:
                    return
                droppedItem = player.inventory.dropItemAtIndex(player.inventory.SIndex)
                if droppedItem == None:
                    return
                self.inventory.pickupItemToIndex(firstEmptySlot, droppedItem)

        def searchingBehaviour():
            self.animation.trigger("run")
            self.inventory.pickSlot(1)
            self.currentSearch += 1
            if self.currentSearch > self.searchTime and TeacherState.Searching in self.state:
                self.state &= ~TeacherState.Searching

            distance = self.rect.centerx - player.rect.centerx
            if abs(distance) > 680: # If over 20 blocks away and player behind, turn
                self.direction = False if distance >= 0 else True

            self.collisions = self.mover.move(self.rect, (self.search_speed * KDS.Convert.ToMultiplier(self.direction), TEACHER_FALL_SPEED), tiles)
            if self.collisions.right or self.collisions.left:
                self.direction = not self.direction
                self.idle = True
                self.idleTime = random.randint(1 * 60, 3 * 60) // 2

        def combatBehaviour():
            self.animation.trigger("search")
            self.inventory.pickSlot(1)

            distance = self.rect.centerx - player.rect.centerx
            targetDirection = True if distance >= 0 else False
            if targetDirection != self.direction and (abs(distance) > 170 or self.ticksSinceSwitch > 120) and self.health > 0: # If over five blocks away from target or hasn't turned for two seconds while player is behind; turn around
                self.direction = not self.direction
                self.ticksSinceSwitch = 0
            self.ticksSinceSwitch += 1

            self.collisions = self.mover.move(self.rect, (self.run_speed * KDS.Convert.ToMultiplier(self.direction), TEACHER_FALL_SPEED), tiles)
            if self.collisions.right or self.collisions.left:
                self.direction = not self.direction

            hItem = self.inventory.getHandItem()
            if not isinstance(hItem, KDS.Build.Weapon):
                KDS.Logging.AutoError(f"Unexpected hand item of type: {type(hItem).__name__}, expected: {KDS.Build.Weapon.__name__}")
                return
            hItem.shoot()

        def inventoryFullBehaviour():
            raise NotImplementedError("Inventory full behaviour has not been implemented yet!")

        enemyProjectiles: List[KDS.World.Bullet] = []
        dropItems: List[int] = []

        #region Dead
        if self.health <= 0:
            self.animation.trigger("death")
            if not self.deathHandled and self.death_sound != None:
                KDS.Audio.PlaySound(self.death_sound)
                items = self.onDeath()
                KDS.Missions.Listeners.EnemyDeath.Trigger()
                for item in items:
                    if item:
                        dropItems.append(item)
                self.deathHandled = True
            return enemyProjectiles, dropItems
        #endregion
        self.lineOfSight, _ = KDS.AI.searchRect(player.rect, self.rect, self.direction, None, None, tiles, maxSearchUnits=8)
        #region Behaviour Triggers
        if all([x != None and i != 0 for i, x in enumerate(self.inventory)]) and TeacherState.ClearingInventory not in self.state:
            self.state |= TeacherState.ClearingInventory
        if self.lineOfSight:
            self.alertTime += 1
            playerHandItem = player.inventory.getHandItem()
            if not isinstance(playerHandItem, str) and playerHandItem.serialNumber in KDS.Build.Item.contraband:
                if TeacherState.RemovingContraband not in self.state:
                    self.state |= TeacherState.RemovingContraband
            elif TeacherState.RemovingContraband in self.state:
                self.state &= ~TeacherState.RemovingContraband

            alertCombat = TeacherState.Alerted in self.state and (self.alertTime > self.alertTimeBeforeCombat or TeacherState.RemovingContraband in self.state)
            if (alertCombat or TeacherState.Searching in self.state) and TeacherState.Combat not in self.state:
                self.state |= TeacherState.Combat
                if self.agro_sound != None:
                    KDS.Audio.PlaySound(self.agro_sound)
        else:
            self.alertTime = 0

            if TeacherState.RemovingContraband in self.state:
                self.state &= ~TeacherState.RemovingContraband

            if TeacherState.Combat in self.state:
                self.state &= ~TeacherState.Combat
                if TeacherState.Searching not in self.state:
                    self.state |= TeacherState.Searching
        #endregion
        #region States
        if TeacherState.Combat in self.state:
            combatBehaviour()
        elif TeacherState.Searching in self.state:
            searchingBehaviour()
        elif TeacherState.ClearingInventory in self.state:
            inventoryFullBehaviour()
        elif TeacherState.RemovingContraband in self.state:
            contrabandBehaviour()
        elif self.idle:
            idleBehaviour()
        else:
            neutralBehaviour()
        #endregion
        return enemyProjectiles, dropItems

class Test(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit(pygame.Rect(pos[0], pos[1] - 29, 23, 63),
                          KDS.Animator.Animation("koponen_walk", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Teachers/Test"),
                          KDS.Animator.Animation("koponen_walk", 2, 3, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Teachers/Test"),
                          KDS.Animator.Animation("koponen_walk", 2, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Teachers/Test"),
                          KDS.Animator.Animation("koponen_idle", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Teachers/Test"),
                          KDS.Animator.Animation("koponen_idle", 2, 7, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir="Teachers/Test"),
                          None, None, 1000, 10, 1, 3
        )

class LaaTo(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()

class KuuMa(Teacher):
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.internalInit()