from bme688 import *
from microbit import *
import radio
radio.config(channel=42, group=7, length=64)
radio.on()

init_sensor()

while True:
    read_data_registers()
    humidity = calc_humidity()

    msg = "Humidity:," + str(humidity)
    radio.send(msg)

    sleep(500)
