import datetime
from enum import IntEnum, auto
from typing import Any, Literal, Sequence, Tuple, TypeVar, Union, cast, Optional

import pygame
from PIL import Image as PIL_Image
from PIL import ImageFilter as PIL_ImageFilter

import KDS.Colors
import KDS.Logging
import KDS.Math

_T = TypeVar("_T")

class String:
    @staticmethod
    def ToBool(string: str, fallback: Optional[bool] = None, hideError: bool = False) -> Optional[bool]:
        """Converts a string to bool.

        Args:
            string (str): The input string to convert.
            fallback (Optional[bool], optional): The value to be returned if string does not match. Defaults to None.
            hideError (bool, optional): If True; no error message will be displayed if string cannot be converted. Defaults to False.

        Returns:
            Optional[bool]:
                True: String is the start of the word \"true\". (ignores case)
                False: String is the start of the word \"false\". (ignores case)
                fallback: String does not match.
        """
        s = string.lower()
        if "true".startswith(s): return True
        elif "false".startswith(s): return False
        elif not hideError:
            KDS.Logging.AutoError(f"Cannot convert \"{string}\" to bool.")
        return fallback

class DateTime:
    @staticmethod
    def Humanize(value: datetime.datetime) -> str:
        """Return a natural day.
        """
        now = datetime.datetime.now()
        delta = now - value
        seconds = delta.seconds
        days = delta.days

        if days == 0:
            if seconds < 10:
                return "just now"
            if seconds < 60:
                return f"{seconds} seconds ago"
            if seconds < 120:
                return "a minute ago"
            if seconds < 3600:
                return f"{KDS.Math.FloorToInt(seconds / 60)} minutes ago"
            if seconds < 7200:
                return "an hour ago"
            if seconds < 86400:
                return f"{KDS.Math.FloorToInt(seconds / 3600)} hours ago"
            return "<error>"
        if days == 1:
            return "yesterday"
        if days < 7:
            return f"{days} days ago"
        if days < 31:
            return f"{KDS.Math.FloorToInt(days / 7)} weeks ago"
        if days < 365:
            return f"{KDS.Math.FloorToInt(days / 30)} months ago"
        return f"{KDS.Math.FloorToInt(days / 365)} years ago"

#         if delta.days == 0:
#             return "today"
#         elif delta.days == 1:
#             return "tomorrow"
#         elif delta.days == -1:
#             return "yesterday"
#         return value.strftime(format)

# The shittier version of String.ToBool
def ToBool2(value: Any, fallbackValue: Any = False, hideErrorMessage: bool = False) -> Union[bool, Any]:
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

def AutoType(value: str, fallbackValue: _T) -> Union[str, int, float, bool, _T]:
    #region String
    if value.startswith("\"") and value.endswith("\""):
        return value.removeprefix("\"").removesuffix("\"").replace("\\\"", "\"")
    #endregion
    #region Int
    try:
        r = int(value)
        return r
    except ValueError:
        pass
    #endregion
    #region Float
    try:
        r = float(value)
        return r
    except ValueError:
        pass
    #endregion
    #region Bool
    r = String.ToBool(value, None, hideError=True)
    if r != None:
        return r
    #endregion
    return fallbackValue

def AutoType2(value: str, hideErrorMessage: bool = False) -> Union[str, bool, int, float, None]: # Strict type check for auto type
    if value.startswith("\"") and value.endswith("\""):
        return value
    elif value == "True":
        return True
    elif value == "False":
        return False
    elif value.removeprefix("-").isnumeric():
        return int(value)
    else:
        try:
            return float(value)
        except ValueError:
            pass # Not a float
    if not hideErrorMessage:
        KDS.Logging.AutoError(f"Value {value} cannot be parsed to any type!")
    return None

def AutoType3(value: str) -> Union[str, bool, int, float]:
    output = AutoType2(value, hideErrorMessage=True)
    if output == None:
        return value
    return output

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

def ToBlur(image: pygame.Surface, strength: int, alpha: bool = False) -> pygame.Surface:
    mode = "RGB" if not alpha else "RGBA"

    toBlur = pygame.image.tostring(image, mode)
    blurredImage = PIL_Image.frombytes(mode, image.get_size(), toBlur).filter(PIL_ImageFilter.GaussianBlur(radius=strength))
    blurredString = blurredImage.tobytes("raw", mode)
    blurredSurface: pygame.Surface = pygame.image.fromstring(blurredString, image.get_size(), mode)
    if alpha: blurredSurface = blurredSurface.convert_alpha()
    else: blurredSurface = blurredSurface.convert()
    return blurredSurface

class AspectMode(IntEnum):
    WidthControlsHeight = auto()
    HeightControlsWidth = auto()
    FitInTarget = auto()
    EnvelopeTarget = auto()
    EnvelopeTargetCrop = auto()

class ScalingMode(IntEnum):
    Quick = auto()
    Smooth = auto()

