import KDS.Missions
import KDS.ConfigManager
import KDS.Koponen
import KDS.Story
from enum import IntEnum

class Modes(IntEnum):
    """The list of gamemodes this game has.
    """
    Story = 0
    Campaign = 1
    CustomCampaign = 2

gamemode: Modes = Modes.Story

def SetGamemode(Gamemode: Modes, LevelIndex: int = 0):
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
            KDS.Missions.InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (KDS.Missions.Listeners.InventorySlotSwitching, 0.25))
            KDS.Missions.InitialiseTask("tutorial", "trash", "Poista roska tavaraluettelostasi painamalla: Q", (KDS.Missions.Listeners.ItemDrop, 6, 1.0), (KDS.Missions.Listeners.ItemPickup, 6, -1.0))

        @staticmethod
        def KoponenIntroduction():
            KDS.Missions.InitialiseMission("koponen_introduction", "Tutustu Koposeen")
            KDS.Missions.InitialiseTask("koponen_introduction", "talk", "Puhu Koposelle", (KDS.Missions.Listeners.KoponenTalk, 1.0))
            KDS.Missions.InitialiseTask("koponen_introduction", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 1.0))

        @staticmethod
        def KoponenMissionRequest():
            KDS.Missions.InitialiseMission("koponen_mission_request", "Tehtävä Koposelta")
            KDS.Missions.InitialiseTask("koponen_mission_request", "talk", "Puhu Koposelle", (KDS.Missions.Listeners.KoponenTalk, 1.0))
            KDS.Missions.InitialiseTask("koponen_mission_request", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 1.0))

        @staticmethod
        def LevelExit():
            KDS.Missions.InitialiseMission("reach_level_exit", "Uloskäynti")
            KDS.Missions.InitialiseTask("reach_level_exit", "exit", "Löydä Uloskäynti", (KDS.Missions.Listeners.LevelEnder, 1.0))

    index = LevelIndex

    KDS.Missions.Clear()
    KDS.Koponen.Talk.Conversation.clear()
    if gamemode == Modes.Story:
        if index == 1:
            Presets.Tutorial()
            KDS.Missions.InitialiseMission("enter_school", "Mene Kouluun")
            KDS.Missions.InitialiseTask("enter_school", "enter", "Avaa koulun ovi painamalla: E", (KDS.Missions.Listeners.Teleport, 1.0))

            Presets.KoponenIntroduction()

            KDS.Koponen.Talk.Conversation.schedule("Hei! Siinä sinä oletkin. Halusinkin kertoa sinulle uudesta tavasta nostaa num... Hetkinen, ethän sinä ole tyttö... tai edes oppilaani. No jaa, näytät kuitenkin ihan fiksulta kaverilta.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Voit nostaa numeroasi suorittamalla tehtäviä. Voisit aloittaa pyytämällä tehtävää.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST)
            KDS.Koponen.Talk.Conversation.schedule("Kahvikuppini taitaa olla hukassa... Olisitko kiltti ja etsisit sen?", KDS.Koponen.Prefixes.koponen, True)

            KDS.Missions.InitialiseMission("coffee_mission", "Kuumaa Kamaa")
            KDS.Missions.InitialiseTask("coffee_mission", "find_mug", "Etsi Koposen Kahvikuppi", (KDS.Missions.Listeners.ItemPickup, 3, 1.0))
            KDS.Missions.InitialiseKoponenTask("coffee_mission", "return_mug", "Palauta Koposen Kahvikuppi", "kahvikuppi", "kahvikupin", 3)

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN)
            KDS.Koponen.Talk.Conversation.schedule("Hienoa työtä ystäväiseni.", KDS.Koponen.Prefixes.koponen, True)
            KDS.Koponen.Talk.Conversation.schedule("Voit nyt hetken rauhassa tutkia uutta kouluasi. Kokeile vaikka löytää saunavessa, sieltä pääset jatkamaan koulupolkuasi.", KDS.Koponen.Prefixes.koponen)

            KDS.Missions.InitialiseMission("sauna_and_exit", "Suuret Haaveet")
            KDS.Missions.InitialiseTask("sauna_and_exit", "find_and_exit", "Etsi Saunavessa Koulupolkusi Jatkamiseksi", (KDS.Missions.Listeners.LevelEnder, 1.0))
        elif index == 2:
            KDS.Missions.InitialiseMission("t", "Telttailua")
            KDS.Missions.InitialiseTask("t", "tent", "Mene telttaan nukkumaan", (KDS.Missions.Listeners.TentSleepStart, 1.0))

            KDS.Missions.InitialiseMission("o", "O'ou")
            KDS.Missions.InitialiseTask("o", "kill", "Hankkiudu Eroon Vartijasta", (KDS.Missions.Listeners.EnemyDeath, 1.0))

            KDS.Missions.InitialiseMission("s", "Kuin Tukki")
            KDS.Missions.InitialiseTask("s", "sleep_again", "Nuku aamuun asti", (KDS.Missions.Listeners.TentSleepStart, 0.5))

            KDS.Missions.InitialiseMission("wait", "Odota")
            KDS.Missions.InitialiseTask("wait", "unlock_door", "Odota Koposta, kunnes hän tulee avaamaan oven")
            KDS.Missions.InitialiseTask("wait", "follow", "Seuraa Koposta kouluun", (KDS.Missions.Listeners.LevelEnder, 1.0))
        elif index == 3:
            KDS.Missions.InitialiseMission("explore", "Kummituksia", NoSound=True)
            KDS.Missions.InitialiseTask("explore", "find_walkie_talkie", "Tutki vanhaa koulurakennusta")

            KDS.Missions.InitialiseMission("fuck", "Mitä vittua?")
            KDS.Missions.InitialiseTask("fuck", "bail", "Pakene koulusta")
        elif index == 4:
            KDS.Missions.InitialiseMission("biology_exam", "Biologian Tunti")
            KDS.Missions.InitialiseTask("biology_exam", "go_to_biology", "Mene Biologian Tunnille")

            KDS.Missions.InitialiseMission("lunch", "Ruokailu")
            KDS.Missions.InitialiseTask("lunch", "go_to_canteen", "Mene Ruokalaan")
            Presets.KoponenMissionRequest()

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST)
            KDS.Koponen.Talk.Conversation.schedule("Onko sinulla tehtävää minulle?", KDS.Koponen.Prefixes.player, True)
            KDS.Koponen.Talk.Conversation.schedule("Olen kuullut, että fysiikan opettaja keittelee laittomuuksia alakerrassa. Voisitko tuoda minulle mahdollisesti todisteen siitä?", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Missä on \"alakerta\"?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Niinpä... Tämän takia pyysin sinua tekemään tämän.", KDS.Koponen.Prefixes.koponen)

            KDS.Missions.InitialiseMission("physics_teacher_blood", "Laittomuuksia")
            KDS.Missions.InitialiseTask("physics_teacher_blood", "downstairs", "Löydä Alakerta")
            KDS.Missions.InitialiseTask("physics_teacher_blood", "something_suspicious", "Etsi Jotain Epäilyttävää")
            KDS.Missions.InitialiseTask("physics_teacher_blood", "return_suspicious", "Palauta Tämä Koposelle")

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN)
            KDS.Koponen.Talk.Conversation.schedule("Kiitos erittäin paljon. Otan tämän varmuuden vuoksi mukaan seuraavaan opettajien kokoukseen.", KDS.Koponen.Prefixes.koponen, True)
            KDS.Koponen.Talk.Conversation.schedule("Oho perkele... Tuntisi alkaa kohta. Hopi hopi!", KDS.Koponen.Prefixes.koponen)
