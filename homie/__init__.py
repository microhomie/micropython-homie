import sys
import utime
import machine
import network
import ubinascii

from collections import namedtuple

from umqtt.simple import MQTTClient


__version__ = b'0.1.0'


# Default config
CONFIG = {
    'mqtt': {
        'broker': '127.0.0.1',
        'port': 0,
        'user': None,
        'pass': None,
        'keepalive': 60,
        'ssl': False,
        'ssl_params': {},
        'base_topic': b'homie'
    },
    'device': {
        'id': ubinascii.hexlify(machine.unique_id()),
        'name': b'mydevice',
        'fwname': b'uhomie',
        'fwversion': __version__,
        'localip': bytes(network.WLAN(0).ifconfig()[0], 'utf-8'),
        'mac': ubinascii.hexlify(network.WLAN(0).config('mac'), ':'),
        'platform': bytes(sys.platform, 'utf-8'),
        'stats_interval': 60
    }
}


Property = namedtuple('Property', (
    'topic',
    'payload',
    'retain',
))


class HomieDevice:

    """ MicroPython implementation of the homie v2 convention. """

    def __init__(self, cfg=None):
        self.nodes = []
        self.node_ids = []
        self.topic_callbacks = {}

        # update config
        if cfg is not None:
            if 'mqtt' in cfg:
                CONFIG['mqtt'].update(cfg['mqtt'])
            if 'device' in cfg:
                CONFIG['device'].update(cfg['device'])

        self.start_time = utime.time()
        self.next_update = utime.time()
        self.stats_interval = CONFIG['device']['stats_interval']

        # base topic
        self.topic = b'/'.join((CONFIG['mqtt']['base_topic'],
                               CONFIG['device']['id']))

        self._umqtt_connect()

    def _umqtt_connect(self):
        # mqtt client
        self.mqtt = MQTTClient(
            CONFIG['device']['id'],
            CONFIG['mqtt']['broker'],
            port=CONFIG['mqtt']['port'],
            user=CONFIG['mqtt']['user'],
            password=CONFIG['mqtt']['pass'],
            keepalive=CONFIG['mqtt']['keepalive'],
            ssl=CONFIG['mqtt']['ssl'],
            ssl_params=CONFIG['mqtt']['ssl_params'])

        # set callback
        self.mqtt.set_callback(self.sub_cb)

        # set last will testament
        self.mqtt.set_last_will(self.topic + b'/$online', b'false',
                                retain=True, qos=1)

        self.mqtt.connect()

        # subscribe to device topics
        self.mqtt.subscribe(self.topic + b'/$stats/interval/set')
        self.mqtt.subscribe(self.topic + b'/$broadcast/#')

    def add_node(self, node):
        """add a node class of HomieNode to this device"""
        self.nodes.append(node)

        # add node_ids
        self.node_ids.extend(node.get_node_id())

        # subscribe node topics
        for topic in node.subscribe:
            topic = b'/'.join((self.topic, topic))
            self.mqtt.subscribe(topic)
            self.topic_callbacks[topic] = node.callback

    def sub_cb(self, topic, message):
        # device callbacks
        if b'$stats/interval/set' in topic:
            self.stats_interval = int(message.decode())
            self.publish(b'$stats/interval', self.stats_interval, True)
            self.next_update = utime.time() + self.stats_interval
        elif b'$broadcast/#' in topic:
            for node in self.nodes:
                node.broadcast(topic, message)
        else:
            # node property callbacks
            if topic in self.topic_callbacks:
                self.topic_callbacks[topic](topic, message)

    def publish(self, topic, payload, retain=True, qos=1):
        if not isinstance(payload, bytes):
            payload = bytes(str(payload), 'utf-8')
        t = b'/'.join((self.topic, topic))
        done = False
        while not done:
            try:
                self.mqtt.publish(t, payload, retain=retain, qos=qos)
                done = True
            except Exception as e:
                # some error during publishing
                done = False
                done_reconnect = False

                # tries to reconnect
                while not done_reconnect:
                    try:
                        self._umqtt_connect()
                        done_reconnect = True
                    except Exception as e:
                        done_reconnect = False
                        print(str(e))
                        utime.sleep(2)

    def publish_properties(self):
        """publish device and node properties"""
        # node properties
        properties = (
            Property(b'$homie', b'2.1.0', True),
            Property(b'$online', b'true', True),
            Property(b'$fw/name', CONFIG['device']['fwname'], True),
            Property(b'$fw/version', CONFIG['device']['fwversion'], True),
            Property(b'$implementation', CONFIG['device']['platform'], True),
            Property(b'$localip', CONFIG['device']['localip'], True),
            Property(b'$mac', CONFIG['device']['mac'], True),
            Property(b'$stats/interval', self.stats_interval, True),
            Property(b'$nodes', b','.join(self.node_ids), True)
        )

        # publish all properties
        for prop in properties:
            self.publish(*prop)

        # device properties
        for node in self.nodes:
            for prop in node.get_properties():
                self.publish(*prop)

    def publish_data(self):
        """publish node data if node has updates"""
        self.publish_device_stats()
        # node data
        for node in self.nodes:
            if node.has_update():
                for prop in node.get_data():
                    self.publish(*prop)

    def publish_device_stats(self):
        if utime.time() > self.next_update:
            # uptime
            uptime = utime.time() - self.start_time
            self.publish(b'$stats/uptime', uptime, True)
            # set next update
            self.next_update = utime.time() + self.stats_interval
