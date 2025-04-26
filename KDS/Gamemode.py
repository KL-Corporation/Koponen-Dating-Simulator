import KDS.Math
import KDS.Missions
import KDS.ConfigManager
import KDS.Koponen
import KDS.Story
import KDS.Logging
import KDS.Keys

from enum import IntEnum

class Modes(IntEnum):
    """The list of gamemodes this game has.
    """
    Story = 0
    Campaign = 1
    CustomCampaign = 2

gamemode: Modes = Modes.Story

def SetGamemode(Gamemode: Modes, MissionsId: str, EnemyCount: int):
    """Sets the gamemode in the first argument and creates the necessary missions for the level"""

    global gamemode
    gamemode = Gamemode

    class Presets:
        @staticmethod
        def Tutorial():
            KDS.Missions.InitialiseMission("tutorial", "Tutoriaali")
            KDS.Missions.InitialiseTask(
                "tutorial", "walk",
                f"Liiku käyttämällä: {{binding:{KDS.Keys.moveUp.name}}}, {{binding:{KDS.Keys.moveLeft.name}}}, {{binding:{KDS.Keys.moveDown.name}}}, {{binding:{KDS.Keys.moveRight.name}}} ja {{binding:{KDS.Keys.moveRun.name}}}",
                (KDS.Missions.Listeners.Movement, 0.005)
            )
            KDS.Missions.InitialiseTask("tutorial", "inventory", "Käytä tavaraluetteloa rullaamalla hiirtä", (KDS.Missions.Listeners.InventorySlotSwitching, 0.25))
            KDS.Missions.InitialiseTask("tutorial", "trash", f"Poista roska tavaraluettelostasi painamalla: {{binding:{KDS.Keys.dropItem.name}}}", (KDS.Missions.Listeners.ItemDrop, 6, 1.0), (KDS.Missions.Listeners.ItemPickup, 6, -1.0))

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

    KDS.Missions.Clear()
    KDS.Koponen.Talk.Conversation.reset()
    KDS.Koponen.requestReturnAlt = None
    KDS.Koponen.storyDateOverride = False
    KDS.Missions.Listeners.TileFireCreated.OnTrigger -= KDS.Story.badStoryEndingFunc
    KDS.Missions.Listeners.KoponenTalkEmbed1.OnTrigger -= KDS.Story.switchToStoryHappyTalkMusic
    KDS.Story.BadEndingTrigger = False
    #region Story
    if MissionsId == "story_1":
        Presets.Tutorial()
        KDS.Missions.InitialiseMission("enter_school", "Mene Kouluun")
        KDS.Missions.InitialiseTask("enter_school", "enter", f"Avaa koulun ovi painamalla: {{binding:{KDS.Keys.functionKey.name}}}", (KDS.Missions.Listeners.Teleport, 1.0))

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

    elif MissionsId == "story_2":
        KDS.Missions.InitialiseMission("story_exam", "Biologian Tunti", True)
        KDS.Missions.InitialiseTask("story_exam", "go_to_class", "Mene biologian tunnille")

        KDS.Missions.InitialiseMission("food", "Ruokailu", False)
        KDS.Missions.InitialiseTask("food", "go_to_eat", "Mene Ruokalaan", (KDS.Missions.Listeners.LevelEnder, 1.0))

        Presets.KoponenMissionRequest()

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Onko sinulla tehtävää minulle?", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Tulit juuri sopivaan aikaan. Haluaisin tehdä tutkimuksen siitä kuka olisi koulun paras opettaja... Siis minun lisäkseni tietenkin... Kävisitkö kyselemässä tätä muutamalta oppilaalta?", KDS.Koponen.Prefixes.koponen)

        KDS.Missions.InitialiseMission("research", "Tutkimus")
        KDS.Missions.InitialiseStudentTask("research", "ask","Kysy oppilaiden mielipidettä", 10, f"Kysy mielipidetta [{{binding:{KDS.Keys.functionKey.name}}}]", 39)
        KDS.Missions.InitialiseKoponenTask("research", "answers", "Palauta kyselypaperi", 39)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
        KDS.Koponen.Talk.Conversation.schedule("Tässä ovat tulokseni", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Ohhoh... Kiitoksia. Katsotaanpas...", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Hetkinen... Miksi olet merkinnyt tähän kaikille saman määrän ääniä?", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Koulumme opettajat olivat niin hyviä, ettei kukaan osannut päättää.", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Hmm... Kiinnostavaa. Hyvää työtä {playerName}", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("En muuten nähnyt musiikin opettajaa listassa... Ehkä se saattaisi muuttaa tuloksia.", KDS.Koponen.Prefixes.player)

    elif MissionsId == "story_3":
        Presets.KoponenMissionRequest()

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Sattuisiko sinulla olemaan mitään tehtävää minulle?", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Olen kuullut, että fysiikan opettaja keittelee laittomuuksia kemiavarastossa. Voisitko tuoda minulle mahdollisesti todisteen siitä?", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)

        KDS.Missions.InitialiseMission("laittomuuksia", "Laittomuuksia")
        KDS.Missions.InitialiseTask("laittomuuksia", "search", "Etsi jotain epäilyttävää kemiavarastosta", (KDS.Missions.Listeners.ItemPickup, 27, 1.0))
        KDS.Missions.InitialiseKoponenTask("laittomuuksia", "return", "Palauta se Koposelle", 27)

        KDS.Koponen.Talk.Conversation.schedule("Kiitos erittäin paljon. Otan tämän varmuuden vuoksi mukaan seuraavaan opettajien kokoukseen.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("""Jatketaanpas sitten tuntia...
Ensimmäisen asteen yhtälössä esiintyy muuttujan ensimmäinen potenssi, mutta ei korkeampia potensseja. Ensimmäisen asteen yhtälöitä ovat esimerkiksi
2x – 1 = 3 ja
4x + 6 = -x – 11
Toisen asteen yhtälössä taas esiintyy muuttujan toinen potenssi, mutta ei korkeampia potensseja. Toisen asteen yhtälöitä ovat esimerkiksi
x^2 = 7 ja
4x^2 + 3x – 1 = 0
Kolmannen asteen yhtälöitä taas ovat esimerkiksi
x^3 = 69 ja
420x^3 + 13x – 69 = 69420
Joo vitut jatka pelin pelaamista mä en jaksa kirjottaa enempää tekstiä Koposen sanottavaks...""", KDS.Koponen.Prefixes.koponen, True)
    elif MissionsId == "story_4":
        Presets.KoponenMissionRequest()

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Jotkut ovat raportoineet, että vanhassa koulurakennuksessamme on havaittu kummituksia... Kävisitkö tutkimassa asiaa?", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule("Pelkään kummituksia...", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Niin minäkin... Sinähän halusit matikasta kympin, vai mitä?", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule("Kyllä Koponen...", KDS.Koponen.Prefixes.player)

        KDS.Missions.InitialiseMission("go", "Kohti Vanhaa")
        KDS.Missions.InitialiseTask("go", "bus", "Nouse bussin kyytiin", (KDS.Missions.Listeners.LevelEnder, 1.0))
    elif MissionsId == "story_5":
        KDS.Missions.InitialiseMission("explore", "Kummituksia", NoSound=True)
        KDS.Missions.InitialiseTask("explore", "find_walkie_talkie", "Tutki vanhaa koulurakennusta")

        KDS.Missions.InitialiseMission("fuck", "Mitä vittua?")
        KDS.Missions.InitialiseTask("fuck", "bail", "Pakene koulusta", (KDS.Missions.Listeners.LevelEnder, 1.0))

    elif MissionsId == "story_6":
        Presets.KoponenMissionRequest()

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Minulla on tylsää... Olisiko sinulla jotain tehtävää minulle?", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Kyllähän näitä aina löytyy... Mietitäänpäs...", KDS.Koponen.Prefixes.koponen, forcePrefix=True)
        KDS.Koponen.Talk.Conversation.schedule("Olen kuullut muutamalta oppilaalta, että tänne koulun pihalle tulisi yön aikana vartijoita kiusaamaan kilttejä oppilaita. Voisitko jäädä tänne yöksi selvittämään asiaa?", KDS.Koponen.Prefixes.koponen, forcePrefix=True)
        KDS.Koponen.Talk.Conversation.schedule("Ehdottomasti. Mitä vain omalle Koposelleni.", KDS.Koponen.Prefixes.player)

    elif MissionsId == "story_7":
        KDS.Missions.InitialiseMission("t", "Telttailua")
        KDS.Missions.InitialiseTask("t", "tent", "Mene telttaan nukkumaan", (KDS.Missions.Listeners.TileSleepStart, 1.0))

        KDS.Missions.InitialiseMission("o", "O'ou")
        KDS.Missions.InitialiseTask("o", "kill", "Hankkiudu Eroon Vartijasta", (KDS.Missions.Listeners.EnemyDeath, 1.0))

        KDS.Missions.InitialiseMission("s", "Kuin Tukki")
        KDS.Missions.InitialiseTask("s", "sleep_again", "Nuku aamuun asti", (KDS.Missions.Listeners.TileSleepStart, 0.5))

        KDS.Missions.InitialiseMission("wait", "Odota")
        KDS.Missions.InitialiseTask("wait", "unlock_door", "Odota Koposta, kunnes hän tulee avaamaan oven")
        KDS.Missions.InitialiseTask("wait", "follow", "Seuraa Koposta kouluun", (KDS.Missions.Listeners.LevelEnder, 1.0))

    elif MissionsId == "story_8":
        KDS.Missions.InitialiseMission("principal_name", "Rehtoripilailua")
        KDS.Missions.InitialiseTask("principal_name", "name_it", "Keksi rehtorille pilanimi")

        KDS.Koponen.Talk.Conversation.schedule("Heh, minulla on sinulle mahtavia uutisia.", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule("Koulumme sai juuri uuden rehtorin, jolle voimme keksiä pilanimen...", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule("Mitä ehdottaisit?", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.PRINCIPALNAMEINPUT, None)
        KDS.Koponen.Talk.Conversation.schedule("Kävisikö {principalName}?", KDS.Koponen.Prefixes.player)
        KDS.Koponen.Talk.Conversation.schedule("Hahaha, tuo on täydellinen.", KDS.Koponen.Prefixes.koponen)
        KDS.Koponen.Talk.Conversation.schedule("Pitää alkaa kutsumaan häntä tuolla nimellä.", KDS.Koponen.Prefixes.koponen)

    elif MissionsId == "story_9":
        KDS.Koponen.requestReturnAlt = "CARD"

        KDS.Missions.InitialiseMission("rules", "Ohjeistus")
        KDS.Missions.InitialiseTask("rules", "listen", "Kuuntele Koposen ohjeistus", (KDS.Missions.Listeners.KoponenTalk, 1.0))

        KDS.Koponen.Talk.Conversation.schedule("Tervetuloa Clarion Hotelliin. Ennen huoneisiin lähtöä haluaisin kertoa teille hieman turvallisuussäännöistä. Seuraa tätä tarkkaan, sillä tulen esittämään teille hotellimme turvaominaisuudet.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Älypuhelimia ja muita kannettavia elektronisia laitteita voidaan käyttää aulasta huoneisiin hotellitilassa ja normaalitilassa huoneisiin pääsyn jälkeen.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Muut elektroniset laitteet, kuten kannettavat tietokoneet täytyy sammuttaa ja pakata huoneeseen menemisen ajaksi.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Varmista, että jalkasi ovat kävelyasennossa ja silmäsi ovat auki. Nosta selkäsi pystyasentoon ja pakkaa reppusi.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Reppusi suljetaan vetämällä vetoketjusi kiinni. Avataksesi repun, vedä vetoketju auki.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Reppusi täytyy olla kiinni hotellihuoneeseen menon ja -paluun aikana ja -aina hotellihuoneessa, kun reppuvalo on päällä.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Reissumme on päihteetön ja hotellilain mukaan, päihteiden käyttäminen on kielletty vessoissa. Tämä pätee myös kannabikseen.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Hotellihenkilökuntasi on koulutettu takaamaan turvallisuutesi hotellissa. Sinun täytyy aina noudattaa heidän antamiaan ohjeita.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Jos hotellin paine tippuu, happimaskit tippuvat automaattisesti katosta. Ota lähin maski ja pue se päällesi. Pussi ei välttämättä täyty, vaikka happea virtaa. Pistä aina oma maskisi ensimmäiseksi ja auta vasta sen jälkeen muita.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Jos asut bisneshuoneessa, pelastusliivisi on sänkysi alla lokerossa. Turistihuoneessa pelastusliivisi on sänkysi alla pussissa.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Pistä liivi kaulasi ympärille ja kiristä sopivasti. Täytä pelastusliivi ainoastaan, kun poistut hotellista.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Tässä hotellissa on kahdeksan hätäpoistumistietä, jotka ovat kaikki merkattu vihervalkoisilla \"EXIT\" -kylteillä. Kaikki poistumistiet on varustettu liukumäillä. Lattiatason valot johtavat näihin uloskäynteihin.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Sinun täytyy mennä välittömästi hätäasentoon, kun sinua ohjeistetaan tekemään näin. Siinä on tärkeää taipua eteenpäin ja mahdollisimman alas. Hätätilanteessa on myös äärimmäisen tärkeää jättää kaikki käsimatkatavarat hotelliin.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Tämän hotellin turvallisuussäännöt löytyvät myös turvallisuuskortista, joka sijaitsee sängyn taskussa.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Jos teillä on joitain huolia tai murheita, kuten esimerkiksi tiputte yöllä sängystä ja murratte jalkanne, niin minut löytää huoneesta 210.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Jos teillä taas on suuri koti-ikävä, niin uima-allas on ylimmässä kerroksessa, jossa kyyneleenne eivät aiheuta vesivahinkoa.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Ja muistakaa, että lisääntyminen on sitten kiellettyä.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Nyt saatte mennä huoneisiinne heti, kun olette hakeneet korttinne minulta.", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("rm", "Huoneeseen")
        KDS.Missions.InitialiseTask("rm", "card", "Pyydä huoneesi avainkortti Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 1.0))
        KDS.Missions.InitialiseTask("rm", "go", "Mene huoneeseesi", (KDS.Missions.Listeners.LevelEnder, 1.0))

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.GIVEHOTELCARD, None)
        KDS.Koponen.Talk.Conversation.schedule("Tässä.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Huoneesi on 311.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Kiitos", KDS.Koponen.Prefixes.player, True)

        KDS.Missions.InitialiseMission("slp", "Hohhoijaa")
        KDS.Missions.InitialiseTask("slp", "sleep", "Mene nukkumaan", (KDS.Missions.Listeners.TileSleepStart, 1.0))

    elif MissionsId == "story_10":
        KDS.Missions.InitialiseMission("music", "Karseeta Jumputusmusaa")
        KDS.Missions.InitialiseTask("music", "findout", "Selvitä musiikin lähtöperä", (KDS.Missions.Listeners.LevelEnder, 1.0))

        KDS.Missions.InitialiseMission("more", "Lisää Selvitystä")
        KDS.Missions.InitialiseTask("more", "knock", "Koputa huoneen ovea", (KDS.Missions.Listeners.DoorGuardNPCEnable, 1.0), (KDS.Missions.Listeners.DoorGuardNPCDisable, -1.0))

        KDS.Missions.InitialiseMission("story_index_11_mission_door_blockage", "Ärsyttävä Este")
        KDS.Missions.InitialiseTask("story_index_11_mission_door_blockage", "annoying", "Tapa huoneen ovenvartija", (KDS.Missions.Listeners.DoorGuardNPCDeath, 1.0))
        KDS.Missions.InitialiseTask("story_index_11_mission_door_blockage", "story_index_11_mission_task_goin", "Mene huoneeseen") # Progress set by HotelGuardDoor class

        KDS.Missions.InitialiseMission("heck", "Hitto...")
        KDS.Missions.InitialiseTask("heck", "goslp", "Mene takaisin nukkumaan", (KDS.Missions.Listeners.TileSleepStart, 1.0))
        KDS.Missions.InitialiseTask("heck", "donttell", "(et kerro sitten tästä kenellekään)", (KDS.Missions.Listeners.TileSleepStart, 1.0))

    elif MissionsId == "story_11":
        # Auto open KoponenTalk
        KDS.Koponen.Talk.Conversation.schedule("Mitä vittua oikeesti?", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Hei arvaas mitä?", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("{principalName} antoi minulle potkut!", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Mukamas \"oppilaiden viihdyttäminen oppitunneilla on ehdottomasti kielletty tässä koulussa\" sekä \"kiusaamistilanteeseen ei saa missään nimessä puuttua\".", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Kostan tämän hänelle...", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Polttaisin tämän koulun, mutta minulla on vain kuusi euroa ja halvimmat sytytyspalat maksavat seitsemän euroa.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Hetkinen... Televisiossahan oli hetki sitten mainos tarjouksesta SS-Etukortin omistajalle... Olen varma, että biologian opettajalla on sellainen. Olen nähnyt hänet useasti käyttämässä sitä ostaessaan materiaaleja oppitunneillensa.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Ostavatko opettajat materiaaleja oppitunneillensa?", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Pakkohan sitä, kun koulu ei voi maksaa...", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Mutta kuitenkin... Koita keksiä joku tapa hankkia biologian opettajan SS-Etukortti. Jos joudut varautumaan voimakeinoihin, niin muista edes piilottaa ruumis. Tai noh... Totta puhuen minua ei kyllä kiinnosta onko se piilotettu.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Kortin saatuasi voisit mennä vanhan koulurakennuksen kautta SS-Marketille.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Tässä rahasi.", KDS.Koponen.Prefixes.koponen, True)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.REQUESTRETURNPALAT, None)

        KDS.Missions.InitialiseMission("hot", "Kuumat Paikat")
        KDS.Missions.InitialiseTask("hot", "search", "Etsi ase", (KDS.Missions.Listeners.AnyWeaponPickup, 1.0))
        KDS.Missions.InitialiseTask("hot", "kill", "Murhaa biologian opettaja", (KDS.Missions.Listeners.KuuMaDeath, 1.0))
        KDS.Missions.InitialiseTask("hot", "item", "Ota SS-Etukortti", (KDS.Missions.Listeners.ItemPickup, 19, 1.0))

        KDS.Missions.InitialiseMission("end", "Kaiken Loppu?")
        KDS.Missions.InitialiseTask("end", "goto_ss", "Mene SS-Markettiin", (KDS.Missions.Listeners.LevelEnder, 1.0))
        KDS.Missions.InitialiseTask("end", "buy", "Osta Lappi Sytytyspalat", (KDS.Missions.Listeners.ItemPurchase, 8, 1.0))
        KDS.Missions.InitialiseKoponenTask("end", "return", "Anna sytytyspalat Koposelle", 8, removeItems=False)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.REQUESTRETURNCLEAR, None)
        KDS.Koponen.Talk.Conversation.schedule("Ei sinun tarvitse noita minulle antaa... Sinä saat kunnian tehdä tämän.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Oletko varma?", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Olen täysin varma.", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("the_last_straw", "Viimeinen Oljenkorsi")
        KDS.Missions.InitialiseTask("the_last_straw", "lappisytytyspalat_ignite", "Sytytä tuli pääkäytävään", (KDS.Missions.Listeners.TileFireCreated, 1.0))
        KDS.Missions.Listeners.TileFireCreated.OnTrigger += KDS.Story.badStoryEndingFunc

        KDS.Missions.InitialiseMission("fire", "TULTA!")
        KDS.Missions.InitialiseTask("fire", "tell", "Kerro Koposelle tulesta", (KDS.Missions.Listeners.KoponenTalkEmbed0, 1.0))

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORTILEFIRE, None)
        KDS.Koponen.Talk.Conversation.schedule("Sytytin tulen. Poistutaan.", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Ei. Minä jään tänne.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Miksi? Sinähän kuolet!", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Nimenomaan.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Ei! Älä tee näin!", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Minun elämälläni ei ole enää merkitystä. Juokse nyt pois ennen kuin se on myöhäistä!", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.TRIGGERLISTENER0, None)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORSTORYENDING, None)

        KDS.Missions.InitialiseMission("exit", "Pakene Tulta")
        KDS.Missions.InitialiseTask("exit", "run", "Juokse pois koulusta")#, (KDS.Missions.Listeners.KoponenTalkEmbed1, 1.0))
                                                                          # We don't need the listener anymore as we force the ending through STORYDATEKOPONENENDING
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.TRIGGERLISTENER1, None)

        KDS.Missions.Listeners.KoponenTalkEmbed1.OnTrigger += KDS.Story.switchToStoryHappyTalkMusic

        KDS.Koponen.Talk.Conversation.schedule("Koponen! Sinunhan piti kuolla?", KDS.Koponen.Prefixes.player, True)
        KDS.Koponen.Talk.Conversation.schedule("Nähtyäni surusi tajusin jotain... Sinä olet elämäni tarkoitus. Sinä tuot merkitystä elämääni. Olet ollut ihana minulle enkä minä saa tuottaa sinulle pettymystä.", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Saatan olla rakastunut sinuun...", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Tulisitko kanssani treffeille?", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.STORYDATEKOPONENENDING, None)
    #endregion
    #region Campaign
    elif MissionsId == "campaign_tutorial":
        Presets.Tutorial()

        KDS.Missions.InitialiseMission("continue", "Jatka")
        KDS.Missions.InitialiseTask("continue", "cont", "Jatka kenttää eteenpäin", (KDS.Missions.Listeners.KeyDoorLocked, 1.0), (KDS.Missions.Listeners.ItemPickup, 13, 1.0))
        # check for item pickup since if the key has already been picked up, KeyDoorLocked will not fire anymore.

        KDS.Missions.InitialiseMission("red_key", "Ovi On Lukittu")
        KDS.Missions.InitialiseTask("red_key", "pick_key", "Nouda punainen avain yläkerrasta", (KDS.Missions.Listeners.ItemPickup, 13, 1.0))

        Presets.LevelExit()
    elif MissionsId == "campaign_legacy1":
        KDS.Missions.InitialiseMission("r1", "Tehtävä Koposelta")
        KDS.Missions.InitialiseTask("r1", "talk", "Puhu Koposelle", (KDS.Missions.Listeners.KoponenTalk, 1.0))
        KDS.Missions.InitialiseTask("r1", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 1.0))

        KDS.Koponen.Talk.Conversation.schedule("Hyvää päivää", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Saisinko tehtävän?", KDS.Koponen.Prefixes.sina, True)
        KDS.Koponen.Talk.Conversation.schedule("Toisitko minulle kahvikupin", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("cm", "Kahvikuppi")
        KDS.Missions.InitialiseKoponenTask("cm", "f", "Etsi kahvikuppi Koposelle", 3)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
        KDS.Koponen.Talk.Conversation.schedule("Loistavaa työtä", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("r2", "Tehtävä Koposelta")
        KDS.Missions.InitialiseTask("r2", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 0.5))

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Saisinko tehtävän?", KDS.Koponen.Prefixes.sina, True)
        KDS.Koponen.Talk.Conversation.schedule("Toisitko minulle kaasupolttimen", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("gb", "Kaasupoltin")
        KDS.Missions.InitialiseKoponenTask("gb", "f", "Etsi kaasupoltin Koposelle", 4)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
        KDS.Koponen.Talk.Conversation.schedule("Loistavaa työtä", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("r3", "Tehtävä Koposelta")
        KDS.Missions.InitialiseTask("r3", "mission", "Pyydä Tehtävää Koposelta", (KDS.Missions.Listeners.KoponenRequestMission, 0.34))

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONREQUEST, None)
        KDS.Koponen.Talk.Conversation.schedule("Saisinko tehtävän?", KDS.Koponen.Prefixes.sina, True)
        KDS.Koponen.Talk.Conversation.schedule("Toisitko minulle SS-Etukortin", KDS.Koponen.Prefixes.koponen, True)

        KDS.Missions.InitialiseMission("ss", "SS-Etukortti")
        KDS.Missions.InitialiseKoponenTask("ss", "f", "Etsi SS-Etukortti Koposelle", 19)

        KDS.Koponen.Talk.Conversation.schedule(KDS.Koponen.Talk.Conversation.WAITFORMISSIONRETURN, None)
        KDS.Koponen.Talk.Conversation.schedule("Loistavaa työtä", KDS.Koponen.Prefixes.koponen, True)
        KDS.Koponen.Talk.Conversation.schedule("Tulisitko kanssani treffeille?", KDS.Koponen.Prefixes.sina, True)
        KDS.Koponen.Talk.Conversation.schedule("Tulen kanssasi", KDS.Koponen.Prefixes.koponen, True)
    #endregion
    #region Presets
    elif MissionsId == "preset_tutorial":
        Presets.Tutorial()
    elif MissionsId == "preset_killEnemies":
        # bit increment so that if float addition has inaccuracies, we still reach 1.0
        addPerKill: float = KDS.Math.BitIncrement(1 / EnemyCount)
        KDS.Missions.InitialiseMission("kill_all_enemies", "Viholliset")
        KDS.Missions.InitialiseTask("kill_all_enemies", "exit", "Tapa Kaikki Viholliset", (KDS.Missions.Listeners.EnemyDeath, addPerKill))
    else:
        Presets.LevelExit()
    #endregion

#region Biology Exam
#     KDS.Missions.InitialiseMission("biology_exam", "Biologian Tunti")
#     KDS.Missions.InitialiseTask("biology_exam", "go_to_biology", "Mene Biologian Tunnille")
#
#     KDS.Missions.InitialiseMission("lunch", "Ruokailu")
#     KDS.Missions.InitialiseTask("lunch", "go_to_canteen", "Mene Ruokalaan")
#     Presets.KoponenMissionRequest()
#endregion