def AspectScale(image: pygame.Surface, targetSize: Sequence[int], aspectMode: AspectMode = AspectMode.FitInTarget, scalingMode: ScalingMode = ScalingMode.Quick) -> pygame.Surface:
    imageSize = image.get_size()
    if aspectMode == AspectMode.FitInTarget:
        scaling = min(targetSize[0] / imageSize[0], targetSize[1] / imageSize[1])
    elif aspectMode == AspectMode.EnvelopeTarget or aspectMode == AspectMode.EnvelopeTargetCrop:
        scaling = max(targetSize[0] / imageSize[0], targetSize[1] / imageSize[1])
    elif aspectMode == AspectMode.WidthControlsHeight:
        scaling = targetSize[0] / imageSize[0]
    elif aspectMode == AspectMode.HeightControlsWidth:
        scaling = targetSize[1] / imageSize[1]
    else:
        KDS.Logging.AutoError("Invalid Aspect Mode! Image will not be scaled.")
        scaling = 1.0

    if scalingMode == ScalingMode.Quick:
        scalingAlgorithm = pygame.transform.scale
    elif scalingMode == ScalingMode.Smooth:
        scalingAlgorithm = pygame.transform.smoothscale
    else:
        KDS.Logging.AutoError("Invalid Scaling Mode! Image will not be scaled.")
        scalingAlgorithm = lambda surf, _: surf.copy()

    scaled: pygame.Surface = scalingAlgorithm(image, (round(imageSize[0] * scaling), round(imageSize[1] * scaling)))

    if aspectMode == AspectMode.EnvelopeTargetCrop:
        scaled = cast(pygame.Surface, scaled.subsurface(scaled.get_width() // 2 - targetSize[0] // 2, scaled.get_height() // 2 - targetSize[1] // 2, targetSize[0], targetSize[1]))

    return scaled

def ToMultiplier(boolean: bool) -> Union[Literal[-1], Literal[1]]:
    """
    Returns:
        int: -1 if boolean else 1
    """
    return -1 if boolean else 1

def CorrelatedColorTemperatureToRGB(kelvin: float) -> Tuple[int, int, int]:
    """Color Correlated Color Temperature as an RGB color.

    Args:
        kelvin (float): The correlated color temperature. Is clamped to the range [1000, 40000].

    Returns:
        Tuple[int, int, int]: The output RGB
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
        hue (float): The hue of the color. range[0.0, 360.0]
        saturation (float): The saturation of the color.
        value (float): The value / brightness of the color.

    Returns:
        Tuple[float, float, float]: The converted RGB color.
    """
    return HSVToRGB2(hue / 360.0, saturation, value)

def HSVToRGB2(hue: float, saturation: float, value: float) -> Tuple[float, float, float]:
    """Converts an HSV color to RGB. This method does NOT automatically convert the hue to the range of 0-1.

    Args:
        hue (float): The hue of the color. range[0.0, 1.0]
        saturation (float): The saturation of the color.
        value (float): The value / brightness of the color.

    Returns:
        Tuple[float, float, float]: The converted RGB color.
    """
    # I have no idea what's happening here... I just stole this.

    if saturation == 0.0:
        value *= 255
        return (value, value, value)
    i = int(hue * 6.0)
    f = (hue * 6.0) - i
    p, q, t = int(255 * (value * (1.0 - saturation))), int(255 * (value * (1.0 - saturation * f))), int(255 * (value * (1.0 -saturation * (1.0 - f))))
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
        return (0.0, 0.0, 0.0)

def ToLines(text: str, font: pygame.font.Font, max_width: Union[int, float]) -> Tuple[str, ...]:
    if font.size(text)[0] < max_width:
        return tuple([text])

    # Freezes if word is longer than max_width...
    text_split = [" " + wrd for wrd in text.split(" ")]
    new_split = [text_split]
    while font.size( "".join(toTest := new_split[-1]).lstrip() )[0] > max_width:
        i = 0
        while font.size( "".join(toTest[:i]).lstrip() )[0] <= max_width:
            i += 1
            if i >= len(toTest):
                break

            if i == 1 and font.size( "".join(toTest[:i]).lstrip() )[0] > max_width:
                i += 1 # Added because minus one
                break # Fix for freezing if word is longer than max_width... But why I have that other comment I don't know... Maybe I've cocked something up.
        i -= 1 # Fixes getting the wrong index... Or that is what I remember this does...  I should've documented this more clearly...

        new_split.append(toTest[i:])
        new_split[-2] = toTest[:i]

    if len(new_split[-1]) < 1:
        del(new_split[-1])

    return tuple(["".join(new_split[i]).lstrip() for i in range(len(new_split))])

def ToRational(value: float) -> str:
    fraction, integer = KDS.Math.SplitFloat(value)
    integer = int(integer)
    marks = {0.0: "", 0.25: "+", 0.5: "½", 0.75: "-", 1.0: ""}
    closest = KDS.Math.Closest(fraction, marks.keys())
    mark = marks[closest]
    if closest > 0.5:
        integer += 1
    return f"{integer}{mark}"
