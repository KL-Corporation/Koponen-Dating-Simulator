import inspect
import traceback
import logging
import os
import cProfile
import pstats
from typing import Any
from pygame.draw import line
from termcolor import colored
from datetime import datetime

running = False
profiler_running = False
profile = None
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

def __log(message: str, consoleVisible: bool, stack_info: bool, logLevel: int, color: str):
    _frameinfo = inspect.getouterframes(inspect.currentframe(), 2)[2]
    logging.log(logLevel, message, stack_info=stack_info, stacklevel=4)
    if stack_info:
        message = f"File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function}\n    {message}\n    Read log file for more details."
    if consoleVisible: print(colored(message, color))

def debug(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.DEBUG, "green")
    
def info(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.INFO, "blue")
    
def warning(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.WARNING, "yellow")
    
def error(message: str, consoleVisible: bool = False, stack_info: bool = False):
    __log(message, consoleVisible, stack_info, logging.ERROR, "red")

def AutoError(message):
    """Generates an automatic error message.

    Args:
        Message (str): The error message.
    """
    if running:
        logging.exception(message, stack_info=True)
        printInfo = inspect.getouterframes(inspect.currentframe())[1]
        print(colored(f"File \"{printInfo.filename}\", line {printInfo.lineno}, in {printInfo.function}\nException: {message}\nRead log file for more details.", "red"))
    else: print(f"Log not successful! Logger has been shut down already. Original message: {message}")

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
            log_stream = open(logFileName, "a+")
            log_stream.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I\n\n")
            ps = pstats.Stats(profile, stream=log_stream)
            ps.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
            ps.print_stats()
            log_stream.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I")
            log_stream.close()
        except IOError as e: AutoError(f"IO Error! Details: {e}")
        
def quit():
    global running
    running = False
    logging.shutdown()