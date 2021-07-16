# Code used to generate the new build data. DO NOT USE
"""
import json
import os
from typing import Dict, List, Union

path = input("Enter build.json file path: ")
if not path.endswith("build.json"):
    raise ValueError("Invalid path.")

with open(path, "r") as f:
    build = json.loads(f.read())

baseDir = os.path.dirname(os.path.abspath(__file__))

def Parse(filename: str, values: Dict[str, str], sounds: Dict[str, str] = None, **properties: List[int]):
    filename = os.path.join(baseDir, filename)
    output: Dict[str, Dict[str, Union[str, int, bool, None]]] = {}
    name = 0
    for k, v in values.items():
        output[f"noname_{name}"] = {}
        tmp = output[f"noname_{name}"]
        tmp["serialNumber"] = int(k)
        tmp["path"] = v

        for pk, pv in properties.items():
            tmp[pk] = bool(int(k) in pv)

        if sounds != None:
            tmp["sound"] = None
            if k in sounds:
                tmp["sound"] = sounds[k]

        name += 1

    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(output, indent=4))


Parse("tiles.kdf", build["tile_textures"], build["tile_sounds"], specialTile=build["special_tiles"], noCollision=build["noCollision"], trueScale=build["trueScale"])
Parse("teleports.kdf", build["teleport_textures"])
Parse("items.kdf", build["item_textures"], doubleSize=build["item_doubles"], supportsInventory=build["inventory_items"], isContraband=build["contraband"])
"""