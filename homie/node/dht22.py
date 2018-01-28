"""
import utime
import settings

from homie.node.dht22 import DHT22
from homie import HomieDevice


homie = HomieDevice(settings)
homie.add_node(DHT22(pin=4))

homie.publish_properties()

while True:
    homie.publish_data()
    utime.sleep(1)
"""

import dht

from machine import Pin

from . import HomieNode, Property


class DHT22(HomieNode):

    def __init__(self, pin=4, interval=60):
        super(DHT22, self).__init__(interval=interval)
        self.dht22 = dht.DHT22(Pin(pin))
        self.temperature = 0
        self.humidity = 0

    def __str__(self):
        return 'DHT22: Temperature = {}, Humidity = {}'.format(
            self.temperature, self.humidity)

    def get_node_id(self):
        return [b'temperature', b'humidity']

    def get_properties(self):
        return (
            # temperature
            Property(b'temperature/$type', b'temperature', True),
            Property(b'temperature/$properties', b'degrees', True),
            Property(b'temperature/degrees/$settable', b'false', True),
            Property(b'temperature/degrees/$unit', b'°C', True),
            Property(b'temperature/degrees/$datatype', b'float', True),
            Property(b'temperature/degrees/$format', b'20.0:60', True),
            # humidity
            Property(b'humidity/$type', b'humidity', True),
            Property(b'humidity/$properties', b'percentage', True),
            Property(b'humidity/percentage/$settable', b'false', True),
            Property(b'humidity/percentage/$unit', b'%', True),
            Property(b'humidity/percentage/$datatype', b'float', True),
            Property(b'humidity/percentage/$format', b'0:100', True),
        )

    def update_data(self):
        self.dht22.measure()
        self.temperature = self.dht22.temperature()
        self.humidity = self.dht22.humidity()

    def get_data(self):
        return (
            Property(b'temperature/degrees', self.temperature, True),
            Property(b'humidity/percentage', self.humidity, True)
        )
