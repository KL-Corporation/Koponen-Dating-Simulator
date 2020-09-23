from inspect import currentframe
from subprocess import call
import os
import shutil
import KDS.Logging

def hide(path: str):
    """Hides the file or directory specified by path. [WINDOWS ONLY]

    Args:
        path (str): The path to the file or directory to be hidden.
    """
    call(["attrib", "+H", path])
    
def unhide(path: str):
    """Unhides the file or directory specified by path. [WINDOWS ONLY]

    Args:
        path (str): The path to the file or directory to be unhidden.
    """
    call(["attrib", "-H", path])
    
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