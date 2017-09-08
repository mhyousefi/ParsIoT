from threading import Thread
import command
import main_flow_function
import xbee
import mqtt_server_connection


COMMANDS_COUNT = 6

DRF1605H = xbee.XBeeModule(
    serial_dir="/dev/ttyUSB0",
    baudrate=9600,
    timeout=1,
    module_name="DRF1605H",
    address="0001"
)

commands = command.Commands()

# mqtt_thread = Thread(target=mqtt_server_connection.mqtt_threaded_function(commands), args=())
# http_thread = Thread(
#     target=main_flow_function.main_flow_threaded_function(
#        xbee_module=DRF1605H,
#        commands_count=COMMANDS_COUNT,
#        commands=commands
#    ),
#    args=()
#)

# mqtt_thread.start()
# http_thread.start()

main_flow_function.main_flow_threaded_function(
	xbee_module=DRF1605H,
    commands_count=COMMANDS_COUNT,
    commands=commands)
