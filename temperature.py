from microbit import *
import radio
from bme688 import *
import time

init_sensor()
radio.on()
radio.config(channel = 42, group =7)
loop =True
numOfReadings = 0

while loop:
    
    read_data_registers()
    temperature = calc_temperature() # degrees C float
    
    temp = ("Temperature: {} C".format(temperature))
    
    radio.send(temp)
    
    numOfReadings += 1
    
    if button_a.is_pressed() or (numOfReadings > 50):
        display.show(Image.DIAMOND)
        loop = False


    sleep(500)
