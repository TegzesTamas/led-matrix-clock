from enum import Enum, auto
from typing import Tuple

from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions


def brightness(r: int, g: int, b: int) -> int:
    return max(r, g, b)


def normalize_brightness(r: int, g: int, b: int) -> Tuple[int, int, int]:
    bright = brightness(r, g, b)
    return (
        r * 255 / bright,
        g * 255 / bright,
        b * 255 / bright
    )


def set_brightness(r: int, g: int, b: int, bright: int) -> Tuple[int, int, int]:
    curr_bright = brightness(r, g, b)
    return (
        r * bright / curr_bright,
        g * bright / curr_bright,
        b * bright / curr_bright
    )


def create_matrix() -> RGBMatrix:
    options = RGBMatrixOptions()
    options.hardware_mapping = 'adafruit-hat-pwm'
    options.rows = 16
    options.cols = 32
    options.chain_length = 1
    options.parallel = 1
    options.multiplexing = 0
    options.row_address_type = 0
    options.pwm_bits = 11
    options.brightness = 100
    options.pwm_lsb_nanoseconds = 200
    options.led_rgb_sequence = 'RGB'
    options.pixel_mapper_config = ''
    options.panel_type = ''
    options.show_refresh_rate = 1
    options.drop_privileges = False
    options.gpio_slowdown = 4
    return RGBMatrix(options=options)


def limit(num, bot, top):
    if num > top:
        return top
    if num < bot:
        return bot
    return num


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def sign(a):
    if a == 0:
        return 0
    elif a > 0:
        return 1
    else:
        return -1


class Effect(Enum):
    DARK_CLOCK_FIX_COLOR = auto()
    DARK_CLOCK_SWEEPING_COLOR = auto()
    PIPES_CLOCK = auto()
    PIPES_NOCLOCK = auto()
    FIELD_CLOCK = auto()
    FIELD_NOCLOCK = auto()
    FIX_COLOR = auto()
    FIX_COLOR_CLOCK = auto()
    RANDOM_COLOR = auto()
    RANDOM_COLOR_CLOCK = auto()

    def draw_clock(self):
        return (
            self is Effect.DARK_CLOCK_FIX_COLOR or
            self is Effect.DARK_CLOCK_SWEEPING_COLOR or
            self is Effect.PIPES_CLOCK or
            self is Effect.FIELD_CLOCK or
            self is Effect.FIX_COLOR_CLOCK or
            self is Effect.RANDOM_COLOR_CLOCK
        )

    def colored_background(self):
        return (
            self is Effect.PIPES_CLOCK or
            self is Effect.PIPES_NOCLOCK or
            self is Effect.FIELD_CLOCK or
            self is Effect.FIELD_NOCLOCK or
            self is Effect.FIX_COLOR or
            self is Effect.FIX_COLOR_CLOCK or
            self is Effect.RANDOM_COLOR or
            self is Effect.RANDOM_COLOR_CLOCK
        )

    def change_color(self):
        return (
            self is Effect.DARK_CLOCK_SWEEPING_COLOR or
            self is Effect.RANDOM_COLOR or
            self is Effect.RANDOM_COLOR_CLOCK
        )
