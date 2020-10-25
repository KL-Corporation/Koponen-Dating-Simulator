import pygame
import KDS.Logging
import KDS.Colors
import KDS.Math
from inspect import currentframe
from PIL import Image as PIL_Image
from PIL import ImageFilter as PIL_ImageFilter

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

def ToBlur(image: pygame.Surface, strength: int):
    toBlur = pygame.image.tostring(image, "RGBA")
    blurredImage = PIL_Image.frombytes("RGBA", image.get_size(), toBlur).filter(PIL_ImageFilter.GaussianBlur(radius=strength))
    blurredString = blurredImage.tobytes("raw", "RGBA")
    blurredSurface = pygame.image.fromstring(blurredString, image.get_size(), "RGBA").convert()
    return blurredSurface

def AspectScale(image: pygame.Surface, size: tuple[int, int], horizontalOnly: bool = False, verticalOnly: bool = False):
    if (image.get_width() / image.get_height() > size[0] / size[1] or horizontalOnly) and not verticalOnly: scaling = size[0] / image.get_width()
    else: scaling = size[1] / image.get_height()
    return pygame.transform.scale(image, (int(image.get_width() * scaling), int(image.get_height() * scaling)))

def ToMultiplier(boolean: bool):
    return -1 if boolean else 1

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
                    
            new_split.append(toTest[i:])
            new_split[-2] = toTest[:i]
        if len(new_split[-1]) < 1: del(new_split[-1])
        return ["".join(new_split[i]) for i in range(len(new_split))]
    else: return text