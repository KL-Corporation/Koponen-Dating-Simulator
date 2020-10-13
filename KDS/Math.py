import KDS.Logging
import math
from inspect import currentframe

def Clamp(value: int or float, _min: int or float, _max: int or float):
    return max(_min, min(value, _max))

def getDistance(point1: tuple, point2: tuple):
    """
    Calculates the distance between two points.
    """
    try:
        q = point1[0] - point2[0]
        w = point1[1] - point2[1]
        r = q ** 2 + w ** 2
        return math.sqrt(abs(r))
    except Exception as e:
        KDS.Logging.AutoError(e, currentframe())
        return (0, 0)
        
def A_map(x, in_min, in_max, out_min, out_max):
    """
    Converts a value to another value within the given arguments.
    """
    try:
        rtn = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        return rtn
    except Exception as e:
        KDS.Logging.AutoError(str(e), currentframe())
        return 0

def toPositive(value):
    if value > 0:
        return value
    elif value < 0:
        return -value
    else:
        return 0

def getSlope(p1: tuple, p2: tuple):
    """
    Calculates slope of straight going trough two points
    """
    return (p2[1] - p1[1]) / (p2[0]- p1[0])

def getSlope2(angle): #Angle in degrees
    """
    Calculates slope of straight from angle
    """
    return math.tan(math.radians(angle)) 

def getAngle(p1: tuple, p2: tuple):
    """Calculates the angle between two vectors.

    Args:
        p1 (tuple): First vector
        p2 (tuple): Secod vector

    Returns:
        float: The angle between the vectors
    """
    try:
        q = p1[0] - p2[0]
        w = p1[1] - p2[1]
        if w == 0:
            w = 1
        r = q / w

        a = math.degrees(math.atan(r))
        #a = 360 - a
        #while a >= 360:
        #    a = a - 360

        return a
    except Exception as e:
        KDS.Logging.AutoError(e, currentframe())
        return 0

def getAngle2(p1, p2):
    """Calculates the angle between two vectors faster, but without error handling.

    Args:
        p1 (tuple): First vector
        p2 (tuple): Second vector

    Returns:
        float: The angle between the vectors
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]


    return math.degrees(math.atan2(dy,dx))

def Lerp(a: float, b: float, t: float):
    """Linearly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp(t, 0.0, 1.0)
    return a + ((b - a) * t)

def SmoothStep(a: float, b: float, t: float):
    """Smoothly interpolates between a and b by t.
    
    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp(t, 0, 1)
    t = t * t * (3.0 - (2.0 * t))
    return Lerp(a, b, t)
