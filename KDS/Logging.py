import cProfile
import inspect
import logging
import os
import pstats
import platform
import KDS.Application
import KDS.Math
import KDS.System
import KDS.Linq
import pygame
import sys
import faulthandler
import re
import psutil
from datetime import datetime
from typing import Any, List, Optional, Self
import time

running = False
profiler_running = False
profile = cProfile.Profile()

faultHandlerEnabled: bool = False
stderrPath: Optional[str] = None

def init(_AppDataPath: str, _LogPath: str, debugInfo: bool = True, _faultHandler: bool = True):
    global running, AppDataPath, LogPath, stderrPath, faultHandlerEnabled, logFileName
    running = True
    AppDataPath = _AppDataPath
    LogPath = _LogPath

    logFiles: List[str] = list(KDS.Linq.Where(os.listdir(LogPath), lambda f: os.path.splitext(f)[1] == ".log"))
    logFiles.sort(key=lambda f: int("".join(re.findall(r'\d+', f))))
    while len(logFiles) > 4:
        wholeLogPath = os.path.join(LogPath, logFiles.pop(0))
        try:
            os.remove(wholeLogPath)
        except Exception:
            print(f"Could not remove errorlog file: {wholeLogPath}")

    errorlogFiles: List[str] = list(KDS.Linq.Where(os.listdir(LogPath), lambda f: os.path.splitext(f)[1] == ".errorlog"))
    errorlogFiles.sort(key=lambda f: int("".join(re.findall(r'\d+', f))))
    for errorlog in errorlogFiles:
        wholeErrorlogPath = os.path.join(LogPath, errorlog)
        rmErrorlog: bool = False
        with open(wholeErrorlogPath, "r") as f:
            if len(f.read()) < 1:
                rmErrorlog = True
        if rmErrorlog:
            try:
                os.remove(wholeErrorlogPath)
            except Exception:
                print(f"Could not remove errorlog file: {wholeErrorlogPath}")

    logtime: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logFileName = os.path.join(LogPath, f"log_{logtime}.log")
    logging.basicConfig(filename=logFileName, format="%(levelname)s-%(asctime)s: %(message)s", level=logging.NOTSET, datefmt="%H:%M:%S")
    debug(f"Created log file: {logFileName}")

    faultHandlerEnabled = _faultHandler
    if faultHandlerEnabled:
        stderrPath = os.path.join(LogPath, f"""errorlog_{logtime}.errorlog""")
        sys.stderr = open(stderrPath, "w")
        debug(f"Created errorlog file: {stderrPath}")
        faulthandler.enable(sys.stderr, all_threads=True)
        debug(f"Enabled faulthandler.")

    if not debugInfo:
        return

    def _format_version(ver: tuple[int, int, int] | None):
        if ver is None:
            return "null"
        else:
            return f"{ver[0]}.{ver[1]}.{ver[2]}"

    def _format_bool(b: bool) -> str:
        return "Yes" if b else "No"

    def _format_accel(accel: bool, hw: bool):
        out: str = _format_bool(accel)
        if accel:
            out += f" ({'hardware' if hw else 'software'})"
        return out

    display_info = pygame.display.Info()
    cpu_inst_info = pygame.system.get_cpu_instruction_sets()

    platform_info = platform.uname()
    architecture_info = platform.architecture()

    memory_info = psutil.virtual_memory()

    hw_accel: bool = bool(display_info.hw)
    blit_accel: bool = bool(display_info.blit_hw if hw_accel else display_info.blit_sw)
    blit_CC_accel: bool = bool(display_info.blit_hw_CC if hw_accel else display_info.blit_sw_CC)
    blit_A_accel: bool = bool(display_info.blit_hw_A if hw_accel else display_info.blit_sw_A)

    debug(f"""
I=====[ DEBUG INFO ]=====I
    [Version Info]
    - Application: {KDS.Application.VERSION}
    - pygame-ce: {_format_version(pygame.version.vernum)}
    - SDL: {_format_version(pygame.get_sdl_version())}
        - Mixer: {_format_version(pygame.mixer.get_sdl_mixer_version())}
        - TTF: {_format_version(pygame.font.get_sdl_ttf_version())}
        - Image: {_format_version(pygame.image.get_sdl_image_version())}
    - Python: {platform.python_implementation()} {_format_version(sys.version_info[0:3])}
    - {platform_info.system} {platform_info.release}: {platform_info.version}

    [Driver Info]
    - SDL Video Driver: {pygame.display.get_driver()}
    - SDL Mixer Driver: {pygame.mixer.get_driver()}

    [Video Info]
    - Hardware Acceleration: {_format_bool(hw_accel)}
        - Accelerated blit: {_format_accel(blit_accel, hw_accel)}
        - Accelerated colorkey blit: {_format_accel(blit_CC_accel, hw_accel)}
        - Accelerated pixel alpha blit: {_format_accel(blit_A_accel, hw_accel)}
    - Pixel Format: {display_info.pixel_format.removeprefix("PIXELFORMAT_")}
    - Window Allowed: {_format_bool(bool(display_info.wm))}

    [System Info]
    - Machine: {platform_info.machine}
    - Architecture: {architecture_info[0]}
    - Linkage: {architecture_info[1]}
    - Processor: {KDS.System.GetProcessorName()}
        - Cores: {psutil.cpu_count(logical=False)}
        - Threads: {psutil.cpu_count(logical=True)}
        - Max Frequency: {psutil.cpu_freq().max / 1000} GHz
        - Supports:
            - SSE2: {_format_bool(cpu_inst_info["SSE2"])}
            - AVX2: {_format_bool(cpu_inst_info["AVX2"])}
            - NEON: {_format_bool(cpu_inst_info["NEON"])}
    - RAM: {memory_info.available / 1_073_741_824:.2f} GB Available ({memory_info.total / 1_073_741_824:.2f} GB Total)
I=====[ DEBUG INFO ]=====I""")

