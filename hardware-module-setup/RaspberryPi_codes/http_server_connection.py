import requests

SERVER_PLATFORM_URL = "http://thingtalk.ir/update"

channel_API_keys = {
    "sensorData": "YMJM61SMT2B6TG2D",
    "YLData": "DJIFGYCC45B0KLNW",
    "RaspberryComms": "P9QZLR4VHXP9DX7Z",
    "userFanCommands": "LR8COSLIN20AOX2G",
    "userPump1Commands": "FKJKQRD6Y0IQ1KJF",
    "userPump2Commands": "M02OGLRYVTH1XJL5",
    "userIdleActuatorCommands": "PN2QD5QKANXZK59A"
}


def send_sensor_data_to_server(received_data):
    key = channel_API_keys['sensorData']

    temp_payload = {'key': key, 'field1': received_data.temp}
    payload_humidity = {'key': key, 'field2': received_data.humidity}
    smoke_payload = {'key': key, 'field3': received_data.smoke_value}
    water_level_payload = {'key': key, 'field4': received_data.water_level}

    temp_req = requests.post(SERVER_PLATFORM_URL, temp_payload)
    humidity_req = requests.post(SERVER_PLATFORM_URL, payload_humidity)
    smoke_req = requests.post(SERVER_PLATFORM_URL, smoke_payload)
    water_level_req = requests.post(SERVER_PLATFORM_URL, water_level_payload)


def send_yl_data_to_server(received_data):
    key = channel_API_keys['YLData']

    for ind in range(1, 8):
        field = 'field' + str(ind)
        # print "IND = " + str(ind)
        field_value = received_data.yl_69_values[ind - 1]
        payload = {'key': key, field: field_value}
        req = requests.post(SERVER_PLATFORM_URL, payload)


def send_commands_to_server(commands):
    key = channel_API_keys['RaspberryComms']

    for ind in range(1, 7):
        field = 'field' + str(ind)
        field_value = commands[ind - 1]
        payload = {'key': key, field: field_value}
        req = requests.post(SERVER_PLATFORM_URL, payload)



