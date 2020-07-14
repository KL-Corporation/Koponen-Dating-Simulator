from math import sqrt

def getDistance(point1: tuple, point2: tuple): #Calculate distance between two points.
    try:
        q = point1[0] - point2[0]
        w = point1[1] - point1[-1]
        r = q ** 2 + w ** 2

        if r < 0:
            r = -r

        return sqrt(r)

    except Exception:
        return (0,0)