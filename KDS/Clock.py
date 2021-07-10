from typing import Optional
import pygame
import KDS.Math

_tick: int = 0
_clock: pygame.time.Clock = pygame.time.Clock()

def Tick(framerate: int = 60):
    global _tick
    if framerate > 0:
        _tick = (_tick + 1) % framerate
    else:
        _tick = -1
    _clock.tick_busy_loop(framerate)

def GetTick() -> int: # Not used, but good to have.
    global _tick
    return _tick

def GetFPS(roundingDigits: Optional[int] = None) -> float:
    fps = _clock.get_fps()
    if roundingDigits != None:
        return KDS.Math.RoundCustom(fps, roundingDigits, KDS.Math.MidpointRounding.AwayFromZero)
    return fps

def GetDeltaTime() -> float: # Would've been useful in variable framerate, but that was not possible to implement.
    """The interval in seconds from the last frame to the current one."""
    return _clock.get_time() / 1000

def Sleep(milliseconds: int):
    pygame.time.delay(milliseconds)