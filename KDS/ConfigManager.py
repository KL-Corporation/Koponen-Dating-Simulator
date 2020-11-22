#region Importing
import json
import dill as pickle
import shutil
import pygame
import KDS.Animator
import KDS.Gamemode
import KDS.Logging
import os
import zipfile
from typing import Any, Dict, List, Tuple
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
            ↳ inventory.kbf (binary)
            ↳ data.kdf (json)
                ↳ Player
                    ↳ position (tuple)
                    ↳ health (float)
                    ↳ stamina (float)
                    ↳ keys: (dict)
                    ↳ farting (bool)
                ↳ Koponen
                    ↳ position (tuple)
                ↳ Game
                    ↳ scroll (list)
                    ↳ SpecialTiles
                        ↳ [{pos[0]}-{pos[1]}-{serial}] (dict of class values except pygame shite)
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
                shutil.move(_path + ".zip", _path)
            shutil.rmtree(SaveCachePath)
        #encodes and stores a save file to storage

    @staticmethod
    def init(_SaveIndex: int) -> bool:
        """decodes and loads a save file to cache.

        Args:
            _SaveIndex (int): Index of the savegame.

        Returns:
            bool: Is the save new or old.
        """
        Save.PlayerFileCache = os.path.join(SaveCachePath, "data.kdf")
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
                return False
        return True

        #decodes and loads a save file to cache
     
    @staticmethod
    def GetExistence(index: int):
        return True if os.path.isfile(os.path.join(SaveDirPath, f"save_{index}.kds")) else False
    
    @staticmethod
    def ConvertToSave(SaveItem):
        if not hasattr(SaveItem, "toSave"):
            for item in SaveItem:
                if hasattr(item, "toSave"):
                    if callable(item.toSave): item.toSave()
                    else: KDS.Logging.AutoError(f"toSave of {item} is not callable!")
        elif callable(SaveItem.toSave): SaveItem.toSave()
        else: KDS.Logging.AutoError(f"toSave of {SaveItem} is not callable!")
    
    @staticmethod
    def ConvertFromSave(SaveItem):
        if not hasattr(SaveItem, "fromSave"):
            for item in SaveItem:
                if hasattr(item, "fromSave"):
                    if callable(item.fromSave): item.fromSave()
                    else: KDS.Logging.AutoError(f"fromSave of {item} is not callable!")
                for thingy in item.__dict__:
                    print(item.__dict__[thingy])
        elif callable(SaveItem.fromSave): SaveItem.fromSave()
        else: KDS.Logging.AutoError(f"fromSave of {SaveItem} is not callable!")
    
    @staticmethod
    def SetWorld(path: str, SaveItem):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            _path = os.path.join(SaveCachePath, path + (".kbf" if os.path.splitext(path)[1] != ".kbf" else ""))
            Save.ConvertToSave(SaveItem)
            try:
                with open(_path, "wb") as f:
                    temp = pickle.dumps(SaveItem)
                    f.write(temp)
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
            Save.ConvertFromSave(SaveItem)
    
    @staticmethod
    def GetWorld(path: str, DefaultValue):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            _path = os.path.join(SaveCachePath, path + (".kbf" if os.path.splitext(path)[1] != ".kbf" else ""))
            if os.path.isfile(_path):
                try:
                    with open(_path, "rb") as f:
                        data = pickle.loads(f.read())
                        Save.ConvertFromSave(data)
                    return data
                except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
        return DefaultValue
    
    @staticmethod            
    def SetData(path: str, item: Any):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            JSON.Set(Save.PlayerFileCache, path, item)
     
    @staticmethod
    def GetData(path: str, default: Any):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            return JSON.Get(Save.PlayerFileCache, path, default)
        else: return default
    
    ignoreTileTypes = [
        pygame.Surface,
        pygame.mixer.Sound,
        pygame.Rect,
        KDS.Animator.Animation,
        KDS.Animator.MultiAnimation
    ]
    
    @staticmethod
    def SetTiles(tiles, specialTilesD):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            tiles = tiles.copy()
            for row in tiles:
                for tile in row:
                    if tile.serialNumber in specialTilesD:
                        tileVars: Dict[Any] = tile.__dict__
                        ignoreKeys = []
                        for key in tileVars:
                            if isinstance(tileVars[key], list) or isinstance(tileVars[key], tuple):
                                for ignore in Save.ignoreTileTypes:
                                    if isinstance(tileVars[key][0], ignore):
                                        ignoreKeys.append(key)
                                        break
                            for ignore in Save.ignoreTileTypes:
                                if isinstance(tileVars[key], ignore):
                                    ignoreKeys.append(key)
                                    break
                        saveVars = {}
                        for key, var in tileVars.items():
                            if key not in ignoreKeys:
                                saveVars[key] = var
                            else:
                                KDS.Logging.Log(KDS.Logging.LogType.debug, f"Ignored variable [{key}, {var}] from special tile of type {tile.serialNumber} at position {tile.rect.topleft}.")
                        Save.SetData(f"Game/SpecialTiles/{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}", saveVars)
    
    @staticmethod
    def GetTiles(tiles):
        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story:
            savedSpecials = Save.GetData("Game/SpecialTiles", {})
            for row in tiles:
                for tile in row:
                    if f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}" in savedSpecials:
                        vals: Dict[str, Any] = savedSpecials[f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}"]
                        for k, v in vals.items():
                            setattr(tile, k, v)

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