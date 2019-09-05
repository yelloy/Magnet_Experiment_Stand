from I2C_BUS import I2CBus
from magnet_sensor_tlv493d.tlv493d import STANDARD_TLV493D_ADDRESS
from magnet_sensor_tlv493d.sensor_cascade import CascadeOfCascades
import sys  # Импортируем библиотеки для обработки исключений
import traceback  # Импортируем библиотеки для обработки исключений
import RPi.GPIO as GPIO
import threading

# I2C пины нельзя переназначить тут. Библиотека, использующая их обращается к ../dev/i2c-*** устройству,
# которое использует зарезервированные пины. В нашем случае это пины 2 и 3
# PIN_I2C_SDA = 2
# PIN_I2C_SCL = 3

PIN_SENSOR_LINE_1 = 5
PIN_SENSOR_LINE_2 = 6
PIN_SENSOR_LINE_3 = 7
PIN_SENSOR_LINE_4 = 8
PIN_STEP = 9
PIN_DIR = 10
PIN_OPTIC_SENSOR = 11

DUTY_CYCLE = 50  # Скважность

CASCADES_NUMBER = 1
# Количество каскадов опционально, количество сенсоров - нет
SENSORS_NUMBER = 4

stepper_speed = 50  # Начальная скорость (шагов/секунду)
moving_direction = False


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


def callback_optic_sensor(_):
    global old_optic_sensor_value, optic_sensor_value, moving_direction, DIRECTION_CHANGED
    optic_sensor_value = GPIO.input(PIN_OPTIC_SENSOR)
    if optic_sensor_value != old_optic_sensor_value:
        if optic_sensor_value == 1:
            moving_direction = not moving_direction
            print("change moving direction: ", moving_direction)
            GPIO.output(PIN_DIR, moving_direction)
            DIRECTION_CHANGED = True
        old_optic_sensor_value = optic_sensor_value


def init_pins():
    # GPIO.BCM/GPIO.BOARD определяют распиновку.
    GPIO.setmode(GPIO.BCM)

    # Настройка пинов платы магнитных датчиков
    GPIO.setup(PIN_SENSOR_LINE_1, GPIO.OUT)
    GPIO.setup(PIN_SENSOR_LINE_2, GPIO.OUT)
    GPIO.setup(PIN_SENSOR_LINE_3, GPIO.OUT)
    GPIO.setup(PIN_SENSOR_LINE_4, GPIO.OUT)
    # Выставляю низкий уровень на все линии для выключения датчиков
    GPIO.setup(PIN_SENSOR_LINE_1, GPIO.LOW)
    GPIO.setup(PIN_SENSOR_LINE_2, GPIO.LOW)
    GPIO.setup(PIN_SENSOR_LINE_3, GPIO.LOW)
    GPIO.setup(PIN_SENSOR_LINE_4, GPIO.LOW)

    # Настройка пинов шаговика
    GPIO.setup(PIN_STEP, GPIO.OUT)
    GPIO.setup(PIN_DIR, GPIO.OUT)
    # Запускаю генерацию шим на STEP пине
    pwm = GPIO.PWM(PIN_STEP, stepper_speed)
    # Запуск ШИМ с заданной скважностью
    pwm.start(DUTY_CYCLE)
    # Выбираем начальное направление движения
    GPIO.output(PIN_DIR, moving_direction)

    # Пин оптического концевика. Настраиваем режим входа и подтягиваем к земле
    GPIO.setup(PIN_OPTIC_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Добавляем прерывание. По спаду/возрастанию сигнала на пине концевика вызывается функция
    GPIO.add_event_detect(PIN_OPTIC_SENSOR, GPIO.BOTH, callback=callback_optic_sensor)


# НЕ ГОТОВО. Есть вероятность проблемы необходимости переподключения 8 датчиков для переподключения 1-го
def sensor_thread(cc, bus):
    address_list = [0x4a, 0x4e, 0x5a, 0x5e]
    for i in range(SENSORS_NUMBER):
        for j in range(CASCADES_NUMBER):
            i2c_hub_switch(j)
            data = cc.cascades[j].sensors[i].write_buffer.pop(0)
            while not bus.write_data(STANDARD_TLV493D_ADDRESS, data[0], data[1:]):
                print("Not connected. Cascade: ", i, " Sensor: ", j)
            print("Connected. Cascade: ", i, " Sensor: ", j)


def i2c_hub_switch(j):
    pass


def init_sensors(bus):
    # Инициализируем каскад датчиков
    cc = CascadeOfCascades(CASCADES_NUMBER)
    sensor_lines = [PIN_SENSOR_LINE_1, PIN_SENSOR_LINE_2, PIN_SENSOR_LINE_3, PIN_SENSOR_LINE_4]
    for i in range(SENSORS_NUMBER):
        GPIO.output(sensor_lines[i], GPIO.HIGH)
        for j in range(CASCADES_NUMBER):
            i2c_hub_switch(j)
            data = cc.cascades[j].sensors[i].write_buffer.pop(0)
            while not bus.write_data(STANDARD_TLV493D_ADDRESS, data[0], data[1:]):
                print("Not connected. Cascade: ", i, " Sensor: ", j)
            print("Connected. Cascade: ", i, " Sensor: ", j)
    return cc


if __name__ == "__main__":
    try:
        init_pins()
        i2c_bus = I2CBus()

        board = init_sensors(i2c_bus)
        st = threading.Thread(target=sensor_thread, args=(board, i2c_bus))
        st.start()

    except IOError as error:
        print("IOError: ", error)
    except ValueError as error:
        print("ValueError: ", error)
    except:
        print("UNEXPECTED EXCEPTION")
        print("--- Start Exception Data:")
        traceback.print_exc(limit=2, file=sys.stdout)  # Подробности исключения через traceback
        print("--- End Exception Data:")
    finally:
        GPIO.cleanup()  # Возвращаем пины в исходное состояние
        print("CLEAN UP PINS")  # Информируем о сбросе пинов
    # 1. init stand system
    # 1.1 start sensor thread
    # 1.1.1 init addresses
    # 1.1.2 read data
    # 1.2 start communication with master PC thread
