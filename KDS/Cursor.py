from dataclasses import dataclass
from typing import Final, NamedTuple, Self, TypeAlias
import pygame

import KDS.ConfigManager
import KDS.Convert
import KDS.Logging
import KDS.Math

class CustomCursor(NamedTuple):
    hotspot: tuple[int, int]
    texture_path: str
    colorkey: tuple[int, int, int] | None = None

    def load_surface(self) -> pygame.Surface:
        cursor_tex: pygame.Surface = pygame.image.load(self.texture_path)
        if self.colorkey is not None:
            cursor_tex.set_colorkey(self.colorkey)
        return cursor_tex

    def load_and_create_cursor(self) -> pygame.Cursor:
        return pygame.Cursor(self.hotspot, self.load_surface())

class PygameCursor(NamedTuple):
    cursor: pygame.Cursor
    debug_name: str

    @classmethod
    def system(cls, system_cursor_id: int, *, debug_name: str) -> Self:
        return cls(pygame.Cursor(system_cursor_id), debug_name=debug_name)

Cursor: TypeAlias = CustomCursor | PygameCursor

@dataclass(frozen=True, eq=False, kw_only=True)
class CursorData:
    default: Cursor
    select: Cursor | None = None
    text: Cursor | None = None

    preview_path: str

class LoadedCursor(NamedTuple):
    default: pygame.Cursor
    select: pygame.Cursor
    text: pygame.Cursor

    preview: pygame.Surface

CURSORS: Final[tuple[CursorData, ...]] = (
    CursorData(
        default=PygameCursor.system(pygame.SYSTEM_CURSOR_ARROW, debug_name="SYSTEM_ARROW"),
        select=PygameCursor.system(pygame.SYSTEM_CURSOR_HAND, debug_name="SYSTEM_HAND"),
        text=PygameCursor.system(pygame.SYSTEM_CURSOR_IBEAM, debug_name="SYSTEM_IBEAM"),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor0.png"
    ),
    CursorData(
        default=CustomCursor(
            hotspot=(1, 1),
            texture_path="Assets/Textures/UI/Cursors/cursor1.png",
            colorkey=(255, 255, 255)
        ),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor1.png"
    ),
    CursorData(
        default=CustomCursor(
            hotspot=(8, 4),
            texture_path="Assets/Textures/UI/Cursors/cursor2.png"
        ),
        select=CustomCursor(
            hotspot=(8, 4),
            texture_path="Assets/Textures/UI/Cursors/cursor2_select.png"
        ),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor2.png"
    ),
    CursorData(
        default=CustomCursor(
            hotspot=(1, 1),
            texture_path="Assets/Textures/UI/Cursors/cursor3.png",
            colorkey=(255, 0, 0)
        ),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor3.png"
    ),
    CursorData(
        default=PygameCursor(pygame.cursors.arrow, debug_name="PYGAME_ARROW"),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor4.png"
    ),
    CursorData(
        default=PygameCursor(pygame.cursors.tri_left, debug_name="PYGAME_TRI_LEFT"),
        preview_path="Assets/Textures/UI/Cursors/Preview/cursor5.png"
    )
)

_current_cursor: tuple[CursorData, LoadedCursor]
def init(*, cursor_index_override: int | None = None):
    _switch_cursor(index_override=cursor_index_override, offset=0)

def get_preview() -> pygame.Surface:
    _, loaded = _current_cursor
    return loaded.preview

def _internal_load_cursor(cursor: Cursor) -> pygame.Cursor:
    if isinstance(cursor, CustomCursor):
        return cursor.load_and_create_cursor()
    return cursor.cursor

def _load_cursor(cursor: CursorData) -> None:
    global _current_cursor

    default: pygame.Cursor = _internal_load_cursor(cursor.default)
    select: pygame.Cursor = _internal_load_cursor(cursor.select) if cursor.select is not None else default
    text: pygame.Cursor = _internal_load_cursor(cursor.text) if cursor.text is not None else select

    preview: pygame.Surface = pygame.image.load(cursor.preview_path).convert_alpha()

    loaded: LoadedCursor = LoadedCursor(default=default, select=select, text=text, preview=preview)

    _current_cursor = (cursor, loaded)

def _update_cursor() -> bool:
    """Returns `True` if a special cursor was used."""

    loaded: LoadedCursor = _current_cursor[1]
    special_cursor: pygame.Cursor | None = None
    if len(_interacts) > 0:
        special_cursor = loaded.select
    if _textedit:
        special_cursor = loaded.text

    pygame.mouse.set_cursor(special_cursor if special_cursor else loaded.default)
    return special_cursor is not None

_textedit: bool = False
def set_textedit(enabled: bool):
    global _textedit
    if _textedit != enabled:
        _textedit = enabled
        _update_cursor()

_interacts: set[object] = set()
def reset_interactables() -> None:
    if len(_interacts) > 0:
        _interacts.clear()
        _update_cursor()

def add_interactable_reference(element: object) -> bool:
    """
    Returns `True` if the element was added.
    If the element exists already, returns `False`.
    """

    if element not in _interacts:
        _interacts.add(element)
        _update_cursor() # could be optimized by checking if count changes from/to 0, but I'm too lazy to implement that
        return True
    else:
        return False

def remove_interactable_reference(element: object):
    """
    Returns `True` if the element was removed.
    If the element doesn't exist, returns `False`.
    """

    output: bool
    if element in _interacts:
        _interacts.remove(element)
        _update_cursor()
        return True
    else:
        return False

def next_cursor():
    _switch_cursor(offset=1)

def previous_cursor():
    _switch_cursor(offset=-1)

def _switch_cursor(*, index_override: int | None = None, offset: int):
    """
    Offset defines how many positions to offset from the current cursor.
    If index is overridden, load the cursor at index ignoring setting loading/saving completely (used by LevelBuilder).
    """

    index: int
    if index_override is None:
        index = KDS.ConfigManager.GetSetting("UI/cursor", ...)
        assert(isinstance(index, int))

        if offset != 0:
            index = KDS.Math.Clamp(index + offset, 0, len(CURSORS) - 1)
            KDS.ConfigManager.SetSetting("UI/cursor", index)
    else:
        index = KDS.Math.Clamp(index_override, 0, len(CURSORS) - 1)

    _load_cursor(CURSORS[index])
    _update_cursor()
