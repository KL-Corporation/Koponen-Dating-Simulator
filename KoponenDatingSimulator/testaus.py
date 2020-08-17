import os, shutil

originalPath = os.getcwd()

src = "C:/Users/aarok/OneDrive/Työpöytä/gzdoom-4-3-3-Windows-64bit"

os.chdir(src)

files = os.listdir()
files_to_remove = list()

for file in files:
    if ".wad" in file and " - " in file:
        print(file)
        source = os.path.join(src, file)
        destination = os.path.join(src, "playedMaps", file)
        shutil.move(source, destination)

os.chdir(originalPath)