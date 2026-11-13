"""Layout tests using the real submodule font and a simulated framebuffer."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "submodules" / "pico-oled-1.3-driver"))

import BasicFont
from display_helpers import draw_game, draw_scores, draw_word
from display_helpers.display import _text_width


class Display:
    width = 128
    height = 64
    font = BasicFont.BasicFontCondensed

    def __init__(self):
        self.pixels = set()
        self.labels = []
        self.refreshes = 0

    def fill_rect(self, left, top, width, height, colour):
        if not (0 <= left <= left + width <= self.width
                and 0 <= top <= top + height <= self.height):
            raise AssertionError("Rectangle outside the screen")
        for column in range(left, left + width):
            for row in range(top, top + height):
                if colour:
                    self.pixels.add((column, row))
                else:
                    self.pixels.discard((column, row))

    def text(self, text, left, top, colour, wrap, just):
        self.labels.append((text, left, top, just))
        if just == 1:
            left -= _text_width(self, text)
        for character in text:
            glyph = self.font[ord(character) - 32]
            for column, bits in enumerate(glyph):
                for row in range(8):
                    if bits & (1 << row):
                        self.fill_rect(left + column, top + row, 1, 1, colour)
            left += len(glyph)

    def show(self):
        self.refreshes += 1


class DisplayHelpersTests(unittest.TestCase):
    def test_scores_use_opposite_corners(self):
        display = Display()
        draw_scores(display, 12, 34, left_team=3, right_team=4)
        self.assertEqual(display.labels, [("T3: 12", 1, 1, 0), ("T4: 34", 127, 1, 1)])
        self.assertEqual(display.refreshes, 1)
        self.assertTrue(all(row < 12 for column, row in display.pixels))

    def test_word_is_centred_and_scaled_using_real_glyph_widths(self):
        display = Display()
        draw_word(display, "CAT")
        width = _text_width(display, "CAT")
        left = (128 - width * 3) // 2
        expected = Display()
        for character in "CAT":
            glyph = display.font[ord(character) - 32]
            for column, bits in enumerate(glyph):
                for row in range(8):
                    if bits & (1 << row):
                        expected.fill_rect(left + column * 3, 20 + row * 3, 3, 3, 1)
            left += len(glyph) * 3
        self.assertEqual(display.pixels, expected.pixels)

    def test_independent_updates_preserve_other_region(self):
        display = Display()
        draw_game(display, "CAT", 1, 2)
        header = {pixel for pixel in display.pixels if pixel[1] < 12}
        draw_word(display, "DOG")
        self.assertEqual({pixel for pixel in display.pixels if pixel[1] < 12}, header)
        word = {pixel for pixel in display.pixels if pixel[1] >= 12}
        draw_scores(display, 0, 0)
        self.assertEqual({pixel for pixel in display.pixels if pixel[1] >= 12}, word)
        draw_word(display, "")
        self.assertTrue(display.pixels)
        self.assertTrue(all(row < 12 for column, row in display.pixels))

    def test_combined_and_deferred_refresh(self):
        display = Display()
        draw_game(display, "CAT", 10, 20)
        self.assertEqual(display.refreshes, 1)
        draw_scores(display, 11, 20, show=False)
        draw_word(display, "DOG", show=False)
        self.assertEqual(display.refreshes, 1)

    def test_long_word_uses_native_size(self):
        display = Display()
        draw_word(display, "MMMMMMMMMMMMMMMM")
        self.assertTrue(display.pixels)
        self.assertTrue(all(28 <= row < 36 for column, row in display.pixels))

    def test_invalid_content_does_not_clear_existing_frame(self):
        display = Display()
        draw_game(display, "CAT", 1, 2)
        before = display.pixels.copy()
        for word in ("M" * 100, "bad\nword", "caf\u00e9"):
            with self.assertRaises(ValueError):
                draw_game(display, word, 3, 4)
            self.assertEqual(display.pixels, before)
        with self.assertRaises(ValueError):
            draw_scores(display, 10 ** 50, 0)
        self.assertEqual(display.pixels, before)


if __name__ == "__main__":
    unittest.main()