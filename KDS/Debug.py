from typing import Any
import pygame
from pygame.constants import SRCALPHA
import KDS.Clock
import KDS.Colors
import KDS.Cursor
import KDS.Logging

Enabled: bool = False

# def IsVSCodeDebugging() -> bool:
#     """
#     Works with other IDE's, but KL Corporation's Management strongly recommends to use Visual Studio Code whenever you touch any of Koponen Dating Simulator's code.
#     """
#     return bool(sys.gettrace() != None)

pygame.init()
font = pygame.font.Font("Assets/Fonts/harbinger.otf", 25)
padding: dict[str, int] = {"left": 10, "right": 10, "top": 10, "bottom": 10}
background_color = KDS.Colors.DarkGray
background_alpha = 128
text_color = KDS.Colors.White

def RenderData(data: dict[str, Any] | None, fontOverride: pygame.font.Font | None = None) -> pygame.Surface:
    f = font if fontOverride == None else fontOverride

    cursor_interactions: tuple[str, ...] = KDS.Cursor.get_currently_interacting_names()

    rnd_data: dict[str, Any] = {
        "FPS": KDS.Clock.GetFPS(3)
    }
    if KDS.Logging.profiler_running:
        rnd_data["Profiler"] = "enabled"
    if len(cursor_interactions) > 0:
        rnd_data["Cursor Interactions"] = ", ".join(cursor_interactions)
    if data is not None:
        rnd_data.update(data)

    rList: list[pygame.Surface] = []
    for key, value in rnd_data.items():
        rList.append(f.render(f"{key}: {value}", True, text_color))

    w = max(rList, key=lambda r: r.get_width()).get_width()
    fh = f.get_height()
    h = len(rList) * fh
    surf = pygame.Surface((w + padding["left"] + padding["right"], h + padding["top"] + padding["bottom"]), flags=SRCALPHA)
    surf.fill((*background_color, background_alpha))

    for i, r in enumerate(rList):
        surf.blit(r, (padding["left"], padding["top"] + i * fh))

    return surf
