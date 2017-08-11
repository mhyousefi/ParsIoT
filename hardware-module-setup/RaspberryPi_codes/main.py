import time
import serial
import binascii
import XBee

DELAY_TIME = 4

DRF1605H = XBee.XBeeModule(
	serial_dir="/dev/ttyUSB0", 
	baudrate=9600, 
	timeout=1, 
	module_name="DRF1605H", 
	address="143e")


while True:
    
    data_to_be_sent = XBee.XBeeData(
		single_dest=True, 
		nums_count=1, 
		dest_address="0001", 
		origin_address="143e", 
		nums=[15])	
    #DRF1605H.send_data(data_to_be_sent)
    DRF1605H.receive_data().print_data()
    time.sleep(DELAY_TIME)
