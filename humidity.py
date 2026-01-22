from bme688 import *
from microbit import *

init_sensor()

while True:
    read_data_registers()
    humidity = calc_humidity()
    print("Humidity:", humidity, "%")
    sleep(500)
