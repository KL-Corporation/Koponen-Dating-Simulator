from typing import Final, Optional, Union
import pygame
import pygame.time
import time
import KDS.Math

# _customClock() custom clock broke everything... Should've considered it a bit earlier
# class _customClock:
#     def __init__(self) -> None:
#         self.prev_ns: int = time.perf_counter_ns()
#         self.fps: float = 0.0
#         self.delta_time: float = 0.0
#
#     def tick(self, framerate: int):
#         curr_ns = time.perf_counter_ns()
#         diff = curr_ns - self.prev_ns
#         diff_seconds = diff / 1_000_000_000
#         delay_seconds = max(1.0 / framerate - diff_seconds, 0)
#         time.sleep(delay_seconds)
#         self.delta_time = delay_seconds + diff_seconds
#         self.fps = 1.0 / self.delta_time
#         self.prev_ns = curr_ns
#
#     def tick_busy_loop(self, framerate: int):
#         self.tick(framerate)
#
#     def get_fps(self) -> float:
#         return self.fps
#
#     def get_time(self) -> float:
#         return self.delta_time * 1000 # Multiplying for pygame clock compatibility

_clock: pygame.time.Clock = pygame.time.Clock()

DEFAULT_FRAMERATE: Final[float] = 62.5
# 60 fps rounds to 62.5 due to pygame inaccuracies. We set 62.5 manually in case this behaviour changes in the future.
# DO NOT CHANGE THIS BACK TO 60!! KDS.Math.SmoothDamp depends on this new value.

framerate: float = DEFAULT_FRAMERATE
def Tick(framerate_override: int | None = None):
    _clock.tick_busy_loop(framerate_override if framerate_override is not None else framerate)

def GetFPS(roundingDigits: Optional[int] = None) -> float:
    fps = _clock.get_fps()
    if roundingDigits != None:
        return KDS.Math.RoundCustom(fps, roundingDigits, KDS.Math.MidpointRounding.AwayFromZero)
    return fps

def GetFrameTimeMs() -> int:
    """Includes the time slept to achieve target fps."""
    return _clock.get_time()

def GetRawFrameTimeMs() -> int:
    """Does not include the time slept to achieve target fps."""
    return _clock.get_rawtime()

def GetDeltaTime() -> float: # Would've been useful in variable framerate, but that was not possible to implement.
    """The interval in seconds from the last frame to the current one."""
    return _clock.get_time() / 1000

def Sleep(milliseconds: int):
    pygame.time.delay(milliseconds)
