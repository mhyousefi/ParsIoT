from threading import Thread
from time import sleep
import server_connection_http
import xbee
import constants
from constants import COMMANDS_COUNT
from constants import FLOWER_TYPE_INFO
import paho.mqtt.client as paho


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
    if received_data.smoke_value > plant_info["smoke_thresholds"][1]:
        # smoke level getting higher than the upper threshold
        result.append(1)
    elif received_data.smoke_value < plant_info["smoke_thresholds"][0]:
        # smoke level getting lower than the lower threshold
        result.append(0)

    if received_data.water_level == 1:  # the reservoir is out of water
        result.append(1)
    else:
        result.append(0)


def eval_relay_status(result, received_data, plant_info):
    if received_data.temp > plant_info["temp_thresholds"][1]:  # temp is at the lower threshold
        result.append(1)
    elif received_data.temp < plant_info["temp_thresholds"][0]:  # temp is at the lower threshold
        result.append(0)

    pump_value = 0
    for value in received_data.yl_69_values:
        if value > plant_info["soil_humidity_thresholds"][1]:  # pump is turned on if at least one plant has dry soil
            pump_value = 1
            break
    result.append(pump_value)


def issue_commands(received_data, plant_info):
    result = []

    eval_led_status(result, received_data, plant_info)
    eval_relay_status(result, received_data, plant_info)

    result.append(0);
    result.append(0);

    # result = list(map(int, raw_input("Enter commands: ").split(" "))) # for debugging purposes
    print "COMMANDS ISSUED"
    return result


def receive_arduino_data(xbee_module):
    raw_data = xbee_module.receive_data()
    raw_data.print_data()
    cleaned_data = raw_data.export_greenhouse_data()
    print "MEANINGFUL DATA RECEIVED!"
    return cleaned_data


def send_alarm(greenhouse_data):
    message = ""
    lower_smoke_thr = FLOWER_TYPE_INFO["smoke_thresholds"][0]
    upper_smoke_thr = FLOWER_TYPE_INFO["smoke_thresholds"][1]

    if greenhouse_data.smoke_value in range(lower_smoke_thr, upper_smoke_thr):
        message += "0"
    else:
        message += "1"
    message += str(greenhouse_data.water_level)

    (rc, mid) = client.publish("ParsIoT_alarms", message, qos=1)


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

        commands.set_values(raspberry_commands[2:], raspberry_commands[0], raspberry_commands[1])
        print "comms: " + str(commands.get_values())

        message = xbee.XBeeData(
            single_dest=True,
            nums_count=COMMANDS_COUNT,
            nums=commands.get_values(),
            dest_address=greenhouse_data.address,
            origin_address=xbee_module.address
        )
        xbee_module.send_data(message)
        send_alarm(greenhouse_data)

        thread_lock.release()
