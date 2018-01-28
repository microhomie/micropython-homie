import utime
import settings

from homie.node.simple import SimpleHomieNode
from homie import HomieDevice

homie = HomieDevice(settings)

node = SimpleHomieNode("nodetype", "node_property")

homie.add_node(node)

# publish device and node properties
homie.publish_properties()

while True:

    # publish device data
    homie.publish_data()

    node.value = utime.time()

    utime.sleep(1)
