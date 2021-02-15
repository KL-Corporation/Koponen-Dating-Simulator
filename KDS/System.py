import ctypes
import os
import shutil
import subprocess

import KDS.Logging

def hide(path: str):
    """Hides the file or directory specified by path. [WINDOWS ONLY]

    Args:
        path (str): The path to the file or directory to be hidden.
    """
    subprocess.call(["attrib", "+H", path])
    
def unhide(path: str):
    """Unhides the file or directory specified by path. [WINDOWS ONLY]

    Args:
        path (str): The path to the file or directory to be unhidden.
    """
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
            KDS.Logging.AutoError("Cannot determine child type.")
            
class MessageBox:
    class Buttons:
        ABORTRETRYIGNORE = 2
        CANCELTRYCONTINUE = 6
        HELP = 16384
        OK = 0
        OKCANCEL = 1
        RETRYCANCEL = 5
        YESNO = 4
        YESNOCANCEL = 3
        
    class Icon:
        EXCLAMATION = 48
        WARNING = 48
        INFORMATION = 64
        ASTERISK = 64
        QUESTION = 32
        STOP = 16
        ERROR = 16
        HAND = 16
        
    class DefaultButton:
        BUTTON1 = 0
        BUTTON2 = 256
        BUTTON3 = 512
        BUTTON4 = 768
        
    class Responses:
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
    def Show(title: str, text: str, buttons: int = None, icon: int = None, *args: int):
        argVal = buttons if buttons != None else 0
        argVal += icon if icon != None else 0
        for arg in args: argVal += arg
        return ctypes.windll.user32.MessageBoxW(0, text, title, argVal)

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
