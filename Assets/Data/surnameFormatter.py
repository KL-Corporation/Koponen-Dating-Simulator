# Put a surname Excel file (https://www.avoindata.fi/data/fi/dataset/none) in this Data folder and run this script.

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
df = pandas.read_excel(file, sheet_name="Nimet")

newSukunimet = ""
for s in df["Sukunimi"].values:
    if " " not in s:
        newSukunimet += f"{s}\n"
    else:
        print(f"Skipped \"{s}\" because it has whitespace.")    

def addCustom(customSurname: str):
    global newSukunimet
    if customSurname not in newSukunimet:
        newSukunimet += f"{customSurname}\n"
    else:
        print(f"Custom surname {customSurname} is already in sukunimet!")
#endregion
#region Custom Surnames
    # Currently there is no need to add any
#endregion
#region File Saving 
with open("surnames.txt", "w", encoding="utf-8") as f:
    f.write(newSukunimet.strip("\n"))
#endregion