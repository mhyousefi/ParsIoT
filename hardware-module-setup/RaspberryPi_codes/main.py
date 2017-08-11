import time
import XBee

DELAY_TIME = 1

XBee = XBee.XBeeModule(serial_dir="dev/ttyUSB0", baudrate=9600, timeout=1, module_name="DRF1605H", address="143e")

while True:
    time.sleep(DELAY_TIME)
    print XBee.receive_data()