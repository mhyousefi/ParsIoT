import http_server_connection
import plants
import xbee
import time


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
			

def main_flow_threaded_function(xbee_module, commands_count, commands):
	# time.sleep(2)
	print "HTTP thread is up and running."
	# time.sleep(2)
	print "Interactions with the Arduino began..."
	# time.sleep(2)
	while True:
		print "\nListening for data..."
		received_data = receive_arduino_data(xbee_module)
		http_server_connection.send_sensor_data_to_server(received_data)
		http_server_connection.send_yl_data_to_server(received_data) 

		plant_info = plants.flower_type_info[received_data.address]
		raspberry_commands = issue_commands(received_data, plant_info)
		http_server_connection.send_commands_to_server(raspberry_commands)

		commands.set_values(raspberry_commands[2:], raspberry_commands[0], raspberry_commands[1])
		print "comms: " + str(commands.get_values())
		
		message = xbee.XBeeData(
			single_dest=True,
			nums_count=commands_count,
			nums=commands.get_values(),
			dest_address=received_data.address,
			origin_address=xbee_module.address
		)
		
		xbee_module.send_data(message)
