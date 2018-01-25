""""
Reed switch door example
"""

from machine import Pin

from . import HomieNode, Property


class Reed(HomieNode):

    def __init__(self, pin, interval=1):
        super().__init__(interval=interval)
        self.switch = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.last_status = None

    def __str__(self):
        status = 'open' if self.is_open() else 'closed'
        return 'Door is {}'.format(status)

    def get_node_id(self):
        return [b'door']

    def is_open(self, as_str=False):
        return True if self.switch.value() else False

    def get_properties(self):
        return (
            Property(b'door/$type', b'door', True),
            Property(b'door/$properties', b'open', True),
            Property(b'door/open/$settable', b'false', True),
            Property(b'door/open/$name', b'door', True),
            Property(b'door/open/$datatype', b'boolean', True),
            Property(b'door/open/$format', b'true,false', True)
        )

    def has_update(self):
        status = self.switch.value()
        if status != self.last_status:
            self.last_status = status
            return True
        return False

    def get_data(self):
        return (Property(b'door/open', self.is_open(), True),)
