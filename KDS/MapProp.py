from dataclasses import dataclass
import json
import os
from typing import Any, Self
from uuid import UUID

import KDS.ConfigManager
import KDS.Logging


class LevelProp:
    _cachedValues: dict[str, Any] = {}

    @staticmethod
    def init(MapPath: str):
        path: str = os.path.join(MapPath, "levelprop.kdf")
        KDS.Logging.debug(f"Loading new LevelProp: '{path}'...", consoleVisible=True)
        try:
            with open(path, "r") as f:
                LevelProp._cachedValues = json.loads(f.read())
            LevelProp._initialised_map_path = MapPath
        except IOError as e:
            KDS.Logging.AutoError(e)
        except json.decoder.JSONDecodeError as e:
            KDS.Logging.AutoError(e)

    @staticmethod
    def Get(path: str, DefaultValue: Any) -> Any:
        paths: list[str] = KDS.ConfigManager.JSON.ToKeyList(path)
        tmpvals = LevelProp._cachedValues
        for i in range(len(paths)):
            p = paths[i]
            if p not in tmpvals:
                return DefaultValue
            if i < len(paths) - 1: tmpvals = tmpvals[p]
            else: return tmpvals[p]

        KDS.Logging.AutoError("This code should not execute!")
        return DefaultValue

@dataclass(frozen=True)
class CampaignPropData:
    levelName: str

    countScores: bool
    scoresGuid: UUID | None

    @classmethod
    def load(cls, filepath: str) -> Self:
        name = KDS.ConfigManager.JSON.Get(filepath, "Level/name", None, writeMissing=False, warnMissing=True)
        if not isinstance(name, str):
            name = "<error>"

        scoresEnabled = KDS.ConfigManager.JSON.Get(filepath, "Scores/enabled", None, writeMissing=False, warnMissing=True)
        if not isinstance(scoresEnabled, bool):
            scoresEnabled = False

        scoresGuid: str | None = None
        if scoresEnabled:
            scoresGuid = KDS.ConfigManager.JSON.Get(filepath, "Scores/guid", None, writeMissing=False, warnMissing=True)
            if not isinstance(scoresGuid, str):
                KDS.Logging.warning("No valid scores GUID found in campaignprop.kdf. Disabling score counting...")
                scoresGuid = None
                scoresEnabled = False

        return cls(
            levelName=name,
            countScores=scoresEnabled,
            scoresGuid=UUID(scoresGuid) if scoresGuid is not None else None,
        )

    @classmethod
    def default(cls) -> Self:
        return cls(
            levelName="unnamed",
            countScores=False,
            scoresGuid=None
        )

    @classmethod
    def errored(cls) -> Self:
        return cls(
            levelName="<error>",
            countScores=False,
            scoresGuid=None
        )

class CampaignProp:
    data: CampaignPropData | None = None

    @staticmethod
    def init(MapPath: str):
        path: str = os.path.join(MapPath, "campaignprop.kdf")
        if os.path.isfile(path):
            KDS.Logging.debug(f"Loading new CampaignProp: '{path}'...", consoleVisible=True)
            CampaignProp.data = CampaignPropData.load(path)
        else:
            KDS.Logging.debug(f"No CampaignProp file found.", consoleVisible=True)
            CampaignProp.data = None
