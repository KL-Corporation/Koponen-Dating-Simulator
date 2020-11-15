import inquirer
import PyInstaller.__main__
import os, shutil
from datetime import datetime

class CompileOptions:
    main = "main.py"
    levelBuilder = "LevelBuilder.py"
toCompile = inquirer.Checkbox("toCompile", "Which scripts do you want to compile?", (CompileOptions.main, CompileOptions.levelBuilder), "main.py")
answers = inquirer.prompt([
    toCompile
])

AppDataPath = os.path.join(os.getenv('APPDATA'), "KL Corporation", "KDS Compiler")
CachePath = os.path.join(AppDataPath, "cache")
workDir = os.path.join(AppDataPath, "work")
build_index = 0
while os.path.isdir(os.path.join(AppDataPath, f"build_{build_index}")):
    build_index += 1
buildDir = os.path.join(AppDataPath, f"build_{build_index}")
levelBuilderBuildDir = os.path.join(AppDataPath, f"LevelBuilder_build_{build_index}")
os.makedirs(AppDataPath, exist_ok=True)
os.makedirs(CachePath, exist_ok=True)
os.makedirs(workDir, exist_ok=True)
os.makedirs(buildDir, exist_ok=True)
os.makedirs(levelBuilderBuildDir, exist_ok=True)

homeDir = os.path.dirname(os.path.abspath(__file__))

if CompileOptions.main in answers["toCompile"]:
    PyInstaller.__main__.run([
        "--noconfirm",
        f"--name=main.py",
        "--windowed",
        f"--paths={homeDir}/KDS",
        f"--distpath={buildDir}",
        f"--workpath={workDir}",
        f"--add-data={homeDir}/Assets;Assets",
        f"--icon={homeDir}/Assets/Textures/Branding/gameIcon.ico",
        ""
    ])
    
    #pyinstaller --noconfirm --onedir --windowed --icon "F:/PyGame/Koponen-Dating-Simulator/Assets/Textures/Branding/gameIcon.ico" --add-data "F:/PyGame/Koponen-Dating-Simulator/KDS;KDS/" --add-data "F:/PyGame/Koponen-Dating-Simulator/Assets;Assets/"  ""
    
    
if CompileOptions.levelBuilder in answers["toCompile"]:
    PyInstaller.__main__.run([
        "--noconfirm",
        f"--name=LevelBuilder.py",
        "--windowed",
        f"--paths={homeDir}/KDS",
        f"--distpath={buildDir}",
        f"--workpath={workDir}",
        f"--add-data={homeDir}/Assets;Assets",
        f"--icon={homeDir}/Assets/Textures/Branding/levelBuilderIcon.ico",
        ""
    ])
    
shutil.rmtree(CachePath)