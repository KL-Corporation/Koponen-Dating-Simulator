import logging
import os
from datetime import datetime

def init():
    try:
        logFiles = os.listdir("logs/")
    except:
        os.mkdir("logs")
        f = open("logs/initLog.log", "w+")
        f.write("*THIS LOG INITIALISES THE LOGGING SYSTEM*\n\n\nDO NOT DELETE THIS LOG FILE!")
        f.close()
        logFiles = os.listdir("logs/")

    while len(logFiles) >= 5:
        os.remove("logs/" + logFiles[0])
        logFiles = os.listdir("logs/")

    now = datetime.now()
    logFileName = "logs/log_" + now.strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    logging.basicConfig(filename=logFileName, level=logging.NOTSET)
    logging.debug("Created log file: " + logFileName)
    logging.info('Initialising Game...')

class LogType():
    execption = 70
    log = 60
    critical = 50
    error = 40
    warning = 30
    info = 20
    debug = 10
    notset = 0

def Log(logType: LogType, message: str, consoleVisible: bool):
    if logType == LogType.execption:
        logging.exception(message)
    elif logType == LogType.log:
        logging.log(message)
    elif logType == LogType.critical:
        logging.critical(message)
    elif logType == LogType.error:
        logging.error(message)
    elif logType == LogType.warning:
        logging.warning(message)
    elif logType == LogType.info:
        logging.info(message)
    elif logType == LogType.debug:
        logging.debug(message)
    elif logType == LogType.notset:
        logging.NOTSET(message)
    if consoleVisible:
        print(message)