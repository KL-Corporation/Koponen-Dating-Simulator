from typing import Iterable, List, Sequence, SupportsFloat, Tuple, TypeVar, Union, cast
import sys
import enum

from math import tan as Tan
from math import atan as Atan
from math import atan2 as Atan2
from math import sin as Sin
from math import asin as Asin
from math import cos as Cos
from math import acos as Acos
from math import ceil as CeilToInt
from math import floor as FloorToInt
from math import sqrt as Sqrt
from math import log as Log
from math import isclose as Approximately
from math import isinf as IsInfinity
from math import isnan as IsNan
from math import modf as SplitFloat
from math import pi as PI

T = TypeVar("T")
Value = TypeVar("Value", int, float)

import KDS.Logging

#region Constants
EPSILON = sys.float_info.epsilon
INFINITY = float("inf")
NEGATIVEINFINITY = float("-inf")
NAN = float("nan")
DEG2RAD = (PI * 2) / 360
RAD2DEG = 1 / DEG2RAD
MAXVALUE = sys.maxsize
MINVALUE = -MAXVALUE - 1
#endregion

#region Default Math Functions
def Ceil(f: float, digits: int = 0) -> float:
    power10: int = pow(10, digits) # Anything to the power of zero is one.
    return CeilToInt(f * power10) / power10

def Floor(f: float, digits: int = 0) -> float:
    power10: int = pow(10, digits) # Anything to the power of zero is one.
    return FloorToInt(f * power10) / power10

def Sign(f: Union[int, float]) -> int: return bool(f > 0) - bool(f < 0) # Bruh this is like 9000 IQ code

def IsPositiveInfinity(f: float) -> bool: return IsInfinity(f) and f > 0 # faster than f == INFINITY
def IsNegativeInfinity(f: float) -> bool: return IsInfinity(f) and f < 0 # faster than f == NEGATIVEINFINITY
#endregion

#region Value Manipulation
def GetFraction(__x: SupportsFloat) -> float:
    """Returns the fractional part of ``__x``.

    Args:
        __x (float): The value to get the fractional.

    Returns:
        float: The extracted fractional. Will be negative if ``__x`` is negative.
    """
    return SplitFloat(__x)[0]

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
    return Clamp(value, 0, 1) # Should be fine without being the same type...? # type: ignore
                              # Not casting, because it will call two extra functions and slow the code down.

def Remap(value: float, from1: float, to1: float, from2: float, to2: float) -> float:
    """
    Converts a value to another value within the given arguments.
    """
    try:
        return (value - from1) / (to1 - from1) * (to2 - from2) + from2
    except ZeroDivisionError:
        KDS.Logging.AutoError(f"Division by zero! Params: (value: {value}, from1: {from1}, to1: {to1}, from2: {from2}, to2: {to2})")
        return NAN

def Remap01(value: float, from1: float, from2: float) -> float:
    """
    Converts a value to another value within the given arguments.
    """
    return Remap(value, from1, 0.0, from2, 1.0)
#endregion

#region Rounding
class MidpointRounding(enum.Enum):
    ToEven = 0
    AwayFromZero = 1

def RoundCustom(value: float, digits: int = 0, mode: MidpointRounding = MidpointRounding.ToEven) -> float:
    """
    Round a number to a given precision in decimal digits and rounding mode.

    The return value is a float. \"digits\" may be negative.
    """
    if (IsNan(value) or IsInfinity(value)) and digits != 0:
        return value
    power10: int = pow(10, digits) # 10 to the power of zero is one
    value *= power10
    if mode == MidpointRounding.AwayFromZero:
        fraction, value = SplitFloat(value)
        if abs(fraction) >= 0.5:
            value += Sign(fraction)
    elif mode == MidpointRounding.ToEven:
        value = round(value) # Python's builtin round rounds to even
    else:
        raise ValueError("Invalid midpoint rounding mode!")
    value /= power10
    return value

