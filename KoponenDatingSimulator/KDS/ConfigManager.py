#region Importing
import KDS.Logging
import configparser
import os
from inspect import currentframe, getframeinfo
#endregion

def LoadSave(SaveIndex: int, SaveDirectory: str, SaveName: str, DefaultValue: str):
    config = configparser.ConfigParser()
    config.read("saves/save_" + str(SaveIndex) + ".kds")
    try:
        return config.get(SaveDirectory, SaveName)
    except:
        try:
            config.set(SaveDirectory, SaveName, DefaultValue)
            return DefaultValue
        except:
            try:
                config.add_section(SaveDirectory)
                config.set(SaveDirectory, SaveName, DefaultValue)
                return DefaultValue
            except:
                frameinfo = getframeinfo(currentframe())
                KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + frameinfo.lineno + ")\nException: " + str(Exception))
    with open("saves/save_" + str(SaveIndex) + ".kds", "w") as savFile:
        config.write(savFile)
def LoadSetting(SaveDirectory: str, SaveName: str, DefaultValue: str):
    config = configparser.ConfigParser()
    config.read("settings.cfg")
    try:
        return config.get(SaveDirectory, SaveName)
    except:
        try:
            config.set(SaveDirectory, SaveName, DefaultValue)
            return DefaultValue
        except:
            try:
                config.add_section(SaveDirectory)
                config.set(SaveDirectory, SaveName, DefaultValue)
                return DefaultValue
            except:
                frameinfo = getframeinfo(currentframe())
                KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ")\nException: " + str(Exception))
    with open("saves/save_" + "settings.cfg" + ".kds", "w") as savFile:
        config.write(savFile)

def SetSetting(SaveDirectory: str, SaveName: str, SaveValue: str):
    config = configparser.ConfigParser()
    config.read("settings.cfg")
    try:
        config.set(SaveDirectory, SaveName, SaveValue)
    except:
        try:
            config.add_section(SaveDirectory)
            config.set(SaveDirectory, SaveName, SaveValue)
        except:
                frameinfo = getframeinfo(currentframe())
                KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ")\nException: " + str(Exception))
    with open("settings.cfg", "w") as cfg_file:
        config.write(cfg_file)
def SetSave(SaveIndex: int, SaveDirectory: str, SaveName: str, SaveValue: str):
    config = configparser.ConfigParser()
    saveFilePath = "saves/save_" + str(SaveIndex) + ".kds"
    config.read(saveFilePath)
    try:
        config.set(SaveDirectory, SaveName, SaveValue)
    except:
        try:
            config.add_section(SaveDirectory)
            config.set(SaveDirectory, SaveName, SaveValue)
        except:
                frameinfo = getframeinfo(currentframe())
                KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ")\nException: " + str(Exception))
    with open(saveFilePath, "w") as sav_file:
        config.write(sav_file)