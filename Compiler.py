import shutil
import PyInstaller.__main__
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
EditorTexturesPath = os.path.join(BuildPath, "KoponenDatingSimulator", "Assets", "Textures", "Editor")
toBuild = {
    "Koponen Dating Simulator": {
        "filename": "KoponenDatingSimulator.py",
        "iconname": "gameIcon.ico",
        "keepEditor": False
    },
    "Level Builder": {
        "filename": "LevelBuilder.py",
        "iconname": "levelBuilderIcon.ico",
        "keepEditor": True
    }
}

for buildType in toBuild.items():
    filename = buildType[1]["filename"]
    iconname = buildType[1]["iconname"]
    
    PyInstaller.__main__.run([
        "--noconfirm",
        "--distpath",
        BuildPath,
        "--workpath",
        WorkPath,
        "--specpath",
        CachePath,
        "--windowed",
        "--icon",
        f"{parentDir}/Assets/Textures/Branding/{iconname}",
        "--add-data",
        f"{parentDir}/Assets;Assets/",
        "--paths",
        f"{parentDir}/KDS",
        f"{parentDir}/{filename}"
    ])
    if not buildType[1]["keepEditor"] and os.path.isdir(EditorTexturesPath):
        shutil.rmtree(EditorTexturesPath)
        print(f"Deleted Editor Textures directory at {EditorTexturesPath}")

if os.path.isdir(os.path.join(AppDataPath, "cache")):
    print("Clearing cache...")
    shutil.rmtree(os.path.join(AppDataPath, "cache"))

for buildType in toBuild.items():
    cutName = os.path.splitext(buildType[1]["filename"])[0]
    print(KDS.System.Console.Colored(f"Built {buildType[0]} at " + os.path.join(BuildPath, cutName, cutName + ".exe"), "green"))
