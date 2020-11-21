import inspect
import logging
import os
import cProfile
import pstats
from termcolor import colored
from pstats import SortKey
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

    logFileName = os.path.join(LogPath, "log_{}.log".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
    logging.basicConfig(filename=logFileName, level=logging.NOTSET, datefmt="%H:%M:%S")
    logging.debug("Created log file: " + logFileName)

class LogType():
    """The list of LogTypes you can log.
    """
    exception = 60
    critical = 50
    error = 40
    warning = 30
    info = 20
    debug = 10

def Log(Log_Type: LogType and int, Message: str, Console_Visible=False):
    """Log a log.

    Args:
        Log_Type (LogType): The type of your log.
        Message (str): The message you want to log.
        Console_Visible (bool, optional): Determines if the message will be displayed in the console. Defaults to False.
    """
    if running:
        logging.log(Log_Type, Message)
        if Console_Visible:
            if Log_Type >= LogType.error: Message = colored(Message, "red")
            elif Log_Type == LogType.warning: Message = colored(Message, "yellow")
            elif Log_Type == LogType.debug: Message = colored(Message, "green")
            else: Message = colored(Message, "cyan")
            print(Message)
    else: print(f"Log not successful! Logger has been shut down already. Original message: {Message}")

def AutoError(Message):
    """Generates an automatic error message.

    Args:
        Message (str): The error message.
        _currentframe: The current frame you get from currentframe().
    """
    _frameinfo = inspect.getouterframes(inspect.currentframe(), 2)[1]
    Log(LogType.error, f"ERROR! File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function} [Exception: {Message}]", True)

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
            ps.strip_dirs().sort_stats(SortKey.CUMULATIVE)
            ps.print_stats()
            log_stream.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I")
            log_stream.close()
        except IOError as e: AutoError(f"IO Error! Details: {e}")
        
def quit():
    global running
    running = False
    logging.shutdown()