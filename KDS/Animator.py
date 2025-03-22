from typing import Callable, Dict, Final, List, NamedTuple, Optional, Sequence, Tuple, Union

from enum import IntEnum, auto

import pygame

import KDS.Colors
import KDS.Logging
import KDS.Math


class OnAnimationEnd(IntEnum):
    Stop = auto()
    Loop = auto()
    PingPong = auto()

class _SurfaceCacheKey(NamedTuple):
    texture_path: str
    alpha: bool

    def __str__(self) -> str:
        return f"{self.texture_path}?alpha={'true' if self.alpha else 'false'}"

class _CachedAnimationSurface:
    def __init__(self, key: _SurfaceCacheKey, surf: pygame.Surface) -> None:
        self.key: Final[_SurfaceCacheKey] = key
        self.surface: Final[pygame.Surface] = surf
        self.refcount: int = 0

_surfaceCache: dict[_SurfaceCacheKey, _CachedAnimationSurface] = {}

class ShootFrametime(NamedTuple):
    frame_index: int
    frame_duration: int

class Animation:
    def __init__(self, animation_name: str, number_of_images: int, duration: int, colorkey: Union[list[int], Tuple[int, int, int], None] = KDS.Colors.White, _OnAnimationEnd: OnAnimationEnd = OnAnimationEnd.Stop, *, filetype: str = ".png", animation_dir: str = "Animations", alpha: bool = False, load_in_reverse: bool = False) -> None:
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
        self._images: List[_CachedAnimationSurface] = []
        self._duration = duration

        self.ticks = number_of_images * duration - 1
        self.tick = 0

        self.onAnimationEnd = _OnAnimationEnd
        self.PingPong = False
        self.done = False

        KDS.Logging.debug(f"Initialising {number_of_images} animation images...")
        iterRange = (0, number_of_images, 1) if not load_in_reverse else (number_of_images - 1, -1, -1)
        for i in range(*iterRange):
            converted_animation_name = animation_name + "_" + str(i) + filetype
            texture_path: str = f"{animation_dir}/{converted_animation_name}"
            cache_key: _SurfaceCacheKey = _SurfaceCacheKey(texture_path, alpha=alpha)
            surf: _CachedAnimationSurface | None = _surfaceCache.get(cache_key)
            if surf is None:
                path = "Assets/Textures/" + texture_path
                loaded_image: Final[pygame.Surface] = pygame.image.load(path)
                image: pygame.Surface
                if alpha:
                    image = loaded_image.convert_alpha()
                else:
                    image = loaded_image.convert()
                if colorkey is not None:
                    image.set_colorkey(colorkey)

                surf = _CachedAnimationSurface(cache_key, image)
                _surfaceCache[cache_key] = surf

                KDS.Logging.debug(f"Loaded shared animation image: {cache_key}")

            # We switched to shared surfaces so we assert this just in case
            verify_colorkey: Final[tuple[int, int, int, int] | None] = surf.surface.get_colorkey()
            if colorkey is None:
                if verify_colorkey is not None:
                    raise ValueError("Cached animation texture's colorkey does not match the requested colorkey.")
            else:
                if verify_colorkey != (*colorkey, 255):
                    raise ValueError("Cached animation texture's colorkey does not match the requested colorkey.")

            self._images.append(surf) # for each append we add a refcount
            surf.refcount += 1
            # KDS.Logging.debug(f"Initialised animation image: {animation_id}")

        self.size = self._images[0].surface.get_size()

    def __del__(self):
        for img in self._images: # when destroyed, decrement refcount
            img.refcount -= 1
            if img.refcount <= 0:
                # we only have a hadful of animations so unloading them is not that needed
                # but from my testing unloading and reloading didn't give a significant performance boost
                # so we'll just unload them then to save a bit of RAM
                _surfaceCache.pop(img.key, None) # Supply a default value so that if the key isn't found, we don't raise an error.
                if KDS.Logging.running: # Logger might have quit during application exit before __del__ is called
                    KDS.Logging.debug(f"Unloaded shared animation image: {img.key}")

    # HACK: I can't be bothered to refactor this old KDS codebase
    # so we create a special method to restore the old animation behaviour for AI shoot
    # this code is very vulnerable and can be broken/brake things easily
    def init_shoot_parameters(self, frametimes: tuple[ShootFrametime, ...]):
        """
        Hack function for KDS.AI

        DO NOT CALL MULTIPLE TIMES!!
        """
        assert(self._duration == 1)

        images: list[_CachedAnimationSurface] = []
        for f in frametimes:
            img: _CachedAnimationSurface = self._images[f.frame_index]
            images.extend(img for _ in range(f.frame_duration))
            # use duration 1 and append multiple identical frames
            # as Animation doesn't support per frame durations
            # and implementing that is out of the scope of this small-ish KDS update
        self._images = images
        self.ticks = len(images) - 1

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
                    self.tick = self.ticks
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
                    self.tick = 0
                else:
                    KDS.Logging.AutoError("Invalid On Animation End Type!")

        return self.get_frame()

    def get_frame(self) -> pygame.Surface:
        """Returns the currently active frame.

        Returns:
            pygame.Surface: Currently active frame.
        """
        return self._images[KDS.Math.FloorToInt(self.tick / self._duration)].surface

    # Commented out as we now use shared surfaces
    # def change_colorkey(self, colorkey: Tuple[int, int, int]):
    #     for image in self.images:
    #         image.set_colorkey(colorkey)

    def get_size(self) -> Tuple[int, int]:
        return self.size

    def get_width(self) -> int:
        return self.size[0]

    def get_height(self) -> int:
        return self.size[1]

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
        # self.value = From Seems to be a mistake that was left in the codebase, should use get_value instead.

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
        self._t: Final = Value(0.0, 1.0, Duration=Duration, _AnimationType=_AnimationType, _OnAnimationEnd=_OnAnimationEnd)

        self.From: tuple[int, int, int] = From
        self.To: tuple[int, int, int] = To

    @property
    def Finished(self) -> bool:
        return self._t.Finished

    @property
    def tick(self) -> int:
        return self._t.tick

    @tick.setter
    def tick(self, value: int):
        self._t.tick = value

    @property
    def ticks(self) -> int:
        return self._t.ticks

    def get_value(self) -> Tuple[int, int, int]:
        return self._get_value(self._t.get_value())

    def update(self, reverse: bool = False) -> Tuple[int, int, int]:
        return self._get_value(self._t.update(reverse=reverse))


    def _value(self, index: int, t: float) -> int:
        return round(KDS.Math.LerpUnclamped(self.From[index], self.To[index], t))

    def _get_value(self, t: float) -> tuple[int, int, int]:
        return (self._value(0, t), self._value(1, t), self._value(2, t))
