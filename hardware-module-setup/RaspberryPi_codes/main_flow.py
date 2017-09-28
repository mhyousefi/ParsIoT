from threading import Thread
import server_connection_http as server
import paho.mqtt.client as paho
import constants
import server_connection_http
import xbee
from constants import COMMANDS_COUNT
from constants import FLOWER_TYPE_INFO


def on_publish(client, userdata, mid):
    print("ALARM SENT TO APP")


client = paho.Client()
client.on_publish = on_publish
client.connect(constants.MQTT_URL, constants.MQTT_PORT)
client.loop_start()


class MainFlowThread(Thread):
    def __init__(self, thread_name, thread_lock, xbee_module, commands_count, commands):
        Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_lock = thread_lock
        self.xbee_module = xbee_module
        self.commands_count = commands_count
        self.commands = commands

    def run(self):
        print "Starting %s" % self.thread_name
        main_flow(self.xbee_module, self.commands, self.thread_lock)


def eval_led_status(result, received_data, plant_info):
    if received_data.smoke_value > plant_info["smoke_threshold"]:
        # smoke level exceeding the threshold
        result.append(1)
    else:
        # smoke level under the threshold
        result.append(0)

    if received_data.water_level == 0:  # the reservoir is out of water
        result.append(1)
    else:
        result.append(0)


def eval_relay_status(result, received_data, plant_info):
    if received_data.temp > plant_info["temp_threshold"]:
        # temp is exceeding the threshold
        result.append(1)
    else:
        result.append(0)

    pump_value = 0
    for value in received_data.yl_69_values:
        # pump is turned on if at least one plant has dry soil
        if value > plant_info["soil_humidity_threshold"]:
            pump_value = 1
            break
    result.append(pump_value)

	# These two commands correspond to two other actuators 
    result.append(0);
    result.append(0);


def issue_commands(received_data, plant_info):
    result = []

    eval_led_status(result, received_data, plant_info)
    eval_relay_status(result, received_data, plant_info)

    # result = list(map(int, raw_input("Enter commands: ").split(" "))) # for debugging purposes
    print "COMMANDS ISSUED"
    return result


def receive_arduino_data(xbee_module):
    raw_data = xbee_module.receive_data()
    raw_data.print_data()
    cleaned_data = raw_data.export_greenhouse_data()
    print "MEANINGFUL DATA RECEIVED!"
    return cleaned_data


def send_alarm(commands):
	message = commands.get_alarm_message()
	(rc, mid) = client.publish(constants.MQTT_ALARM_TOPIC_NAME, message, qos=1)


def apply_user_comms(commands):
	user_comms = server.get_last_user_comms_from_server()
	if user_comms[0] == "0":
		commands.turn_man_override_off()
	elif user_comms[0] == "1":
		commands.turn_man_override_on()
		values = []
		for ind in range(1, len(user_comms)):
			values.append(int(user_comms[ind]))
		commands.set_relay_values(values)
	#print "user commands applied"



def main_flow(xbee_module, commands, thread_lock):
    print "HTTP thread is up and running."
    print "Interactions with the Arduino began..."

    while True:
        thread_lock.acquire()

        print "\nListening for data..."

        greenhouse_data = receive_arduino_data(xbee_module)
        server_connection_http.send_sensor_data_to_server(greenhouse_data)
        server_connection_http.send_yl_data_to_server(greenhouse_data)

        plant_info = FLOWER_TYPE_INFO[greenhouse_data.address]
        raspberry_commands = issue_commands(greenhouse_data, plant_info)
        server_connection_http.send_commands_to_server(raspberry_commands)

        apply_user_comms(commands)
        commands.set_values(
			new_relay_values=raspberry_commands[2:], 
			smoke_led_new_value=raspberry_commands[0], 
			water_level_led_new_value=raspberry_commands[1]
		)
        print "comms being sent: " + str(commands.get_values())

        message = xbee.XBeeData(
            single_dest=True,
            nums_count=COMMANDS_COUNT,
            nums=commands.get_values(),
            dest_address=greenhouse_data.address,
            origin_address=xbee_module.address
        )
        xbee_module.send_data(message)
        send_alarm(commands)

        thread_lock.release()
