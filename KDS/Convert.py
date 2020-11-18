from typing import Tuple
import pygame
import math
import KDS.Logging
import KDS.Colors
import KDS.Math
from inspect import currentframe, getouterframes
from PIL import Image as PIL_Image
from PIL import ImageFilter as PIL_ImageFilter

def ToBool(value, fallbackValue: bool = False, hideErrorMessage: bool = False) -> bool:
    """Converts a value to bool with these rules:
        1. String: [t, true = True] [f, false = False] (Not case dependent)
        2. Int: [0 > True] [0 <= False]
        3. Float: [0.0 > True] [0.0 <= False]
        4. Bool: [True = True] [False = False]
        Will return fallbackValue if requirements are not met.
        
    Args:
        value: The value you want to convert.

    Returns:
        bool: The converted bool.
    """
    if isinstance(value, str):
        value = value.lower()
        if value in ("t", "true"): return True
        elif value in ("f", "false"): return False
        elif not hideErrorMessage:
            KDS.Logging.AutoError(f"Cannot convert {value} to bool.", currentframe())
            return fallbackValue
    elif isinstance(value, int):
        if value > 0: return True
        else: return False
    elif isinstance(value, float):
        if value > 0.0: return True
        else: return False
    elif isinstance(value, bool): return value
    if not hideErrorMessage: KDS.Logging.AutoError(f"Value {value} is not a valid type.", currentframe())
    return fallbackValue

def ToGrayscale(image: pygame.Surface):
    """Converts an image to grayscale.

    Args:
        image (pygame.Surface): The image to be converted.

    Returns:
        pygame.Surface: The converted image.
    """
    arr = pygame.surfarray.pixels3d(image)
    arr = arr.dot([0.298, 0.587, 0.114])[:, :, None].repeat(3, axis=2)
    return pygame.surfarray.make_surface(arr)

def ToBlur(image: pygame.Surface, strength: int, alpha: bool = False):
    mode = "RGB"
    if alpha:
        mode = "RGBA"
    toBlur = pygame.image.tostring(image, mode)
    blurredImage = PIL_Image.frombytes(mode, image.get_size(), toBlur).filter(PIL_ImageFilter.GaussianBlur(radius=strength))
    blurredString = blurredImage.tobytes("raw", mode)
    blurredSurface = pygame.image.fromstring(blurredString, image.get_size(), mode)
    if alpha: blurredSurface.convert_alpha()
    else: blurredSurface.convert()
    return blurredSurface

def AspectScale(image: pygame.Surface, size: Tuple[int, int], horizontalOnly: bool = False, verticalOnly: bool = False):
    if (image.get_width() / image.get_height() > size[0] / size[1] or horizontalOnly) and not verticalOnly: scaling = size[0] / image.get_width()
    else: scaling = size[1] / image.get_height()
    return pygame.transform.scale(image, (int(image.get_width() * scaling), int(image.get_height() * scaling)))

def ToMultiplier(boolean: bool):
    return -1 if boolean else 1

def CorrelatedColorTemperatureToRGB(kelvin: float) -> Tuple[int, int, int]:
    """Color Correlated Color Temperature as an RGB color.

    Args:
        kelvin (float): The correlated color temperature. Is clamped to the range [1000, 40000].

    Returns:
        Tuple[int, int, int]: [description]
    """
    
    kelvin = KDS.Math.Clamp(kelvin, 1000, 40000)
    
    tmp_internal = kelvin / 100.0
    
    # red 
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        red = round(KDS.Math.Clamp(tmp_red, 0, 255))
    
    # green
    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        green = round(KDS.Math.Clamp(tmp_green, 0, 255))
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        green = round(KDS.Math.Clamp(tmp_green, 0, 255))
    
    # blue
    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        blue = round(KDS.Math.Clamp(tmp_blue, 0, 255))
    
    return red, green, blue

def ToLines(text: str, font: pygame.font.Font, max_width: int or float):
    if font.size(text)[0] > max_width:
        text_split = [wrd + " " for wrd in text.split(" ")]
        text_split[len(text_split) - 1] = text_split[len(text_split) - 1].strip()
        new_split = [text_split]
        while font.size("".join(new_split[-1]))[0] > max_width:
            toTest = new_split[-1]
            i = 0
            while font.size("".join(toTest[:i]))[0] <= max_width:
                i += 1
                if i >= len(toTest):
                    break
            i -= 1
                    
            new_split.append(toTest[i:])
            new_split[-2] = toTest[:i]
        if len(new_split[-1]) < 1: del(new_split[-1])
        return tuple(["".join(new_split[i]) for i in range(len(new_split))])
    else: return tuple([text])