def RoundCustomInt(value: float, mode: MidpointRounding = MidpointRounding.ToEven) -> int:
    """
    Same as RoundCustom, but converts the returned value to an int.
    """
    return int(RoundCustom(value=value, digits=0, mode=mode))
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
def GetAngle(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """Calculates the angle between two vectors faster.

    Args:
        p1 (tuple): First vector
        p2 (tuple): Second vector

    Returns:
        float: The angle between the vectors
    """
    try:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return Atan2(dy, dx) * RAD2DEG
    except Exception as e:
        KDS.Logging.AutoError(e)
        return NAN

def GetAngle2(p1: Tuple[int, int], p2: Tuple[int, int]):
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
            return 0.0

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

def LerpColor(a: Sequence[int], b: Sequence[int], t: float) -> Tuple[int, int, int]:
    """Same as Lerp, but lerps color sequences instead.

    The parameter t is clamped to the range [0, 1]. Variables a and b are assumed to be sequences of size three with integers in range [0, 255].
    """
    _r = Lerp(a[0], b[0], t)
    _g = Lerp(a[1], b[1], t)
    _b = Lerp(a[2], b[2], t)
    return (round(_r), round(_g), round(_b))

# def LerpAngle(a: float, b: float, t: float) -> float:
#     """Same as Lerp but makes sure the values interpolate correctly when they wrap around 360 degrees.
#
#     The parameter t is clamped to the range [0, 1]. Variables a and b are assumed to be in degrees.
#     """
#     delta = Repeat(b - a, 360.0)
#     if (delta > 180): delta -= 360
#     return a + delta * Clamp01(t)

def SmoothStep(a: float, b: float, t: float) -> float:
    """Smoothly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    t = Clamp01(t)
    t = -2.0 * t * t * t + 3.0 * t * t
    return b * t + a * (1 - t)

def MoveTowards(current: float, target: float, maxDelta: float) -> float:
    """Moves a value current towards target.
    This is essentially the same as Lerp, but instead the function will ensure that the speed never exceeds maxDelta. Negative values of maxDelta pushes the value away from target.

    Args:
        current (float): The current value.
        target (float): The value to move towards.
        maxDelta (float): The maximum change that should be applied to the value.
    """
    if abs(target - current) <= maxDelta: return target
    return current + Sign(target - current) * maxDelta

def MoveTowardsAngle(current: float, target: float, maxDelta: float) -> float:
    """Same as MoveTowards but makes sure the values interpolate correctly when they wrap around 360 degrees.
    Variables current and target are assumed to be in degrees. For optimization reasons, negative values of maxDelta are not supported and may cause oscillation. To push current away from a target angle, add 180 to that angle instead.
    """

    deltaAngle = DeltaAngle(current, target)
    if (-maxDelta < deltaAngle and deltaAngle < maxDelta): return target
    target = current + deltaAngle
    return MoveTowards(current, target, maxDelta)

# def PingPong(t: float, length: float) -> float:
#     t = Repeat(t, length * 2)
#     return length - abs(t - length)
#endregion

#region Iterables
def Closest(value: float, iterable: Iterable[Value]) -> Value:
    COMPARISONFUNCTION = lambda k: abs(k - value)
    # key means that instead of finding the smallest value it will run the function "COMPARISONFUNCTION"
    # and return the value that was associated with the smallest return value from the function
    return min(iterable, key=COMPARISONFUNCTION)

def Furthest(value: float, iterable: Iterable[Value]) -> Value:
    COMPARISONFUNCTION = lambda k: abs(k - value)
    return max(iterable, key=COMPARISONFUNCTION)
#endregion

#region Scrapped

# def TriangleCollidePoint(triangle: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], point: Tuple[int, int]) -> bool:
#     A = GetTriangleArea(triangle)
#     A1 = GetTriangleArea((point, triangle[1], triangle[2]))
#     A2 = GetTriangleArea((triangle[0], point, triangle[2]))
#     A3 = GetTriangleArea((triangle[0], triangle[1], point))
#     return True if sum((A1, A2, A3)) == A else False

# def GetTriangleArea(triangle: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]):
#     return abs((triangle[0][0] * (triangle[1][1] - triangle[2][1]) + triangle[1][0] * (triangle[2][1] - triangle[0][1])  + triangle[2][0] * (triangle[0][1] - triangle[1][1])) / 2.0)
#                 # WTF is happening?

# def getAngle(p1: Tuple[int, int], p2: Tuple[int, int]):
#     """Calculates the angle between two vectors.
#
#     Args:
#         p1 (tuple): First vector
#         p2 (tuple): Secod vector
#
#     Returns:
#         float: The angle between the vectors
#     """
#     try:
#         q = p1[0] - p2[0]
#         w = p1[1] - p2[1]
#         if w == 0:
#             w = 1
#         r = q / w
#
#         a = Atan(r) * RAD2DEG
#         #a = 360 - a
#         #while a >= 360:
#         #    a = a - 360
#
#         return a
#     except Exception as e:
#         KDS.Logging.AutoError(e)
#         return 0

#endregion
