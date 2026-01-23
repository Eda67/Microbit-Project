from microbit import *
import radio
from bme688 import *
import time

init_sensor()
radio.on()
radio.config(channel = 42, group =7)
loop =True
numOfReadings = 0

display.show(Image.HAPPY)

while loop:
    
    read_data_registers()
    temperature = calc_temperature() # degrees C float
    pressure = calc_pressure() # Pressure Pa int
    
    display.scroll("Temperature: {} C".format(temperature))
    display.scroll("Pressure: {} Pa".format(pressure))
    
    temp = ("Temperature: {} C".format(temperature))
    pres = ("Pressure: {} Pa".format(pressure))
    
    radio.send(temp)
    radio.send(pres)
    
    numOfReadings += 1
    
    if button_a.is_pressed() or (numOfReadings > 50):
        display.show(Image.DIAMOND)
        loop = False


    sleep(5000)
