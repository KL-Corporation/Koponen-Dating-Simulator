from typing import Any, Tuple, Union

import pygame
from PIL import Image as PIL_Image
from PIL import ImageFilter as PIL_ImageFilter

import KDS.Colors
import KDS.Logging
import KDS.Math

def ToBool(value, fallbackValue: Any = False, hideErrorMessage: bool = False) -> Union[bool, Any]:
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
    try:
        if isinstance(value, str):
            value = value.lower()
            if value in ("t", "true"): return True
            elif value in ("f", "false"): return False
            elif not hideErrorMessage:
                KDS.Logging.AutoError(f"Cannot convert {value} to bool.")
                return fallbackValue
        elif isinstance(value, int) or isinstance(value, float):
            if value > 0: return True
            else: return False
        elif isinstance(value, bool): return value
        if not hideErrorMessage: KDS.Logging.AutoError(f"Value {value} is not a valid type.")
    except Exception as e:
        KDS.Logging.AutoError(f"Encountered an error when converting to bool. Exception: {e}")
    return fallbackValue

def AutoType(value: str, fallbackValue: Any = None) -> Union[int, float, bool, Any]:
    try:
        r = int(value)
        return r
    except ValueError:
        pass
    try:
        r = float(value)
        return r
    except ValueError:
        pass
    r = ToBool(value, None, True)
    if r != None:
        return r
    return fallbackValue

def AutoType2(value: str):
    return AutoType(value, value)

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
    mode = "RGB" if not alpha else "RGBA"

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

    kelvin = KDS.Math.Clamp(kelvin, 1000.0, 40000.0)

    tmp_internal = kelvin / 100.0

    # red
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * pow(tmp_internal - 60, -0.1332047592)
        red = round(KDS.Math.Clamp(tmp_red, 0.0, 255.0))

    # green
    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * KDS.Math.Log(tmp_internal) - 161.1195681661
        green = round(KDS.Math.Clamp(tmp_green, 0.0, 255.0))
    else:
        tmp_green = 288.1221695283 * pow(tmp_internal - 60, -0.0755148492)
        green = round(KDS.Math.Clamp(tmp_green, 0.0, 255.0))

    # blue
    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * KDS.Math.Log(tmp_internal - 10) - 305.0447927307
        blue = round(KDS.Math.Clamp(tmp_blue, 0.0, 255.0))

    return red, green, blue

def HSVToRGB(hue: float, saturation: float, value: float) -> Tuple[float, float, float]:
    """Converts an HSV color to RGB. This method automatically converts the hue to the range of 0-1.

    Args:
        hue (float): The hue of the color.
        saturation (float): The saturation of the color.
        value (float): The value / brightness of the color.

    Returns:
        Tuple[float, float, float]: The converted RGB color.
    """
    return HSVToRGB2(hue / 360.0, saturation, value)

def HSVToRGB2(hue: float, saturation: float, value: float) -> Tuple[float, float, float]:
    """Converts an HSV color to RGB. This method does not automatically convert the hue to the range of 0-1.

    Args:
        hue (float): The hue of the color.
        saturation (float): The saturation of the color.
        value (float): The value / brightness of the color.

    Returns:
        Tuple[float, float, float]: The converted RGB color.
    """
    # I have no idea what's happening here... I just stole this.

    if saturation == 0.0:
        value *= 255
        return (value, value, value)
    i = int(hue*6.)
    f = (hue*6.)-i
    p, q, t = int(255*(value*(1.-saturation))), int(255*(value * (1.-saturation*f))), int(255*(value*(1.-saturation*(1.-f))))
    value *= 255
    i %= 6
    if i == 0:
        return (value, t, p)
    if i == 1:
        return (q, value, p)
    if i == 2:
        return (p, value, t)
    if i == 3:
        return (p, q, value)
    if i == 4:
        return (t, p, value)
    if i == 5:
        return (value, p, q)
    else:
        KDS.Logging.AutoError("Invalid HSV => RGB Conversion color.")
        return (0, 0, 0)

def ToLines(text: str, font: pygame.font.Font, max_width: Union[int, float]):
    # Freezes if word is longer than max_width...
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

def ToRational(value: float) -> str:
    rational, base = KDS.Math.SplitFloat(value)
    base = int(base)
    marks = {0.0: "", 0.25: "+", 0.5: "½", 0.75: "-", 1.0: ""}
    closest = KDS.Math.Closest(rational, marks.keys())
    mark = marks[closest]
    if closest > 0.5:
        base += 1
    return f"{base}{mark}"
