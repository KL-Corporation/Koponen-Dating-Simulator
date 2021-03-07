from typing import Iterable, List, Tuple, TypeVar, Union
import math
import sys
import random
import enum

T = TypeVar("T")
Value = TypeVar("Value", int, float)

import KDS.Logging

#region Constants
PI = math.pi
EPSILON = sys.float_info.epsilon
INFINITY = float("inf")
NEGATIVEINFINITY = float("-inf")
DEG2RAD = (PI * 2) / 360
RAD2DEG = 1 / DEG2RAD
#endregion

#region Default Math Functions
def Tan(f: float) -> float: return math.tan(f)
def Atan(f: float) -> float: return math.atan(f)
def Atan2(x: float, y: float) -> float: return math.atan2(x, y)

def Sin(f: float) -> float: return math.sin(f)
def Asin(f: float) -> float: return math.asin(f)

def Cos(f: float) -> float: return math.cos(f)
def Acos(f: float) -> float: return math.acos(f)

def Ceil(f: float, digits: int = 0) -> float: power10: int = pow(10, digits); return math.ceil(f * power10) / power10
def CeilToInt(f: float) -> int: return math.ceil(f)
def Floor(f: float, digits: int = 0) -> float: power10: int = pow(10, digits); return math.floor(f * power10) / power10
def FloorToInt(f: float) -> int: return math.floor(f)

def Sqrt(f: float) -> float: return math.sqrt(f)
def Log(f: float) -> float: return math.log(f)

def Sign(f: Union[int, float]) -> int: return 1 if f >= 0 else -1

def Approximately(a: float, b: float) -> bool: return math.isclose(a, b)

def IsInfinity(f: float) -> bool: return math.isinf(f)
def IsPositiveInfinity(f: float) -> bool: return math.isinf(f) and f > 0
def IsNegativeInfinity(f: float) -> bool: return math.isinf(f) and f < 0
def IsNan(f: float) -> bool: return math.isnan(f)
#endregion

#region Bitwise
def Double(f: int) -> int:
    return f << 1

def Halve(f: int) -> int:
    return f >> 1
#endregion

#region Value Manipulation
def SplitFloat(f: float) -> Tuple[float, float]:
    """Returns the fractional and integer parts of \"f\" in a two-item tuple.

    Args:
        f (float): The value to split.

    Returns:
        Tuple[float, float]: (fraction, integer parts)
    """
    return math.modf(f)

def GetFraction(f: float) -> float:
    """Returns the fractional part of \"f\".

    Args:
        f (float): The value to get the fractional.

    Returns:
        float: The extracted fractional. Will be negative if \"f\" is negative.
    """
    return math.modf(f)[0]

def Clamp(value: Value, _min: Value, _max: Value) -> Value:
    """Clamps the given value between the given minimum and maximum values. Returns the given value if it is within the min and max range.

    Args:
        value: The value to restrict inside the range defined by the min and max values.
        _min: The minimum value to compare against. (inclusive)
        _max: The maximum value to compare against. (inclusive)

    Returns:
        The result between the min and max values.
    """
    return max(_min, min(value, _max))

def Clamp01(value: Value) -> Value:
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
    try:
        return (value - from1) / (0 - from1) * (1 - from2) + from2
    except ZeroDivisionError:
        KDS.Logging.AutoError("Division by zero!")
        return float("nan")

def Repeat(t: float, length: float) -> float:
    """Loops the value t, so that it is never larger than length and never smaller than 0.

    This is similar to the modulo operator but it works with floating point numbers. For example, using 3.0 for t and 2.5 for length, the result would be 0.5. With t = 5 and length = 2.5, the result would be 0.0. Note, however, that the behaviour is not defined for negative numbers as it is for the modulo operator.
    """
    return Clamp(t - Floor(t / length) * length, 0.0, length)
#endregion

#region Rounding
class MidpointRounding(enum.Enum):
    ToEven = 0
    AwayFromZero = 1
    ToZero = 2
    ToNegativeInfinity = 3
    ToPositiveInfinity = 4

