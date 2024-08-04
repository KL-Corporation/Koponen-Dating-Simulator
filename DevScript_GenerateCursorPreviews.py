import time
from typing import Final
import pygame
import KDS.System
if KDS.System.ISLINUX:
    raise Exception("Linux not supported.")

import KDS.Cursor

import win32gui
import win32ui
from PIL import Image

TEXTURE_SIZE: tuple[int, int] = (34, 34)
SCALE_SIZE: tuple[int, int] = (68, 68)

def get_cursor_texture(*, colorkey: tuple[int, int, int, int] = (0, 0, 0, 0)) -> Image.Image:
    # adapted from: https://stackoverflow.com/questions/72328718/python-take-screenshot-including-mouse-cursor/72471744#72471744

    hcursor = win32gui.GetCursorInfo()[1]
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 36, 36)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0,0), hcursor)

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    cursor = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1).convert("RGBA")

    win32gui.DestroyIcon(hcursor)
    win32gui.DeleteObject(hbmp.GetHandle())
    hdc.DeleteDC()


    pixdata = cursor.load()
    assert(pixdata is not None)

    width, height = cursor.size
    for y in range(height):
        for x in range(width):
            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = colorkey

    return cursor

def render_cursor_bitmap(size: tuple[int, int], hotspot: tuple[int, int], xormasks: tuple[int, ...], andmasks: tuple[int, ...]) -> pygame.Surface:
    # Inspiration taken from pygame.cursors.compile()

    surf: Final = pygame.Surface(size, flags=pygame.SRCALPHA)

    for i in range(size[0] * size[1]):
        y, x = divmod(i, size[0])
        byte, offset = divmod(i, 8)

        mask: int = 0b10000000 >> offset
        fill: bool = bool(andmasks[byte] & mask)
        invert: bool = bool(xormasks[byte] & mask)

        if fill:
            surf.set_at((x, y), (0, 0, 0) if invert else (255, 255, 255))

    return surf

def get_pygame_cursor(cursor: KDS.Cursor.PygameCursor) -> pygame.Surface:
    time.sleep(0.5)

    if cursor.cursor.type == "system":
        img: Image.Image = get_cursor_texture()
        assert(img.mode == "RGBA")
        return pygame.image.frombytes(img.tobytes(), img.size, "RGBA")
    elif cursor.cursor.type == "bitmap":
        return render_cursor_bitmap(*cursor.cursor.data) # type: ignore
    else:
        raise NotImplementedError()

def get_custom_cursor(cursor: KDS.Cursor.CustomCursor) -> pygame.Surface:
    return cursor.load_surface()

def generate_and_save_cursor(*, cursor: KDS.Cursor.Cursor, image_path: str, is_default: bool) -> None:
    cursor_surf: pygame.Surface
    if isinstance(cursor, KDS.Cursor.CustomCursor):
        print(f"Computing: '{cursor.texture_path}'...")
        pygame.mouse.set_cursor(cursor.load_and_create_cursor())
        cursor_surf = get_custom_cursor(cursor)
    else:
        print(f"Computing: '{cursor.debug_name}'...")
        pygame.mouse.set_cursor(cursor.cursor)
        cursor_surf = get_pygame_cursor(cursor)

    br: pygame.Rect = cursor_surf.get_bounding_rect()

    surf: Final = pygame.Surface(TEXTURE_SIZE, flags=pygame.SRCALPHA)
    surf.blit(cursor_surf, ((surf.width - br.width) // 2, (surf.height - br.height) // 2), br)

    pygame.image.save(pygame.transform.scale(surf, SCALE_SIZE), image_path)
    print(f"Saved to: '{image_path}'")

def main():
    screenInfo = pygame.display.Info()
    screen_center: tuple[int, int] = (screenInfo.current_w // 2, screenInfo.current_h // 2)

    DISPLAY_SIZE: Final[tuple[int, int]] = (256, 256)
    DISPLAY_CENTER: Final[tuple[int, int]] = (DISPLAY_SIZE[0] // 2, DISPLAY_SIZE[1] // 2)
    pygame.init()


    display: Final = pygame.display.set_mode(DISPLAY_SIZE)
    display.fill((0, 255, 255))
    pygame.display.flip()

    # get mouse focus
    pygame.event.set_grab(True)
    time.sleep(0.5)
    pygame.event.set_grab(False)
    time.sleep(0.5)

    for i, cursor in enumerate(KDS.Cursor.CURSORS):
        pygame.event.pump()
        pygame.display.set_window_position((screen_center[0] - DISPLAY_SIZE[0] // 2, screen_center[1] - DISPLAY_SIZE[1] // 2))
        pygame.mouse.set_pos(DISPLAY_CENTER)

        time.sleep(0.5)
        generate_and_save_cursor(cursor=cursor.default, image_path=cursor.preview_path, is_default=(i == 0))
        time.sleep(0.5)


if __name__ == "__main__":
    main()
