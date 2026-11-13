"""Desktop-only asset builder. Requires Pillow, never imported on the Pico."""

from pathlib import Path

from PIL import Image


def build():
    root = Path(__file__).resolve().parents[2]
    source = Image.open(root / "media" / "images" / "Bear.png").convert("RGBA")
    source = source.crop((50, 133, 1151, 991))
    source.thumbnail((256, 200), Image.Resampling.LANCZOS)
    width, height = source.size
    foreground = set()
    for row in range(height):
        for column in range(width):
            red, green, blue, alpha = source.getpixel((column, row))
            if alpha > 127 and min(red, green, blue) < 180:
                foreground.add((column, row))

    largest = set()
    while foreground:
        seed = foreground.pop()
        component = {seed}
        pending = [seed]
        while pending:
            column, row = pending.pop()
            for neighbour in ((column - 1, row), (column + 1, row),
                              (column, row - 1), (column, row + 1)):
                if neighbour in foreground:
                    foreground.remove(neighbour)
                    component.add(neighbour)
                    pending.append(neighbour)
        if len(component) > len(largest):
            largest = component

    mask = Image.new("L", source.size)
    for position in largest:
        mask.putpixel(position, 255)
    bounds = mask.getbbox()
    source = source.crop(bounds).resize((64, 50), Image.Resampling.NEAREST)
    mask = mask.crop(bounds).resize((64, 50), Image.Resampling.NEAREST)
    preview = Image.new("1", (64, 50))
    for row in range(50):
        for column in range(64):
            if not mask.getpixel((column, row)):
                continue
            red, green, blue, alpha = source.getpixel((column, row))
            edge = any(
                not (0 <= neighbour_x < 64 and 0 <= neighbour_y < 50)
                or not mask.getpixel((neighbour_x, neighbour_y))
                for neighbour_x, neighbour_y in (
                    (column - 1, row), (column + 1, row),
                    (column, row - 1), (column, row + 1)
                )
            )
            if red > 130 and green > 110:
                lit = True
            elif red > 100 and red > green * 1.8:
                lit = True
            elif max(red, green, blue) < 15:
                lit = edge
            elif max(red, green, blue) < 45:
                lit = True
            else:
                lit = edge or (column + row) % 2 == 0
            preview.putpixel((column, row), int(lit))

    packed = preview.tobytes()
    output = Path(__file__).resolve().parent
    chunks = [repr(packed[offset:offset + 32]) for offset in range(0, len(packed), 32)]
    (output / "_sprite.py").write_text(
        '"""Generated bear-and-skis bitmap; rebuild with build_sprite.py."""\n\n'
        'WIDTH = 64\nHEIGHT = 50\nPIXELS = (\n'
        + "".join("    " + chunk + "\n" for chunk in chunks) + ")\n",
        encoding="ascii",
    )
    preview.resize((512, 400), Image.Resampling.NEAREST).save(output / "preview.png")
    print("Built 64 x 50 bear sprite (%d bytes), without text." % len(packed))


if __name__ == "__main__":
    build()