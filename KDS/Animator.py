from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from enum import IntEnum, auto

import pygame

import KDS.Colors
import KDS.Logging
import KDS.Math


class OnAnimationEnd(IntEnum):
    Stop = auto()
    Loop = auto()
    PingPong = auto()

class Animation:
    def __init__(self, animation_name: str, number_of_images: int, duration: int, colorkey: Union[List[int], Tuple[int, int, int]] = KDS.Colors.White, _OnAnimationEnd: OnAnimationEnd = OnAnimationEnd.Stop, filetype: str = ".png", animation_dir: str = "Animations", load_in_reverse: bool = False) -> None:
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
        self.images: List[pygame.Surface] = []
        self.duration = duration
        self.ticks = number_of_images * duration - 1
        self.tick = 0
        self.colorkey = colorkey
        self.onAnimationEnd = _OnAnimationEnd
        self.PingPong = False
        self.done = False

        KDS.Logging.debug(f"Initialising {number_of_images} Animation Images...")
        iterRange = (0, number_of_images, 1) if not load_in_reverse else (number_of_images - 1, -1, -1)
        for i in range(*iterRange):
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

    def get_size(self) -> Tuple[int, int]:
        if len(self.images) > 0:
            return self.images[0].get_size()
        return (-1, -1)

    def get_width(self) -> int:
        return self.get_size()[0]

    def get_height(self) -> int:
        return self.get_size()[1]

class MultiAnimation:
    def __init__(self, **animations: Animation):
        if len(animations) < 1:
            raise ValueError("MultiAnimation requires atleast one animation to function!")
        self.animations: Dict[str, Animation] = animations
        firstKV = next(iter(animations.items()))
        self.active: Animation = firstKV[1]
        self.active_key: str = firstKV[0]

    def trigger(self, animation_trigger: str):
        if animation_trigger in self.animations:
            self.active = self.animations[animation_trigger]
            self.active_key = animation_trigger
        else:
            KDS.Logging.AutoError("MultiAnimation trigger invalid.")

    def update(self, reverse: bool = False):
        return self.active.update(reverse)

    def get_frame(self):
        return self.active.get_frame()

    def reset(self):
        for anim in self.animations:
            self.animations[anim].tick = 0

class AnimationType(IntEnum):
    Linear = auto()
    EaseInSine = auto()
    EaseOutSine = auto()
    EaseInOutSine = auto()
    EaseInCubic = auto()
    EaseOutCubic = auto()
    EaseInOutCubic = auto()
    EaseInQuint = auto()
    EaseOutQuint = auto()
    EaseInOutQuint = auto()
    EaseInCirc = auto()
    EaseOutCirc = auto()
    EaseInOutCirc = auto()
    EaseInElastic = auto()
    EaseOutElastic = auto()
    EaseInOutElastic = auto()
    EaseInQuad = auto()
    EaseOutQuad = auto()
    EaseInOutQuad = auto()
    EaseInQuart = auto()
    EaseOutQuart = auto()
    EaseInOutQuart = auto()
    EaseInExpo = auto()
    EaseOutExpo = auto()
    EaseInOutExpo = auto()
    EaseInBack = auto()
    EaseOutBack = auto()
    EaseInOutBack = auto()
    EaseInBounce = auto()
    EaseOutBounce = auto()
    EaseInOutBounce = auto()

