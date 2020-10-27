from inspect import getframeinfo
import logging
import os
import cProfile
import pstats
from pstats import SortKey
from datetime import datetime

running = True
AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
logPath = os.path.join(AppDataPath, "logs")
profiler_running = False
profile = None

os.makedirs(logPath, exist_ok=True)
while len(os.listdir(logPath)) >= 5:
    os.remove(os.path.join(logPath, os.listdir(logPath)[0]))

logFileName = os.path.join(logPath, "log_{}.log".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
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
        if Console_Visible: print(Message)
    else: print("Log not successful! Logger has been shut down already.")

def AutoError(Message, _currentframe):
    """Generates an automatic error message.

    Args:
        Message (str): The error message.
        _currentframe: The current frame you get from currentframe().
    """
    _frameinfo = getframeinfo(_currentframe)
    Log(LogType.error, f"ERROR! File \"{_frameinfo.filename}\", line {_frameinfo.lineno}, in {_frameinfo.function} [Exception: {Message}]", True)

def Profiler(enabled):
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
        log_stream = open(logFileName, "a+")
        log_stream.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I\n\n")
        ps = pstats.Stats(profile, stream=log_stream)
        ps.strip_dirs().sort_stats(SortKey.CUMULATIVE)
        ps.print_stats()
        log_stream.write(f"I=========================[ EXPORTED PROFILER DATA ]=========================I")
        log_stream.close()
        
def quit():
    global running
    running = False
    logging.shutdown()