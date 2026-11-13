"""A finite, text-free ski-in animation for a 128 x 64 OLED."""

import time

from ._sprite import HEIGHT, PIXELS, WIDTH


def _draw(display, left, top):
    for row in range(HEIGHT):
        screen_y = top + row
        if not 0 <= screen_y < display.height:
            continue
        for column in range(WIDTH):
            screen_x = left + column
            if 0 <= screen_x < display.width:
                offset = row * WIDTH + column
                if PIXELS[offset // 8] & (128 >> (offset % 8)):
                    display.pixel(screen_x, screen_y, 1)


def play(display=None, duration=3.0, fps=20, hold=0.6, clear_after=True):
    """Ski in, brake, then hand the display back to the game.

    duration is the motion time in seconds; hold is the final still time.
    Pass an existing PicoOled13 display, or make PicoOled13 and BasicFont
    importable so the driver can be obtained automatically. Importing this
    package does not initialise hardware. The display is returned for reuse.
    """
    if duration <= 0 or fps <= 0 or hold < 0:
        raise ValueError("duration and fps must be positive; hold must be non-negative")
    if display is None:
        import PicoOled13

        display = PicoOled13.get()
    if display.width < WIDTH or display.height < HEIGHT:
        raise ValueError("display must be at least %d x %d" % (WIDTH, HEIGHT))

    frames = max(2, int(duration * fps))
    centre_x = (display.width - WIDTH) // 2
    centre_y = (display.height - HEIGHT) // 2
    bob = (0, 0, 1, 1, 0, 0, -1, -1)
    for frame in range(frames):
        started = time.ticks_ms() if hasattr(time, "ticks_ms") else time.monotonic()
        progress = frame / (frames - 1)
        eased = 1 - (1 - progress) ** 3
        left = int(display.width + (centre_x - display.width) * eased)
        top = centre_y + (bob[frame % len(bob)] if progress < 0.85 else 0)
        display.fill(0)
        if 0.15 < progress < 0.85:
            for flake in range(6):
                snow_x = left + WIDTH - 6 + ((frame * 3 + flake * 7) % 22)
                snow_y = top + HEIGHT - 3 - ((frame + flake * 3) % 9)
                if 0 <= snow_x < display.width and 0 <= snow_y < display.height:
                    display.pixel(snow_x, snow_y, 1)
        _draw(display, left, top)
        display.show()
        if hasattr(time, "ticks_ms"):
            elapsed = time.ticks_diff(time.ticks_ms(), started) / 1000
        else:
            elapsed = time.monotonic() - started
        time.sleep(max(0, duration / frames - elapsed))

    time.sleep(hold)
    if clear_after:
        display.fill(0)
        display.show()
    return display