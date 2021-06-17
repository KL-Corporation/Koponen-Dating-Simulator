#region Importing
from datetime import datetime
import json
import os
import shutil
import re
from typing import Any, Dict, List, Optional, Union

import KDS.AI
import KDS.Animator
import KDS.Gamemode
import KDS.Logging
import KDS.Missions
import KDS.System
import KDS.World
import KDS.Scores
#endregion

def init(_AppDataPath: str, _CachePath: str, _SaveDirPath: str):
    global AppDataPath, CachePath, SaveDirPath, SaveCachePath, SettingsPath
    AppDataPath = _AppDataPath
    CachePath = _CachePath
    SaveDirPath = _SaveDirPath
    SaveCachePath = os.path.join(CachePath, "save")
    SettingsPath = os.path.join(AppDataPath, "settings.cfg")
    if not os.path.isfile(SettingsPath):
        OverrideDefaultSettings()

    # Could be put into an else statement, but it's just unnecessary nesting
    defaultVersion = JSON.Get("Assets/Data/defaultSettings.kdf", "Data/settingsFileVersion", True, writeMissing=False, warnMissing=True, encoding="utf-8")
    currentVersion = JSON.Get(SettingsPath, "Data/settingsFileVersion", False, writeMissing=False, warnMissing=True, encoding="utf-8")
    if defaultVersion != currentVersion:
        OverrideDefaultSettings()

class JSON:
    NULLPATH = "[config_manager_null_path]"
    EMPTY = "[config_manager_empty_json]"

    @staticmethod
    def ToKeyList(jsonPath: str):
        return re.sub(r"\/+", "/", jsonPath.strip("/")).split("/")

    @staticmethod
    def Set(filePath: str, jsonPath: str, value: Any, sortKeys: bool = True, encoding: str = None) ->  Union[Any, None]:
        if value == JSON.EMPTY:
            value = {}

        config: Dict[str, Any] = {}
        if os.path.isfile(filePath):
            try:
                with open(filePath, "r", encoding=encoding) as f:
                    try:
                        config = json.loads(f.read())
                    except json.decoder.JSONDecodeError as e:
                        KDS.Logging.AutoError(f"JSON Error! Details: {e}")
            except IOError as e:
                KDS.Logging.AutoError(f"IO Error! Details: {e}")

        if jsonPath != JSON.NULLPATH:
            path = JSON.ToKeyList(jsonPath)
            tmpConfig = config
            for i in range(len(path)):
                p = path[i]
                if i < len(path) - 1:
                    if p not in tmpConfig:
                        tmpConfig[p] = {}
                    tmpConfig = tmpConfig[p]
                elif p not in tmpConfig or tmpConfig[p] != value:
                    tmpConfig[p] = value
                else:
                    return value
        elif config != value:
            config = value
        else:
            return value

        try:
            with open(filePath, "w", encoding=encoding) as f:
                f.write(json.dumps(config, sort_keys = sortKeys, indent = 4))
            return value
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")
            return None

    @staticmethod
    def Get(filePath: str, jsonPath: str, defaultValue: Any, writeMissing: bool = True, warnMissing: bool = False, encoding: str = None) -> Any:
        config: Dict[str, Any] = {}
        if not os.path.isfile(filePath):
            if warnMissing:
                KDS.Logging.warning(f"No file found in path: {filePath}." + (f" Value of the file's {jsonPath} has been set as default to: {defaultValue}" if writeMissing else ""), True)
            if writeMissing:
                JSON.Set(filePath, jsonPath, defaultValue)
            return defaultValue

        try:
            with open(filePath, "r", encoding=encoding) as f:
                try:
                    config = json.loads(f.read())
                except json.decoder.JSONDecodeError as e:
                    KDS.Logging.AutoError(f"JSON Error with file {filePath}! Details: {e}")
        except IOError as e:
            KDS.Logging.AutoError(f"IO Error! Details: {e}")

        if jsonPath == JSON.NULLPATH:
            return config

        path = JSON.ToKeyList(jsonPath)
        tmpConfig = config
        for i in range(len(path)):
            p = path[i]
            if p not in tmpConfig:
                if warnMissing:
                    KDS.Logging.warning(f"No value found in path: {jsonPath} of file: {filePath}." + (f" Value of {jsonPath} has been set as default to: {defaultValue}" if writeMissing else ""), True)
                if writeMissing:
                    JSON.Set(filePath, jsonPath, defaultValue)
                return defaultValue
            if i < len(path) - 1:
                tmpConfig = tmpConfig[p]
            else:
                return tmpConfig[p]
        KDS.Logging.AutoError("Unknown Error! This code should never execute.")
        return defaultValue

