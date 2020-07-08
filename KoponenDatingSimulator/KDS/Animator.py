import KDS.Logging
import pygame

class Animation:

    """
    Ensimmäinen argumentti odottaa animaation nimeä esim. "gasburner"
    Toinen argumentti odottaa kyseisen animaation kuvien määrää. Jos animaatiossa on 2 kuvaa, kannattaa toiseksi argumentiksi laittaa 2
    Kolmas argumentti odottaa yhden kuvan kestoa tickeinä.
    Animaation kuvat tulee tallentaa animations-kansioon png-muodossa tähän malliin:
        gasburner_0, gasburner_1, gasburner_2, gasburner_3 ja niin edelleen
    animation_name - string, number_of_images - int, duration - int
    """

    def __init__(self, animation_name: str, number_of_images: int, duration: int, colorkey, loops): #loops = -1, if infinite loops
        self.images = []
        self.duration = duration
        self.ticks = number_of_images * duration - 1
        self.tick = 0
        self.colorkey = colorkey
        self.loops = loops
        if loops != -1:
            self.loops_count = 0
            self.done = False

        for i in range(number_of_images):
            path = "resources/animations/" + animation_name + "_" + str(i) + ".png" #Kaikki animaation kuvat ovat oletusarvoisesti png-muotoisia
            image = pygame.image.load(path).convert()
            image.set_colorkey(self.colorkey) #Kaikki osat kuvasata joiden väri on RGB 255,255,255 muutetaan läpinäkyviksi

            for _ in range(duration):
                self.images.append(image)

        print(self.images)
        KDS.Logging.Log(KDS.Logging.LogType.debug, "Animation Images Initialised: " + str(len(self.images)))
        for image in self.images:
            KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialised Animation Image: " + str(image))
                
    #update-funktio tulee kutsua silmukan jokaisella kierroksella, jotta animaatio toimii kunnolla
    #update-funktio palauttaa aina yhden pygame image-objektin

    def update(self):
        self.tick += 1
        if self.tick > self.ticks:
            self.tick = 0
            if self.loops != -1:
                self.loops_count += 1
                if self.loops_count == self.loops:
                    self.done = True

        if self.loops == -1:
            return self.images[self.tick]
        else:
            return self.images[self.tick], self.done

    def reset(self):
        self.tick = 0
        self.loops_count = 0
        self.done = False
