import command
import paho.mqtt.client as paho
from threading import Thread
from threading import Lock
from constants import MQTT_COMMANDS_TOPIC_NAME
from constants import MQTT_URL
from constants import MQTT_PORT

mqtt_comms = command.Commands()
th_lock = Lock()


def apply_mqtt_message_on_commands(message):
    if message[0] == "1":
        command_values = []
        for ind in range(1, len(message)):
            command_values.append(int(message[ind]))
        mqtt_comms.apply_user_input(man_override_will_be_on=True, user_input=command_values)
    elif message[0] == "0":
        mqtt_comms.turn_man_override_off()
    else:
        return


def on_mqtt_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_mqtt_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    th_lock.acquire()
    message = str(msg.payload)
    print ("MQTT Message: " + message)
    apply_mqtt_message_on_commands(message)
    print "&&& MQTT &&&: " + str(mqtt_comms.get_values())
    th_lock.release()


client = paho.Client()
client.on_subscribe = on_mqtt_subscribe
client.on_message = on_mqtt_message
client.connect(MQTT_URL, MQTT_PORT)
client.subscribe(MQTT_COMMANDS_TOPIC_NAME, qos=1)


class MqttThread(Thread):
    def __init__(self, thread_name, thread_lock, commands):
        Thread.__init__(self)
        self.thread_name = thread_name
        global mqtt_comms, th_lock
        mqtt_comms = commands
        th_lock = thread_lock

    def run(self):
        print "Starting %s" % self.thread_name
        client.loop_forever()
