# Display Helpers

Importable MicroPython helpers for the 128 x 64 PicoOled13 display.
They use the driver's current font without importing or initialising hardware.

Copy this folder to `/display_helpers` on the Pico alongside `PicoOled13.py`
and `BasicFont.py` from `submodules/pico-oled-1.3-driver`.

```python
import PicoOled13
from display_helpers import draw_game, draw_scores, draw_word

display = PicoOled13.get()

draw_game(display, "ELEPHANT", left_score=0, right_score=0)
draw_scores(display, left_score=1, right_score=0)
draw_word(display, "SNOWBOARD")
```

- `draw_scores(display, left_score, right_score, left_team=1, right_team=2)`
  writes `T1: <score>` and `T2: <score>` at the top left and right.
  The word is preserved; shorter replacement scores leave no stale pixels.
- `draw_word(display, word)` centres the word horizontally and vertically,
  choosing a 1x, 2x or 3x font scale that fits without overlapping the scores.
  The scores are preserved; an empty word clears only the word region.
- `draw_game(display, word, left_score, right_score, left_team=1, right_team=2)`
  updates both regions and refreshes the screen once.

The two individual helpers accept `show=False` for batching changes before
calling `display.show()`. Labels must fit their half of the screen, words must
fit at native font size, and all text must be printable ASCII. Oversized or
unsupported content raises `ValueError` before changing the framebuffer,
rather than silently truncating a score or word. The top 12 rows are reserved
for scores; these helpers own the rest of the screen for the word.

Run desktop tests from the repository root after initialising the submodule:

```sh
python scripts/test-scripts/test_display_helpers.py
```