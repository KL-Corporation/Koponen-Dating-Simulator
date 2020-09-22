import KDS.Logging
import math
from inspect import currentframe

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
        KDS.Logging.AutoError(e, currentframe())
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
    return (p2[1] - p1[1])/(p2[0]- p1[0])

def getSlope(angle): #Angle in degrees
    """
    Calculates slope of straight from angle
    """
    return math.tan(math.radians(angle)) 

def getAngle(p1: tuple, p2: tuple):
    """
    Calculates the angle between two vectors.
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

def Lerp(a: float, b: float, t: float):
    """
    Linearly interpolates between a and b by t.
    """
    return (t * a) + ((1 - t) * b)