def _log(message: str | BaseException, consoleVisible: bool, stack_info: bool, logLevel: int, color: str, **kwargs: Any) -> None:
    if not running:
        print(f"Log not succesful! Logger has been shut down already. Original message: {message}")
        return

    if isinstance(message, BaseException):
        message = f"{type(message).__name__}: {str(message)}"
    logging.log(logLevel, message, stack_info=stack_info, stacklevel=3, **kwargs)
    if stack_info:
        _frameinfo = inspect.getouterframes(inspect.currentframe(), 2)[2]
        message = f"File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function}\n    {message}\n    Read log file for more details."
    if consoleVisible:
        print(KDS.System.Console.Colored(message, color))

# remembed to also update the individual log functions (debug, info, etc.) as they use a static variable for performance reasons
_logLevelColors: dict[int, str] = {
    logging.DEBUG: "green",
    logging.INFO: "blue",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
}
def debug(message: str | BaseException, consoleVisible: bool = False, stack_info: bool = False) -> None:
    _log(message, consoleVisible, stack_info, logging.DEBUG, "green")

def info(message: str | BaseException, consoleVisible: bool = False, stack_info: bool = False) -> None:
    _log(message, consoleVisible, stack_info, logging.INFO, "blue")

def warning(message: str | BaseException, consoleVisible: bool = False, stack_info: bool = False) -> None:
    _log(message, consoleVisible, stack_info, logging.WARNING, "yellow")

def error(message: str | BaseException, consoleVisible: bool = False, stack_info: bool = False) -> None:
    _log(message, consoleVisible, stack_info, logging.ERROR, "red")

def AutoError(message: str | BaseException, **kwargs: Any) -> None:
    """Generates an automatic error message.

    Args:
        Message (str): The error message.
    """
    _log(message, True, True, 40, "red", **kwargs)

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
        _dump_profile_stats(profile, title="EXPORTED PROFILER DATA")

class MapLoadingProfiler:
    def __init__(self, *, _profile: cProfile.Profile) -> None:
        self._profile: cProfile.Profile = _profile

    @classmethod
    def start(cls) -> Self:
        p: cProfile.Profile = cProfile.Profile()
        instance: Self = cls(_profile=p)
        p.enable()
        return instance

    def stop(self):
        self._profile.disable()
        _dump_profile_stats(self._profile, title="MAP LOADING PROFILER DATA")

def _dump_profile_stats(profile: cProfile.Profile, *, title: str):
    try:
        with open(logFileName, "a+") as f:
            f.write(f"I=========================[ {title} ]=========================I\n\n")
            ps = pstats.Stats(profile, stream=f)
            ps.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
            ps.print_stats()
            f.write(f"I=========================[ {title} ]=========================I\n")
    except IOError as e: AutoError(f"IO Error! Details:\n{e}")

class ExecutionTimeLogger:
    def __init__(self, logLevel: int, msg_prefix: str) -> None:
        self._level: int = logLevel
        self._msg_prefix: str = msg_prefix

        self._startTime: float | None = None
        self._times: list[float] = []

    @property
    def is_running(self) -> bool:
        return self._startTime is not None

    @property
    def accumulatedTime(self) -> float:
        # Calculate the accumulated time using kahan summation algorithm
        # https://www.geeksforgeeks.org/kahan-summation-algorithm/
        count: int = len(self._times)
        if count == 0:
            return 0
        if count == 1:
            return self._times[0]

        sum = 0.0
        c = 0.0

        for f in self._times:
            y = f - c
            t = sum + y

            c = (t - sum) - y
            sum = t

        return sum

    @classmethod
    def debug(cls, msg_prefix: str = "") -> Self:
        return cls(logging.DEBUG, msg_prefix)
    @classmethod
    def info(cls, msg_prefix: str = "") -> Self:
        return cls(logging.INFO, msg_prefix)
    @classmethod
    def warning(cls, msg_prefix: str = "") -> Self:
        return cls(logging.WARNING, msg_prefix)
    @classmethod
    def error(cls, msg_prefix: str = "") -> Self:
        return cls(logging.ERROR, msg_prefix)

    def start(self, message: str, consoleVisible: bool = False, stack_info: bool = False):
        if self._startTime is not None:
            raise RuntimeError("Timer is already running!")

        _log(self._msg_prefix + message, consoleVisible=consoleVisible, stack_info=stack_info, logLevel=self._level, color=_logLevelColors[self._level])

        self._startTime = time.perf_counter()

    def stop(self, message: str, consoleVisible: bool = False, stack_info: bool = False):
        if self._startTime is None:
            raise RuntimeError("Timer wasn't running!")

        seconds: float = time.perf_counter() - self._startTime
        self._times.append(seconds)
        self._startTime = None

        _log(self._msg_prefix + message + f" (took {seconds:.3f} seconds)", consoleVisible=consoleVisible, stack_info=stack_info, logLevel=self._level, color=_logLevelColors[self._level])

def quit():
    global running, faultHandlerEnabled
    if faultHandlerEnabled:
        faultHandlerEnabled = False
        faulthandler.disable()
        sys.stderr.close()
        if stderrPath != None:
            os.remove(stderrPath)
        else:
            AutoError("stderrPath is none when faulthandler is enabled!")

    running = False

    logging.shutdown()
    Profiler(False)
