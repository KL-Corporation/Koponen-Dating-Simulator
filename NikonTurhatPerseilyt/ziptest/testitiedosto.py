import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import zipfile

zipfile.ZipFile("testZippi.zip", "r").extractall("testosteroni")