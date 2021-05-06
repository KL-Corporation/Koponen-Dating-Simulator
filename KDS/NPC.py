from __future__ import annotations

import pygame
import KDS.Math
import KDS.Logging
import KDS.Animator
import KDS.Audio
import KDS.ConfigManager
import KDS.Colors
import KDS.World
import KDS.Build
import KDS.Jobs
import KDS.Convert
import KDS.Debug

import os
import random
from typing import Dict, Optional, Sequence, TYPE_CHECKING, Tuple, List
from enum import IntEnum, auto

if TYPE_CHECKING:
    from KoponenDatingSimulator import PlayerClass
else:
    PlayerClass = None

NPC_FALL_SPEED = 8

class Type(IntEnum):
    Idle = auto()
    DefaultWalking = auto()
    FranticWalking = auto()


class NPC:
    InstanceList: List[NPC] = []

    def __init__(self, pos: Tuple[int, int]) -> None:
        pass

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        if value < self._health:
            self.onDamage()
        self._health = max(value, 0)

    def internalInit(self, rect: pygame.Rect, _type: Type, w: KDS.Animator.Animation, r: KDS.Animator.Animation, d: KDS.Animator.Animation, i: KDS.Animator.Animation, health: int, walk_speed: int, run_speed: int, direction: bool = False, randomWalkTurnChance: int = 25):
        NPC.InstanceList.append(self)

        self.type = _type

        self.rect = rect
        self._health = health

        self.idleTimer: Optional[int] = None

        self.direction = direction
        self.randomTurnChance = randomWalkTurnChance

        self.animation = KDS.Animator.MultiAnimation(walk = w, run = r, death = d, idle = i)

        self.walk_speed = walk_speed
        self.run_speed = run_speed
        self.collisions = KDS.World.Collisions()

        self.panicked: bool = False
        self.noPanick: bool = False

        self.enabled = True

        self.mover = KDS.World.EntityMover()

    def lateInit(self):
        pass

    def render(self, surface: pygame.Surface, scroll: Sequence[int]):
        if KDS.Debug.Enabled:
            pygame.draw.rect(surface, KDS.Colors.Magenta if self.panicked else KDS.Colors.Green, (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.width, self.rect.height))
        surface.blit(pygame.transform.flip(self.animation.update(), self.direction, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, surface: pygame.Surface, scroll: Sequence[int], tiles: List[List[List[KDS.Build.Tile]]], player: PlayerClass) -> Tuple[List[KDS.World.Bullet], List[int]]:
        def panickBehaviour():
            self.animation.trigger("run")
            if self.direction:
                if self.rect.centerx > player.rect.centerx:
                    self.direction = not self.direction
            elif self.rect.centerx < player.rect.centerx:
                self.direction = not self.direction

        def idleBehaviour():
            self.animation.trigger("idle")

        def neutralBehaviour():
            self.animation.trigger("walk")
            self.collisions = self.mover.move(self.rect, (self.walk_speed * KDS.Convert.ToMultiplier(self.direction), NPC_FALL_SPEED), tiles)
            if self.collisions.right or self.collisions.left:
                self.direction = not self.direction
                self.idleTimer = random.randint(1 * 60, 5 * 60)

        def franticBehaviour():
            self.animation.trigger("walk")
            if random.randint(0, 100) < self.randomTurnChance:
                self.direction = not self.direction

            self.collisions = self.mover.move(self.rect, (self.walk_speed * KDS.Convert.ToMultiplier(self.direction), NPC_FALL_SPEED), tiles)
            if self.collisions.right or self.collisions.left:
                self.direction = not self.direction

        if self.health <= 0:
            self.animation.trigger("death")
            self.render(surface, scroll)
            return [], []

        if self.panicked:
            panickBehaviour()
        else:
            if self.type == Type.Idle:
                idleBehaviour()
            elif self.idleTimer != None:
                self.idleTimer -= 1
                if self.idleTimer < 0:
                    self.idleTimer = None
                idleBehaviour()
            elif self.type == Type.DefaultWalking:
                neutralBehaviour()
            elif self.type == Type.FranticWalking:
                franticBehaviour()
            else:
                KDS.Logging.AutoError(f"Unexpected NPC type. Got: {self.type.name}")
        self.render(surface, scroll)
        return [], []


    def onDamage(self):
        if not self.noPanick:
            self.panicked = True
        KDS.Jobs.Schedule(NPC.panickNearby, self.rect) # Threaded to not cause a massive lag spike even though I'm not sure if it's gonna even happen, but still... We will have a lot of NPC's

    @staticmethod
    def panickNearby(rect: pygame.Rect):
        for npc in NPC.InstanceList:
            if abs(rect.centerx - npc.rect.centerx) < 16 * 34 and abs(rect.centery - npc.rect.centery) < 34:
                npc.panicked = True

class StudentNPC(NPC):
    def __init__(self, pos: Tuple[int, int]) -> None:
        randomPerson_dir = random.choice(os.listdir("Assets/Textures/NPC/Static"))
        idle_anim_dir = os.path.join("NPC/Static", randomPerson_dir)
        idle_anim = KDS.Animator.Animation("npc-idle", len(os.listdir(f"Assets/Textures/{idle_anim_dir}")), 30, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop, animation_dir=idle_anim_dir)
        idle_anim_size = idle_anim.get_size()
        rect = pygame.Rect(pos[0], pos[1] + (34 - idle_anim_size[1]), idle_anim_size[0], idle_anim_size[1])
        self.internalInit(rect, Type.Idle, idle_anim, idle_anim, idle_anim, idle_anim, 100, 0, 0)
        self.noPanick = True


# region OLD NPC CODE
#
# last_NPCID = 0
# def get_NPCID():
#     global last_NPCID
#     last_NPCID += 1
#     return last_NPCID - 1
#
# class EntityComponent(object):
#     pass
#
# class NPC:
#     def __init__(self, datapath: str, position: Tuple[int, int]):
#         self.call_unique_update = False
#         self.entityComponents = List[EntityComponent]
#         self.NPCID = get_NPCID()
#
#         property_json = os.path.join("datapath", "data")
#         self.speed = KDS.ConfigManager.JSON.Get(property_json, "speed", 1)
#
#         self.movement = [self.speed, 0]
#
#         self.air_time = 0
#         self.y_velocity = 0
#
#         self.collisions = KDS.World.Collisions()
#
#         self.resources = {}
#         self.animation: KDS.Animator.MultiAnimation
#         self.loadResources(datapath)
#         self.animation.trigger("idle")
#
#         rect_size = KDS.ConfigManager.JSON.Get(property_json, "rect_size", self.animation.get_frame().get_size())
#         self.rect = pygame.Rect(position[0], position[1], rect_size[0], rect_size[1])
#
#         self.mover = KDS.World.EntityMover()
#
#     def loadResources(self, path: str):
#         texture_resources = os.listdir(path)
#         texture_resources.sort()
#         animations: Dict[str, KDS.Animator.Animation] = {}
#         npc_idle: List[str] = []
#         npc_walk: List[str] = []
#         npc_death: List[str] = []
#         for texture_resource in texture_resources:
#             if "npc-idle" in texture_resource:
#                 self.resources["idle_animation"] = True
#                 npc_idle.append(texture_resource)
#             if "npc-walk" in texture_resource:
#                 self.resources["walk_animation"] = True
#                 npc_walk.append(texture_resource)
#             if "npc-death" in texture_resource:
#                 self.resources["death_animation"] = True
#                 npc_death.append(texture_resource)
#
#         if len(npc_idle) > 0: animations["idle"] = KDS.Animator.Animation("npc-idle", len(npc_idle), 60, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
#         if len(npc_walk) > 0: animations["walk"] = KDS.Animator.Animation("npc-walk", len(npc_walk), 12, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
#         if len(npc_death) > 0: animations["death"] = KDS.Animator.Animation("npc-idle", len(npc_death), 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
#
#         self.animation = KDS.Animator.MultiAnimation(**animations)
#
#     def update(self, tiles: list):
#         if self.call_unique_update: self.unique_update()
#
#         if self.collisions.bottom: # Pylance complains about this, because pylance is completely useless piece of shit
#                                    # No. Pylance complains, because you are a completely useless piece of shit (jk)
#             self.air_time = 0
#             self.y_velocity = 0
#         else: self.air_time += 1
#
#         self.y_velocity += 0.5
#         self.y_velocity = min(8.0, self.y_velocity)
#         self.movement[1] = self.y_velocity
#
#         self.collisions = self.mover.move(self.rect, self.movement, tiles)
#
#     def render(self, Surface: pygame.Surface, scroll: Tuple[int, int], debugMode: bool = False):
#         if debugMode: pygame.draw.rect(Surface, KDS.Colors.Magenta, (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h))
#         Surface.blit(self.animation.update(), (self.rect.x - scroll[0], self.rect.y - scroll[1]))
#
#     def unique_update(self): #Koska python on mitä on, toi ei vaan voi olla virtual void unique_update() = 0;
#         pass
#
# class StudentNPC(NPC):
#     def __init__(self, datapath: str, position: Tuple[int, int]):
#         super().__init__(datapath, position)
#
#endregion