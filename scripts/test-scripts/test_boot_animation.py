"""Desktop tests; no Pico hardware or third-party packages required."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boot_animation import play
from boot_animation import animation


class Display:
    width = 128
    height = 64

    def __init__(self):
        self.pixels = set()
        self.frames = []

    def fill(self, colour):
        if colour != 0:
            raise AssertionError("Only black clears are expected")
        self.pixels.clear()

    def pixel(self, column, row, colour):
        if not (0 <= column < self.width and 0 <= row < self.height):
            raise AssertionError("Drawing outside framebuffer")
        if colour != 1:
            raise AssertionError("Only monochrome pixels are expected")
        self.pixels.add((column, row))

    def show(self):
        self.frames.append(self.pixels.copy())


class BootAnimationTests(unittest.TestCase):
    def test_packed_sprite_and_clipping(self):
        self.assertEqual(len(animation.PIXELS), animation.WIDTH * animation.HEIGHT // 8)
        display = Display()
        for left, top in ((-63, -49), (127, 63), (-64, 0), (128, 0)):
            animation._draw(display, left, top)

    def test_motion_settles_at_centre_and_clears(self):
        display = Display()
        with patch.object(animation.time, "sleep") as sleep:
            self.assertIs(play(display, duration=0.5, fps=20, hold=0.2), display)
        self.assertEqual(len(display.frames), 11)
        self.assertFalse(display.frames[0])
        expected = Display()
        animation._draw(expected, 32, 7)
        self.assertEqual(display.frames[-2], expected.pixels)
        self.assertFalse(display.frames[-1])
        self.assertGreater(len({frozenset(frame) for frame in display.frames}), 3)
        self.assertEqual(sleep.call_args.args, (0.2,))

    def test_can_keep_final_image(self):
        display = Display()
        with patch.object(animation.time, "sleep"):
            play(display, duration=0.01, hold=0, clear_after=False)
        self.assertEqual(len(display.frames), 2)
        self.assertTrue(display.frames[-1])

    def test_lazy_driver_factory(self):
        display = Display()
        driver = SimpleNamespace(get=lambda: display)
        with patch.dict(sys.modules, {"PicoOled13": driver}):
            with patch.object(animation.time, "sleep"):
                self.assertIs(play(duration=0.01, hold=0), display)

    def test_micropython_clock_path(self):
        sleeps = []
        clock = SimpleNamespace(
            ticks_ms=lambda: 100,
            ticks_diff=lambda end, start: end - start,
            sleep=sleeps.append,
        )
        with patch.object(animation, "time", clock):
            play(Display(), duration=0.1, fps=20, hold=0)
        self.assertEqual(sleeps, [0.05, 0.05, 0])

    def test_rejects_invalid_settings_before_touching_hardware(self):
        for settings in ({"duration": 0}, {"duration": -1}, {"fps": 0}, {"hold": -1}):
            with self.assertRaises(ValueError):
                play(**settings)
        display = Display()
        display.height = 32
        with self.assertRaises(ValueError):
            play(display)
        self.assertFalse(display.frames)


if __name__ == "__main__":
    unittest.main()