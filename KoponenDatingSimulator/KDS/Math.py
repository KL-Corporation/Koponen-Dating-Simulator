import KDS.Logging
import math
from inspect import currentframe, getframeinfo

def getDistance(point1: tuple, point2: tuple):
    """
    Calculates the distance between two points.
    """
#    try:
    q = point1[0] - point2[0]
    w = point1[1] - point2[1]
    r = q ** 2 + w ** 2

    return math.sqrt(abs(r))
    """
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.execption, "Error! (" + str(frameinfo.filename) + ", " + str(frameinfo.lineno) + ")\nException: " + str(e), True)
        return (0, 0)
    """
def A_map(x, in_min, in_max, out_min, out_max):
    """
    Converts a value to another value within the given arguments.
    """
    try:
        rtn = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        return rtn
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.execption, "Error! (" + str(frameinfo.filename) + ", " + str(frameinfo.lineno) + ")\nException: " + str(e), True)
        return 0

def getAngle(p1: tuple, p2: tuple):
    """
    Calculates the angle between two vectors
    """
    try:
        q = p1[0] - p2[0]
        w = p1[1] - p2[1]
        if w == 0:
            w = 1
        r = q/w

        a = math.degrees(math.atan(r))
        a = 360 - a
        if a > 360:
            a = a -360

        return a
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.execption, "Error! (" + str(frameinfo.filename) + ", " + str(frameinfo.lineno) + ")\nException: " + str(e), True)
        return 0

def Lerp(a: float, b: float, t: float):
    """
    Linearly interpolates between a and b by t.
    """
    value = (t * a) + ((1 - t) * b)
    return value