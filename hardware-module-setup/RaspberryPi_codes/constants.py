# XBee info
SERIAL_DIRECTORY = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 1
XBEE_NAME = "DRF1605H"
XBEE_ADDR = "0001"
COMMANDS_COUNT = 6

# Server info
HTTP_URL = "http://thingtalk.ir/update"
MQTT_URL = "thingtalk.ir"
MQTT_COMMANDS_TOPIC_NAME = "ParsIoT_commands"
MQTT_ALARM_TOPIC_NAME = "ParsIoT_alarms"
MQTT_PORT = 1883

CHANNEL_API_KEYS = {
    "sensorData": "YMJM61SMT2B6TG2D",
    "YLData": "DJIFGYCC45B0KLNW",
    "RaspberryComms": "P9QZLR4VHXP9DX7Z",
    "userFanCommands": "LR8COSLIN20AOX2G",
    "userPump1Commands": "FKJKQRD6Y0IQ1KJF",
    "userPump2Commands": "M02OGLRYVTH1XJL5",
    "userIdleActuatorCommands": "PN2QD5QKANXZK59A"
}

# Flower info
# Dictionary keys represent the XBee address of the module
# present in the greenhouse with specific flower info and requirements
FLOWER_TYPE_INFO = {
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
