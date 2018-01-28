"""
import utime
import settings

from homie.node.simple import SimpleHomieNode
from homie import HomieDevice


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

from . import HomieNode, Property


class SimpleHomieNode(HomieNode):

    def __init__(self, node_type, node_property, interval=60):
        super().__init__(interval=interval)
        self.type = node_type
        self.property = node_property
        self.value = None

    def __str__(self):
        return "{}/{}: {}".format(self.type.decode(),
                                  self.property.decode(),
                                  self.value)

    def get_node_id(self):
        return [self.type]

    def broadcast_callback(self, payload):
        """nothing happens on a broadcast"""
        pass

    def get_data(self):
        """returns the data value"""
        return [
            Property(b'/'.join([self.type, self.property]), self.value, True)
        ]

    def update_data(self):
        """nothing happens on update data"""
        pass

    def get_properties(self):
        """no special properties"""
        return (
            Property(self.type + b'/$type', self.type, True),
            Property(self.type + b'/$properties', self.property, True),
        )
