import math


class WindModel:

    def __init__(self, amplitude=1.0, frequency=0.5):
        self.A = amplitude
        self.w = frequency

    def force(self, t):
        return self.A * math.sin(self.w * t)