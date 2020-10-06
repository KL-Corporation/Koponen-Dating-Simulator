from inspect import currentframe
import KDS.Logging
import KDS.Math
import KDS.Colors
import pygame
import math

class OnAnimationEnd:
    Stop = "stop"
    Loop = "loop"
    PingPong = "pingpong"

class Animation:
    def __init__(self, animation_name: str, number_of_images: int, duration: int, colorkey: tuple, loops: int, filetype=".png"): #loops = -1, if infinite loops
        """Initialises an animation.

        Args:
            animation_name (str): The name of the animation. Will load the corresponding files from the Animations folder. Name will be converted to [animation_name]_[animation_index].
            number_of_images (int): The frame count of your animation.
            duration (int): The duration of every frame in ticks.
            colorkey (tuple): The color that will be converted to alpha in every frame.
            loops (int): The amount of times you want the animation to loop. (-1 = infinite)
        """
        self.images = []
        self.duration = duration
        self.ticks = number_of_images * duration - 1
        self.tick = 0
        self.colorkey = colorkey
        self.loops = loops
        if loops != -1:
            self.loops_count = 0
            self.done = False

        KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialising {} Animation Images...".format(number_of_images), False)
        for i in range(number_of_images):
            converted_animation_name = animation_name + "_" + str(i) + filetype
            path = "Assets/Textures/Animations/" + converted_animation_name #Kaikki animaation kuvat ovat oletusarvoisesti png-muotoisia
            image = pygame.image.load(path).convert()
            image.set_colorkey(self.colorkey) #Kaikki osat kuvasta joiden väri on colorkey muutetaan läpinäkyviksi
            KDS.Logging.Log(KDS.Logging.LogType.debug, "Initialised Animation Image: {}".format(converted_animation_name), False)

            for _ in range(duration):
                self.images.append(image)

                
    #update-funktio tulee kutsua silmukan jokaisella kierroksella, jotta animaatio toimii kunnolla
    #update-funktio palauttaa aina yhden pygame image-objektin

    def update(self):
        """Updates the animation

        Returns:
            Surface | Surface, bool: Returns the image to blit and an animation finished bool if loops is not infinite.
        """

        self.tick += 1
        if self.tick > self.ticks:
            if self.loops == -1:
                self.tick = 0
            else:
                self.tick = self.ticks - 1
            if self.loops != -1:
                self.loops_count += 1
                if self.loops_count == self.loops:
                    self.done = True

        if self.loops == -1:
            return self.images[self.tick]
        else:
            return self.images[self.tick], self.done

    def get_frame(self) -> pygame.Surface:
        """Returns the currently active frame.

        Returns:
            pygame.Surface: Currently active frame.
        """
        return self.images[self.tick]

    def reset(self):
        self.tick = 0
        self.loops_count = 0
        self.done = False

class Legacy:
    """The legacy animator
    """
    @staticmethod
    def load_animation(name: str, number_of_images: int):
        """Loads an animation sequence using the legacy Animator.

        Args:
            name (str): The name of your frames inside Assets => Textures => Player. (A number will be appended to the end to load each frame)
            number_of_images (int): The number of images ("frames") your animation has.

        Returns:
            list: A list of all of the images in the animation
        """
        animation_list = []
        for i in range(number_of_images):
            path = "Assets/Textures/Player/" + name + str(i) + ".png"
            img = pygame.image.load(path).convert()
            img.set_colorkey(KDS.Colors.GetPrimary.White)
            animation_list.append(img)
        return animation_list
    
    #Float is not already a name of a variable, float is. Also it doesn't matter... It is still accessed by KDS.Animator.Float because it is not imported as from KDS.Animator so it will not conflict.
class Float:
    class AnimationType:
        Linear = "Linear"
        EaseIn = "EaseIn"
        EaseOut = "EaseOut"
        Exponential = "Exponential"
        SmoothStep = "SmoothStep"
        SmootherStep = "SmootherStep"
        
    def __init__(self, From: float, To: float, Duration: int, Type: AnimationType or str, _OnAnimationEnd: OnAnimationEnd or str):
        """Initialises a float animation.

        Args:
            From (float): The starting point of the float animation.
            To (float): The ending point of the float animation.
            Duration (int): The amount of ticks it takes to finish the entire float animation.
            Type (AnimationType): The type of float animation you want.
            _OnAnimationEnd (OnAnimationEnd): What will the animator do when the animaton has finished.
        """
        self.From = From
        self.To = To
        self.ticks = Duration
        self.tick = 0
        self.onAnimationEnd = _OnAnimationEnd
        self.type = Type
        self.PingPong = False
        self.value = From

    def get_value(self) -> float:
        """Returns the current value.

        Returns:
            float: Current value.
        """
        if self.type == Float.AnimationType.Linear:
            t = self.tick / self.ticks
            return KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.EaseIn:
            t = 1.0 - math.cos((self.tick / self.ticks) * math.pi * 0.5)
            return KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.EaseOut:
            t = math.sin((self.tick / self.ticks) * math.pi * 0.5)
            return KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.Exponential:
            t = self.tick / self.ticks
            return KDS.Math.Lerp(self.From, self.To, t * t)
        elif self.type == Float.AnimationType.SmoothStep:
            t = self.tick / self.ticks
            return KDS.Math.SmoothStep(self.From, self.To, t * t * (3.0 - (2.0 * t)))
        elif self.type == Float.AnimationType.SmootherStep:
            t = self.tick / self.ticks
            return KDS.Math.Lerp(self.From, self.To, t * t * t * (t * ((6.0 * t) - 15.0) + 10.0))
        else:
            KDS.Logging.AutoError("Incorrect Float Animation Type!", currentframe())
            return 0
    
    def update(self, reverse=False):
        """Updates the float animation

        Args:
            reverse (bool, optional): Determines the animation direction. Defaults to False.

        Returns:
            float: The lerped float value.
        """
        if self.PingPong:
            reverse = not reverse
        if not reverse:
            self.tick += 1
            if self.tick > self.ticks:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = self.ticks
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = 0
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = True
        else:
            self.tick -= 1
            if self.tick < 0:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = 0
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = self.ticks
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = False
        
        if self.type == Float.AnimationType.Linear:
            t = self.tick / self.ticks
            self.value = KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.EaseIn:
            t = 1.0 - math.cos((self.tick / self.ticks) * math.pi * 0.5)
            self.value = KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.EaseOut:
            t = math.sin((self.tick / self.ticks) * math.pi * 0.5)
            self.value = KDS.Math.Lerp(self.From, self.To, t)
        elif self.type == Float.AnimationType.Exponential:
            t = self.tick / self.ticks
            self.value = KDS.Math.Lerp(self.From, self.To, t * t)
        elif self.type == Float.AnimationType.SmoothStep:
            t = self.tick / self.ticks
            self.value = KDS.Math.SmoothStep(self.From, self.To, t * t * (3.0 - (2.0 * t)))
        elif self.type == Float.AnimationType.SmootherStep:
            t = self.tick / self.ticks
            self.value = KDS.Math.Lerp(self.From, self.To, t * t * t * (t * ((6.0 * t) - 15.0) + 10.0))
        else:
            KDS.Logging.AutoError("Incorrect Float Animation Type!", currentframe())
            self.value = 0
        
        return self.value