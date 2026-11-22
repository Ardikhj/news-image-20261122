#!/usr/bin/env python3
"""Render the Sunday 22 November 2026 world-news summary image.

Draws one 1024x1024 picture: a teal masthead naming the day, a hero
panel on the Baltic drone strike on the Russian cargo ship Sparta II
(with a small drawn sea scene), two story cards down the right side,
three cards along the bottom, and a footer ticker of shorter items.

Run:  python3 render.py   (writes entry.png next to this file)
"""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W, H = 1024, 1024
PAPER = (246, 241, 230)
INK = (26, 26, 26)
TEAL = (11, 59, 59)
GOLD = (217, 164, 65)
RED = (179, 55, 47)
NAVY = (18, 38, 58)
CARD = (255, 255, 255)
CARD_EDGE = (216, 207, 192)
MUTED = (90, 84, 72)
LIGHT = (238, 238, 232)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap measured with the real font."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, label, fnt):
    draw.text((x, y), label, font=fnt, fill=RED)
    return y + int(fnt.size * 1.5)


def card(draw, box, title, body, title_fnt, body_fnt, kicker_label=None,
         source=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill=CARD, outline=CARD_EDGE, width=2)
    px = x0 + 18
    py = y0 + 14
    if kicker_label:
        py = kicker(draw, px, py, kicker_label, font(SANS_B, 15))
    title_lines = wrap_text(draw, title, title_fnt, x1 - px - 16)
    py = draw_lines(draw, title_lines, px, py + 2, title_fnt, INK,
                    int(title_fnt.size * 1.18))
    body_lines = wrap_text(draw, body, body_fnt, x1 - px - 16)
    draw_lines(draw, body_lines, px, py + 6, body_fnt, MUTED,
               int(body_fnt.size * 1.32))
    if source:
        draw.text((px, y1 - 32), source, font=font(SERIF, 14), fill=MUTED)


