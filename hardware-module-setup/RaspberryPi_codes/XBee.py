import serial
import binascii
import time


def xbee_byte_to_str(byte):
    return str(binascii.hexlify(byte))


def xbee_byte_to_int(byte):
    return int(str(binascii.hexlify(byte)), 16)


class XBeeModule:
    def __init__(self, serial_dir, baudrate, timeout, module_name, address):
        self.name = module_name
        self.address = address
        self.serial_dir = serial_dir
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = serial.Serial(self.serial_dir, baudrate=self.baudrate, timeout=self.timeout)

    def get_str_byte(self):
        return xbee_byte_to_str(self.serial_port.read())

    def get_int_byte(self):
        return xbee_byte_to_int(byte=self.serial_port.read())

    def send_data(self, xbee_data):
        """ **Sends data according to the XBee format:** \n
            BYTE 1: FD if sending to a specific destination, something else if not \n
            BYTE 2: # of data bytes to send \n
            BYTE 3 and 4: destination address \n
            OTHER BYTES: actual data \n
            **EXAMPLE:** data = [0xfd, 0x02, 0x00, 0x01, 0xa1, 0xb2] sends the TWO numbers: 0xa1 and 0xb2
            to XBee module in the network with address 0x0001...
        """
        self.serial_port.write(xbee_data.export_xbee_format())

    def receive_data(self):
        data = XBeeData(single_dest=False, nums_count=0, dest_address="", origin_address="", nums=[])
        while True:
            if self.get_str_byte() == "fd":
                data.single_dest = True
                data.nums_count = self.get_int_byte()
                data.dest_address = self.address
                byte3, byte4 = (self.get_int_byte(), self.get_int_byte())

                for i in range(data.nums_count):
                    data.nums[i] = self.get_int_byte()

                data.origin_address = self.get_str_byte() + self.get_str_byte()

            return data


class XBeeData:
    """ **This class defines the data format required in a XBee network** \n
        **single_dest:** True if data is sent to a specific destination \n
        **data_count** # of data bytes (numbers) to be sent \n
        **data:** an array of hex numbers to be sent e.g. [0x01, 0x02, ...]
    """

    def __init__(self, single_dest, nums_count, dest_address, origin_address, nums):
        self.single_dest = single_dest
        self.nums_count = nums_count
        self.nums = nums
        self.dest_address = dest_address
        self.origin_address = origin_address

    def export_xbee_format(self):
        """Returns a an array which is ready to be written using a XBeeModule obj"""
        result = []

        if self.single_dest:
            result.append('0xfd')
        else:
            result.append('0xfc')

        result.append(hex(self.nums_count))
        result.append("0x" + self.dest_address[:2])
        result.append("0x" + self.dest_address[2:])

        for i in range(self.nums_count):
            result.append(hex(self.nums[i]))

        result = binascii.hexlify(bytearray(result))
        return bytearray.fromhex(result)
        return result


# DRF1605H.send_data([0xfd, 0x01, 0x00, 0x00, 0xab])
# DRF1605H = XBeeModule(serial_dir="dev/ttyUSB0", baudrate=9600, timeout=1, module_name="DRF1605H", address=0x0000)
d = XBeeData(single_dest=True, nums_count=2, dest_address="143e", origin_address="", nums=[9, 10])
print d.export_xbee_format()