class Value:
    _animT = {
        # Multiplying by 0.5 instead of dividing by 2, because Python doesn't have a compiler and multiplying is faster than division.
        AnimationType.EaseInSine: lambda t: 1 - KDS.Math.Cos(t * KDS.Math.PI * 0.5),
        AnimationType.EaseOutSine: lambda t: KDS.Math.Sin(t * KDS.Math.PI * 0.5),
        AnimationType.EaseInOutSine: lambda t: -(KDS.Math.Cos(KDS.Math.PI * t) - 1) * 0.5,
        AnimationType.EaseInCubic: lambda t: t * t * t,
        AnimationType.EaseOutCubic: lambda t: 1 - pow(1 - t, 3),
        AnimationType.EaseInOutCubic: lambda t: 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) * 0.5,
        AnimationType.EaseInQuint: lambda t: t * t * t * t * t,
        AnimationType.EaseOutQuint: lambda t: 1 - pow(1 - t, 5),
        AnimationType.EaseInOutQuint: lambda t: 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) * 0.5,
        AnimationType.EaseInCirc: lambda t: 1 - KDS.Math.Sqrt(1 - pow(t, 2)),
        AnimationType.EaseOutCirc: lambda t: KDS.Math.Sqrt(1 - pow(t - 1, 2)),
        AnimationType.EaseInOutCirc: lambda t: (1 - KDS.Math.Sqrt(1 - pow(2 * t, 2))) * 0.5 if t < 0.5 else (KDS.Math.Sqrt(1 - pow(-2 * t + 2, 2)) + 1) * 0.5,
        AnimationType.EaseInElastic: lambda t: 0 if t == 0 else (1 if t == 1 else -pow(2, 10 * t - 10) * KDS.Math.Sin((t * 10 - 10.75) * ((2 * KDS.Math.PI) / 3))),
        AnimationType.EaseOutElastic: lambda t: 0 if t == 0 else (1 if t == 1 else pow(2, -10 * t) * KDS.Math.Sin((t * 10 - 0.75) * ((2 * KDS.Math.PI) / 3)) + 1),
        AnimationType.EaseInOutElastic: lambda t: 0 if t == 0 else (1 if t == 1 else (-(pow(2, 20 * t - 10) * KDS.Math.Sin((20 * t - 11.125) * ((2 * KDS.Math.PI) / 4.5))) * 0.5 if t < 0.5 else (pow(2, -20 * t + 10) * KDS.Math.Sin((20 * t - 11.125) * ((2 * KDS.Math.PI) / 4.5))) * 0.5 + 1)), #Yeah... I have no idea what's happening here...
        AnimationType.EaseInQuad: lambda t: t * t,
        AnimationType.EaseOutQuad: lambda t: 1 - (1 - t) * (1 - t),
        AnimationType.EaseInOutQuad: lambda t: 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) * 0.5,
        AnimationType.EaseInQuart: lambda t: t * t * t * t,
        AnimationType.EaseOutQuart: lambda t: 1 - pow(1 - t, 4),
        AnimationType.EaseInOutQuart: lambda t: 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) * 0.5,
        AnimationType.EaseInExpo: lambda t: 0 if t == 0 else pow(2, 10 * t - 10),
        AnimationType.EaseOutExpo: lambda t: 1 if t == 1 else 1 - pow(2, -10 * t),
        AnimationType.EaseInOutExpo: lambda t: 0 if t == 0 else (1 if t == 1 else (pow(2, 20 * t - 10) * 0.5 if t < 0.5 else (2 - pow(2, -20 * t + 10)) * 0.5)),
        AnimationType.EaseInBack: lambda t: 2.70158 * t * t * t - 1.70158 * t * t,
        AnimationType.EaseOutBack: lambda t: 1 + 2.70158 * pow(t - 1, 3) + 1.70158 * pow(t - 1, 2),
        AnimationType.EaseInOutBack: lambda t: (pow(2 * t, 2) * ((2.5949095 + 1) * 2 * t - 2.5949095)) * 0.5 if t < 0.5 else (pow(2 * t - 2, 2) * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) * 0.5,
        AnimationType.EaseInBounce: lambda t: 1 - (lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t := t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t := t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t := t - 2.625 / 2.75) * t + 0.984375)))(1 - t),
        AnimationType.EaseOutBounce: lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t := t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t := t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t := t - 2.625 / 2.75) * t + 0.984375)),
        AnimationType.EaseInOutBounce: lambda t: (1 - (lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t := t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t := t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t := t - 2.625 / 2.75) * t + 0.984375)))(1 - 2 * t)) * 0.5 if t < 0.5 else (1 + (lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t := t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t := t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t := t - 2.625 / 2.75) * t + 0.984375)))(2 * t - 1)) * 0.5
    }

    def __init__(self, From: float, To: float, Duration: int, _AnimationType: AnimationType = AnimationType.Linear, _OnAnimationEnd: OnAnimationEnd = OnAnimationEnd.Stop) -> None:
        """Initialises a value animation.

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
        self.type = Value._animT[_AnimationType] if _AnimationType in Value._animT else None
        self.PingPong = False
        self.value = From

    def get_value(self) -> float:
        """Returns the current value.

        Returns:
            float: Current value.
        """
        try:
            t = self.tick / self.ticks
        except ZeroDivisionError:   # Trying and catching so that the function is generally faster
            t = 1.0                 # than when the user uses the animator not so optimally...
        if self.type != None: t = self.type(t)

        return KDS.Math.Lerp(self.From, self.To, t)

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

        return self.get_value()

class Color:
    def __init__(self, From: Tuple[int, int, int], To: Tuple[int, int, int], Duration: int, _AnimationType: AnimationType = AnimationType.Linear, _OnAnimationEnd: OnAnimationEnd = OnAnimationEnd.Stop) -> None:
        self._r = Value(From[0], To[0], Duration, _AnimationType, _OnAnimationEnd)
        self._g = Value(From[1], To[1], Duration, _AnimationType, _OnAnimationEnd)
        self._b = Value(From[2], To[2], Duration, _AnimationType, _OnAnimationEnd)

    @property
    def From(self) -> Tuple[int, int, int]:
        return (int(self._r.From), int(self._g.From), int(self._b.From))

    @From.setter
    def From(self, value: Tuple[int, int, int]):
        self._r.From = value[0]
        self._g.From = value[1]
        self._b.From = value[2]

    @property
    def To(self) -> Tuple[int, int, int]:
        return (int(self._r.To), int(self._g.To), int(self._b.To))

    @To.setter
    def To(self, value: Tuple[int, int, int]):
        self._r.To = value[0]
        self._g.To = value[1]
        self._b.To = value[2]

    @property
    def Finished(self) -> bool:
        return self._r.Finished and self._g.Finished and self._b.Finished

    @property
    def tick(self) -> int:
        return self._r.tick

    @tick.setter
    def tick(self, value: int):
        self._r.tick = value
        self._g.tick = value
        self._b.tick = value

    @property
    def ticks(self) -> int:
        return self._r.ticks

    def get_value(self) -> Tuple[int, int, int]:
        return (round(self._r.get_value()), round(self._g.get_value()), round(self._b.get_value()))

    def update(self, reverse: bool = False) -> Tuple[int, int, int]:
        return (round(self._r.update(reverse)), round(self._g.update(reverse)), round(self._b.update(reverse)))
