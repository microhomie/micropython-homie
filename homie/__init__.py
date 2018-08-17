import sys
import utime
from ucollections import namedtuple
from umqtt.simple import MQTTClient

from homie import utils

__version__ = b'0.3.0'


RETRY_DELAY = 10


Property = namedtuple('Property', (
    'topic',
    'payload',
    'retain',
))


class HomieDevice:

    """MicroPython implementation of the Homie MQTT convention for IoT."""

    def __init__(self, settings):
        self.errors = 0
        self.settings = settings

        self.nodes = []
        self.node_ids = []
        self.topic_callbacks = {}

        self.start_time = utime.time()
        self.next_update = utime.time()
        self.stats_interval = self.settings.DEVICE_STATS_INTERVAL

        # base topic
        self.topic = b'/'.join((self.settings.MQTT_BASE_TOPIC,
                                self.settings.DEVICE_ID))

        # setup wifi
        utils.setup_network()
        utils.wifi_connect()

        try:
            self._umqtt_connect()
        except Exception:
            print('ERROR: can not connect to MQTT')
            # self.mqtt.publish = lambda topic, payload, retain, qos: None

    def _umqtt_connect(self):
        # mqtt client
        mqtt = MQTTClient(
            self.settings.DEVICE_ID,
            self.settings.MQTT_BROKER,
            port=self.settings.MQTT_PORT,
            user=self.settings.MQTT_USERNAME,
            password=self.settings.MQTT_PASSWORD,
            keepalive=self.settings.MQTT_KEEPALIVE,
            ssl=self.settings.MQTT_SSL,
            ssl_params=self.settings.MQTT_SSL_PARAMS)

        mqtt.DEBUG = True

        # set callback
        mqtt.set_callback(self.sub_cb)

        # set last will testament
        mqtt.set_last_will(self.topic + b'/$online', b'false',
                           retain=True, qos=1)

        mqtt.connect()

        # subscribe to device topics
        mqtt.subscribe(self.topic + b'/$stats/interval/set')
        mqtt.subscribe(self.topic + b'/$broadcast/#')

        self.mqtt = mqtt

    def add_node(self, node):
        """add a node class of HomieNode to this device"""
        self.nodes.append(node)

        # add node_ids
        try:
            self.node_ids.extend(node.get_node_id())
        except NotImplementedError:
            raise
        except Exception:
            print('ERROR: getting Node')

        # subscribe node topics
        for topic in node.subscribe:
            topic = b'/'.join((self.topic, topic))
            self.mqtt.subscribe(topic)
            self.topic_callbacks[topic] = node.callback

    def sub_cb(self, topic, message):
        # device callbacks
        print('MQTT SUBSCRIBE: {} --> {}'.format(topic, message))

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
        # try wifi reconnect in case it lost connection
        utils.wifi_connect()

        if not isinstance(payload, bytes):
            payload = bytes(str(payload), 'utf-8')
        t = b'/'.join((self.topic, topic))
        done = False
        while not done:
            try:
                print('MQTT PUBLISH: {} --> {}'.format(t, payload))
                self.mqtt.publish(t, payload, retain=retain, qos=qos)
                done = True
            except Exception as e:
                # some error during publishing
                done = False
                done_reconnect = False
                utime.sleep(RETRY_DELAY)
                # tries to reconnect
                while not done_reconnect:
                    try:
                        self._umqtt_connect()
                        self.publish_properties()  # re-publish
                        done_reconnect = True
                    except Exception as e:
                        done_reconnect = False
                        print('ERROR: cannot connect, {}'.format(str(e)))
                        utime.sleep(RETRY_DELAY)

    def get_properties(self):
        """device properties"""
        yield Property(b'$homie', b'2.0.1', True)
        yield Property(b'$online', b'true', True)
        yield Property(b'$name', self.settings.DEVICE_NAME, True)
        yield Property(b'$fw/name', self.settings.DEVICE_FW_NAME, True)
        yield Property(b'$fw/version', __version__, True)
        yield Property(b'$implementation', bytes(sys.platform, 'utf-8'), True)
        yield Property(b'$localip', utils.get_local_ip(), True)
        yield Property(b'$mac', utils.get_local_mac(), True)
        yield Property(b'$stats/interval', self.stats_interval, True)
        yield Property(b'$nodes', b','.join(self.node_ids), True)

    def publish_properties(self):
        """publish device and node properties"""
        for prop in self.get_properties():
            self.publish(*prop)

        # device properties
        for node in self.nodes:
            try:
                for prop in node.get_properties():
                    self.publish(*prop)
            except NotImplementedError:
                raise
            except Exception as error:
                self.node_error(node, error)

    def publish_data(self):
        """publish node data if node has updates"""
        self.publish_device_stats()
        # node data
        for node in self.nodes:
            try:
                if node.has_update():
                    for prop in node.get_data():
                        self.publish(*prop)
            except NotImplementedError:
                raise
            except Exception as error:
                self.node_error(node, error)

    def publish_device_stats(self):
        if utime.time() > self.next_update:
            # uptime
            uptime = utime.time() - self.start_time
            self.publish(b'$stats/uptime', uptime, True)
            # set next update
            self.next_update = utime.time() + self.stats_interval

    def node_error(self, node, error):
        self.errors += 1
        print('ERROR: during publish_data for node: {}'.format(node))
        print(error)
