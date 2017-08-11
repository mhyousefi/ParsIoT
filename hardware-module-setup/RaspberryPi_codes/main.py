import time
import serial
import binascii
import XBee

DELAY_TIME = 5

DRF1605H = XBee.XBeeModule(
	serial_dir="/dev/ttyUSB0", 
	baudrate=9600, 
	timeout=1, 
	module_name="DRF1605H", 
	address="143e")


while True:
    time.sleep(DELAY_TIME)
    data = XBee.XBeeData(
		single_dest=True, 
		nums_count=1, 
		dest_address="0001", 
		origin_address="", 
		nums=[15])
	
    DRF1605H.send_data(data)