def draw_sea_scene(draw, x0, y0, x1, y1):
    """Schematic dusk sea: dark sky band, grey-blue water, a cargo ship
    silhouette with containers, an orange smoke plume and two drones."""
    draw.rectangle([x0, y0, x1, y1], fill=(24, 52, 74))
    # low sun glow
    draw.ellipse([x1 - 190, y0 + 18, x1 - 90, y0 + 118], fill=(216, 150, 70))
    # sea
    sea_y = y0 + int((y1 - y0) * 0.62)
    draw.rectangle([x0, sea_y, x1, y1], fill=(16, 74, 107))
    for i, wy in enumerate(range(sea_y + 14, y1 - 8, 26)):
        shade = (120, 165, 195) if i % 2 == 0 else (90, 140, 175)
        draw.line([x0 + 12, wy, x1 - 12, wy], fill=shade, width=3)
    # ship hull
    hull_y = sea_y - 6
    hull = [(x0 + 60, hull_y), (x0 + 300, hull_y),
            (x0 + 330, hull_y + 42), (x0 + 30, hull_y + 42)]
    draw.polygon(hull, fill=(12, 12, 14))
    # containers
    for i, cx in enumerate(range(x0 + 78, x0 + 290, 44)):
        col = [(150, 60, 45), (70, 110, 130), (190, 150, 60)][i % 3]
        draw.rectangle([cx, hull_y - 34, cx + 38, hull_y - 2], fill=col)
    # bridge tower
    draw.rectangle([x0 + 300, hull_y - 58, x0 + 330, hull_y - 2], fill=(200, 200, 195))
    # smoke plume: small grey puffs rising from the deck fire
    sx, sy = x0 + 150, hull_y - 30
    for ox, oy, r in [(-6, 0, 15), (-16, -22, 12), (-28, -42, 9)]:
        draw.ellipse([sx + ox - r, sy + oy - r, sx + ox + r, sy + oy + r],
                     fill=(150, 148, 145))
    # flame on deck
    draw.ellipse([sx - 16, sy - 6, sx + 8, sy + 14], fill=(232, 130, 60))
    draw.ellipse([sx - 9, sy + 2, sx + 3, sy + 14], fill=(245, 180, 90))
    # two drones
    for dx, dy in [(x0 + 420, y0 + 46), (x0 + 470, y0 + 84)]:
        draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(20, 20, 20))
        draw.line([dx - 14, dy, dx + 14, dy], fill=(20, 20, 20), width=2)
        draw.line([dx, dy - 14, dx, dy + 14], fill=(20, 20, 20), width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------
    d.rectangle([0, 0, W, 128], fill=TEAL)
    d.text((512, 22), "THE WORLD IN ONE PICTURE",
           font=font(SERIF_B, 52), fill=(255, 255, 255), anchor="ma")
    d.text((512, 84), "SUNDAY  22  NOVEMBER  2026",
           font=font(SANS_B, 26), fill=GOLD, anchor="ma")
    d.rectangle([0, 128, W, 132], fill=GOLD)

    # ---- hero panel (Baltic) --------------------------------------
    hx0, hy0, hx1, hy1 = 24, 146, 618, 566
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=12, fill=NAVY)
    draw_sea_scene(d, hx0 + 14, hy0 + 14, hx1 - 14, hy0 + 178)
    ty = hy0 + 196
    d.text((hx0 + 20, ty), "THE BALTIC  •  WAR AT SEA",
           font=font(SANS_B, 16), fill=GOLD)
    ty += 30
    hl = wrap_text(d, "WAR SPILLS INTO THE BALTIC",
                   font(SERIF_B, 40), hx1 - hx0 - 40)
    ty = draw_lines(d, hl, hx0 + 20, ty, font(SERIF_B, 40),
                    (255, 255, 255), 46)
    deck = ("Drones strike the Russian cargo ship Sparta II in the Gulf "
            "of Finland. Finland says Ukraine is likely behind it; the "
            "16 crew are evacuated.")
    dl = wrap_text(d, deck, font(SANS, 20), hx1 - hx0 - 40)
    draw_lines(d, dl, hx0 + 20, ty + 10, font(SANS, 20),
               (214, 220, 224), 26)

    # ---- right column ----------------------------------------------
    rx0, rx1 = 634, 1000
    card(d, (rx0, 146, rx1, 352),
         "IRAN SAYS IT DOWNED TWO U.S. DRONES",
         "Tehran claims two U.S. drones downed over the Strait of "
         "Hormuz; tankers hit near Oman.",
         font(SERIF_B, 24), font(SANS, 17), "THE GULF")
    card(d, (rx0, 368, rx1, 566),
         "RUSSIAN STRIKES KILL AT LEAST TWO",
         "Overnight attacks hit towns across Ukraine. Zelenskyy calls "
         "Putin a 'murderer'.",
         font(SERIF_B, 24), font(SANS, 17), "UKRAINE")

    # ---- bottom row -------------------------------------------------
    by0, by1 = 582, 884
    cols = [(24, 340), (356, 672), (688, 1000)]
    stories = [
        ("THE ANDES", "6.9 QUAKE SHAKES PERU",
         "A magnitude 6.9 tremor rattles the central Andes; no "
         "casualties or damage are reported at first.",
         "— Reuters"),
        ("CHINA", "TRUMP LANDS IN SHENZHEN FOR APEC",
         "A trilateral meeting with Xi and Putin is planned. Trump "
         "calls China's nuclear build-up 'rapid and concerning'.",
         "— AP"),
        ("EUROPE", "ESTONIA TO SHUT ITS BORDER WITH RUSSIA",
         "Tallinn moves to close the frontier as Baltic tensions rise; "
         "Moscow denounces a 'new Iron Curtain'.",
         "— AP"),
    ]
    for (cx0, cx1), (kick, title, body, src) in zip(cols, stories):
        card(d, (cx0, by0, cx1, by1), title, body,
             font(SERIF_B, 25), font(SANS, 18), kick, source=src)

    # ---- footer ticker ----------------------------------------------
    d.rectangle([0, 900, W, H], fill=TEAL)
    d.rectangle([0, 900, W, 904], fill=GOLD)
    ticker = ("BOLSONARO IN ICU  •  FRANCE PROTESTS, WEEK 6  •  "
              "CYCLONE AKVAN DISRUPTS FLIGHTS  •  ZELENSKYY EYES G-20 TALKS")
    tick_size = 19
    while (d.textlength(ticker, font=font(SANS_B, tick_size)) > 1000
           and tick_size > 12):
        tick_size -= 1
    d.text((512, 922), ticker, font=font(SANS_B, tick_size),
           fill=(255, 255, 255), anchor="ma")
    d.text((512, 958), "22 NOVEMBER 2026  •  THE WORLD IN ONE PICTURE",
           font=font(SANS, 16), fill=GOLD, anchor="ma")

    img.save(OUT, "PNG", optimize=True)
    size = OUT.stat().st_size
    print(f"wrote {OUT} {W}x{H} {size} bytes")
    assert size <= 1_048_576, "over the 1 MiB cap"


if __name__ == "__main__":
    main()
