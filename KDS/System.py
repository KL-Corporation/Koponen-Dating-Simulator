from inspect import currentframe
import subprocess
import os
import shutil
import KDS.Logging
import ctypes

print(os.getpid())

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
            KDS.Logging.AutoError("Cannot determine child type.", currentframe())
            
class MessageBox:
    class Styles:
        Ok = 0
        Ok_Cancel = 1
        Abort_Retry_Ignore = 2
        Yes_No_Cancel = 3
        Yes_No = 4
        Retry_No = 5
        Cancel_TryAgain_Continue = 6
    
    @staticmethod
    def Show(title: str, text: str, style: Styles or int):
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)