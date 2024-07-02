import json
import os
from typing import Any, NamedTuple

import pygame

import KDS.Colors

class BuildData(NamedTuple):
    data: dict[str, dict[str, Any]]
    textures: dict[int, pygame.Surface]

def load_tiles() -> BuildData:
    return _load("Assets/Data/Build/tiles.kdf", "Assets/Textures/Tiles")

def load_teleports() -> BuildData:
    return _load("Assets/Data/Build/teleports.kdf", "Assets/Textures/Teleports")

def load_items() -> BuildData:
    return _load("Assets/Data/Build/items.kdf", "Assets/Textures/Items")

def _load(data_filepath: str, texture_dirpath: str) -> BuildData:
    data: dict[str, dict[str, Any]]
    with open(data_filepath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    textures: dict[int, pygame.Surface] = {}
    for d in data.values():
        d_srl: int = d["serialNumber"]
        assert(isinstance(d_srl, int))

        texture_name: str = d["path"]
        assert(isinstance(texture_name, str))
        loaded_tex: pygame.Surface = pygame.image.load(os.path.join(texture_dirpath, texture_name))

        perPixelAlpha: bool = d.get("texturePerPixelAlpha", False)
        assert(isinstance(perPixelAlpha, bool))
        texture: pygame.Surface
        if perPixelAlpha:
            texture = loaded_tex.convert_alpha()
        else:
            texture = loaded_tex.convert()

        overrideAlpha: int | None = d.get("textureOverrideAlpha")
        if overrideAlpha is not None:
            assert(isinstance(overrideAlpha, int))
            texture.set_alpha(overrideAlpha)

        if "textureOverrideColorkey" in d:
            overrideColorkey: str | None = d["textureOverrideColorkey"]
            if overrideColorkey is not None:
                assert(isinstance(overrideColorkey, str))
                texture.set_colorkey(pygame.Color(overrideColorkey))
            else:
                # overrideColorkey is None, we don't set a colorkey.
                pass
        else:
            texture.set_colorkey(KDS.Colors.White)

        textures[d_srl] = texture

    return BuildData(data, textures)
