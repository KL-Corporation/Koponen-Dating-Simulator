import os
from tkinter import filedialog
import uuid
import KDS.ConfigManager
import KDS.Console
import KDS.Convert

def generateCampaignProp():
    """
    Generate a campaignProp.kdf using this tool.
    """
    level_name = KDS.Console.Start("Level Name:", True, KDS.Console.CheckTypes.String(28))
    if not isinstance(level_name, str) or len(level_name) < 1:
        return

    scores_enabled_str = KDS.Console.Start("High Score Enabled: (bool)", True, KDS.Console.CheckTypes.Bool(), defVal="true")
    if not isinstance(scores_enabled_str, str) or len(scores_enabled_str) < 1:
        return
    scores_enabled: bool = KDS.Convert.ToBool2(scores_enabled_str)
    scores_guid: str = str(uuid.uuid4())

    savePath = filedialog.asksaveasfilename(initialfile="campaignprop", defaultextension=".kdf", filetypes=(("Koponen Data Format", "*.kdf"), ("All files", "*.*")), title="Save CampaignProp")
    if len(savePath) > 0:
        if os.path.isfile(savePath):
            os.remove(savePath)

        KDS.ConfigManager.JSON.Set(savePath, "Level/name", level_name)

        KDS.ConfigManager.JSON.Set(savePath, "Scores/enabled", scores_enabled)
        if scores_enabled:
            KDS.ConfigManager.JSON.Set(savePath, "Scores/guid", scores_guid)
