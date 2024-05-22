import os
from tkinter import filedialog
import KDS.ConfigManager
import KDS.Console

def generateLevelProp():
    """
    Generate a levelProp.kdf using this tool.
    """
    p_start_pos = KDS.Console.Start("Player Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="100, 100", autoFormat=True)
    k_enabled = KDS.Console.Start("Koponen Enabled: (bool)", False, KDS.Console.CheckTypes.Bool(), autoFormat=True)
    k_start_pos: tuple[int, int] = (0, 0)
    if k_enabled:
        k_start_pos = KDS.Console.Start("Koponen Start Position: (int, int)", False, KDS.Console.CheckTypes.Tuple(2, 0), defVal="200, 200", autoFormat=True)

    dark = KDS.Console.Start("Darkness Enabled: (bool)", False, KDS.Console.CheckTypes.Bool(), autoFormat=True)
    darkness: int = 0
    player_light: bool = False
    if dark:
        darkness = KDS.Console.Start("Darkness Strength: (int[0, 255])", False, KDS.Console.CheckTypes.Int(0, 255), autoFormat=True)
        player_light = KDS.Console.Start("Player Light: (bool)", False, KDS.Console.CheckTypes.Bool(), defVal="true", autoFormat=True)

    tb_start, tb_end = KDS.Console.Start("Time Bonus Range in seconds: (full points: int, no points: int)", False, KDS.Console.CheckTypes.Tuple(2, 0, requireIncrease=True), autoFormat=True)

    savePath = filedialog.asksaveasfilename(initialfile="levelprop", defaultextension=".kdf", filetypes=(("Koponen Data Format", "*.kdf"), ("All files", "*.*")), title="Save LevelProp")
    if len(savePath) > 0:
        if os.path.isfile(savePath):
            os.remove(savePath)
        #region User-defined
        KDS.ConfigManager.JSON.Set(savePath, "Data/TimeBonus/start", tb_start)
        KDS.ConfigManager.JSON.Set(savePath, "Data/TimeBonus/end", tb_end)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/enabled", k_enabled)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/startPos", k_start_pos)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Player/startPos", p_start_pos)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/enabled", dark)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/strength", darkness)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Darkness/playerLight", player_light)
        #endregion
        #region Defaults
        KDS.ConfigManager.JSON.Set(savePath, "Data/infiniteAmmo", False)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/forceTalk", False)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/startWithTalk", False)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/forceIdle", False)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/talk", False)
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/lscript", [])
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Koponen/listeners", [])
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Player/Inventory", {})
        KDS.ConfigManager.JSON.Set(savePath, "Entities/Player/spawnInverted", False)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/AmbientLight/enabled", False)
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/AmbientLight/tint", (0, 0, 0))
        KDS.ConfigManager.JSON.Set(savePath, "Rendering/Indicator/enabled", True) # Story-only
        #endregion
