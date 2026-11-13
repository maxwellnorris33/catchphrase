"""Layout helpers using PicoOled13's own variable-width font."""

HEADER_HEIGHT = 12
PADDING = 1
FONT_HEIGHT = 8


def _text_width(display, text):
    width = 0
    for character in text:
        code = ord(character)
        if not 32 <= code <= 126:
            raise ValueError("text must contain printable ASCII characters only")
        width += len(display.font[code - 32])
    return width


def _score_labels(display, left_team, left_score, right_team, right_score):
    left = "T%s: %s" % (left_team, left_score)
    right = "T%s: %s" % (right_team, right_score)
    available = display.width // 2 - 2 * PADDING
    if min(display.width, display.height) < HEADER_HEIGHT:
        raise ValueError("display is too small for the score header")
    if max(_text_width(display, left), _text_width(display, right)) > available:
        raise ValueError("team labels and scores must each fit half the screen")
    return left, right


def _word_layout(display, word):
    word = str(word).strip()
    width = _text_width(display, word)
    available_width = display.width - 2 * PADDING
    available_height = display.height - 2 * HEADER_HEIGHT
    if available_height < FONT_HEIGHT or width > available_width:
        raise ValueError("word does not fit the display")
    scale = min(3, available_height // FONT_HEIGHT)
    if width:
        scale = min(scale, available_width // width)
    return word, width, scale


def draw_scores(display, left_score, right_score, left_team=1, right_team=2, show=True):
    """Draw T<team>: <score> at the top corners, preserving the word.

    Set show=False to defer the hardware update until display.show().
    Invalid or oversized labels raise ValueError before altering the screen.
    """
    left, right = _score_labels(display, left_team, left_score, right_team, right_score)
    display.fill_rect(0, 0, display.width, HEADER_HEIGHT, 0)
    display.text(left, PADDING, PADDING, 1, wrap=0, just=0)
    display.text(right, display.width - PADDING, PADDING, 1, wrap=0, just=1)
    if show:
        display.show()


def draw_word(display, word, show=True):
    """Centre a word at 1x, 2x or 3x size, preserving the score header.

    An empty string clears the word region. Words must be printable ASCII
    and fit at 1x size; oversized words raise ValueError without clearing.
    """
    word, width, scale = _word_layout(display, word)
    display.fill_rect(0, HEADER_HEIGHT, display.width, display.height - HEADER_HEIGHT, 0)
    left = (display.width - width * scale) // 2
    top = (display.height - FONT_HEIGHT * scale) // 2
    for character in word:
        glyph = display.font[ord(character) - 32]
        for column, bits in enumerate(glyph):
            for row in range(FONT_HEIGHT):
                if bits & (1 << row):
                    display.fill_rect(left + column * scale, top + row * scale,
                                      scale, scale, 1)
        left += len(glyph) * scale
    if show:
        display.show()


def draw_game(display, word, left_score, right_score, left_team=1, right_team=2):
    """Update both scores and the centred word with a single display refresh."""
    _score_labels(display, left_team, left_score, right_team, right_score)
    _word_layout(display, word)
    draw_scores(display, left_score, right_score, left_team, right_team, show=False)
    draw_word(display, word, show=False)
    display.show()