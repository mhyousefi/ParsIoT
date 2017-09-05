# Implementing data-holder classes: Flower and Greenhouse

# Dictionary keys represent the XBee address of the module
# present in the greenhouse with specific flower info and requirements
flower_type_info = {
    "0000": {
        "temp_thresholds": [15, 20],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [150, 220],
        "smoke_thresholds": [140, 250]
    },
    "0001": {
        "temp_thresholds": [15, 20],
        "humidity_thresholds": [20, 70],
        "soil_humidity_thresholds": [150, 200],
        "smoke_thresholds": [180, 250]
    }
}


class Flower:
    def __init__(self, temp_thresholds, humidity_thresholds, soil_humidity_thresholds, watering_min_interval):
        self.temp_thresholds = temp_thresholds
        self.humidity_thresholds = humidity_thresholds
        self.soil_humidity_thresholds = soil_humidity_thresholds
        self.watering_min_interval = watering_min_interval


class Greenhouse:
    def __init__(self, address, temp, humidity, smoke_value, yl_69_values, water_level):
        self.address = address
        self.temp = temp
        self.humidity = humidity
        self.smoke_value = smoke_value
        self.yl_69_values = yl_69_values
        self.water_level = water_level
