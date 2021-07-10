from __future__ import annotations

##### MOST FUNCTIONS DO NOT SUPPORT LINUX #####

import ctypes
import os
import shutil
import subprocess
import platform
import sys
from typing import Dict, Optional
import webbrowser

import KDS.Logging

from enum import IntEnum

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
        HELP = 16384
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
        QUESTION = 32
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
    def Show(title: str, text: str, buttons: MessageBox.Buttons = None, icon: MessageBox.Icon = None, defaultButton: MessageBox.DefaultButton = None, *args: int) -> MessageBox.Responses:
        if ISLINUX:
            MessageBox._sendLinuxNotification(title, text, icon)
            return MessageBox.Responses.OK # notify doesn't have buttons so we will return this same response... Shut up, I know this is stupid.

        argVal = buttons.value if buttons != None else 0
        argVal += icon.value if icon != None else 0
        argVal += defaultButton.value if defaultButton != None else 0
        argVal += sum(args)
        response = ctypes.windll.user32.MessageBoxW(0, text, title, argVal)
        return MessageBox.Responses(response)

    @staticmethod
    def _sendLinuxNotification(title: str, text: str, icon: MessageBox.Icon = None):
        icons: Dict[Optional[MessageBox.Icon], Optional[str]] = {
            MessageBox.Icon.EXCLAMATION: "error",
            MessageBox.Icon.WARNING: "dialog-warning",
            MessageBox.Icon.INFORMATION: "info",
            MessageBox.Icon.ASTERISK: "info",
            MessageBox.Icon.QUESTION: "help",
            MessageBox.Icon.STOP: "stop",
            MessageBox.Icon.ERROR: "stop",
            MessageBox.Icon.HAND: "stop",
            None: None
        }
        cmd = ["/usr/bin/notify-send"]

        tmpicon = icons[icon]
        if tmpicon != None:
            cmd.append(f"--icon={tmpicon}")

        cmd.append(title)
        cmd.append(text)
        subprocess.run(cmd)

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
    NameUnknown = 0,
    NameFullyQualifiedDN = 1,
    NameSamCompatible = 2,
    NameDisplay = 3,
    NameUniqueId = 6,
    NameCanonical = 7,
    NameUserPrincipal = 8,
    NameCanonicalEx = 9,
    NameServicePrincipal = 10,
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