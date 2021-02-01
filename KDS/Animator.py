from typing import Callable, List, Tuple, Union

import pygame

import KDS.Colors
import KDS.Logging
import KDS.Math


class OnAnimationEnd:
    Stop = "stop"
    Loop = "loop"
    PingPong = "pingpong"

class Animation:
    def __init__(self, animation_name: str, number_of_images: int, duration: int, colorkey: Union[List[int], Tuple[int, int, int]] = KDS.Colors.White, _OnAnimationEnd: str = OnAnimationEnd.Stop, filetype: str = ".png", animation_dir: str = "Animations") -> None:
        """Initialises an animation.

        Args:
            animation_name (str): The name of the animation. Will load the corresponding files from the Animations folder. Name will be converted to {animation_name}_{animation_index}.
            number_of_images (int): The frame count of your animation.
            duration (int): The duration of evert frame in ticks.
            colorkey (tuple, optional): The color that will be converted to alpha in every frame. Defaults to (255, 255, 255).
            _OnAnimationEnd (OnAnimationEnd, optional): What will the animator do when the animation has finished. Defaults to OnAnimationEnd.Stop.
            filetype (str, optional): Specifies the loaded file's filetype. Defaults to ".png".
            animation_dir (str, optional): The directory of the Textures directory this script is going to search for the animation images. Defaults to "Animations".
        """
        if number_of_images < 1 or duration < 1:
            KDS.Logging.AutoError(f"Number of images or duration cannot be less than 1! Number of images: {number_of_images}, duration: {duration}")
        self.images = []
        self.duration = duration
        self.ticks = number_of_images * duration - 1
        self.tick = 0
        self.colorkey = colorkey
        self.onAnimationEnd = _OnAnimationEnd
        self.PingPong = False
        self.done = False

        KDS.Logging.debug(f"Initialising {number_of_images} Animation Images...")
        for i in range(number_of_images):
            converted_animation_name = animation_name + "_" + str(i) + filetype
            path = f"Assets/Textures/{animation_dir}/{converted_animation_name}" #Kaikki animaation kuvat ovat oletusarvoisesti png-muotoisia
            image = pygame.image.load(path).convert()
            image.set_colorkey(self.colorkey) #Kaikki osat kuvasta joiden väri on colorkey muutetaan läpinäkyviksi
            KDS.Logging.debug(f"Initialised Animation Image: {animation_dir}/{converted_animation_name}")

            for _ in range(duration):
                self.images.append(image)
        
        self.size = self.images[0].get_size()
                
    #update-funktio tulee kutsua silmukan jokaisella kierroksella, jotta animaatio toimii kunnolla
    #update-funktio palauttaa aina yhden pygame image-objektin

    def update(self, reverse: bool = False) -> pygame.Surface:
        """Updates the animation

        Returns:
            Surface: Returns the image to blit.
        """
        self.done = False
        if self.PingPong:
            reverse = not reverse
        if not reverse:
            self.tick += 1
            if self.tick > self.ticks:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = self.ticks
                    self.done = True
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = 0
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = True
                else:
                    KDS.Logging.AutoError("Invalid On Animation End Type!")
        else:
            self.tick -= 1
            if self.tick < 0:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = 0
                    self.done = True
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = self.ticks
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = False
                else:
                    KDS.Logging.AutoError("Invalid On Animation End Type!")
        return self.images[self.tick]

    def get_frame(self) -> pygame.Surface:
        """Returns the currently active frame.

        Returns:
            pygame.Surface: Currently active frame.
        """
        return self.images[self.tick]
    
    def change_colorkey(self, colorkey: Tuple[int, int, int]):
        for image in self.images:
            image.set_colorkey(colorkey)
            
class MultiAnimation:
    def __init__(self, **animations: Animation):
        self.animations = animations
        self.active = None
        for key in animations:
            if self.active == None:
                self.active = animations[key]
            else:
                break
    
    def trigger(self, animation_trigger):
        if animation_trigger in self.animations:
            self.active = self.animations[animation_trigger]
        else:
            KDS.Logging.AutoError("MultiAnimation trigger invalid.")
            
    def update(self, reverse: bool = False):
        return self.active.update(reverse)
    
    def get_frame(self):
        return self.active.get_frame()
    
    def reset(self):
        for anim in self.animations:
            self.animations[anim].tick = 0

