#!/usr/bin/env python

from random import randint
import time

from Drawer import Drawer
from common import Effect, limit, normalize_brightness, set_brightness, sign


def random_color():
    return normalize_brightness(*tuple(randint(50, 255) for _ in range(3)))


class ColorEffect(Drawer):

    color_target = random_color()

    def draw(self, canvas, effect: Effect, brightness: int, color: dict):
        (nr, ng, nb) = (color['r'], color['g'], color['b'])
        (r, g, b) = set_brightness(nr, ng, nb, brightness)
        (tr, tg, tb) = set_brightness(*self.color_target, brightness)
        if effect.change_color():
            (rdiff, gdiff, bdiff) = tuple(target-base
                                          for base, target in zip((r, g, b), (tr, tg, tb)))
            if (abs(rdiff) + abs(gdiff) + abs(bdiff)) < 10:
                self.color_target = random_color()
            (r, g, b) = tuple(base + sign(diff)
                              for (base, diff) in zip((r, g, b), (rdiff, gdiff, bdiff)))
            (nr, ng, nb) = (normalize_brightness(r, g, b))
        if effect.colored_background():
            for x in range(32):
                for y in range(16):
                    canvas.SetPixel(x, y, r, g, b)
        return {
            'r': nr,
            'g': ng,
            'b': nb
        }
