import KDS.Missions

class Modes():
    Story = 0
    Campaign = 1

gamemode = Modes.Story

def SetGamemode(Gamemode: Modes, LevelIndex=0):
    """
    1. Gamemode: The gamemode you want to set
    2. LevelIndex (OPTIONAL): Will load the corresponding missions of a map if gamemode is set as campaign
    """
    global gamemode
    gamemode = Gamemode
    KDS.Missions.InitialiseMissions(LevelIndex)
