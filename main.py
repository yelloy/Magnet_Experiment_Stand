from magnet_sensor_tlv493d.I2C_BUS import I2CBus
from magnet_sensor_tlv493d.tlv493d import STANDARD_TLV493D_ADDRESS
from magnet_sensor_tlv493d.sensor_cascade import CascadeOfCascades
import RPi.GPIO as GPIO
#

class Board():
    def __init__(self):
        init_plate()
        start_read_data_from_sensors_thread()

        C = sensor_cascade.Cascade(4)
        i2c_bus = I2CBus()
        message_to_write = C.sensors[0].write_buffer.pop(0)
        i2c_bus.write_data(STANDARD_TLV493D_ADDRESS, message_to_write[0], message_to_write[1:])

        # Вывод сообщения 0-го датчика из буфера
        print(hex(C.sensors[0].write_buffer[0][1]))

    def start_read_data_from_sensors_thread(self):
        pass
