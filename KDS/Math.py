from typing import Tuple
import KDS.Logging
import math
from inspect import currentframe

#region Value Manipulation
def Clamp(value: float, _min: float, _max: float) -> float:
    """Clamps the given value between the given minimum and maximum values. Returns the given value if it is within the min and max range.

    Args:
        value: The value to restrict inside the range defined by the min and max values.
        _min: The minimum value to compare against. (inclusive)
        _max: The maximum value to compare against. (inclusive)

    Returns:
        The result between the min and max values.
    """
    return max(_min, min(value, _max))

def Remap(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    Converts a value to another value within the given arguments.
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
#endregion

#region Distance
def getDistance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
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
        return 0
#endregion

#region Slope
def getSlope(p1: Tuple[int, int], p2: Tuple[int, int]):
    """
    Calculates slope of straight going trough two points
    """
    return (p2[1] - p1[1]) / (p2[0]- p1[0])

def getSlope2(angle): #Angle in degrees
    """
    Calculates slope of straight from angle
    """
    return math.tan(math.radians(angle)) 
#endregion

#region Angles
def getAngle(p1: Tuple[int, int], p2: Tuple[int, int]):
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

def getAngle2(p1: Tuple[int, int], p2: Tuple[int, int]):
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

def DeltaAngle(current: int or float, target: int or float):
    return ((target - current) + 180) % 360 - 180
#endregion

#region Interpolation
def Lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp(t, 0.0, 1.0)
    return a + ((b - a) * t)

def LerpUnclamped(a: float, b: float, t: float):
    """Linearly interpolates between a and b by t.

    The parameter t is not clamped.
    """
    return a + ((b - a) * t)

def SmoothStep(a: float, b: float, t: float):
    """Smoothly interpolates between a and b by t.
    
    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp(t, 0, 1)
    t = t * t * (3.0 - (2.0 * t))
    return Lerp(a, b, t)
#endregion