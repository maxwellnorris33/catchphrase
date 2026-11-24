# imports
from animation import play
from display import draw_game, draw_scores, draw_word
from machine import Pin
import PicoOled13
import random
import time
from word_library import WORD_LISTS

# initiate modules
__all__ = ("play", "draw_game", "draw_scores", "draw_word")
category_keys = tuple(WORD_LISTS.keys())

#initiate the display object
display = PicoOled13.get()

#inititiate the buttons
key0 = Pin(15, Pin.IN, Pin.PULL_UP)
key1 = Pin(17, Pin.IN, Pin.PULL_UP)
next_word = Pin(21, Pin.IN, Pin.PULL_UP)
next_category = Pin(20, Pin.IN, Pin.PULL_UP)

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
next_word.irq(trigger=Pin.IRQ_FALLING, handler=make_handler("next word"))
next_category.irq(trigger=Pin.IRQ_FALLING, handler=make_handler("next category"))

#game state variables
team_one_score = 0
team_two_score = 0
category_index = 0
current_catchphrase = "word"
select_category = True
game_active = True
time_remaining = 60_000


#bootup animation
play() #default settings

#gameplay loop
while game_active:

    # draw and perform the category selection mode
    if select_category:
        # draw current game state
        draw_game(display, category_keys[category_index], team_one_score, team_two_score)

        # define action after an interrupt is flagged
        if pressed:
            key = pressed.pop(0)
            if key == "Key 0":
                team_one_score += 1
            elif key == "Key 1":
                team_two_score += 1
            elif key == "next category":
                category_index = (category_index + 1) % len(category_keys)
            elif key == "next word":
                select_category = False
                current_catchphrase = random.choice(WORD_LISTS[category_keys[category_index]])
                deadline = time.ticks_add(time.ticks_ms(), time_remaining)
                
                
        # check win conditions
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
    
    # draw and perform the word guessing, "catchphrase" mode
    else:
        # draw current game state
        draw_game(display, current_catchphrase, team_one_score, team_two_score)

        # define action after an interrupt is flagged
        if pressed:
            key = pressed.pop(0)
            if key == "next word":
                current_catchphrase = random.choice(WORD_LISTS[category_keys[category_index]])

        # time is up
        current_difference = time.ticks_diff(deadline, time.ticks_ms())
        if current_difference <= 0:
            select_category = True


