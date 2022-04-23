#!/usr/bin/env python

from random import randint

import time

from Drawer import Drawer
from common import flatten, limit, Effect


class PipesEffect(Drawer):
    level = [[(0, 0, 0) for j in range(16)] for i in range(32)]
    height = [randint(0, 4) for _ in range(16)]
    color = [(randint(50, 255), randint(50, 255), randint(50, 255))
             for _ in height]

    def draw(self, canvas, effect: Effect, brightness: int, color: dict):
        self.color = [tuple(limit(base + randint(-25, 25), 50, brightness)
                            for base in c) for c in self.color]
        self.height = [limit(old + randint(-1, 1), 1, 8)
                       for old in self.height]
        new_col = flatten([[c] * h for c, h in zip(self.color, self.height)])
        self.level = self.level[1:] + [new_col]
        for x, col in enumerate(self.level):
            for y, (r, g, b) in enumerate(col[:16]):
                canvas.SetPixel(x, y, r, g, b)
        return color
