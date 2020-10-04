import pygame
import KDS.Logging
from inspect import currentframe
    
def ToString(value, fallbackValue: str = "none"):
    try:
        return value
    except Exception:
        KDS.Logging.AutoError(f"Cannot convert {value} to string. With error: {e}", currentframe())
        return fallbackValue

def ToInt(value, fallbackValue: int = 0, roundFloat: bool = False, boolRange = (0, 1)) -> int:
    """Converts a value to int with these rules:
        1. String: [value = (int)value] [value = (int)value]
        2. Int: [value = value] [value = value]
        3. Float: [value = (int)value] [value = (int)value] (Optional rounding)
        4. Bool: [True = 1] [False = 0] (Can be modified with boolRange=(int, int))
        Will return fallbackValue if requirements are not met.
        
    Args:
        value: The value you want to convert.

    Returns:
        int: The converted int.
    """
    if isinstance(value, str):
        try:
            return int(value)
        except Exception as e:
            KDS.Logging.AutoError(f"Cannot convert {value} to int. With error: {e}", currentframe())
            return fallbackValue
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        if roundFloat:
            value = round(value)
        return int(value)
    elif isinstance(value, bool):
        if not value:
            return int(boolRange[0])
        else:
            return int(boolRange[1])
        
def ToFloat(value, fallbackValue: int = 0, roundFloat: bool = False, boolRange = (0.0, 1.0)) -> float:
    """Converts a value to float with these rules:
        1. String: [value = (float)value] [value = (float)value]
        2. Int: [value = (float)value] [value = (float)value]
        3. Float: [value = value] [value = value] (Optional rounding)
        4. Bool: [True = 1.0] [False = 0.0] (Can be modified with boolRange=(int[from], int[to]))
        Will return fallbackValue if requirements are not met.
        
    Args:
        value: The value you want to convert.

    Returns:
        float: The converted float.
    """
    if isinstance(value, str):
        try:
            return float(value)
        except Exception as e:
            KDS.Logging.AutoError(f"Cannot convert {value} to float. With error: {e}", currentframe())
            return fallbackValue
    elif isinstance(value, int):
        return float(value)
    elif isinstance(value, float):
        if roundFloat:
            value = round(value)
        return float(value)
    elif isinstance(value, bool):
        if not value:
            return float(boolRange[0])
        else:
            return float(boolRange[1])

def ToBool(value, fallbackValue: bool = False) -> bool:
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
        if value in ("t", "true"):
            return True
        elif value in ("f", "false"):
            return False
        else:
            KDS.Logging.AutoError(f"Cannot convert {value} to bool.", currentframe())
            return fallbackValue
    elif isinstance(value, int):
        if value > 0:
            return True
        else:
            return False
    elif isinstance(value, float):
        value = float(round(value))
        if value > 0.0:
            return True
        else:
            return False
    elif isinstance(value, bool):
        return value
    else:
        KDS.Logging.AutoError(f"Value {value} is not a valid type.", currentframe())
        return fallbackValue

def ToType(value, convertTo: str, fallbackValue = None, roundFloat: bool = False, boolRange = (0, 1)):
    if convertTo == "str" or convertTo == "string":
        return str(value)
    elif convertTo == "int":
        return ToInt(value, fallbackValue=fallbackValue, roundFloat=roundFloat, boolRange=boolRange)
    elif convertTo == "float":
        return ToFloat(value, fallbackValue=fallbackValue, roundFloat=roundFloat, boolRange=boolRange)
    elif convertTo == "bool":
        return ToBool(value, fallbackValue=fallbackValue)
    else:
        KDS.Logging.AutoError(f"Type {convertTo} is not a valid type.", currentframe())
        return fallbackValue

def ToAlpha(image: pygame.Surface, alpha: int or float):
    """Adds transparency to an image.

    Args:
        image (pygame.Surface): The image to be converted.
        alpha: The alpha value the image will be converted to.
            int: (0 - 255)
            float: (0.0 - 1.0)

    Returns:
        pygame.Surface: The converted image.
    """
    if isinstance(alpha, int):
        image.set_alpha(alpha)
        return image
    elif isinstance(alpha, float):
        image.set_alpha(int(alpha * 255))
        return image
    else:
        KDS.Logging.AutoError("Alpha is not a valid type.", currentframe())
        return None

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

def AspectScale(image: pygame.Surface, size: tuple, horizontalOnly: bool = False, verticalOnly: bool = False):
    if (image.get_width() / image.get_height() > size[0] / size[1] or horizontalOnly) and not verticalOnly:
        scaling = size[0] / image.get_width()
    else:
        scaling = size[1] / image.get_height()
    return pygame.transform.scale(image, (int(image.get_width() * scaling), int(image.get_height() * scaling)))