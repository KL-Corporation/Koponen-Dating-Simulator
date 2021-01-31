import math
from matplotlib import pyplot as plt

Linear = lambda t: t
EaseInSine = lambda t: 1 - math.cos(t * math.pi * 0.5)
EaseOutSine = lambda t: math.sin(t * math.pi * 0.5)
EaseInOutSine = lambda t: -(math.cos(math.pi * t) - 1) * 0.5
EaseInCubic = lambda t: t * t * t
EaseOutCubic = lambda t: 1 - pow(1 - t, 3)
EaseInOutCubic = lambda t: 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) * 0.5
EaseInQuint = lambda t: t * t * t * t * t
EaseOutQuint = lambda t: 1 - pow(1 - t, 5)
EaseInOutQuint = lambda t: 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) * 0.5
EaseInCirc = lambda t: 1 - KDS.Math.Sqrt(1 - pow(t, 2))
EaseOutCirc = lambda t: KDS.Math.Sqrt(1 - pow(t - 1, 2))
EaseInOutCirc = lambda t: (1 - KDS.Math.Sqrt(1 - pow(2 * t, 2))) * 0.5 if t < 0.5 else (KDS.Math.Sqrt(1 - pow(-2 * t + 2, 2)) + 1) * 0.5
EaseInElastic = lambda t: 0 if math.isclose(t, 0) else (1 if math.isclose(t, 1) else -pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * ((2 * math.pi) / 3)))
EaseOutElastic = lambda t: 0 if math.isclose(t, 0) else (1 if math.isclose(t, 1) else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * ((2 * math.pi) / 3)) + 1)
EaseInOutElastic = lambda t: 0 if math.isclose(t, 0) else (1 if math.isclose(t, 1) else (-(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) * 0.5 if t < 0.5 else (pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) * 0.5 + 1)) #Yeah... I have no idea what's happening here...
EaseInQuad = lambda t: t * t
EaseOutQuad = lambda t: 1 - (1 - t) * (1 - t)
EaseInOutQuad = lambda t: 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) * 0.5
EaseInQuart = lambda t: t * t * t * t
EaseOutQuart = lambda t: 1 - pow(1 - t, 4)
EaseInOutQuart = lambda t: 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) * 0.5
EaseInExpo = lambda t: 0 if math.isclose(t, 0) else pow(2, 10 * t - 10)
EaseOutExpo = lambda t: 1 if math.isclose(t, 1) else 1 - pow(2, -10 * t)
EaseInOutExpo = lambda t: 0 if math.isclose(t, 0) else (1 if math.isclose(t, 1) else (pow(2, 20 * t - 10) * 0.5 if t < 0.5 else (2 - pow(2, -20 * t + 10)) * 0.5))
EaseInBack = lambda t: 2.70158 * t * t * t - 1.70158 * t * t
EaseOutBack = lambda t: 1 + 2.70158 * pow(t - 1, 3) + 1.70158 * pow(t - 1, 2)
EaseInOutBack = lambda t: (pow(2 * t, 2) * ((2.5949095 + 1) * 2 * t - 2.5949095)) * 0.5 if t < 0.5 else (pow(2 * t - 2, 2) * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) * 0.5
EaseInBounce = lambda t: 1 - EaseOutBounce(1 - t)
EaseOutBounce = lambda t: 7.5625 * t * t if t < 1 / 2.75 else (7.5625 * (t - 1.5 / 2.75) * t + 0.75 if t < 2 / 2.75 else (7.5625 * (t - 2.25 / 2.75) * t + 0.9375 if t < 2.5 / 2.75 else 7.5625 * (t - 2.625 / 2.75) * t + 0.984375))
EaseInOutBounce = lambda t: (1 - EaseOutBounce(1 - 2 * t)) * 0.5 if t < 0.5 else (1 + EaseOutBounce(2 * t - 1)) * 0.5
SmoothStep = lambda t: t * t * (3 - (2 * t))
SmootherStep = lambda t: t * t * t * (t * ((6 * t) - 15) + 10)

fig, axs = plt.subplots(2)


_max = 100000
A = SmoothStep
B = EaseInOutSine

xA = []
yA = []
xB = []
yB = []
for i in range(0, _max + 1):
    v = i / _max
    xA.append(v)
    yA.append(A(v))
    
    xB.append(v)
    yB.append(B(v))
    
plt.plot(xA, yA, label="Conv A")
plt.plot(xB, yB, label="Conv B")
plt.legend()
plt.show()