import pygame
import KDS.Logging
from inspect import currentframe

def ToBool(value, fallbackValue: bool = False):
    """Converts a value to bool with these rules:
        1. String: [t, true = True] [f, false = False] (Not case dependent)
        2. Int: [1 = True] [0 = False]
        3. Float: [1.0 = True] [0.0 = False] (Will be rounded)
        4. Bool: [True = True] [False = False]
        Will return None if requirements are not met.
        
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
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            KDS.Logging.AutoError(f"Cannot convert {value} to bool.", currentframe())
            return fallbackValue
    elif isinstance(value, float):
        value = float(round(value))
        if value == 1.0:
            return True
        elif value == 0.0:
            return False
        else:
            KDS.Logging.AutoError(f"Cannot convert {value} to bool.", currentframe())
            return fallbackValue
    elif isinstance(value, bool):
        return value
    else:
        KDS.Logging.AutoError(f"Value {value} is not a valid type.", currentframe())
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

def AspectScale(image: pygame.Surface, size: tuple):
    if image.get_width() / image.get_height() > size[0] / size[1]:
        scaling = size[0] / image.get_width()
    else:
        scaling = size[1] / image.get_height()
    return pygame.transform.scale(image, (int(image.get_width() * scaling), int(image.get_height() * scaling)))