# Put a forename Excel file (https://www.avoindata.fi/data/fi/dataset/none) in this Data folder and run this script.
# Current statistics are from 1.2.2024 (DD.MM.YYYY)

import os
import pandas
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#region File Loading
file = None
for f in os.listdir("."):
    if f.endswith(".xlsx"):
        file = f
        break
if file == None:
    raise FileExistsError("No Excel file found!")
#endregion
#region File parsing
df = pandas.read_excel(file, sheet_name="Naiset kaikki")

newNaistenNimet = ""
for s in df["Etunimi"].values:
    if " " not in s:
        newNaistenNimet += f"{s}\n"
    else:
        print(f"Skipped \"{s}\" because it has whitespace.")

def addCustom(customSurname: str):
    global newNaistenNimet
    if customSurname not in newNaistenNimet:
        newNaistenNimet += f"{customSurname}\n"
    else:
        print(f"Custom surname {customSurname} is already in naisten etunimet!")
#endregion
#region Custom Forename
    # Currently there is no need to add any
#endregion
#region File Saving
with open("women_forenames.txt", "w", encoding="utf-8") as f:
    f.write(newNaistenNimet.strip("\n"))
#endregion
