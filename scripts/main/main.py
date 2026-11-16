# imports
from animation import play
from display import draw_game, draw_scores, draw_word
from machine import Pin
import PicoOled13
import time

# initiate modules
__all__ = ("play", "draw_game", "draw_scores", "draw_word")

#initiate the display object
display = PicoOled13.get()

#inititiate the buttons
key0 = Pin(15, Pin.IN, Pin.PULL_UP)
key1 = Pin(17, Pin.IN, Pin.PULL_UP)

#initiate the button interupts
last_press = 0
def make_handler(name):
    def handler(pin):
        global last_press
        now = time.ticks_ms()
        if time.ticks_diff(now, last_press) > 200:   # debounce
            last_press = now
            pressed.append(name)
    return handler

pressed = []
key0.irq(trigger=Pin.IRQ_FALLING, handler=make_handler("Key 0"))
key1.irq(trigger=Pin.IRQ_FALLING, handler=make_handler("Key 1"))

#game state variables
team_one_score = 0
team_two_score = 0
current_category = "category"
current_catchphrase = "word"
select_category = True
game_active = True
time_remaining = 60


#bootup animation
play() #default settings

#gameplay loop
while game_active:
    if select_category:
        draw_game(display, current_category, team_one_score, team_two_score)
        if pressed:
            key = pressed.pop(0)
            if key == "Key 0":
                team_one_score += 1
            elif key == "Key 1":
                team_two_score += 1
        if team_one_score >= 7:
            draw_word(display, "Team 1 Wins!")
            time.sleep(3)
            team_one_score = 0
            team_two_score = 0
            play()
        elif team_two_score >= 7:
            draw_word(display, "Team 2 Wins!")
            time.sleep(3)
            team_one_score = 0
            team_two_score = 0
            play()
    else:
        draw_game(display, current_catchphrase, team_one_score, team_two_score)



