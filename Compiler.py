import shutil
import PyInstaller.__main__
import os
import inquirer
import inquirer.themes
import termcolor
from datetime import datetime

AppDataPath = os.path.join(os.getenv('APPDATA'), "KL Corporation", "KDS Compiler")
BuildsPath = os.path.join(AppDataPath, "Builds")
os.makedirs(BuildsPath, exist_ok=True)
WorkPath = os.path.join(AppDataPath, "cache", "work")
SpecPath = os.path.join(AppDataPath, "cache")

questions = [
    inquirer.Checkbox("toBuild", "Which KDS Modules you want to build?", ("Koponen Dating Simulator", "Level Builder"), "Koponen Dating Simulator")
]

answers = inquirer.prompt(questions)

parentDir = os.path.dirname(os.path.abspath(__file__))

BuildPath = os.path.join(BuildsPath, "build_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
EditorTexturesPath = os.path.join(BuildPath, "KoponenDatingSimulator", "Assets", "Textures", "Editor")
BuiltNames = []
for buildType in answers["toBuild"]:
    if buildType == "Koponen Dating Simulator":
        fileName = "KoponenDatingSimulator.py"
        iconName = "gameIcon.ico"
    else:
        fileName = "LevelBuilder.py"
        iconName = "levelBuilderIcon.ico"
        
    PyInstaller.__main__.run([
        "--noconfirm",
        "--distpath",
        BuildPath,
        "--workpath",
        WorkPath,
        "--specpath",
        SpecPath,
        "--windowed",
        "--icon",
        f"{parentDir}/Assets/Textures/Branding/{iconName}",
        "--add-data",
        f"{parentDir}/Assets;Assets/",
        "--paths",
        f"{parentDir}/KDS",
        f"{parentDir}/{fileName}"
    ])
    if os.path.isdir(EditorTexturesPath):
        shutil.rmtree(EditorTexturesPath)
        print(f"Deleted Editor Textures directory at {EditorTexturesPath}")
    BuiltNames.append((buildType, os.path.splitext(fileName)[0]))

if len(answers["toBuild"]) < 1:
    print(termcolor.colored("Nothing was built.", "red"))
else:
    for name in BuiltNames:
        print(termcolor.colored(f"Built {name[0]} at " + os.path.join(BuildPath, name[1], name[1] + ".exe"), "green"))

if os.path.isdir(os.path.join(AppDataPath, "cache")): shutil.rmtree(os.path.join(AppDataPath, "cache"))