import PicoOled13

from time import sleep

display = PicoOled13.get()

display.clear()

display.text("TOP", 0, 0, 0xFFFF)

display.text("MID", 8, 28, 0xFFFF)

display.text("END", 100, 56, 0xFFFF)

display.show()

sleep(10)