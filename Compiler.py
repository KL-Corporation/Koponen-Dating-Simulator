import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    "--windowed",
    "--icon",
    "F:/PyGame/Koponen-Dating-Simulator/Assets/Textures/Branding/gameIcon.ico",
    "--add-data",
    "F:/PyGame/Koponen-Dating-Simulator/Assets;Assets/",
    "--paths",
    "F:/PyGame/Koponen-Dating-Simulator/KDS",
    f"{os.path.dirname(os.path.abspath(__file__))}/KoponenDatingSimulator.py"
])