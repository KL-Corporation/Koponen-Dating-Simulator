import KDS.Missions
import KDS.ConfigManager
import KDS.Koponen
import KDS.Story
import KDS.Logging
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
    KDS.Koponen.requestReturnAlt = None
    if gamemode == Modes.Story:
        if index == 1:
            Presets.Tutorial()
            KDS.Missions.InitialiseMission("enter_school", "Mene Kouluun")
            KDS.Missions.InitialiseTask("enter_school", "enter", "Avaa koulun ovi painamalla: E", (KDS.Missions.Listeners.LevelEnder, 1.0))

        elif index == 2:
            Presets.KoponenIntroduction()

            KDS.Koponen.Talk.Conversation.schedule("Hei! Siinä sinä oletkin. Halusinkin kertoa sinulle uudesta tavasta nostaa num... Hetkinen, ethän sinä ole tyttö... tai edes oppilaani. No jaa, näytät kuitenkin ihan fiksulta kaverilta.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Voit nostaa numeroasi suorittamalla tehtäviä. Voisit aloittaa pyytämällä tehtävää.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
            KDS.Koponen.Talk.Conversation.schedule("Kahvikuppini taitaa olla hukassa... Olisitko kiltti ja etsisit sen?", KDS.Koponen.Prefixes.koponen, True)

            KDS.Missions.InitialiseMission("coffee_mission", "Kuumaa Kamaa")
            KDS.Missions.InitialiseTask("coffee_mission", "find_mug", "Etsi Koposen Kahvikuppi", (KDS.Missions.Listeners.ItemPickup, 3, 1.0))
            KDS.Missions.InitialiseKoponenTask("coffee_mission", "return_mug", "Palauta Koposen Kahvikuppi", 3)

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
            KDS.Koponen.Talk.Conversation.schedule("Hienoa työtä ystäväiseni.", KDS.Koponen.Prefixes.koponen, True)
            KDS.Koponen.Talk.Conversation.schedule("Voit nyt hetken rauhassa tutkia uutta kouluasi. Kokeile vaikka löytää saunavessa, sieltä pääset jatkamaan koulupolkuasi.", KDS.Koponen.Prefixes.koponen)

            KDS.Missions.InitialiseMission("sauna_and_exit", "Suuret Haaveet")
            KDS.Missions.InitialiseTask("sauna_and_exit", "find_and_exit", "Etsi saunavessa koulupolkusi jatkamiseksi", (KDS.Missions.Listeners.LevelEnder, 1.0))

        elif index == 4:
            Presets.KoponenMissionRequest()

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
            KDS.Koponen.Talk.Conversation.schedule("Sattuisiko sinulla olemaan mitään tehtävää minulle?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Olen kuullut, että fysiikan opettaja keittelee laittomuuksia kemiavarastossa. Voisitko tuoda minulle mahdollisesti todisteen siitä?", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)

            KDS.Missions.InitialiseMission("laittomuuksia", "Laittomuuksia")
            KDS.Missions.InitialiseTask("laittomuuksia", "search", "Etsi jotain epäilyttävää kemiavarastosta", (KDS.Missions.Listeners.ItemPickup, 27, 1.0))
            KDS.Missions.InitialiseKoponenTask("laittomuuksia", "return", "Palauta se Koposelle", 27)

            KDS.Koponen.Talk.Conversation.schedule("Kiitos erittäin paljon. Otan tämän varmuuden vuoksi mukaan seuraavaan opettajien kokoukseen.", KDS.Koponen.Prefixes.koponen, True)
            KDS.Koponen.Talk.Conversation.schedule("""Jatketaanpas sitten tuntia…
Ensimmäisen asteen yhtälössä esiintyy muuttujan ensimmäinen potenssi, mutta ei korkeampia potensseja. Ensimmäisen asteen yhtälöitä ovat esimerkiksi
2x − 1 = 3 ja
4x + 6 = -x – 11
Toisen asteen yhtälössä taas esiintyy muuttujan toinen potenssi, mutta ei korkeampia potensseja. Toisen asteen yhtälöitä ovat esimerkiksi
x^2 = 7 ja
4x^2 + 3x – 1 = 0
Kolmannen asteen yhtälöitä taas ovat esimerkiksi
x^3 = 69 ja
420x^3 + 13x – 69 = 69420
Joo vitut jatka pelin pelaamista mä en jaksa kirjottaa enempää tekstiä Koposen sanottavaks...""", KDS.Koponen.Prefixes.koponen, True)
        elif index == 3:
            KDS.Missions.InitialiseMission("explore", "Kummituksia", NoSound=True)
            KDS.Missions.InitialiseTask("explore", "find_walkie_talkie", "Tutki vanhaa koulurakennusta")

            KDS.Missions.InitialiseMission("fuck", "Mitä vittua?")
            KDS.Missions.InitialiseTask("fuck", "bail", "Pakene koulusta", (KDS.Missions.Listeners.LevelEnder, 1.0))

        elif index == 7:
            Presets.KoponenMissionRequest()

            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
            KDS.Koponen.Talk.Conversation.schedule("Minulla on tylsää... Olisiko sinulla jotain tehtävää minulle?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Kyllähän näitä aina löytyy... Mietitäänpäs...", KDS.Koponen.Prefixes.koponen, forcePrefix=True)
            KDS.Koponen.Talk.Conversation.schedule("Olen kuullut muutamalta oppilaalta, että tänne koulun pihalle tulisi yön aikana vartijoita kiusaamaan kilttejä oppilaita. Voisitko jäädä tänne yöksi selvittämään asiaa?", KDS.Koponen.Prefixes.koponen, forcePrefix=True)
            KDS.Koponen.Talk.Conversation.schedule("Ehdottomasti. Mitä vain omalle Koposelleni.", KDS.Koponen.Prefixes.player)

        elif index == 8:
            KDS.Missions.InitialiseMission("t", "Telttailua")
            KDS.Missions.InitialiseTask("t", "tent", "Mene telttaan nukkumaan", (KDS.Missions.Listeners.TentSleepStart, 1.0))

            KDS.Missions.InitialiseMission("o", "O'ou")
            KDS.Missions.InitialiseTask("o", "kill", "Hankkiudu Eroon Vartijasta", (KDS.Missions.Listeners.EnemyDeath, 1.0))

            KDS.Missions.InitialiseMission("s", "Kuin Tukki")
            KDS.Missions.InitialiseTask("s", "sleep_again", "Nuku aamuun asti", (KDS.Missions.Listeners.TentSleepStart, 0.5))

            KDS.Missions.InitialiseMission("wait", "Odota")
            KDS.Missions.InitialiseTask("wait", "unlock_door", "Odota Koposta, kunnes hän tulee avaamaan oven")
            KDS.Missions.InitialiseTask("wait", "follow", "Seuraa Koposta kouluun", (KDS.Missions.Listeners.LevelEnder, 1.0))

        elif index == 9:
            KDS.Missions.InitialiseMission("principal_name", "Rehtoripilailua")
            KDS.Missions.InitialiseTask("principal_name", "name_it", "Keksi rehtorille pilanimi")

            KDS.Koponen.Talk.Conversation.schedule("Heh, minulla on sinulle mahtavia uutisia.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Koulumme sai juuri uuden rehtorin, jolle voimme keksiä pilanimen...", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Mitä ehdottaisit?", KDS.Koponen.Prefixes.koponen, True)
            KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.PRINCIPALNAMEINPUT, None)
            KDS.Koponen.Talk.Conversation.schedule("Kävisikö {principalName}?", KDS.Koponen.Prefixes.player)
            KDS.Koponen.Talk.Conversation.schedule("Hahaha, tuo on täydellinen.", KDS.Koponen.Prefixes.koponen)
            KDS.Koponen.Talk.Conversation.schedule("Pitää alkaa kutsumaan häntä tuolla nimellä.", KDS.Koponen.Prefixes.koponen)

        elif index == 10:
            KDS.Koponen.requestReturnAlt = "CARD"


#region Biology Exam
#     KDS.Missions.InitialiseMission("biology_exam", "Biologian Tunti")
#     KDS.Missions.InitialiseTask("biology_exam", "go_to_biology", "Mene Biologian Tunnille")
#
#     KDS.Missions.InitialiseMission("lunch", "Ruokailu")
#     KDS.Missions.InitialiseTask("lunch", "go_to_canteen", "Mene Ruokalaan")
#     Presets.KoponenMissionRequest()
#endregion

    elif gamemode == Modes.Campaign:
        if index == 1:
            Presets.Tutorial()
            Presets.LevelExit()
        else:
            Presets.LevelExit()
    elif gamemode == Modes.CustomCampaign:
        Presets.LevelExit()
    else:
        KDS.Logging.AutoError("Invalid gamemode!")