import utime


class HomieNode(object):

    def __init__(self, interval=60):
        self.update_interval = interval
        self.next_update = utime.time()
        self.subscribe = []

    def has_update(self):
        """Depending on the interval:

        returns True if its time for an update,
        returns False if its not yet time for an update
        """
        if utime.time() > self.next_update:
            self.update_data()
            self.next_update = utime.time() + self.update_interval
            return True
        return False

    def __str__(self):
        """Print nice information about the object"""
        raise Exception('not implemented')

    def get_node_id(self):
        """Return one ore more node ids as list"""
        raise Exception('not implemented')

    def get_properties(self):
        """General properties of this node"""
        raise Exception('not implemented')

    def get_data(self):
        """Return the current values"""
        raise Exception('not implemented')

    def update_data(self):
        """Prepare new data. Measure nodes... """
        raise Exception('not implemented')

    def callback(self, topic, payload):
        """Gets called when self.subscribe has topics"""
        raise Exception('not implemented')

    def broadcast_callback(self, payload):
        """Gets called when the broadcast topic receives a message"""
        pass

    def get_property_id_from_topic(self, topic):
        """Return the property id from topic as integer"""
        topic = topic.decode()
        return int(topic.split('/')[-2].split('_')[-1])