# KDS.Koponen.Talk.Conversation.schedule("Heh, minulla on sinulle mahtavia uutisia.", KDS.Koponen.Prefixes.koponen)
# KDS.Koponen.Talk.Conversation.schedule("Koulumme sai juuri uuden rehtorin, jolle voimme keksiä pilanimen...", KDS.Koponen.Prefixes.koponen)
# KDS.Koponen.Talk.Conversation.schedule("Mitä ehdottaisit?", KDS.Koponen.Prefixes.koponen, True)
# KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.PRINCIPALNAMEINPUT)
# KDS.Koponen.Talk.Conversation.schedule("Kävisikö {principalName}?", KDS.Koponen.Prefixes.player)
# KDS.Koponen.Talk.Conversation.schedule("Hahaha, tuo on täydellinen.", KDS.Koponen.Prefixes.koponen)
# KDS.Koponen.Talk.Conversation.schedule("Pitää alkaa kutsumaan häntä tuolla nimellä.", KDS.Koponen.Prefixes.koponen)

# KDS.Missions.InitialiseMission("principal_name", "Rehtoripilailua")
# KDS.Missions.InitialiseTask("principal_name", "name_it", "Keksi rehtorille pilanimi")
    else:
        if index == 1:
            Presets.Tutorial()
            Presets.LevelExit()
        else:
            Presets.LevelExit()