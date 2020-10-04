import pickle
import os

"""
<<<<<<<<<<<<<<<<<<<<<<<< DISCLAIMER >>>>>>>>>>>>>>>>>>>>>>>>>

Me ei nyt käytetäkään string formaattia sen hitauden, huonouden
ja hankalakäyttöisyyden takia. Sen sijaan käytetään bytes muuttujaa
sekä read- ja writebinary ominaisuuksia. Käytämme siis binary filejä.

¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
"""

class Testiclass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg1 * arg2

listOfClassInstances = [Testiclass(a, b) for a, b in zip([x for x in range(0,5)], [x for x in range(5,10)])]
print(listOfClassInstances)

byteString = pickle.dumps(listOfClassInstances) #<-- Muuttujan listOfClassInstances tyyppi on lista; Lista on täynnä Testiclass instanceja
print(byteString) #<-- muuttujan byteString tyyppi on bytes

with open(os.path.join(os.path.dirname(__file__), "classlist.kdsbinary"), "wb") as f:
    f.write(byteString)
    #Huomaa, että tätä ei tarvitse sulkea "f.close()" komennolla
#Tiedosto on suljettu tässä kohtaa automaattisesti

##############################################################

#Sitten otetaan data takaisin tiedostosta

with open(os.path.join(os.path.dirname(__file__), "classlist.kdsbinary"), "rb") as f:
    data = f.read()

outputList = pickle.loads(data)
print(outputList) #<-- alkuperäinen lista on siis ladattu tiedostosta
print(outputList[0].arg1)#<-- Listan instancet pitävät sisällään alkuperäiset muuttujat ja niiden arvot

#############################################################################
#                                                                           #
#                    TÄSTÄ KAIKESTA VOIMME SIIS PÄÄTELLÄ:                   #
#                                                                           #
#    Meidän kannattaa tallentaa siis jokainen save joko kansiona tai        #
#    zip-filenä. Kansio voi olla helpompi. Kansioon siis tulee kaikkki      #
#    enemies.kdsbinary ja tiles.kdsbinary tiedostot. (Yksi mahdollisuus)    #
#                                                                           #
#############################################################################

