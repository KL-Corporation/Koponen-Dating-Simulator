import pygame
import KDS.Logging
from inspect import currentframe, getframeinfo

def ToBool(value):
    """
    Converts a value to bool with these rules:
    1. String [t, T, true and True = True] [f, F, false and False = False]
    2. Int [1 = True] [0 = False]
    3. Float [1.0 = True] [0.0 = False]
    4. Bool [True = True] [False = False]
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
    """
    1. image: The image you want to convert.
    2. alpha: The alpha (0 - 255) you want the image to be.
    """
    image.set_alpha(alpha)
    return image

