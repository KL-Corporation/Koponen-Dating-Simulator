#region Importing
import json
import pickle
import shutil
from typing import Any
import KDS.Gamemode
import KDS.Logging
import os
import zipfile
#endregion
def init(_AppDataPath: str, _CachePath: str, _SaveDirPath: str):
    global AppDataPath, CachePath, SaveDirPath, SaveCachePath
    AppDataPath = _AppDataPath
    CachePath = _CachePath
    SaveDirPath = _SaveDirPath
    SaveCachePath = os.path.join(CachePath, "save")
    if not os.path.isfile(os.path.join(AppDataPath, "settings.cfg")): shutil.copyfile("Assets/defaultSettings.kdf", os.path.join(AppDataPath, "settings.cfg"))

class JSON:
    @staticmethod
    def Set(filePath: str, jsonPath: str, value: Any):
        config = {}
        if os.path.isfile(filePath):
            try:
                with open(filePath, "r") as f:
                    try: config = json.loads(f.read())
                    except json.decoder.JSONDecodeError as e: KDS.Logging.AutoError(f"JSON Error! Details: {e}")
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
        
        path = jsonPath.split("/")
        tmpConfig = config
        for i in range(len(path)):
            p = path[i]
            if i < len(path) - 1:
                if p not in tmpConfig: tmpConfig[p] = {}
                tmpConfig = tmpConfig[p]
            else: tmpConfig[p] = value
        
        try:
            with open(filePath, "w") as f: f.write(json.dumps(config, sort_keys=True, indent=4))
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
        
    @staticmethod
    def Get(filePath: str, jsonPath: str, defaultValue: Any, warnMissing: bool = False):
        config = {}
        if os.path.isfile(filePath):
            try:
                with open(filePath, "r") as f:
                    try: config = json.loads(f.read())
                    except json.decoder.JSONDecodeError as e: KDS.Logging.AutoError(f"JSON Error! Details: {e}")
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
            path = jsonPath.split("/")
            tmpConfig = config
            for i in range(len(path)):
                p = path[i]
                if p not in tmpConfig:
                    if warnMissing: KDS.Logging.Log(KDS.Logging.LogType.warning, f"No value found in path: {jsonPath} of file: {filePath}. Value of {jsonPath} has been set as default to: {defaultValue}", True)
                    JSON.Set(filePath, jsonPath, defaultValue)
                    return defaultValue
                if i < len(path) - 1: tmpConfig = tmpConfig[p]
                else: return tmpConfig[p]
        else:
            if warnMissing: KDS.Logging.Log(KDS.Logging.LogType.warning, f"No value found in path: {jsonPath} of file: {filePath}. Value of {jsonPath} has been set as default to: {defaultValue}", True)
            JSON.Set(filePath, jsonPath, defaultValue)
            return defaultValue
        KDS.Logging.AutoError("Unknown Error! This code should never execute.")
        return defaultValue

    @staticmethod
    def Serializable(value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except Exception: return False

def GetSetting(path: str, default: Any):
    """
    1. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    2. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    3. DefaultValue, The value that is going to be loaded if no value was found.
    """
    return JSON.Get(os.path.join(AppDataPath, "settings.cfg"), path, default, warnMissing=True)

def SetSetting(path: str, value: Any):
    """
    Automatically fills FilePath to SaveFunction
    1. SaveDirectory, The name of the class (directory) your data will be saved. Please prefer using already established directories.
    2. SaveName, The name of the setting you are saving. Make sure this does not conflict with any other SaveName!
    3. SaveValue, The value that is going to be saved.
    """
    JSON.Set(os.path.join(AppDataPath, "settings.cfg"), path, value)

def GetGameData(path: str):
    return JSON.Get("Assets/GameData.kdf", path, None)

def GetLevelProp(path: str, DefaultValue: Any, listToTuple: bool = True):
    val = JSON.Get(os.path.join(CachePath, "map", "levelprop.kdf"), path, DefaultValue)
    return tuple(val) if isinstance(val, list) and listToTuple else val

class Save:
    WorldDirCache = ""
    PlayerDirCache = ""
    PlayerFileCache = ""
    SaveIndex = -1
    """
    Save File Structure:
        ↳ save_0.kds (.zip)
            ↳ items.kbf (binary)
            ↳ enemies.kbf (binary)
            ↳ explosions.kbf (binary)
            ↳ ballistic_objects.kbf (binary)
            ↳ missions.kbf (binary)
            ↳ data.kdf (json)
                ↳ Player
                    ↳ position (tuple)
                    ↳ health (float)
                    ↳ stamina (float)
                    ↳ Inventory
                        ↳ storage (list)
                        ↳ index (int)
                    ↳ keys: (dict)
                    ↳ farting (bool)
                ↳ Koponen
                    ↳ position (tuple)
                ↳ Renderer
                    ↳ scroll (list)
                    
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
    def SetWorld(path: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            _path = os.path.join(Save.WorldDirCache, path + (".kbf" if os.path.splitext(path)[1] != ".kbf" else ""))
            for item in SaveItem:
                toSaveF = getattr(item, "toSave", None)
                if callable(toSaveF): toSaveF()
            try:
                with open(_path, "wb") as f:
                    temp = pickle.dumps(SaveItem)
                    f.write(temp)
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
            for item in SaveItem:
                fromSaveF = getattr(item, "fromSave", None)
                if callable(fromSaveF): fromSaveF()
    
    @staticmethod
    def GetWorld(path: str, DefaultValue):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            _path = os.path.join(Save.WorldDirCache, path + (".kbf" if os.path.splitext(path)[1] != ".kbf" else ""))
            if os.path.isfile(_path):
                with open(_path, "rb") as f:
                    data = pickle.loads(f.read())
                for item in data:
                    fromSaveF = getattr(item, "fromSave", None)
                    if callable(fromSaveF): fromSaveF()
                return data
            else: return DefaultValue
        else: return DefaultValue
    
    @staticmethod            
    def SetPlayer(path: str, item: Any):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            JSON.Set(Save.PlayerFileCache, path, item)
     
    @staticmethod
    def GetPlayer(path: str, default: Any):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            JSON.Get(Save.PlayerFileCache, path, default)
        else: return default

"""
def SetJSONLegacy(FilePath: str, SaveDirectory: str, SaveName: str, SaveValue):
    if os.path.isfile(FilePath):
        try:
            with open(FilePath, "r") as f:
                try: config = json.loads(f.read())
                except json.decoder.JSONDecodeError: config = {}
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
    else:
        config = {}
    if SaveDirectory not in config:
        config[SaveDirectory] = {}
    config[SaveDirectory][SaveName] = SaveValue
    try:
        with open(FilePath, "w") as f: f.write(json.dumps(config, sort_keys=True, indent=4))
    except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
    
def GetJSONLegacy(FilePath: str, SaveDirectory: str, SaveName: str, DefaultValue):
    if os.path.isfile(FilePath):
        try:
            with open(FilePath, "r") as f:
                try: config = json.loads(f.read())
                except json.decoder.JSONDecodeError: config = {}
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
    else:
        config = {}
    if SaveDirectory not in config:
        config[SaveDirectory] = {}
    if SaveName not in config[SaveDirectory]:
        config[SaveDirectory][SaveName] = DefaultValue
        try:
            with open(FilePath, "w") as f: f.write(json.dumps(config, sort_keys=True, indent=4))
        except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
    return config[SaveDirectory][SaveName]
"""