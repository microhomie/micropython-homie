from machine import Pin

from . import HomieNode, Property


class PIR(HomieNode):

    def __init__(self, pin=4, interval=1):
        super().__init__(interval=interval)
        self.pir = Pin(pin, Pin.IN, pull=Pin.PULL_UP)
        self.last_pir_state = 0

    def __str__(self):
        return 'Last PIR State = {}'.format(self.last_pir_state)

    def get_node_id(self):
        return [b'pir']

    def get_properties(self):
        return (
            Property(b'pir/$type', b'pir', True),
            Property(b'pir/$properties', b'motion', True),
            Property(b'pir/motion/$settable', b'false', True),
            Property(b'pir/motion/$datatype', b'boolean', True),
            Property(b'pir/motion/$format', b'true,false', True)
        )

    def has_update(self):
        new_pir_state = self.pir.value()
        if new_pir_state != self.last_pir_state:
            self.last_pir_state = new_pir_state
            return True
        return False

    def get_data(self):
        payload = 'true' if self.last_pir_state == 1 else 'false'
        return (Property(b'pir/motion', payload, True),)
