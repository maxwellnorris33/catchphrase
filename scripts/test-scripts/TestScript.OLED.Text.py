import PicoOled13

display = PicoOled13.get()

display.clear()

display.text("Hello!", 0, 0, 0xFFFF)

display.show()