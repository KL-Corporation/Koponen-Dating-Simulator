import cProfile
import inspect
import logging
import os
import pstats
import KDS.System
import pygame
import sys
from datetime import datetime
from typing import Any, Union

running = False
profiler_running = False
profile = cProfile.Profile()

def init(_AppDataPath: str, _LogPath: str, debugInfo: bool = True):
    global running, AppDataPath, LogPath, logFileName
    running = True
    AppDataPath = _AppDataPath
    LogPath = _LogPath

    while len(logFiles := os.listdir(LogPath)) > 4:
        os.remove(os.path.join(LogPath, logFiles[0]))

    fileTimeFormat = "%Y-%m-%d-%H-%M-%S"
    logTimeFormat = "%H:%M:%S"
    logFormat = "%(levelname)s-%(asctime)s: %(message)s"
    logFileName = os.path.join(LogPath, f"log_{datetime.now().strftime(fileTimeFormat)}.log")
    logging.basicConfig(filename=logFileName, format=logFormat, level=logging.NOTSET, datefmt=logTimeFormat)
    debug(f"Created log file: {logFileName}")

    if not debugInfo:
        return

    display_info = pygame.display.Info()
    debug(f"""
I=====[ DEBUG INFO ]=====I
    [Version Info]
    - pygame: {pygame.version.ver}
    - SDL: {pygame.version.SDL.major}.{pygame.version.SDL.minor}.{pygame.version.SDL.patch}
    - Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
    - Windows {sys.getwindowsversion().major}{f".{sys.getwindowsversion().minor}" if sys.getwindowsversion().minor != 0 else ""}: {sys.getwindowsversion().build}

    [Video Info]
    - SDL Video Driver: {pygame.display.get_driver()}
    - Hardware Acceleration: {bool(display_info.hw)}
    - Window Allowed: {bool(display_info.wm)}
    - Video Memory: {display_info.video_mem if display_info.video_mem != 0 else "N/A"}

    [Pixel Info]
    - Bit Size: {display_info.bitsize}
    - Byte Size: {display_info.bytesize}
    - Masks: {display_info.masks}
    - Shifts: {display_info.shifts}
    - Losses: {display_info.losses}

    [Hardware Acceleration]
    - Hardware Blitting: {bool(display_info.blit_hw)}
    - Hardware Colorkey Blitting: {bool(display_info.blit_hw_CC)}
    - Hardware Pixel Alpha Blitting: {bool(display_info.blit_hw_A)}
    - Software Blitting: {bool(display_info.blit_sw)}
    - Software Colorkey Blitting: {bool(display_info.blit_sw_CC)}
    - Software Pixel Alpha Blitting: {bool(display_info.blit_sw_A)}
I=====[ DEBUG INFO ]=====I""")

def __log(message: Union[str, Exception], consoleVisible: bool, stack_info: bool, logLevel: int, color: str, **kwargs: Any) -> None:
    if not running:
        print(f"Log not succesful! Logger has been shut down already. Original message: {message}")
        return

    message = str(message)
    _frameinfo = inspect.getouterframes(inspect.currentframe(), 2)[2]
    logging.log(logLevel, message, stack_info=stack_info, stacklevel=4, **kwargs)
    if stack_info:
        message = f"File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function}\n    {message}\n    Read log file for more details."
    if consoleVisible:
        print(KDS.System.Console.Colored(message, color))

def debug(message: Union[str, Exception], consoleVisible: bool = False, stack_info: bool = False) -> None:
    __log(message, consoleVisible, stack_info, logging.DEBUG, "green")

def info(message: Union[str, Exception], consoleVisible: bool = False, stack_info: bool = False) -> None:
    __log(message, consoleVisible, stack_info, logging.INFO, "blue")

def warning(message: Union[str, Exception], consoleVisible: bool = False, stack_info: bool = False) -> None:
    __log(message, consoleVisible, stack_info, logging.WARNING, "yellow")

def error(message: Union[str, Exception], consoleVisible: bool = False, stack_info: bool = False) -> None:
    __log(message, consoleVisible, stack_info, logging.ERROR, "red")

def AutoError(message: Union[str, Exception], **kwargs: Any) -> None:
    """Generates an automatic error message.

    Args:
        Message (str): The error message.
    """
    __log(message, True, True, 40, "red", **kwargs)

def Profiler(enabled: bool = True):
    """Turns the profiler on or off.

    Args:
        enabled (bool, optional): Defines if the profiler will be enabled or disabled. Defaults to True.
    """
    global profiler_running, profile, logFileName
    if enabled and not profiler_running:
        profiler_running = True
        profile = cProfile.Profile()
        profile.enable()
    elif not enabled and profiler_running:
        profiler_running = False
        profile.disable()
        try:
            with open(logFileName, "a+") as f:
                f.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I\n\n")
                ps = pstats.Stats(profile, stream=f)
                ps.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
                ps.print_stats()
                f.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I\n")
        except IOError as e: AutoError(f"IO Error! Details: {e}")

def quit():
    global running
    running = False
    logging.shutdown()
    Profiler(False)
