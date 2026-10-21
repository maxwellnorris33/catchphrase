print("this is pico talking from my pc")

from machine import Pin
from time import sleep_ms

led = Pin(25, Pin.OUT)

while True:
    led.toggle()
    sleep_ms(500)