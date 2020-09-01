import pygame
import KDS.Logging
from inspect import currentframe, getframeinfo
def ToBool(value):
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
            return None
    elif isinstance(value, int):
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            return None
    elif isinstance(value, float):
        value = float(round(value))
        if value == 1.0:
            return True
        elif value == 0.0:
            return False
        else:
            return None
    elif isinstance(value, bool):
        return value
    else:
        KDS.Logging.AutoError("Value is not a valid type.", getframeinfo(currentframe()))
        return None

def ToAlpha(image, alpha):
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
        KDS.Logging.AutoError("Alpha is not a valid type.", getframeinfo(currentframe()))
        return None

def ToGrayscale(image):
    """Converts an image to grayscale.

    Args:
        image (pygame.Surface): The image to be converted.

    Returns:
        pygame.Surface: The converted image.
    """
    arr = pygame.surfarray.pixels3d(image)
    arr = arr.dot([0.298, 0.587, 0.114])[:, :, None].repeat(3, axis=2)
    return pygame.surfarray.make_surface(arr)