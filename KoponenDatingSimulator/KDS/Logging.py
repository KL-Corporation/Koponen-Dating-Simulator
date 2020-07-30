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

def Log(Log_Type: LogType, Message: str, Console_Visible=False):
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