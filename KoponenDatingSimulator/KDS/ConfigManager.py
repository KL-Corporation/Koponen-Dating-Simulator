#region Importing
import KDS.Logging
import configparser
import os
from inspect import currentframe, getframeinfo
#endregion

AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
saveDirPath = os.path.join(AppDataPath, "saves")
saveCachePath = CachePath = os.path.join(AppDataPath, "cache", "save")

def init():
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    if not os.path.isdir(saveCachePath):
        os.mkdir(saveCachePath)

def GetSetting(SaveDirectory: str, SaveName: str, DefaultValue: str):
    """
    1. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    2. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    3. DefaultValue, The value that is going to be loaded if no value was found.
    """
    FilePath = os.path.join(AppDataPath, "settings.cfg")
    config = configparser.ConfigParser()
    config.read(FilePath)
    if config.has_section(SaveDirectory):
        if config.has_option(SaveDirectory, SaveName):
            return config.get(SaveDirectory, SaveName)
        else:
            config.set(SaveDirectory, SaveName, DefaultValue)
            with open(FilePath, "w+") as cfg_file:
                config.write(cfg_file)
                cfg_file.close()
            return DefaultValue
    else:
        config.add_section(SaveDirectory)
        if config.has_option(SaveDirectory, SaveName):
            return config.get(SaveDirectory, SaveName)
        else:
            with open(FilePath, "w+") as cfg_file:
                config.write(cfg_file)
                cfg_file.close()
            config.set(SaveDirectory, SaveName, DefaultValue)
            return DefaultValue

def SetSetting(SaveDirectory: str, SaveName: str, SaveValue: str):
    """
    Automatically fills FilePath to SaveFunction
    1. SaveDirectory, The name of the class (directory) your data will be saved. Please prefer using already established directories.
    2. SaveName, The name of the setting you are saving. Make sure this does not conflict with any other SaveName!
    3. SaveValue, The value that is going to be saved.
    """
    FilePath = os.path.join(AppDataPath, "settings.cfg")
    config = configparser.ConfigParser()
    config.read(FilePath)
    if config.has_section(SaveDirectory):
        config.set(SaveDirectory, SaveName, SaveValue)
    else:
        config.add_section(SaveDirectory)
        config.set(SaveDirectory, SaveName, SaveValue)
    with open(FilePath, "w+") as cfg_file:
        config.write(cfg_file)
        cfg_file.close()
        
class Save:
    @staticmethod
    def init():
        #decodes and loads a save file to cache
        pass
        
    @staticmethod
    def SetSave(SaveIndex: int, SafeName: str, SaveItem: str or list):
        pass

    @staticmethod
    def GetSave(SaveIndex: int, SafeName: str, DefaultValue: str or list):
        pass
    
    @staticmethod
    def quit():
        #encodes and stores a save file to storage
        pass