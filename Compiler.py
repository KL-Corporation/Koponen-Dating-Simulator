from enum import IntEnum
import shutil
from typing import NamedTuple
import PyInstaller.__main__ as pyinstaller
import os
import KDS.System
from datetime import datetime

AppDataPath = os.path.join(str(os.getenv('APPDATA')), "KL Corporation", "KDS Compiler")
BuildsPath = os.path.join(AppDataPath, "Builds")
os.makedirs(BuildsPath, exist_ok=True)
WorkPath = os.path.join(AppDataPath, "cache", "work")
CachePath = os.path.join(AppDataPath, "cache")
if os.path.isdir(CachePath): shutil.rmtree(CachePath)

parentDir = os.path.dirname(os.path.abspath(__file__))

BuildPath = os.path.join(BuildsPath, "build_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
EditorDirectoryPath = os.path.join(BuildPath, "KoponenDatingSimulator", "Assets", "Editor")

class ConsoleType(IntEnum):
    CONSOLE_YES = 0
    CONSOLE_NO = 1
    CONSOLE_HIDE = 2
    """Windows only"""

class BuildTask(NamedTuple):
    display_name: str
    """The display name of the build task."""

    filename: str
    """The filename of the main Python script located in the project's root."""

    icon_filename: str
    """A filename of an icon file located in Assets/Textures/Branding/"""

    keep_editor: bool = False
    """Whether to keep the Assets/Editor/ directory or not. Defaults to False."""

    console_type: ConsoleType = ConsoleType.CONSOLE_NO

build_tasks: list[BuildTask] = [
    BuildTask(
        display_name="Koponen Dating Simulator",
        filename="KoponenDatingSimulator.py",
        icon_filename="gameIcon.ico"
    ),
    BuildTask(
        display_name="Level Builder",
        filename="LevelBuilder.py",
        icon_filename="levelBuilderIcon.ico",
        keep_editor=True,
        console_type=ConsoleType.CONSOLE_HIDE
    ),
]

def printInfo(msg: str):
    print(KDS.System.Console.Colored(msg, "cyan"))
def printSuccess(msg: str):
    print(KDS.System.Console.Colored(msg, "green"))
def printWarning(msg: str):
    print(KDS.System.Console.Colored(msg, "yellow"))
def printError(msg: str):
    print(KDS.System.Console.Colored(msg, "red"))

def clearCache():
    if os.path.isdir(CachePath):
        printInfo("Clearing cache...")
        shutil.rmtree(CachePath)

for build in build_tasks:
    printInfo(f"Compiling {build.display_name}...")

    clearCache()

    console_type: tuple[str, ...]
    match build.console_type:
        case ConsoleType.CONSOLE_YES:
            console_type = ("--console",)
        case ConsoleType.CONSOLE_NO:
            console_type = ("--windowed",)
        case ConsoleType.CONSOLE_HIDE:
            console_type = ("--hide-console", "minimize-late")

    pyinstaller.run([
        "--noconfirm",

        "--onedir",
        "--contents-directory",
        ".",

        "--distpath",
        BuildPath,
        "--workpath",
        WorkPath,
        "--specpath",
        CachePath,

        *console_type,

        "--icon",
        f"{parentDir}/Assets/Textures/Branding/{build.icon_filename}",

        "--add-data",
        f"{parentDir}/Assets;Assets/",
        "--paths",
        f"{parentDir}/KDS",

        f"{parentDir}/{build.filename}"
    ])

    if not build.keep_editor:
        if os.path.isdir(EditorDirectoryPath):
            shutil.rmtree(EditorDirectoryPath)
            printInfo(f"Deleted Editor Textures directory at: \"{EditorDirectoryPath}\"")
        else:
            printWarning(f"Could not find Editor Textures directory at: \"{EditorDirectoryPath}\"")

clearCache()

for build in build_tasks:
    cutName = os.path.splitext(build.filename)[0]
    printSuccess(f"Built {build.display_name} at: \"" + os.path.join(BuildPath, cutName, f"{cutName}.exe") + "\"")
