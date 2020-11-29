#region Importing
import json
import shutil
import numpy
import pygame
import KDS.Animator
import KDS.AI
import KDS.Gamemode
import KDS.Logging
import os
import zipfile
from typing import Any, Dict, Iterable, List, Tuple
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
    def ToKeyList(jsonPath: str):
        return jsonPath.strip("/").split("/")
    
    @staticmethod
    def Set(filePath: str, jsonPath: str, value: Any):
        config = {}
        if os.path.isfile(filePath):
            try:
                with open(filePath, "r") as f:
                    try: config = json.loads(f.read())
                    except json.decoder.JSONDecodeError as e: KDS.Logging.AutoError(f"JSON Error! Details: {e}")
            except IOError as e: KDS.Logging.AutoError(f"IO Error! Details: {e}")
        
        if len(jsonPath) > 0:
            path = JSON.ToKeyList(jsonPath)
            tmpConfig = config
            for i in range(len(path)):
                p = path[i]
                if i < len(path) - 1:
                    if p not in tmpConfig: tmpConfig[p] = {}
                    tmpConfig = tmpConfig[p]
                else: tmpConfig[p] = value
        else: config = value
        
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
            if len(jsonPath) < 1:
                return config
            path = JSON.ToKeyList(jsonPath)
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
            ↳ tiles.kdf (json)
            ↳ items.kdf (json)
            ↳ enemies.kdf (json)
            ↳ ballistic_objects.kdf (json)
            ↳ player.kdf (json)
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

            ↳ missions.kbf ([undetermined]])
            ↳ inventory.kbf ([undetermined]])
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
    def init(_SaveIndex: int):
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
        KDS.Logging.AutoError(f"Game settings are incorrect! Gamemode: {KDS.Gamemode.gamemode}, SaveIndex: {Save.SaveIndex}.")
        return True
        #decodes and loads a save file to cache
     
    @staticmethod
    def GetExistence(index: int):
        return True if os.path.isfile(os.path.join(SaveDirPath, f"save_{index}.kds")) else False
    
    @staticmethod            
    def SetData(path: str, item: Any):
        JSON.Set(Save.PlayerFileCache, path, item)
     
    @staticmethod
    def GetData(path: str, default: Any):
        return JSON.Get(Save.PlayerFileCache, path, default, True)
    
    ignoreTypes = [
        pygame.Surface,
        pygame.mixer.Sound,
        pygame.Rect,
        KDS.Animator.Animation,
        KDS.Animator.MultiAnimation
        #Inventory is automatically appended here by main
    ]
    
    @staticmethod
    def SetClass(item: Any, filePathFromSaveCache: str, *identificationAttributes: str, identifier: str = "null", ):
        # Älä haasta meitä oikeuteen omena, pliis.
        iVars: Dict[Any] = item.__dict__
        ignoreKeys = []
        for key, var in iVars.items():
            testVar = var
            if isinstance(var, list) or isinstance(var, tuple):
                testVar = var[0] if len(var) > 0 else var
            for ignore in Save.ignoreTypes:
                if isinstance(testVar, ignore):
                    ignoreKeys.append(key)
                    break
        sVars = {}
        for key, var in iVars.items():
            if key not in ignoreKeys:
                if isinstance(var, tuple):
                    sVars[key] = { "saveVarTupleOverride": True, "values": var }
                else: sVars[key] = var
            else: KDS.Logging.Log(KDS.Logging.LogType.debug, f"Ignored variable [{key}, {var}] from {item}.")
        itemIdentifier = identifier if len(identificationAttributes) < 1 else ""
        for i in range(len(identificationAttributes)):
            if i > 0: itemIdentifier += "-"
            itemIdentifier += str(getattr(item, identificationAttributes[i]))
        JSON.Set(os.path.join(SaveCachePath, filePathFromSaveCache), itemIdentifier, sVars)
    
    @staticmethod
    def GetClass(Class, filePathFromSaveCache: str, identifier: str):
        attrs = JSON.Get(os.path.join(SaveCachePath, filePathFromSaveCache), identifier, None, True)
        if attrs == None:
            KDS.Logging.AutoError(f"Saved items of type {type(Class)} with identifier {identifier} not found!")
            return
        instance = Class()
        for k, v in attrs.items():
            if isinstance(v, dict) and "saveVarTupleOverride" in v and v["saveVarTupleOverride"] == True:
                setattr(instance, k, tuple(v["values"]))
            else: setattr(instance, k, v)
        return instance

    @staticmethod
    def SetClassList(item: Iterable[Any], filePathFromSaveCache: str):
        for i, v in enumerate(item): Save.SetClass(v, os.path.join(SaveCachePath, filePathFromSaveCache), identifier=str(i))
        
    @staticmethod
    def GetClassList(Class, filePathFromSaveCache: str):
        cList = JSON.Get(os.path.join(SaveCachePath, filePathFromSaveCache), "", None, True)
        if cList == None:
            KDS.Logging.AutoError(f"Saved items file for type {type(Class)} not found!")
            return
        instanceList = []
        for key in cList:
            instanceList.append(Save.GetClass(Class, filePathFromSaveCache, key))
        return instanceList
    
    @staticmethod
    def SetTiles(tiles, specialTilesD, RespawnAnchorClass):
        tiles = tiles.copy()
        for row in tiles:
            for tile in row:
                if tile.serialNumber in specialTilesD:
                    Save.SetClass(tile, os.path.join(SaveCachePath, "tiles.kdf"), "rect", "serialNumber")
        JSON.Set(os.path.join(SaveCachePath, "tiles.kdf"), "Data/RespawnAnchor/active", f"{RespawnAnchorClass.active.rect.left}-{RespawnAnchorClass.active.rect.top}-{RespawnAnchorClass.active.serialNumber}" if RespawnAnchorClass.active != None else None)
    
    @staticmethod
    def GetTiles(tiles, RespawnAnchorClass):
        savedSpecials = JSON.Get(os.path.join(SaveCachePath, "tiles.kdf"), "", {})
        for row in tiles:
            for tile in row:
                if f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}" in savedSpecials:
                    vals: Dict[str, Any] = savedSpecials[f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}"]
                    for k, v in vals.items():
                        if isinstance(v, dict) and "saveVarTupleOverride" in v and v["saveVarTupleOverride"] == True:
                            setattr(tile, k, tuple(v["values"]))
                        else: setattr(tile, k, v)
                if f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}" == JSON.Get(os.path.join(SaveCachePath, "tiles.kdf"), "Data/RespawnAnchor/active", None):
                    RespawnAnchorClass.active = tile
                        
    @staticmethod
    def SetItems(items):
        for i, v in enumerate(items): Save.SetClass(v, os.path.join(SaveCachePath, "items.kdf"), identifier=f"{v.serialNumber}-{i}")
        
    @staticmethod
    def GetItems(ItemClass):
        #Taas, omena
        iList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "items.kdf"), "", None, True)
        if iList == None:
            KDS.Logging.AutoError("Save file for items not found!")
            return
        instanceList = []
        for key in iList:
            srlNum = int(key.split("-")[0])
            instanceList.append(Save.GetClass(ItemClass.serialNumbers[srlNum], "items.kdf", key))
        return instanceList
    
    @staticmethod
    def SetEnemies(enemies):
        for i, v in enumerate(enemies): Save.SetClass(v, os.path.join(SaveCachePath, "enemies.kdf"), identifier=f"{type(v)}-{i}")
        
    @staticmethod
    def GetEnemies():
        eList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "enemies.kdf"), "", None, True)
        if eList == None:
            KDS.Logging.AutoError("Save file for enemies not found!")
            return
        instanceList = []
        for key in eList:
            typeKey = key.split("-")[0]
            instanceList.append(Save.GetClass(getattr(KDS.AI, typeKey)(), "enemies.kdf", key))
        return instanceList