def GetSetting(path: str, default: Any, writeMissingOverride: Optional[bool] = None, warnMissingOverride: Optional[bool] = None):
    """
    1. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    2. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    3. DefaultValue, The value that is going to be loaded if no value was found.
    """
    output = JSON.Get(SettingsPath, path, default, warnMissing=True if warnMissingOverride == None else warnMissingOverride, writeMissing=default is not ... if writeMissingOverride == None else writeMissingOverride, encoding="utf-8")
    if default is not ... or output is not ...:
        return output

    KDS.Logging.warning("Loading setting from \"defaultSettings.kdf\"!", True)
    output = JSON.Get("Assets/Data/defaultSettings.kdf", path, None, writeMissing=False, warnMissing=False, encoding="utf-8")
    if output == None:
        raise RuntimeError(f"No default setting found on path: \"{path}\"")
    SetSetting(path, output)
    return output

def SetSetting(path: str, value: Any) -> Any:
    """
    1. SaveDirectory, The name of the class (directory) your data will be saved. Please prefer using already established directories.
    2. SaveName, The name of the setting you are saving. Make sure this does not conflict with any other SaveName!
    3. SaveValue, The value that is going to be saved.
    """
    return JSON.Set(SettingsPath, path, value, sortKeys=False, encoding="utf-8")

def ToggleSetting(path: str, default: Union[bool, Any]):
    """### USE ``Any`` TO ONLY PASS IN ELLIPSIS!"""
    v = GetSetting(path, default)
    SetSetting(path, not v)

def OverrideDefaultSettings():
    with open(SettingsPath, "w", encoding="utf-8") as settingsFile:
        with open("Assets/Data/defaultSettings.kdf", "r", encoding="utf-8") as defaultsFile:
            settingsFile.write(defaultsFile.read())

def GetGameData(path: str):
    return JSON.Get("Assets/GameData.kdf", path, None, False, True)

class LevelProp:
    cachedValues: Dict[str, Any] = {}

    @staticmethod
    def init(MapPath: str):
        try:
            with open(os.path.join(MapPath, "levelprop.kdf"), "r") as f:
                LevelProp.cachedValues = json.loads(f.read())
        except IOError as e:
            KDS.Logging.AutoError(e)
        except json.decoder.JSONDecodeError as e:
            KDS.Logging.AutoError(e)

    @staticmethod
    def Get(path: str, DefaultValue: Any) -> Any:
        paths: List[str] = JSON.ToKeyList(path)
        tmpvals = LevelProp.cachedValues
        for i in range(len(paths)):
            p = paths[i]
            if p not in tmpvals:
                return DefaultValue
            if i < len(paths) - 1: tmpvals = tmpvals[p]
            else: return tmpvals[p]

        KDS.Logging.AutoError("This code should not execute!")
        return DefaultValue