class AnimationType:
    # Multiplying by 0.5 instead of dividing by 2, because Python doesn't have a compiler and multiplying is faster than division.
    Linear = lambda t: t
    EaseInSine = lambda t: 1 - KDS.Math.Cos(t * KDS.Math.PI * 0.5)
    EaseOutSine = lambda t: KDS.Math.Sin(t * KDS.Math.PI * 0.5)
    EaseInOutSine = lambda t: -(KDS.Math.Cos(KDS.Math.PI * t) - 1) * 0.5
    EaseInCubic = lambda t: t * t * t
    EaseOutCubic = lambda t: 1 - pow(1 - t, 3)
    EaseInOutCubic = lambda t: 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) * 0.5
    EaseInQuint = lambda t: t * t * t * t * t
    EaseOutQuint = lambda t: 1 - pow(1 - t, 5)
    EaseInOutQuint = lambda t: 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) * 0.5
    EaseInCirc = lambda t: 1 - KDS.Math.Sqrt(1 - pow(t, 2))
    EaseOutCirc = lambda t: KDS.Math.Sqrt(1 - pow(t - 1, 2))
    EaseInOutCirc = lambda t: (1 - KDS.Math.Sqrt(1 - pow(2 * t, 2))) * 0.5 if t < 0.5 else (KDS.Math.Sqrt(1 - pow(-2 * t + 2, 2)) + 1) * 0.5
    EaseInElastic = lambda t: 0 if KDS.Math.Approximately(t, 0) else (1 if KDS.Math.Approximately(t, 1) else -pow(2, 10 * t - 10) * KDS.Math.Sin((t * 10 - 10.75) * ((2 * KDS.Math.PI) / 3)))
    EaseOutElastic = lambda t: 0 if KDS.Math.Approximately(t, 0) else (1 if KDS.Math.Approximately(t, 1) else pow(2, -10 * t) * KDS.Math.Sin((t * 10 - 0.75) * ((2 * KDS.Math.PI) / 3)) + 1)
    EaseInOutElastic = lambda t: 0 if KDS.Math.Approximately(t, 0) else (1 if KDS.Math.Approximately(t, 1) else (-(pow(2, 20 * t - 10) * KDS.Math.Sin((20 * t - 11.125) * ((2 * KDS.Math.PI) / 4.5))) * 0.5 if t < 0.5 else (pow(2, -20 * t + 10) * KDS.Math.Sin((20 * t - 11.125) * ((2 * KDS.Math.PI) / 4.5))) * 0.5 + 1)) #Yeah... I have no idea what's happening here...
    EaseInQuad = lambda t: t * t
    EaseOutQuad = lambda t: 1 - (1 - t) * (1 - t)
    EaseInOutQuad = lambda t: 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) * 0.5
    EaseInQuart = lambda t: t * t * t * t
    EaseOutQuart = lambda t: 1 - pow(1 - t, 4)
    EaseInOutQuart = lambda t: 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) * 0.5
    EaseInExpo = lambda t: 0 if KDS.Math.Approximately(t, 0) else pow(2, 10 * t - 10)
    EaseOutExpo = lambda t: 1 if KDS.Math.Approximately(t, 1) else 1 - pow(2, -10 * t)
    EaseInOutExpo = lambda t: 0 if KDS.Math.Approximately(t, 0) else (1 if KDS.Math.Approximately(t, 1) else (pow(2, 20 * t - 10) * 0.5 if t < 0.5 else (2 - pow(2, -20 * t + 10)) * 0.5))
    EaseInBack = lambda t: 2.70158 * t * t * t - 1.70158 * t * t
    EaseOutBack = lambda t: 1 + 2.70158 * pow(t - 1, 3) + 1.70158 * pow(t - 1, 2)
    EaseInOutBack = lambda t: (pow(2 * t, 2) * ((2.5949095 + 1) * 2 * t - 2.5949095)) * 0.5 if t < 0.5 else (pow(2 * t - 2, 2) * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) * 0.5
    EaseInBounce = lambda t: 1 - AnimationType.EaseOutBounce(1 - t)
    EaseOutBounce = lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t := t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t := t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t := t - 2.625 / 2.75) * t + 0.984375))
    EaseInOutBounce = lambda t: (1 - AnimationType.EaseOutBounce(1 - 2 * t)) * 0.5 if t < 0.5 else (1 + AnimationType.EaseOutBounce(2 * t - 1)) * 0.5

