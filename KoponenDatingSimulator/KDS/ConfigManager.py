#region Importing
import KDS.Logging
import configparser
import os
from inspect import currentframe, getframeinfo
#endregion

AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
saveDirPath = os.path.join(AppDataPath, "saves")
if not os.path.exists(saveDirPath):
    os.mkdir(saveDirPath)
elif not os.path.isdir(saveDirPath):
    os.mkdir(saveDirPath)

def LoadSave(SaveIndex: int, SaveDirectory: str, SaveName: str, DefaultValue: str):
    global AppDataPath, saveDirPath
    """
    1. SaveIndex, The index of the currently played save.
    2. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    3. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    4. DefaultValue, The value that is going to be loaded if no value was found.
    """
    return LoadFunction(os.path.join(saveDirPath, "save_" + str(SaveIndex) + ".kds"), SaveDirectory, SaveName, DefaultValue)
def LoadSetting(SaveDirectory: str, SaveName: str, DefaultValue: str):
    """
    1. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    2. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    3. DefaultValue, The value that is going to be loaded if no value was found.
    """
    return LoadFunction(os.path.join(AppDataPath, "settings.cfg"), SaveDirectory, SaveName, DefaultValue)

def LoadFunction(FilePath: str, SaveDirectory: str, SaveName: str, DefaultValue: str):
    """The function LoadSave and LoadSetting uses for loading data.

    Args:
        FilePath (str): The path to the file where the value will be loaded.
        SaveDirectory (str): The directory inside the file where the value will be loaded.
        SaveName (str): The name that will be used to load the corresponding value.
        DefaultValue (str): What will be returned if no value was found.

    Returns:
        str: The loaded value.
    """
    config = configparser.ConfigParser()
    config.read(FilePath)
    if config.has_section(SaveDirectory):
        if config.has_option(SaveDirectory, SaveName):
            return config.get(SaveDirectory, SaveName)
        else:
            config.set(SaveDirectory, SaveName, DefaultValue)
            return DefaultValue
    else:
        config.add_section(SaveDirectory)
        if config.has_option(SaveDirectory, SaveName):
            return config.get(SaveDirectory, SaveName)
        else:
            config.set(SaveDirectory, SaveName, DefaultValue)
            return DefaultValue
    with open(FilePath, "w") as cfgFile:
        config.write(cfgFile)

def SetSetting(SaveDirectory: str, SaveName: str, SaveValue: str):
    """
    Automatically fills FilePath to SaveFunction
    1. SaveDirectory, The name of the class (directory) your data will be saved. Please prefer using already established directories.
    2. SaveName, The name of the setting you are saving. Make sure this does not conflict with any other SaveName!
    3. SaveValue, The value that is going to be saved.
    """
    SaveFunction(os.path.join(AppDataPath, "settings.cfg"), SaveDirectory, SaveName, SaveValue)

def SetSave(SaveIndex: int, SaveDirectory: str, SaveName: str, SaveValue: str):
    """
    Automatically fills FilePath to SaveFunction
    1. SaveIndex, The index of the currently played save.
    2. SaveDirectory, The name of the class (directory) your data will be loaded. Please prefer using already established directories.
    3. SaveName, The name of the setting you are loading. Make sure this does not conflict with any other SaveName!
    4. SaveValue, The value that is going to be saved.
    """
    SaveFunction(os.path.join(saveDirPath, "save_" + str(SaveIndex) + ".kds"), SaveDirectory, SaveName, SaveValue)

def SaveFunction(FilePath: str, SaveDirectory: str, SaveName: str, SaveValue: str):
    """The function SetSave and SetSetting uses for saving data.

    Args:
        FilePath (str): The path to the file where the value will be saved.
        SaveDirectory (str): The directory inside the file where the value will be saved.
        SaveName (str): The name that will be used to save the corresponding value.
        SaveValue (str): What will be saved to the path.
    """
    config = configparser.ConfigParser()
    config.read(FilePath)
    if config.has_section(SaveDirectory):
        config.set(SaveDirectory, SaveName, SaveValue)
    else:
        config.add_section(SaveDirectory)
        config.set(SaveDirectory, SaveName, SaveValue)
    with open(FilePath, "w") as cfg_file:
        config.write(cfg_file)