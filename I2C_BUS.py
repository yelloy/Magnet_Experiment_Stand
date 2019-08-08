from smbus import SMBus


class I2CBus:
    def __init__(self, bus_number=1):
        self.bus = SMBus(bus_number)

    def write_data(self, address, cmd, data_list):
        try:
            self.bus.write_i2c_block_data(address, cmd, data_list)
            return 1
        except OSError as my_error:
            print("CAN`T WRITE DATA. ERROR: ", my_error)
            return 0

    def read_data(self, address, register, number_of_bytes):
        try:
            self.bus.read_i2c_block_data(address, register, number_of_bytes)
            return 1
        except OSError as my_error:
            print("CAN`T READ DATA. ERROR: ", my_error)
            return 0
