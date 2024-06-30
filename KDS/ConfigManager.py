#region Importing
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import shutil
import re
from typing import Any, Dict, Final, Iterable, List, Optional, Self, Union
from uuid import UUID

import KDS.AI
import KDS.Animator
import KDS.Gamemode
import KDS.Logging
import KDS.Missions
import KDS.System
import KDS.World
import KDS.Scores
#endregion

AppDataPath: str
SaveDirPath: str
CampaignSaveDirPath: str
SettingsPath: str
def init(_AppDataPath: str, _SaveDirPath: str, _CampaignSaveDirPath: str):
    global AppDataPath, SaveDirPath, CampaignSaveDirPath, SettingsPath
    AppDataPath = _AppDataPath
    SaveDirPath = _SaveDirPath
    CampaignSaveDirPath = _CampaignSaveDirPath
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
    def Set(filePath: str, jsonPath: str, value: Any, sortKeys: bool = True, encoding: Optional[str] = None) ->  Union[Any, None]:
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
    def Get(filePath: str, jsonPath: str, defaultValue: Any, writeMissing: bool = True, warnMissing: bool = False, encoding: Optional[str] = None) -> Any:
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

@dataclass(frozen=True)
class CampaignRun:
    score: int
    deaths: int
    duration: timedelta

    @classmethod
    def from_scores(cls, scores: KDS.Scores.RunScores) -> Self:
        return cls(
            score=scores.total_score,
            deaths=scores.deathless_bonus.deathCount,
            duration=scores.time_bonus.gametime
        )

    @classmethod
    def to_json_obj(cls, run: Self) -> dict[str, Any]:
        return {
            "score": run.score,
            "deaths": run.deaths,
            "duration": run.duration.total_seconds()
        }

    @classmethod
    def from_json_obj(cls, json: dict[str, Any]) -> Self:
        score: int = json["score"]
        assert(isinstance(score, int))

        deaths: int = json["deaths"]
        assert(isinstance(deaths, int))

        duration_seconds: int | float = json["duration"]
        assert(isinstance(score, (int, float)))
        duration: timedelta = timedelta(seconds=duration_seconds)

        return cls(
            score=score,
            deaths=deaths,
            duration=duration
        )

# due to optimisation reasons, campaign save file is a partially valid json
# we fix the json when loading all of the data.
class CampaignSave:
    def __init__(self, *, _runs: Iterable[CampaignRun]) -> None:
        self._runs: tuple[CampaignRun, ...] = tuple(_runs)

    @property
    def can_be_scored(self) -> bool:
        return len(self._runs) > 0

    def get_max_score(self) -> int:
        return max(self._runs, key=lambda r: r.score).score

    def get_min_duration(self) -> timedelta:
        return min(self._runs, key=lambda r: r.duration).duration

    def get_total_deaths(self) -> int:
        return sum(r.deaths for r in self._runs)

    def get_run_count(self) -> int:
        return len(self._runs)

    @staticmethod
    def _get_path(uuid: UUID) -> str:
        return os.path.join(CampaignSaveDirPath, str(uuid) + ".kds")

    @classmethod
    def load(cls, uuid: UUID) -> Self:
        partial_json: str | None = None

        path: str = CampaignSave._get_path(uuid)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    partial_json = f.read()
            except IOError as e:
                KDS.Logging.AutoError(f"IOError when loading campaign save:\n{e}")

        complete_json: str
        if partial_json is not None:
            complete_json = '[' + partial_json.removesuffix(',') + ']'
        else:
            complete_json = "[]"

        json_obj: list[dict[str, Any]] = json.loads(complete_json)
        runs: list[CampaignRun] = [CampaignRun.from_json_obj(jobj) for jobj in json_obj]

        return cls(_runs=runs)

    @staticmethod
    def add_run(uuid: UUID, run: CampaignRun):
        run_json: str = json.dumps(
            CampaignRun.to_json_obj(run),
            separators=(',', ':')
        )

        with open(CampaignSave._get_path(uuid), "a+", encoding="utf-8") as f:
            f.write(run_json)
            f.write(',')
