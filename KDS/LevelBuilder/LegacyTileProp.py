import json
import os
from tkinter import filedialog
from typing import Any, Callable

import KDS.System
import KDS.Logging
from KDS.LevelBuilder.Shared import *

def upgradeTileProp(msgs: Callable[[str], None]):
    """tkinter required"""

    filename: str = filedialog.askopenfilename(filetypes=(("Tileprops file", "tileprops.kdf"), ("Koponen Data Format file", "*.kdf"), ("All files", "*.*")), title="Select Tileprops File")
    if len(filename) < 1:
        return
    try:
        with open(filename, "r") as f:
            data: dict[str, dict[str, Any]] = json.loads(f.read())
        newData: dict[str, dict[int, dict[str, Any]]] = {}

        for k, v in data.items():
            newData[k] = {}
            for k2, v2 in v.items():
                if k2 != "overlay":
                    if UnitType.Tile.value not in newData[k]: # Adding it if needed, because due to overlays being a different type, this might be empty.
                        newData[k][UnitType.Tile.value] = {}
                    newData[k][UnitType.Tile.value][k2] = v2
                else:
                    if UnitType.Unspecified.value not in newData[k]:
                        newData[k][UnitType.Unspecified.value] = {}
                    newData[k][UnitType.Unspecified.value][k2] = v2

        with open(os.path.join(os.path.dirname(filename), "properties.kdf"), "w", encoding="utf-8") as f:
            f.write(json.dumps(newData, separators=(',', ':'))) # Separators specified to remove useless spaces.

        if KDS.System.MessageBox.Show("Success!", "Tileprops was converted to properties succesfully. Do you want to delete the old tileprops file?", KDS.System.MessageBox.Buttons.YESNO, KDS.System.MessageBox.Icon.INFORMATION) == KDS.System.MessageBox.Responses.YES:
            os.remove(filename)
    except Exception as e:
        KDS.System.MessageBox.Show("Failure!", "Tileprops conversion failed.", KDS.System.MessageBox.Buttons.OK, KDS.System.MessageBox.Icon.ERROR)
        KDS.Logging.AutoError(e) # Number probably means a key error
