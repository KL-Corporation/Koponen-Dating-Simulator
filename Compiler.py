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

BuildPath = os.path.join(BuildsPath, "build_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
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
        f"F:/PyGame/Koponen-Dating-Simulator/Assets/Textures/Branding/{iconName}",
        "--add-data",
        "F:/PyGame/Koponen-Dating-Simulator/Assets;Assets/",
        "--paths",
        "F:/PyGame/Koponen-Dating-Simulator/KDS",
        f"{os.path.dirname(os.path.abspath(__file__))}/{fileName}"
    ])
    BuiltNames.append((buildType, os.path.splitext(fileName)[0]))

if len(answers["toBuild"]) < 1:
    print(termcolor.colored("Nothing was built.", "red"))
else:
    for name in BuiltNames:
        print(termcolor.colored(f"Built {name[0]} at " + os.path.join(BuildPath, name[1], name[1] + ".exe"), "green"))

if os.path.isdir(os.path.join(AppDataPath, "cache")): shutil.rmtree(os.path.join(AppDataPath, "cache"))