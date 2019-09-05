from smbus import SMBus
import threading


class I2CBus:
    def __init__(self, bus_number=1):
        self.bus = SMBus(bus_number)
        self.lock = threading.Lock()

    def write_data(self, address, cmd, data_list):
        with self.lock:
            try:
                self.bus.write_i2c_block_data(address, cmd, data_list)
                return 1
            except OSError as my_error:
                print("CAN`T WRITE DATA. ERROR: ", my_error)
                return 0

    def read_data(self, address, register, number_of_bytes):
        with self.lock:
            try:
                recieved_data = self.bus.read_i2c_block_data(address, register, number_of_bytes)
                return recieved_data
            except OSError as my_error:
                print("CAN`T READ DATA. ERROR: ", my_error)
                return 0
