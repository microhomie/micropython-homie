import uasyncio as asyncio


class BaseNode:
    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
        self.topic = None
        self.device = None
        self.properties = []

    def set_topic(self):
        self.topic = "{}/{}".format(
            self.device.dtopic,
            self.id,
        )

    def add_property(self, p, cb=None):
        p.node = self
        self.properties.append(p)

        if cb:
            p.on_message = cb

    async def publish_properties(self):
        """General properties of this node"""
        task = asyncio.create_task
        publish = self.device.publish

        # Publish name and type
        task(publish("{}/$name".format(self.topic), self.name))
        task(publish("{}/$type".format(self.topic), self.type))

        # Publish properties registerd with the node
        properties = self.properties
        task(publish(
            "{}/$properties".format(self.topic),
            ",".join([p.id for p in properties]),
        ))

        # Publish registerd properties
        for p in properties:
            task(p.publish_properties())


# Keep for backward compatibility
HomieNode = BaseNode
