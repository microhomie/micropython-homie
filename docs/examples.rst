
Examples
--------

Please find multiple examples in the ``examples`` folder.




Example: ESP8266 example device
_________________________________

In this example we use the on-board LED from the ESP8266. Copy the ``example-led.py`` file from the ``examples`` diretory to your device and rename it to ``main.py``.

You can now connect a MQTT client to your MQTT Broker an listen to the ``homie/#`` topic, or whatever you set as base topic.

Reset your ESP8266 and watch incoming MQTT messages.

The on-board LED status is reversed to the pin status. On start the on-board
LED is on. To turn it off send *on* or *toggle* via MQTT. Replace ``<DEVICEID>`` with the ID from the MQTT topic:

.. code-block:: shell

    $ mosquitto_pub -t 'homie/<DEVICEID>/led/power/set' -m on
    $ mosquitto_pub -t 'homie/<DEVICEID>/led/power/set' -m off
    $ mosquitto_pub -t 'homie/<DEVICEID>/led/power/set' -m toggle





Example: Simple node
_______________________

In most cases you write your own node classes. But if you just want to test publishing or have a simple use case, you can use the ``SimpleHomieNode`` class. The ``SimpleHomieNode`` does not provide all homie properties, but can be used as a fast start, when you don't want to write anything in a class:

.. code-block:: python

    import utime
    import settings

    from homie.node.simple import SimpleHomieNode
    from homie.device import HomieDevice


    homie_device = HomieDevice(settings)

    n = SimpleHomieNode(node_type=b'dummy', node_property=b'value', interval=5)
    n.value = 17

    homie_device.add_node(n)
    homie_device.publish_properties()

    while True:
        homie_device.publish_data()
        n.value = utime.time()
        print(n)
        utime.sleep(1)
