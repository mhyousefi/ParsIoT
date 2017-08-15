import time
import XBee
import Plants

flower_type_info = {
    "0000": {
        "temp_thresholds": [25, 30],
        "humidity_thresholds": [20, 50],
        "soil_humidity_thresholds": [100, 200],
        "watering_min_interval": 2,
        "smoke_thresholds": [140, 160]
    },
    "0001": {
        "temp_thresholds": [27, 30],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [200, 250],
        "watering_min_interval": 3,
        "smoke_thresholds": [140,160]
    },
    "": {
        "temp_thresholds": [27, 30],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [200, 250],
        "watering_min_interval": 3,
        "smoke_thresholds": [140,160]
    },
}

DRF1605H = XBee.XBeeModule(
    serial_dir="/dev/ttyUSB0",
    baudrate=9600,
    timeout=1,
    module_name="DRF1605H",
    address="143e"
)

def issue_commands(received_data, plant_info):
    result = []
    if received_data.temp > plant_info["temp_thresholds"][1]:  # temp is at the lower threshold
        result.append(1)
    elif received_data.temp < plant_info["temp_thresholds"][0]:  # temp is at the lower threshold
        result.append(0)

    pump_value = 0
    for value in received_data.yl_69_values:
        if value < plant_info["soil_humidity_thresholds"]:  # pump is turned on if at least one plant has dry soil
            pump_value = 1
            break;
    result.append(pump_value)

    if received_data.water_level:  # the reservoir is out of water
        result.append(1)
    else:
        result.append(0)

    if received_data.smoke_value > plant_info["smoke_thresholds"][1]:  # smoke level getting higher than the upper threshold
        result.append(1)
    elif received_data.smoke_value < plant_info["smoke_thresholds"][0]:  # smoke level getting lower than the lower threshold
        result.append(0)

    return result

while True:
    while True:
		raw_data = DRF1605H.receive_data()
		raw_data.print_data()
		received_data = raw_data.export_greenhouse_data()
		if (received_data.address != ""):
			break
		
    greenhouse_address = received_data.address
    plant_info = flower_type_info[greenhouse_address]

    # commands = [fan, pump, out_of_water, too_much_smoke]
    # 1 to activate and 0 otherwise
    commands = issue_commands(received_data, plant_info)

    message = XBee.XBeeData(
        single_dest=True,
        nums_count=4,
        nums=commands,
        dest_address=greenhouse_address,
        origin_address=DRF1605H.address
    )

    DRF1605H.send_data(message)
