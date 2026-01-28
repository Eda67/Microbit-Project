from bme688 import *
from microbit import *
import radio



init_sensor()
radio.on()
radio.config(channel = 42, group =7)
loop =True
numOfReadings = 0

while True:
    read_data_registers()
    humidity = calc_humidity()
    temperature = calc_temperature() # degrees C float


    radio.send("Temperature," + str(temperature))
    sleep(30)
    radio.send("Humidity," + str(humidity))
    
   


    sleep(500)
