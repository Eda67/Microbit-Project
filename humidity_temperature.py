from bme688 import *
from microbit import *
import radio

init_sensor() # Initialises the sensor
sleep(2000) # Small delay to help bme688 initialise
radio.on() 
radio.config(channel = 42, group =7) 

while True:
    read_data_registers()  # Reads the registers from the sensor, to give raw values
    humidity = calc_humidity() # Humidity % int
    temperature = calc_temperature() # Degrees C float
    
    radio.send("Temperature, " + str(temperature)) # Sends str of reading temp eg. Temperature,25
    sleep(100) # Small pause to avoid packet collision
    radio.send("Humidity," + str(humidity)) # sends str of reading humidity eg. Humidity, 25
    
    sleep(5000) # 5 second delay before next reading
