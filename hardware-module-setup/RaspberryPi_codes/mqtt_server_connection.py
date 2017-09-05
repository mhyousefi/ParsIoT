import paho.mqtt.client as paho


def apply_mqtt_message_on_commands(message, commands):
    if message[0] == "1":
        command_values = []
        for ind in range(1, len(message)):
            command_values.append(int(message[ind]))
        commands.apply_user_input(man_override_will_be_on=True, user_input=command_values)
    elif message[0] == "0":
        commands.apply_user_input(man_override_will_be_on=False, user_input=[0, 0, 0, 0])
    else:
        return


def on_mqtt_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_mqtt_message(client, userdata, msg, commands):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    message = str(msg.payload)
    print ("MQTT Message: " + message)
    apply_mqtt_message_on_commands(message, commands)


client = paho.Client()
client.on_subscribe = on_mqtt_subscribe
client.on_message = on_mqtt_message
client.connect("thingtalk.ir", 1883)
client.subscribe("ParsIoT_TOPIC", qos=1)


def mqtt_threaded_function(commands):
    client.loop_forever(commands)