class Float:
    def __init__(self, From: float, To: float, Duration: int, _AnimationType: Callable[[float], float] = AnimationType.Linear, _OnAnimationEnd: str = OnAnimationEnd.Stop) -> None:
        """Initialises a float animation.

        Args:
            From (float): The starting point of the float animation.
            To (float): The ending point of the float animation.
            Duration (int): The amount of ticks it takes to finish the entire float animation.
            _AnimationType (AnimationType): The type of float animation you want.
            _OnAnimationEnd (OnAnimationEnd): What will the animator do when the animaton has finished.
        """
        self.From = From
        self.To = To
        self.Finished = False
        self.ticks = Duration
        self.tick = 0
        self.onAnimationEnd = _OnAnimationEnd
        self.type = _AnimationType
        self.PingPong = False
        self.value = From

    def get_value(self) -> float:
        """Returns the current value.

        Returns:
            float: Current value.
        """
        if self.ticks != 0: return KDS.Math.Lerp(self.From, self.To, self.type(self.tick / self.ticks))
        else: return self.To
    
    def update(self, reverse: bool = False) -> float:
        """Updates the float animation

        Args:
            reverse (bool, optional): Determines the animation direction. Defaults to False.

        Returns:
            float: The lerped float value.
        """
        self.Finished = False
        if self.PingPong:
            reverse = not reverse
        if not reverse:
            self.tick += 1
            if self.tick > self.ticks:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = self.ticks
                    self.Finished = True
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = 0
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = True
                else:
                    KDS.Logging.AutoError("Invalid On Animation End Type!")
        else:
            self.tick -= 1
            if self.tick < 0:
                if self.onAnimationEnd == OnAnimationEnd.Stop:
                    self.tick = 0
                    self.Finished = True
                elif self.onAnimationEnd == OnAnimationEnd.Loop:
                    self.tick = self.ticks
                elif self.onAnimationEnd == OnAnimationEnd.PingPong:
                    self.PingPong = False
                else:
                    KDS.Logging.AutoError("Invalid On Animation End Type!")
        
        if self.ticks != 0: return KDS.Math.Lerp(self.From, self.To, self.type(self.tick / self.ticks))
        else: return self.To

class Color:
    def __init__(self, From: Tuple[int, int, int], To: Tuple[int, int, int], Duration: int, _AnimationType: Callable[[float], float] = AnimationType.Linear, _OnAnimationEnd: str = OnAnimationEnd.Stop) -> None:
        self.int0 = Float(From[0], To[0], Duration, _AnimationType, _OnAnimationEnd)
        self.int1 = Float(From[1], To[1], Duration, _AnimationType, _OnAnimationEnd)
        self.int2 = Float(From[2], To[2], Duration, _AnimationType, _OnAnimationEnd)
        
    def get_value(self) -> Tuple[int, int, int]:
        return (round(self.int0.get_value()), round(self.int1.get_value()), round(self.int2.get_value()))
    
    def update(self, reverse: bool = False) -> Tuple[int, int, int]:
        return (round(self.int0.update(reverse)), round(self.int1.update(reverse)), round(self.int2.update(reverse)))
    
    def changeValues(self, From: Tuple[int, int, int], To: Tuple[int, int, int]):
        self.int0.From = From[0]
        self.int0.To = To[0]
        self.int1.From = From[1]
        self.int1.To = To[1]
        self.int2.From = From[2]
        self.int2.To = To[2]
    
    def getValues(self):
        return (self.int0.From, self.int1.From, self.int2.From), (self.int0.From, self.int1.From, self.int2.From)
    
    def getFinished(self):
        return True if self.int0.Finished and self.int1.Finished and self.int2.Finished else False  
