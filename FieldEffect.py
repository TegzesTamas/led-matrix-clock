#!/usr/bin/env python

from random import randint

import time

from Drawer import Drawer
from common import limit, Effect

blur_kernel = [[1.0, 2.0, 1.0],
               [2.0, 5.0, 2.0],
               [1.0, 2.0, 1.0]]


class FieldEffect(Drawer):
    level = [[(randint(25, 255), randint(25, 255), randint(25, 255))
              for j in range(16)] for i in range(32)]
    target = [[px for px in row] for row in level]

    def draw(self, canvas, effect: Effect, brightness: int, color: dict):
        for x in range(32):
            for y in range(16):
                self.target[x][y] = tuple(
                    limit(color + randint(-50, 50), 25, brightness) for color in self.target[x][y]
                )

        for x in range(32):
            for y in range(16):
                neighbor_sum = (0, 0, 0)
                count = 0.0
                for i in range(max(x - 1, 0), min(x + 1, 32)):
                    for j in range(max(y - 1, 0), min(y + 1, 16)):
                        multiplier = blur_kernel[i - x + 1][j - y + 1]
                        neighbour = self.target[i][j]
                        neighbor_sum = tuple(
                            s + n * multiplier for s, n in zip(neighbor_sum, neighbour))
                        count = count + multiplier
                self.level[x][y] = tuple(limit(pc + limit(int(blur_c / count) - pc, -5, 5), 50, brightness)
                                         for blur_c, pc in zip(neighbor_sum, self.level[x][y])
                                         )
        for x, col in enumerate(self.level):
            for y, (r, g, b) in enumerate(col):
                canvas.SetPixel(x, y, r, g, b)
        return color