class Save:
    Active = None

    @staticmethod
    def ToPath(index: int):
        return os.path.join(SaveDirPath, f"{index}.kds")

    @staticmethod
    def GetMenuData():
        retu: List[Optional[Dict[str, Any]]] = []
        for i in range(3):
            path = Save.ToPath(i)
            if os.path.isfile(path):
                retu.append({
                    "name": JSON.Get(path, "Story/playerName", "<name-error>", False, True),
                    "progress": ((JSON.Get(path, "Story/index", -1, False, True) - 1) / GetGameData("Story/levelCount")),
                    "grade": JSON.Get(path, "Story/examGrade", -1.0, False, True),
                    "score": JSON.Get(path, "Stats/score", -1, False, True),
                    "playtime": JSON.Get(path, "Stats/playtime", -1, False, True),
                    "lastPlayedTimestamp": JSON.Get(path, "Stats/lastPlayed", -1, False, True)
                })
            else:
                retu.append(None)
        return tuple(retu)

    class StoryData:
        def __init__(self) -> None:
            self.playerName: str = "<name-error>"
            self.index: int = 1
            self.examGrade: float = -1.0
            self.principalName: str = "<principal-name-error>"

    class StatsData:
        def __init__(self) -> None:
            self.playtime: float = 0
            self.score: int = 0
            self.lastPlayed: float = -1

    def __init__(self, index: int) -> None:
        Save.Active = self
        self.index = index
        self.Story = Save.StoryData()
        self.Stats = Save.StatsData()
        if os.path.isfile(Save.ToPath(self.index)):
            with open(Save.ToPath(self.index), "r") as f:
                data: Dict[str, Any] = json.loads(f.read())

            for dataKey in ("Story", "Stats"):
                for k, v in data[dataKey].items():
                    setattr(getattr(self, dataKey), k, v)
        else:
            self.save()

    def save(self, updateStats: bool = True):
        path = Save.ToPath(self.index)

        if updateStats:
            if KDS.Scores.GameTime.Timer != None:
                try:
                    self.Stats.playtime += KDS.Scores.GameTime.Timer.GetGameTime().total_seconds()
                except Exception as e:
                    try:
                        KDS.Scores.ScoreCounter.Stop()
                        self.Stats.playtime += KDS.Scores.GameTime.Timer.GetGameTime().total_seconds()
                    except Exception as e:
                        KDS.Logging.AutoError(e)
            self.Stats.score += KDS.Scores.score
            self.Stats.lastPlayed = datetime.now().timestamp()

        data = {"Story": self.Story.__dict__, "Stats": self.Stats.__dict__}
        with open(path, "w") as f:
            f.write(json.dumps(data, separators=(',', ':')))

    def delete(self):
        path = Save.ToPath(self.index)
        if os.path.isfile(path):
            os.remove(path)



