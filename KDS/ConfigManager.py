#region Importing
import json
import pickle
import shutil
import KDS.Gamemode
import KDS.Logging
import os
import zipfile
from inspect import currentframe
#endregion
def init(_AppDataPath: str, _CachePath: str, _SaveDirPath: str):
    global AppDataPath, CachePath, SaveDirPath, SaveCachePath
    AppDataPath = _AppDataPath
    CachePath = _CachePath
    SaveDirPath = _SaveDirPath
    SaveCachePath = os.path.join(CachePath, "save")

def GetJSON(FilePath: str, SaveDirectory: str, SaveName: str, DefaultValue):
    if os.path.isfile(FilePath):
        try:
            with open(FilePath, "r") as f:
                try: config = json.loads(f.read())
                except json.decoder.JSONDecodeError: config = {}
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
    else:
        config = {}
    if SaveDirectory not in config:
        config[SaveDirectory] = {}
    if SaveName not in config[SaveDirectory]:
        config[SaveDirectory][SaveName] = DefaultValue
        try:
            with open(FilePath, "w") as f: f.write(json.dumps(config, sort_keys=True, indent=4))
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
    return config[SaveDirectory][SaveName]

def GetSetting(SaveDirectory: str, SaveName: str, DefaultValue):
    """
    1. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    2. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    3. DefaultValue, The value that is going to be loaded if no value was found.
    """
    return GetJSON(os.path.join(AppDataPath, "settings.cfg"), SaveDirectory, SaveName, DefaultValue)

def GetGameSetting(*path: str):
    try:
        with open("Assets/GameSettings.kdf") as f:
            data: dict = json.loads(f.read())
    except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
    value = data
    for p in path:
        value = value[p]
    return value

def GetLevelProp(SaveDirectory: str, SaveName: str, DefaultValue):
    return GetJSON(os.path.join(CachePath, "map", "levelprop.kdf"), SaveDirectory, SaveName, DefaultValue)

def SetJSON(FilePath: str, SaveDirectory: str, SaveName: str, SaveValue):
    if os.path.isfile(FilePath):
        try:
            with open(FilePath, "r") as f:
                try: config = json.loads(f.read())
                except json.decoder.JSONDecodeError: config = {}
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
    else:
        config = {}
    if SaveDirectory not in config:
        config[SaveDirectory] = {}
    config[SaveDirectory][SaveName] = SaveValue
    try:
        with open(FilePath, "w") as f: f.write(json.dumps(config, sort_keys=True, indent=4))
    except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())

def SetSetting(SaveDirectory: str, SaveName: str, SaveValue):
    """
    Automatically fills FilePath to SaveFunction
    1. SaveDirectory, The name of the class (directory) your data will be saved. Please prefer using already established directories.
    2. SaveName, The name of the setting you are saving. Make sure this does not conflict with any other SaveName!
    3. SaveValue, The value that is going to be saved.
    """
    SetJSON(os.path.join(AppDataPath, "settings.cfg"), SaveDirectory, SaveName, SaveValue)

class Save:
    WorldDirCache = ""
    PlayerDirCache = ""
    PlayerFileCache = ""
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
            if os.path.isfile(Save.PlayerFileCache):
                _path = os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds")
                shutil.make_archive(_path, 'zip', SaveCachePath)
                shutil.move(f"{_path}.zip", _path)
            shutil.rmtree(SaveCachePath)
        #encodes and stores a save file to storage

    @staticmethod
    def init(_SaveIndex: int):
        Save.WorldDirCache = os.path.join(SaveCachePath, "WorldData")
        Save.PlayerDirCache = os.path.join(SaveCachePath, "PlayerData")
        Save.PlayerFileCache = os.path.join(Save.PlayerDirCache, "data.kdf")
        Save.SaveIndex = _SaveIndex
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story and Save.SaveIndex >= 0:
            if os.path.isfile(Save.PlayerFileCache):
                Save.quit()
            if os.path.isdir(SaveCachePath):
                shutil.rmtree(SaveCachePath)
            os.makedirs(SaveCachePath, exist_ok=True)
            _path = os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds")
            if os.path.isfile(_path):
                zipfile.ZipFile(_path, "r").extractall(SaveCachePath)
            os.makedirs(Save.WorldDirCache, exist_ok=True)
            os.makedirs(Save.PlayerDirCache, exist_ok=True)
            
        #decodes and loads a save file to cache
     
    @staticmethod
    def GetExistence(index: int):
        return True if os.path.isfile(os.path.join(SaveDirPath, f"save_{index}.kds")) else False
     
    @staticmethod
    def SetWorld(SafeName: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            for item in SaveItem:
                toStringF = getattr(item, "toString", None)
                if callable(toStringF):
                    toStringF()
            try:
                with open(os.path.join(Save.WorldDirCache, SafeName + ".kbf"), "wb") as f:
                    temp = pickle.dumps(SaveItem)
                    f.write(temp)
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
            for item in SaveItem:
                fromStringF = getattr(item, "fromString", None)
                if callable(fromStringF):
                    fromStringF()
    
    @staticmethod            
    def SetPlayer(SafeName: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            if os.path.isfile(Save.PlayerFileCache):
                try:
                    with open(Save.PlayerFileCache, "r") as f:
                        try:
                            data = json.loads(f.read())
                        except json.decoder.JSONDecodeError:
                            data = {}
                except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
            else:
                data = {}
            data[SafeName] = SaveItem
            try:
                with open(Save.PlayerFileCache, "w") as f:
                    f.write(json.dumps(data, sort_keys=True, indent=4))
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
    
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
                try:
                    with open(Save.PlayerFileCache, "r") as f:
                        data = json.loads(f.read())
                except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}", currentframe())
                if SafeName in data:
                    return data[SafeName]
                else:
                    return DefaultValue
            else:
                return DefaultValue
        else:
            return DefaultValue