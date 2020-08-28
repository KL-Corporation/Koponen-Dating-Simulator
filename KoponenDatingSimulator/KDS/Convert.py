import pygame
import KDS.Logging
from inspect import currentframe, getframeinfo
def ToBool(value):
    """Converts a value to bool with these rules:
        1. String: [t, T, true and True = True] [f, F, false and False = False]
        2. Int: [1 = True] [0 = False]
        3. Float: [1.0 = True] [0.0 = False] (Will be rounded)
        4. Bool: [True = True] [False = False]
        5. Any Other: None
        
    Args:
        value: The value you want to convert.

    Returns:
        bool: The converted bool.
    """
    if isinstance(value, str):
        if value == "t" or value == "T" or value == "true" or value == "True":
            return True
        elif value == "f" or value == "F" or value == "false" or value == "False":
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
        return None
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.error, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ")\nValue is not a valid type.", True)

def ToAlpha(image, alpha: int):
    """Adds transparency to an image.

    Args:
        image (pygame.Surface): The image to be converted.
        alpha (int): The (0 - 255) alpha value the image will be converted to.

    Returns:
        pygame.Surface: The converted image.
    """
    image.set_alpha(alpha)
    return image

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