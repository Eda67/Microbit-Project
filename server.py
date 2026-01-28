from microbit import *
import radio
radio.config(channel=42, group=7, length=64)
radio.on()

uart.init(baudrate=115200)

while True:
    msg= radio.receive()
   
    if msg:
    uart.write(msg + "\n")
  
    
   
