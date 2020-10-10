#region Importing
import json
from os import rename
import pickle
import shutil
import numpy
import KDS.Gamemode
import KDS.Logging
import configparser
import os
import zipfile
from inspect import currentframe, getframeinfo
#endregion

AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
CachePath = os.path.join(AppDataPath, "cache")
SaveDirPath = os.path.join(AppDataPath, "saves")
SaveCachePath = os.path.join(CachePath, "save")

def init():
    if not os.path.isdir(SaveDirPath):
        os.makedirs(SaveDirPath, exist_ok=True)

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
            with open(FilePath, "w") as cfg_file:
                config.write(cfg_file)
                cfg_file.close()
            return DefaultValue
    else:
        config.add_section(SaveDirectory)
        if config.has_option(SaveDirectory, SaveName):
            return config.get(SaveDirectory, SaveName)
        else:
            with open(FilePath, "w") as cfg_file:
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
    with open(FilePath, "w") as cfg_file:
        config.write(cfg_file)
        cfg_file.close()
        
class Save:
    WorldDirCache = os.path.join(SaveCachePath, "WorldData")
    PlayerDirCache = os.path.join(SaveCachePath, "PlayerData")
    PlayerFileCache = os.path.join(PlayerDirCache, "data.kdf")
    SaveIndex = -1
    """
    Save File Structure:
        ↳ save_0.kds (.zip)
            ↳ WorldData
                ↳ items.kbf (binary)
                ↳ enemies.kbf (binary)
                ↳ explosions.kbf (binary)
                ↳ ballistic_objects.kbf (binary)
            ↳ PlayerData
                ↳ data.kdf (json)
    """
    class DataType:
        World = "world"
        Player = "player"
        
    @staticmethod
    def quit():
        if os.path.isdir(SaveCachePath):
            shutil.make_archive(os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds"), 'zip', SaveCachePath)
            shutil.rmtree(SaveCachePath)
        #encodes and stores a save file to storage

    @staticmethod
    def init(_SaveIndex: int):
        Save.quit()
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            Save.SaveIndex = _SaveIndex
            if os.path.isdir(SaveCachePath):
                shutil.rmtree(SaveCachePath)
            os.makedirs(SaveCachePath)
            os.mkdir(Save.WorldDirCache)
            os.mkdir(Save.PlayerDirCache)
            _path = os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds")
            if os.path.isfile(_path):
                zipfile.ZipFile(_path, "r").extractall(Save.PlayerDirCache)
        #decodes and loads a save file to cache
        
    @staticmethod
    def SetWorld(SafeName: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            for item in SaveItem:
                toStringF = getattr(item, "toString2", None)
                if toStringF == None:
                    toStringF = getattr(item, "toString", None)
                if callable(toStringF):
                    toStringF()
                jutskia = dir(item)
                for jutska in jutskia:
                    #print(jutska, getattr(item, jutska))
                    pass
            with open(os.path.join(Save.WorldDirCache, SafeName + ".kbf"), "wb") as f:
                temp = pickle.dumps(SaveItem)
                f.write(temp)
            for item in SaveItem:
                fromStringF = getattr(item, "fromString", None)
                if callable(fromStringF):
                    fromStringF()
    
    @staticmethod            
    def SetPlayer(SafeName: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            data = {}
            if os.path.isfile(Save.PlayerFileCache):
                with open(Save.PlayerFileCache, "r") as f:
                    data = json.loads(f.read())
            data[SafeName] = SaveItem
            with open(Save.PlayerFileCache, "w") as f:
                f.write(json.dumps(data, sort_keys=True, indent=4))
    
    @staticmethod
    def GetWorld(SafeName: str, DefaultValue):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            _path = os.path.join(Save.WorldDirCache, SafeName + ".kbf")
            if os.path.isfile(_path):
                with open(_path, "rb") as f:
                    data = pickle.loads(f.read())
                for item in data:
                    fromStringF = getattr(item, "fromString", None)
                    if callable(fromStringF):
                        fromStringF()
                return data
            else:
                return DefaultValue
        else:
            return DefaultValue
        
    @staticmethod
    def GetPlayer(SafeName: str, DefaultValue):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            if os.path.isfile(Save.PlayerFileCache):
                with open(Save.PlayerFileCache, "r") as f:
                    data = json.loads(f.read())
                if SafeName in data:
                    return data[SafeName]
                else:
                    return DefaultValue
            else:
                return DefaultValue
        else:
            return DefaultValue