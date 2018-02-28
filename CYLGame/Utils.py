from __future__ import division


class OnlineMean:
    def __init__(self, i=0, mean=0):
        self.i = i
        self.mean = mean

    def __add__(self, other):
        new_obj = OnlineMean(self.i, self.mean)
        new_obj.add(other)
        return new_obj

    def add(self, n):
        n = float(n)
        if self.i == 0:
            self.mean = n
        else:
            self.mean = ((self.mean * self.i) / (self.i + 1)) + (n / (self.i + 1))
        self.i += 1
        return self.mean

    @property
    def floored_mean(self):
        return int(self.mean)
