import serial
import binascii
import time
import base64

DELAY_TIME = 2
XBeeSer = serial.Serial ("/dev/ttyUSB0", baudrate = 9600, timeout = 13)

def XBee_byte_to_int(byte):
	return int(str(binascii.hexlify(byte)), 16) 
	
def XBee_byte_to_str(byte):
	return str(binascii.hexlify(byte))
	
def receive_XBee_data():
	"""Receives XBee data and returns an array of data"""
	data = []
	while(True):
		byte = XBee_byte_to_str(XBeeSer.read())
		if (byte == "fd"):
			return True
		else:
			return False
	

while(True):
    time.sleep(DELAY_TIME)    
    #data = [0xfd, 0x01, 0x00, 0x00, 0xAB]
    #data = binascii.hexlify(bytearray(data))
    #XBeeSer.write(bytearray.fromhex(data))
    byte = XBeeSer.read()
    if byte != "":
		print XBee_byte_to_str(byte)
    #print data


