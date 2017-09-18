import threading
import xbee
import command
import constants
import plants
from main_flow import MainFlowThread
# from server_connection_mqtt import MqttThread

DRF1605H = xbee.XBeeModule(
    serial_dir=constants.SERIAL_DIRECTORY,
    baudrate=constants.BAUDRATE,
    timeout=constants.TIMEOUT,
    module_name=constants.XBEE_NAME,
    address=constants.XBEE_ADDR
)

commands = command.Commands()
greenhouseData = plants.Greenhouse()
lock = threading.Lock()
# threads = []

# Creating new threads
main_flow_thread = MainFlowThread(
    thread_name="Main Flow Thread",
    thread_lock=lock,
    xbee_module=DRF1605H,
    commands_count=constants.COMMANDS_COUNT,
    commands=commands
)
# mqtt_thread = MqttThread(
#     thread_name="MQTT Thread",
#     thread_lock=lock,
#     commands=commands
# )

# Starting new Threads
main_flow_thread.start()
# mqtt_thread.start()

# Adding threads to thread list
# threads.append(main_flow_thread)
# threads.append(mqtt_thread)

# Wait for all threads to complete
# for t in threads:
#     t.join()
print "Exiting Main Thread"
