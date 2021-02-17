# Put a surname Excel file (https://www.avoindata.fi/data/fi/dataset/none) in this Data folder and run this script.

import os
import pandas
os.chdir(os.path.dirname(os.path.abspath(__file__)))

file = None
for f in os.listdir("."):
    if f.endswith(".xlsx"):
        file = f
        break
if file == None:
    raise FileExistsError("No Excel file found!")

df = pandas.read_excel(file, sheet_name="Nimet")

newSukunimet = []
for s in df["Sukunimi"].values:
    if " " not in s:
        newSukunimet.append(s)
        newSukunimet.append("\n")
    else:
        print(f"Skipped \"{s}\" because it has whitespace.")
        
with open("surnames.txt", "w", encoding="utf-8") as f:
    f.writelines(newSukunimet)