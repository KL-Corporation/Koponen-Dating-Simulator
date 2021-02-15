import pygame
import KDS.Math
import KDS.Logging
import KDS.Animator
import KDS.Audio
import KDS.ConfigManager
import KDS.Colors

import os
from KDS.World import move_entity
from typing import Dict, Tuple, List

last_NPCID = 0
def get_NPCID():
    global last_NPCID
    last_NPCID += 1
    return last_NPCID - 1

class EntityComponent(object):
    pass

class NPC:
    def __init__(self, datapath: str, position: Tuple[int, int]):
        self.call_unique_update = False
        self.entityComponents = List[EntityComponent]
        self.NPCID = get_NPCID()

        property_json = os.path.join("datapath", "data")
        self.speed = KDS.ConfigManager.JSON.Get(property_json, "speed", 1)

        self.movement = [self.speed, 0]

        self.air_time = 0
        self.y_velocity = 0

        self.collisions = Dict[str, bool]
        
        self.resources = {}
        self.animation: KDS.Animator.MultiAnimation
        self.loadResources(datapath)
        self.animation.trigger("idle")
        
        rect_size = KDS.ConfigManager.JSON.Get(property_json, "rect_size", self.animation.get_frame().get_size())
        self.rect = pygame.Rect(position[0], position[1], rect_size[0], rect_size[1])

    def loadResources(self, path: str):
        texture_resources = os.listdir(path)
        texture_resources.sort()
        animations = {}
        npc_idle = []
        npc_walk = []
        npc_death = []
        for texture_resource in texture_resources:
            if "npc-idle" in texture_resource: 
                self.resources["idle_animation"] = True
                npc_idle.append(texture_resource)
            if "npc-walk" in texture_resource: 
                self.resources["walk_animation"] = True
                npc_walk.append(texture_resource)
            if "npc-death" in texture_resource: 
                self.resources["death_animation"] = True
                npc_death.append(texture_resource)

        if len(npc_idle): animations["idle"] = KDS.Animator.Animation("npc-idle", len(npc_idle), 60, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        if len(npc_walk): animations["walk"] = KDS.Animator.Animation("npc-walk", len(npc_walk), 12, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)
        if len(npc_death): animations["death"] = KDS.Animator.Animation("npc-idle", len(npc_death), 9, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Loop)

        self.animation = KDS.Animator.MultiAnimation(**animations)

    def update(self, tiles: list):
        if self.call_unique_update: self.unique_update()
        self.rect, self.collisions = move_entity(self.rect, self.movement, tiles)

    def render(self, Surface: pygame.Surface, scroll: Tuple[int, int], debugMode: bool = False):
        if debugMode: pygame.draw.rect(Surface, KDS.Colors.Magenta, (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h))
        Surface.blit(self.animation.update(), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def unique_update(self): #Koska python on mitä on, toi ei vaan voi olla virtual void unique_update() = 0;
        pass 

class StudentNPC(NPC):
    def __init__(self, datapath: str, position: Tuple[int, int]):
        super().__init__(datapath, position)