import logging
import os
from datetime import datetime

def init():
    """Initialises the logger.
    """
    AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
    logPath = os.path.join(AppDataPath, "logs")
    if os.path.exists(logPath) and os.path.isdir(logPath):
        logFiles = os.listdir(logPath)
    else:
        os.mkdir(logPath)
        logFiles = os.listdir(logPath)

    while len(logFiles) >= 5:
        os.remove(os.path.join(logPath, logFiles[0]))
        logFiles = os.listdir(logPath)

    now = datetime.now()
    logFileName = os.path.join(logPath, "log_" + now.strftime("%Y-%m-%d-%H-%M-%S") + ".log")
    logging.basicConfig(filename=logFileName, level=logging.NOTSET)
    logging.debug("Created log file: " + logFileName)
    logging.info('Initialising Game...')

class LogType():
    """The list of LogTypes you can log.
    """
    execption = 70
    log = 60
    critical = 50
    error = 40
    warning = 30
    info = 20
    debug = 10
    notset = 0

def Log(Log_Type: LogType, Message: str, Console_Visible=False):
    """Log a log.

    Args:
        Log_Type (LogType): The type of your log.
        Message (str): The message you want to log.
        Console_Visible (bool, optional): Determines if the message will be displayed in the console. Defaults to False.
    """
    if Log_Type == LogType.execption:
        logging.exception(Message)
    elif Log_Type == LogType.log:
        logging.log(Message)
    elif Log_Type == LogType.critical:
        logging.critical(Message)
    elif Log_Type == LogType.error:
        logging.error(Message)
    elif Log_Type == LogType.warning:
        logging.warning(Message)
    elif Log_Type == LogType.info:
        logging.info(Message)
    elif Log_Type == LogType.debug:
        logging.debug(Message)
    elif Log_Type == LogType.notset:
        logging.NOTSET(Message)
        
    if Console_Visible:
        print(Message)