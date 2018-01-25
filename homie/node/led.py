from machine import Pin

from . import HomieNode, Property


ONOFF = {b'off': 0, b'on': 1, 0: b'off', 1: b'on'}


class LED(HomieNode):

    def __init__(self, pin=2, interval=1):
        super().__init__(interval=interval)
        self.led = Pin(pin, Pin.OUT, value=0)
        self.subscribe = [b'led/power/set']
        self.has_new_update = True

    def __str__(self):
        return 'LED status = {}'.format(ONOFF[self.led.value()])

    def get_node_id(self):
        return [b'led']

    def get_properties(self):
        return (
            Property(b'led/$type', b'led', True),
            Property(b'led/$properties', b'power', True),
            Property(b'led/power/$settable', b'true', True),
            Property(b'led/power/$name', b'LED', True),
            Property(b'led/power/$datatype', b'string', True),
            Property(b'led/power/$format', b'on,off', True)
        )

    def callback(self, topic, message):
        if message == b'toggle':
            self.led.value(not self.led.value())
        else:
            self.led.value(ONOFF[message])

        self.has_new_update = True

    def has_update(self):
        if self.has_new_update is True:
            self.has_new_update = False
            return True
        return False

    def get_data(self):
        return (Property(b'led/power', ONOFF[self.led.value()]),)
