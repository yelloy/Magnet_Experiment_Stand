# МОДУЛЬ РАБОТЫ С ДАТЧИКОМ TLV493D

# Стандартные адреса 0x5e/0x1f. При запитывание датчиков при высоком уровне на шине SDA ставится адрес 0x5e
# Если на шине SDA низкий уровень, адрес выставляется как 0x1f
# В нашем случае используется стандартный адрес 0x5e

STANDARD_TLV493D_ADDRESS = 0x5e


class TLV493D:
    def __init__(self, sensor_number):
        # Создаем внутренний буффер для общения с шиной i2c, т.к. модуль связи - отдельный модуль,
        # он сам будет разгребать буферы с датчиков
        self.write_buffer = []
        # Буфер для данных пришедших с датчика
        self.read_buffer = []

        # Состояние подключения
        self.connected = False

        # Текущий адрес
        self.address = STANDARD_TLV493D_ADDRESS
        self.sensor_number = sensor_number

        # Регистр, конфигурирующий адрес
        self.MOD1 = 0x65 - 0x20*self.sensor_number
        # Параметр используемый в i2c пакетах, как cmd но не используемый данным датчиком, необходимо выставлять равным
        # нулю. По сути это значение идет под запись в нулевой регистр датчика, который зарезервирован под нули.
        self.RESERVED = 0
        # 0x40 - 0100 0000 Выключаю бит четности, включаю Low-power period 12ms и включаю датчик температуры.
        # Можно посмотреть в документации, USER MANUAL страница 26
        self.MOD2 = 0x40

        self.configured_data = [self.RESERVED, self.MOD1, self.RESERVED, self.MOD2]
        self.connect()

    def connect(self):
        self.write_data(self.configured_data)

    def write_data(self, data):
        self.write_buffer.append(data)

    def read_data(self):
        if self.check_read_buffer():
            data_block = self.read_buffer.pop(0)

            bx_high = data_block[0]
            by_high = data_block[1]
            bz_high = data_block[2]
            # temp_high = data_block[3]
            bxy_low = data_block[4]
            bz_low = data_block[5]
            # temp_low = data_block[6]

            bx_value = (bx_high << 4) + ((bxy_low & 0xF0) >> 4)
            by_value = (by_high << 4) + (bxy_low & 0x0F)
            bz_value = (bz_high << 4) + (bz_low & 0x0F)
            # temp_value = ((temp_high & 0xF0) << 4) + temp_low

            bx = (-2048) * (bx_value >> 11) + (bx_value & 0x7FF)
            by = (-2048) * (by_value >> 11) + (by_value & 0x7FF)
            bz = (-2048) * (bz_value >> 11) + (bz_value & 0x7FF)
            return bx, by, bz
        else:
            return None

    def check_write_buffer(self):
        if len(self.write_buffer):
            return 1
        else:
            return 0

    def check_read_buffer(self):
        if len(self.read_buffer):
            return 1
        else:
            return 0
