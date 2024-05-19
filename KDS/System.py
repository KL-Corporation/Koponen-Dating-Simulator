from __future__ import annotations

##### MOST FUNCTIONS DO NOT SUPPORT LINUX #####

import ctypes
import os
import shutil
import subprocess
import platform
import gc as gc
from typing import Final, Literal, Optional
import webbrowser

import KDS.Logging

from enum import IntEnum
from pygame.display import message_box as pygame_message_box

BASEDIR = str(os.path.dirname(os.path.abspath(__file__)))

ISLINUX = platform.system() == "Linux"

def hide(path: str):
    """Hides the file or directory specified by path.

    Args:
        path (str): The path to the file or directory to be hidden.
    """
    if ISLINUX:
        return

    subprocess.call(["attrib", "+H", path])

def unhide(path: str):
    """Unhides the file or directory specified by path.

    Args:
        path (str): The path to the file or directory to be unhidden.
    """
    if ISLINUX:
        return

    subprocess.call(["attrib", "-H", path])

def emptdir(dirpath: str):
    """Removes all children from the specified directory.

    Args:
        dirpath (str): The path to the directory to be emptied.
    """
    for item in os.listdir(dirpath):
        itemPath = os.path.join(dirpath, item)
        if os.path.isfile(itemPath):
            os.remove(itemPath)
        elif os.path.isdir(itemPath):
            shutil.rmtree(itemPath)
        else:
            KDS.Logging.AutoError(f"Cannot determine child type of path: \"{itemPath}\".")

def GetLineCount(path: str) -> int:
    with open(path, "r") as f:
        lines = f.read().splitlines()

    while len(lines) > 0 and len(lines[-1]) < 1:
        lines.pop(-1)

    return len(lines)

class MessageBox:
    class Buttons(IntEnum):
        ABORTRETRYIGNORE = 2
        CANCELTRYCONTINUE = 6
        # HELP = 16384
        OK = 0
        OKCANCEL = 1
        RETRYCANCEL = 5
        YESNO = 4
        YESNOCANCEL = 3

    class Icon(IntEnum):
        EXCLAMATION = 48
        WARNING = 48
        INFORMATION = 64
        ASTERISK = 64
        # QUESTION = 32
        STOP = 16
        ERROR = 16
        HAND = 16

    class DefaultButton(IntEnum):
        BUTTON1 = 0
        BUTTON2 = 256
        BUTTON3 = 512
        BUTTON4 = 768

    class Responses(IntEnum):
        ABORT = 3
        CANCEL = 2
        CONTINUE = 11
        IGNORE = 5
        NO = 7
        OK = 1
        RETRY = 4
        TRYAGAIN = 10
        YES = 6

    @staticmethod
    def Show(title: str, text: str, buttons: MessageBox.Buttons, icon: MessageBox.Icon, defaultButton: MessageBox.DefaultButton = DefaultButton.BUTTON1) -> MessageBox.Responses:
        if ISLINUX:
            return MessageBox._pygameMessageboxFallback(title=title, text=text, buttons=buttons, icon=icon, defaultButton=defaultButton)

        argVal = buttons.value
        argVal += icon.value
        argVal += defaultButton.value
        # argVal += sum(args)
        response = ctypes.windll.user32.MessageBoxW(0, text, title, argVal)
        return MessageBox.Responses(response)

    @staticmethod
    def _pygameMessageboxFallback(title: str, text: str, buttons: MessageBox.Buttons, icon: MessageBox.Icon, defaultButton: MessageBox.DefaultButton) -> MessageBox.Responses:
        """Slow, janky and shit."""
        BUTTONS: Final[dict[MessageBox.Buttons, tuple[str, ...]]] = {
            MessageBox.Buttons.ABORTRETRYIGNORE: ("Abort", "Retry", "Ignore"),
            MessageBox.Buttons.CANCELTRYCONTINUE: ("Cancel", "Try Again", "Continue"),
            # MessageBox.Buttons.HELP: ("Help",), # non-standard, should be a dedicated help button
            MessageBox.Buttons.OK: ("OK",),
            MessageBox.Buttons.OKCANCEL: ("OK", "Cancel"),
            MessageBox.Buttons.RETRYCANCEL: ("Retry", "Cancel"),
            MessageBox.Buttons.YESNO: ("Yes", "No"),
            MessageBox.Buttons.YESNOCANCEL: ("Yes", "No", "Cancel")
        }

        ICONS: Final[dict[MessageBox.Icon, Literal["info", "warn", "error"]]] = {
            MessageBox.Icon.STOP: "error",
            MessageBox.Icon.ERROR: "error",
            MessageBox.Icon.HAND: "error",
            MessageBox.Icon.EXCLAMATION: "warn",
            MessageBox.Icon.WARNING: "warn",
            MessageBox.Icon.INFORMATION: "info",
            MessageBox.Icon.ASTERISK: "info",
            # MessageBox.Icon.QUESTION: "info" # non-standard, should be a question mark
        }

        DEFAULT_BUTTONS: Final[dict[MessageBox.DefaultButton, int]] = {
            MessageBox.DefaultButton.BUTTON1: 0,
            MessageBox.DefaultButton.BUTTON2: 1,
            MessageBox.DefaultButton.BUTTON3: 2,
            MessageBox.DefaultButton.BUTTON4: 3
        }

        RESPONSES: Final[dict[str, MessageBox.Responses]] = {
            "Abort": MessageBox.Responses.ABORT,
            "Retry": MessageBox.Responses.RETRY,
            "Ignore": MessageBox.Responses.IGNORE,
            "Cancel": MessageBox.Responses.CANCEL,
            "Try Again": MessageBox.Responses.TRYAGAIN,
            "Continue": MessageBox.Responses.CONTINUE,
            "OK": MessageBox.Responses.OK,
            "Cancel": MessageBox.Responses.CANCEL,
            "Retry": MessageBox.Responses.RETRY,
            "Yes": MessageBox.Responses.YES,
            "No": MessageBox.Responses.NO
        }

        btns: tuple[str, ...] = BUTTONS[buttons]
        button_index: int = pygame_message_box(
            title=title,
            message=text,
            message_type=ICONS[icon],
            buttons=btns,
            return_button=DEFAULT_BUTTONS[defaultButton],
        )

        return RESPONSES[btns[button_index]]

