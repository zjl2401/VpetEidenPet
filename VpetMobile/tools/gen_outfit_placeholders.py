# -*- coding: utf-8 -*-
"""Generate Eiden-style gift_art / user_paint placeholders (not Aoba stubs)."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(r"C:\Users\36255\Desktop\VpetEidenPet\VpetMobile\app\src\main\assets\home")
OUT.mkdir(parents=True, exist_ok=True)

# 12x12 palette matching pet_outfit
PAL = [
    None,
    (255, 102, 136, 255),  # pink
    (255, 204, 102, 255),  # yellow
    (102, 204, 255, 255),  # cyan
    (136, 238, 170, 255),  # green
    (255, 255, 255, 255),
    (204, 136, 255, 255),  # purple
    (68, 34, 51, 255),
]


def cells_to_img(cells, scale=6):
    img = Image.new("RGBA", (12 * scale, 12 * scale), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for y in range(12):
        for x in range(12):
            c = cells[y * 12 + x]
            if c and c < len(PAL) and PAL[c]:
                dr.rectangle(
                    [x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1],
                    fill=PAL[c],
                )
    return img


def paint(fn):
    cells = [0] * 144

    def put(x, y, c):
        if 0 <= x < 12 and 0 <= y < 12:
            cells[y * 12 + x] = c

    fn(put)
    return cells


# gift box
gift = paint(
    lambda put: (
        [put(x, y, 1) for x in range(3, 9) for y in range(4, 10)]
        + [put(x, 3, 2) for x in range(2, 10)]
        + [put(5, y, 2) for y in range(2, 10)]
        + [put(6, y, 2) for y in range(2, 10)]
        + [put(4, 2, 6), put(7, 2, 6)]
    )
)
# user paint: little eiden-ish star+heart mark
user = paint(
    lambda put: (
        [put(x, y, 2) for x, y in ((5, 1), (5, 2), (4, 3), (5, 3), (6, 3), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (5, 5))]
        + [put(x, y, 1) for x, y in ((3, 7), (4, 7), (7, 7), (8, 7), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (4, 9), (5, 9), (6, 9), (5, 10))]
    )
)

cells_to_img(gift).save(OUT / "gift_art.png")
cells_to_img(user).save(OUT / "user_paint.png")
print("wrote", OUT / "gift_art.png", (OUT / "gift_art.png").stat().st_size)
print("wrote", OUT / "user_paint.png", (OUT / "user_paint.png").stat().st_size)
