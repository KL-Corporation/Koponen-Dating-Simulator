import KDS.Missions

class Modes:
    """The list of gamemodes this game has.
    """
    Story = 0
    Campaign = 1
    CustomCampaign = 2

gamemode = Modes.Story

def SetGamemode(Gamemode: Modes and int, LevelIndex=0):
    """Sets the gamemode in the first argument.

    Args:
        Gamemode (Modes): The game mode you want to set.
        LevelIndex (int, optional): Will load the corresponding missions of a map if gamemode is set as campaign. Defaults to 0.
    """
    global gamemode
    gamemode = Gamemode
    KDS.Missions.InitialiseMissions(LevelIndex)