def RoundCustom(value: float, digits: int = 0, mode: MidpointRounding = MidpointRounding.ToEven) -> float:
    """
    Round a number to a given precision in decimal digits and rounding mode.

    The return value is an integer if \"digits\" is 0. Otherwise the return value will be float. \"digits\" may be negative.
    """
    if math.isnan(value) or math.isinf(value):
        return value
    power10 = pow(10, digits) # 10 to the power of zero is one
    value *= power10
    if mode == MidpointRounding.AwayFromZero:
        fraction, value = math.modf(value)
        if abs(fraction) >= 0.5:
            value += Sign(fraction)
    elif mode == MidpointRounding.ToEven:
        value = round(value)
    else:
        raise ValueError("Invalid midpoint rounding mode!")
    value /= power10
    return value

def RoundCustomInt(value: float, mode: MidpointRounding = MidpointRounding.ToEven):
    return int(RoundCustom(value=value, digits=0, mode=mode))
#endregion

#region Area
def triangleArea(triangle: List[Tuple[int, int]]):
    return abs((triangle[0][0] * (triangle[1][1] - triangle[2][1]) + triangle[1][0] * (triangle[2][1] - triangle[0][1])  + triangle[2][0] * (triangle[0][1] - triangle[1][1])) / 2.0)
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

def LerpAngle(a: float, b: float, t: float) -> float:
    """Same as Lerp but makes sure the values interpolate correctly when they wrap around 360 degrees.

    The parameter t is clamped to the range [0, 1]. Variables a and b are assumed to be in degrees.
    """
    delta = Repeat(b - a, 360.0)
    if (delta > 180): delta -= 360
    return a + delta * Clamp01(t)

def SmoothStep(a: float, b: float, t: float) -> float:
    """Smoothly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp01(t)
    t = -2.0 * t * t * t + 3.0 * t * t
    return b * t + a * (1 - t)

def MoveTowards(current: float, target: float, maxDelta: float) -> float:
    """Moves a value current towards target.
    This is essentially the same as KDS.Math.Lerp but instead the function will ensure that the speed never exceeds maxDelta. Negative values of maxDelta pushes the value away from target.

    Args:
        current (float): The current value.
        target (float): The value to move towards.
        maxDelta (float): The maximum change that should be applied to the value.
    """
    if (abs(target - current) <= maxDelta): return target
    return current + Sign(target - current) * maxDelta

def MoveTowardsAngle(current: float, target: float, maxDelta: float) -> float:
    """Same as MoveTowards but makes sure the values interpolate correctly when they wrap around 360 degrees.
    Variables current and target are assumed to be in degrees. For optimization reasons, negative values of maxDelta are not supported and may cause oscillation. To push current away from a target angle, add 180 to that angle instead.
    """

    deltaAngle = DeltaAngle(current, target)
    if (-maxDelta < deltaAngle and deltaAngle < maxDelta): return target
    target = current + deltaAngle
    return MoveTowards(current, target, maxDelta)

def PingPong(t: float, length: float) -> float:
    t = Repeat(t, length * 2)
    return length - abs(t - length)
#endregion

#region Iterables
def Closest(value: float, iterable: Iterable[Value]) -> Value:
    COMPARISONFUNCTION = lambda k: abs(k - value)
    # key means that instead of finding the smallest value it will run the function "comparisonFunction"
    # and return the value that was associated with the smallest return value from the function
    return min(iterable, key=COMPARISONFUNCTION)

def Furthest(value: float, iterable: Iterable[Value]) -> Value:
    COMPARISONFUNCTION = lambda k: abs(k - value)
    return max(iterable, key=COMPARISONFUNCTION)
#endregion

#region Misc
def trianglePointIntersect(triangle: List[Tuple[int, int]], point: Tuple[int, int]) -> bool:
    A = triangleArea(triangle)
    A1 = triangleArea([point, triangle[1], triangle[2]])
    A2 = triangleArea([triangle[0], point, triangle[2]])
    A3 = triangleArea([triangle[0], triangle[1], point])
    return True if sum((A1, A2, A3)) == A else False
#endregion