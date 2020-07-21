import KDS.Logging
from math import sqrt
from inspect import currentframe, getframeinfo

def getDistance(point1: tuple, point2: tuple): #Calculate distance between two points.
    try:
        q = point1[0] - point2[0]
        w = point1[1] - point1[-1]
        r = q ** 2 + w ** 2

        if r < 0:
            r = -r

        return sqrt(r)
    except Exception:
        frameinfo = getframeinfo(currentframe())
        KDS.Logging.Log(KDS.Logging.LogType.execption, "Error! (" + frameinfo.filename + ", " + str(frameinfo.lineno) + ")\nException: " + Exception, True)
        return (0, 0)