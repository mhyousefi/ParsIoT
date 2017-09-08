# Implementing data-holder classes: Flower and Greenhouse


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
