from typing import List, SupportsFloat, Tuple
import KDS.Logging
import math
import sys

#region Constants
PI = math.pi
EPSILON = sys.float_info.epsilon
INFINITY = float("inf")
NEGATIVEINFINITY = float("-inf")
DEG2RAD = (PI * 2) / 360
RAD2DEG = 360 / (PI * 2)
#endregion

#region Default Math Functions
def Tan(f: SupportsFloat) -> float: return math.tan(f)
def Atan(f: SupportsFloat) -> float: return math.atan(f)
def Atan2(x: SupportsFloat, y: SupportsFloat) -> float: return math.atan2(x, y)

def Sin(f: SupportsFloat) -> float: return math.sin(f)
def Asin(f: SupportsFloat) -> float: return math.asin(f)

def Cos(f: SupportsFloat) -> float: return math.cos(f)
def Acos(f: SupportsFloat) -> float: return math.acos(f)

def Ceil(f: SupportsFloat) -> int: return math.ceil(f)
def Floor(f: SupportsFloat) -> int: return math.floor(f)

def Sqrt(f: SupportsFloat) -> float: return math.sqrt(f)
def Pow(f: SupportsFloat, p: SupportsFloat) -> float: return math.pow(f, p)
def Log(f: SupportsFloat) -> float: return math.log(f)
#endregion

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

def Clamp01(value: float) -> float:
    return max(0, min(value, 1))

def Remap(value: float, from1: float, to1: float, from2: float, to2: float) -> float:
    """
    Converts a value to another value within the given arguments.
    """
    return (value - from1) / (to1 - from1) * (to2 - from2) + from2

def Remap01(value: float, from1: float, from2: float) -> float:
    """
    Converts a value to another value within the given arguments.
    """
    return (value - from1) / (0 - from1) * (1 - from2) + from2
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
        return Sqrt(r)
    except Exception as e:
        KDS.Logging.AutoError(e)
        return 0
#endregion

#region Slope
def getSlope(p1: Tuple[int, int], p2: Tuple[int, int]):
    """
    Calculates slope of straight going trough two points
    """
    return (p2[1] - p1[1]) / (p2[0]- p1[0])

def getSlope2(angle: float) -> float: #Angle in degrees
    """
    Calculates slope of straight from angle
    """
    return Tan(angle * DEG2RAD) 
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

        a = Atan(r) * RAD2DEG
        #a = 360 - a
        #while a >= 360:
        #    a = a - 360

        return a
    except Exception as e:
        KDS.Logging.AutoError(e)
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


    return Atan2(dy, dx) * RAD2DEG

def DeltaAngle(current: float, target: float):
    return ((target - current) + 180) % 360 - 180
#endregion

#region Interpolation
def Lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    return a + (b - a) * Clamp01(t)

def LerpUnclamped(a: float, b: float, t: float) -> float:
    """Linearly interpolates between a and b by t.

    The parameter t is not clamped.
    """
    return a + (b - a) * t

def SmoothStep(a: float, b: float, t: float) -> float:
    """Smoothly interpolates between a and b by t.
    
    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp01(t)
    t = -2.0 * t * t * t + 3.0 * t * t
    return b * t + a * (1 - t)
#endregion
