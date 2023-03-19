#!/usr/bin/env python
import time
from typing import Final
import threading

from rgbmatrix import graphics

from FieldEffect import FieldEffect
from PipesEffect import PipesEffect

import paho.mqtt.client as mqtt
import uuid
import json

from ColorEffect import ColorEffect
from common import Effect, create_matrix

from argparse import ArgumentParser

ENTITY_ID: Final = format(uuid.getnode(), 'X')

BASE_TOPIC: Final = f'homeassistant/light/{ENTITY_ID}'

AVAIL_TOPIC: Final = f'{BASE_TOPIC}/available'
AVAIL_PAYLOAD_TRUE: Final = 'online'
AVAIL_PAYLOAD_FALSE: Final = 'offline'

CMD_TOPIC: Final = f'{BASE_TOPIC}/cmd'
STATE_TOPIC: Final = f'{BASE_TOPIC}/state'

ONOFF_PAYLOAD_TRUE = 'ON'
ONOFF_PAYLOAD_FALSE = 'OFF'


def onoff_str_to_bool(state: str) -> bool:
    if state == ONOFF_PAYLOAD_TRUE:
        return True
    elif state == ONOFF_PAYLOAD_FALSE:
        return False
    else:
        raise ValueError(f'Received unexpected state: {state} '
                         f'Was expecting {ONOFF_PAYLOAD_FALSE} or {ONOFF_PAYLOAD_TRUE}')
    pass


def bool_to_onoff_str(state: bool) -> str:
    return ONOFF_PAYLOAD_TRUE if state else ONOFF_PAYLOAD_FALSE


class LedMatrixClient:
    def __init__(
        self,
        mqtt_broker_host,
        font
    ):
        self.mqtt_broker_host = mqtt_broker_host
        self.font = font

    client = mqtt.Client()
    turned_on: bool = True
    brightness: int = 255
    effect: Effect = Effect.PIPES_CLOCK
    color: dict = {
        'r': 255,
        'g': 255,
        'b': 255
    }

    matrix = create_matrix()
    canvas = matrix.CreateFrameCanvas()

    lock = threading.Lock()

    def publish_available(self):
        self.client.publish(AVAIL_TOPIC, AVAIL_PAYLOAD_TRUE, retain=False)

    def publish_state(self):
        self.client.publish(STATE_TOPIC, retain=True, payload=json.dumps(
            {
                'brightness': self.brightness,
                'color_mode': 'rgb',
                'color': self.color,
                'effect': self.effect.name,
                'state': self.turned_on
            }
        ))

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print(f'Connected with result code {rc}')
        self.client.subscribe(CMD_TOPIC)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        print(
            f'received message on topic {msg.topic} with payload {str(msg.payload)}')
        if msg.topic == CMD_TOPIC:
            old_effect = self.effect
            command: dict = json.loads(msg.payload)
            self.lock.acquire()
            self.turned_on = onoff_str_to_bool(command.get(
                'state', bool_to_onoff_str(self.turned_on)))
            self.brightness = command.get('brightness', self.brightness)
            self.effect = Effect[command.get('effect', self.effect.name)]
            self.color = command.get('color', self.color)
            self.publish_state()
            self.publish_available()

            self.lock.release()

    def main(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.will_set(AVAIL_TOPIC, AVAIL_PAYLOAD_FALSE, retain=True)
        self.client.connect(self.mqtt_broker_host, 1883, 10)
        try:
            self.client.publish(
                f'{BASE_TOPIC}/config',
                retain=True,
                payload=json.dumps(
                    {
                        'name': 'LED Matrix',
                        'icon': 'mdi:clock-digital',
                        'schema': 'json',
                        'retain': True,
                        'availability': {
                            'payload_available': AVAIL_PAYLOAD_TRUE,
                            'payload_not_available': AVAIL_PAYLOAD_FALSE,
                            'topic': AVAIL_TOPIC
                        },
                        'brightness': True,
                        'color_mode': True,
                        'supported_color_modes': ['rgb'],
                        'effect': True,
                        'effect_list': [effect.name for effect in Effect],

                        'optimistic': True,

                        'command_topic': CMD_TOPIC,
                        'state_topic': STATE_TOPIC
                    }
                )
            )
            self.publish_state()
            self.publish_available()

            self.client.loop_start()

            font = graphics.Font()
            font.LoadFont(self.font)

            pipes_effect = PipesEffect()
            field_effect = FieldEffect()
            color_effect = ColorEffect()

            drawers = {
                Effect.DARK_CLOCK_FIX_COLOR: color_effect,
                Effect.DARK_CLOCK_SWEEPING_COLOR: color_effect,
                Effect.PIPES_CLOCK: pipes_effect,
                Effect.PIPES_NOCLOCK: pipes_effect,
                Effect.FIELD_CLOCK: field_effect,
                Effect.FIELD_NOCLOCK: field_effect,
                Effect.FIX_COLOR: color_effect,
                Effect.FIX_COLOR_CLOCK: color_effect,
                Effect.RANDOM_COLOR: color_effect,
                Effect.RANDOM_COLOR_CLOCK: color_effect
            }

            while True:
                self.lock.acquire()
                self.canvas.Clear()
                if self.turned_on:
                    drawer = drawers[self.effect]
                    if drawer:
                        self.color = drawer.draw(
                            self.canvas, self.effect, self.brightness, self.color)
                    if self.effect.draw_clock():
                        if self.effect.colored_background():
                            text_color = (0, 0, 0)
                        else:
                            text_color = (self.color['r'] * self.brightness / 255,
                                          self.color['g'] *
                                          self.brightness / 255,
                                          self.color['b'] * self.brightness / 255)

                        graphics.DrawText(self.canvas, font, 1, 12,
                                          graphics.Color(*text_color),
                                          time.strftime("%H:%M"))
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                self.publish_state()
                self.lock.release()
                self.publish_available()
                time.sleep(0.03)
        finally:
            self.client.publish(
                AVAIL_TOPIC,
                AVAIL_PAYLOAD_FALSE,
                retain=True
            )
            self.client.disconnect()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--mqtt_broker_host",
        help="Hostname of the MQTT broker to connect to",
        required=True
    )
    parser.add_argument(
        "-f", "--font_file",
        help="Font file to use to print the clock",
        required=True
    )
    args = parser.parse_args()
    LedMatrixClient(
        mqtt_broker_host=args.mqtt_broker_host,
        font=args.font_file
    ).main()
