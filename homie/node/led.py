from machine import Pin

from homie.node import HomieNode


ONOFF = {b'off': 0, b'on': 1, 0: b'off', 1: b'on'}


class LED(HomieNode):

    def __init__(self, pin=2, interval=1):
        super().__init__(interval=interval)
        self.pin = pin
        self.led = Pin(pin, Pin.OUT, value=0)
        self.updated = True

    def __repr__(self):
        return "LED(pin={!r}, interval={!r})".format(
            self.pin, self.interval
        )

    def __str__(self):
        return 'LED status = {}'.format(ONOFF[self.led.value()])

    @property
    def subscribe(self):
        yield b'led/power/set'

    def get_node_id(self):
        return [b'led']

    def get_properties(self):
        yield (b'led/$type', b'led')
        yield (b'led/$properties', b'power')
        yield (b'led/power/$settable', b'true')
        yield (b'led/power/$name', b'LED')
        yield (b'led/power/$datatype', b'string')
        yield (b'led/power/$format', b'on,off')

    def callback(self, topic, msg):
        if msg == b'toggle':
            self.led(not self.led.value())
        else:
            self.led(ONOFF[msg])

        self.updated = True

    def has_update(self):
        if self.updated is True:
            self.updated = False
            return True
        return False

    def get_data(self):
        yield (b'led/power', ONOFF[self.led()])
