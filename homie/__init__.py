import utime

from umqtt.simple import MQTTClient


__version__ = b'0.1.0'


class HomieDevice:

    """ MicroPython implementation of the homie v2 convention. """

    def __init__(self, settings):
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

        self._umqtt_connect()

    def _umqtt_connect(self):
        # mqtt client
        self.mqtt = MQTTClient(
            self.settings.DEVICE_ID,
            self.settings.MQTT_BROKER,
            port=self.settings.MQTT_PORT,
            user=self.settings.MQTT_USERNAME,
            password=self.settings.MQTT_PASSWORD,
            keepalive=self.settings.MQTT_KEEPALIVE,
            ssl=self.settings.MQTT_SSL,
            ssl_params=self.settings.MQTT_SSL_PARAMS)

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
            (b'$homie', b'2.1.0', True),
            (b'$online', b'true', True),
            (b'$name', self.settings.DEVICE_NAME, True),
            (b'$fw/name', self.settings.DEVICE_FW_NAME, True),
            (b'$fw/version', __version__, True),
            (b'$implementation', self.settings.DEVICE_PLATFORM, True),
            (b'$localip', self.settings.DEVICE_LOCALIP, True),
            (b'$mac', self.settings.DEVICE_MAC, True),
            (b'$stats/interval', self.stats_interval, True),
            (b'$nodes', b','.join(self.node_ids), True)
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
