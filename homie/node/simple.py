"""
import utime
import settings

from homie.node.simple import SimpleHomieNode
from homie.device import HomieDevice


homie = HomieDevice(settings)

n = SimpleHomieNode(node_type=b'dummy', node_property=b'value', interval=5)
n.value = 17

homie.add_node(n)
homie.publish_properties()

while True:
    homie.publish_data()
    n.value = utime.time()
    print(n)
    utime.sleep(1)
"""

from homie.node import HomieNode


class SimpleHomieNode(HomieNode):
    def __init__(self, type, property, interval=60):
        super().__init__(interval=interval)
        self.type = type
        self.property = property
        self.value = None

    def __repr__(self):
        return "SimpleHomieNode(type={!r}, property={!r}, interval={!r})".format(
            self.type, self.property, self.interval
        )

    def __str__(self):
        return "{}/{}: {}".format(
            self.type.decode(), self.property.decode(), self.value
        )

    def get_node_id(self):
        return [self.type]

    def broadcast_callback(self, payload):
        """nothing happens on a broadcast"""
        pass

    def get_data(self):
        """returns the data value"""
        yield (b"{}/{}".format(self.type, self.property), self.value)

    def update_data(self):
        """nothing happens on update data"""
        pass

    def get_properties(self):
        """no special properties"""
        _type = self.type
        yield (_type + b"/$type", _type)
        yield (_type + b"/$properties", self.property)
