import cProfile
import inspect
import logging
import os
import pstats
import KDS.System
from datetime import datetime
from typing import Any

running = False
profiler_running = False
profile = cProfile.Profile()

def init(_AppDataPath: str, _LogPath: str):
    global running, AppDataPath, LogPath, logFileName
    running = True
    AppDataPath = _AppDataPath
    LogPath = _LogPath

    while len(os.listdir(LogPath)) >= 5:
        os.remove(os.path.join(LogPath, os.listdir(LogPath)[0]))

    fileTimeFormat = "%Y-%m-%d-%H-%M-%S"
    logTimeFormat = "%H:%M:%S"
    logFormat = "%(levelname)s-%(asctime)s: %(message)s"
    logFileName = os.path.join(LogPath, f"log_{datetime.now().strftime(fileTimeFormat)}.log")
    logging.basicConfig(filename=logFileName, format=logFormat, level=logging.NOTSET, datefmt=logTimeFormat)
    logging.debug("Created log file: " + logFileName)

def __log(message: str, consoleVisible: bool, stack_info: bool, logLevel: int, color: str, **kwargs: Any):
    if running:
        _frameinfo = inspect.getouterframes(inspect.currentframe(), 2)[2]
        logging.log(logLevel, message, stack_info=stack_info, stacklevel=4, **kwargs)
        if stack_info:
            message = f"File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function}\n    {message}\n    Read log file for more details."
        if consoleVisible: print(KDS.System.Console.Colored(message, color))
        return
    print(f"Log not succesful! Logger has been shut down already. Original message: {message}")

def debug(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.DEBUG, "green")

def info(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.INFO, "blue")

def warning(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.WARNING, "yellow")

def error(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.ERROR, "red")

def AutoError(message: str, **kwargs: Any):
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
