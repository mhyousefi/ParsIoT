import time
import XBee
import Plants

flower_type_info = {
    "0000": {
        "temp_thresholds": [17, 25],
        "humidity_thresholds": [20, 50],
        "soil_humidity_thresholds": [100, 200],
        "watering_min_interval": 2
    },
    "0001": {
        "temp_thresholds": [20, 30],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [200, 250],
        "watering_min_interval": 3
    }
}

DRF1605H = XBee.XBeeModule(
    serial_dir="/dev/ttyUSB0",
    baudrate=9600,
    timeout=1,
    module_name="DRF1605H",
    address="143e"
)


while True:
    time.sleep(1)
    received_data = DRF1605H.receive_data().export_greenhouse_data()
    greenhouse_address = received_data.address
    plant_info = flower_type_info[greenhouse_address]

    # missing some function to analyze soil humidity and issue a power on command for the water pump
    fan_value = 0
    pump_value = 0
    if received_data.temp > plant_info["temp_thresholds"][1]:
        fan_value = 1
    elif received_data.temp < plant_info["temp_thresholds"][0]:
        fan_value = 0

    message = XBee.XBeeData(
        single_dest=True,
        nums_count=2,
        nums=[fan_value, pump_value],
        dest_address=greenhouse_address,
        origin_address=DRF1605H.address
    )

    DRF1605H.send_data(message)
