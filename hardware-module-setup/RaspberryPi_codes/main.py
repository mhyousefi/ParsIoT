import time
import XBee
import Plants
import requests

url1 = "http://thingtalk.ir/update"

flower_type_info = {
    "0001": {
        "temp_thresholds": [28, 40],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [150, 220],
        "smoke_thresholds": [140, 250]
    },
    "143e": {
        "temp_thresholds": [28, 20],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [150, 200],
        "smoke_thresholds": [180, 250]
    }
}

DRF1605H = XBee.XBeeModule(
    serial_dir="/dev/ttyUSB0",
    baudrate=9600,
    timeout=1,
    module_name="DRF1605H",
    address="0000"
)


def issue_commands(received_data, plant_info):
    result = []
    if received_data.temp > plant_info["temp_thresholds"][1]:  # temp is at the lower threshold
        result.append(1)
    elif received_data.temp < plant_info["temp_thresholds"][0]:  # temp is at the lower threshold
        result.append(0)

    pump_value = 0
    for value in received_data.yl_69_values:
        if value > plant_info["soil_humidity_thresholds"][1]:  # pump is turned on if at least one plant has dry soil
            pump_value = 1
            break;
    result.append(pump_value)

    if received_data.water_level == 1:  # the reservoir is out of water
        result.append(1)
    else:
        result.append(0)

    if received_data.smoke_value > plant_info["smoke_thresholds"][1]:
        # smoke level getting higher than the upper threshold
        result.append(1)
    elif received_data.smoke_value < plant_info["smoke_thresholds"][0]:
        # smoke level getting lower than the lower threshold
        result.append(0)
        print "COMMANDS ISSUED"
    return result


def receive_arduino_data():
    while True:
        raw_data = DRF1605H.receive_data()
        raw_data.print_data()
        received_data = raw_data.export_greenhouse_data()
        # print received_data.address
        if received_data.address != "":
            print "MEANINGFUL DATA RECEIVED!"
            return received_data


while True:
    received_data = receive_arduino_data()

    greenhouse_address = received_data.address
    plant_info = flower_type_info[greenhouse_address]

    commands = issue_commands(received_data, plant_info)
    print "Commands: " + str(commands)

    message = XBee.XBeeData(
        single_dest=True,
        nums_count=4,
        nums=commands,
        dest_address=greenhouse_address,
        origin_address=DRF1605H.address)

    """
    payload1={'key':'DBM24BJ53DYD0W22', 'field1':received_data.yl_69_values[0]}
    payload2={'key':'DBM24BJ53DYD0W22','field2':received_data.yl_69_values[1]}
    payload3={'key':'DBM24BJ53DYD0W22','field2':received_data.smoke_value}
    payload4={'key':'DBM24BJ53DYD0W22','field3':received_data.temp}
    payload5={'key':'DBM24BJ53DYD0W22','field5':received_data.humidity}
    payload6={'key':'DBM24BJ53DYD0W22','field6':received_data.water_level}
    payload7={'key':'DBM24BJ53DYD0W22','field7':commands[0]}
    payload8={'key':'DBM24BJ53DYD0W22','field8':commands[1]}
    
    r=requests.post(url1,payload1)
    r=requests.post(url1,payload2)
    r=requests.post(url1,payload3)
    r=requests.post(url1,payload4)
    r=requests.post(url1,payload5)
    r=requests.post(url1,payload6)
    r=requests.post(url1,payload7)
    r=requests.post(url1,payload8)
    """

    DRF1605H.send_data(message)
    print ""