class Console:
    ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
    del ATTRIBUTES['']
    HIGHLIGHTS = dict(
            list(zip([
                'on_grey',
                'on_red',
                'on_green',
                'on_yellow',
                'on_blue',
                'on_magenta',
                'on_cyan',
                'on_white'
                ],
                list(range(40, 48))
                ))
            )
    COLORS = dict(
            list(zip([
                'grey',
                'red',
                'green',
                'yellow',
                'blue',
                'magenta',
                'cyan',
                'white',
                ],
                list(range(30, 38))
                ))
            )
    RESET = '\033[0m'

    @staticmethod
    def Colored(text, color=None, on_color=None, attrs=None):
        """Colorize text.

        Available text colors:
            red, green, yellow, blue, magenta, cyan, white.

        Available text highlights:
            on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

        Available attributes:
            bold, dark, underline, blink, reverse, concealed.

        Example:
            colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
            colored('Hello, World!', 'green')
        """
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (Console.COLORS[color], text)

            if on_color is not None:
                text = fmt_str % (Console.HIGHLIGHTS[on_color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (Console.ATTRIBUTES[attr], text)

            text += Console.RESET
        return text

class EXTENDED_NAME_FORMAT(IntEnum):
    NameUnknown = 0
    NameFullyQualifiedDN = 1
    NameSamCompatible = 2
    NameDisplay = 3
    NameUniqueId = 6
    NameCanonical = 7
    NameUserPrincipal = 8
    NameCanonicalEx = 9
    NameServicePrincipal = 10
    NameDnsDomain = 12

def GetUserNameEx(NameDisplay: EXTENDED_NAME_FORMAT) -> Optional[str]:
    if ISLINUX:
        lgin = os.getlogin()
        return lgin if len(lgin) > 0 else None

    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay.value, None, size)

    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay.value, nameBuffer, size)
    return nameBuffer.value

def OpenURL(url: str):
    webbrowser.open_new_tab(url)
