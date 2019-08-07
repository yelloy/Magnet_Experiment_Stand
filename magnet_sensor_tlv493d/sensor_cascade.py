import tlv493d

MAX_SENSOR_NUMBER = 4
# Каскад датчиков


class Cascade:
    def __init__(self, sensors_number):
        if sensors_number > MAX_SENSOR_NUMBER:
            raise ValueError("Magnet sensors number exceed limit")

        self.sensors_number = sensors_number
        self.sensors = []
        for i in range(sensors_number):
            self.sensors.append(tlv493d.TLV493D(i))


class CascadeOfCascades:
    def __init__(self, cascade_number):
        self.cascade_number = cascade_number
        self.cascades = []
        for i in range(cascade_number):
            self.cascades.append(Cascade(4))


if __name__ == "__main__":
    C = Cascade(4)
    # Вывод сообщения 0-го датчика из буфера
    print(hex(C.sensors[0].write_buffer[0][1]))
