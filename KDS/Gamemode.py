import KDS.Missions
import KDS.Koponen

class Modes:
    """The list of gamemodes this game has.
    """
    Story = 0
    Campaign = 1
    CustomCampaign = 2

gamemode = Modes.Story

def SetGamemode(Gamemode: int, LevelIndex: int = 0):
    """Sets the gamemode in the first argument.

    Args:
        Gamemode (Modes): The game mode you want to set.
        LevelIndex (int, optional): Will load the corresponding missions of a map if gamemode is set as campaign. Defaults to 0.
    """
    
    global gamemode
    gamemode = Gamemode
    
    class Presets:
        @staticmethod
        def Tutorial():
            KDS.Missions.InitialiseMission("tutorial", "Tutoriaali")
            KDS.Missions.InitialiseTask("tutorial", "walk", "Liiku käyttämällä: WASD, Vaihto, CTRL ja Välilyönti", (KDS.Missions.Listeners.Movement, 0.005))
            KDS.Missions.InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (KDS.Missions.Listeners.InventorySlotSwitching, 0.2))
            KDS.Missions.InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q", (KDS.Missions.Listeners.ItemDrop, 6, 1.0), (KDS.Missions.Listeners.ItemPickup, 6, -1.0))
            
        @staticmethod
        def KoponenIntroduction():
            KDS.Missions.InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            KDS.Missions.InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", (KDS.Missions.Listeners.KoponenTalk, 1.0))
            KDS.Missions.InitialiseTask("koponen_introduction", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 1.0))
            
        @staticmethod
        def KoponenMissionRequest():
            KDS.Missions.InitialiseMission("koponen_mission_request", "Tehtävä Koposelta")
            KDS.Missions.InitialiseTask("koponen_mission_request", "talk", "Puhu Koposelle")
            KDS.Missions.InitialiseTask("koponen_mission_request", "mission", "Pyydä Tehtävää Koposelta")

        @staticmethod
        def LevelExit():
            KDS.Missions.InitialiseMission("reach_level_exit", "Uloskäynti")
            KDS.Missions.InitialiseTask("reach_level_exit", "exit", "Löydä Uloskäynti", (KDS.Missions.Listeners.LevelEnder, 1.0))
    
    index = LevelIndex
    
    KDS.Missions.Clear()
    if gamemode == Modes.Story:
        if index == 1:
            Presets.Tutorial()
            KDS.Missions.InitialiseMission("enter_school", "Mene Kouluun")
            KDS.Missions.InitialiseTask("enter_school", "enter", "Kävele Kouluun", (KDS.Missions.Listeners.LevelEnder, 1.0))
            
        elif index == 2:
            Presets.KoponenIntroduction()
            
            KDS.Koponen.Talk.Conversation.schedule("Hei! Siinä sinä oletkin. Halusinkin kertoa sinulle uudesta tavasta nostaa num... Hetkinen, ethän sinä ole tyttö... tai edes oppilaani. No jaa, näytät kuitenkin ihan fiksulta kaverilta.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Voit nostaa numeroasi suorittamalla tehtäviä. Voisit aloittaa pyytämällä tehtävää.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST)
            KDS.Koponen.Talk.Conversation.schedule("Kahvikuppini taitaa olla hukassa... Olisitko kiltti ja etsisit sen?")
            
            KDS.Missions.InitialiseMission("coffee_mission", "Kahvi Kuumana, Koponen Nuorena")
            KDS.Missions.InitialiseTask("coffee_mission", "find_mug", "Etsi Koposen Kahvikuppi", (KDS.Missions.Listeners.ItemPickup, 3, 1.0))
            KDS.Missions.InitialiseKoponenTask("coffee_mission", "return_mug", "Palauta Koposen Kahvikuppi", "kahvikuppi", "kahvikupin", 3)
            
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN)
            KDS.Koponen.Talk.Conversation.schedule("Hienoa työtä ystäväiseni.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Voit nyt hetken rauhassa tutkia uutta kouluasi. Kokeile vaikka löytää saunavessa, sieltä pääset jatkamaan koulupolkuasi.", KDS.Koponen.Prefixes.koponen)

            KDS.Missions.InitialiseMission("sauna_and_exit", "Suuret Haaveet")
            KDS.Missions.InitialiseTask("sauna_and_exit", "find_and_exit", "Etsi Saunavessa Koulupolkusi Jatkamiseksi", (KDS.Missions.Listeners.LevelEnder, 1.0))
            
        elif index == 3:
            KDS.Missions.InitialiseMission("biology_exam", "Biologian Tunti")
            KDS.Missions.InitialiseTask("biology_exam", "go_to_biology", "Mene Biologian Tunnille")
            
            KDS.Missions.InitialiseMission("lunch", "Ruokailu")
            KDS.Missions.InitialiseTask("lunch", "go_to_canteen", "Mene Ruokalaan")
            Presets.KoponenMissionRequest()
            
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST)
            KDS.Koponen.Talk.Conversation.schedule("Onko sinulla tehtävää minulle?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Olen kuullut, että fysiikan opettaja keittelee laittomuuksia alakerrassa. Voisitko tuoda minulle mahdollisesti todisteen siitä?", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Missä on \"alakerta\"?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Niinpä... Tämän takia pyysin sinua tekemään tämän.", KDS.Koponen.Prefixes.koponen)
            
            KDS.Missions.InitialiseMission("physics_teacher_meth", "Laittomuuksia")
            KDS.Missions.InitialiseTask("physics_teacher_meth", "downstairs", "Löydä Alakerta")
            KDS.Missions.InitialiseTask("physics_teacher_meth", "something_suspicious", "Etsi Jotain Epäilyttävää")
            KDS.Missions.InitialiseTask("physics_teacher_meth", "return_suspicious", "Palauta Tämä Koposelle")
            
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN)
            KDS.Koponen.Talk.Conversation.schedule("Kiitos erittäin paljon. Otan tämän varmuuden vuoksi mukaan seuraavaan opettajien kokoukseen.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Oho perkele... Tuntisi alkaa kohta. Hopi hopi!", KDS.Koponen.Prefixes.koponen)
    else:
        if index == 1:
            Presets.Tutorial()
            Presets.LevelExit()
        else:
            Presets.LevelExit()