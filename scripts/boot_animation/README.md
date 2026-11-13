# Bear Boot Animation

Text-free, retro pixel art derived from `media/images/Bear.png`. The bear and
skis are isolated from the lettering and packed into a 400-byte, 64 x 50
monochrome sprite for the 128 x 64 OLED. It skis in from the right, bobs,
throws a little snow, and settles at centre. Motion defaults to 3 seconds,
followed by a 0.6-second hold; display transfer time can lengthen playback.

## On the Pico

Initialise the repository's driver if needed:

```sh
git submodule update --init -- submodules/pico-oled-1.3-driver
```

Copy `PicoOled13.py` and `BasicFont.py` from that submodule to the Pico's
filesystem root. Copy this directory as `/boot_animation`, retaining
`__init__.py`, `animation.py`, and `_sprite.py`. The builder, preview and
this README are desktop-only and do not need to be copied.

In your game's `main.py`, before entering the game loop:

```python
import PicoOled13
from boot_animation import play

display = PicoOled13.get()
play(display)
```

Or let the animation obtain and return the driver's shared display:

```python
from boot_animation import play

display = play(duration=2.5, fps=20, hold=0.5)
```

Imports have no hardware side effects. Playback is blocking and finite,
then clears the display for the game. Use `clear_after=False` to keep the
final bear visible until your game draws its first screen. No game text
is drawn. The OLED is monochrome, so the source colours use outlines and
dithering rather than an RGB palette.

## Rebuild the Artwork

On a desktop with Python and Pillow, from the repository root:

```sh
python -m pip install Pillow
python scripts/boot_animation/build_sprite.py
python scripts/test-scripts/test_boot_animation.py
```

The builder regenerates `_sprite.py` and the enlarged `preview.png`.
Pillow is not a runtime dependency of the animation. Tests use a simulated
display and exercise clipping, motion, handoff, settings, and both clock APIs;
they do not verify physical SPI transfer or OLED orientation.