#region Fuck off
#class Save:
#    PlayerFileCache = ""
#    SaveIndex = -1
#    """
#    Save File Structure:
#        ↳ save_0.kds (.zip)
#            ↳ tiles.kdf (json)
#            ↳ items.kdf (json)
#            ↳ enemies.kdf (json)
#            ↳ ballistic_objects.kdf (json)
#            ↳ player.kdf (json)
#            ↳ data.kdf (json)
#                ↳ Player
#                    ↳ position (tuple)
#                    ↳ health (float)
#                    ↳ stamina (float)
#                    ↳ keys: (dict)
#                    ↳ farting (bool)
#                ↳ Koponen
#                    ↳ position (tuple)
#                ↳ Game
#                    ↳ scroll (list)
#
#            ↳ missions.kbf ([undetermined]])
#            ↳ inventory.kbf ([undetermined]])
#    """
#    class DataType:
#        World = "world"
#        Player = "player"
#
#    @staticmethod
#    def quit():
#        if os.path.isdir(SaveCachePath):
#            if os.path.isfile(Save.PlayerFileCache):
#                _path = os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds")
#                shutil.make_archive(_path, 'zip', SaveCachePath)
#                shutil.move(f"{_path}.zip", _path)
#            shutil.rmtree(SaveCachePath)
#        #encodes and stores a save file to storage
#
#    @staticmethod
#    def init(_SaveIndex: int):
#        """decodes and loads a save file to cache.
#
#        Args:
#            _SaveIndex (int): Index of the savegame.
#
#        Returns:
#            bool: Is the save new or old.
#        """
#        Save.PlayerFileCache = os.path.join(SaveCachePath, "data.kdf")
#        Save.SaveIndex = _SaveIndex
#        if KDS.Gamemode.gamemode == KDS.Gamemode.Modes.Story and Save.SaveIndex >= 0:
#            if os.path.isfile(Save.PlayerFileCache):
#                Save.quit()
#            if os.path.isdir(SaveCachePath):
#                shutil.rmtree(SaveCachePath)
#            os.makedirs(SaveCachePath, exist_ok=True)
#            _path = os.path.join(SaveDirPath, f"save_{Save.SaveIndex}.kds")
#            if os.path.isfile(_path):
#                zipfile.ZipFile(_path, "r").extractall(SaveCachePath)
#                return False
#            return True
#        KDS.Logging.AutoError(f"Game settings are incorrect! Gamemode: {KDS.Gamemode.gamemode}, SaveIndex: {Save.SaveIndex}.")
#        return True
#        #decodes and loads a save file to cache
#
#    @staticmethod
#    def GetExistence(index: int):
#        return True if os.path.isfile(os.path.join(SaveDirPath, f"save_{index}.kds")) else False
#
#    @staticmethod
#    def SetData(path: str, item: Any):
#        JSON.Set(Save.PlayerFileCache, path, item)
#
#    @staticmethod
#    def GetData(path: str, default: Any):
#        return JSON.Get(Save.PlayerFileCache, path, default, True)
#
#    ignoreTypes = [
#        pygame.Surface,
#        pygame.mixer.Sound,
#        KDS.Animator.Animation,
#        KDS.Animator.MultiAnimation
#        #Inventory is automatically appended here by main
#    ]
#
#    @staticmethod
#    def SetClass(item: Any, filePathFromSaveCache: str, *identificationAttributes: str, identifier: str = None):
#        # Älä haasta meitä oikeuteen omena, pliis.
#        iVars: Dict[Any] = item.__dict__
#        ignoreKeys = []
#        for key, var in iVars.items():
#            testVar = var
#            if isinstance(var, list) or isinstance(var, tuple):
#                testVar = var[0] if len(var) > 0 else var
#            for ignore in Save.ignoreTypes:
#                if isinstance(testVar, ignore):
#                    ignoreKeys.append(key)
#                    break
#        sVars = {}
#        for key, var in iVars.items():
#            if key not in ignoreKeys:
#                if isinstance(var, pygame.Rect):
#                    sVars[key] = { "config_manager_pygame_rect": True, "data": (var.x, var.y, var.width, var.height) }
#                elif isinstance(var, tuple):
#                    sVars[key] = { "config_manager_tuple": True, "values": var }
#                else: sVars[key] = var
#            else: KDS.Logging.debug(f"Ignored variable [{key}, {var}] from {item}.")
#        itemIdentifier = identifier if identifier != None else ""
#        for i in range(len(identificationAttributes)):
#            if i > 0: itemIdentifier += "-"
#            itemIdentifier += str(getattr(item, identificationAttributes[i]))
#        JSON.Set(os.path.join(SaveCachePath, filePathFromSaveCache), itemIdentifier, sVars)
#
#    @staticmethod
#    def GetClass(Class, filePathFromSaveCache: str, identifier: str, classArgs: List[Any] = []):
#        attrs = JSON.Get(os.path.join(SaveCachePath, filePathFromSaveCache), identifier, None, True)
#        if attrs == None:
#            KDS.Logging.AutoError(f"Saved items of type {Class} with identifier {identifier} not found!")
#            return
#        instance = Class(*classArgs)
#        for k, v in attrs.items():
#            if isinstance(v, dict):
#                if "config_manager_pygame_rect" in v and v["config_manager_pygame_rect"] == True:
#                    rectData = v["data"]
#                    setattr(instance, k, pygame.Rect(rectData[0], rectData[1], rectData[2], rectData[3]))
#                elif "config_manager_tuple" in v and v["config_manager_tuple"] == True:
#                    setattr(instance, k, tuple(v["values"]))
#            else: setattr(instance, k, v)
#        return instance
#
#    @staticmethod
#    def SetTiles(tiles, specialTilesD, RespawnAnchorClass):
#        tiles = tiles.copy()
#        for row in tiles:
#            for tile in row:
#                if tile.serialNumber in specialTilesD:
#                    Save.SetClass(tile, os.path.join(SaveCachePath, "tiles.kdf"), "rect", "serialNumber")
#        JSON.Set(os.path.join(SaveCachePath, "tiles.kdf"), "Data/RespawnAnchor/active", f"{RespawnAnchorClass.active.rect.left}-{RespawnAnchorClass.active.rect.top}-{RespawnAnchorClass.active.serialNumber}" if RespawnAnchorClass.active != None else None)
#
#    @staticmethod
#    def GetTiles(tiles, RespawnAnchorClass):
#        savedSpecials = JSON.Get(os.path.join(SaveCachePath, "tiles.kdf"), JSON.NULLPATH, JSON.EMPTY)
#        for row in tiles:
#            for tile in row:
#                if f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}" in savedSpecials:
#                    vals: Dict[str, Any] = savedSpecials[f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}"]
#                    for k, v in vals.items():
#                        if isinstance(v, dict) and "config_manager_tuple" in v and v["config_manager_tuple"] == True:
#                            setattr(tile, k, tuple(v["values"]))
#                        else: setattr(tile, k, v)
#                if f"{tile.rect.left}-{tile.rect.top}-{tile.serialNumber}" == JSON.Get(os.path.join(SaveCachePath, "tiles.kdf"), "Data/RespawnAnchor/active", None):
#                    RespawnAnchorClass.active = tile
#
#    @staticmethod
#    def SetItems(items: Iterable[Any]):
#        itemsPath = os.path.join(SaveCachePath, "items.kdf")
#        if len(items) > 0:
#            for i, v in enumerate(items):
#                Save.SetClass(v, itemsPath, identifier=f"{v.serialNumber}-{i}")
#        else:
#            JSON.Set(itemsPath, JSON.NULLPATH, JSON.EMPTY)
#
#    @staticmethod
#    def GetItems(ItemClass):
#        #Taas, omena
#        iList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "items.kdf"), JSON.NULLPATH, None, True)
#        if iList == None:
#            KDS.Logging.AutoError("Save file for items not found!")
#            return []
#        instanceList = []
#        for key in iList:
#            srlNum = int(key.split("-")[0])
#            instanceList.append(Save.GetClass(ItemClass.serialNumbers[srlNum], "items.kdf", key, ((0, 0), srlNum)))
#        return instanceList
#
#    @staticmethod
#    def SetEnemies(enemies):
#        enemiesPath = os.path.join(SaveCachePath, "enemies.kdf")
#        if len(enemies) > 0:
#            for i, v in enumerate(enemies):
#                Save.SetClass(v, enemiesPath, identifier=f"{type(v)}-{i}")
#        else:
#            JSON.Set(enemiesPath, JSON.NULLPATH, JSON.EMPTY)
#
#    @staticmethod
#    def GetEnemies():
#        eList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "enemies.kdf"), JSON.NULLPATH, None, True)
#        if eList == None:
#            KDS.Logging.AutoError("Save file for enemies not found!")
#            return []
#        instanceList = []
#        for key in eList:
#            typeKey = key.split("-")[0][15:-2]
#            instanceList.append(Save.GetClass(getattr(KDS.AI, typeKey), "enemies.kdf", key, [(0, 0)]))
#        return instanceList
#
#    @staticmethod
#    def SetBallistic(ballistic_objects):
#        ballisticPath = os.path.join(SaveCachePath, "ballistic_objects.kdf")
#        if len(ballistic_objects) > 0:
#            for i, v in enumerate(ballistic_objects):
#                Save.SetClass(v, ballisticPath, identifier=f"{type(v)}-{i}")
#        else:
#            JSON.Set(ballisticPath, JSON.NULLPATH, JSON.EMPTY)
#
#    @staticmethod
#    def GetBallistic():
#        bList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "ballistic_objects.kdf"), JSON.NULLPATH, None, True)
#        if bList == None:
#            KDS.Logging.AutoError("Save file for ballistic objects not found!")
#            return []
#        instanceList = []
#        for key in bList:
#            typeKey = key.split("-")[0][15:-2]
#            instanceList.append(Save.GetClass(getattr(KDS.World, typeKey), "ballistic_objects.kdf", key, [pygame.Rect(0, 0, 0, 0), 0, 0, False, 0.0, 0, None]))
#        return instanceList
#
#    def SetMissions(missions: KDS.Missions.MissionHolder):
#        saveDict = {}
#        for mission in missions.GetMissionList():
#            missionDict = {}
#            for task in mission:
#                pass #Yeah fuck this
#
#
#    @staticmethod
#    def SetExplosions(explosions):
#        explosionsPath = os.path.join(SaveCachePath, "explosions.kdf")
#        if len(explosions) > 0:
#            for i, v in enumerate(explosions):
#                Save.SetClass(v, explosionsPath, identifier=f"{type(v)}-{i}")
#        else:
#            JSON.Set(explosionsPath, JSON.NULLPATH, JSON.EMPTY)
#
#    @staticmethod
#    def GetExplosions():
#        eList: Dict[str, Any] = JSON.Get(os.path.join(SaveCachePath, "explosions.kdf"), JSON.NULLPATH, None, True)
#        if eList == None:
#            KDS.Logging.AutoError("Save file for explosions not found!")
#            return []
#        instanceList = []
#        for key in eList:
#            typeKey = key.split("-")[0][15:-2]
#            instanceList.append(Save.GetClass(getattr(KDS.World, typeKey), "explosions.kdf", key, [KDS.Animator.Animation("explosion", 7, 5, KDS.Colors.White, KDS.Animator.OnAnimationEnd.Stop), (0, 0)]))
#        return instanceList
#endregion
