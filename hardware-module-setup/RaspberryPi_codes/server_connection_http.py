import requests
from constants import HTTP_URL as URL
from constants import CHANNEL_API_KEYS


def send_sensor_data_to_server(received_data):
    key = CHANNEL_API_KEYS['sensorData']

    temp_payload = {'key': key, 'field1': received_data.temp}
    payload_humidity = {'key': key, 'field2': received_data.humidity}
    smoke_payload = {'key': key, 'field3': received_data.smoke_value}
    water_level_payload = {'key': key, 'field4': received_data.water_level}

    temp_req = requests.post(URL, temp_payload)
    humidity_req = requests.post(URL, payload_humidity)
    smoke_req = requests.post(URL, smoke_payload)
    water_level_req = requests.post(URL, water_level_payload)


def send_yl_data_to_server(received_data):
    key = CHANNEL_API_KEYS['YLData']

    for ind in range(1, 8):
        field = 'field' + str(ind)
        # print "IND = " + str(ind)
        field_value = received_data.yl_69_values[ind - 1]
        payload = {'key': key, field: field_value}
        req = requests.post(URL, payload)


def send_commands_to_server(commands):
    key = CHANNEL_API_KEYS['RaspberryComms']

    for ind in range(1, 7):
        field = 'field' + str(ind)
        field_value = commands[ind - 1]
        payload = {'key': key, field: field_value}
        req = requests.post(URL, payload)



