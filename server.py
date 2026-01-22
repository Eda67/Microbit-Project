from microbit import *
import radio
radio.config(channel=42, group=7, length=64)

display.show('S')

while True:
  msg= radio.receive()
  if msg:
    display.show('R')
    print(msg)
    sleep(1000)
    display.show('S')
