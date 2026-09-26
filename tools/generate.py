#!/usr/bin/env python3
"""Generate the demo covers, reader pages and the source script from catalog.json.

    .venv/bin/python tools/generate.py

Everything is drawn from scratch (shapes, halftone, text in macOS system fonts), so the
artwork is original and safe to show in store screenshots. Output:
  assets/covers/<slug>.jpg     600x900 cover per series
  assets/pages/pNN.jpg         shared reader pages (every chapter cycles through them)
  sources/demo/main.js         the source script, with the catalog embedded
"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "catalog.json").read_text())
COVERS = ROOT / "assets" / "covers"
PAGES = ROOT / "assets" / "pages"
PAGE_COUNT = 12

FONTS = "/System/Library/Fonts"
TITLE_FONTS = [
    (f"{FONTS}/Supplemental/Impact.ttf", 0),
    (f"{FONTS}/Supplemental/Futura.ttc", 4),        # Futura Condensed ExtraBold
    (f"{FONTS}/Avenir Next Condensed.ttc", 8),      # Heavy
    (f"{FONTS}/Supplemental/DIN Condensed Bold.ttf", 0),
]
BODY_FONT = (f"{FONTS}/Avenir Next.ttc", 5)          # Demi Bold
BUBBLE_FONT = (f"{FONTS}/Supplemental/Chalkboard.ttc", 1)


def font(spec, size):
    path, index = spec
    return ImageFont.truetype(path, size, index=index)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mix(top, bottom, y / (h - 1)))
    return img


def halftone(draw, box, color, spacing, max_r, direction="down"):
    x0, y0, x1, y1 = box
    for y in range(y0, y1, spacing):
        t = (y - y0) / max(1, (y1 - y0))
        r = max_r * (t if direction == "down" else 1 - t)
        for x in range(x0 + (spacing // 2 if (y // spacing) % 2 else 0), x1, spacing):
            if r > 0.6:
                draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def wrap(text, fnt, max_width, draw):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------- covers

def cover(entry, index):
    W, H = 600, 900
    bg, accent, light = (hex_rgb(c) for c in entry["palette"])
    rnd = random.Random(entry["slug"])
    style = entry["style"]

    img = vertical_gradient((W, H), bg, mix(bg, accent, 0.35))
    d = ImageDraw.Draw(img)

    if style == "sun":
        cx, cy, r = W // 2, int(H * 0.45), 190
        for i in range(24):
            a = i * math.pi / 12
            d.polygon([(cx, cy), (cx + math.cos(a) * 900, cy + math.sin(a) * 900),
                       (cx + math.cos(a + 0.12) * 900, cy + math.sin(a + 0.12) * 900)],
                      fill=mix(bg, accent, 0.18))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        d.ellipse([cx - r + 26, cy - r + 26, cx + r - 26, cy + r - 26], outline=light, width=6)
        # A skyline silhouette across the lower third.
        x = 0
        while x < W:
            bw, bh = rnd.randint(40, 90), rnd.randint(90, 260)
            d.rectangle([x, H * 0.66 - bh, x + bw, H], fill=mix(bg, (0, 0, 0), 0.35))
            x += bw - 4
    elif style == "rings":
        cx, cy = int(W * 0.5), int(H * 0.42)
        for i, r in enumerate(range(420, 20, -34)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=accent if i % 2 == 0 else light, width=10 if i % 3 else 4)
        d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=light)
        halftone(d, (0, int(H * 0.62), W, H), mix(bg, (0, 0, 0), 0.45), 18, 8)
    elif style == "dots":
        img.paste(light, [0, 0, W, H])
        d = ImageDraw.Draw(img)
        halftone(d, (0, 0, W, H), mix(light, accent, 0.45), 22, 9, "up")
        for _ in range(7):
            r = rnd.randint(40, 130)
            x, y = rnd.randint(40, W - 40), rnd.randint(140, int(H * 0.7))
            d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice([accent, bg]))
        d.rectangle([0, int(H * 0.72), W, H], fill=bg)
    elif style == "stripes":
        for i in range(-10, 30):
            x = i * 48
            d.polygon([(x, 0), (x + 24, 0), (x + 24 - 400, H), (x - 400, H)],
                      fill=mix(bg, accent, 0.25 if i % 2 else 0.08))
        d.rectangle([60, 150, W - 60, int(H * 0.66)], outline=light, width=8)
        d.rectangle([90, 180, W - 90, int(H * 0.66) - 30], fill=accent)
        halftone(d, (90, 180, W - 90, int(H * 0.66) - 30), mix(accent, bg, 0.5), 16, 6)
    else:  # split
        d.polygon([(0, 0), (W, 0), (W, int(H * 0.38)), (0, int(H * 0.62))], fill=accent)
        d.polygon([(0, int(H * 0.62)), (W, int(H * 0.38)), (W, int(H * 0.44)), (0, int(H * 0.68))],
                  fill=light)
        halftone(d, (0, int(H * 0.68), W, H), mix(bg, accent, 0.3), 20, 8, "up")
        cx, cy, r = int(W * 0.7), int(H * 0.28), 90
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)

    # Title block: always the palette's darkest colour behind its lightest, so titles stay
    # readable whatever the palette. The font shrinks until the longest word fits.
    by_luma = sorted((bg, accent, light), key=lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    band, ink = mix(by_luma[0], (0, 0, 0), 0.35), mix(by_luma[2], (255, 255, 255), 0.2)
    size = 78
    title = entry["title"].upper()
    while size > 40:
        title_font = font(TITLE_FONTS[index % len(TITLE_FONTS)], size)
        if max(d.textlength(w, font=title_font) for w in title.split()) <= W - 80:
            break
        size -= 4
    lines = wrap(title, title_font, W - 80, d)
    # The title band sits in the upper third: the app draws unread badges in the top corners
    # and its own title along the bottom of Library covers, so both edges stay clear.
    line_h = int(size * 1.03)
    block_h = line_h * len(lines) + 70
    top = 190
    d.rectangle([0, top - 26, W, top + block_h - 10], fill=band)
    for i, line in enumerate(lines):
        d.text((40, top + i * line_h), line, font=title_font, fill=ink)
    d.text((42, top + len(lines) * line_h + 12), entry["author"].upper(),
           font=font(BODY_FONT, 26), fill=mix(by_luma[1], ink, 0.35))
    d.text((W - 110, 26), "VOL. 1", font=font(BODY_FONT, 24), fill=ink)

    img.save(COVERS / f"{entry['slug']}.jpg", quality=86, optimize=True)


# ---------------------------------------------------------------------------- pages

LINES = [
    "We're late again.", "Did you hear that?", "Hold on!", "It's only the wind.",
    "Not this time.", "You kept it all these years?", "Then we go together.",
    "Look up.", "I'll explain later.", "That wasn't in the plan.", "Tomorrow, then.",
    "Nobody told me!", "Quiet. Listen.", "Is it open?", "One more try.",
]


def panel_layouts(rnd):
    """A few classic page grids, as (x0, y0, x1, y1) fractions."""
    return rnd.choice([
        [(0, 0, 1, .38), (0, .38, .55, .7), (.55, .38, 1, .7), (0, .7, 1, 1)],
        [(0, 0, .6, .45), (.6, 0, 1, .45), (0, .45, 1, .72), (0, .72, .45, 1), (.45, .72, 1, 1)],
        [(0, 0, 1, .3), (0, .3, 1, .62), (0, .62, .5, 1), (.5, .62, 1, 1)],
        [(0, 0, .5, .5), (.5, 0, 1, .33), (.5, .33, 1, .66), (0, .5, .5, 1), (.5, .66, 1, 1)],
    ])


def page(n):
    W, H, M, G = 1000, 1440, 48, 18
    rnd = random.Random(f"page-{n}")
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    bubble_font = font(BUBBLE_FONT, 30)

    for (fx0, fy0, fx1, fy1) in panel_layouts(rnd):
        x0 = M + fx0 * (W - 2 * M) + (G / 2 if fx0 > 0 else 0)
        y0 = M + fy0 * (H - 2 * M) + (G / 2 if fy0 > 0 else 0)
        x1 = M + fx1 * (W - 2 * M) - (G / 2 if fx1 < 1 else 0)
        y1 = M + fy1 * (H - 2 * M) - (G / 2 if fy1 < 1 else 0)
        x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
        pw, ph = x1 - x0, y1 - y0

        panel = Image.new("L", (pw, ph), 255)
        p = ImageDraw.Draw(panel)
        kind = rnd.choice(["speed", "sky", "figure", "tone"])
        if kind == "speed":
            cx, cy = rnd.randint(pw // 3, 2 * pw // 3), rnd.randint(ph // 3, 2 * ph // 3)
            for i in range(90):
                a = rnd.random() * 2 * math.pi
                r0 = rnd.randint(60, 140)
                p.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                        (cx + math.cos(a) * 1400, cy + math.sin(a) * 1400)],
                       fill=0, width=rnd.randint(1, 4))
        elif kind == "sky":
            halftone(p, (0, 0, pw, ph), 150, 14, 5, "up")
            x = 0
            while x < pw:
                bw, bh = rnd.randint(30, 80), rnd.randint(ph // 5, ph // 2)
                p.rectangle([x, ph - bh, x + bw, ph], fill=30)
                for wy in range(ph - bh + 12, ph - 10, 22):
                    for wx in range(x + 8, x + bw - 10, 16):
                        if rnd.random() < .4:
                            p.rectangle([wx, wy, wx + 6, wy + 9], fill=235)
                x += bw + rnd.randint(-6, 8)
        elif kind == "figure":
            halftone(p, (0, 0, pw, ph), 190, 12, 4)
            fx, base = rnd.randint(pw // 4, 3 * pw // 4), ph + 20
            head = max(28, min(pw, ph) // 9)
            p.ellipse([fx - head, base - head * 7, fx + head, base - head * 5], fill=20)
            p.polygon([(fx - head * 2.2, base), (fx + head * 2.2, base),
                       (fx + head * 1.3, base - head * 5), (fx - head * 1.3, base - head * 5)], fill=20)
        else:
            for y in range(0, ph, 6):
                p.line([(0, y), (pw, y)], fill=int(90 + 140 * y / ph), width=3)

        panel = panel.filter(ImageFilter.SMOOTH)
        img.paste(panel, (x0, y0))
        d.rectangle([x0, y0, x1, y1], outline=0, width=5)

        # Speech bubble in about two out of three panels.
        if rnd.random() < .7 and pw > 220 and ph > 180:
            text = rnd.choice(LINES)
            lines = wrap(text, bubble_font, min(300, pw - 80), d)
            tw = max(d.textlength(l, font=bubble_font) for l in lines)
            th = 36 * len(lines)
            bx = rnd.randint(x0 + 20, max(x0 + 21, x1 - int(tw) - 70))
            by = y0 + rnd.randint(18, max(19, min(80, ph - th - 60)))
            box = [bx, by, bx + tw + 50, by + th + 36]
            tail_x = (box[0] + box[2]) / 2
            d.polygon([(tail_x - 14, box[3] - 6), (tail_x + 14, box[3] - 6),
                       (tail_x + rnd.choice([-30, 30]), box[3] + 34)], fill=255, outline=0)
            d.ellipse(box, fill=255, outline=0, width=4)
            for i, l in enumerate(lines):
                lw = d.textlength(l, font=bubble_font)
                d.text((bx + (tw + 50 - lw) / 2, by + 16 + i * 36), l, font=bubble_font, fill=0)

    img.convert("RGB").save(PAGES / f"p{n:02d}.jpg", quality=82, optimize=True)


# ---------------------------------------------------------------------------- icon

def icon():
    S = 256
    img = vertical_gradient((S, S), hex_rgb("#3a2350"), hex_rgb("#7b3f6e"))
    d = ImageDraw.Draw(img)
    halftone(d, (0, S // 2, S, S), hex_rgb("#5a2f5f"), 14, 5)
    # A stack of three book spines.
    for i, c in enumerate(["#f2a65a", "#5ec2c9", "#f7e8c8"]):
        x = 58 + i * 50
        d.rounded_rectangle([x, 48 + i * 10, x + 38, 208], radius=6, fill=hex_rgb(c))
        d.rectangle([x + 8, 70 + i * 10, x + 30, 76 + i * 10], fill=hex_rgb("#3a2350"))
    img.save(ROOT / "sources" / "demo" / "icon.png")


# ---------------------------------------------------------------------------- source script

def write_script():
    template = (ROOT / "tools" / "main.template.js").read_text()
    catalog = [{k: e[k] for k in ("slug", "title", "author", "genres", "status", "chapters",
                                   "hoursAgo", "description")} for e in CATALOG]
    script = template.replace("/*CATALOG*/[]", json.dumps(catalog, indent=4, ensure_ascii=False)) \
                     .replace("/*PAGE_COUNT*/0", str(PAGE_COUNT))
    (ROOT / "sources" / "demo" / "main.js").write_text(script)


if __name__ == "__main__":
    COVERS.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    for i, entry in enumerate(CATALOG):
        cover(entry, i)
    for n in range(1, PAGE_COUNT + 1):
        page(n)
    icon()
    write_script()
    print(f"{len(CATALOG)} covers, {PAGE_COUNT} pages, sources/demo/main.js")
