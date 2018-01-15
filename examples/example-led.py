"""
Example device and node for the ESP8266 onboard LED.

The onboard led status is reversed to the pin status. On start the onboard
LED is on. To turn it off send 'on' or 'toggle' via mqtt:

$ mosquitto_pub -t 'uhomie/esp8266/led/power/set' -m on
$ mosquitto_pub -t 'uhomie/esp8266/led/power/set' -m off
$ mosquitto_pub -t 'uhomie/esp8266/led/power/set' -m toggle
"""

import utime

from homie.node.led import LED
from homie import HomieDevice

CONFIG = {
    'mqtt': {
        'broker': 'localhost',
        'base_topic': b'uhomie'
    },
    'device': {
        'id': b'esp8266',
    }
}

homie = HomieDevice(CONFIG)

# Add LED node to device
homie.add_node(LED(pin=2))

# publish device and node properties
homie.publish_properties()

while True:

    # publish device data
    homie.publish_data()

    # check for new mqtt messages
    homie.mqtt.check_msg()

    utime.sleep(1)
